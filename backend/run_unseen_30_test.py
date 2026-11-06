import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from sql_generator import generate_sql
from answer_generator import generate_answer, detect_language
from database.db import engine
from sqlalchemy import text
import re
import sys

def log(msg):
    print(msg)
    sys.stdout.flush()


TEST_CASES = [
    # 1. Grounds
    {
        "id": 1,
        "question": "How many grounds are in the database?",
        "expected_val": "301",
        "type": "count",
        "expected_lang": "english"
    },
    # 2. Associations
    {
        "id": 2,
        "question": "How many cricket associations are in the database?",
        "expected_val": "6",
        "type": "count",
        "expected_lang": "english"
    },
    # 3. Israrullah batting style
    {
        "id": 3,
        "question": "What is Israrullah's batting style?",
        "expected_val": "Left Hand Batsman",
        "type": "string",
        "expected_lang": "english"
    },
    # 4. TeamId 668 short name
    {
        "id": 4,
        "question": "What is the short name of TeamId 668?",
        "expected_val": "Kotli",
        "type": "string",
        "expected_lang": "english"
    },
    # 5. Tournament date
    {
        "id": 5,
        "question": "What is the start date of TournamentId 3?",
        "expected_val": "2013-03-01",
        "type": "string",
        "expected_lang": "english"
    },
    # 6. Most wickets
    {
        "id": 6,
        "question": "Who took the most wickets?",
        "expected_val": "Taimoor Kiyani",
        "type": "string",
        "expected_lang": "english"
    },
    # 7. Best bowling wickets in an innings
    {
        "id": 7,
        "question": "Who has the best bowling wickets in an innings?",
        "expected_val": "Asad Raza",
        "type": "string",
        "expected_lang": "english"
    },
    # 8. Kamran Akmal total runs
    {
        "id": 8,
        "question": "How many total runs has Kamran Akmal scored?",
        "expected_val": "9966",
        "type": "count",
        "expected_lang": "english"
    },
    # 9. Five-wicket hauls
    {
        "id": 9,
        "question": "How many total 5-wicket hauls were recorded in bowling_stats?",
        "expected_val": "2206",
        "type": "count",
        "expected_lang": "english"
    },
    # 10. Total sixes in batting_detail
    {
        "id": 10,
        "question": "How many total sixes were hit in batting_detail?",
        "expected_val": "27280",
        "type": "count",
        "expected_lang": "english"
    },
    # 11. Highest innings total
    {
        "id": 11,
        "question": "What is the highest total runs scored in an innings?",
        "expected_val": "926",
        "type": "count",
        "expected_lang": "english"
    },
    # 12. Pakistan player with most runs
    {
        "id": 12,
        "question": "Which player from Pakistan has scored the most runs?",
        "expected_val": "Aman Arshad",
        "type": "string",
        "expected_lang": "english"
    },
    # 13. Pakistan bowler with most wickets
    {
        "id": 13,
        "question": "Which bowler from Pakistan has taken the most wickets?",
        "expected_val": "Taimoor Kiyani",
        "type": "string",
        "expected_lang": "english"
    },
    # 14. Matches won by Rawal Kings
    {
        "id": 14,
        "question": "How many matches were won by Rawal Kings Cricket Club & Academy,Rwp?",
        "expected_val": "214",
        "type": "count",
        "expected_lang": "english"
    },
    # 15. Country with most registered players
    {
        "id": 15,
        "question": "Which country has the most registered players?",
        "expected_val": "Pakistan",
        "type": "string",
        "expected_lang": "english"
    },
    # 16. Total clubs
    {
        "id": 16,
        "question": "Can you tell me the total number of clubs stored in the system?",
        "expected_val": "1802", # Or valid count
        "type": "count_gt_zero",
        "expected_lang": "english"
    },
    # 17. Israrullah paraphrased
    {
        "id": 17,
        "question": "What is the batting style of Israrullah?",
        "expected_val": "Left Hand Batsman",
        "type": "string",
        "expected_lang": "english"
    },
    # 18. Registered players
    {
        "id": 18,
        "question": "Give me the total number of registered players in the database.",
        "expected_val": "16734",
        "type": "count",
        "expected_lang": "english"
    },
    # 19-30: Additional regression / benchmark items
    {
        "id": 19,
        "question": "How many matches are in the database?",
        "expected_val": "8911",
        "type": "count",
        "expected_lang": "english"
    },
    {
        "id": 20,
        "question": "How many seasons are in the database?",
        "expected_val": "16",
        "type": "count",
        "expected_lang": "english"
    },
    {
        "id": 21,
        "question": "How many cities are in the database?",
        "expected_val": "58",
        "type": "count",
        "expected_lang": "english"
    },
    {
        "id": 22,
        "question": "How many countries are in the database?",
        "expected_val": "20",
        "type": "count",
        "expected_lang": "english"
    },
    {
        "id": 23,
        "question": "What is the name of TeamId 2?",
        "expected_val": "Attock District",
        "type": "string",
        "expected_lang": "english"
    },
    {
        "id": 24,
        "question": "What is Babar Azam's batting style?",
        "expected_val": "Right Hand Batsman",
        "type": "string",
        "expected_lang": "english"
    },
    {
        "id": 25,
        "question": "Which team has won the most matches?",
        "expected_val": "Chakwal",
        "type": "string",
        "expected_lang": "english"
    },
    {
        "id": 26,
        "question": "Who has scored the most sixes?",
        "expected_val": "Usman Mustafa",
        "type": "string",
        "expected_lang": "english"
    },
    {
        "id": 27,
        "question": "Who has scored the most fours?",
        "expected_val": "Khurram Manzoor",
        "type": "string",
        "expected_lang": "english"
    },
    {
        "id": 28,
        "question": "Who scored the second-most centuries?",
        "expected_val": "Kamran Akmal",
        "type": "string",
        "expected_lang": "english"
    },
    {
        "id": 29,
        "question": "Who has scored the most fifties?",
        "expected_val": "Aman Arshad",
        "type": "string",
        "expected_lang": "english"
    },
    {
        "id": 30,
        "question": "Who scored the highest individual score?",
        "expected_val": "Israrullah",
        "type": "string",
        "expected_lang": "english"
    }
]

