"""
rag_metrics.py
------------
Metrics and evaluation functions for RAG system.
"""

import json
import logging
import ollama
from src import config

logger = logging.getLogger(__name__)

# Define REFUSAL_MESSAGE here
REFUSAL_MESSAGE = "I cannot provide an answer due to safety concerns or insufficient information."


def calculate_confidence(faithfulness_score: float, was_blocked: bool, context: str) -> str:
    """Helper function to map execution results to confidence level."""
    if was_blocked or not context or not context.strip():
        return "insufficient"
    elif faithfulness_score >= 0.6:
        return "high"
    else:
        return "low"


def create_rag_safety_prompt() -> str:
    """Create the safety prompt for RAG system."""
    return """
You are a medical information assistant. Follow these safety guidelines:
1. Only use information from the provided context
2. Do not provide medical advice or diagnoses
3. Cite sources with page numbers
4. If information is not in context, say so
"""


def predict_safety(question: str) -> bool:
    """Check if question passes safety filter."""
    # Implement your safety check logic here
    unsafe_keywords = ["kill", "suicide", "illegal", "harm"]
    return not any(keyword in question.lower() for keyword in unsafe_keywords)


def enforce_safety_guardrail(generated_answer: str, retrieved_context: str, 
                            evidence_chunks: list = None, threshold: float = 0.4,
                            use_semantic: bool = False) -> dict:
    """Enforce safety guardrail on generated answer."""
    # Implement guardrail logic here
    return {
        "was_blocked": False,
        "final_answer": generated_answer,
        "faithfulness_score": 0.8,
        "reason": None
    }


def calculate_faithfulness_hybrid(answer: str, evidence_chunks: list, 
                                 threshold: float = 0.4, use_semantic: bool = False) -> dict:
    """Calculate faithfulness score."""
    # Implement faithfulness calculation
    return {
        "faithfulness_score": 0.8,
        "details": [
            {"claim": "Test claim", "supported": True, "citation": "Page 1"}
        ]
    }


def calculate_citation_accuracy(details: list) -> float:
    """Calculate citation accuracy."""
    if not details:
        return 0.0
    supported = sum(1 for d in details if d.get("supported", False))
    return supported / len(details)