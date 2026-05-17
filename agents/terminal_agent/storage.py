"""
Storage backend for the Terminal Agent.
Provides SQLite persistence for command history and session state.
"""

import json
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.logger import Logger
from core.config import Config

from .models import TerminalSession, CommandRecord, SessionStatus


class TerminalStorage:
    """SQLite storage for terminal sessions and command history."""

    def __init__(self, db_path: Optional[str] = None):
        self.logger = Logger().get_logger("TerminalStorage")
        if db_path is None:
            config = Config()
            db_path = config.get("database.path", "data/nexus.db")
        self._db_path = str(Path(__file__).parent.parent.parent / db_path)
        os.makedirs(os.path.dirname(self._db_path), exist_ok=True)
        self._initialize()

    def _initialize(self):
        with self._get_connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS terminal_sessions (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    working_directory TEXT DEFAULT '',
                    status TEXT DEFAULT 'idle',
                    environment TEXT DEFAULT '{}',
                    command_history TEXT DEFAULT '[]',
                    created_at TEXT,
                    last_active TEXT,
                    max_history INTEGER DEFAULT 100
                );

                CREATE TABLE IF NOT EXISTS command_history (
                    id TEXT PRIMARY KEY,
                    session_id TEXT,
                    command TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    output TEXT DEFAULT '',
                    error TEXT DEFAULT '',
                    exit_code INTEGER DEFAULT -1,
                    started_at TEXT,
                    completed_at TEXT,
                    duration_seconds REAL DEFAULT 0.0,
                    working_directory TEXT DEFAULT '',
                    is_safe INTEGER DEFAULT 1,
                    safety_reason TEXT DEFAULT '',
                    stream_mode INTEGER DEFAULT 0,
                    FOREIGN KEY (session_id) REFERENCES terminal_sessions(id) ON DELETE SET NULL
                );

                CREATE INDEX IF NOT EXISTS idx_cmd_session ON command_history(session_id);
                CREATE INDEX IF NOT EXISTS idx_cmd_status ON command_history(status);
                CREATE INDEX IF NOT EXISTS idx_cmd_started ON command_history(started_at);
                CREATE INDEX IF NOT EXISTS idx_cmd_safe ON command_history(is_safe);
            """)
        self.logger.info("Terminal storage initialized")

    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def save_session(self, session: TerminalSession) -> bool:
        with self._get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO terminal_sessions
                (id, name, working_directory, status, environment, command_history,
                 created_at, last_active, max_history)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session.id, session.name, session.working_directory, session.status.value,
                json.dumps(session.environment), json.dumps(session.command_history),
                session.created_at, session.last_active, session.max_history,
            ))
        return True

    def get_session(self, session_id: str) -> Optional[TerminalSession]:
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM terminal_sessions WHERE id = ?", (session_id,)
            ).fetchone()
        if not row:
            return None
        return self._row_to_session(row)

    def get_all_sessions(self, limit: int = 20) -> List[TerminalSession]:
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM terminal_sessions ORDER BY last_active DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [self._row_to_session(r) for r in rows]

    def get_active_sessions(self) -> List[TerminalSession]:
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM terminal_sessions WHERE status = 'active' ORDER BY last_active DESC"
            ).fetchall()
        return [self._row_to_session(r) for r in rows]

    def delete_session(self, session_id: str) -> bool:
        with self._get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM terminal_sessions WHERE id = ?", (session_id,)
            )
        return cursor.rowcount > 0

    def save_command(self, record: CommandRecord) -> bool:
        with self._get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO command_history
                (id, session_id, command, status, output, error, exit_code,
                 started_at, completed_at, duration_seconds, working_directory,
                 is_safe, safety_reason, stream_mode)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record.id, record.session_id, record.command, record.status.value,
                record.output, record.error, record.exit_code,
                record.started_at, record.completed_at, record.duration_seconds,
                record.working_directory, int(record.is_safe), record.safety_reason,
                int(record.stream_mode),
            ))
        return True

    def get_command(self, record_id: str) -> Optional[CommandRecord]:
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM command_history WHERE id = ?", (record_id,)
            ).fetchone()
        if not row:
            return None
        return self._row_to_command(row)

    def get_session_commands(self, session_id: str, limit: int = 50) -> List[CommandRecord]:
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM command_history WHERE session_id = ? ORDER BY started_at DESC LIMIT ?",
                (session_id, limit),
            ).fetchall()
        return [self._row_to_command(r) for r in rows]

    def get_recent_commands(self, limit: int = 50) -> List[CommandRecord]:
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM command_history ORDER BY started_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [self._row_to_command(r) for r in rows]

    def search_commands(self, query: str, limit: int = 20) -> List[CommandRecord]:
        with self._get_connection() as conn:
            rows = conn.execute(
                """SELECT * FROM command_history
                   WHERE command LIKE ? OR output LIKE ?
                   ORDER BY started_at DESC LIMIT ?""",
                (f"%{query}%", f"%{query}%", limit),
            ).fetchall()
        return [self._row_to_command(r) for r in rows]

    def get_failed_commands(self, limit: int = 20) -> List[CommandRecord]:
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM command_history WHERE status = 'failed' ORDER BY started_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [self._row_to_command(r) for r in rows]

    def get_blocked_commands(self, limit: int = 20) -> List[CommandRecord]:
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM command_history WHERE is_safe = 0 ORDER BY started_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [self._row_to_command(r) for r in rows]

    def get_stats(self) -> Dict[str, Any]:
        with self._get_connection() as conn:
            total_cmds = conn.execute("SELECT COUNT(*) FROM command_history").fetchone()[0]
            completed = conn.execute("SELECT COUNT(*) FROM command_history WHERE status = 'completed'").fetchone()[0]
            failed = conn.execute("SELECT COUNT(*) FROM command_history WHERE status = 'failed'").fetchone()[0]
            blocked = conn.execute("SELECT COUNT(*) FROM command_history WHERE is_safe = 0").fetchone()[0]
            total_sessions = conn.execute("SELECT COUNT(*) FROM terminal_sessions").fetchone()[0]
            active_sessions = conn.execute("SELECT COUNT(*) FROM terminal_sessions WHERE status = 'active'").fetchone()[0]
            avg_duration = conn.execute(
                "SELECT AVG(duration_seconds) FROM command_history WHERE status = 'completed'"
            ).fetchone()[0] or 0.0

        return {
            "total_commands": total_cmds,
            "completed_commands": completed,
            "failed_commands": failed,
            "blocked_commands": blocked,
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "average_duration_seconds": round(avg_duration, 2),
        }

    def clear_history(self, older_than_days: int = 0) -> int:
        if older_than_days > 0:
            from datetime import datetime, timedelta
            cutoff = (datetime.now() - timedelta(days=older_than_days)).isoformat()
            with self._get_connection() as conn:
                cursor = conn.execute(
                    "DELETE FROM command_history WHERE started_at < ?", (cutoff,)
                )
            return cursor.rowcount
        else:
            with self._get_connection() as conn:
                cursor = conn.execute("DELETE FROM command_history")
            return cursor.rowcount

    def _row_to_session(self, row) -> TerminalSession:
        return TerminalSession(
            id=row["id"], name=row["name"],
            working_directory=row["working_directory"],
            status=SessionStatus(row["status"]),
            environment=json.loads(row["environment"]),
            command_history=json.loads(row["command_history"]),
            created_at=row["created_at"], last_active=row["last_active"],
            max_history=row["max_history"],
        )

    @staticmethod
    def _row_to_command(row) -> CommandRecord:
        from .models import CommandStatus
        return CommandRecord(
            id=row["id"], command=row["command"],
            session_id=row["session_id"],
            status=CommandStatus(row["status"]),
            output=row["output"], error=row["error"],
            exit_code=row["exit_code"],
            started_at=row["started_at"], completed_at=row["completed_at"],
            duration_seconds=row["duration_seconds"],
            working_directory=row["working_directory"],
            is_safe=bool(row["is_safe"]),
            safety_reason=row["safety_reason"],
            stream_mode=bool(row["stream_mode"]),
        )
