import os
import shutil

INPUT_DIR = "schema_docs_enriched"
OUTPUT_DIR = "schema_chunks"

# Recreate output folder
if os.path.exists(OUTPUT_DIR):
    shutil.rmtree(OUTPUT_DIR)

os.makedirs(OUTPUT_DIR)

total_chunks = 0

for filename in os.listdir(INPUT_DIR):

    if not filename.endswith(".txt"):
        continue

    src = os.path.join(INPUT_DIR, filename)
    dst = os.path.join(OUTPUT_DIR, filename)

    with open(src, "r", encoding="utf-8") as f:
        text = f.read()

    with open(dst, "w", encoding="utf-8") as f:
        f.write(text)

    total_chunks += 1

print(f"\n✅ Created {total_chunks} schema chunks.")
print(f"📁 Saved to: {OUTPUT_DIR}")
