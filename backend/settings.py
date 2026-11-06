import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy.engine import URL


PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_NAME = os.getenv("DB_NAME", "clubinfo_afc")

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3")

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
SCHEMA_COLLECTION = os.getenv("SCHEMA_COLLECTION", "cricket_schema")
KNOWLEDGE_COLLECTION = os.getenv("KNOWLEDGE_COLLECTION", "cricket_knowledge")


def get_database_url() -> URL:
    if not DB_USER or not DB_PASSWORD:
        raise RuntimeError(
            "DB_USER and DB_PASSWORD are required. Set them in the project-root .env file."
        )

    return URL.create(
        "mysql+pymysql",
        username=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
    )
