import math
from sentence_transformers import SentenceTransformer
from config import EMBEDDING_MODEL_NAME

_embedding_model = None

def get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return _embedding_model

def embed_text(text: str) -> list[float]:
    model = get_embedding_model()
    vector = model.encode(text, convert_to_numpy = True)
    return vector.tolist()

def cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    if not vec1 or not vec2:
        return 0.0

    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    norm_1 = math.sqrt(sum(a * a for a in vec1))
    norm_2 = math.sqrt(sum(b * b for b in vec2))

    if norm_1 == 0 or norm_2 == 0:
        return 0.0

    return dot_product / (norm_1 * norm_2)



