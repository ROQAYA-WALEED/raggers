from pydantic import BaseModel
from typing import List, Optional

class QueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5

class DocumentResult(BaseModel):
    text: str
    score: float

class QueryResponse(BaseModel):
    results: List[DocumentResult]