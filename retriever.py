import json
import os
import re
from config import RAG_KNOWLEDGE_FILE, RAG_SIMILARITY_THRESHOLD
from embedding_utils import embed_text, cosine_similarity

class SimpleRetriever:
    def __init__(self, knowledge_file = RAG_KNOWLEDGE_FILE, similarity_threshold = RAG_SIMILARITY_THRESHOLD):
        self.knowledge_file = knowledge_file
        self.similarity_threshold = similarity_threshold

    def load_knowledge_base(self):
        if not os.path.exists(self.knowledge_file):
            return []

        with open(self.knowledge_file, "r", encoding="utf-8") as file:
            return json.load(file)

    def retrieve(self, query, top_k = 3):
        knowledge_base = self.load_knowledge_base()

        if not knowledge_base:
            return []

        query_embedding = embed_text(query)
        scored_entries = []
       
        for entry in knowledge_base:
            entry_eb = entry.get("embedding", [])
            if not isinstance(entry_eb, list) or not entry_eb:
                continue

            similarity = cosine_similarity(query_embedding, entry_eb)
            if similarity >= self.similarity_threshold:
                scored_entries.append(
                    {
                        "id": entry.get("id"),
                        "title": entry.get("title"),
                        "content": entry.get("content"),
                        "score": round(similarity, 4)
                    }
                )

        scored_entries.sort(key=lambda item: item["score"], reverse=True)
        return scored_entries[:top_k]