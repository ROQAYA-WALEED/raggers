"""
pdf_table_aware_chunker.py
===========================

Turns a noisy scanned/exported PDF (cover pages, running headers/footers,
page numbers, dozens of tables mixed into the body text) into clean,
LLM-friendly chunks.

Approach
--------
1. Extraction -> pymupdf4llm.to_markdown(..., page_chunks=True)
   Chosen specifically because, unlike PyPDF2/pdfplumber-raw-text, it already
   (a) gives markdown with real headings turned into "#"/"##" based on
       font size/boldness, and
   (b) auto-detects tables and renders them as proper markdown pipe-tables
       ( |a|b|c|\n|---|---|---|\n|1|2|3| ), which is exactly the format an
       LLM can "fathom" best.
   We still post-process both of these (see below) because font-based
   heading detection and table detection aren't perfect.

2. Noise removal
   - Running headers/footers: any line that repeats (after digits are
     normalized to "#") across a large fraction of pages is boilerplate,
     not content -> stripped from every page.
   - Standalone page numbers ("12", "Page 12", "- 12 -", "12 | 20") -> stripped.
   - Front-matter pages (cover, copyright, table-of-contents-only pages)
     near the start of the document -> dropped entirely, not chunked.

3. Heading normalization
   Any leftover bold short line that looks like a title but wasn't
   auto-marked -> promoted to a "##" heading.

4. Table-aware chunking
   The page's cleaned markdown is split into an ordered sequence of
   segments: heading / table / prose. Prose is chunked normally
   (sentence-aware, size + overlap). A table is treated as a hard
   exception: it is NEVER split, and always ends up in its own chunk
   together with the prose that immediately preceded it on the page
   (used as leading "overlap" context so the table isn't orphaned from
   what it was describing).

5. Output
   A flat JSON list, each item: {"text": ..., "page": ..., "section": ...}
   "section" is the nearest preceding heading, or None if the chunk
   appears before any heading was seen.
"""

import os
import re
import json
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from src import config
from src.config import CHUNK_SIZE, CHUNK_OVERLAP

import pymupdf4llm
from src.config import SELECTED_RAW_FILE_PATH, PROCESSED_DOCUMENTS_DIR, SELECTED_RAW_FILENAME


# ==========================================
# ⚙️ Configuration
# ==========================================

TABLE_CONTEXT_OVERLAP_WORDS = 40  # how much preceding prose to attach to a table chunk

NOISE_REPEAT_RATIO = 0.25       # a line repeating on >=25% of pages -> running header/footer
MIN_PAGES_FOR_NOISE_DETECTION = 4

FRONT_MATTER_SCAN_PAGES = 8      # look this many leading pages for ToC/copyright-style front matter
FRONT_MATTER_SPARSE_PAGES = 2    # only the very first N pages get dropped purely for being sparse
                                  # (cover/half-title pages) -- a short page deeper in never gets
                                  # dropped just for having few words, only real front-matter signals do
FRONT_MATTER_MIN_WORDS = 40
TOC_DOT_LEADER = re.compile(r'\.{3,}\s*\d+')


# ==========================================
# 🧹 STEP 1: Noise line detection (running headers/footers, page numbers)
# ==========================================

def _normalize_for_repeat_check(line: str) -> str:
    """Collapse digits/whitespace so 'Page 12' and 'Page 13' compare equal."""
    s = line.strip().lower()
    s = re.sub(r'\d+', '#', s)
    s = re.sub(r'\s+', ' ', s)
    s = re.sub(r'[^\w\s#]', '', s)
    return s.strip()

def _is_page_number_line(line: str) -> bool:
    s = line.strip().strip('*_').strip()
    if not s:
        return False
    if re.fullmatch(r'\d{1,4}', s):
        return True
    if re.fullmatch(r'[-–—]\s*\d{1,4}\s*[-–—]', s):
        return True
    if re.fullmatch(r'page\s+\d{1,4}', s, flags=re.I):
        return True
    if re.fullmatch(r'\d{1,4}\s*/\s*\d{1,4}', s):
        return True
    if re.fullmatch(r'\d{1,4}\s*\|\s*\d{1,4}', s):
        return True
    return False

