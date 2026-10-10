import os
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional
from qdrant_client import QdrantClient, models
from src.vector_store.base import BaseVectorStore, SearchResult

class QdrantStore(BaseVectorStore):
    """Qdrant Vector Database implementation.
    
    Supports:
    1. Local embedded disk mode (path="./data/qdrant_db") - 100% Free, zero external services!
    2. Qdrant Cloud Free Tier (url="https://...", api_key="...") - 1GB free cluster forever!
    3. In-memory mode (path=":memory:") - for tests.
    """

    def __init__(
        self,
        collection_name: str = "github_page_rag",
        storage_path: Optional[str] = "./data/qdrant_db",
        qdrant_url: Optional[str] = None,
        qdrant_api_key: Optional[str] = None,
    ):
        self.collection_name = collection_name
        self.vector_dimension: Optional[int] = None

        if qdrant_url:
            self.client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
        elif storage_path == ":memory:":
            self.client = QdrantClient(":memory:")
        else:
            resolved_path = Path(storage_path or "./data/qdrant_db").resolve()
            resolved_path.mkdir(parents=True, exist_ok=True)
            self.client = QdrantClient(path=str(resolved_path))

    def initialize(self, vector_dimension: int) -> None:
        self.vector_dimension = vector_dimension
        collections = self.client.get_collections().collections
        exists = any(c.name == self.collection_name for c in collections)
        if not exists:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=vector_dimension,
                    distance=models.Distance.COSINE
                ),
            )

    def upsert(
        self,
        chunk_ids: List[str],
        vectors: List[List[float]],
        texts: List[str],
        metadatas: List[Dict[str, Any]],
    ) -> None:
        if not chunk_ids:
            return

        if self.vector_dimension is None and vectors:
            self.initialize(len(vectors[0]))

        points: List[models.PointStruct] = []
        for cid, vec, txt, meta in zip(chunk_ids, vectors, texts, metadatas):
            # Generate deterministic UUID from chunk_id
            point_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, cid))
            payload = {
                "chunk_id": cid,
                "text": txt,
                **meta
            }
            points.append(
                models.PointStruct(
                    id=point_uuid,
                    vector=vec,
                    payload=payload
                )
            )

        # Batch upsert
        batch_size = 100
        for i in range(0, len(points), batch_size):
            self.client.upsert(
                collection_name=self.collection_name,
                points=points[i : i + batch_size],
            )

    def search(
        self,
        query_vector: List[float],
        top_k: int = 4,
        score_threshold: float = 0.0,
    ) -> List[SearchResult]:
        if not self.client.collection_exists(self.collection_name):
            return []

        response = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=top_k,
            score_threshold=score_threshold if score_threshold > 0 else None,
        )

        results: List[SearchResult] = []
        for point in response.points:
            payload = point.payload or {}
            chunk_id = payload.get("chunk_id", str(point.id))
            text = payload.get("text", "")
            meta = {k: v for k, v in payload.items() if k not in {"chunk_id", "text"}}
            results.append(
                SearchResult(
                    chunk_id=chunk_id,
                    text=text,
                    score=float(point.score),
                    metadata=meta,
                )
            )
        return results

    def count(self) -> int:
        if not self.client.collection_exists(self.collection_name):
            return 0
        info = self.client.get_collection(self.collection_name)
        return info.points_count or 0

    def clear(self) -> None:
        if self.client.collection_exists(self.collection_name):
            self.client.delete_collection(self.collection_name)
        if self.vector_dimension:
            self.initialize(self.vector_dimension)
