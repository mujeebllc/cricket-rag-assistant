from langchain_ollama import OllamaLLM
from settings import OLLAMA_BASE_URL, OLLAMA_MODEL

print("Loading model...")

llm = OllamaLLM(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL)

print("Loaded")

print(llm.invoke("Hello"))
