import pytest
from src.data_loader import DataLoader
from src.text_splitter import RecursiveTextSplitter, Document

def test_data_loader_local():
    loader = DataLoader()
    docs = loader.load_path("./data/sample_docs")
    assert len(docs) >= 3
    filenames = [d.metadata["filename"] for d in docs]
    assert "about.md" in filenames
    assert "projects.md" in filenames

def test_text_splitter():
    splitter = RecursiveTextSplitter(chunk_size=100, chunk_overlap=20)
    doc = Document(
        content="This is the first sentence. This is the second sentence. Here is more text to split up into multiple pieces.",
        metadata={"filename": "test.txt", "title": "Test Doc"}
    )
    chunks = splitter.split_document(doc)
    assert len(chunks) >= 2
    assert chunks[0].metadata["filename"] == "test.txt"
