import sys
from pathlib import Path

from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from settings import EMBEDDING_MODEL, KNOWLEDGE_COLLECTION, QDRANT_URL, SCHEMA_COLLECTION


# ============================================================
# CONFIGURATION
# ============================================================

KNOWLEDGE_DIR = Path(__file__).parent

COLLECTION_NAME = KNOWLEDGE_COLLECTION
if COLLECTION_NAME == SCHEMA_COLLECTION:
    raise RuntimeError("KNOWLEDGE_COLLECTION must not match SCHEMA_COLLECTION.")


# ============================================================
# LOAD EMBEDDING MODEL
# ============================================================

print("Loading embedding model...")

model = SentenceTransformer(EMBEDDING_MODEL)

print("Embedding model loaded!")


# ============================================================
# CONNECT TO QDRANT
# ============================================================

client = QdrantClient(url=QDRANT_URL, timeout=60)


# ============================================================
# READ KNOWLEDGE FILES
# ============================================================

documents = []
for file_path in KNOWLEDGE_DIR.glob("*.txt"):
    print(f"Reading: {file_path.name}")
    text = file_path.read_text(encoding="utf-8")
    paragraphs = [paragraph.strip() for paragraph in text.split("\n\n") if paragraph.strip()]
    for section, paragraph in enumerate(paragraphs, start=1):
        documents.append(
            {
                "file": file_path.name,
                "title": f"{file_path.stem.replace('_', ' ').title()} #{section}",
                "text": paragraph,
            }
        )


# ============================================================
# CHECK DOCUMENTS
# ============================================================

if not documents:
    print("No knowledge passages found.")
    sys.exit(1)

print(f"\nFound {len(documents)} knowledge passage(s).")


# CREATE EMBEDDINGS
# ============================================================

texts = [
    document["text"]
    for document in documents
]


print("\nCreating embeddings...")

vectors = model.encode(texts, show_progress_bar=True).tolist()

print("Embeddings created!")


# ============================================================
# CREATE / RECREATE QDRANT COLLECTION
# ============================================================

print(
    f"\nCreating Qdrant collection: "
    f"{COLLECTION_NAME}"
)


if client.collection_exists(collection_name=COLLECTION_NAME):
    client.delete_collection(collection_name=COLLECTION_NAME)

client.create_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=VectorParams(size=len(vectors[0]), distance=Distance.COSINE),
)


# ============================================================
# INSERT DOCUMENTS
# ============================================================

points = []


for index, document in enumerate(documents):

    points.append(

        PointStruct(

            id=index,

            vector=vectors[index],

            payload={

                "file": document["file"],
                "title": document["title"],
                "section": index,

                "text": document["text"]

            }

        )

    )


client.upsert(

    collection_name=COLLECTION_NAME,

    points=points

)


# ============================================================
# FINISHED
# ============================================================

print(
    "\n========================================"
)

print(
    "Knowledge passages indexed successfully!"
)

print(
    f"Collection: {COLLECTION_NAME}"
)

print(
    f"Passages indexed: {len(points)}"
)

print(
    "========================================"
)
