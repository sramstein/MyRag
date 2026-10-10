import json
import re
import time
from typing import Generator, Optional
import httpx
from src.llm.base import BaseLLM

class LocalLLM(BaseLLM):
    """Local LLM with automatic Ollama detection and fallback smart synthesizer.
    
    1. If Ollama is running at ollama_url: sends queries to Ollama (llama3.2, mistral, etc.)
    2. If Ollama is not active: cleanly extracts and synthesizes answers from the context chunks
       so you can test the RAG pipeline, API, and chat widget immediately without downloading gigabytes.
    """

    def __init__(
        self,
        ollama_url: str = "http://localhost:11434",
        ollama_model: str = "llama3.2",
        temperature: float = 0.2,
    ):
        self.ollama_url = ollama_url.rstrip("/")
        self.ollama_model = ollama_model
        self.temperature = temperature
        self._is_ollama_available = self._check_ollama()

    def _check_ollama(self) -> bool:
        try:
            r = httpx.get(f"{self.ollama_url}/api/version", timeout=1.0)
            return r.status_code == 200
        except Exception:
            return False

    def generate(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        if self._check_ollama():
            return self._call_ollama(prompt, system_instruction)
        return self._fallback_synthesis(prompt)

    def stream(self, prompt: str, system_instruction: Optional[str] = None) -> Generator[str, None, None]:
        if self._check_ollama():
            yield from self._stream_ollama(prompt, system_instruction)
        else:
            full_text = self._fallback_synthesis(prompt)
            # Simulate streaming word by word for realistic frontend UX
            words = full_text.split(" ")
            for i, word in enumerate(words):
                yield word + (" " if i < len(words) - 1 else "")
                time.sleep(0.015)

    def _call_ollama(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        payload = {
            "model": self.ollama_model,
            "prompt": prompt,
            "system": system_instruction or "",
            "stream": False,
            "options": {"temperature": self.temperature},
        }
        with httpx.Client(timeout=60.0) as client:
            resp = client.post(f"{self.ollama_url}/api/generate", json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data.get("response", "")

    def _stream_ollama(self, prompt: str, system_instruction: Optional[str] = None) -> Generator[str, None, None]:
        payload = {
            "model": self.ollama_model,
            "prompt": prompt,
            "system": system_instruction or "",
            "stream": True,
            "options": {"temperature": self.temperature},
        }
        with httpx.Client(timeout=60.0) as client:
            with client.stream("POST", f"{self.ollama_url}/api/generate", json=payload) as resp:
                resp.raise_for_status()
                for line in resp.iter_lines():
                    if line:
                        chunk = json.loads(line)
                        if "response" in chunk:
                            yield chunk["response"]

    def _fallback_synthesis(self, prompt: str) -> str:
        """Smart local context synthesizer for test mode without heavy local model."""
        # Extract context block from prompt
        context_match = re.search(r"Context:\s*(.*?)\s*Question:\s*(.*)", prompt, re.DOTALL | re.IGNORECASE)
        if not context_match:
            return (
                "Hello! I am your GitHub Page AI Assistant. "
                "I am running in local test mode. Add documents to the `data/` directory or configure Gemini in `config.yaml` to get started."
            )

        context_text = context_match.group(1).strip()
        question = context_match.group(2).strip()

        if not context_text or context_text == "No relevant context found.":
            return (
                f"I looked through the indexed documents, but I couldn't find specific information to answer '{question}'. "
                "Feel free to ask another question or check my GitHub repositories!"
            )

        # Split context into paragraphs/sentences and rank relevance
        question_words = set(re.findall(r"\w+", question.lower())) - {"what", "is", "the", "a", "an", "how", "can", "you", "who", "where", "my"}
        paragraphs = [p.strip() for p in context_text.split("\n\n") if p.strip()]

        scored_paragraphs = []
        for p in paragraphs:
            score = sum(1 for w in question_words if w in p.lower())
            scored_paragraphs.append((score, p))

        scored_paragraphs.sort(key=lambda x: x[0], reverse=True)
        top_paragraphs = [p for score, p in scored_paragraphs[:3] if score > 0]

        if not top_paragraphs and paragraphs:
            top_paragraphs = paragraphs[:2]

        synthesis = "\n\n".join(top_paragraphs)
        return (
            f"Based on the project documentation:\n\n"
            f"{synthesis}\n\n"
            f"> *Note: Running with local test synthesizer. To use Gemini or Ollama, update `config.yaml`.*"
        )
