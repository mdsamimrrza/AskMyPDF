"""Lightweight vector store that lazily imports heavy ML libraries.

Delay loading SentenceTransformer and faiss until they're first needed so
the application process doesn't blow memory at import time (important for
small cloud instances like Render with 512Mi).
"""
from typing import List


_model = None
_faiss = None


def _get_model():
    """Lazily load and cache the SentenceTransformer model."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer

        # Keep the small/default model — you can override by editing this file
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def _get_faiss():
    """Lazily import faiss to avoid importing it at module import time."""
    global _faiss
    if _faiss is None:
        import faiss

        _faiss = faiss
    return _faiss


class VectorStore:
    def __init__(self):
        self.index = None
        self.text_chunks: List[str] = []

    def create_index(self, texts: List[str]):
        self.text_chunks = texts
        model = _get_model()
        embeddings = model.encode(texts)

        import numpy as np

        embeddings = np.array(embeddings).astype("float32")
        faiss = _get_faiss()
        self.index = faiss.IndexFlatL2(embeddings.shape[1])
        self.index.add(embeddings)

    def query(self, question: str, top_k: int = 3) -> List[str]:
        model = _get_model()
        import numpy as np

        question_embedding = model.encode([question])
        question_embedding = np.array(question_embedding).astype("float32")
        distances, indices = self.index.search(question_embedding, top_k)
        return [self.text_chunks[i] for i in indices[0]]
