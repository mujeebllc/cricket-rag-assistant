from sqlalchemy import create_engine, text
from langchain_ollama import OllamaLLM
from settings import OLLAMA_BASE_URL, OLLAMA_MODEL, get_database_url

# -----------------------------
# Connect to Database
# -----------------------------
engine = create_engine(get_database_url())

# -----------------------------
# Load Ollama Model
# -----------------------------
llm = OllamaLLM(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL)

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
