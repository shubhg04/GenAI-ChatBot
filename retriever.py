import json
import os
import numpy as np
import faiss
from config import RAG_METADATA_FILE, FAISS_INDEX_FILE, RAG_TOP_K, RAG_SIMILARITY_THRESHOLD
from embedding_utils import embed_text
import logging

logger = logging.getLogger(__name__)

class FAISSRetriever:
    def __init__(self):
        self.metadata = self.load_metadata()
        self.index = self.load_index()
        logger.info(
            f"FAISSRetriever initialized | metadata_count: {len(self.metadata)} "
            f"index_loaded: {self.index is not None}"
        )

    def load_metadata(self):
        if not os.path.exists(RAG_METADATA_FILE):
            logger.warning(f"Retriever metadata file not found: {RAG_METADATA_FILE}")
            return []

        with open(RAG_METADATA_FILE, "r", encoding="utf-8") as file:
            metadata = json.load(file)
        logger.info(f"Retriever metadata loaded successfully | metadata_count: {len(metadata)}")
        return metadata
    
    def load_index(self):
        if not os.path.exists(FAISS_INDEX_FILE):
            logger.warning(f"FAISS index file not found: {FAISS_INDEX_FILE}")
            return None
        
        index = faiss.read_index(FAISS_INDEX_FILE)
        logger.info("FAISS index loaded successfully")
        return index

    def retrieve(self, query, top_k = RAG_TOP_K):
        logger.info(
            f"retriever_stage = retrieve_start query_length: {len(query.strip())} "
            f"top_k: {top_k} similarity_threshold: {RAG_SIMILARITY_THRESHOLD}"
        )

        if not self.metadata or self.index is None:
            logger.warning(
                f"retriever_stage = retrieve_skipped reason = missing_metadata_or_index "
                f"metadata_count: {len(self.metadata)} index_loaded: {self.index is not None}"
            )
            return []

        query_embedding = embed_text(query)
        query_vector = np.array([query_embedding], dtype = "float32")

        faiss.normalize_L2(query_vector)

        distances, indices = self.index.search(query_vector, top_k)
        logger.info(
            f"retriever_stage = faiss_search_done raw_scores: {distances[0].tolist()} "
            f"raw_indices: {indices[0].tolist()}"
        )

        results = []
        for score, idx in zip(distances[0], indices[0]):
            if idx < 0 or idx >= len(self.metadata):
                logger.info(
                    f"retriever_stage = chunk_skipped reason = invalid_index "
                    f"idx: {idx} score: {round(float(score), 4)}"
                )
                continue

            similarity_score = float(score)

            if similarity_score < RAG_SIMILARITY_THRESHOLD:
                logger.info(
                    f"retriever_stage = chunk_skipped reason = below_threshold "
                    f"chunk_id: {self.metadata[idx]['id']} "
                    f"score: {round(similarity_score, 4)} "
                    f"threshold: {RAG_SIMILARITY_THRESHOLD}"
                )
                continue

            chunk = self.metadata[idx]

            results.append({
                "id": chunk["id"],
                "title": chunk["title"],
                "content": chunk["content"],
                "score": round(float(score), 4)
            })
        
        logger.info(
            f"retriever_stage = retrieve_done returned_count: {len(results)}"
        )
        return results