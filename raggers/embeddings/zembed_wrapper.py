from typing import List
from llama_index.core.embeddings import BaseEmbedding
from sentence_transformers import SentenceTransformer

class ZEmbedEmbedding(BaseEmbedding):
    def __init__(self, model_name: str = "zeroentropy/zembed-1", **kwargs):
        super().__init__()
        self._model = SentenceTransformer(
            model_name,
            trust_remote_code=True,
            model_kwargs={"torch_dtype": "float32"},
        )
        self._embedding_dim = 2560

    def _get_query_embedding(self, query: str) -> List[float]:
        return self._model.encode_query(query).tolist()

    def _get_text_embedding(self, text: str) -> List[float]:
        return self._model.encode_document([text])[0].tolist()

    def _get_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        return [emb.tolist() for emb in self._model.encode_document(texts)]

    async def _aget_query_embedding(self, query: str) -> List[float]:
        return self._get_query_embedding(query)
    async def _aget_text_embedding(self, text: str) -> List[float]:
        return self._get_text_embedding(text)
    async def _aget_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        return self._get_text_embeddings(texts)

    @property
    def class_name(self) -> str:
        return "ZEmbedEmbedding"
    @property
    def embedding_dim(self) -> int:
        return self._embedding_dim