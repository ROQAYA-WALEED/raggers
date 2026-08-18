"""
embedder.py
-----------
Thin wrapper around fastembed so the rest of the app doesn't need
to know which embedding library we're using.
"""

from fastembed import TextEmbedding
from src import config


class Embedder:
    """Turns text into vectors using a local embedding model."""

    def __init__(self, model_name: str = config.EMBEDDING_MODEL):
        # fastembed downloads the model once and caches it locally
        self.model = TextEmbedding(model_name=model_name)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed a batch of chunks (used during ingestion)."""
        # fastembed returns a generator of numpy arrays -> convert to plain lists
        return [vector.tolist() for vector in self.model.embed(texts)]

    def embed_query(self, text: str) -> list[float]:
        """Embed a single user question (used during retrieval)."""
        return self.embed_documents([text])[0]


# Single shared instance so we don't reload the model everywhere it's used
embedder = Embedder()