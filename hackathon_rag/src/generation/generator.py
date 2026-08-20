"""
Generation module with integrated 2-layer safety & guardrail checks.
Instructs the LLM to output structured JSON adhering to the specified schema format.

Returns structured output containing:
  1. "LLM response": Recommendation, Evidence, Citation, and Confidence level.
  2. "Guardrail metrics": Execution status, blocking pipeline details, faithfulness score, and citation accuracy.
"""

import json
import logging
import re
import ollama
from src import config
from .rag_metrics import (
    REFUSAL_MESSAGE,
    calculate_citation_accuracy,
    calculate_faithfulness_hybrid,
    create_rag_safety_prompt,
    enforce_safety_guardrail,
    predict_safety,
)

logger = logging.getLogger(__name__)

# Keep the rest of generator.py as is, but remove the duplicate calculate_confidence
# since it's now imported from rag_metrics


def calculate_confidence(
    faithfulness_score: float, was_blocked: bool, context: str
) -> str:
    """Helper function to map execution results to confidence level."""
    if was_blocked or not context or not context.strip():
        return "insufficient"
    elif faithfulness_score >= 0.7:
        return "high"
    else:
        return "low"


def clean_and_parse_llm_response(raw_output: str) -> dict:
    """Extract and clean nested JSON from LLM response.

    Handles cases where the LLM nests JSON inside the Recommendation field.
    """
    try:
        # First, try to parse as-is
        data = json.loads(raw_output)
    except json.JSONDecodeError:
        # If that fails, try to extract JSON from markdown code blocks
        json_match = re.search(r"```json\s*(\{.*?\})\s*```", raw_output, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group(1))
            except Exception:
                # Last resort: try to find any JSON object
                json_match = re.search(r"\{.*\}", raw_output, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group(0))
                else:
                    raise
        else:
            raise

    # Check for nested JSON in Recommendation field
    if "LLM response" in data:
        response = data["LLM response"]

        # Handle both possible spellings
        rec_field = response.get("Recommendation") or response.get(
            "Recomendation", ""
        )

        if isinstance(rec_field, str) and "```json" in rec_field:
            # Extract inner JSON from the Recommendation string
            inner_match = re.search(
                r"```json\s*(\{.*?\})\s*```", rec_field, re.DOTALL
            )
            if inner_match:
                try:
                    inner_data = json.loads(inner_match.group(1))
                    if "LLM response" in inner_data:
                        # Update with inner values (priority to inner)
                        for key, value in inner_data["LLM response"].items():
                            # Only update if the inner value is more complete
                            if value and (
                                not response.get(key)
                                or len(str(value)) > len(str(response.get(key, "")))
                            ):
                                response[key] = value
                except Exception:
                    pass
            else:
                # Try to extract just the JSON part without code block markers
                clean_rec = re.sub(r"```json\s*|\s*```", "", rec_field)
                try:
                    inner_data = json.loads(clean_rec)
                    if "LLM response" in inner_data:
                        for key, value in inner_data["LLM response"].items():
                            if value:
                                response[key] = value
                except Exception:
                    pass

        # Ensure consistent field names (prefer Recommendation over Recomendation)
        if "Recommendation" in response and "Recomendation" not in response:
            response["Recomendation"] = response["Recommendation"]
        elif "Recomendation" in response and "Recommendation" not in response:
            response["Recommendation"] = response["Recomendation"]

        # Clean the Recommendation field - ensure it's plain text
        if "Recommendation" in response and isinstance(
            response["Recommendation"], str
        ):
            # Remove any JSON-like artifacts
            response["Recommendation"] = re.sub(
                r"```json\s*|\s*```", "", response["Recommendation"]
            )
            # Remove any leftover JSON structure
            if response["Recommendation"].strip().startswith("{"):
                try:
                    # Try to extract text content if it's still a JSON string
                    temp = json.loads(response["Recommendation"])
                    if (
                        "LLM response" in temp
                        and "Recommendation" in temp["LLM response"]
                    ):
                        response["Recommendation"] = temp["LLM response"][
                            "Recommendation"
                        ]
                except Exception:
                    pass

    return data


