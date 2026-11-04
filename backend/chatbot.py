from answer_generator import generate_answer
from sqlalchemy import text
from sql_generator import generate_sql
from database.db import engine


def execute_sql(sql):
    """
    Executes SQL query and returns columns + rows.
    """
    try:
        with engine.connect() as conn:
            result = conn.execute(text(sql))
            columns = result.keys()
            rows = result.fetchall()
            return columns, rows
    except Exception as e:
        return f"SQL Error:\n{e}"


if __name__ == "__main__":
    while True:
        question = input("\nAsk Question (exit): ")

        if question.lower() == "exit":
            break

        # -------------------------
        # Generate SQL
        # -------------------------
        sql = generate_sql(question)

        print("\nGenerated SQL:\n")
        print(sql)

        # -------------------------
        # Execute SQL
        # -------------------------
        result = execute_sql(sql)

        if isinstance(result, str):
            print(result)
            continue

        columns, rows = result

        # -------------------------
        # Display Table
        # -------------------------
        print("\nResult:\n")

        print(" | ".join(columns))
        print("-" * 150)

        for row in rows:
            print(" | ".join(str(value) for value in row))

        if len(rows) == 0:
            print("No records found.")
            continue

        # -------------------------
        # Generate Natural Language Answer
        # -------------------------
        answer = generate_answer(question, sql, columns, rows)

        print("\nAssistant:\n")
        print(answer)
