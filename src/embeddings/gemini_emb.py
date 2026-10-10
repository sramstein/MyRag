import os
from typing import List, Optional
from src.embeddings.base import BaseEmbedding

class GeminiEmbedding(BaseEmbedding):
    """Google Gemini API Embeddings via the official google-genai SDK."""

    def __init__(self, model_name: str = "gemini-embedding-001", api_key: Optional[str] = None):
        from google import genai

        self.model_name = model_name
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable or argument is required for Gemini embeddings.")
        self.client = genai.Client(api_key=self.api_key)
        self._dim: Optional[int] = None

    @property
    def dimension(self) -> int:
        if self._dim is None:
            sample = self.embed_query("dimension test")
            self._dim = len(sample)
        return self._dim

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        
        # Batch calls to client.models.embed_content
        embeddings: List[List[float]] = []
        # Gemini handles batch contents
        batch_size = 50
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            response = self.client.models.embed_content(
                model=self.model_name,
                contents=batch,
            )
            for item in response.embeddings:
                embeddings.append(item.values)
        return embeddings

    def embed_query(self, text: str) -> List[float]:
        response = self.client.models.embed_content(
            model=self.model_name,
            contents=text,
        )
        return response.embeddings[0].values
