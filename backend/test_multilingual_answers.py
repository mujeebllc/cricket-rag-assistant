import sys
import py_compile
import re
from sqlalchemy import text

sys.path.append('/home/inara/aiproject/backend')

print("======================================================================")
print("            MULTILINGUAL ANSWER GENERATION VERIFICATION               ")
print("======================================================================\n")

# 1. COMPILATION CHECK
print("--- 1. PY_COMPILE CHECK ---")
files_to_check = [
    '/home/inara/aiproject/backend/prompts/answer_prompt.py',
    '/home/inara/aiproject/backend/answer_generator.py',
]
for f in files_to_check:
    py_compile.compile(f, doraise=True)
    print(f"  [PASS] {f.split('/')[-1]} compiled successfully.")

from sql_generator import generate_sql
from answer_generator import generate_answer, detect_language
from database.db import engine

# 2. MULTILINGUAL TESTS (3 QUESTION TYPES ACROSS 3 LANGUAGES)
print("\n--- 2. MULTILINGUAL ANSWER TESTS (3 TYPES x 3 LANGUAGES) ---")

test_cases = [
    # TYPE 1: RANKING / MOST RUNS
    {
        "type": "Ranking - Most Runs",
        "lang": "English",
        "question": "Who scored the most runs?",
        "expected_lang": "english",
        "expected_sub": "Aman Arshad",
    },
    {
        "type": "Ranking - Most Runs",
        "lang": "Urdu Script",
        "question": "سب سے زیادہ رنز کس نے بنائے؟",
        "expected_lang": "urdu",
        "expected_sub": "15", # Contains stat value or Urdu name
    },
    {
        "type": "Ranking - Most Runs",
        "lang": "Roman Urdu",
        "question": "Sabse zyada runs kiske hain?",
        "expected_lang": "roman_urdu",
        "expected_sub": "Aman Arshad",
    },

    # TYPE 2: ENTITY COUNT - TEAMS
    {
        "type": "Count - Teams",
        "lang": "English",
        "question": "How many teams are there?",
        "expected_lang": "english",
        "expected_sub": "982",
    },
    {
        "type": "Count - Teams",
        "lang": "Urdu Script",
        "question": "ڈیٹا بیس میں کتنی ٹیمیں ہیں؟",
        "expected_lang": "urdu",
        "expected_sub": "982",
    },
    {
        "type": "Count - Teams",
        "lang": "Roman Urdu",
        "question": "Database mein kitni teams hain?",
        "expected_lang": "roman_urdu",
        "expected_sub": "982",
    },

    # TYPE 3: RANKING / MOST WICKETS
    {
        "type": "Ranking - Most Wickets",
        "lang": "English",
        "question": "Who has taken the most wickets?",
        "expected_lang": "english",
        "expected_sub": "Taimoor Kiyani",
    },
    {
        "type": "Ranking - Most Wickets",
        "lang": "Urdu Script",
        "question": "سب سے زیادہ وکٹیں کس نے لیں؟",
        "expected_lang": "urdu",
        "expected_sub": "778", # Contains stat value or Urdu name
    },
    {
        "type": "Ranking - Most Wickets",
        "lang": "Roman Urdu",
        "question": "Sabse zyada wickets kiske hain?",
        "expected_lang": "roman_urdu",
        "expected_sub": "Taimoor Kiyani",
    },
]

passed_multi = 0
for tc in test_cases:
    q = tc["question"]
    det_lang = detect_language(q)
    try:
        sql = generate_sql(q)
        with engine.connect() as conn:
            res = conn.execute(text(sql))
            cols = list(res.keys())
            rows = res.fetchall()
        ans = generate_answer(q, sql, cols, rows)

        lang_ok = (det_lang == tc["expected_lang"])
        sub_ok = tc["expected_sub"].lower() in ans.lower()

        # Extra script checks
        script_ok = True
        if tc["expected_lang"] == "urdu":
            script_ok = bool(re.search(r'[\u0600-\u06FF]', ans))
        elif tc["expected_lang"] == "roman_urdu":
            script_ok = not bool(re.search(r'[\u0600-\u06FF]', ans))

        if lang_ok and sub_ok and script_ok and len(ans) > 0:
            passed_multi += 1
            print(f"\n  [PASS] [{tc['type']}] ({tc['lang']}): '{q}'")
            print(f"    SQL: {sql.strip()}")
            print(f"    Detected Lang: {det_lang}")
            print(f"    Generated Answer: '{ans}'")
        else:
            print(f"\n  [FAIL] [{tc['type']}] ({tc['lang']}): '{q}'")
            print(f"    Det Lang: {det_lang} (Expected {tc['expected_lang']})")
            print(f"    Script OK: {script_ok} | Sub OK: {sub_ok}")
            print(f"    Ans: '{ans}'")
    except Exception as e:
        print(f"\n  [ERROR] [{tc['type']}] ({tc['lang']}): '{q}' | Error: {e}")

print(f"\nMultilingual Answer Generation Result: {passed_multi}/{len(test_cases)} passed ({passed_multi/len(test_cases)*100:.1f}%)")

# 3. ACCURACY REGRESSION TEST (11/11)
print("\n--- 3. ACCURACY REGRESSION TEST (accuracy_test.py 11/11) ---")
from accuracy_test import TEST_CASES, check_count_result, check_name_result

passed_reg = 0
for idx, case in enumerate(TEST_CASES, start=1):
    q = case["question"]
    exp = case["expected_value"]
    ctype = case["type"]
    sql = generate_sql(q)
    with engine.connect() as conn:
        res = conn.execute(text(sql))
        rows = res.fetchall()
    if ctype == "count":
        ok, msg = check_count_result(rows, exp)
    else:
        ok, msg = check_name_result(rows, exp)
    if ok:
        passed_reg += 1

print(f"Regression Result: {passed_reg}/{len(TEST_CASES)} passed ({passed_reg/len(TEST_CASES)*100:.1f}%)\n")

print("======================================================================")
print(f"FINAL SUMMARY: Multilingual={passed_multi}/{len(test_cases)} | Regression={passed_reg}/{len(TEST_CASES)}")
print("======================================================================")
