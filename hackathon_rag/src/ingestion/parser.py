"""
parser.py
---------
Reads raw files from assets/documents and turns each one into plain text.
Supports .txt / .md natively and .pdf via pypdf, returning page metadata.
"""

from pathlib import Path
from pypdf import PdfReader
from src import config


def parse_txt(path: Path) -> list[dict]:
    """Read a plain text / markdown file as a single-page document."""
    text = path.read_text(encoding="utf-8", errors="ignore")
    if not text.strip():
        return []
    return [{"source": path.name, "page": 1, "text": text}]


def parse_pdf(path: Path) -> list[dict]:
    """Extract text page-by-page from a PDF file."""
    reader = PdfReader(str(path))
    pages = []
    for idx, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        if text.strip():
            pages.append({"source": path.name, "page": idx, "text": text})
    return pages


def parse_file(path: Path) -> list[dict]:
    """Dispatch to the right parser based on file extension."""
    suffix = path.suffix.lower()
    if suffix in (".txt", ".md"):
        return parse_txt(path)
    if suffix == ".pdf":
        return parse_pdf(path)
    raise ValueError(f"Unsupported file type: {suffix}")


def load_documents() -> list[dict]:
    """
    Walk assets/documents and parse every supported file.
    Returns a list of {"source": filename, "page": page_num, "text": content} dicts.
    """
    documents = []
    for path in sorted(config.DOCUMENTS_DIR.glob("*")):
        if path.suffix.lower() not in (".txt", ".md", ".pdf"):
            continue
        docs = parse_file(path)
        documents.extend(docs)
    return documents