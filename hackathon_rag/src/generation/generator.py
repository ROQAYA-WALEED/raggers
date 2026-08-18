"""
generator.py
------------
Sends the retrieved context + user question to a local Llama model and returns the answer.
"""

import ollama
from src import config

SYSTEM_PROMPT = (
    "You are a helpful assistant that answers questions using ONLY the "
    "provided context. If the context doesn't contain the answer, say so "
    "honestly instead of guessing."
)


def generate_answer(question: str, context: str) -> str:
    """Call local Llama with the question + retrieved context, return plain text answer."""
    user_message = (
        f"Context:\n{context}\n\n"
        f"Question: {question}\n\n"
        "Answer using only the context above."
    )

    response = ollama.chat(
        model=config.LLM_MODEL,  # e.g., "llama3" or "llama3.2"
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        options={
            "num_predict": config.MAX_TOKENS,
        },
    )

    return response["message"]["content"]