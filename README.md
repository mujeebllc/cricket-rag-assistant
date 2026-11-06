# Cricket RAG Assistant

This project provides a FastAPI cricket question-answering API and a browser UI. The active API translates questions to read-only MariaDB queries, uses schema retrieval for complex questions, and returns both query results and a natural-language answer. It uses Ollama for text generation and Qdrant for schema retrieval.

The second, cricket-knowledge RAG implementation is retained in `backend/rag/knowledge/` for future use. It uses its own Qdrant collection and is not removed or folded into the active API flow.

## Requirements

- Python 3.10+
- MariaDB or MySQL, with the supplied dump imported if you need the included data
- Ollama running with the model named in `OLLAMA_MODEL`
- Qdrant running at `QDRANT_URL`

Install the repository wherever you prefer. Application data paths are derived from the source files, and configuration is read from the repository-root `.env` file.

## Setup

Run these commands from the repository root unless noted:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and set `DB_USER` and `DB_PASSWORD` for your MariaDB/MySQL account. Update the other database fields if your installation uses a different host, port, or database name. Do not commit `.env`; it is ignored by Git.

Start Ollama and pull the selected model:

```powershell
ollama pull qwen2.5:7b
```

Start Qdrant locally with Docker:

```powershell
docker run -d --name cricket-qdrant -p 6333:6333 -p 6334:6334 -v cricket-qdrant-data:/qdrant/storage qdrant/qdrant
```

Import `database/clubinfo_afc-04-05-26.sql` into the database specified by `DB_NAME`. Use your MariaDB/MySQL client for the import; the dump path above is relative to the repository root.

### Index the schema RAG

The checked-in schema chunks are under `backend/rag/schema_chunks`. To index them, run from the `backend` directory:

```powershell
python -m rag.store_embeddings
```

If you need to regenerate the schema files first, run these from `backend`, in order:

```powershell
python -m rag.schema_extractor
python -m rag.enrich_schema
python -m rag.chunk_schema
python -m rag.store_embeddings
```

These scripts read and write beside their own source files, so they do not depend on the current working directory.

## Run the application

Start the API from the `backend` directory:

```powershell
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

The API health check is at `http://localhost:8000/`; interactive API documentation is at `http://localhost:8000/docs`.

In another terminal, serve the frontend from the repository root:

```powershell
python -m http.server 3000 --directory frontend
```

Open `http://localhost:3000`. The frontend targets port `8000` on the same host by default. For a different API address, use a query parameter such as `http://localhost:3000/?api=http%3A%2F%2Fapi-host%3A8000`.

## Change models and services

Edit the project-root `.env` file; no Python source changes are needed for supported configuration changes:

| Variable | Purpose |
|---|---|
| `OLLAMA_MODEL` | LLM model tag used by the active generator and the retained agent examples. Choose a model available on your Ollama server. |
| `OLLAMA_BASE_URL` | Ollama server URL. |
| `EMBEDDING_MODEL` | Sentence-Transformers model for schema and knowledge RAG. Re-index Qdrant collections if changing embedding models. |
| `QDRANT_URL` | Qdrant endpoint. |
| `SCHEMA_COLLECTION` | Collection used by the active schema retriever. |
| `KNOWLEDGE_COLLECTION` | Separate collection reserved for the retained cricket-knowledge RAG. |
| `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME` | MariaDB/MySQL connection settings. |

`OLLAMA_MODEL` selects an Ollama model identifier, not an arbitrary provider API. Pull the model with `ollama pull <model-tag>` before using it. Embedding model changes require regenerating and re-indexing vectors so the stored vectors match the model.

## Project layout

- `backend/main.py`: FastAPI application.
- `backend/sql_generator.py`, `backend/answer_generator.py`: active SQL generation and answer generation.
- `backend/settings.py`: loads root `.env` and centralizes service/model configuration.
- `backend/rag/retriever.py`: active schema RAG retriever.
- `backend/rag/knowledge/`: retained, separate knowledge RAG implementation.
- `backend/rag/schema_chunks/`: checked-in schema input for indexing.
- `database/`: database dump.
- `frontend/`: static browser client.
- `requirements.txt`: runtime dependencies for the API, agents, and both RAG implementations.

## Optional cleanup candidates

These are not needed to run the API, but keep them if you want their recovery, testing, or diagnostic purpose:

- `backend/prompts/system_prompt.py.save`: saved prompt copy.
- `backend/test_out.txt` and `backend/overall_test_out.txt`: captured test output.
- Standalone diagnostics and benchmarks such as `backend/inspect_db.py`, `backend/inspect_db_deep.py`, `backend/test_ollama.py`, `backend/test_prompt.py`, and `backend/accuracy_test.py`.

No files have been removed. Keep both RAG implementations—including `backend/rag/knowledge/`—if you plan to use them later; backup scripts are also left untouched.

## Tests and utilities

From `backend`, use the existing scripts as needed:

```powershell
python accuracy_test.py
python run_unseen_30_test.py
python overall_accuracy_test.py
```

These database/model-backed checks require the services above to be running and configured. The API also supports `GET /` and `POST /api/chat` with a JSON body such as `{"question":"Who scored the most runs?"}`.
