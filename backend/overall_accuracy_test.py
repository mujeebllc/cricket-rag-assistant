from sqlalchemy import text
from database.db import engine
from sql_generator import generate_sql


TEST_CASES = [
    # 1-7: Database counts
    {
        "question": "How many matches are in the database?",
        "expected": 8911,
        "type": "count",
    },
    {
        "question": "How many seasons are in the database?",
        "expected": 16,
        "type": "count",
    },
    {
        "question": "How many cities are in the database?",
        "expected": 58,
        "type": "count",
    },
    {
        "question": "How many countries are in the database?",
        "expected": 20,
        "type": "count",
    },
    {
        "question": "How many tournaments are currently live?",
        "expected": 1,
        "type": "count",
    },
    {
        "question": "How many teams are currently valid?",
        "expected": 38,
        "type": "count",
    },
    {
        "question": "How many players are currently registered?",
        "expected": 16734,
        "type": "count",
    },

    # 8-12: Player / Team information
    {
        "question": "What is the name of TeamId 2?",
        "expected": "Attock District",
        "type": "name",
    },
    {
        "question": "What is Babar Azam's batting style?",
        "expected": "Right Hand Batsman",
        "type": "name",
    },
    {
        "question": "What is Babar Azam's bowling style?",
        "expected": "Right Arm Offbreak",
        "type": "name",
    },
    {
        "question": "What is Babar Azam's playing role?",
        "expected": "Allrounder",
        "type": "name",
    },
    {
        "question": "Which country does Babar Azam belong to?",
        "expected": "Pakistan",
        "type": "name",
    },

    # 13-19: Team / Batting rankings
    {
        "question": "Which team has won the most matches?",
        "expected": "Chakwal",
        "type": "name",
    },
    {
        "question": "How many matches has Chakwal won?",
        "expected": 489,
        "type": "count",
    },
    {
        "question": "Which team has the second most wins?",
        "expected": "Peshawar",
        "type": "name",
    },
    {
        "question": "Who has scored the most sixes?",
        "expected": "Usman Mustafa",
        "type": "name",
    },
    {
        "question": "How many sixes has Usman Mustafa scored?",
        "expected": 369,
        "type": "count",
    },
    {
        "question": "Who has scored the most fours?",
        "expected": "Khurram Manzoor",
        "type": "name",
    },
    {
        "question": "How many fours has Khurram Manzoor scored?",
        "expected": 1267,
        "type": "count",
    },

    # 20-30: NEW century / fifty tests
    {
        "question": "Who scored the second-most centuries?",
        "expected": "Kamran Akmal",
        "type": "name",
    },
    {
        "question": "How many centuries did Kamran Akmal score?",
        "expected": 27,
        "type": "count",
    },
    {
        "question": "What is the highest number of centuries scored by one player?",
        "expected": 28,
        "type": "count",
    },
    {
        "question": "How many players have scored at least two centuries?",
        "expected": 378,
        "type": "count",
    },
    {
        "question": "How many players have scored at least five centuries?",
        "expected": 125,
        "type": "count",
    },
    {
        "question": "How many double centuries were scored in total?",
        "expected": 100,
        "type": "count",
    },
    {
        "question": "Who has scored the most fifties?",
        "expected": "Aman Arshad",
        "type": "name",
    },
    {
        "question": "How many fifties has Aman Arshad scored?",
        "expected": 116,
        "type": "count",
    },
    {
        "question": "Who scored the second-most fifties?",
        "expected": "Kamran Razzaq",
        "type": "name",
    },
    {
        "question": "How many fifties did Kamran Razzaq score?",
        "expected": 111,
        "type": "count",
    },
    {
        "question": "Who has the highest individual score?",
        "expected": "Israrullah",
        "type": "name",
    },
]


def run_query(sql):
    with engine.connect() as conn:
        result = conn.execute(text(sql))
        return result.fetchall()


def check_result(rows, expected, result_type):
    if not rows:
        return False, "No rows returned"

    if result_type == "count":
        actual = rows[0][0]

        try:
            passed = int(actual) == int(expected)
        except Exception:
            passed = False

        return passed, f"Expected {expected}, got {actual}"

    if result_type == "name":
        row_text = " | ".join(
            str(value) for value in rows[0]
        ).lower()

        passed = str(expected).lower() in row_text

        return passed, (
            f"Expected '{expected}', got row: {rows[0]}"
        )

    return False, "Unknown test type"


def main():
    total = len(TEST_CASES)
    passed_count = 0

    print("\n")
    print("=" * 75)
    print("             OVERALL NL2SQL ACCURACY TEST")
    print("=" * 75)
    print(f"Total NEW test cases: {total}")
    print("Previous 11 accuracy questions are NOT included.")
    print("=" * 75)

    for number, case in enumerate(TEST_CASES, start=1):

        question = case["question"]
        expected = case["expected"]
        result_type = case["type"]

        print("\n" + "-" * 75)
        print(f"TEST {number}/{total}")
        print(f"Question: {question}")
        print(f"Expected: {expected}")
        print("-" * 75)

        try:
            sql = generate_sql(question)
            rows = run_query(sql)

            passed, detail = check_result(
                rows,
                expected,
                result_type
            )

        except Exception as e:
            passed = False
            sql = "ERROR"
            detail = str(e)

        status = "PASS" if passed else "FAIL"

        if passed:
            passed_count += 1

        print(f"RESULT: {status}")
        print(f"DETAIL: {detail}")
        print(f"SQL: {sql}")

    accuracy = (
        passed_count / total * 100
        if total > 0
        else 0
    )

    print("\n")
    print("=" * 75)
    print("                       FINAL RESULT")
    print("=" * 75)
    print(
        f"OVERALL NEW TEST ACCURACY: "
        f"{passed_count}/{total} ({accuracy:.1f}%)"
    )
    print("=" * 75)


if __name__ == "__main__":
    main()
