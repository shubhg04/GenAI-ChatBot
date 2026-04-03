import json
import os
import re
from config import RAG_KNOWLEDGE_FILE


DOCUMENTS_FILE = "knowledge_docs.json"
CHUNK_SIZE = 2
STOP_WORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "being", "been",
    "and", "or", "but", "if", "then", "else", "of", "to", "in", "on", "for",
    "with", "by", "at", "from", "as", "it", "this", "that", "these", "those",
    "can", "could", "should", "would", "will", "may", "might", "into", "than",
    "so", "such", "their", "there", "them", "they", "he", "she", "you", "we",
    "i", "my", "our", "your", "his", "her", "its"
}


def load_documents():
    if not os.path.exists(DOCUMENTS_FILE):
        return []

    with open(DOCUMENTS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def split_into_sentences(text):
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [sentence.strip() for sentence in sentences if sentence.strip()]


def extract_keywords(text, max_keywords=8):
    words = re.findall(r"\b[a-zA-Z][a-zA-Z0-9_-]*\b", text.lower())

    filtered_words = []
    for word in words:
        if word not in STOP_WORDS and len(word) > 2:
            filtered_words.append(word)

    unique_keywords = []
    seen = set()

    for word in filtered_words:
        if word not in seen:
            seen.add(word)
            unique_keywords.append(word)

    return unique_keywords[:max_keywords]


def build_chunks_from_document(document, chunk_size=CHUNK_SIZE):
    sentences = split_into_sentences(document.get("content", ""))
    chunks = []

    for index in range(0, len(sentences), chunk_size):
        chunk_sentences = sentences[index:index + chunk_size]
        chunk_text = " ".join(chunk_sentences)
        chunk = {
            "id": f"{document['doc_id']}-chunk-{(index // chunk_size) + 1}",
            "title": document.get("title", "Untitled"),
            "content": chunk_text,
            "keywords": extract_keywords(chunk_text)
        }
        chunks.append(chunk)

    return chunks


def build_knowledge_base():
    documents = load_documents()
    knowledge_base = []

    for document in documents:
        document_chunks = build_chunks_from_document(document)
        knowledge_base.extend(document_chunks)

    with open(RAG_KNOWLEDGE_FILE, "w", encoding="utf-8") as file:
        json.dump(knowledge_base, file, indent=4)

    return {
        "message": f"Knowledge base built successfully.",
        "total_documents": len(documents),
        "total_chunks": len(knowledge_base),
        "knowledge_file": RAG_KNOWLEDGE_FILE
    }


if __name__ == "__main__":
    result = build_knowledge_base()
    print(result["message"])
    print(f"Total documents: {result['total_documents']}")
    print(f"Total chunks: {result['total_chunks']}")
    print(f"Knowledge file: {result['knowledge_file']}")
    