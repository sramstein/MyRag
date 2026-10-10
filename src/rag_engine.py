from typing import Any, Dict, Generator, List, Optional
from src.config import Settings, load_settings
from src.data_loader import DataLoader, Document
from src.text_splitter import RecursiveTextSplitter, TextChunk
from src.embeddings.factory import get_embedding_model
from src.vector_store.factory import get_vector_store
from src.vector_store.base import SearchResult
from src.llm.factory import get_llm

class RagEngine:
    """Core RAG engine managing data ingestion, retrieval, and generation."""

    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or load_settings()
        self.loader = DataLoader()
        self.splitter = RecursiveTextSplitter(
            chunk_size=self.settings.chunking.chunk_size,
            chunk_overlap=self.settings.chunking.chunk_overlap,
        )
        self.embeddings = get_embedding_model(self.settings.embedding)
        self.vector_store = get_vector_store(self.settings.vector_db)
        self.llm = get_llm(self.settings.llm)

    def ingest_path(self, target_path: str, clear_existing: bool = False) -> Dict[str, Any]:
        """Ingests files or directories into the vector database."""
        if clear_existing:
            self.vector_store.clear()

        docs = self.loader.load_path(target_path)
        if not docs:
            return {"status": "warning", "message": f"No supported documents found in {target_path}", "chunks_added": 0}

        return self._process_and_store_docs(docs)

    def ingest_url(self, url: str) -> Dict[str, Any]:
        """Fetches a web URL or GitHub document and adds it to the index."""
        doc = self.loader.load_url(url)
        return self._process_and_store_docs([doc])

    def _process_and_store_docs(self, docs: List[Document]) -> Dict[str, Any]:
        chunks = self.splitter.split_documents(docs)
        if not chunks:
            return {"status": "warning", "message": "Documents were empty", "chunks_added": 0}

        texts = [c.text for c in chunks]
        chunk_ids = [c.chunk_id for c in chunks]
        metadatas = [c.metadata for c in chunks]

        # Generate embeddings
        vectors = self.embeddings.embed_documents(texts)

        # Upsert into vector store
        self.vector_store.upsert(
            chunk_ids=chunk_ids,
            vectors=vectors,
            texts=texts,
            metadatas=metadatas,
        )

        return {
            "status": "success",
            "documents_indexed": len(docs),
            "chunks_added": len(chunks),
            "total_vectors": self.vector_store.count(),
        }

    def retrieve(self, question: str) -> List[SearchResult]:
        """Retrieve most relevant chunks for a question."""
        query_vector = self.embeddings.embed_query(question)
        return self.vector_store.search(
            query_vector=query_vector,
            top_k=self.settings.retrieval.top_k,
            score_threshold=self.settings.retrieval.score_threshold,
        )

    def build_prompt(self, question: str, results: List[SearchResult]) -> str:
        """Construct the augmented context prompt."""
        if not results:
            context_str = "No relevant context found."
        else:
            context_blocks = []
            for r in results:
                source_name = r.metadata.get("filename") or r.metadata.get("source", "Document")
                title = r.metadata.get("title", "")
                header = f"[{source_name} - {title}]" if title else f"[{source_name}]"
                context_blocks.append(f"{header}\n{r.text}")
            context_str = "\n\n---\n\n".join(context_blocks)

        prompt = (
            f"Context:\n{context_str}\n\n"
            f"Question: {question}\n\n"
            f"Answer the question based strictly on the context above. If you don't know, state so clearly."
        )
        return prompt

    def query(self, question: str) -> Dict[str, Any]:
        """Run non-streaming RAG query."""
        results = self.retrieve(question)
        prompt = self.build_prompt(question, results)
        answer = self.llm.generate(
            prompt=prompt,
            system_instruction=self.settings.prompt.system_instruction,
        )
        return {
            "answer": answer,
            "sources": [
                {
                    "title": r.metadata.get("title") or r.metadata.get("filename", "Source"),
                    "source": r.metadata.get("source", ""),
                    "score": round(r.score, 3),
                    "preview": r.text[:140] + "..." if len(r.text) > 140 else r.text,
                }
                for r in results
            ],
        }

    def query_stream(self, question: str) -> Generator[str, None, None]:
        """Run streaming RAG query yielding text tokens."""
        results = self.retrieve(question)
        prompt = self.build_prompt(question, results)
        yield from self.llm.stream(
            prompt=prompt,
            system_instruction=self.settings.prompt.system_instruction,
        )

    def get_stats(self) -> Dict[str, Any]:
        """Return engine statistics."""
        return {
            "total_vectors": self.vector_store.count(),
            "embedding_provider": self.settings.embedding.provider,
            "embedding_model": self.settings.embedding.model_name,
            "llm_provider": self.settings.llm.provider,
            "llm_model": self.settings.llm.model_name,
            "vector_db_provider": self.settings.vector_db.provider,
        }
