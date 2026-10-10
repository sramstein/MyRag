import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional
import httpx
from pydantic import BaseModel

class Document(BaseModel):
    content: str
    metadata: Dict[str, Any]

class DataLoader:
    """Plug-and-play data loader supporting Markdown, text, HTML, code, and web URLs."""

    SUPPORTED_EXTENSIONS = {
        ".md", ".markdown", ".txt", ".text", ".rst",
        ".html", ".htm", ".json", ".yaml", ".yml",
        ".py", ".js", ".ts", ".jsx", ".tsx", ".sh", ".c", ".cpp"
    }

    def load_path(self, target_path: str) -> List[Document]:
        """Loads documents from a file path or directory recursively."""
        path = Path(target_path)
        if not path.exists():
            raise FileNotFoundError(f"Path does not exist: {target_path}")

        documents: List[Document] = []
        if path.is_file():
            doc = self._load_file(path)
            if doc:
                documents.append(doc)
        elif path.is_dir():
            for root, _, files in os.walk(path):
                for file_name in files:
                    file_path = Path(root) / file_name
                    if file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                        doc = self._load_file(file_path)
                        if doc:
                            documents.append(doc)
        return documents

    def load_url(self, url: str) -> Document:
        """Fetch content from a web URL (e.g., GitHub README or website)."""
        response = httpx.get(url, timeout=15.0, follow_redirects=True)
        response.raise_for_status()
        raw_text = response.text

        clean_text = self._strip_html(raw_text) if url.endswith((".html", ".htm")) or "<html" in raw_text.lower() else raw_text
        title = self._extract_title(clean_text) or url.split("/")[-1]

        return Document(
            content=clean_text.strip(),
            metadata={
                "source": url,
                "filename": url.split("/")[-1] or "webpage",
                "title": title,
                "is_url": True,
            }
        )

    def _load_file(self, file_path: Path) -> Optional[Document]:
        """Reads a file and extracts metadata."""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read().strip()
        except Exception as e:
            print(f"Warning: Failed to read {file_path}: {e}")
            return None

        if not content:
            return None

        ext = file_path.suffix.lower()
        if ext in {".html", ".htm"}:
            clean_content = self._strip_html(content)
        else:
            clean_content = content

        title = self._extract_title(clean_content) or file_path.stem.replace("-", " ").replace("_", " ").title()

        return Document(
            content=clean_content,
            metadata={
                "source": str(file_path),
                "filename": file_path.name,
                "extension": ext,
                "title": title,
            }
        )

    def _strip_html(self, html_text: str) -> str:
        """Strip HTML tags and convert basic markup into readable text."""
        # Remove script and style elements
        text = re.sub(r"<(script|style).*?>.*?</\1>", "", html_text, flags=re.DOTALL | re.IGNORECASE)
        # Replace line-breaking elements with newlines
        text = re.sub(r"<(br|p|div|h[1-6]|li)[\s>]/?>", "\n", text, flags=re.IGNORECASE)
        # Strip all other tags
        text = re.sub(r"<[^>]+>", " ", text)
        # Normalize whitespace
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n\s*\n+", "\n\n", text)
        return text.strip()

    def _extract_title(self, text: str) -> Optional[str]:
        """Extract main header or markdown title if present."""
        match = re.search(r"^\s*#\s+(.+)$", text, re.MULTILINE)
        if match:
            return match.group(1).strip()
        return None
