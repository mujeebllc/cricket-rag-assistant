import json
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from settings import CHAT_HISTORY_DB_PATH


DB_PATH = CHAT_HISTORY_DB_PATH


def _connect() -> sqlite3.Connection:
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id TEXT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
            role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
            content TEXT NOT NULL,
            metadata TEXT,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_messages_conversation
            ON messages(conversation_id, id);
        """
    )
    return connection


@contextmanager
def _connection():
    connection = _connect()
    try:
        with connection:
            yield connection
    finally:
        connection.close()


def _validate_id(conversation_id: str) -> str:
    try:
        return str(uuid.UUID(conversation_id))
    except (ValueError, AttributeError, TypeError) as exc:
        raise ValueError("Conversation ID must be a valid UUID.") from exc


def create_conversation() -> str:
    conversation_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    with _connection() as connection:
        connection.execute(
            "INSERT INTO conversations (id, created_at, updated_at) VALUES (?, ?, ?)",
            (conversation_id, now, now),
        )
    return conversation_id


def conversation_exists(conversation_id: str) -> bool:
    conversation_id = _validate_id(conversation_id)
    with _connection() as connection:
        return connection.execute(
            "SELECT 1 FROM conversations WHERE id = ?", (conversation_id,)
        ).fetchone() is not None


def list_conversations(limit: int = 100) -> List[Dict[str, str]]:
    with _connection() as connection:
        rows = connection.execute(
            """
            SELECT c.id, c.updated_at,
                   (SELECT content FROM messages
                    WHERE conversation_id = c.id AND role = 'user'
                    ORDER BY id LIMIT 1) AS title
            FROM conversations AS c
            ORDER BY c.updated_at DESC, c.id
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [
        {
            "id": row["id"],
            "title": row["title"] or "New conversation",
            "updated_at": row["updated_at"],
        }
        for row in rows
    ]


def get_messages(conversation_id: str) -> List[Dict[str, Any]]:
    conversation_id = _validate_id(conversation_id)
    with _connection() as connection:
        rows = connection.execute(
            """
            SELECT role, content, metadata, created_at
            FROM messages
            WHERE conversation_id = ?
            ORDER BY id
            """,
            (conversation_id,),
        ).fetchall()
    return [
        {
            "role": row["role"],
            "content": row["content"],
            "metadata": json.loads(row["metadata"]) if row["metadata"] else None,
            "created_at": row["created_at"],
        }
        for row in rows
    ]


def get_recent_context(conversation_id: str, max_chars: int) -> List[Dict[str, str]]:
    conversation_id = _validate_id(conversation_id)
    context: List[Dict[str, str]] = []
    remaining = max_chars
    with _connection() as connection:
        rows = connection.execute(
            """
            SELECT role, content
            FROM messages
            WHERE conversation_id = ?
            ORDER BY id DESC
            """,
            (conversation_id,),
        )
        for row in rows:
            if remaining <= 0:
                break
            content = row["content"]
            if len(content) > remaining:
                if not context and row["role"] == "assistant" and max_chars > 1:
                    prior_user = next(rows, None)
                    if prior_user is not None and prior_user["role"] == "user":
                        user_content = prior_user["content"]
                        user_budget = min(len(user_content), max_chars)
                        if len(user_content) > max_chars:
                            user_budget = max_chars // 2
                        assistant_budget = max_chars - user_budget
                        if assistant_budget:
                            context.append(
                                {
                                    "role": "assistant",
                                    "content": content[:assistant_budget],
                                }
                            )
                        context.append(
                            {
                                "role": "user",
                                "content": user_content[:user_budget],
                            }
                        )
                        remaining = max_chars - assistant_budget - user_budget
                        continue
                    assistant_budget = max_chars // 2
                    context.append(
                        {"role": row["role"], "content": content[:assistant_budget]}
                    )
                    remaining -= assistant_budget
                    continue
                if context:
                    if row["role"] == "user":
                        context.append(
                            {"role": row["role"], "content": content[:remaining]}
                        )
                    break
                context.append({"role": row["role"], "content": content[:remaining]})
                break
            context.append({"role": row["role"], "content": content})
            remaining -= len(content)
    return list(reversed(context))


def append_turn(
    conversation_id: str,
    question: str,
    answer: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    conversation_id = _validate_id(conversation_id)
    now = datetime.now(timezone.utc).isoformat()
    with _connection() as connection:
        exists = connection.execute(
            "SELECT 1 FROM conversations WHERE id = ?", (conversation_id,)
        ).fetchone()
        if exists is None:
            raise KeyError("Conversation not found.")
        connection.executemany(
            """
            INSERT INTO messages (conversation_id, role, content, metadata, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            [
                (conversation_id, "user", question, None, now),
                (
                    conversation_id,
                    "assistant",
                    answer,
                    json.dumps(metadata, ensure_ascii=False) if metadata else None,
                    now,
                ),
            ],
        )
        connection.execute(
            "UPDATE conversations SET updated_at = ? WHERE id = ?",
            (now, conversation_id),
        )


def delete_conversation(conversation_id: str) -> bool:
    conversation_id = _validate_id(conversation_id)
    with _connection() as connection:
        cursor = connection.execute(
            "DELETE FROM conversations WHERE id = ?", (conversation_id,)
        )
        return cursor.rowcount > 0
