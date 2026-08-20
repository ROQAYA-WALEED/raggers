"""
schemas.py
----------
Pydantic request/response models for the API.
"""

from pydantic import BaseModel


class ChatRequest(BaseModel):
    question: str


class SourceChunk(BaseModel):
    text: str
    source: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceChunk]
