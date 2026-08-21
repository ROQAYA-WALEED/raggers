# src/main.py
from contextlib import asynccontextmanager
from typing import Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from src.rag_pipeline import initialize_pipeline, run_rag_pipeline


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs initialization ONCE when server boots up
    initialize_pipeline(force_reingest=False)
    yield


app = FastAPI(title="Medical RAG API", lifespan=lifespan)


class QueryRequest(BaseModel):
    question: str = Field(
        ...,
        json_schema_extra={
            "example": "What is the recommended dose of artesunate?"
        },
    )


class QueryResponse(BaseModel):
    question: str
    recommendation: str | None = None
    evidence: Any | None = None
    citation: Any | None = None
    confidence: Any | None = None
    guardrail_metrics: dict[str, Any] | None = None


@app.get("/")
def read_root():
    return {"status": "online", "message": "Medical RAG API is live"}


@app.post("/api/v1/query", response_model=QueryResponse)
def handle_query(request: QueryRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        result = run_rag_pipeline(request.question)

        # Extract answer from guardrail metrics if recommendation is empty
        guardrail_metrics = result.get("guardrail_metrics", {})
        fallback_answer = guardrail_metrics.get("answer")

        if not result.get("recommendation") and fallback_answer:
            result["recommendation"] = fallback_answer

        return result
    except Exception as e:
        # Print actual error in server logs before raising
        print(f"Pipeline Error: {e}")
        raise HTTPException(
            status_code=500, detail=f"Internal Server Error: {str(e)}"
        )