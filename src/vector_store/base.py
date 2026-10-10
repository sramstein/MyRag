from abc import ABC, abstractmethod
from typing import Any, Dict, List
from pydantic import BaseModel

class SearchResult(BaseModel):
    chunk_id: str
    text: str
    score: float
    metadata: Dict[str, Any]

class BaseVectorStore(ABC):
    @abstractmethod
    def initialize(self, vector_dimension: int) -> None:
        """Initialize collection if needed."""
        pass

    @abstractmethod
    def upsert(self, chunk_ids: List[str], vectors: List[List[float]], texts: List[str], metadatas: List[Dict[str, Any]]) -> None:
        """Upsert vectors with payload texts and metadata."""
        pass

    @abstractmethod
    def search(self, query_vector: List[float], top_k: int = 4, score_threshold: float = 0.0) -> List[SearchResult]:
        """Search similar vectors and return results."""
        pass

    @abstractmethod
    def count(self) -> int:
        """Return total number of vectors in collection."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Delete all points or reset collection."""
        pass
