from typing import TypedDict
from sqlalchemy import create_engine, text
from langchain_ollama import OllamaLLM
from langgraph.graph import StateGraph, END
import re

# -----------------------------
# Database Connection
# -----------------------------
DATABASE_URL = "mysql+pymysql://appuser:app123@127.0.0.1:3306/clubinfo_afc"
engine = create_engine(DATABASE_URL)

# -----------------------------
# Load LLM
# -----------------------------
llm = OllamaLLM(model="qwen2.5:7b")

# -----------------------------
# Graph State
# -----------------------------
class AgentState(TypedDict):
    question: str

# -----------------------------
# SQL Agent Node
# -----------------------------
def sql_node(state):

    question = state["question"]

    prompt = f"""
You are an expert MariaDB SQL generator.

Database: clubinfo_afc

Table: player

Columns:
PlayerId
FullName
DOB
MajorTeams
BattingStyle
BowlingStyle
Image
ClubId
Status
PlayingRole
Registered
FBId
Height
Weight
TwitterId
ShortName
FatherName
CNIC
Domicile
Qualification
PresentAddress
PermanentAddress
PHoneNo
CityId
CountryId
City
Country

Rules:

Return ONLY SQL.

Never explain.

Never use markdown.

Never invent column names.

Use ONLY the columns listed above.

Question:

{question}
"""

    response = llm.invoke(prompt)

    match = re.search(
        r"(SELECT|INSERT|UPDATE|DELETE).*?;",
        response,
        re.IGNORECASE | re.DOTALL,
    )

    if not match:
        print("\nNo SQL Found\n")
        print(response)
        return state

    sql = match.group(0).strip()

    print("\nGenerated SQL:\n")
    print(sql)

    try:

        with engine.connect() as conn:

            result = conn.execute(text(sql))

            rows = result.fetchall()

            print(f"\nReturned {len(rows)} rows\n")

            for row in rows[:20]:
                print(row)

    except Exception as e:

        print("\nSQL Error\n")
        print(e)

    return state

# -----------------------------
# Build Graph
# -----------------------------
builder = StateGraph(AgentState)

builder.add_node("sql_agent", sql_node)

builder.set_entry_point("sql_agent")

builder.add_edge("sql_agent", END)

graph = builder.compile()

# -----------------------------
# Run
# -----------------------------
print("🤖 Cricket SQL Agent Started!")

while True:

    question = input("\nAsk Question (type exit): ")

    if question.lower() == "exit":
        break

    graph.invoke({"question": question})

