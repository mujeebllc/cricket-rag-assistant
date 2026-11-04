import py_compile
import sys
sys.path.append('/home/inara/aiproject/backend')

print("=== STEP 1: RUN PY_COMPILE ===")
try:
    py_compile.compile('/home/inara/aiproject/backend/sql_generator.py', doraise=True)
    print("SUCCESS: sql_generator.py py_compile passed cleanly with no syntax errors!")
except Exception as e:
    print(f"FAILED: py_compile error: {e}")
    sys.exit(1)

from sql_generator import generate_sql
from database.db import engine
from sqlalchemy import text

print("\n=== STEP 2: TEST POSITIVE QUESTIONS ===")
positive_questions = [
    "Which teams participated in the most tournaments?",
    "Which team participated in the most tournaments?",
    "What teams played in the most tournaments?",
    "Which teams have participated in the most tournaments?",
]

for q in positive_questions:
    print(f"\nQuestion: '{q}'")
    generated_sql = generate_sql(q)
    print(f"Generated SQL:\n{generated_sql}")
    assert "HAVING COUNT(DISTINCT TournamentId)" in generated_sql, f"Failed for {q}"

print("\n=== STEP 3: TEST NEGATIVE QUESTIONS (MUST NOT TRIGGER RULE) ===")
negative_questions = [
    "Which tournament has the most teams?",
    "Which teams won the most matches?",
    "Show all teams.",
]

for q in negative_questions:
    print(f"\nQuestion: '{q}'")
    generated_sql = generate_sql(q)
    print(f"Generated SQL:\n{generated_sql}")
    assert "HAVING COUNT(DISTINCT TournamentId)" not in generated_sql, f"False positive triggered for {q}"

print("\n=== STEP 4: EXECUTE GENERATED SQL AGAINST MARIADB ===")
target_q = "Which teams participated in the most tournaments?"
sql_to_run = generate_sql(target_q)
print(f"Executing SQL against MariaDB database clubinfo_afc:\n{sql_to_run}\n")

with engine.connect() as conn:
    res = conn.execute(text(sql_to_run)).fetchall()
    print("=== MARIADB QUERY RESULT ===")
    for row in res:
        print(f"Team: {row[0]} | Tournament Count: {row[1]}")

print("\nALL VERIFICATIONS PASSED SUCCESSFULLY!")
