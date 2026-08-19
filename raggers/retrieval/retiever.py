from .reranker import Reranker
from vectorstore.chroma.chroma_store import ChromaStore
from rank_bm25 import BM25Okapi
import pickle
import numpy as np
from typing import List, Dict, Any
import yaml

class HybridRetriever:
    def __init__(self, config_path: str = "config.yaml"):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        self.chroma = ChromaStore(collection_name=self.config['collection_name'])
        self.reranker = Reranker(model_name=self.config['embedding_model_reranker'])

        # Load BM25 data
        with open("assets/bm25_data.pkl", "rb") as f:
            data = pickle.load(f)
            self.bm25_ids = data["ids"]
            self.bm25_texts = data["texts"]
            # Tokenize for BM25 (simple whitespace tokenizer)
            tokenized_corpus = [doc.lower().split() for doc in self.bm25_texts]
            self.bm25 = BM25Okapi(tokenized_corpus)

    def hybrid_search(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        if top_k is None:
            top_k = self.config.get('top_k_retrieve', 10)

        # 1. Dense retrieval from Chroma
        # Get query embedding (use same embedder as during ingestion – we need to load it)
        from ingestion.embedder import get_embedding_model
        embed_model = get_embedding_model(self.config['embedding_model_dense'])
        query_emb = embed_model._get_query_embedding(query)
        dense_results = self.chroma.query(query_emb, top_k=top_k)
        # dense_results: {"ids": [[...]], "documents": [[...]], "metadatas": [[...]], "distances": [[...]]}
        dense_ids = dense_results['ids'][0]
        dense_docs = dense_results['documents'][0]
        dense_metadatas = dense_results['metadatas'][0]
        dense_scores = dense_results['distances'][0]  # lower is better

        # Build a dict for dense
        dense_dict = {id_: {"doc": doc, "meta": meta, "score": score} for id_, doc, meta, score in zip(dense_ids, dense_docs, dense_metadatas, dense_scores)}

        # 2. Sparse (BM25) retrieval
        # Tokenize query
        tokenized_query = query.lower().split()
        bm25_scores = self.bm25.get_scores(tokenized_query)
        # Get top_k BM25 results (by score descending)
        bm25_indices = np.argsort(bm25_scores)[::-1][:top_k]
        bm25_ids = [self.bm25_ids[i] for i in bm25_indices]
        bm25_scores = [bm25_scores[i] for i in bm25_indices]

        # 3. Combine scores (take union)
        # We'll use a simple reciprocal rank fusion (RRF) or sum of normalized scores.
        # For simplicity, we'll do a weighted sum: dense_score (normalized) + sparse_score.
        # First, normalize dense distances to similarity: 1 - distance (if distance is cosine, range [0,2])
        # Better: use similarity = 1 - (distance/2)
        combined = {}
        for idx, id_ in enumerate(dense_ids):
            norm_sim = 1 - (dense_results['distances'][0][idx] / 2.0)  # map to [0,1]
            combined[id_] = {"doc": dense_docs[idx], "meta": dense_metadatas[idx], "score": norm_sim, "source": "dense"}

        for id_, score in zip(bm25_ids, bm25_scores):
            # BM25 score is unbounded, we need to normalize per query
            # We'll use min-max scaling across the BM25 results
            # For now, just add to combined if not present, else average
            norm_bm25 = score / max(bm25_scores) if max(bm25_scores) > 0 else 0
            if id_ in combined:
                # combine scores: average
                combined[id_]["score"] = (combined[id_]["score"] + norm_bm25) / 2
                combined[id_]["source"] = "hybrid"
            else:
                # we need the document text and metadata for BM25-only results
                # we stored text and ids; we can retrieve from bm25_texts
                idx = self.bm25_ids.index(id_)
                combined[id_] = {
                    "doc": self.bm25_texts[idx],
                    "meta": {},  # we don't have metadata from BM25 alone; could fetch from chroma if needed
                    "score": norm_bm25,
                    "source": "sparse"
                }

        # Sort combined by score descending
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
        # Hybrid search
        candidates = self.hybrid_search(query, top_k=self.config.get('top_k_retrieve', 10))
        # Rerank
        reranked = self.reranker.rerank(query, candidates, top_k=self.config.get('top_k_rerank', 3))
        return reranked