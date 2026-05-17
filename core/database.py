import sqlite3
import os
from pathlib import Path
from typing import Optional
from contextlib import contextmanager


class Database:
    """SQLite database manager for NEXUS."""

    _instance = None
    _db_path: str = ""

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._db_path:
            from core.config import Config

            config = Config()
            db_path = config.get("database.path", "data/nexus.db")
            self._db_path = str(Path(__file__).parent.parent / db_path)
            os.makedirs(os.path.dirname(self._db_path), exist_ok=True)
            self._initialize()

    def _initialize(self):
        with self._get_connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    agent TEXT DEFAULT 'manager'
                );

                CREATE TABLE IF NOT EXISTS memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT NOT NULL UNIQUE,
                    value TEXT NOT NULL,
                    category TEXT DEFAULT 'general',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT NOT NULL UNIQUE,
                    status TEXT DEFAULT 'pending',
                    agent TEXT NOT NULL,
                    command TEXT NOT NULL,
                    result TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    completed_at DATETIME
                );

                CREATE TABLE IF NOT EXISTS preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT NOT NULL UNIQUE,
                    value TEXT NOT NULL,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS workflows (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    steps TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
            """)

    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        with self._get_connection() as conn:
            return conn.execute(query, params)

    def fetchone(self, query: str, params: tuple = ()) -> Optional[sqlite3.Row]:
        with self._get_connection() as conn:
            return conn.execute(query, params).fetchone()

    def fetchall(self, query: str, params: tuple = ()) -> list:
        with self._get_connection() as conn:
            return conn.execute(query, params).fetchall()

    def executemany(self, query: str, params_list: list):
        with self._get_connection() as conn:
            conn.executemany(query, params_list)

    @property
    def db_path(self) -> str:
        return self._db_path
