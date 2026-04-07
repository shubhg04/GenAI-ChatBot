import json
import os
import numpy as np
import faiss
from config import RAG_METADATA_FILE, FAISS_INDEX_FILE, RAG_TOP_K, RAG_SIMILARITY_THRESHOLD
from embedding_utils import embed_text

class FAISSRetriever:
    def __init__(self):
        self.metadata = self.load_metadata()
        self.index = self.load_index()

    def load_metadata(self):
        if not os.path.exists(RAG_METADATA_FILE):
            return []

        with open(RAG_METADATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
        
    def load_index(self):
        if not os.path.exists(FAISS_INDEX_FILE):
            return None

        return faiss.read_index(FAISS_INDEX_FILE)

    def retrieve(self, query, top_k = RAG_TOP_K):
        if not self.metadata or self.index is None:
            return []

        query_embedding = embed_text(query)
        query_vector = np.array([query_embedding], dtype = "float32")

        faiss.normalize_L2(query_vector)

        distances, indices = self.index.search(query_vector, top_k)

        results = []

        for score, idx in zip(distances[0], indices[0]):
            if idx < 0 or idx >= len(self.metadata):
                continue

            similarity_score = float(score)

            if similarity_score < RAG_SIMILARITY_THRESHOLD:
                continue

            chunk = self.metadata[idx]

            results.append({
                "id": chunk["id"],
                "title": chunk["title"],
                "content": chunk["content"],
                "score": round(float(score), 4)
            })

        return results