import sys
import py_compile

sys.path.append('/home/inara/aiproject/backend')

print("=== STEP 1: VERIFY PY_COMPILE ===")
py_compile.compile('/home/inara/aiproject/backend/sql_generator.py', doraise=True)
print("SUCCESS: py_compile passed with 0 syntax errors.")

from sql_generator import generate_direct_team_tournament_participation_sql, generate_sql
from database.db import engine
from sqlalchemy import text

print("\n=== STEP 2: TEST POSITIVE PHRASINGS ===")
positive_questions = [
    "Which teams participated in the most tournaments?",
    "Which team participated in the most tournaments?",
    "What teams played in the most tournaments?",
    "Which teams have participated in the most tournaments?",
    "Which team played in the most tournaments?",
    "What team participated in the most tournaments?",
]

for q in positive_questions:
    rule_sql = generate_direct_team_tournament_participation_sql(q)
    full_sql = generate_sql(q)
    assert rule_sql is not None, f"Rule returned None for '{q}'"
    assert rule_sql == full_sql, f"generate_sql did not use deterministic rule for '{q}'"
    print(f"PASS: '{q}' -> Triggered rule correctly.")

print("\n=== STEP 3: TEST NEGATIVE QUESTIONS (MUST BE IGNORED BY RULE) ===")
negative_questions = [
    "Which tournament has the most teams?",
    "Which teams won the most matches?",
    "Show all teams.",
]

for q in negative_questions:
    rule_sql = generate_direct_team_tournament_participation_sql(q)
    assert rule_sql is None, f"Rule incorrectly claimed negative query: '{q}' (Rule SQL: {rule_sql})"
    print(f"PASS: '{q}' -> Correctly ignored by tournament participation rule (returns None).")

print("\n=== STEP 4: EXECUTE DETERMINISTIC SQL AGAINST MARIADB ===")
q_target = "Which teams participated in the most tournaments?"
sql_target = generate_sql(q_target)

print(f"Executing Query against database clubinfo_afc:\n{sql_target}\n")

with engine.connect() as conn:
    rows = conn.execute(text(sql_target)).fetchall()
    print(f"Returned {len(rows)} row(s):")
    for r in rows:
        print(f"  TeamName: {r[0]} | TournamentCount: {r[1]}")

print("\nALL VERIFICATIONS PASSED 100% CLEANLY!")
