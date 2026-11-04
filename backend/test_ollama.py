from langchain_ollama import OllamaLLM

print("Loading model...")

llm = OllamaLLM(model="qwen2.5:7b")

print("Loaded")

print(llm.invoke("Hello"))
