from src.config import Settings, VectorDbConfig
from src.rag_engine import RagEngine

def test_rag_engine_end_to_end():
    # Use in-memory vector db for isolated test
    settings = Settings()
    settings.vector_db = VectorDbConfig(provider="memory", collection_name="test_mem_collection")
    
    engine = RagEngine(settings)
    ingest_res = engine.ingest_path("./data/sample_docs")
    assert ingest_res["status"] == "success"
    assert ingest_res["chunks_added"] > 0

    # Query
    res = engine.query("What projects are mentioned?")
    assert "answer" in res
    assert len(res["answer"]) > 0
    assert len(res["sources"]) > 0
