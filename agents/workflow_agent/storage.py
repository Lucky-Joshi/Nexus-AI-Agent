"""
Storage backend for the Workflow Mode Agent.
Provides SQLite for session history and JSON for mode definitions.
"""

import json
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.logger import Logger
from core.config import Config

from .models import WorkflowMode, ModeState, ModeSession, ModeStatus


class WorkflowStorage:
    """SQLite storage for workflow mode sessions and state."""

    def __init__(self, db_path: Optional[str] = None):
        self.logger = Logger().get_logger("WorkflowStorage")
        if db_path is None:
            config = Config()
            db_path = config.get("database.path", "data/nexus.db")
        self._db_path = str(Path(__file__).parent.parent.parent / db_path)
        os.makedirs(os.path.dirname(self._db_path), exist_ok=True)
        self._initialize()

    def _initialize(self):
        with self._get_connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS mode_sessions (
                    id TEXT PRIMARY KEY,
                    mode_id TEXT NOT NULL,
                    mode_name TEXT NOT NULL,
                    started_at TEXT,
                    ended_at TEXT,
                    duration_seconds REAL DEFAULT 0.0,
                    status TEXT DEFAULT 'completed',
                    actions_completed INTEGER DEFAULT 0,
                    actions_failed INTEGER DEFAULT 0,
                    error TEXT DEFAULT ''
                );

                CREATE TABLE IF NOT EXISTS mode_state (
                    mode_id TEXT PRIMARY KEY,
                    mode_name TEXT,
                    status TEXT DEFAULT 'idle',
                    started_at TEXT,
                    activated_at TEXT,
                    progress REAL DEFAULT 0.0,
                    total_actions INTEGER DEFAULT 0,
                    completed_actions INTEGER DEFAULT 0,
                    failed_actions INTEGER DEFAULT 0,
                    skipped_actions INTEGER DEFAULT 0,
                    launched_apps TEXT DEFAULT '[]',
                    activated_agents TEXT DEFAULT '[]',
                    previous_notification_state TEXT DEFAULT 'normal',
                    previous_focus_state INTEGER DEFAULT 0,
                    error TEXT DEFAULT '',
                    action_states TEXT DEFAULT '[]'
                );

                CREATE TABLE IF NOT EXISTS custom_modes (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT DEFAULT '',
                    definition TEXT NOT NULL,
                    created_at TEXT,
                    updated_at TEXT,
                    enabled INTEGER DEFAULT 1
                );

                CREATE INDEX IF NOT EXISTS idx_mode_sessions_mode ON mode_sessions(mode_id);
                CREATE INDEX IF NOT EXISTS idx_mode_sessions_started ON mode_sessions(started_at);
            """)
        self.logger.info("Workflow storage initialized")

    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def save_session(self, session: ModeSession) -> bool:
        with self._get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO mode_sessions
                (id, mode_id, mode_name, started_at, ended_at, duration_seconds,
                 status, actions_completed, actions_failed, error)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session.id, session.mode_id, session.mode_name,
                session.started_at, session.ended_at, session.duration_seconds,
                session.status, session.actions_completed, session.actions_failed,
                session.error,
            ))
        return True

    def get_session(self, session_id: str) -> Optional[ModeSession]:
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM mode_sessions WHERE id = ?", (session_id,)
            ).fetchone()
        if not row:
            return None
        return self._row_to_session(row)

    def get_recent_sessions(self, limit: int = 20) -> List[ModeSession]:
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM mode_sessions ORDER BY started_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [self._row_to_session(r) for r in rows]

    def get_sessions_by_mode(self, mode_id: str, limit: int = 10) -> List[ModeSession]:
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM mode_sessions WHERE mode_id = ? ORDER BY started_at DESC LIMIT ?",
                (mode_id, limit),
            ).fetchall()
        return [self._row_to_session(r) for r in rows]

    def save_mode_state(self, state: ModeState) -> bool:
        with self._get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO mode_state
                (mode_id, mode_name, status, started_at, activated_at, progress,
                 total_actions, completed_actions, failed_actions, skipped_actions,
                 launched_apps, activated_agents, previous_notification_state,
                 previous_focus_state, error, action_states)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                state.mode_id, state.mode_name, state.status.value,
                state.started_at, state.activated_at, state.progress,
                state.total_actions, state.completed_actions, state.failed_actions,
                state.skipped_actions, json.dumps(state.launched_apps),
                json.dumps(state.activated_agents), state.previous_notification_state,
                int(state.previous_focus_state), state.error,
                json.dumps(state.action_states),
            ))
        return True

    def get_mode_state(self, mode_id: str) -> Optional[ModeState]:
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM mode_state WHERE mode_id = ?", (mode_id,)
            ).fetchone()
        if not row:
            return None
        return self._row_to_state(row)

    def clear_mode_state(self, mode_id: str) -> bool:
        with self._get_connection() as conn:
            conn.execute("DELETE FROM mode_state WHERE mode_id = ?", (mode_id,))
        return True

    def save_custom_mode(self, mode: WorkflowMode) -> bool:
        from datetime import datetime
        with self._get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO custom_modes
                (id, name, description, definition, created_at, updated_at, enabled)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                mode.id, mode.name, mode.description,
                json.dumps(mode.to_dict()),
                mode.created_at, datetime.now().isoformat(),
                int(mode.enabled),
            ))
        return True

    def get_custom_mode(self, name: str) -> Optional[WorkflowMode]:
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM custom_modes WHERE name = ? AND enabled = 1", (name,)
            ).fetchone()
        if not row:
            return None
        return WorkflowMode.from_dict(json.loads(row["definition"]))

    def get_all_custom_modes(self) -> List[WorkflowMode]:
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM custom_modes WHERE enabled = 1 ORDER BY name"
            ).fetchall()
        return [WorkflowMode.from_dict(json.loads(r["definition"])) for r in rows]

    def delete_custom_mode(self, name: str) -> bool:
        with self._get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM custom_modes WHERE name = ?", (name,)
            )
        return cursor.rowcount > 0

    def get_stats(self) -> Dict[str, Any]:
        from datetime import datetime, timedelta
        now = datetime.now()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        week_ago = (now - timedelta(days=7)).isoformat()

        with self._get_connection() as conn:
            total_sessions = conn.execute("SELECT COUNT(*) FROM mode_sessions").fetchone()[0]
            today_sessions = conn.execute(
                "SELECT COUNT(*) FROM mode_sessions WHERE started_at >= ?", (today,)
            ).fetchone()[0]
            week_sessions = conn.execute(
                "SELECT COUNT(*) FROM mode_sessions WHERE started_at >= ?", (week_ago,)
            ).fetchone()[0]
            total_duration = conn.execute(
                "SELECT COALESCE(SUM(duration_seconds), 0) FROM mode_sessions"
            ).fetchone()[0]
            custom_modes = conn.execute(
                "SELECT COUNT(*) FROM custom_modes WHERE enabled = 1"
            ).fetchone()[0]
            active_state = conn.execute(
                "SELECT mode_name FROM mode_state WHERE status = 'active'"
            ).fetchone()

            mode_counts = conn.execute(
                "SELECT mode_name, COUNT(*) as cnt FROM mode_sessions GROUP BY mode_name ORDER BY cnt DESC LIMIT 10"
            ).fetchall()

        return {
            "total_sessions": total_sessions,
            "today_sessions": today_sessions,
            "week_sessions": week_sessions,
            "total_duration_hours": round(total_duration / 3600, 1),
            "custom_modes": custom_modes,
            "active_mode": active_state[0] if active_state else None,
            "top_modes": {r["mode_name"]: r["cnt"] for r in mode_counts},
        }

    @staticmethod
    def _row_to_session(row) -> ModeSession:
        return ModeSession(
            id=row["id"], mode_id=row["mode_id"], mode_name=row["mode_name"],
            started_at=row["started_at"], ended_at=row["ended_at"],
            duration_seconds=row["duration_seconds"], status=row["status"],
            actions_completed=row["actions_completed"],
            actions_failed=row["actions_failed"], error=row["error"],
        )

    @staticmethod
    def _row_to_state(row) -> ModeState:
        return ModeState(
            mode_id=row["mode_id"], mode_name=row["mode_name"],
            status=ModeStatus(row["status"]),
            started_at=row["started_at"], activated_at=row["activated_at"],
            progress=row["progress"], total_actions=row["total_actions"],
            completed_actions=row["completed_actions"],
            failed_actions=row["failed_actions"],
            skipped_actions=row["skipped_actions"],
            launched_apps=json.loads(row["launched_apps"]),
            activated_agents=json.loads(row["activated_agents"]),
            previous_notification_state=row["previous_notification_state"],
            previous_focus_state=bool(row["previous_focus_state"]),
            error=row["error"],
            action_states=json.loads(row["action_states"]),
        )
