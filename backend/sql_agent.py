from sqlalchemy import create_engine, text
from langchain_ollama import OllamaLLM

# -------------------------
# Database Connection
# -------------------------
DATABASE_URL = "mysql+pymysql://appuser:app123@127.0.0.1:3306/clubinfo_afc"

engine = create_engine(DATABASE_URL)

# -------------------------
# Load Qwen
# -------------------------
llm = OllamaLLM(model="qwen2.5:7b")

print("✅ LangChain + Ollama Loaded")
print("✅ Database Connected")

# -------------------------
# Test Database
# -------------------------
with engine.connect() as conn:
    result = conn.execute(text("SHOW TABLES;"))

    print("\nTables:\n")

    for row in result:
        print(row[0])
