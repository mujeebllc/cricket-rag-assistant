from sqlalchemy import create_engine
from langchain_community.utilities import SQLDatabase

from settings import get_database_url

# Create Engine
engine = create_engine(get_database_url())

# Create SQLDatabase object
db = SQLDatabase(engine)
