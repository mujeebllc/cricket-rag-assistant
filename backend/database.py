from sqlalchemy import create_engine, text

from settings import DB_NAME, get_database_url

try:
    # Create connection
    engine = create_engine(get_database_url())

    # Connect to MariaDB
    with engine.connect() as connection:
        print("✅ Connected to MariaDB Successfully!")

        # Show all tables
        result = connection.execute(text("SHOW TABLES;"))

        print(f"\nTables in {DB_NAME}:\n")

        for table in result:
            print(table[0])

except Exception as e:
    print("❌ Connection Failed!")
    print(e)