def find_repeating_noise_lines(pages_text: List[str]) -> set:
    """
    Any (digit-normalized) line that shows up on a large fraction of pages
    is almost certainly a running header/footer, not real content.
    """
    if len(pages_text) < MIN_PAGES_FOR_NOISE_DETECTION:
        return set()

    counts: Dict[str, int] = {}
    for text in pages_text:
        seen_this_page = set()
        for raw_line in text.splitlines():
            norm = _normalize_for_repeat_check(raw_line)
            if not norm or len(norm) < 3:
                continue
            seen_this_page.add(norm)
        for norm in seen_this_page:
            counts[norm] = counts.get(norm, 0) + 1

    threshold = max(2, int(len(pages_text) * NOISE_REPEAT_RATIO))
    noisy = {norm for norm, c in counts.items() if c >= threshold}
    return noisy

def strip_noise_lines(text: str, noisy_norms: set) -> str:
    kept = []
    for raw_line in text.splitlines():
        if _is_page_number_line(raw_line):
            continue
        norm = _normalize_for_repeat_check(raw_line)
        if norm and norm in noisy_norms:
            continue
        kept.append(raw_line)
    return "\n".join(kept)


# ==========================================
# 🧹 STEP 2: Front-matter detection (cover / copyright / ToC pages)
# ==========================================

def is_front_matter_page(text: str, page_index: int) -> bool:
    """
    page_index is 0-based position in the document. Only pages within
    FRONT_MATTER_SPARSE_PAGES get dropped purely for being short (that's
    the cover/half-title heuristic) -- a short real section deeper in the
    scan window is never dropped on word-count alone, only on explicit
    ToC/copyright signals.
    """
    stripped = text.strip()
    if not stripped:
        return True

    words = re.findall(r"\w+", stripped)

    # A page that is mostly dot-leader ToC lines ("Chapter 1 ..... 3")
    toc_line_count = sum(1 for ln in stripped.splitlines() if TOC_DOT_LEADER.search(ln))
    if toc_line_count >= 2:
        return True

    lowered = stripped.lower()
    if re.search(r'\btable of contents\b', lowered) and len(words) < 120:
        return True
    if re.search(r'\bcopyright\b|\ball rights reserved\b|\bisbn\b', lowered) and len(words) < 80:
        return True

    # Very sparse pages right at the front (cover, half-title, blank leaf)
    if page_index < FRONT_MATTER_SPARSE_PAGES and len(words) < FRONT_MATTER_MIN_WORDS:
        return True

    return False


# ==========================================
# 🏷️ STEP 3: Heading normalization
# ==========================================

BOLD_ONLY_LINE = re.compile(r'^\*\*(.+?)\*\*\s*$')

def normalize_headings(text: str) -> str:
    """
    pymupdf4llm already turns big/bold text into '#'/'##' most of the time.
    This catches leftovers: short bold-only lines that are clearly a title
    but weren't auto-promoted, and turns them into a '##' heading.
    """
    out_lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith('#'):
            out_lines.append(line)
            continue

        m = BOLD_ONLY_LINE.match(stripped)
        if m:
            inner = m.group(1).strip()
            word_count = len(inner.split())
            looks_like_table_caption = bool(re.match(r'^(table|figure|fig\.?)\s*\d*', inner, re.I))
            if 0 < word_count <= 10 and not looks_like_table_caption:
                out_lines.append(f"## {inner}")
                continue
        out_lines.append(line)
    return "\n".join(out_lines)


# ==========================================
# 🔗 STEP 4: Segment the page into heading / table / prose blocks
# ==========================================

TABLE_ROW = re.compile(r'^\s*\|.*\|\s*$')
TABLE_SEPARATOR = re.compile(r'^\s*\|?[\s:\-]+\|[\s:\-\|]+\s*$')

