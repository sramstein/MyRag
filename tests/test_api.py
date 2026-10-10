from fastapi.testclient import TestClient
from src.api import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_stats_endpoint():
    response = client.get("/api/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_vectors" in data
    assert "embedding_provider" in data

def test_chat_endpoint():
    response = client.post("/api/chat", json={"query": "Who is Sacha?"})
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "sources" in data
