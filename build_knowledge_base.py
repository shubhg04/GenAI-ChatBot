import json
import os
import re
import faiss
import numpy as np
from config import RAG_METADATA_FILE, FAISS_INDEX_FILE, RAG_CHUNK_SIZE, RAG_CHUNK_OVERLAP
from embedding_utils import embed_text


DOCUMENTS_FILE = "knowledge_docs.json"

def load_documents():
    if not os.path.exists(DOCUMENTS_FILE):
        return []

    with open(DOCUMENTS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)

def normalize_text(text: str):
    if not text or not text.strip():
        return ""

    text = re.sub(r'\r\n?', '\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text.strip()


def split_text_into_chunks(
    text: str,
    chunk_size: int = RAG_CHUNK_SIZE,
    overlap: int = RAG_CHUNK_OVERLAP
):
    text = normalize_text(text)

    if not text:
        return []

    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = min(start + chunk_size, text_length)

        if end < text_length:
            newline_boundary = text.rfind("\n", start, end)
            sentence_boundary = text.rfind(". ", start, end)
            space_boundary = text.rfind(" ", start, end)

            boundary = max(newline_boundary, sentence_boundary, space_boundary)

            if boundary > start + int(chunk_size * 0.6):
                end = boundary + 1

        chunk_text = text[start:end].strip()

        if chunk_text:
            chunks.append(chunk_text)

        if end >= text_length:
            break

        start = max(0, end - overlap)

    return chunks


def build_chunks_from_document(document):
    if not isinstance(document, dict):
        return []

    doc_id = document.get("doc_id")
    if not doc_id:
        return []

    content = document.get("content", "").strip()
    if not content:
        return []

    text_chunks = split_text_into_chunks(content)
    chunks = []

    for index, chunk_text in enumerate(text_chunks, start=1):
        chunk = {
            "id": f"{doc_id}-chunk-{index}",
            "doc_id": doc_id,
            "title": document.get("title", "Untitled"),
            "content": chunk_text,
            "chunk_index": index
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
    