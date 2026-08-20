"""
vector_store.py
----------------
Thin wrapper around a persistent ChromaDB collection.
Everything else in the app talks to Chroma through this class only.
"""

import chromadb
from src import config

from pathlib import Path
import chromadb

# Point directly to your project's chroma directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent
CHROMA_PATH = BASE_DIR / "chroma_db"  # Adjust "chroma_db" to match your folder name

class VectorStore:
    def __init__(self):
        # PersistentClient writes the db to disk (src/vectorstore/chroma)
        self.client = chromadb.PersistentClient(path=str(config.CHROMA_DIR))
        self.collection = self.client.get_or_create_collection(
            name=config.COLLECTION_NAME
        )

    def add_chunks(self, chunks: list[dict], embeddings: list[list[float]]):
        """
        Store chunks + their embeddings.
        chunks: [{"id", "source", "page", "text"}, ...]
        """
        metadatas = []
        for c in chunks:
            meta = {"source": c.get("source", "unknown")}
            # Only add 'page' to metadata if it exists and is not None
            if c.get("page") is not None:
                meta["page"] = c["page"]
            metadatas.append(meta)

        self.collection.upsert(
            ids=[c["id"] for c in chunks],
            embeddings=embeddings,
            documents=[c["text"] for c in chunks],
            metadatas=metadatas,
        )

    def query(self, query_embedding: list[float], top_k: int = config.TOP_K) -> list[dict]:
        """Return the top_k most similar chunks to the given query embedding."""
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
        )

        # Chroma returns parallel lists; zip them back into readable dicts
        matches = []
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        dists = results.get("distances", [[]])[0]
        
        for text, meta, dist in zip(docs, metas, dists):
            match = {
                "text": text,
                "source": meta.get("source", "unknown"),
                "distance": dist,
            }
            # Retrieve page from metadata if present
            if "page" in meta:
                match["page"] = meta["page"]
                
            matches.append(match)

        return matches

    def count(self) -> int:
        """Number of chunks currently stored (handy for debugging/UI)."""
        return self.collection.count()


# Single shared instance
vector_store = VectorStore()