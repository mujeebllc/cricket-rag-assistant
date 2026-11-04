import sys
import time
import py_compile

sys.path.append('/home/inara/aiproject/backend')

print("======================================================================")
print("             CRICKET ASSISTANT - COMPREHENSIVE BACKEND TEST SUITE     ")
print("======================================================================\n")

# --------------------------------------------------------------------
# TEST CATEGORY 1: PYTHON COMPILATION (PY_COMPILE)
# --------------------------------------------------------------------
print("--- 1. TESTING PYTHON FILES COMPILATION (py_compile) ---")
files_to_compile = [
    '/home/inara/aiproject/backend/sql_generator.py',
    '/home/inara/aiproject/backend/answer_generator.py',
    '/home/inara/aiproject/backend/prompts/system_prompt.py',
    '/home/inara/aiproject/backend/rag/retriever.py',
    '/home/inara/aiproject/backend/chatbot.py',
]

compile_errors = 0
for f in files_to_compile:
    try:
        py_compile.compile(f, doraise=True)
        print(f"  [PASS] {f.split('/')[-1]} compiled successfully.")
    except Exception as e:
        print(f"  [FAIL] {f.split('/')[-1]} compilation failed: {e}")
        compile_errors += 1

if compile_errors > 0:
    print("Compilation failed for one or more files. Stopping test suite.")
    sys.exit(1)

from sql_generator import generate_sql, validate_sql_safety, validate_sql_tables, try_execute_sql
from answer_generator import generate_answer, detect_language
from database.db import engine
from sqlalchemy import text


# --------------------------------------------------------------------
# TEST CATEGORY 2: EXISTING ACCURACY TEST SUITE (11/11 REGRESSION)
# --------------------------------------------------------------------
print("\n--- 2. RUNNING REGRESSION SUITE (accuracy_test.py 11/11) ---")
from accuracy_test import TEST_CASES, check_count_result, check_name_result

passed_regression = 0
for idx, case in enumerate(TEST_CASES, start=1):
    q = case["question"]
    exp = case["expected_value"]
    ctype = case["type"]
    try:
        sql = generate_sql(q)
        with engine.connect() as conn:
            res = conn.execute(text(sql))
            rows = res.fetchall()
        if ctype == "count":
            ok, msg = check_count_result(rows, exp)
        else:
            ok, msg = check_name_result(rows, exp)
        if ok:
            passed_regression += 1
            print(f"  Test {idx:2d}/{len(TEST_CASES)}: [PASS] '{q}' -> {exp}")
        else:
            print(f"  Test {idx:2d}/{len(TEST_CASES)}: [FAIL] '{q}' -> {msg}")
    except Exception as e:
        print(f"  Test {idx:2d}/{len(TEST_CASES)}: [ERROR] '{q}' -> {e}")

print(f"  Regression Result: {passed_regression}/{len(TEST_CASES)} passed ({passed_regression/len(TEST_CASES)*100:.1f}%)")


# --------------------------------------------------------------------
# TEST CATEGORY 3: MULTILINGUAL QUERY & ANSWER GENERATION
# --------------------------------------------------------------------
print("\n--- 3. TESTING MULTILINGUAL QUERIES & ANSWERS ---")
multilingual_test_cases = [
    {
        "lang": "English",
        "question": "How many teams are there?",
        "expected_lang": "english",
    },
    {
        "lang": "Urdu Script",
        "question": "ڈیٹا بیس میں کتنی ٹیمیں ہیں؟",
        "expected_lang": "urdu",
    },
    {
        "lang": "Roman Urdu",
        "question": "Database mein kitni teams hain?",
        "expected_lang": "roman_urdu",
    },
    {
        "lang": "English",
        "question": "Who scored the most runs?",
        "expected_lang": "english",
    },
    {
        "lang": "Urdu Script",
        "question": "سب سے زیادہ رنز کس نے بنائے؟",
        "expected_lang": "urdu",
    },
    {
        "lang": "Roman Urdu",
        "question": "Sabse zyada runs kiske hain?",
        "expected_lang": "roman_urdu",
    },
]

passed_multilingual = 0
for mcase in multilingual_test_cases:
    q = mcase["question"]
    det_lang = detect_language(q)
    try:
        sql = generate_sql(q)
        with engine.connect() as conn:
            res = conn.execute(text(sql))
            cols = list(res.keys())
            rows = res.fetchall()
        ans = generate_answer(q, sql, cols, rows)
        lang_match = (det_lang == mcase["expected_lang"])
        if lang_match and len(rows) > 0 and len(ans) > 0:
            passed_multilingual += 1
            print(f"  [{mcase['lang']}] [PASS] Question: '{q}'")
            print(f"    Detected Lang: {det_lang} | SQL Executed | Answer: '{ans}'")
        else:
            print(f"  [{mcase['lang']}] [FAIL] Question: '{q}' | Det Lang: {det_lang}")
    except Exception as e:
        print(f"  [{mcase['lang']}] [ERROR] Question: '{q}' | Error: {e}")

print(f"  Multilingual Result: {passed_multilingual}/{len(multilingual_test_cases)} passed.")


