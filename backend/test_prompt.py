from langchain_ollama import OllamaLLM

llm = OllamaLLM(model="qwen2.5:7b")

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
