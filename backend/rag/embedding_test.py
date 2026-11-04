from sentence_transformers import SentenceTransformer

print("Loading embedding model...")

model = SentenceTransformer("BAAI/bge-m3")

print("Model loaded successfully!")

text = "Show all players in Islamabad United"

embedding = model.encode(text)

print("Embedding dimension:", len(embedding))
print("First 10 values:")
print(embedding[:10])
