import chromadb
from chromadb.config import Settings
from typing import List, Optional

class ChromaStore:
    def __init__(self, collection_name: str, persist_directory: str = "./chroma_db"):
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def add_documents(self, ids: List[str], documents: List[str], embeddings: List[List[float]], metadatas: List[dict]):
        self.collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )

    def query(self, query_embedding: List[float], top_k: int) -> dict:
        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )