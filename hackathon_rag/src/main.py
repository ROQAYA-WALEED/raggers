# src/api/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.rag_pipeline import run_rag_pipeline, initialize_pipeline

app = FastAPI(title="Medical RAG API")

initialize_pipeline(force_reingest=True)  # Ensure vector store is ready on startup

class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    question: str
    answer: str 
    sources: list[dict]


@app.get("/")
def read_root():
    return {"Hello": "World"}


# Flutter App: Makes an HTTP POST request to http://<YOUR_SERVER_IP>:8000/api/v1/query with body {"question": "What is the primary vector for malaria?"}
@app.post("/api/v1/query", response_model=QueryResponse)
def handle_query(request: QueryRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    result = run_rag_pipeline(request.question)
    return result
