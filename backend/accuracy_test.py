from sqlalchemy import text
from database.db import engine
from sql_generator import generate_sql


# ============================================================
# ACCURACY TEST CASES
# ============================================================

TEST_CASES = [

    {
        "question": "How many teams are there?",
        "expected_value": 982,
        "type": "count",
    },

    {
        "question": "How many players are there?",
        "expected_value": 18485,
        "type": "count",
    },

    {
        "question": "How many tournaments are there?",
        "expected_value": 185,
        "type": "count",
    },

    {
        "question": "Who scored the most runs?",
        "expected_value": "Aman Arshad",
        "type": "name",
    },

    {
        "question": "Who has taken the most wickets?",
        "expected_value": "Taimoor Kiyani",
        "type": "name",
    },

    {
        "question": "How many players have scored at least one century?",
        "expected_value": 915,
        "type": "count",
    },

    {
        "question": "Who scored the highest individual score?",
        "expected_value": "Israrullah",
        "type": "name",
    },

    {
        "question": "How many centuries were scored in total?",
        "expected_value": 2336,
        "type": "count",
    },

    {
        "question": "Which player scored the most centuries?",
        "expected_value": "Khurram Manzoor",
        "type": "name",
    },

    {
        "question": "How many players scored 200 or more?",
        "expected_value": 80,
        "type": "count",
    },

    {
        "question": "How many players scored 50 or more?",
        "expected_value": 3336,
        "type": "count",
    },

]


# ============================================================
# EXECUTE SQL
# ============================================================

def run_query(sql):
    """Execute SQL against the real database and return rows."""

    with engine.connect() as conn:
        result = conn.execute(text(sql))
        columns = list(result.keys())
        rows = result.fetchall()

    return columns, rows


# ============================================================
# CHECK COUNT RESULT
# ============================================================

def check_count_result(rows, expected_value):

    if not rows:
        return False, "No rows returned"

    actual_value = rows[0][0]

    if actual_value is None:
        actual_value = 0

    passed = int(actual_value) == int(expected_value)

    return passed, f"Expected {expected_value}, got {actual_value}"


# ============================================================
# CHECK NAME RESULT
# ============================================================

def check_name_result(rows, expected_value):

    if not rows:
        return False, "No rows returned"

    # Search all columns in the first row
    row_text = " | ".join(
        str(value) for value in rows[0]
    ).lower()

    expected_lower = str(expected_value).lower()

    passed = expected_lower in row_text

    return passed, (
        f"Expected to find '{expected_value}', "
        f"got row: {rows[0]}"
    )


# ============================================================
# RUN ACCURACY TEST
# ============================================================

def run_accuracy_test():

    results = []
    passed_count = 0

    total = len(TEST_CASES)

    print("\n")
    print("=" * 70)
    print("        NL2SQL CHATBOT - ACCURACY TEST")
    print("=" * 70)
    print(f"Total test cases: {total}")
    print("=" * 70)

    for number, case in enumerate(TEST_CASES, start=1):

        question = case["question"]
        expected_value = case["expected_value"]
        case_type = case["type"]

        print("\n")
        print("-" * 70)
        print(f"TEST {number}/{total}")
        print(f"Question: {question}")
        print(f"Expected: {expected_value}")
        print("-" * 70)

        try:

            # Generate SQL
            sql = generate_sql(question)

            # Execute generated SQL
            columns, rows = run_query(sql)

            # Check answer
            if case_type == "count":

                passed, detail = check_count_result(
                    rows,
                    expected_value
                )

            elif case_type == "name":

                passed, detail = check_name_result(
                    rows,
                    expected_value
                )

            else:

                passed = False
                detail = (
                    f"Unknown test type: {case_type}"
                )

        except Exception as e:

            passed = False

            sql = "ERROR generating/running SQL"

            detail = str(e)

        status = "PASS" if passed else "FAIL"

        if passed:
            passed_count += 1

        print(f"RESULT: {status}")
        print(f"DETAIL: {detail}")
        print(f"SQL: {sql}")

        results.append({
            "question": question,
            "status": status,
            "detail": detail,
            "sql": sql,
        })


    # ========================================================
    # FINAL ACCURACY
    # ========================================================

    accuracy = (
        passed_count / total * 100
        if total > 0
        else 0
    )

    print("\n")
    print("=" * 70)
    print("                    FINAL RESULT")
    print("=" * 70)

    print(
        f"ACCURACY: {passed_count}/{total} "
        f"passed ({accuracy:.1f}%)"
    )

    print("=" * 70)


    # ========================================================
    # SAVE REPORT
    # ========================================================

    with open("accuracy_report.txt", "w") as f:

        f.write(
            "NL2SQL CHATBOT - ACCURACY REPORT\n"
        )

        f.write("=" * 70 + "\n\n")

        f.write(
            f"Overall Accuracy: "
            f"{passed_count}/{total} "
            f"({accuracy:.1f}%)\n\n"
        )

        for r in results:

            f.write(
                f"Question: {r['question']}\n"
            )

            f.write(
                f"Status:   {r['status']}\n"
            )

            f.write(
                f"Detail:   {r['detail']}\n"
            )

            f.write(
                f"SQL:      {r['sql']}\n"
            )

            f.write("-" * 70 + "\n")


    print("\nFull report saved to:")
    print("accuracy_report.txt")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    run_accuracy_test()
