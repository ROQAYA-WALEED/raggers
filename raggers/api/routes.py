from fastapi import APIRouter, HTTPException
from .schemas import QueryRequest, QueryResponse
from retrieval.retriever import HybridRetriever
from generation.generator import StrictGenerator

router = APIRouter()
retriever = HybridRetriever()
generator = StrictGenerator()

@router.post("/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest):
    try:
        # Retrieve documents
        docs = retriever.retrieve(request.query, top_k=request.top_k)
        if not docs:
            return QueryResponse(
                answer="I cannot answer this question because the required information is not present in the provided document.",
                sources=[]
            )
        # Generate answer
        answer = generator.generate(request.query, docs)
        return QueryResponse(answer=answer, sources=docs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))