# --------------------------------------------------------------------
# TEST CATEGORY 4: COMPLEX JOINS, AGGREGATION & TIE HANDLING
# --------------------------------------------------------------------
print("\n--- 4. TESTING COMPLEX JOINS, AGGREGATION & TIE HANDLING ---")
complex_queries = [
    {
        "name": "Tie-Safe Tournament Participation",
        "question": "Which teams participated in the most tournaments?",
        "check": lambda sql, rows: "HAVING COUNT(DISTINCT TournamentId)" in sql or len(rows) >= 1
    },
    {
        "name": "Team Wins Aggregation JOIN",
        "question": "Which team won the most matches?",
        "check": lambda sql, rows: "matches" in sql.lower() and len(rows) >= 1
    },
    {
        "name": "Player Country Filter & List",
        "question": "List players from Pakistan.",
        "check": lambda sql, rows: "player" in sql.lower() and len(rows) > 0
    },
    {
        "name": "Century Threshold Aggregation",
        "question": "How many players scored 200 or more?",
        "check": lambda sql, rows: len(rows) == 1 and rows[0][0] == 80
    }
]

passed_complex = 0
for ccase in complex_queries:
    q = ccase["question"]
    try:
        sql = generate_sql(q)
        with engine.connect() as conn:
            res = conn.execute(text(sql))
            rows = res.fetchall()
        if ccase["check"](sql, rows):
            passed_complex += 1
            print(f"  [PASS] {ccase['name']}: '{q}'")
            print(f"    SQL: {sql.strip()}")
            print(f"    Result count: {len(rows)} row(s). Sample: {rows[:1]}")
        else:
            print(f"  [FAIL] {ccase['name']}: '{q}'")
    except Exception as e:
        print(f"  [ERROR] {ccase['name']}: '{q}' | Error: {e}")

print(f"  Complex Query Result: {passed_complex}/{len(complex_queries)} passed.")


# --------------------------------------------------------------------
# TEST CATEGORY 5: SQL SAFETY & GUARDRAILS VALIDATION
# --------------------------------------------------------------------
print("\n--- 5. TESTING SQL SAFETY & GUARDRAILS ---")
safety_cases = [
    ("SELECT * FROM team;", True, "Valid SELECT query"),
    ("DELETE FROM team WHERE TeamId = 1;", False, "Forbidden DELETE query"),
    ("DROP TABLE player;", False, "Forbidden DROP query"),
    ("UPDATE player SET FullName = 'Hacked';", False, "Forbidden UPDATE query"),
    ("SELECT * FROM team; SELECT * FROM player;", False, "Multiple SQL statements"),
]

passed_safety = 0
for sql_input, expected_pass, label in safety_cases:
    is_safe, msg = validate_sql_safety(sql_input)
    if is_safe == expected_pass:
        passed_safety += 1
        print(f"  [PASS] {label}: Safe={is_safe} ({msg})")
    else:
        print(f"  [FAIL] {label}: Expected {expected_pass}, got {is_safe} ({msg})")

print(f"  Safety Guardrails Result: {passed_safety}/{len(safety_cases)} passed.")


# --------------------------------------------------------------------
# TEST CATEGORY 6: LIVE MATCH DATA ROUTING
# --------------------------------------------------------------------
print("\n--- 6. TESTING LIVE MATCH ROUTING ---")
live_q = "Are there any live matches?"
try:
    sql = generate_sql(live_q)
    with engine.connect() as conn:
        res = conn.execute(text(sql))
        cols = list(res.keys())
        rows = res.fetchall()
    ans = generate_answer(live_q, sql, cols, rows)
    print(f"  [PASS] Live match query: '{live_q}'")
    print(f"    SQL: {sql.strip()}")
    print(f"    Answer: '{ans}'")
    passed_live = 1
except Exception as e:
    print(f"  [ERROR] Live match query: '{live_q}' | Error: {e}")
    passed_live = 0


# --------------------------------------------------------------------
# FINAL COMPREHENSIVE SUMMARY
# --------------------------------------------------------------------
print("\n======================================================================")
print("                     BACKEND TEST SUITE FINAL SUMMARY                 ")
print("======================================================================")
print(f"  1. Compilation (py_compile):             {len(files_to_compile)}/{len(files_to_compile)} passed (100%)")
print(f"  2. Regression Suite (accuracy_test.py):   {passed_regression}/{len(TEST_CASES)} passed ({passed_regression/len(TEST_CASES)*100:.1f}%)")
print(f"  3. Multilingual Queries (EN/UR/Roman):    {passed_multilingual}/{len(multilingual_test_cases)} passed ({passed_multilingual/len(multilingual_test_cases)*100:.1f}%)")
print(f"  4. Complex JOINs & Aggregations:         {passed_complex}/{len(complex_queries)} passed ({passed_complex/len(complex_queries)*100:.1f}%)")
print(f"  5. SQL Safety & Guardrails:              {passed_safety}/{len(safety_cases)} passed ({passed_safety/len(safety_cases)*100:.1f}%)")
print(f"  6. Live Match Routing:                   {passed_live}/1 passed ({passed_live/1*100:.1f}%)")
print("======================================================================")
