from sqlalchemy import create_engine
from langchain_community.utilities import SQLDatabase

# Database URL
DATABASE_URL = "mysql+pymysql://appuser:app123@127.0.0.1:3306/clubinfo_afc"

# Create Engine
engine = create_engine(DATABASE_URL)

# Create SQLDatabase object
db = SQLDatabase(engine)
