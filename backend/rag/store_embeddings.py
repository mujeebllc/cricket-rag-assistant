import os
import sys
from pathlib import Path
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
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
client = QdrantClient(url=QDRANT_URL, timeout=60)

COLLECTION_NAME = SCHEMA_COLLECTION

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
        size=model.get_sentence_embedding_dimension(),
        distance=Distance.COSINE
    )
)

print("Collection ready!")

# -----------------------------
# Read Chunks
# -----------------------------
CHUNK_DIR = Path(__file__).resolve().parent / "schema_chunks"

files = sorted(os.listdir(CHUNK_DIR))

points = []

print(f"\nFound {len(files)} chunk files")

# -----------------------------
# Embed + Prepare Points
# -----------------------------
for idx, filename in enumerate(files):

    path = CHUNK_DIR / filename

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
