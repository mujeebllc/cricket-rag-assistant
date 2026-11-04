import os
import re
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database.db import db

OUTPUT_DIR = "rag/schema_docs"

os.makedirs(OUTPUT_DIR, exist_ok=True)

tables = db.get_usable_table_names()

print(f"Found {len(tables)} tables.\n")

for table in tables:

    print(f"Processing: {table}")

    schema = db.get_table_info([table])

    # -----------------------------
    # Keep ONLY CREATE TABLE block
    # -----------------------------
    match = re.search(
        r"CREATE TABLE.*?\((.*?)\)\s*;",
        schema,
        re.DOTALL
    )

    if not match:
        continue

    columns = re.findall(r"`(\w+)`", match.group(1))

    text = f"Table: {table}\n\n"

    text += "Columns:\n"

    for column in columns:
        text += f"- {column}\n"

    with open(f"{OUTPUT_DIR}/{table}.txt", "w", encoding="utf-8") as f:
        f.write(text)

print("\n✅ Schema extraction completed.")
