"""
routes.py
---------
FastAPI routes exposing the RAG pipeline over HTTP.
"""

from fastapi import APIRouter
from src.api.schemas import ChatRequest, ChatResponse, SourceChunk
from src.retrieval.retriever import retrieve, format_context
from src.generation.generator import generate_answer

router = APIRouter()


@router.get("/health")
def health():
    """Simple liveness check."""
    return {"status": "ok"}


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Full RAG round-trip:
      question -> retrieve relevant chunks -> ask Claude -> return answer + sources
    """
    chunks = retrieve(request.question)
    context = format_context(chunks)
    answer = generate_answer(request.question, context)

    sources = [SourceChunk(text=c["text"], source=c["source"]) for c in chunks]
    return ChatResponse(answer=answer, sources=sources)
