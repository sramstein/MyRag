from src.config import EmbeddingConfig
from src.embeddings.base import BaseEmbedding
from src.embeddings.fastembed_emb import FastEmbedEmbedding
from src.embeddings.gemini_emb import GeminiEmbedding

def get_embedding_model(config: EmbeddingConfig) -> BaseEmbedding:
    """Factory to instantiate the configured embedding provider."""
    provider = config.provider.lower()
    if provider == "gemini":
        return GeminiEmbedding(model_name=config.model_name)
    elif provider == "local":
        return FastEmbedEmbedding(model_name=config.model_name, batch_size=config.batch_size)
    else:
        # Default to local
        return FastEmbedEmbedding(model_name=config.model_name, batch_size=config.batch_size)
