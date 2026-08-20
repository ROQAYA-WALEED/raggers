from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class QueryRequest(BaseModel):
    query: str
    top_k: int = 3

class SourceInfo(BaseModel):
    id: str
    text: str
    metadata: Dict[str, Any]
    score: float
    rerank_score: Optional[float] = None

class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceInfo]