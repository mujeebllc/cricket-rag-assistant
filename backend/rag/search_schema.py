from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient

# -----------------------------
# Load Embedding Model
# -----------------------------
print("Loading embedding model...")
model = SentenceTransformer("BAAI/bge-m3")
print("Model loaded!")

# -----------------------------
# Connect to Qdrant
# -----------------------------
client = QdrantClient(
    host="localhost",
    port=6333
)

COLLECTION_NAME = "cricket_schema"

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
