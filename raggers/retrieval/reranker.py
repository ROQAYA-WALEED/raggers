from sentence_transformers import CrossEncoder
from typing import List, Dict, Any

class Reranker:
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model = CrossEncoder(model_name)

    def rerank(self, query: str, candidates: List[Dict[str, Any]], top_k: int = 3) -> List[Dict[str, Any]]:
        if not candidates:
            return []
        pairs = [(query, cand["text"]) for cand in candidates]
        scores = self.model.predict(pairs)
        # Sort by score descending
        scored = list(zip(candidates, scores))
        scored.sort(key=lambda x: x[1], reverse=True)
        top = scored[:top_k]
        results = []
        for cand, score in top:
            res = cand.copy()
            res["rerank_score"] = float(score)
            results.append(res)
        return results