import uuid
from typing import List
from src.data_loader import Document

class TextChunk:
    def __init__(self, text: str, metadata: dict, chunk_id: str = None):
        self.chunk_id = chunk_id or str(uuid.uuid4())
        self.text = text
        self.metadata = metadata

    def to_dict(self):
        return {
            "chunk_id": self.chunk_id,
            "text": self.text,
            "metadata": self.metadata,
        }

class RecursiveTextSplitter:
    """Splits documents recursively based on natural separators with overlap."""

    def __init__(self, chunk_size: int = 600, chunk_overlap: int = 100):
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = ["\n\n", "\n", ". ", "? ", "! ", " ", ""]

    def split_document(self, document: Document) -> List[TextChunk]:
        raw_chunks = self._split_text(document.content)
        chunks: List[TextChunk] = []

        for idx, text in enumerate(raw_chunks):
            chunk_meta = dict(document.metadata)
            chunk_meta["chunk_index"] = idx
            chunk_meta["total_chunks"] = len(raw_chunks)
            chunk = TextChunk(
                text=text.strip(),
                metadata=chunk_meta,
                chunk_id=f"{document.metadata.get('filename', 'doc')}_{idx}_{uuid.uuid4().hex[:6]}"
            )
            chunks.append(chunk)

        return chunks

    def split_documents(self, documents: List[Document]) -> List[TextChunk]:
        all_chunks: List[TextChunk] = []
        for doc in documents:
            all_chunks.extend(self.split_document(doc))
        return all_chunks

    def _split_text(self, text: str) -> List[str]:
        if len(text) <= self.chunk_size:
            return [text] if text.strip() else []

        pieces = self._recursive_split(text, self.separators)
        
        # Merge pieces into chunks of roughly chunk_size with overlap
        chunks: List[str] = []
        current_chunk: List[str] = []
        current_len = 0

        for piece in pieces:
            piece_len = len(piece)
            if current_len + piece_len > self.chunk_size and current_chunk:
                merged = "".join(current_chunk)
                chunks.append(merged)
                
                # Keep overlap from the end of current_chunk
                overlap_pieces: List[str] = []
                overlap_len = 0
                for prev in reversed(current_chunk):
                    if overlap_len + len(prev) <= self.chunk_overlap:
                        overlap_pieces.insert(0, prev)
                        overlap_len += len(prev)
                    else:
                        break
                current_chunk = overlap_pieces
                current_len = overlap_len

            current_chunk.append(piece)
            current_len += piece_len

        if current_chunk:
            merged = "".join(current_chunk)
            if merged.strip():
                chunks.append(merged)

        return chunks

    def _recursive_split(self, text: str, separators: List[str]) -> List[str]:
        if not separators or len(text) <= self.chunk_size:
            return [text]

        separator = separators[0]
        remaining_separators = separators[1:]

        if separator == "":
            return list(text)

        splits = text.split(separator)
        result: List[str] = []

        for idx, s in enumerate(splits):
            part = s if idx == len(splits) - 1 else s + separator
            if not part:
                continue
            if len(part) > self.chunk_size and remaining_separators:
                result.extend(self._recursive_split(part, remaining_separators))
            else:
                result.append(part)

        return result
