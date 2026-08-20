from fastapi import APIRouter, HTTPException
from .schemas import QueryRequest, QueryResponse, SourceInfo

router = APIRouter()

@router.post("/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest):
    try:
        # Lazy imports – only when the endpoint is called
        from ..retrieval.retriever import HybridRetriever
        from ..generation.generator import StrictGenerator

        retriever = HybridRetriever()
        generator = StrictGenerator()

        docs = retriever.retrieve(request.query, top_k=request.top_k)
        if not docs:
            return QueryResponse(
                answer="I cannot answer this question because the required information is not present in the provided document.",
                sources=[]
            )
        answer = generator.generate(request.query, docs)
        sources = [SourceInfo(**doc) for doc in docs]
        return QueryResponse(answer=answer, sources=sources)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))