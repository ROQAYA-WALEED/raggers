"""
main.py
-------
FastAPI entrypoint. Run with:
    uvicorn src.main:app --reload

This is the "backend" version of the chatbot (used if you want an HTTP API
instead of / alongside the Streamlit UI in app.py).
"""

from fastapi import FastAPI
from src.api.routes import router

app = FastAPI(title="AutoEngineer RAG Chatbot")
app.include_router(router)
