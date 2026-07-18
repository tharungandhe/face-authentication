"""
SQLite persistence for user profile records (username, full name, etc).
The actual biometric vectors live in ChromaDB - this table only stores
non-biometric metadata plus the id used to link the two stores.
"""
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from utils.config import SQLITE_DB_PATH


def _init_db() -> None:
    Path(SQLITE_DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_uuid TEXT UNIQUE NOT NULL,
                username TEXT UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                face_image_path TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


@contextmanager
def get_connection():
    conn = sqlite3.connect(SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def username_exists(username: str) -> bool:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT 1 FROM users WHERE username = ?", (username,)
        ).fetchone()
        return row is not None


def create_user(user_uuid: str, username: str, full_name: str, face_image_path: str) -> int:
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO users (user_uuid, username, full_name, face_image_path, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_uuid, username, full_name, face_image_path, datetime.utcnow().isoformat()),
        )
        conn.commit()
        return cursor.lastrowid


def get_user_by_uuid(user_uuid: str) -> Optional[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM users WHERE user_uuid = ?", (user_uuid,)
        ).fetchone()


def list_users() -> List[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute("SELECT * FROM users ORDER BY created_at DESC").fetchall()


def delete_user(user_uuid: str) -> bool:
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM users WHERE user_uuid = ?", (user_uuid,))
        conn.commit()
        return cursor.rowcount > 0


_init_db()