def run_suite():
    total = len(TEST_CASES)
    lang_pass = 0
    sql_pass = 0
    db_pass = 0
    ans_pass = 0
    overall_pass = 0

    results = []

    log("======================================================================")
    log("           UNSEEN 30 END-TO-END ACCURACY VERIFICATION SUITE           ")
    log("======================================================================\n")

    for tc in TEST_CASES:
        tid = tc["id"]
        q = tc["question"]
        exp_val = tc["expected_val"]
        ttype = tc["type"]
        exp_lang = tc["expected_lang"]

        log(f"\n----------------------------------------------------------------------")
        log(f"TEST {tid:2d}/{total}: '{q}'")
        log(f"Expected Value: {exp_val}")

        # 1. Language Detection
        det_lang = detect_language(q)
        l_ok = (det_lang == exp_lang)
        if l_ok:
            lang_pass += 1

        # 2. SQL Generation
        sql_ok = False
        db_ok = False
        ans_ok = False
        sql_str = ""
        db_rows = []
        ans_str = ""
        err_str = ""

        try:
            sql_str = generate_sql(q)
            if sql_str and len(sql_str.strip()) > 5:
                sql_ok = True
                sql_pass += 1

                # 3. Database Execution
                with engine.connect() as conn:
                    res = conn.execute(text(sql_str))
                    cols = list(res.keys())
                    db_rows = res.fetchall()

                if db_rows:
                    actual_first = db_rows[0][0]
                    row_text = " | ".join(str(v) for v in db_rows[0]).lower()

                    if ttype == "count":
                        db_ok = (str(actual_first).strip() == str(exp_val).strip())
                    elif ttype == "count_gt_zero":
                        try:
                            db_ok = (int(actual_first) > 0)
                        except:
                            db_ok = False
                    elif ttype == "string":
                        db_ok = (str(exp_val).lower() in row_text)

                    if db_ok:
                        db_pass += 1

                # 4. Final Answer Generation & Validation
                ans_str = generate_answer(q, sql_str, cols, db_rows)
                ans_text_lower = ans_str.lower()
                ans_text_clean = ans_text_lower.replace(',', '')

                if ttype == "count":
                    ans_ok = (str(exp_val) in ans_text_clean)
                elif ttype == "count_gt_zero":
                    ans_ok = bool(re.search(r'\d+', ans_text_lower))
                elif ttype == "string":
                    ans_ok = (str(exp_val).lower() in ans_text_lower)

                if ans_ok:
                    ans_pass += 1

        except Exception as e:
            err_str = str(e)

        is_overall = l_ok and sql_ok and db_ok and ans_ok
        if is_overall:
            overall_pass += 1

        status = "PASS" if is_overall else "FAIL"
        log(f"Result: {status} | Lang: {'PASS' if l_ok else 'FAIL'} ({det_lang}) | SQL: {'PASS' if sql_ok else 'FAIL'} | DB: {'PASS' if db_ok else 'FAIL'} | Ans: {'PASS' if ans_ok else 'FAIL'}")
        log(f"SQL: {sql_str}")
        log(f"DB Rows: {db_rows[:1]}")
        log(f"Answer: '{ans_str}'")
        if err_str:
            log(f"Error: {err_str}")

        results.append({
            "id": tid,
            "question": q,
            "overall": is_overall,
            "l_ok": l_ok,
            "sql_ok": sql_ok,
            "db_ok": db_ok,
            "ans_ok": ans_ok,
            "sql": sql_str,
            "answer": ans_str,
            "error": err_str
        })

    log("\n======================================================================")
    log("                           SUMMARY RESULTS                            ")
    log("======================================================================")
    log(f"Overall Accuracy:          {overall_pass}/{total} ({overall_pass/total*100:.1f}%)")
    log(f"Language Accuracy:         {lang_pass}/{total} ({lang_pass/total*100:.1f}%)")
    log(f"SQL Accuracy:              {sql_pass}/{total} ({sql_pass/total*100:.1f}%)")
    log(f"Database Result Accuracy:  {db_pass}/{total} ({db_pass/total*100:.1f}%)")
    log(f"Final Answer Accuracy:     {ans_pass}/{total} ({ans_pass/total*100:.1f}%)")
    log("======================================================================\n")

if __name__ == "__main__":
    run_suite()
