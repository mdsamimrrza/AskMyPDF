import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")


class VectorStore:
    def __init__(self):
        self.index = None
        self.text_chunks = []

    def create_index(self, texts):
        self.text_chunks = texts
        embeddings = model.encode(texts)
        embeddings = np.array(embeddings).astype("float32")
        self.index = faiss.IndexFlatL2(embeddings.shape[1])
        self.index.add(embeddings)

    def query(self, question, top_k=3):
        question_embedding = model.encode([question])
        question_embedding = np.array(question_embedding).astype("float32")
        distances, indices = self.index.search(question_embedding, top_k)
        return [self.text_chunks[i] for i in indices[0]]
