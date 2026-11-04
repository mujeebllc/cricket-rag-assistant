from sqlalchemy import create_engine, text

# Database Configuration
DB_USER = "appuser"
DB_PASSWORD = "app123"
DB_HOST = "127.0.0.1"
DB_PORT = "3306"
DB_NAME = "clubinfo_afc"

# Database Connection URL
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

try:
    # Create connection
    engine = create_engine(DATABASE_URL)

    # Connect to MariaDB
    with engine.connect() as connection:
        print("✅ Connected to MariaDB Successfully!")

        # Show all tables
        result = connection.execute(text("SHOW TABLES;"))

        print("\nTables in clubinfo_afc:\n")

        for table in result:
            print(table[0])

except Exception as e:
    print("❌ Connection Failed!")
    print(e)
