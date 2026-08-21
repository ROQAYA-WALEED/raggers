"""
section_expanded_retrieval.py
================================

Query -> dense retrieval (top-k chunks) -> expand each hit to include its
section-siblings within a page window (so a table doesn't get pulled in
without the paragraph that explains it, or vice versa) -> dedupe & order
-> grounded answer from a local LLM via Ollama.
"""

import re
from typing import List, Dict, Any

import ollama
from src import config
from src.embedder import embedder
from src.vectorstore.vector_store import vector_store

# ==========================================
# ⚙️ Setup
# ==========================================

PAGE_WINDOW = getattr(config, "PAGE_WINDOW", 2)   # how many pages before/after a hit, within the same section, count as "siblings"


# ==========================================
# 1. Plain dense retrieval
# ==========================================

def dense_retrieve(query: str, k: int = config.TOP_K) -> List[Dict[str, Any]]:
    """Returns a list of {"text", "page", "section", "distance"} dicts, ranked by relevance."""
    # Reuses the pre-initialized embedder and vector_store without creating a new ChromaDB
    q_emb = embedder.embed_query(query)
    return vector_store.query(query_text_or_embedding=q_emb, top_k=k)


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
        page = h.get("page", 0)
        key = (page, h["text"][:40])
        expanded[key] = h

    # Access the underlying collection directly from the shared vector_store
    chroma_coll = vector_store.vector_store._collection

    for h in hits:
        section, page = h.get("section"), h.get("page")
        if not section or page is None:
            continue

        siblings = chroma_coll.get(
            where={"section": section},
            include=["documents", "metadatas"],
        )
        for doc, meta in zip(siblings["documents"], siblings["metadatas"]):
            sibling_page = meta.get("page", 0)
            if abs(sibling_page - page) > page_window:
                continue
            key = (sibling_page, doc[:40])
            if key in expanded:
                continue
            expanded[key] = {
                "text": doc,
                "page": sibling_page,
                "section": section,
                "distance": None,  # pulled in via expansion, not a direct hit
            }

    # order by page so the context reads in document order, not relevance order
    return sorted(expanded.values(), key=lambda x: x.get("page", 0))


# ==========================================
# 3. Build context block with citations
# ==========================================

def build_context(items: List[Dict[str, Any]]) -> str:
    blocks = [f"[p.{it.get('page', 'N/A')}, {it.get('section') or 'unknown'}]\n{it['text']}" for it in items]
    return "\n\n---\n\n".join(blocks)


# ==========================================
# 4. Orchestration
# ==========================================

def expand_context(query: str, k: int = config.TOP_K, page_window: int = PAGE_WINDOW, model: str = config.LLM_MODEL) -> Dict[str, Any]:
    hits = dense_retrieve(query, k=k)
    expanded = expand_by_section(hits, page_window=page_window)
    context = build_context(expanded)
    
    prompt = f"""Answer the question using ONLY the context below. If the context doesn't contain the answer, say so explicitly. Cite page numbers where relevant.

Context:
{context}

Question: {query}"""

    response = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])

    return {
        "answer": response["message"]["content"],
        "direct_hits": hits,          # what dense retrieval alone found
        "expanded_context_items": expanded,  # what actually went into the prompt, after expansion
        "context_used": context,
    }


if __name__ == "__main__":
    result = expand_context("what dose of piperaquine for a 15kg child?")
    print("Direct hits (pages):", [h.get("page") for h in result["direct_hits"]])
    print("Expanded context (pages):", [it.get("page") for it in result["expanded_context_items"]])
    print("\nAnswer:\n", result["answer"])