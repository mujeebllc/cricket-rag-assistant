import sys
from pathlib import Path
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from settings import EMBEDDING_MODEL, QDRANT_URL, SCHEMA_COLLECTION

# -----------------------------
# Load Embedding Model
# -----------------------------
print("Loading embedding model...")
model = SentenceTransformer(EMBEDDING_MODEL)
print("Model loaded!")

# -----------------------------
# Connect to Qdrant
# -----------------------------
client = QdrantClient(url=QDRANT_URL)

COLLECTION_NAME = SCHEMA_COLLECTION

# -----------------------------
# Search Function
# -----------------------------
def search_schema(question, top_k=5):

    query_vector = model.encode(question).tolist()

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k
    )

    print("\nTop Relevant Schema Chunks\n")
    print("=" * 60)

    for i, point in enumerate(results.points, start=1):

        print(f"\nResult {i}")
        print("-" * 60)

        print("File:")
        print(point.payload["file"])

        print("\nContent:")
        print(point.payload["text"][:700])

# -----------------------------
# Main
# -----------------------------
if __name__ == "__main__":

    while True:

        question = input("\nAsk Question (exit to quit): ")

        if question.lower() == "exit":
            break

        search_schema(question)
