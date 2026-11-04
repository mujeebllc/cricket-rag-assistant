from sqlalchemy import create_engine, text
from langchain_ollama import OllamaLLM

# -----------------------------
# Database Configuration
# -----------------------------
DB_USER = "appuser"
DB_PASSWORD = "app123"
DB_HOST = "127.0.0.1"
DB_PORT = "3306"
DB_NAME = "clubinfo_afc"

DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# -----------------------------
# Connect to Database
# -----------------------------
engine = create_engine(DATABASE_URL)

# -----------------------------
# Load Qwen Model
# -----------------------------
llm = OllamaLLM(model="qwen2.5:7b")

print("=" * 50)
print("🤖 Cricket SQL Agent Started!")
print("Type 'exit' to quit.")
print("=" * 50)

while True:

    question = input("\nAsk your question: ")

    if question.lower() == "exit":
        print("Goodbye!")
        break

    # Prompt for Qwen
    prompt = f"""
You are an expert SQL assistant.

Database: MariaDB

Available table:
player

Convert the user's question into ONLY ONE SQL query.

Rules:
1. Return ONLY SQL.
2. Do NOT explain.
3. Do NOT use markdown.
4. Do NOT use ```sql.
5. End the query with ;

User Question:
{question}
"""

    # Generate SQL
    sql = llm.invoke(prompt)

    # Clean the output
    sql = sql.replace("```sql", "")
    sql = sql.replace("```", "")
    sql = sql.strip()

    print("\nGenerated SQL:")
    print(sql)

    try:
        with engine.connect() as connection:

            result = connection.execute(text(sql))

            rows = result.fetchall()

            print("\nQuery Result:\n")

            if len(rows) == 0:
                print("No data found.")

            else:
                for row in rows:
                    print("Player:", row[1])

    except Exception as e:
        print("\n❌ SQL Error:")
        print(e)