def generate_answer(
    question: str, context: str, evidence_chunks: list[dict] = None
) -> list[dict]:
    """Generates an answer using a local Ollama model while enforcing input & output safety guardrails.

    Args:
        question (str): User query.
        context (str): Joined text content of retrieved chunks.
        evidence_chunks (list[dict]): List of dicts formatted as [{"text": ...,
          "page": ..., ...}] representing retrieved documents.

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
    chunk_evidence_text = (
        "\n---\n".join([c.get("text", "") for c in evidence_chunks])
        if evidence_chunks
        else context
    )
    citations = (
        [{k: v for k, v in c.items() if k != "text"} for c in evidence_chunks]
        if evidence_chunks
        else "No metadata available"
    )

    # =========================================================================
    # LAYER 1: Input Safety Filter (Pre-Generation Guardrail)
    # =========================================================================
    if not predict_safety(question):
        logger.warning(
            f"Query blocked at Layer 1 (Input Safety): '{question}'"
        )
        return [
            {
                "LLM response": {
                    "Recomendation": REFUSAL_MESSAGE,
                    "Evidence": "",
                    "Citation": [],
                    "Confidence": "insufficient",
                }
            },
            {
                "Guardrail metrics": {
                    "answer": REFUSAL_MESSAGE,
                    "was_blocked": True,
                    "blocked_at": "Layer 1 (Input Keyword Filter)",
                    "faithfulness_score": 0.0,
                    "citation_accuracy": 0.0,
                    "reason": (
                        "Query triggered input safety filters or unsafe medical"
                        " practices."
                    ),
                }
            },
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
                    "Confidence": "insufficient",
                }
            },
            {
                "Guardrail metrics": {
                    "answer": REFUSAL_MESSAGE,
                    "was_blocked": True,
                    "blocked_at": "Layer 1 (No Context)",
                    "faithfulness_score": 0.0,
                    "citation_accuracy": 0.0,
                    "reason": "No relevant context found in vector store.",
                }
            },
        ]

    # =========================================================================
    # GENERATION: Call Local Ollama Model with Structured Prompt
    # =========================================================================
    base_safety_prompt = create_rag_safety_prompt()
    # Prompt explaining structure and sections to the LLM
    system_prompt = (
        f"{base_safety_prompt}\n"
        "### OUTPUT FORMAT INSTRUCTIONS ###\n"
        "You MUST respond ONLY with a valid JSON object matching this exact"
        " schema:\n\n"
        "{\n"
        '  "LLM response": {\n'
        '    "Recommendation": "Your direct factual response to the question.'
        " Must be plain text with [Page X] citations. DO NOT use markdown, code"
        ' blocks, or nested JSON.",\n'
        '    "Evidence": "The exact verbatim excerpt from the provided'
        ' evidence.",\n'
        '    "Citation": "Source metadata (e.g., [Page 13] or {\\"page\\": 13,'
        ' \\"section\\": \\"recommendations\\"})",\n'
        '    "Confidence": "Choose exactly one: \'high\', \'low\', or'
        " 'insufficient'\"\n"
        "  }\n"
        "}\n\n"
        "### CRITICAL RULES ###\n"
        "1. The 'Recommendation' field MUST be plain text, NOT JSON, NOT"
        " markdown, NOT code blocks.\n"
        "2. Do NOT nest JSON objects inside the 'Recommendation' field.\n"
        "3. Provide ONLY the outer JSON object as your response.\n"
        "4. Use EXACT wording from the evidence where possible.\n"
        "5. Every factual claim must have a [Page X] citation.\n\n"
        "Example of CORRECT output:\n"
        "{\n"
        '  "LLM response": {\n'
        '    "Recommendation": "Avoid artesunate + SP with co-trimoxazole [Page'
        " 13], and avoid artesunate + amodiaquine with efavirenz or zidovudine"
        ' [Page 13].",\n'
        '    "Evidence": "In people who have HIV/AIDS and uncomplicated P.'
        " falciparum malaria, avoid artesunate + SP if they are being treated"
        ' with co-trimoxazole...",\n'
        '    "Citation": "[Page 13]",\n'
        '    "Confidence": "high"\n'
        "  }\n"
        "}\n\n"
        "Do NOT include any extra text outside the JSON object."
    )

    user_message = (
        f"Context Evidence:\n{context}\n\n"
        f"Available Chunk Citations Metadata: {json.dumps(citations)}\n\n"
        f"Question: {question}\n\n"
        "Generate the structured JSON response according to the schema"
        " provided."
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
                "temperature": 0.0,
            },
        )
        raw_llm_output = response["message"]["content"].strip()
        try:
            # Use the cleaning function to handle nested JSON
            cleaned_data = clean_and_parse_llm_response(raw_llm_output)
            llm_response_dict = cleaned_data.get("LLM response", {})
            raw_generated_ans = llm_response_dict.get(
                "Recommendation"
            ) or llm_response_dict.get("Recomendation", raw_llm_output)

            # Clean up the answer text (remove any remaining code block markers)
            if isinstance(raw_generated_ans, str):
                raw_generated_ans = re.sub(
                    r"```json\s*|\s*```", "", raw_generated_ans
                )
                # If it's still JSON-like, try to extract the actual text
                if raw_generated_ans.strip().startswith("{"):
                    try:
                        temp = json.loads(raw_generated_ans)
                        if (
                            "LLM response" in temp
                            and "Recommendation" in temp["LLM response"]
                        ):
                            raw_generated_ans = temp["LLM response"][
                                "Recommendation"
                            ]
                    except Exception:
                        pass

            # Ensure we have all required fields
            if (
                "Evidence" not in llm_response_dict
                or not llm_response_dict["Evidence"]
            ):
                llm_response_dict["Evidence"] = chunk_evidence_text
            if (
                "Citation" not in llm_response_dict
                or not llm_response_dict["Citation"]
            ):
                llm_response_dict["Citation"] = citations
            if "Confidence" not in llm_response_dict:
                llm_response_dict["Confidence"] = "low"

        except Exception as e:
            logger.warning(f"Failed to parse LLM JSON output: {e}")
            raw_generated_ans = raw_llm_output
            llm_response_dict = {
                "Recommendation": raw_generated_ans,
                "Evidence": chunk_evidence_text,
                "Citation": citations,
                "Confidence": "low",
            }

    except Exception as e:
        logger.error(f"Error during Ollama generation: {e}")
        return [
            {
                "LLM response": {
                    "Recommendation": REFUSAL_MESSAGE,
                    "Evidence": "",
                    "Citation": [],
                    "Confidence": "insufficient",
                }
            },
            {
                "Guardrail metrics": {
                    "answer": REFUSAL_MESSAGE,
                    "was_blocked": True,
                    "blocked_at": "Generation Error",
                    "faithfulness_score": 0.0,
                    "citation_accuracy": 0.0,
                    "reason": f"Model inference error: {str(e)}",
                }
            },
        ]

    # =========================================================================
    # LAYER 2: Output Safety Guardrail & Faithfulness Verification
    # =========================================================================
    guardrail_res = enforce_safety_guardrail(
        generated_answer=raw_generated_ans,
        retrieved_context=context,
        threshold=0.4,
    )

    if guardrail_res["was_blocked"]:
        logger.warning(
            "Answer blocked at Layer 2 (Output Guardrail). Reason:"
            f" {guardrail_res['reason']}"
        )
        return [
            {
                "LLM response": {
                    "Recommendation": REFUSAL_MESSAGE,
                    "Evidence": chunk_evidence_text,
                    "Citation": citations,
                    "Confidence": "insufficient",
                }
            },
            {
                "Guardrail metrics": {
                    "answer": guardrail_res["final_answer"],
                    "was_blocked": True,
                    "blocked_at": "Layer 2 (Output Guardrail)",
                    "faithfulness_score": guardrail_res["faithfulness_score"],
                    "citation_accuracy": 0.0,
                    "reason": guardrail_res["reason"],
                }
            },
        ]

    # Calculate detailed Faithfulness and Citation Accuracy for valid outputs
    faithfulness_res = calculate_faithfulness_hybrid(
        answer=raw_generated_ans, evidence_chunks=evidence_chunks, threshold=0.4
    )
    citation_acc = calculate_citation_accuracy(faithfulness_res["details"])
    confidence_level = calculate_confidence(
        faithfulness_res["faithfulness_score"], False, context
    )

    # Ensure response parameters match the requested schema
    final_llm_response = {
        "Recommendation": raw_generated_ans,
        "Evidence": llm_response_dict.get("Evidence", chunk_evidence_text)
        or chunk_evidence_text,
        "Citation": llm_response_dict.get("Citation", citations) or citations,
        "Confidence": confidence_level,
    }

    return [
        {"LLM response": final_llm_response},
        {
            "Guardrail metrics": {
                "answer": raw_generated_ans,
                "was_blocked": False,
                "blocked_at": "None",
                "faithfulness_score": faithfulness_res["faithfulness_score"],
                "citation_accuracy": citation_acc,
                "reason": None,
            }
        },
    ]


if __name__ == "__main__":
    # Test sample call
    test_context = """Patients co-infected with HIV
    In people who have HIV/AIDS and uncomplicated P. falciparum malaria, avoid
    artesunate + SP if they are being treated with co-trimoxazole, and avoid
    artesunate + amodiaquine if they are being treated with efavirenz or zidovudine.
    Good practice statement"""
    test_chunks = [
        {"text": test_context, "page": 13, "section": "recommendations"}
    ]
    test_query = (
        "Which five artemisinin-based combination therapies (ACTs) are"
        " recommended for treating uncomplicated P. falciparum?"
    )

    res = generate_answer(test_query, test_context, test_chunks)
    print(json.dumps(res, indent=2))