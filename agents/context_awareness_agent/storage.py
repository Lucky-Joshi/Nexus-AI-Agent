"""
Context Awareness Agent Storage
SQLite persistence for context history, patterns, triggers, and session data.
"""

import sqlite3
import json
import os
from contextlib import contextmanager
from typing import List, Optional, Dict, Any
from pathlib import Path

from core.logger import Logger


class ContextStorage:
    """SQLite storage for context awareness agent data."""

    def __init__(self, db_path: Optional[str] = None):
        self.logger = Logger().get_logger("ContextStorage")
        if db_path is None:
            db_path = os.path.join(
                Path(__file__).parent.parent.parent, "data", "context.db"
            )
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
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

    def _init_db(self):
        with self._get_connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS context_snapshots (
                    id TEXT PRIMARY KEY,
                    activity TEXT NOT NULL,
                    active_window_title TEXT DEFAULT '',
                    active_process TEXT DEFAULT '',
                    app_count INTEGER DEFAULT 0,
                    focus_level TEXT DEFAULT 'idle',
                    cpu_percent REAL DEFAULT 0.0,
                    memory_percent REAL DEFAULT 0.0,
                    duration_seconds REAL DEFAULT 0.0,
                    timestamp TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS context_patterns (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    activity_type TEXT NOT NULL,
                    required_apps TEXT DEFAULT '[]',
                    time_pattern TEXT DEFAULT '',
                    min_duration_minutes REAL DEFAULT 5.0,
                    confidence REAL DEFAULT 0.0,
                    detection_count INTEGER DEFAULT 0,
                    last_detected TEXT DEFAULT '',
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS adaptive_triggers (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    condition_activity TEXT DEFAULT '',
                    condition_apps TEXT DEFAULT '[]',
                    condition_time TEXT DEFAULT '',
                    condition_focus TEXT DEFAULT '',
                    action TEXT NOT NULL,
                    action_target TEXT DEFAULT '',
                    action_params TEXT DEFAULT '{}',
                    enabled INTEGER DEFAULT 1,
                    trigger_count INTEGER DEFAULT 0,
                    last_triggered TEXT DEFAULT '',
                    cooldown_seconds INTEGER DEFAULT 300
                );

                CREATE TABLE IF NOT EXISTS context_sessions (
                    id TEXT PRIMARY KEY,
                    session_type TEXT NOT NULL,
                    activity TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    ended_at TEXT DEFAULT '',
                    duration_minutes REAL DEFAULT 0.0,
                    apps_used TEXT DEFAULT '[]',
                    window_changes INTEGER DEFAULT 0,
                    focus_level TEXT DEFAULT 'idle',
                    productivity_score REAL DEFAULT 0.0
                );

                CREATE TABLE IF NOT EXISTS context_rules (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    rule_type TEXT NOT NULL,
                    condition TEXT NOT NULL,
                    action TEXT NOT NULL,
                    enabled INTEGER DEFAULT 1,
                    created_at TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_snapshots_timestamp ON context_snapshots(timestamp);
                CREATE INDEX IF NOT EXISTS idx_snapshots_activity ON context_snapshots(activity);
                CREATE INDEX IF NOT EXISTS idx_sessions_started ON context_sessions(started_at);
                CREATE INDEX IF NOT EXISTS idx_sessions_type ON context_sessions(session_type);
                CREATE INDEX IF NOT EXISTS idx_patterns_activity ON context_patterns(activity_type);
                CREATE INDEX IF NOT EXISTS idx_triggers_enabled ON adaptive_triggers(enabled);
            """)
        self.logger.info(f"Context storage initialized: {self.db_path}")

    def save_snapshot(self, snapshot_data: Dict[str, Any]):
        with self._get_connection() as conn:
            conn.execute(
                """INSERT INTO context_snapshots
                   (id, activity, active_window_title, active_process, app_count,
                    focus_level, cpu_percent, memory_percent, duration_seconds, timestamp)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    snapshot_data["id"],
                    snapshot_data["activity"],
                    snapshot_data.get("active_window_title", "")[:100],
                    snapshot_data.get("active_process", ""),
                    snapshot_data.get("app_count", 0),
                    snapshot_data.get("focus_level", "idle"),
                    snapshot_data.get("cpu_percent", 0.0),
                    snapshot_data.get("memory_percent", 0.0),
                    snapshot_data.get("duration_seconds", 0.0),
                    snapshot_data["timestamp"],
                ),
            )

    def get_snapshots(self, limit: int = 100, activity: Optional[str] = None,
                      start_time: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            query = "SELECT * FROM context_snapshots WHERE 1=1"
            params = []
            if activity:
                query += " AND activity = ?"
                params.append(activity)
            if start_time:
                query += " AND timestamp >= ?"
                params.append(start_time)
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)

            rows = conn.execute(query, params).fetchall()
            return [dict(r) for r in rows]

    def save_pattern(self, pattern_data: Dict[str, Any]):
        with self._get_connection() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO context_patterns
                   (id, name, description, activity_type, required_apps, time_pattern,
                    min_duration_minutes, confidence, detection_count, last_detected, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    pattern_data["id"],
                    pattern_data["name"],
                    pattern_data.get("description", ""),
                    pattern_data["activity_type"],
                    json.dumps(pattern_data.get("required_apps", [])),
                    pattern_data.get("time_pattern", ""),
                    pattern_data.get("min_duration_minutes", 5.0),
                    pattern_data.get("confidence", 0.0),
                    pattern_data.get("detection_count", 0),
                    pattern_data.get("last_detected", ""),
                    pattern_data.get("created_at", ""),
                ),
            )

    def get_patterns(self, activity_type: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            if activity_type:
                rows = conn.execute(
                    "SELECT * FROM context_patterns WHERE activity_type = ? ORDER BY detection_count DESC",
                    (activity_type,),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM context_patterns ORDER BY detection_count DESC"
                ).fetchall()
            results = []
            for r in rows:
                d = dict(r)
                d["required_apps"] = json.loads(d.get("required_apps", "[]"))
                results.append(d)
            return results

    def update_pattern_detection(self, pattern_id: str):
        with self._get_connection() as conn:
            from datetime import datetime
            conn.execute(
                """UPDATE context_patterns
                   SET detection_count = detection_count + 1, last_detected = ?
                   WHERE id = ?""",
                (datetime.now().isoformat(), pattern_id),
            )

    def save_trigger(self, trigger_data: Dict[str, Any]):
        with self._get_connection() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO adaptive_triggers
                   (id, name, description, condition_activity, condition_apps, condition_time,
                    condition_focus, action, action_target, action_params, enabled,
                    trigger_count, last_triggered, cooldown_seconds)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    trigger_data["id"],
                    trigger_data["name"],
                    trigger_data.get("description", ""),
                    trigger_data.get("condition_activity", "") or "",
                    json.dumps(trigger_data.get("condition_apps", [])),
                    trigger_data.get("condition_time", ""),
                    trigger_data.get("condition_focus", "") or "",
                    trigger_data["action"],
                    trigger_data.get("action_target", ""),
                    json.dumps(trigger_data.get("action_params", {})),
                    1 if trigger_data.get("enabled", True) else 0,
                    trigger_data.get("trigger_count", 0),
                    trigger_data.get("last_triggered", ""),
                    trigger_data.get("cooldown_seconds", 300),
                ),
            )

    def get_triggers(self, enabled_only: bool = True) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            if enabled_only:
                rows = conn.execute(
                    "SELECT * FROM adaptive_triggers WHERE enabled = 1 ORDER BY name"
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM adaptive_triggers ORDER BY name"
                ).fetchall()
            results = []
            for r in rows:
                d = dict(r)
                d["condition_apps"] = json.loads(d.get("condition_apps", "[]"))
                d["action_params"] = json.loads(d.get("action_params", "{}"))
                d["enabled"] = bool(d["enabled"])
                results.append(d)
            return results

    def update_trigger_fired(self, trigger_id: str):
        with self._get_connection() as conn:
            from datetime import datetime
            conn.execute(
                """UPDATE adaptive_triggers
                   SET trigger_count = trigger_count + 1, last_triggered = ?
                   WHERE id = ?""",
                (datetime.now().isoformat(), trigger_id),
            )

    def save_session(self, session_data: Dict[str, Any]):
        with self._get_connection() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO context_sessions
                   (id, session_type, activity, started_at, ended_at, duration_minutes,
                    apps_used, window_changes, focus_level, productivity_score)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    session_data["id"],
                    session_data["session_type"],
                    session_data["activity"],
                    session_data["started_at"],
                    session_data.get("ended_at", ""),
                    session_data.get("duration_minutes", 0.0),
                    json.dumps(session_data.get("apps_used", [])),
                    session_data.get("window_changes", 0),
                    session_data.get("focus_level", "idle"),
                    session_data.get("productivity_score", 0.0),
                ),
            )

    def get_sessions(self, limit: int = 50, session_type: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            if session_type:
                rows = conn.execute(
                    "SELECT * FROM context_sessions WHERE session_type = ? ORDER BY started_at DESC LIMIT ?",
                    (session_type, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM context_sessions ORDER BY started_at DESC LIMIT ?",
                    (limit,),
                ).fetchall()
            results = []
            for r in rows:
                d = dict(r)
                d["apps_used"] = json.loads(d.get("apps_used", "[]"))
                results.append(d)
            return results

    def save_rule(self, rule_data: Dict[str, Any]):
        with self._get_connection() as conn:
            from datetime import datetime
            conn.execute(
                """INSERT OR REPLACE INTO context_rules
                   (id, name, description, rule_type, condition, action, enabled, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    rule_data["id"],
                    rule_data["name"],
                    rule_data.get("description", ""),
                    rule_data["rule_type"],
                    rule_data["condition"],
                    rule_data["action"],
                    1 if rule_data.get("enabled", True) else 0,
                    rule_data.get("created_at", datetime.now().isoformat()),
                ),
            )

    def get_rules(self, rule_type: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            if rule_type:
                rows = conn.execute(
                    "SELECT * FROM context_rules WHERE rule_type = ? AND enabled = 1 ORDER BY name",
                    (rule_type,),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM context_rules WHERE enabled = 1 ORDER BY name"
                ).fetchall()
            return [dict(r) for r in rows]

    def delete_rule(self, rule_id: str) -> bool:
        with self._get_connection() as conn:
            cursor = conn.execute("DELETE FROM context_rules WHERE id = ?", (rule_id,))
            return cursor.rowcount > 0

    def get_activity_summary(self, days: int = 7) -> Dict[str, Any]:
        with self._get_connection() as conn:
            rows = conn.execute(
                """SELECT activity, COUNT(*) as count, AVG(duration_seconds) as avg_dur,
                   SUM(duration_seconds) as total_dur
                   FROM context_snapshots
                   WHERE timestamp >= date('now', ?)
                   GROUP BY activity ORDER BY count DESC""",
                (f"-{days} days",),
            ).fetchall()

            activities = {}
            for r in rows:
                activities[r["activity"]] = {
                    "count": r["count"],
                    "avg_duration": round(r["avg_dur"] or 0, 1),
                    "total_duration": round(r["total_dur"] or 0, 1),
                }

            total_sessions = conn.execute(
                "SELECT COUNT(*) FROM context_sessions WHERE started_at >= date('now', ?)",
                (f"-{days} days",),
            ).fetchone()[0]

            avg_focus = conn.execute(
                """SELECT AVG(CASE focus_level
                   WHEN 'deep' THEN 5 WHEN 'focused' THEN 4 WHEN 'moderate' THEN 3
                   WHEN 'distracted' THEN 2 WHEN 'idle' THEN 1 ELSE 0 END)
                   FROM context_snapshots WHERE timestamp >= date('now', ?)""",
                (f"-{days} days",),
            ).fetchone()[0] or 0

            return {
                "period_days": days,
                "activities": activities,
                "total_sessions": total_sessions,
                "avg_focus_score": round(avg_focus, 1),
            }

    def cleanup_old_records(self, days: int = 30) -> int:
        with self._get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM context_snapshots WHERE timestamp < date('now', ?)",
                (f"-{days} days",),
            )
            return cursor.rowcount
