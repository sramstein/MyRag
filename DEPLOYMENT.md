# 🚀 Free Deployment Guide for MyRag

Since GitHub Pages only hosts static frontend files (HTML/CSS/JS), your RAG backend needs to run on a lightweight backend service. Here is how to host everything for **$0/month** with zero credit card required.

---

## 🌟 The 100% Free Stack

| Component | Free Provider | Free Tier Limits |
|-----------|---------------|------------------|
| **Frontend Widget** | GitHub Pages (`sramstein.github.io`) | Unlimited static hosting |
| **Vector Database** | Qdrant Cloud Free Tier | 1GB cluster free forever (no credit card) |
| **Backend API** | Render.com or Hugging Face Spaces | 750 free hours/month or free Docker space |
| **Embeddings & LLM** | Google Gemini Free Tier | Up to 15 RPM free on AI Studio |

---

## Option 1: Deploy on Render.com (Recommended)

1. **Sign up at [render.com](https://render.com/)** using your GitHub account.
2. Click **New +** → **Web Service**.
3. Connect your **`MyRag`** GitHub repository.
4. Fill in the service settings:
   - **Name**: `myrag-backend`
   - **Environment**: `Python 3`
   - **Region**: Closest to you (e.g. Frankfurt / Oregon)
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn src.api:app --host 0.0.0.0 --port $PORT`
   - **Plan**: `Free`
5. Under **Environment Variables**, add:
   - `GEMINI_API_KEY`: *(your Gemini key from Google AI Studio)*
   - `RAG_EMBEDDING_PROVIDER`: `gemini`
   - `RAG_LLM_PROVIDER`: `gemini`
   - `QDRANT_URL`: *(your Qdrant Cloud cluster endpoint, e.g. `https://xyz.cloud.qdrant.io`)*
   - `QDRANT_API_KEY`: *(your Qdrant Cloud API key)*
6. Click **Deploy Web Service**.
7. Once deployed, Render gives you a public URL like:
   `https://myrag-backend.onrender.com`

---

## Option 2: Deploy on Hugging Face Spaces (Alternative Free Docker)

1. Go to [huggingface.co/spaces](https://huggingface.co/spaces) and click **Create new Space**.
2. Space Name: `my-rag-backend`
3. Space SDK: **Docker** (Blank)
4. Space Hardware: **CPU Basic (Free - 2 vCPU, 16GB RAM)**
5. Add a `Dockerfile`:
   ```dockerfile
   FROM python:3.11-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   COPY . .
   EXPOSE 7860
   CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "7860"]
   ```
6. Under **Settings → Variables and Secrets**, add `GEMINI_API_KEY`, `QDRANT_URL`, `QDRANT_API_KEY`.
7. Your API will be live at `https://<username>-my-rag-backend.hf.space`.

---

## 📋 Embed the Chat Widget on your GitHub Page

In your GitHub Pages repository (or blog/portfolio repo):

1. Copy [`widget/chat-widget.js`](file:///Users/sacharamstein/Documents/Code/MyRag/widget/chat-widget.js) and [`widget/chat-widget.css`](file:///Users/sacharamstein/Documents/Code/MyRag/widget/chat-widget.css) into your site's assets directory (or serve directly from your deployed backend).
2. Add the following to your site's HTML layout (`index.html`, `_layouts/default.html`, etc.) right before `</body>`:

```html
<!-- MyRag Chat Widget Styles -->
<link rel="stylesheet" href="https://myrag-backend.onrender.com/widget/chat-widget.css">

<!-- MyRag Chat Widget Script -->
<script 
  src="https://myrag-backend.onrender.com/widget/chat-widget.js" 
  data-api-url="https://myrag-backend.onrender.com"
  data-title="Sacha's AI Assistant"
  data-subtitle="Ask anything about my projects">
</script>
```

That's it! Visitors to your GitHub Page can now chat in real time with an AI assistant trained on your projects.
