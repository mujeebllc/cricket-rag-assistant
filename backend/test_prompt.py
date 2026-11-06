from langchain_ollama import OllamaLLM
from settings import OLLAMA_BASE_URL, OLLAMA_MODEL

llm = OllamaLLM(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL)

prompt = """
You are a SQL generator.

Question:
show all teams

Return only SQL.
"""

print("Calling...")
response = llm.invoke(prompt)
print("Done!")
print(response)
