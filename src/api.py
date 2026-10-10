import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from src.config import load_settings
from src.rag_engine import RagEngine

settings = load_settings()
engine = RagEngine(settings)

app = FastAPI(
    title=settings.app.title,
    description=settings.app.description,
    version="1.0.0",
)

# Enable CORS for GitHub Pages
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.app.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    query: str
    stream: bool = False

class IngestPathRequest(BaseModel):
    path: str = "./data/sample_docs"
    clear_existing: bool = False

class IngestUrlRequest(BaseModel):
    url: str

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "service": "MyRag"}

@app.get("/api/stats")
def get_stats():
    return engine.get_stats()

@app.post("/api/chat")
def chat(request: ChatRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    
    response = engine.query(request.query)
    return response

@app.post("/api/chat/stream")
def chat_stream(request: ChatRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    # Retrieve context and sources first
    results = engine.retrieve(request.query)
    prompt = engine.build_prompt(request.query, results)
    sources = [
        {
            "title": r.metadata.get("title") or r.metadata.get("filename", "Source"),
            "source": r.metadata.get("source", ""),
            "score": round(r.score, 3),
            "preview": r.text[:140] + "..." if len(r.text) > 140 else r.text,
        }
        for r in results
    ]

    def event_generator():
        # Stream LLM tokens
        for token in engine.llm.stream(prompt, system_instruction=settings.prompt.system_instruction):
            data = json.dumps({"token": token})
            yield f"data: {data}\n\n"
        
        # Send closing payload with sources
        final_payload = json.dumps({"done": True, "sources": sources})
        yield f"data: {final_payload}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.post("/api/ingest")
def ingest_path(request: IngestPathRequest):
    try:
        result = engine.ingest_path(request.path, clear_existing=request.clear_existing)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ingest/url")
def ingest_url(request: IngestUrlRequest):
    try:
        result = engine.ingest_url(request.url)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount static files for the chat widget and demo preview
widget_dir = Path(__file__).resolve().parent.parent / "widget"
if widget_dir.exists():
    app.mount("/widget", StaticFiles(directory=str(widget_dir), html=True), name="widget")

@app.get("/")
def root():
    return {
        "message": "MyRag API is running!",
        "widget_demo": "/widget/index.html",
        "docs": "/docs",
        "stats": "/api/stats",
    }
