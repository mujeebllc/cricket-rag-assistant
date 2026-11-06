from sqlalchemy import create_engine, text
from langchain_ollama import OllamaLLM

from settings import OLLAMA_BASE_URL, OLLAMA_MODEL, get_database_url

# -------------------------
# Database Connection
# -------------------------
engine = create_engine(get_database_url())

# -------------------------
# Load Ollama Model
# -------------------------
llm = OllamaLLM(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL)

print("✅ LangChain + Ollama Loaded")
print("✅ Database Connected")

with engine.connect() as conn:
    result = conn.execute(text("SHOW TABLES;"))

    print("\nTables:\n")

    for row in result:
        print(row[0])
