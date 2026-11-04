import py_compile
import sys

files = [
    '/home/inara/aiproject/backend/sql_generator.py',
    '/home/inara/aiproject/backend/answer_generator.py',
    '/home/inara/aiproject/backend/answer_prompt.py',
    '/home/inara/aiproject/backend/prompts/answer_prompt.py',
    '/home/inara/aiproject/backend/graph_chatbot.py',
]

for f in files:
    try:
        py_compile.compile(f, doraise=True)
        print(f"PASS: {f}")
    except Exception as e:
        print(f"FAIL: {f} -> {e}")
        sys.exit(1)
print("ALL COMPILED SUCCESSFULLY!")
