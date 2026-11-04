from pathlib import Path

from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct


# ============================================================
# CONFIGURATION
# ============================================================

KNOWLEDGE_DIR = Path(__file__).parent

COLLECTION_NAME = "cricket_knowledge"


# ============================================================
# LOAD EMBEDDING MODEL
# ============================================================

print("Loading embedding model...")

model = SentenceTransformer("BAAI/bge-m3")

print("Embedding model loaded!")


# ============================================================
# CONNECT TO QDRANT
# ============================================================

client = QdrantClient(
    host="localhost",
    port=6333
)


# ============================================================
# READ KNOWLEDGE FILES
# ============================================================

documents = []

for file_path in KNOWLEDGE_DIR.glob("*.txt"):

    if file_path.name == "cricket_knowledge.txt":

        print(f"Reading: {file_path.name}")

        text = file_path.read_text(
            encoding="utf-8"
        )

        documents.append(
            {
                "file": file_path.name,
                "text": text
            }
        )


# ============================================================
# CHECK DOCUMENTS
# ============================================================

if not documents:

    print("No knowledge documents found.")

    exit()


print(
    f"\nFound {len(documents)} knowledge document(s)."
)


# ============================================================
# CREATE EMBEDDINGS
# ============================================================

texts = [
    document["text"]
    for document in documents
]


print("\nCreating embeddings...")

vectors = model.encode(
    texts
).tolist()

print("Embeddings created!")


# ============================================================
# CREATE / RECREATE QDRANT COLLECTION
# ============================================================

print(
    f"\nCreating Qdrant collection: "
    f"{COLLECTION_NAME}"
)


client.recreate_collection(

    collection_name=COLLECTION_NAME,

    vectors_config=VectorParams(

        size=len(vectors[0]),

        distance=Distance.COSINE

    )
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
    "Knowledge documents indexed successfully!"
)

print(
    f"Collection: {COLLECTION_NAME}"
)

print(
    f"Documents indexed: {len(points)}"
)

print(
    "========================================"
)