def segment_page(text: str) -> List[Dict[str, str]]:
    """
    Break a page's cleaned markdown into an ordered list of
    {"type": "heading"|"table"|"prose", "content": str} segments.
    A table segment is guaranteed to contain the ENTIRE contiguous
    markdown table (header row + separator + all data rows), untouched.
    """
    lines = text.splitlines()
    segments: List[Dict[str, str]] = []

    i = 0
    n = len(lines)
    buffer: List[str] = []

    def flush_prose():
        if buffer:
            joined = "\n".join(buffer).strip()
            if joined:
                segments.append({"type": "prose", "content": joined})
            buffer.clear()

    while i < n:
        line = lines[i]
        stripped = line.strip()

        # Heading line
        if re.match(r'^#{1,6}\s+\S', stripped):
            flush_prose()
            segments.append({"type": "heading", "content": stripped})
            i += 1
            continue

        # Start of a markdown table: a "|...|" row followed by a separator row
        if TABLE_ROW.match(line) and i + 1 < n and TABLE_SEPARATOR.match(lines[i + 1]):
            flush_prose()
            table_lines = [line, lines[i + 1]]
            j = i + 2
            while j < n and TABLE_ROW.match(lines[j]):
                table_lines.append(lines[j])
                j += 1
            segments.append({"type": "table", "content": "\n".join(table_lines)})
            i = j
            continue

        buffer.append(line)
        i += 1

    flush_prose()
    return segments


# ==========================================
# 🔗 STEP 5: Sentence-aware prose chunking (with overlap)
# ==========================================

_SENT_SPLIT = re.compile(r'(?<=[.!?])\s+(?=[A-Z0-9])')

def split_sentences(text: str) -> List[str]:
    text = re.sub(r'\s+', ' ', text).strip()
    if not text:
        return []
    parts = _SENT_SPLIT.split(text)
    return [p.strip() for p in parts if p.strip()]

def chunk_prose(sentences: List[str],
                 chunk_size: int = CHUNK_SIZE,
                 overlap_words: int = CHUNK_OVERLAP) -> List[str]:
    """
    Greedy sentence-aware chunker: pack whole sentences into a chunk until
    the target word budget is hit, then start the next chunk by carrying
    the last `overlap_words` worth of sentences forward for continuity.
    """
    if not sentences:
        return []

    chunks = []
    current: List[str] = []
    current_words = 0

    for sent in sentences:
        w = len(sent.split())
        if current and current_words + w > chunk_size:
            chunks.append(" ".join(current))

            # build overlap tail from the end of the chunk we just closed
            overlap: List[str] = []
            overlap_count = 0
            for s in reversed(current):
                sw = len(s.split())
                if overlap_count + sw > overlap_words:
                    break
                overlap.insert(0, s)
                overlap_count += sw
            current = overlap + [sent]
            current_words = sum(len(s.split()) for s in current)
        else:
            current.append(sent)
            current_words += w

    if current:
        chunks.append(" ".join(current))

    return chunks

def tail_sentences(sentences: List[str], max_words: int) -> str:
    """
    Last full sentences from `sentences` whose combined length is closest
    to (without exceeding, unless a single sentence is already bigger)
    max_words. Used as overlap context glued onto a table chunk -- never
    cuts a sentence in half.
    """
    if not sentences:
        return ""
    picked: List[str] = []
    word_count = 0
    for sent in reversed(sentences):
        w = len(sent.split())
        if picked and word_count + w > max_words:
            break
        picked.insert(0, sent)
        word_count += w
    return " ".join(picked).strip()

def clean_heading_text(text: str) -> str:
    """Strip markdown heading markers and bold/italic markers for a plain section name."""
    t = re.sub(r'^#{1,6}\s+', '', text).strip()
    t = re.sub(r'\*\*(.+?)\*\*', r'\1', t)
    t = re.sub(r'\*(.+?)\*', r'\1', t)
    return t.strip()


