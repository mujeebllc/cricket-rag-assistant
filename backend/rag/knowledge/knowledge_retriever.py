from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient


# ============================================================
# LOAD EMBEDDING MODEL
# ============================================================

print("Loading knowledge embedding model...")

model = SentenceTransformer("BAAI/bge-m3")

print("Knowledge embedding model loaded!")


# ============================================================
# CONNECT TO QDRANT
# ============================================================

client = QdrantClient(
    host="localhost",
    port=6333
)


# ============================================================
# COLLECTION
# ============================================================

COLLECTION_NAME = "cricket_knowledge"


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
