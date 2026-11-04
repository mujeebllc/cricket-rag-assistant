import os
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

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
# Recreate Collection
# -----------------------------
collections = [c.name for c in client.get_collections().collections]

if COLLECTION_NAME in collections:
    print("Deleting old collection...")
    client.delete_collection(COLLECTION_NAME)

print("Creating new collection...")

client.create_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=VectorParams(
        size=1024,
        distance=Distance.COSINE
    )
)

print("Collection ready!")

# -----------------------------
# Read Chunks
# -----------------------------
CHUNK_DIR = "schema_chunks"

files = sorted(os.listdir(CHUNK_DIR))

points = []

print(f"\nFound {len(files)} chunk files")

# -----------------------------
# Embed + Prepare Points
# -----------------------------
for idx, filename in enumerate(files):

    path = os.path.join(CHUNK_DIR, filename)

    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    embedding = model.encode(text).tolist()

    points.append(
        PointStruct(
            id=idx,
            vector=embedding,
            payload={
                "file": filename,
                "text": text
            }
        )
    )

# -----------------------------
# Upload
# -----------------------------
print("\nUploading embeddings...")

client.upsert(
    collection_name=COLLECTION_NAME,
    points=points
)

print(f"\nUploaded {len(points)} embeddings successfully!")