# ==========================================
# 🚀 MAIN: page -> ordered list of chunk dicts
# ==========================================

def build_chunks_for_page(page_number: int,
                           segments: List[Dict[str, str]],
                           section_in: Optional[str]) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    """
    Walk a page's segments in order, emitting chunk dicts. Tables are a hard
    exception: always their own chunk, never split, with the trailing words
    of whatever prose came right before them attached as leading context.
    Returns (chunks, section_out) so section tracking carries into the next page.
    """
    chunks: List[Dict[str, Any]] = []
    section = section_in
    pending_prose_sentences: List[str] = []  # last prose seen, for table overlap context

    for seg in segments:
        if seg["type"] == "heading":
            section = clean_heading_text(seg["content"])
            pending_prose_sentences = []
            continue

        if seg["type"] == "table":
            overlap_ctx = tail_sentences(pending_prose_sentences, TABLE_CONTEXT_OVERLAP_WORDS)
            table_text = seg["content"].strip()
            combined = f"{overlap_ctx}\n\n{table_text}" if overlap_ctx else table_text
            chunks.append({
                "text": combined,
                "page": page_number,
                "section": section,
            })
            pending_prose_sentences = []  # don't reuse the same context for a later table
            continue

        # prose
        sentences = split_sentences(seg["content"])
        if not sentences:
            continue
        prose_chunks = chunk_prose(sentences)
        for pc in prose_chunks:
            chunks.append({
                "text": pc,
                "page": page_number,
                "section": section,
            })
        pending_prose_sentences = sentences

    return chunks, section


def process_pdf(file_path: str) -> List[Dict[str, Any]]:
    print(f"📄 Extracting with pymupdf4llm: {file_path}")
    raw_pages = pymupdf4llm.to_markdown(file_path, page_chunks=True)

    pages_text = [p["text"] for p in raw_pages]
    page_numbers = [p["metadata"].get("page_number", idx + 1) for idx, p in enumerate(raw_pages)]

    # --- noise detection across the whole doc ---
    noisy_norms = find_repeating_noise_lines(pages_text)
    print(f"🔍 Detected {len(noisy_norms)} repeating running-header/footer patterns")

    all_chunks: List[Dict[str, Any]] = []
    section = None
    dropped_front_matter = 0

    for idx, (page_num, text) in enumerate(zip(page_numbers, pages_text)):
        cleaned = strip_noise_lines(text, noisy_norms)
        cleaned = normalize_headings(cleaned)

        # Front-matter check only applies near the start of the document,
        # so a legitimately short page deep in the book isn't dropped.
        if idx < FRONT_MATTER_SCAN_PAGES and is_front_matter_page(cleaned, idx):
            dropped_front_matter += 1
            continue

        if not cleaned.strip():
            continue

        segments = segment_page(cleaned)
        page_chunks, section = build_chunks_for_page(page_num, segments, section)
        all_chunks.extend(page_chunks)

    print(f"🗑️  Dropped {dropped_front_matter} front-matter page(s)")
    print(f"✅ Produced {len(all_chunks)} chunks "
          f"({sum(1 for c in all_chunks if TABLE_ROW.search(c['text']))} contain a table)")

    return all_chunks




def save_chunks(chunks: List[Dict[str, Any]], input_dir: str):
    if not os.path.exists(input_dir):
        print(f"❌ Error: The directory '{input_dir}' does not exist.")
        return

    # Extract clean filename without extension using pathlib.Path
    raw_filename = getattr(config, "SELECTED_RAW_FILENAME", "document.pdf")
    clean_filename = Path(raw_filename).stem

    chunk_size = getattr(config, "CHUNK_SIZE", 100)
    chunk_overlap = getattr(config, "CHUNK_OVERLAP", 20)

    output_filename = (
        f"{clean_filename}_{chunk_size}_{chunk_overlap}.json"
    )
    output_path = os.path.join(input_dir, output_filename)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)

    print(f"💾 Saved {len(chunks)} chunks -> {output_path}")