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
