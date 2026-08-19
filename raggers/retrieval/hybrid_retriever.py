from llama_index.core import VectorStoreIndex
from llama_index.core.retrievers import BM25Retriever
from llama_index.core.retrievers import RouterRetriever
from llama_index.core.selectors import PydanticSingleSelector
from llama_index.core.retrievers import BaseRetriever
from typing import List, Tuple
from config.settings import SPARSE_WEIGHT, DENSE_WEIGHT, TOP_K_INITIAL, TOP_K_FINAL
import numpy as np

class HybridRetriever(BaseRetriever):
    def __init__(self, index: VectorStoreIndex, sparse_retriever: BM25Retriever, dense_weight=0.7, sparse_weight=0.3, initial_k=10):
        self._dense_retriever = index.as_retriever(similarity_top_k=initial_k)
        self._sparse_retriever = sparse_retriever
        self.dense_weight = dense_weight
        self.sparse_weight = sparse_weight
        self.initial_k = initial_k
        super().__init__()

    def _retrieve(self, query: str):
        # Get dense results
        dense_nodes = self._dense_retriever.retrieve(query)
        # Get sparse results
        sparse_nodes = self._sparse_retriever.retrieve(query)
        
        # Combine scores (normalize)
        all_nodes = {}
        # Dense scores: assume they are similarity (0-1) or cosine
        for node in dense_nodes:
            all_nodes[node.node_id] = {'node': node, 'dense_score': node.score, 'sparse_score': 0.0}
        for node in sparse_nodes:
            if node.node_id in all_nodes:
                all_nodes[node.node_id]['sparse_score'] = node.score
            else:
                all_nodes[node.node_id] = {'node': node, 'dense_score': 0.0, 'sparse_score': node.score}
        
        # Compute hybrid score: weighted sum (normalize both to [0,1] per type)
        dense_scores = [item['dense_score'] for item in all_nodes.values()]
        sparse_scores = [item['sparse_score'] for item in all_nodes.values()]
        if dense_scores:
            max_dense = max(dense_scores)
            min_dense = min(dense_scores)
            range_dense = max_dense - min_dense if max_dense != min_dense else 1
        if sparse_scores:
            max_sparse = max(sparse_scores)
            min_sparse = min(sparse_scores)
            range_sparse = max_sparse - min_sparse if max_sparse != min_sparse else 1
        
        for item in all_nodes.values():
            dense_norm = (item['dense_score'] - min_dense) / range_dense if range_dense else 0.5
            sparse_norm = (item['sparse_score'] - min_sparse) / range_sparse if range_sparse else 0.5
            item['hybrid_score'] = self.dense_weight * dense_norm + self.sparse_weight * sparse_norm
        
        # Sort by hybrid score descending and return top initial_k
        sorted_items = sorted(all_nodes.values(), key=lambda x: x['hybrid_score'], reverse=True)
        # Return NodeWithScore objects
        from llama_index.core.schema import NodeWithScore
        results = []
        for item in sorted_items[:self.initial_k]:
            node = item['node']
            node.score = item['hybrid_score']
            results.append(NodeWithScore(node=node, score=item['hybrid_score']))
        return results