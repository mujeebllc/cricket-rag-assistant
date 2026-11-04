import traceback
from typing import Any, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import text

# Import functions from existing backend modules
from sql_generator import generate_sql
from answer_generator import generate_answer, detect_language
from database.db import engine

app = FastAPI(
    title="AI-Powered Multilingual Cricket Assistant API",
    description="Backend API wrapper for cricket database Text-to-SQL chatbot",
    version="1.0.0",
)

# Configure CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows localhost and web frontend origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, description="User question about cricket")


class ChatResponse(BaseModel):
    question: str
    language: str
    answer: str
    sql: str
    columns: List[str]
    rows: List[List[Any]]


def serialize_cell(val: Any) -> Any:
    """Converts non-serializable objects (like Decimal, date, datetime) to standard Python types."""
    if val is None or isinstance(val, (int, float, str, bool)):
        return val
    return str(val)


def execute_sql(sql: str):
    """
    Executes SQL query against MariaDB engine and returns columns, raw rows, and JSON-serializable rows.
    """
    with engine.connect() as conn:
        result = conn.execute(text(sql))
        columns = list(result.keys())
        raw_rows = result.fetchall()

        serialized_rows = [
            [serialize_cell(cell) for cell in row]
            for row in raw_rows
        ]
        return columns, raw_rows, serialized_rows


@app.get("/")
def health_check():
    return {
        "status": "ok",
        "service": "AI-Powered Multilingual Cricket Assistant"
    }


@app.post("/api/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        # 1. Detect language using existing logic
        lang = detect_language(question)

        # 2. Generate SQL using existing logic
        sql = generate_sql(question)
        if not sql:
            raise HTTPException(status_code=500, detail="Could not generate valid SQL query.")

        # 3. Execute SQL against MariaDB database
        columns, raw_rows, serialized_rows = execute_sql(sql)

        # 4. Generate final natural-language answer using existing logic
        answer = generate_answer(question, sql, columns, raw_rows)

        return ChatResponse(
            question=question,
            language=lang,
            answer=answer,
            sql=sql,
            columns=columns,
            rows=serialized_rows
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Chat API exception for question '{question}': {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred while processing your query."
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
