from abc import ABC, abstractmethod
from typing import List

class BaseEmbedding(ABC):
    @property
    @abstractmethod
    def dimension(self) -> int:
        """Returns the embedding vector dimension."""
        pass

    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embeds a list of document strings."""
        pass

    @abstractmethod
    def embed_query(self, text: str) -> List[float]:
        """Embeds a single query string."""
        pass
