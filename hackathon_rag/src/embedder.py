"""
embedder.py
-----------
Unified embedding wrapper that handles Hugging Face, local Ollama models, 
and local paths based on project configuration.
"""

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import OllamaEmbeddings
from src import config


class Embedder:
    """Dynamically loads and manages vector embedding models across different backends."""

    def __init__(self):
        if getattr(config, "OLLAMA", False):
            print(f"⚙️ Initializing Ollama Embeddings model: {config.EMBEDDING_MODEL}")
            self.model = OllamaEmbeddings(
                model=config.EMBEDDING_MODEL,
                base_url=getattr(config, "OLLAMA_BASE_URL", "http://localhost:11434"),
            )

        elif getattr(config, "HUGGINGFACE", True):
            print(f"⚙️ Initializing Hugging Face Embeddings model: {config.EMBEDDING_MODEL}")
            self.model = HuggingFaceEmbeddings(
                model_name=config.EMBEDDING_MODEL,
                model_kwargs={"device": getattr(config, "DEVICE", "cpu")},
                encode_kwargs={"normalize_embeddings": True},
            )

        else:
            raise ValueError(
                "❌ Invalid configuration: Neither OLLAMA nor HUGGINGFACE is set to True in config.py."
            )

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed a batch of document chunks (used during ingestion)."""
        if not texts:
            return []
        return self.model.embed_documents(texts)

    def embed_query(self, text: str) -> list[float]:
        """Embed a single user question (used during retrieval)."""
        if not text.strip():
            return []
        return self.model.embed_query(text)


# Single shared instance across the app
embedder = Embedder()