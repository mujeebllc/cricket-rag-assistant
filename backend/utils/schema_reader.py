import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import db

def get_schema():

    tables = db.get_usable_table_names()

    schema = ""

    for table in tables:
        schema += f"\nTable: {table}\n"
        schema += db.get_table_info([table])
        schema += "\n" + "=" * 70 + "\n"

    return schema


if __name__ == "__main__":

    print(get_schema())
