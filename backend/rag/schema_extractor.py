import re
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from database.db import db

OUTPUT_DIR = Path(__file__).resolve().parent / "schema_docs"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

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

    with open(OUTPUT_DIR / f"{table}.txt", "w", encoding="utf-8") as f:
        f.write(text)

print("\n✅ Schema extraction completed.")
