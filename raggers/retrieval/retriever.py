from .reranker import Reranker
from ..vectorstore.chroma.chroma_store import ChromaStore
from ..embeddings.embedder import get_embedding_model
from rank_bm25 import BM25Okapi
import pickle
import numpy as np
from typing import List, Dict, Any
import yaml
import os

def get_project_root():
    return os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

class HybridRetriever:
    def __init__(self, config_path: str = "config.yaml"):
        project_root = get_project_root()
        if not os.path.isabs(config_path):
            config_path = os.path.join(project_root, config_path)
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.chroma = ChromaStore(
            collection_name=self.config['collection_name'],
            persist_directory=os.path.join(project_root, "chroma_db")
        )
        self.reranker = Reranker(model_name=self.config['embedding_model_reranker'])

        # Load BM25 data (if exists)
        bm25_path = os.path.join(project_root, "assets", "bm25_data.pkl")
        try:
            with open(bm25_path, "rb") as f:
                data = pickle.load(f)
                self.bm25_ids = data["ids"]
                self.bm25_texts = data["texts"]
                tokenized_corpus = [doc.lower().split() for doc in self.bm25_texts]
                self.bm25 = BM25Okapi(tokenized_corpus)
        except FileNotFoundError:
            self.bm25 = None
            self.bm25_ids = []
            self.bm25_texts = []
            print("⚠️ Warning: BM25 data not found. Dense‑only retrieval will be used.")

    def hybrid_search(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        if top_k is None:
            top_k = self.config.get('top_k_retrieve', 10)

        # Dense search (always available)
        embed_model = get_embedding_model(self.config['embedding_model_dense'])
        query_emb = embed_model._get_query_embedding(query)
        dense_results = self.chroma.query(query_emb, top_k=top_k)
        dense_ids = dense_results['ids'][0]
        dense_docs = dense_results['documents'][0]
        dense_metadatas = dense_results['metadatas'][0]
        dense_distances = dense_results['distances'][0]

        # Build dense results dict
        dense_dict = {id_: {"doc": doc, "meta": meta, "score": 1 - (dist / 2.0)}
                      for id_, doc, meta, dist in zip(dense_ids, dense_docs, dense_metadatas, dense_distances)}

        # If BM25 not available, return dense results only
        if self.bm25 is None:
            results = []
            for id_ in dense_ids[:top_k]:
                results.append({
                    "id": id_,
                    "text": dense_dict[id_]["doc"],
                    "metadata": dense_dict[id_]["meta"],
                    "score": dense_dict[id_]["score"]
                })
            return results

        # Sparse (BM25) search
        tokenized_query = query.lower().split()
        bm25_scores = self.bm25.get_scores(tokenized_query)
        bm25_indices = np.argsort(bm25_scores)[::-1][:top_k]
        bm25_ids = [self.bm25_ids[i] for i in bm25_indices]
        bm25_scores = [bm25_scores[i] for i in bm25_indices]

        # Combine scores (weighted average, can be improved)
        combined = {}
        for idx, id_ in enumerate(dense_ids):
            combined[id_] = {
                "doc": dense_docs[idx],
                "meta": dense_metadatas[idx],
                "score": dense_dict[id_]["score"],
                "source": "dense"
            }

        max_bm25 = max(bm25_scores) if bm25_scores else 1
        for id_, score in zip(bm25_ids, bm25_scores):
            norm_bm25 = score / max_bm25
            if id_ in combined:
                combined[id_]["score"] = (combined[id_]["score"] + norm_bm25) / 2
                combined[id_]["source"] = "hybrid"
            else:
                # Only in BM25 – need text and metadata
                idx = self.bm25_ids.index(id_)
                combined[id_] = {
                    "doc": self.bm25_texts[idx],
                    "meta": {},  # No metadata from BM25; could fetch from Chroma if needed
                    "score": norm_bm25,
                    "source": "sparse"
                }

        # Sort by combined score descending
        sorted_ids = sorted(combined.keys(), key=lambda k: combined[k]["score"], reverse=True)
        results = []
        for id_ in sorted_ids[:top_k]:
            results.append({
                "id": id_,
                "text": combined[id_]["doc"],
                "metadata": combined[id_]["meta"],
                "score": combined[id_]["score"]
            })
        return results

    def retrieve(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        candidates = self.hybrid_search(query, top_k=self.config.get('top_k_retrieve', 10))
        reranked = self.reranker.rerank(query, candidates, top_k=self.config.get('top_k_rerank', 3))
        return reranked