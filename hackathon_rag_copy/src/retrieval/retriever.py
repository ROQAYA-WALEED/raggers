"""
retriever.py
------------
Given a user question, embed it and pull back the most relevant
chunks from the vector store.
"""

from src.embedder import embedder
from src.vectorstore.vector_store import vector_store
from src import config


def retrieve(query: str, top_k: int = config.TOP_K) -> list[dict]:
    """
    Returns the top_k chunks most relevant to `query`.
    Each result: {"text": ..., "source": ..., "distance": ...}
    """
    query_embedding = embedder.embed_query(query)
    return vector_store.query(query_embedding, top_k=top_k)


def format_context(chunks: list[dict]) -> str:
    """
    Turns retrieved chunks into a single string block to hand to the LLM,
    labeled by source so the model can (loosely) attribute its answer.
    """
    if not chunks:
        return "No relevant context was found."

    blocks = []
    for i, chunk in enumerate(chunks, start=1):
        blocks.append(f"[{i}] (source: {chunk['source']})\n{chunk['text']}")
    return "\n\n".join(blocks)


def retrieve_cosine_similarity(query: str, top_k: int = config.TOP_K) -> list[dict]:
    """
    Returns the top_k chunks most relevant to `query` sorted by Cosine Similarity.
    Each result: {"text": ..., "source": ..., "similarity": ...}
    """
    query_embedding = embedder.embed_query(query)
    raw_results = vector_store.query(query_embedding, top_k=top_k)

    formatted_results = []
    for item in raw_results:
        # Chroma/FAISS usually returns 'distance' (Cosine Distance)
        # Cosine Similarity = 1 - Cosine Distance
        distance = item.get("distance", 0.0)
        similarity = 1.0 - distance

        formatted_results.append({
            "text": item.get("text", ""),
            "source": item.get("source", ""),
            "page": item.get("page", 0),
            "similarity": round(float(similarity), 4),
        })

    # Sort descending by cosine similarity score
    formatted_results.sort(key=lambda x: x["similarity"], reverse=True)
    return formatted_results