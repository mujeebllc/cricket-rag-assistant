from rag.retriever import retrieve_schema

print("Before retrieve")

schema = retrieve_schema("team table")

print("After retrieve")

print(schema[:500])

from rag.retriever import retrieve_schema

print("Before retrieval")

question = "Show me all teams"

schema = retrieve_schema(question)

print("After retrieval")

print("\nRetrieved Schema:\n")
print(schema)
from rag.retriever import retrieve_schema

print("Before retrieve")

schema = retrieve_schema("team table")

print("After retrieve")

print(schema[:500])
