# 🤖 MyRag — AI Assistant for your GitHub Page

A lightweight, plug-and-play **Retrieval-Augmented Generation (RAG)** system and embeddable chat widget designed for **GitHub Pages**, documentation sites, and personal portfolios.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com/)
[![Vector DB: Qdrant Free](https://img.shields.io/badge/Vector_DB-Qdrant_Free-dc2626.svg)](https://qdrant.tech/)
[![Embeddings: Local & Gemini](https://img.shields.io/badge/Embeddings-Local_ONNX_%7C_Gemini-8b5cf6.svg)](https://ai.google.dev/)
[![Widget: Zero Dependencies](https://img.shields.io/badge/Widget-Vanilla_JS-f59e0b.svg)]()

---

## ✨ Highlights

- **🆓 100% Free Vector Database**: Powered by [Qdrant](https://qdrant.tech/). Runs locally on disk with zero setup and zero cost, or connects to the permanent **Qdrant Cloud Free Tier** (1GB cluster free forever).
- **🔌 Plug & Play with Any Data**: Drop Markdown files, plain text, HTML, code files, or point to web/GitHub URLs. The engine handles extraction, recursive chunking, and metadata indexing automatically.
- **🔄 Config-Driven AI Providers**: Test 100% offline with fast local embeddings ([FastEmbed](https://github.com/qdrant/fastembed) ONNX) and instant test synthesis, or switch to **Google Gemini** (`gemini-3.8-flash` / `gemini-embedding-001`) or **Ollama** by editing a single field in `config.yaml`.
- **💬 Drop-in GitHub Pages Widget**: A lightweight (~10KB), zero-dependency floating chat widget with real-time SSE token streaming, markdown formatting, starter suggestions, and interactive source citations.
- **⚡ Fast & Modern API**: Built on FastAPI with CORS support, SSE streaming, and health checks.

---

## 🏗️ Architecture

```
┌────────────────────────────────┐       ┌────────────────────────────────┐
│   GitHub Pages Visitor (Web)   │       │   Data Ingestion Sources       │
│  (sramstein.github.io site)   │       │  (Markdown, HTML, Code, URLs)  │
└───────────────┬────────────────┘       └───────────────┬────────────────┘
                │ HTTP / SSE Stream                      │ Ingest Pipeline
                ▼                                        ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        FastAPI Server (MyRag)                          │
│                                                                        │
│   /api/chat/stream          /api/chat             /api/ingest          │
│   (Realtime SSE)            (JSON)                (Data Indexing)      │
├────────────────────────────────────────────────────────────────────────┤
│                           RAG Engine                                   │
│                                                                        │
│  ┌───────────────────────┐           ┌───────────────────────────────┐ │
│  │   Embedding Layer     │           │       Vector Database         │ │
│  │  - Local: FastEmbed   │  ◄──────► │  - Local: Qdrant Disk (Free)  │ │
│  │  - Cloud: Gemini      │           │  - Cloud: Qdrant 1GB (Free)   │ │
│  └───────────────────────┘           └───────────────────────────────┘ │
│                                                                        │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │                            LLM Layer                              │ │
│  │  - Local Test Mode (extractive synthesizer, instant test)          │ │
│  │  - Google Gemini (gemini-3.8-flash via official google-genai SDK)  │ │
│  │  - Ollama (llama3.2, mistral, etc.)                               │ │
│  └───────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start (Local)

### 1. Setup & Activate Environment

```bash
# Activate the existing virtual environment
source .venv/bin/activate
```
> **Tip:** If you see `command not found: python`, make sure you have run `source .venv/bin/activate`, or use the included `./run.sh` helper!

### 2. Ingest Data (Plug & Play)

Using `./run.sh` (works without activating):
```bash
./run.sh ingest --path ./data/sample_docs --clear
```

Or using `python` with the virtualenv active:
```bash
python -m src.cli ingest --path ./data/sample_docs --clear
```

You can also ingest any web page or GitHub raw file via URL:
```bash
./run.sh ingest --url https://raw.githubusercontent.com/sramstein/MyRag/main/README.md
```

### 3. Ask Questions via CLI

```bash
# Standard query
./run.sh query "What projects did Sacha build?"

# Streaming response
./run.sh query "Who is Sacha?" --stream
```

### 4. Run the API & Preview the Chat Widget

```bash
./run.sh serve --port 8000
```

Open your browser to:
👉 **`http://localhost:8000/widget/index.html`**

You will see a live preview of a GitHub Pages portfolio with the floating chat assistant active in the bottom right corner!

---

## 🐳 Running with Docker (Backend + Ollama)

If you prefer running everything in Docker with local Ollama, you can start the entire stack with a single command:

```bash
docker compose up -d
```

### What Docker starts automatically:
1. **`ollama`**: The official Ollama container on port `11434` with persistent volume storage for models.
2. **`ollama-pull`**: Automatically downloads `llama3.2` on first startup so you don't have to pull it manually.
3. **`backend`**: The MyRag FastAPI server on port `8000` connected to Ollama and serving the chat widget.

### Useful Docker commands:

```bash
# Ingest documents inside the running backend container
docker compose exec backend python -m src.cli ingest --path ./data/sample_docs --clear

# Query directly from Docker
docker compose exec backend python -m src.cli query "What is MyRag?" --stream

# Check logs
docker compose logs -f

# Stop the containers
docker compose down
```

---

## ⚙️ Configuration (`config.yaml`)

Switching database, embeddings, or LLM providers requires zero code changes:

```yaml
# Vector Database
vector_db:
  provider: "qdrant"                  # Free embedded or free cloud
  collection_name: "github_page_rag"
  storage_path: "./data/qdrant_db"    # 100% free local storage
  qdrant_url: null                    # Or set Qdrant Cloud URL (free 1GB forever)
  qdrant_api_key: null

# Embedding Model
embedding:
  provider: "local"                   # "local" (free ONNX) or "gemini"
  model_name: "BAAI/bge-small-en-v1.5"

# LLM Provider
llm:
  provider: "local"                   # "local" (test mode / ollama) or "gemini"
  model_name: "gemini-3.8-flash"      # Used when provider is "gemini"
  temperature: 0.2

# Chunking & Retrieval
retrieval:
  top_k: 4
  score_threshold: 0.35
chunking:
  chunk_size: 600
  chunk_overlap: 100
```

---

## 🌐 Switching to Google Gemini

To switch from local test mode to Google Gemini:

1. Get a free API key from [Google AI Studio](https://aistudio.google.com/).
2. Create a `.env` file:
   ```bash
   GEMINI_API_KEY="your-gemini-api-key"
   ```
3. In `config.yaml`, set:
   ```yaml
   embedding:
     provider: "gemini"
     model_name: "gemini-embedding-001"

   llm:
     provider: "gemini"
     model_name: "gemini-3.8-flash"
   ```
4. Re-ingest your documents:
   ```bash
   python -m src.cli ingest --path ./data/sample_docs --clear
   ```

---

## 📦 Embedding the Widget on your GitHub Page

Adding the chat assistant to any GitHub Pages site (Jekyll, Hugo, Docusaurus, HTML, VitePress) takes just two lines:

```html
<!-- 1. Include the styles -->
<link rel="stylesheet" href="https://your-backend.onrender.com/widget/chat-widget.css">

<!-- 2. Include the widget script with your backend API URL -->
<script 
  src="https://your-backend.onrender.com/widget/chat-widget.js" 
  data-api-url="https://your-backend.onrender.com"
  data-title="Sacha's Assistant"
  data-subtitle="Ask me anything!">
</script>
```

### Free Deployment Options for the Backend:
- **Render.com** (Free Web Service)
- **Hugging Face Spaces** (Free Docker / Python Space)
- **Railway.app** or **Fly.io** (Free starter tiers)
- **Qdrant Cloud** (Free 1GB cluster forever for vector storage)

See [DEPLOYMENT.md](DEPLOYMENT.md) for full step-by-step deployment instructions.

---

## 🧪 Running Tests

```bash
python -m pytest -v
```

---

## 📁 Repository Structure

```
MyRag/
├── config.yaml               # Central configuration (DB, Embedding, LLM)
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variable template
├── src/
│   ├── config.py             # Settings loader (YAML + environment)
│   ├── data_loader.py        # Multi-format ingestion (Markdown, code, HTML, URLs)
│   ├── text_splitter.py      # Recursive chunker with overlap & metadata
│   ├── rag_engine.py         # Main RAG engine (retrieve + augment + generate)
│   ├── api.py                # FastAPI web server with streaming & CORS
│   ├── cli.py                # CLI commands (ingest, query, serve, stats)
│   ├── embeddings/           # Embedding providers (FastEmbed local, Gemini)
│   ├── vector_store/         # Vector DB (Qdrant local embedded & free cloud)
│   └── llm/                  # LLM providers (Local test / Ollama, Gemini)
├── widget/
│   ├── chat-widget.js        # Standalone, zero-dependency embeddable widget
│   ├── chat-widget.css       # Clean, modern responsive widget styling
│   └── index.html            # Live demo simulating a GitHub Pages portfolio
├── data/
│   └── sample_docs/          # Sample docs to test plug-and-play immediately
│       ├── about.md
│       ├── projects.md
│       └── contact.md
└── tests/                    # Unit and integration test suite
```

---

## 📜 License

MIT License. See [LICENSE](LICENSE) for details.