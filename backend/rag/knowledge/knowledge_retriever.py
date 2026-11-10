from functools import lru_cache
from pathlib import Path
import sys

from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from settings import EMBEDDING_MODEL, KNOWLEDGE_COLLECTION, QDRANT_URL


COLLECTION_NAME = KNOWLEDGE_COLLECTION
MIN_RELEVANCE_SCORE = 0.59


@lru_cache(maxsize=1)
def _get_model():
    print("Loading knowledge embedding model...")
    model = SentenceTransformer(EMBEDDING_MODEL)
    print("Knowledge embedding model loaded!")
    return model


@lru_cache(maxsize=1)
def _get_client():
    return QdrantClient(url=QDRANT_URL)


# ============================================================
# RETRIEVE KNOWLEDGE
# ============================================================

def retrieve_knowledge(question, top_k=3):
    print("\n[Knowledge RAG] Retrieving knowledge...")
    query_vector = _get_model().encode(question).tolist()
    results = _get_client().query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k,
        with_payload=True,
        with_vectors=False,
    )

    relevant_points = [
        point
        for point in results.points
        if (point.score or 0.0) >= MIN_RELEVANCE_SCORE
        and point.payload
        and point.payload.get("text")
    ]
    if not relevant_points:
        return "", []

    context_parts = []
    sources = []
    for point in relevant_points:
        source = point.payload.get("title") or point.payload.get("file", "unknown")
        context_parts.append(f"Source: {source}\n{point.payload['text']}")
        if source not in sources:
            sources.append(source)

    return "\n\n".join(context_parts), sources
