"""
embedder.py
-----------
Thin wrapper around fastembed so the rest of the app doesn't need
to know which embedding library we're using.
"""

from sentence_transformers import SentenceTransformer
from src import config


class Embedder:
    """Turns text into vectors using a local embedding model."""

    def __init__(self, model_name: str = config.EMBEDDING_MODEL):
        # sentence-transformers downloads the model once and caches it locally
        self.model = SentenceTransformer(model_name)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed a batch of chunks (used during ingestion)."""
        # sentence-transformers returns a numpy array -> convert to plain list
        return [vector.tolist() for vector in self.model.encode(texts)]

    def embed_query(self, text: str) -> list[float]:
        """Embed a single user question (used during retrieval)."""
        return self.embed_documents([text])[0]


# Single shared instance so we don't reload the model everywhere it's used
embedder = Embedder()