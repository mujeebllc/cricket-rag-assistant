import sys
import py_compile

sys.path.append('/home/inara/aiproject/backend')

print("==================================================")
print("1. RUNNING PY_COMPILE ON sql_generator.py")
print("==================================================")
py_compile.compile('/home/inara/aiproject/backend/sql_generator.py', doraise=True)
print("-> py_compile PASSED: 0 syntax errors found.")

from sql_generator import generate_direct_team_tournament_participation_sql
from database.db import engine
from sqlalchemy import text

print("\n==================================================")
print("2. TESTING DETERMINISTIC RULE ON ENGLISH VARIATIONS")
print("==================================================")
questions = [
    "Which teams participated in the most tournaments?",
    "Which team participated in the most tournaments?",
    "What teams played in the most tournaments?",
    "Which teams have participated in the most tournaments?",
    "Which team played in the most tournaments?",
    "What team participated in the most tournaments?",
]

for q in questions:
    sql = generate_direct_team_tournament_participation_sql(q)
    print(f"\nQuestion: '{q}'")
    if sql:
        print("-> RULE MATCHED! Generated SQL:")
        print(sql)
    else:
        print("-> FAILED: Rule returned None")
        sys.exit(1)

print("\n==================================================")
print("3. TESTING NEGATIVE UNRELATED QUESTIONS")
print("==================================================")
negative_questions = [
    "Which tournament has the most teams?",
    "Which teams won the most matches?",
    "Show all teams.",
]

for q in negative_questions:
    sql = generate_direct_team_tournament_participation_sql(q)
    print(f"\nQuestion: '{q}'")
    if sql is None:
        print("-> PASSED: Rule returned None (ignored query).")
    else:
        print(f"-> FAILED: Rule incorrectly claimed query: {sql}")
        sys.exit(1)

print("\n==================================================")
print("4. EXECUTING GENERATED SQL AGAINST MARIADB")
print("==================================================")
target_q = "Which teams participated in the most tournaments?"
generated_sql = generate_direct_team_tournament_participation_sql(target_q)
print(f"Target Question: '{target_q}'")
print(f"Executing SQL:\n{generated_sql}\n")

with engine.connect() as conn:
    rows = conn.execute(text(generated_sql)).fetchall()
    print(f"MariaDB Result Count: {len(rows)} row(s)")
    for r in rows:
        print(f"  TeamName: {r[0]} | TournamentCount: {r[1]}")

print("\n==================================================")
print("ALL VERIFICATIONS COMPLETED SUCCESSFULLY!")
print("==================================================")
