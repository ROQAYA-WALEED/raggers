# src/rag_pipeline.py
import logging
from src import config
from src.generation.generator import generate_answer
from src.ingestion.ingest import run_ingestion
from src.retrieval.retriever import filter_retrieved_context

logger = logging.getLogger(__name__)


def initialize_pipeline(force_reingest: bool = False) -> None:
    """Ensures the vector store is populated and ready.

    If force_reingest is True, runs the complete ingestion pipeline.
    """
    if force_reingest:
        logger.info("Initializing vector store via ingestion pipeline...")
        run_ingestion()
    else:
        logger.info("Pipeline initialized using existing vector store.")


def run_rag_pipeline(
    question: str, reingest_first: bool = False
) -> dict:
    """Orchestrates ingestion (if requested), retrieval, threshold filtering, and answer generation.

    Args:
        question (str): User medical query.
        reingest_first (bool): If True, runs run_ingestion() before processing
          the query.

    Returns:
        dict: Structured response containing LLM answer and guardrail metrics.
    """
    # 1. Optionally run ingestion to ensure database & embeddings are live
    # if reingest_first:
    #     run_ingestion()

    # 2. Retrieve context filtered by similarity threshold
    threshold = getattr(config, "RELEVANCE_THRESHOLD", 0.60)
    top_k = getattr(config, "TOP_K", 3)

    context_str, evidence_chunks = filter_retrieved_context(
        query=question, threshold=threshold, top_k=top_k
    )

    # 3. Generate structured response with 2-layer safety guardrails
    # If context_str is empty (""), generator.py Layer 1 triggers refusal automatically
    output = generate_answer(
        question=question, context=context_str, evidence_chunks=evidence_chunks
    )

    llm_response = output[0]["LLM response"]
    guardrail_metrics = output[1]["Guardrail metrics"]

    return {
        "question": question,
        "recommendation": llm_response.get("Recomendation"),
        "evidence": llm_response.get("Evidence"),
        "citation": llm_response.get("Citation"),
        "confidence": llm_response.get("Confidence"),
        "guardrail_metrics": guardrail_metrics,
    }


if __name__ == "__main__":
    # Ensure vector store is ingested before testing query execution
    initialize_pipeline(force_reingest=True)

    sample_query = "What is the recommended target dose of parenteral artesunate for children?"
    result = run_rag_pipeline(sample_query)

    import json

    print(json.dumps(result, indent=2))