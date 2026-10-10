from typing import List, Optional
from fastembed import TextEmbedding
from src.embeddings.base import BaseEmbedding

class FastEmbedEmbedding(BaseEmbedding):
    """Local, offline, zero-cost ONNX embeddings via FastEmbed."""

    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5", batch_size: int = 32):
        self.model_name = model_name
        self.batch_size = batch_size
        self._model: Optional[TextEmbedding] = None
        self._dim: Optional[int] = None

    @property
    def model(self) -> TextEmbedding:
        if self._model is None:
            self._model = TextEmbedding(model_name=self.model_name)
        return self._model

    @property
    def dimension(self) -> int:
        if self._dim is None:
            sample = self.embed_query("test")
            self._dim = len(sample)
        return self._dim

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        embeddings = list(self.model.embed(texts, batch_size=self.batch_size))
        return [emb.tolist() for emb in embeddings]

    def embed_query(self, text: str) -> List[float]:
        # fastembed query embedding
        embeddings = list(self.model.query_embed(text))
        if embeddings:
            return embeddings[0].tolist()
        return [0.0] * (self._dim or 384)
