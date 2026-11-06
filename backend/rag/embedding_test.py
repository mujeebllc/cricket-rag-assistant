import sys
from pathlib import Path

from sentence_transformers import SentenceTransformer

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from settings import EMBEDDING_MODEL

print("Loading embedding model...")

model = SentenceTransformer(EMBEDDING_MODEL)

print("Model loaded successfully!")

text = "Show all players in Islamabad United"

embedding = model.encode(text)

print("Embedding dimension:", len(embedding))
print("First 10 values:")
print(embedding[:10])
