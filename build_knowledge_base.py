import json
import os
import re
import faiss
import numpy as np
from config import RAG_METADATA_FILE, FAISS_INDEX_FILE
from embedding_utils import embed_text


DOCUMENTS_FILE = "knowledge_docs.json"
CHUNK_SIZE = 2

def load_documents():
    if not os.path.exists(DOCUMENTS_FILE):
        return []

    with open(DOCUMENTS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def split_into_sentences(text):
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [sentence.strip() for sentence in sentences if sentence.strip()]


def build_chunks_from_document(document, chunk_size = CHUNK_SIZE):
    if not isinstance(document, dict):
        return []
    
    doc_id = document.get("doc_id")
    if not doc_id:
        return []
    
    content = document.get("content", "").strip()
    if not content:
        return []
    
    sentences = split_into_sentences(content)
    chunks = []

    for index in range(0, len(sentences), chunk_size):
        chunk_sentences = sentences[index:index + chunk_size]
        chunk_text = " ".join(chunk_sentences).strip()

        if not chunk_text:
            continue

        chunk = {
            "id": f"{document['doc_id']}-chunk-{(index // chunk_size) + 1}",
            "title": document.get("title", "Untitled"),
            "content": chunk_text,
        }
        chunks.append(chunk)

    return chunks

def build_knowledge_base():
    documents = load_documents()
    metadata = []
    embedding_vectors = []
    processed_docs = 0
    skipped_docs = 0

    for document in documents:
        document_chunks = build_chunks_from_document(document)
        if not document_chunks:
            skipped_docs += 1
            continue
        processed_docs += 1

        for chunk in document_chunks:
            embedding = embed_text(chunk["content"])
            metadata.append(chunk)
            embedding_vectors.append(embedding)

    with open(RAG_METADATA_FILE, "w", encoding="utf-8") as file:
        json.dump(metadata, file, indent = 4)

    if embedding_vectors:
        embedding_matrix = np.array(embedding_vectors, dtype = "float32")
        faiss.normalize_L2(embedding_matrix)
        
        vector_dimension = embedding_matrix.shape[1]
        index = faiss.IndexFlatIP(vector_dimension)
        index.add(embedding_matrix)
        faiss.write_index(index, FAISS_INDEX_FILE)

    return {
        "message": f"Knowledge base built successfully.",
        "total_documents": len(documents),
        "processed_documents": processed_docs,
        "skipped_documents": skipped_docs,
        "total_chunks": len(metadata),
        "knowledge_file": RAG_METADATA_FILE
    }


if __name__ == "__main__":
    result = build_knowledge_base()
    print(result["message"])
    print(f"Total documents: {result['total_documents']}")
    print(f"Total chunks: {result['total_chunks']}")
    print(f"Knowledge file: {result['knowledge_file']}")
    