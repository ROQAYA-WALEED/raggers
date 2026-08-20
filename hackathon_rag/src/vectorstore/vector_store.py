"""vector_store.py.

----------------
Thin wrapper around LangChain's Chroma vector store.
Supports multiple collections inside the same on-disk ChromaDB directory.
"""

import uuid
import chromadb
from langchain_chroma import Chroma
from langchain_core.documents import Document
from src import config
from src.embedder import embedder


class VectorStore:

    def __init__(self, collection_name: str = config.COLLECTION_NAME):
        # Guarantee absolute path string
        self.persist_directory = str(config.CHROMA_DIR.resolve())
        self.collection_name = collection_name
        
        # Explicitly initialize PersistentClient with absolute path
        self.chroma_client = chromadb.PersistentClient(path=self.persist_directory)
        self._init_vector_store(self.collection_name)

    def _init_vector_store(self, collection_name: str):
        """Connects to a specific collection inside ChromaDB."""
        self.collection_name = collection_name
        self.vector_store = Chroma(
            collection_name=collection_name,
            embedding_function=embedder,
            persist_directory=self.persist_directory,
            collection_metadata={"hnsw:space": "cosine"},
        )

    def switch_collection(self, collection_name: str):
        """Switch active collection without creating a new VectorStore instance."""
        self._init_vector_store(collection_name)

    def add_chunks(
        self,
        chunks: list[dict],
        embeddings: list[list[float]] = None,
        collection_name: str = None,
    ):
        """Stores chunks into the active or specified collection."""
        if collection_name and collection_name != self.collection_name:
            self.switch_collection(collection_name)

        documents = []
        ids = []

        for item in chunks:
            content = item.get("text") or item.get("page_content", "")
            metadata = {
                "source": item.get(
                    "source",
                    getattr(config, "SELECTED_RAW_FILENAME", "unknown"),
                )
            }
            if item.get("page") is not None:
                metadata["page"] = item["page"]
            if item.get("section") is not None:
                metadata["section"] = item["section"]

            documents.append(Document(page_content=content, metadata=metadata))
            ids.append(str(item.get("id") or uuid.uuid4()))

        self.vector_store.add_documents(documents=documents, ids=ids)

    def query(
        self,
        query_text_or_embedding,
        top_k: int = config.TOP_K,
        collection_name: str = None,
    ) -> list[dict]:
        """Queries the active or specified collection."""
        if collection_name and collection_name != self.collection_name:
            self.switch_collection(collection_name)

        if isinstance(query_text_or_embedding, str):
            results = self.vector_store.similarity_search_with_score(
                query=query_text_or_embedding, k=top_k
            )
        else:
            results = self.vector_store.similarity_search_by_vector_with_relevance_scores(
                embedding=query_text_or_embedding, k=top_k
            )

        matches = []
        for doc, score in results:
            match = {
                "text": doc.page_content,
                "source": doc.metadata.get("source", "unknown"),
                "distance": score,
            }
            if "page" in doc.metadata:
                match["page"] = doc.metadata["page"]
            if "section" in doc.metadata:
                match["section"] = doc.metadata["section"]
            matches.append(match)

        return matches

    def reset_collection(self, collection_name: str = None):
        """Deletes ONLY the specified collection, preserving all other collections."""
        target = collection_name or self.collection_name
        try:
            # Re-init target first to make sure reference is active
            self._init_vector_store(target)
            self.vector_store.delete_collection()
            print(f"🗑️ Deleted collection: {target}")
            # Re-initialize empty collection with same name
            self._init_vector_store(target)
        except Exception as e:
            print(f"⚠️ Could not reset collection '{target}': {e}")

    def count(self, collection_name: str = None) -> int:
        """Returns document count for active or target collection."""
        if collection_name and collection_name != self.collection_name:
            self.switch_collection(collection_name)
        try:
            return self.vector_store._collection.count()
        except Exception:
            return 0


# Default instance initialized with config.COLLECTION_NAME
vector_store = VectorStore()