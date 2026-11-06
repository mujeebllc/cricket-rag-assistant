import sys
from pathlib import Path

from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from settings import EMBEDDING_MODEL, KNOWLEDGE_COLLECTION, QDRANT_URL


# ============================================================
# LOAD EMBEDDING MODEL
# ============================================================

print("Loading knowledge embedding model...")

model = SentenceTransformer(EMBEDDING_MODEL)

print("Knowledge embedding model loaded!")


# ============================================================
# CONNECT TO QDRANT
# ============================================================

client = QdrantClient(url=QDRANT_URL)


# ============================================================
# COLLECTION
# ============================================================

COLLECTION_NAME = KNOWLEDGE_COLLECTION


# ============================================================
# RETRIEVE KNOWLEDGE
# ============================================================

def retrieve_knowledge(question, top_k=3):

    print("\n[Knowledge RAG] Retrieving knowledge...")

    # Convert question into embedding
    query_vector = model.encode(
        question
    ).tolist()


    # Search Qdrant
    results = client.query_points(

        collection_name=COLLECTION_NAME,

        query=query_vector,

        limit=top_k

    )


    # Get retrieved points
    points = results.points


    if not points:

        print(
            "[Knowledge RAG] No relevant knowledge found."
        )

        return ""


    # Build context
    context = ""


    for point in points:

        filename = point.payload.get(
            "file",
            "unknown"
        )

        text = point.payload.get(
            "text",
            ""
        )


        print(
            f"[Knowledge RAG] Retrieved: {filename}"
        )


        context += text

        context += "\n\n"


    return context
