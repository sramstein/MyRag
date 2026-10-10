from src.config import VectorDbConfig
from src.vector_store.base import BaseVectorStore
from src.vector_store.qdrant_store import QdrantStore

def get_vector_store(config: VectorDbConfig) -> BaseVectorStore:
    """Factory to instantiate the configured vector store."""
    if config.provider.lower() == "qdrant":
        return QdrantStore(
            collection_name=config.collection_name,
            storage_path=config.storage_path,
            qdrant_url=config.qdrant_url,
            qdrant_api_key=config.qdrant_api_key,
        )
    elif config.provider.lower() == "memory":
        return QdrantStore(
            collection_name=config.collection_name,
            storage_path=":memory:",
        )
    else:
        # Default to local Qdrant
        return QdrantStore(
            collection_name=config.collection_name,
            storage_path=config.storage_path,
        )
