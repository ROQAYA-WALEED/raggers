"""
generator.py
------------
Generation module with integrated 2-layer safety & guardrail checks.
Instructs the LLM to output structured JSON adhering to the specified schema format.

Returns structured output containing:
  1. "LLM response": Recommendation, Evidence, Citation, and Confidence level.
  2. "Guardrail metrics": Execution status, blocking pipeline details, faithfulness score, and citation accuracy.
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

# Run this file using --> python -m src.generation.generator
logger = logging.getLogger(__name__)


def calculate_confidence(faithfulness_score: float, was_blocked: bool, context: str) -> str:
    """Helper function to map execution results to confidence level."""
    if was_blocked or not context or not context.strip():
        return "insufficient"
    elif faithfulness_score >= 0.7:
        return "high"
    else:
        return "low"


def generate_answer(
    question: str, 
    context: str, 
    evidence_chunks: list[dict] = None
) -> list[dict]:
    """
    Generates an answer using a local Ollama model while enforcing input & output safety guardrails.

    Args:
        question (str): User query.
        context (str): Joined text content of retrieved chunks.
        evidence_chunks (list[dict]): List of dicts formatted as [{"text": ..., "page": ..., ...}] 
                                       representing retrieved documents.

    Returns:
        list[dict]: A list containing two dictionaries:
            [
                {
                    "LLM response": {
                        "Recomendation": str,
                        "Evidence": str,
                        "Citation": list | dict | str,
                        "Confidence": "high" | "low" | "insufficient"
                    }
                },
                {
                    "Guardrail metrics": {
                        "answer": str,
                        "was_blocked": bool,
                        "blocked_at": str,
                        "faithfulness_score": float,
                        "citation_accuracy": float,
                        "reason": str | None
                    }
                }
            ]
    """
    if evidence_chunks is None:
        evidence_chunks = []

    # Extract metadata/citations from provided evidence chunks
    chunk_evidence_text = "\n---\n".join([c.get("text", "") for c in evidence_chunks]) if evidence_chunks else context
    citations = [
        {k: v for k, v in c.items() if k != "text"} 
        for c in evidence_chunks
    ] if evidence_chunks else "No metadata available"

    # =========================================================================
    # LAYER 1: Input Safety Filter (Pre-Generation Guardrail)
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

    # If retrieved context is empty, refuse immediately
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
    # GENERATION: Call Local Ollama Model with Structured Prompt
    # =========================================================================
    base_safety_prompt = create_rag_safety_prompt()
    
    # Prompt explaining structure and sections to the LLM
    system_prompt = (
        f"{base_safety_prompt}\n"
        "### OUTPUT FORMAT INSTRUCTIONS ###\n"
        "You MUST respond ONLY with a valid JSON object matching this exact schema:\n\n"
        "{\n"
        '  "LLM response": {\n'
        '    "Recomendation": "Your direct factual response to the question strictly based on context. Add page citations in [Page X] format after each factual statement.",\n'
        '    "Evidence": "The exact verbatim excerpt or relevant context text from the provided evidence used to generate the answer.",\n'
        '    "Citation": "The metadata details, section names, or page numbers of the context source chunks used.",\n'
        '    "Confidence": "Choose exactly one: \'high\', \'low\', or \'insufficient\' based on how completely the evidence answers the query."\n'
        "  }\n"
        "}\n\n"
        "Detailed field definitions:\n"
        "- Recomendation (str): The main response text strictly answering the query. Must contain [Page X] markers.\n"
        "- Evidence (str): The actual context text provided that supports your answer.\n"
        "- Citation (list/dict/str): The source metadata and page numbers.\n"
        "- Confidence (str): Set to 'high' if fully supported by context, 'low' if partially supported, or 'insufficient' if context lacks information.\n\n"
        "Do NOT include any extra conversational text outside the JSON object."
    )

    user_message = (
        f"Context Evidence:\n{context}\n\n"
        f"Available Chunk Citations Metadata: {json.dumps(citations)}\n\n"
        f"Question: {question}\n\n"
        "Generate the structured JSON response according to the schema provided."
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
        
        # Parse JSON if output by LLM, fallback gracefully if output as raw text
        try:
            parsed_llm_json = json.loads(raw_llm_output)
            llm_response_dict = parsed_llm_json.get("LLM response", {})
            raw_generated_ans = llm_response_dict.get("Recomendation", raw_llm_output)
        except Exception:
            raw_generated_ans = raw_llm_output
            llm_response_dict = {
                "Recomendation": raw_generated_ans,
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
        generated_answer=raw_generated_ans,
        retrieved_context=context,
        threshold=0.4
    )

    if guardrail_res["was_blocked"]:
        logger.warning(f"Answer blocked at Layer 2 (Output Guardrail). Reason: {guardrail_res['reason']}")
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
                    "answer": guardrail_res["final_answer"],
                    "was_blocked": True,
                    "blocked_at": "Layer 2 (Output Guardrail)",
                    "faithfulness_score": guardrail_res["faithfulness_score"],
                    "citation_accuracy": 0.0,
                    "reason": guardrail_res["reason"]
                }
            }
        ]

    # Calculate detailed Faithfulness and Citation Accuracy for valid outputs
    faithfulness_res = calculate_faithfulness_hybrid(
        answer=raw_generated_ans,
        evidence_chunks=evidence_chunks,
        threshold=0.4
    )
    citation_acc = calculate_citation_accuracy(faithfulness_res["details"])
    confidence_level = calculate_confidence(faithfulness_res["faithfulness_score"], False, context)

    # Ensure response parameters match the requested schema
    final_llm_response = {
        "Recomendation": raw_generated_ans,
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
                "answer": raw_generated_ans,
                "was_blocked": False,
                "blocked_at": "None",
                "faithfulness_score": faithfulness_res["faithfulness_score"],
                "citation_accuracy": citation_acc,
                "reason": None
            }
        }
    ]


if __name__ == "__main__":
    # Test sample call
    test_context = "Malaria is caused by Plasmodium parasites transmitted through female Anopheles mosquitoes. [Page 12]"
    test_chunks = [{"text": test_context, "page": 12, "section": "1. Overview"}]
    test_query = "What causes malaria?"

    res = generate_answer(test_query, test_context, test_chunks)
    print(json.dumps(res, indent=2))