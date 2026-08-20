"""
section_expanded_retrieval.py
================================

Query -> dense retrieval (top-k chunks) -> expand each hit to include its
section-siblings within a page window (so a table doesn't get pulled in
without the paragraph that explains it, or vice versa) -> dedupe & order
-> grounded answer from a local LLM via Ollama.

Requires:
    pip install chromadb fastembed ollama --break-system-packages
    ollama pull llama3.2:3b
    ollama serve
"""

import re
from typing import List, Dict, Any

import ollama
import chromadb
from fastembed import TextEmbedding

# ==========================================
# ⚙️ Setup
# ==========================================

EMBED_MODEL = "BAAI/bge-small-en-v1.5"
LLM_MODEL = "llama3.2:3b"
TOP_K = 5
PAGE_WINDOW = 2   # how many pages before/after a hit, within the same section, count as "siblings"

embedder = TextEmbedding(model_name=EMBED_MODEL)
client = chromadb.PersistentClient(path="./chroma_db")
chunks_collection = client.get_or_create_collection(
    "who_malaria_guidelines", metadata={"hnsw:space": "cosine"}
)


# ==========================================
# 1. Plain dense retrieval
# ==========================================

def dense_retrieve(query: str, k: int = TOP_K) -> List[Dict[str, Any]]:
    """Returns a list of {"text", "page", "section", "distance"} dicts, ranked by relevance."""
    q_emb = list(embedder.embed([query]))[0].tolist()
    res = chunks_collection.query(query_embeddings=[q_emb], n_results=k)

    hits = []
    for doc, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0]):
        hits.append({
            "text": doc,
            "page": meta["page"],
            "section": meta.get("section"),
            "distance": dist,
        })
    return hits


# ==========================================
# 2. Section + page-window expansion
# ==========================================

def expand_by_section(hits: List[Dict[str, Any]], page_window: int = PAGE_WINDOW) -> List[Dict[str, Any]]:
    """
    For each retrieved hit, pull in every chunk that shares the same
    section AND falls within `page_window` pages of it -- not just the
    chunks that happened to score highest individually. This is what
    reunites a table with the paragraph that explains it (or vice versa)
    when only one of the two scored high enough to be a top-k hit.
    """
    expanded: Dict[tuple, Dict[str, Any]] = {}

    # keep the original hits (and their distance, for sorting priority)
    for h in hits:
        key = (h["page"], h["text"][:40])
        expanded[key] = h

    for h in hits:
        section, page = h["section"], h["page"]
        if not section:
            continue

        siblings = chunks_collection.get(
            where={"section": section},
            include=["documents", "metadatas"],
        )
        for doc, meta in zip(siblings["documents"], siblings["metadatas"]):
            if abs(meta["page"] - page) > page_window:
                continue
            key = (meta["page"], doc[:40])
            if key in expanded:
                continue
            expanded[key] = {
                "text": doc,
                "page": meta["page"],
                "section": section,
                "distance": None,  # pulled in via expansion, not a direct hit
            }

    # order by page so the context reads in document order, not relevance order
    return sorted(expanded.values(), key=lambda x: x["page"])


# ==========================================
# 3. Build context block with citations
# ==========================================

def build_context(items: List[Dict[str, Any]]) -> str:
    blocks = [f"[p.{it['page']}, {it['section'] or 'unknown'}]\n{it['text']}" for it in items]
    return "\n\n---\n\n".join(blocks)


# ==========================================
# 4. Orchestration
# ==========================================

def expand_context(query: str, k: int = TOP_K, page_window: int = PAGE_WINDOW, model: str = LLM_MODEL) -> Dict[str, Any]:
    hits = dense_retrieve(query, k=k)
    expanded = expand_by_section(hits, page_window=page_window)
    context = build_context(expanded)
    return expanded

#     prompt = f"""Answer the question using ONLY the context below. If the context doesn't contain the answer, say so explicitly. Cite page numbers where relevant.

# Context:
# {context}

# Question: {query}"""

#     response = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])

#     return {
#         "answer": response["message"]["content"],
#         "direct_hits": hits,          # what dense retrieval alone found
#         "expanded_context_items": expanded,  # what actually went into the prompt, after expansion
#         "context_used": context,
#     }


if __name__ == "__main__":
    result = expand_context("what dose of piperaquine for a 15kg child?")
    print("Direct hits (pages):", [h["page"] for h in result["direct_hits"]])
    print("Expanded context (pages):", [it["page"] for it in result["expanded_context_items"]])
    print("\nAnswer:\n", result["answer"])