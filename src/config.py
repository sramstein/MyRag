import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

class AppConfig(BaseModel):
    title: str = "MyRag Assistant"
    description: str = "RAG Assistant for GitHub Page & Projects"
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: List[str] = ["*"]

class VectorDbConfig(BaseModel):
    provider: str = "qdrant"
    collection_name: str = "github_page_rag"
    storage_path: str = "./data/qdrant_db"
    qdrant_url: Optional[str] = None
    qdrant_api_key: Optional[str] = None

class EmbeddingConfig(BaseModel):
    provider: str = "local"
    model_name: str = "BAAI/bge-small-en-v1.5"
    batch_size: int = 32

class LlmConfig(BaseModel):
    provider: str = "local"
    model_name: str = "gemini-3.8-flash"
    temperature: float = 0.2
    max_output_tokens: int = 1024
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"

class RetrievalConfig(BaseModel):
    top_k: int = 4
    score_threshold: float = 0.35

class ChunkingConfig(BaseModel):
    chunk_size: int = 600
    chunk_overlap: int = 100

class PromptConfig(BaseModel):
    system_instruction: str = (
        "You are an intelligent, friendly AI assistant embedded on my GitHub Page. "
        "Answer questions accurately using ONLY the provided context."
    )

class Settings(BaseModel):
    app: AppConfig = Field(default_factory=AppConfig)
    vector_db: VectorDbConfig = Field(default_factory=VectorDbConfig)
    embedding: EmbeddingConfig = Field(default_factory=EmbeddingConfig)
    llm: LlmConfig = Field(default_factory=LlmConfig)
    retrieval: RetrievalConfig = Field(default_factory=RetrievalConfig)
    chunking: ChunkingConfig = Field(default_factory=ChunkingConfig)
    prompt: PromptConfig = Field(default_factory=PromptConfig)


def load_settings(config_path: Optional[str] = None) -> Settings:
    """Load settings from config.yaml with environment variable overrides."""
    path = Path(config_path) if config_path else BASE_DIR / "config.yaml"
    data: Dict[str, Any] = {}

    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

    settings = Settings(**data)

    # Environment variable overrides
    if os.getenv("QDRANT_URL"):
        settings.vector_db.qdrant_url = os.getenv("QDRANT_URL")
    if os.getenv("QDRANT_API_KEY"):
        settings.vector_db.qdrant_api_key = os.getenv("QDRANT_API_KEY")
    if os.getenv("RAG_EMBEDDING_PROVIDER"):
        settings.embedding.provider = os.getenv("RAG_EMBEDDING_PROVIDER")
    if os.getenv("RAG_LLM_PROVIDER"):
        settings.llm.provider = os.getenv("RAG_LLM_PROVIDER")
    if os.getenv("GEMINI_MODEL"):
        settings.llm.model_name = os.getenv("GEMINI_MODEL")
    if os.getenv("OLLAMA_HOST"):
        settings.llm.ollama_url = os.getenv("OLLAMA_HOST")

    return settings
