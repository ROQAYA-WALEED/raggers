"""
rag_metrics.py
------------
Metrics and evaluation functions for RAG system.
"""

import json
import logging
import ollama
from src import config
from .rag_metrics import (
    create_rag_safety_prompt,
    predict_safety,
    enforce_safety_guardrail,
    calculate_faithfulness_hybrid,
    calculate_citation_accuracy,
    REFUSAL_MESSAGE,
)

logger = logging.getLogger(__name__)

# python -m src.generation.generator

def calculate_confidence(faithfulness_score: float, was_blocked: bool, context: str) -> str:
    """Helper function to map execution results to confidence level."""
    if was_blocked or not context or not context.strip():
        return "insufficient"
    elif faithfulness_score >= 0.6:
        return "high"
    else:
        return "low"


def generate_answer(
    question: str, 
    context: str, 
    evidence_chunks: list[dict] = None,
    use_semantic: bool = False,
    threshold: float = 0.25
) -> list[dict]:
    """
    Generates an answer using a local Ollama model while enforcing input & output safety guardrails.

    Args:
        question (str): User query.
        context (str): Joined text content of retrieved chunks.
        evidence_chunks (list[dict]): List of dicts formatted as [{"text": ..., "page": ...}]
        use_semantic (bool): Whether to use CrossEncoder for semantic evaluation (default: False).
        threshold (float): Faithfulness threshold for Layer 2 guardrail (default: 0.25).

    Returns:
        list[dict]: Output containing 'LLM response' and 'Guardrail metrics'.
    """
    if evidence_chunks is None:
        evidence_chunks = [{"text": context, "page": 1}] if context else []

    # Format citations metadata for LLM prompt
    chunk_evidence_text = "\n---\n".join([c.get("text", "") for c in evidence_chunks]) if evidence_chunks else context
    citations = [
        {k: v for k, v in c.items() if k != "text"} 
        for c in evidence_chunks
    ] if evidence_chunks else []

    # =========================================================================
    # LAYER 1: Input Safety Filter
    # =========================================================================
    if not predict_safety(question):
        logger.warning(f"Query blocked at Layer 1 (Input Safety): '{question}'")
        return [
            {
                "LLM response": {
                    "Recomendation": REFUSAL_MESSAGE,
                    "Evidence": "",
                    "Citation": [],
                    "Confidence": "insufficient"
                }
            },
            {
                "Guardrail metrics": {
                    "answer": REFUSAL_MESSAGE,
                    "was_blocked": True,
                    "blocked_at": "Layer 1 (Input Keyword Filter)",
                    "faithfulness_score": 0.0,
                    "citation_accuracy": 0.0,
                    "reason": "Query triggered input safety filters or unsafe medical practices."
                }
            }
        ]

    # If context is empty, refuse immediately
    if not context or not context.strip():
        logger.warning("Empty context provided. Returning refusal.")
        return [
            {
                "LLM response": {
                    "Recomendation": REFUSAL_MESSAGE,
                    "Evidence": "",
                    "Citation": [],
                    "Confidence": "insufficient"
                }
            },
            {
                "Guardrail metrics": {
                    "answer": REFUSAL_MESSAGE,
                    "was_blocked": True,
                    "blocked_at": "Layer 1 (No Context)",
                    "faithfulness_score": 0.0,
                    "citation_accuracy": 0.0,
                    "reason": "No relevant context found in vector store."
                }
            }
        ]

    # =========================================================================
    # GENERATION: Ollama Inference
    # =========================================================================
    system_prompt = create_rag_safety_prompt()
    user_message = (
        f"Context Evidence:\n{context}\n\n"
        f"Available Citations Metadata: {json.dumps(citations)}\n\n"
        f"Question: {question}\n\n"
        "Respond strictly with the valid JSON format requested."
    )

    try:
        response = ollama.chat(
            model=config.LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            options={
                "num_predict": getattr(config, "MAX_TOKENS", 512),
                "temperature": 0.0
            },
        )
        raw_llm_output = response["message"]["content"].strip()

        # Parse LLM output
        try:
            parsed_json = json.loads(raw_llm_output)
            llm_response_dict = parsed_json.get("LLM response", parsed_json)
            recommendation_text = llm_response_dict.get("Recomendation", raw_llm_output)
        except Exception:
            recommendation_text = raw_llm_output
            llm_response_dict = {
                "Recomendation": recommendation_text,
                "Evidence": chunk_evidence_text,
                "Citation": citations,
                "Confidence": "low"
            }

    except Exception as e:
        logger.error(f"Error during Ollama generation: {e}")
        return [
            {
                "LLM response": {
                    "Recomendation": REFUSAL_MESSAGE,
                    "Evidence": "",
                    "Citation": [],
                    "Confidence": "insufficient"
                }
            },
            {
                "Guardrail metrics": {
                    "answer": REFUSAL_MESSAGE,
                    "was_blocked": True,
                    "blocked_at": "Generation Error",
                    "faithfulness_score": 0.0,
                    "citation_accuracy": 0.0,
                    "reason": f"Model inference error: {str(e)}"
                }
            }
        ]

    # =========================================================================
    # LAYER 2: Output Safety Guardrail & Faithfulness Verification
    # =========================================================================
    guardrail_res = enforce_safety_guardrail(
        generated_answer=recommendation_text,
        retrieved_context=context,
        evidence_chunks=evidence_chunks,
        threshold=threshold,
        use_semantic=use_semantic
    )

    if guardrail_res["was_blocked"]:
        logger.warning(f"Answer blocked at Layer 2. Reason: {guardrail_res['reason']}")
        return [
            {
                "LLM response": {
                    "Recomendation": REFUSAL_MESSAGE,
                    "Evidence": chunk_evidence_text,
                    "Citation": citations,
                    "Confidence": "insufficient"
                }
            },
            {
                "Guardrail metrics": {
                    "answer": REFUSAL_MESSAGE,
                    "was_blocked": True,
                    "blocked_at": "Layer 2 (Output Guardrail)",
                    "faithfulness_score": guardrail_res["faithfulness_score"],
                    "citation_accuracy": 0.0,
                    "reason": guardrail_res["reason"]
                }
            }
        ]

    # Calculate citation accuracy on valid outputs
    faithfulness_res = calculate_faithfulness_hybrid(
        answer=recommendation_text,
        evidence_chunks=evidence_chunks,
        threshold=threshold,
        use_semantic=use_semantic
    )
    citation_acc = calculate_citation_accuracy(faithfulness_res["details"])
    confidence_level = calculate_confidence(faithfulness_res["faithfulness_score"], False, context)

    final_llm_response = {
        "Recomendation": recommendation_text,
        "Evidence": llm_response_dict.get("Evidence", chunk_evidence_text) or chunk_evidence_text,
        "Citation": llm_response_dict.get("Citation", citations) or citations,
        "Confidence": confidence_level
    }

    return [
        {
            "LLM response": final_llm_response
        },
        {
            "Guardrail metrics": {
                "answer": recommendation_text,
                "was_blocked": False,
                "blocked_at": "None",
                "faithfulness_score": faithfulness_res["faithfulness_score"],
                "citation_accuracy": citation_acc,
                "reason": None
            }
        }
    ]