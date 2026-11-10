import traceback
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import text

# Import functions from existing backend modules
from sql_generator import generate_sql
from answer_generator import (
    detect_language,
    generate_answer,
    generate_knowledge_answer,
    resolve_followup_question,
)
import conversation_store
from database.db import engine
from question_router import is_current_match_question, is_general_knowledge_question
from rag.knowledge.knowledge_retriever import retrieve_knowledge
from settings import CHAT_CONTEXT_MAX_CHARS

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
    conversation_id: Optional[UUID] = None


class ConversationSummary(BaseModel):
    id: str
    title: str
    updated_at: str


class ConversationMessage(BaseModel):
    role: str
    content: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: str


class ConversationResponse(BaseModel):
    id: str
    messages: List[ConversationMessage]


class ChatResponse(BaseModel):
    question: str
    resolved_question: str
    conversation_id: str
    language: str
    answer: str
    sql: str
    columns: List[str]
    rows: List[List[Any]]
    route: str = "database"
    sources: List[str] = Field(default_factory=list)


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


def build_context(messages: List[Dict[str, str]]) -> str:
    return "\n".join(
        f"{message['role'].capitalize()}: {message['content']}"
        for message in messages
    )


def get_conversation_id(conversation_id: Optional[UUID]) -> str:
    if conversation_id is None:
        return conversation_store.create_conversation()
    normalized_id = str(conversation_id)
    if not conversation_store.conversation_exists(normalized_id):
        raise HTTPException(status_code=404, detail="Conversation not found.")
    return normalized_id


@app.post("/api/conversations", response_model=ConversationResponse)
def create_conversation_endpoint():
    conversation_id = conversation_store.create_conversation()
    return ConversationResponse(id=conversation_id, messages=[])


@app.get("/api/conversations", response_model=List[ConversationSummary])
def list_conversations_endpoint():
    return conversation_store.list_conversations()


@app.get(
    "/api/conversations/{conversation_id}",
    response_model=ConversationResponse,
)
def get_conversation_endpoint(conversation_id: UUID):
    normalized_id = str(conversation_id)
    if not conversation_store.conversation_exists(normalized_id):
        raise HTTPException(status_code=404, detail="Conversation not found.")
    return ConversationResponse(
        id=normalized_id,
        messages=conversation_store.get_messages(normalized_id),
    )


@app.delete("/api/conversations/{conversation_id}")
def delete_conversation_endpoint(conversation_id: UUID):
    if not conversation_store.delete_conversation(str(conversation_id)):
        raise HTTPException(status_code=404, detail="Conversation not found.")
    return {"deleted": True}


@app.post("/api/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        conversation_id = get_conversation_id(request.conversation_id)
        recent_context = conversation_store.get_recent_context(
            conversation_id, CHAT_CONTEXT_MAX_CHARS
        )
        resolved_question = resolve_followup_question(
            question, build_context(recent_context)
        )
        # 1. Detect language using existing logic
        lang = detect_language(resolved_question)

        if is_current_match_question(resolved_question):
            answer = (
                "Live match scores and results are not connected yet."
                if lang != "roman_urdu"
                else "Live match scores aur results abhi connected nahi hain."
            )
            response_data = {
                "language": lang,
                "answer": answer,
                "sql": "",
                "columns": [],
                "rows": [],
                "route": "unsupported",
                "sources": [],
            }
        elif is_general_knowledge_question(resolved_question):
            try:
                context, sources = retrieve_knowledge(resolved_question)
            except Exception as e:
                print(f"[ERROR] Knowledge retrieval failed for question '{resolved_question}': {e}")
                raise HTTPException(
                    status_code=503,
                    detail="Cricket knowledge is unavailable. Check Qdrant and the knowledge index.",
                ) from e

            response_data = {
                "language": lang,
                "answer": generate_knowledge_answer(resolved_question, context),
                "sql": "",
                "columns": [],
                "rows": [],
                "route": "knowledge",
                "sources": sources,
            }
        else:
            sql = generate_sql(resolved_question)
            if not sql:
                raise HTTPException(status_code=500, detail="Could not generate valid SQL query.")

            columns, raw_rows, serialized_rows = execute_sql(sql)
            response_data = {
                "language": lang,
                "answer": generate_answer(resolved_question, sql, columns, raw_rows),
                "sql": sql,
                "columns": columns,
                "rows": serialized_rows,
                "route": "database",
                "sources": [],
            }

        conversation_store.append_turn(
            conversation_id,
            question,
            response_data["answer"],
            {
                "language": response_data["language"],
                "route": response_data["route"],
                "sql": response_data["sql"],
                "columns": response_data["columns"],
                "rows": response_data["rows"],
                "sources": response_data["sources"],
                "resolved_question": resolved_question,
            },
        )
        return ChatResponse(
            question=question,
            resolved_question=resolved_question,
            conversation_id=conversation_id,
            **response_data,
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
