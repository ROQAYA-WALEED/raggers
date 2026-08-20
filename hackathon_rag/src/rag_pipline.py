# src/rag_pipeline.py
from src.generation.generator import generate_answer
from src.retrieval.retriever import retrieve_context  # Adjust import to match your retriever file


def run_rag_pipeline(question: str) -> dict:
    """Orchestrates retrieval and generation for a user query."""
    # 1. Fetch top relevant context
    context_chunks = retrieve_context(question)
    formatted_context = "\n\n".join(
        [doc.page_content for doc in context_chunks]
    )

    # 2. Call generator
    answer = generate_answer(question=question, context=formatted_context)

    return {
        "question": question,
        "answer": answer,
        "sources": [doc.metadata for doc in context_chunks],
    }