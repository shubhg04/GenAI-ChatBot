import json
import os
import re
from config import RAG_KNOWLEDGE_FILE, RAG_MIN_SCORE

class SimpleRetriever:
    def __init__(self, knowledge_file = RAG_KNOWLEDGE_FILE, min_score = RAG_MIN_SCORE):
        self.knowledge_file = knowledge_file
        self.min_score = min_score

    def load_knowledge_base(self):
        if not os.path.exists(self.knowledge_file):
            return []

        with open(self.knowledge_file, "r", encoding="utf-8") as file:
            return json.load(file)

    def tokenize(self, text):
        return re.findall(r'\b\w+\b', text.lower())

    def score_entry(self, query, entry):
        query_tokens = set(self.tokenize(query))
        content_tokens = set(self.tokenize(entry.get("content", "")))
        keyword_tokens = set(token.lower() for token in entry.get("keywords", []))
        title_tokens = set(self.tokenize(entry.get("title", "")))

        score = 0
        score += len(query_tokens & content_tokens)
        score += 2 * len(query_tokens & keyword_tokens)
        score += len(query_tokens & title_tokens)

        return score

    def retrieve(self, query, top_k = 3):
        knowledge_base = self.load_knowledge_base()

        scored_entries = []
        for entry in knowledge_base:
            score = self.score_entry(query, entry)
            if score >= self.min_score:
                scored_entries.append(
                    {
                        "id": entry.get("id"),
                        "title": entry.get("title"),
                        "content": entry.get("content"),
                        "score": score
                    }
                )

        scored_entries.sort(key=lambda item: item["score"], reverse=True)
        return scored_entries[:top_k]