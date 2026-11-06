import re
from pathlib import Path


RAG_DIR = Path(__file__).resolve().parent


def enrich_individual_schemas(input_dir=None, output_dir=None):
    """
    Reads all table .txt files, guesses relationships using column names,
    and saves enriched copies to a new folder.
    """
    
    input_dir = Path(input_dir) if input_dir is not None else RAG_DIR / "schema_docs"
    output_dir = Path(output_dir) if output_dir is not None else RAG_DIR / "schema_docs_enriched"
    if not input_dir.is_absolute():
        input_dir = RAG_DIR / input_dir
    if not output_dir.is_absolute():
        output_dir = RAG_DIR / output_dir

    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created output folder: {output_dir}")

    table_files = sorted(input_dir.glob("*.txt"))
    
    if not table_files:
        print(f"❌ No .txt files found in {input_dir}/")
        return
    
    # --- Step 1: Build a list of all table names (from filenames) ---
    all_tables = [f.stem for f in table_files]
    print(f"📊 Found {len(all_tables)} tables: {', '.join(all_tables[:5])}...")
    
    # --- Step 2: Process each file ---
    for file_path in table_files:
        table_name = file_path.stem
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # --- Step 3: Extract column names from the CREATE TABLE block ---
        columns = []
        # Find everything inside the first parentheses
        match = re.search(r'\((.*)\)', content, re.DOTALL)
        if match:
            # Find all backtick-enclosed column names
            columns = re.findall(r'`(\w+)`', match.group(1))
        
        # --- Step 4: Guess relationships using heuristics ---
        relationships = []
        
        for col in columns:
            # Heuristic 1: Column ends with 'Id' (e.g., TeamId, PlayerId)
            if col.endswith('Id') and len(col) > 2:
                # Remove 'Id' to guess target table
                target_guess = col[:-2]  # e.g., 'Team' from 'TeamId'
                
                # Check if this exact table exists
                if target_guess.lower() in [t.lower() for t in all_tables]:
                    relationships.append(f"  - {table_name}.{col} → {target_guess}.{col} (guessed)")
                else:
                    # Try adding 's' (e.g., CategoryId -> Categories)
                    target_plural = target_guess + 's'
                    if target_plural.lower() in [t.lower() for t in all_tables]:
                        relationships.append(f"  - {table_name}.{col} → {target_plural}.{col} (guessed)")
            
            # Heuristic 2: Column ends with 'By' (e.g., CreatedBy, UpdatedBy)
            # Usually points to a 'Users' or 'User' table
            elif col.endswith('By') and len(col) > 2:
                user_tables = [t for t in all_tables if t.lower() in ['user', 'users', 'usr']]
                if user_tables:
                    relationships.append(f"  - {table_name}.{col} → {user_tables[0]}.UserId (guessed)")
            
            # Heuristic 3: Column name exactly matches a table name (singular)
            # Example: column 'Category' matches table 'category'
            elif col.lower() in [t.lower() for t in all_tables]:
                target_table = [t for t in all_tables if t.lower() == col.lower()][0]
                relationships.append(f"  - {table_name}.{col} → {target_table}.{col}Id (guessed)")
        
        # --- Step 5: Inject the comment at the top of the file ---
        if relationships:
            comment = f"/* LOGICAL RELATIONSHIPS (Auto-guessed):\n" + "\n".join(relationships) + "\n*/\n\n"
            new_content = comment + content
            print(f"✅ {table_name}: Added {len(relationships)} relationship(s)")
        else:
            new_content = content
            print(f"⚠️ {table_name}: No relationships guessed")
        
        # --- Step 6: Save the enriched version to the output folder ---
        out_path = output_dir / f"{table_name}.txt"
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
    
    print(f"\n🎉 Done! Enriched files saved to: {output_dir}/")

# --- Run the script ---
if __name__ == "__main__":
    enrich_individual_schemas()
