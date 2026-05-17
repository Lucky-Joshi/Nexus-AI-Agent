"""
Learning Agent Storage
SQLite persistence for behavior records, learned patterns, habits, recommendations, and predictions.
"""

import sqlite3
import json
import os
from contextlib import contextmanager
from typing import List, Optional, Dict, Any
from pathlib import Path

from core.logger import Logger


class LearningStorage:
    """SQLite storage for learning agent data."""

    def __init__(self, db_path: Optional[str] = None):
        self.logger = Logger().get_logger("LearningStorage")
        if db_path is None:
            db_path = os.path.join(
                Path(__file__).parent.parent.parent, "data", "learning.db"
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
                CREATE TABLE IF NOT EXISTS behavior_records (
                    id TEXT PRIMARY KEY,
                    action TEXT NOT NULL,
                    agent TEXT DEFAULT '',
                    context TEXT DEFAULT '',
                    timestamp TEXT NOT NULL,
                    hour INTEGER DEFAULT 0,
                    day_of_week INTEGER DEFAULT 0,
                    is_weekday INTEGER DEFAULT 1,
                    preceding_actions TEXT DEFAULT '[]',
                    duration_seconds REAL DEFAULT 0.0,
                    success INTEGER DEFAULT 1
                );

                CREATE TABLE IF NOT EXISTS learned_patterns (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    pattern_type TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    actions TEXT DEFAULT '[]',
                    frequency INTEGER DEFAULT 0,
                    confidence TEXT DEFAULT 'low',
                    confidence_score REAL DEFAULT 0.0,
                    typical_time TEXT DEFAULT '',
                    typical_day TEXT DEFAULT '',
                    context_triggers TEXT DEFAULT '[]',
                    average_duration REAL DEFAULT 0.0,
                    success_rate REAL DEFAULT 0.0,
                    first_seen TEXT NOT NULL,
                    last_seen TEXT NOT NULL,
                    status TEXT DEFAULT 'observing',
                    automation_suggestion TEXT DEFAULT ''
                );

                CREATE TABLE IF NOT EXISTS recommendations (
                    id TEXT PRIMARY KEY,
                    rec_type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    confidence REAL DEFAULT 0.0,
                    pattern_id TEXT DEFAULT '',
                    suggested_action TEXT DEFAULT '',
                    suggested_params TEXT DEFAULT '{}',
                    reason TEXT DEFAULT '',
                    dismissed INTEGER DEFAULT 0,
                    accepted INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS user_habits (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    actions TEXT DEFAULT '[]',
                    typical_time TEXT DEFAULT '',
                    typical_days TEXT DEFAULT '[]',
                    frequency_per_week REAL DEFAULT 0.0,
                    consistency REAL DEFAULT 0.0,
                    duration_minutes REAL DEFAULT 0.0,
                    context TEXT DEFAULT '',
                    automation_potential REAL DEFAULT 0.0,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS prediction_log (
                    id TEXT PRIMARY KEY,
                    predicted_action TEXT NOT NULL,
                    predicted_agent TEXT DEFAULT '',
                    confidence REAL DEFAULT 0.0,
                    actual_action TEXT DEFAULT '',
                    was_correct INTEGER DEFAULT 0,
                    timestamp TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_behaviors_timestamp ON behavior_records(timestamp);
                CREATE INDEX IF NOT EXISTS idx_behaviors_action ON behavior_records(action);
                CREATE INDEX IF NOT EXISTS idx_behaviors_hour ON behavior_records(hour);
                CREATE INDEX IF NOT EXISTS idx_behaviors_day ON behavior_records(day_of_week);
                CREATE INDEX IF NOT EXISTS idx_patterns_type ON learned_patterns(pattern_type);
                CREATE INDEX IF NOT EXISTS idx_patterns_status ON learned_patterns(status);
                CREATE INDEX IF NOT EXISTS idx_patterns_confidence ON learned_patterns(confidence_score);
                CREATE INDEX IF NOT EXISTS idx_recommendations_type ON recommendations(rec_type);
                CREATE INDEX IF NOT EXISTS idx_recommendations_accepted ON recommendations(accepted);
                CREATE INDEX IF NOT EXISTS idx_habits_name ON user_habits(name);
                CREATE INDEX IF NOT EXISTS idx_predictions_timestamp ON prediction_log(timestamp);
            """)
        self.logger.info(f"Learning storage initialized: {self.db_path}")

    def save_behavior(self, record_data: Dict[str, Any]):
        with self._get_connection() as conn:
            conn.execute(
                """INSERT INTO behavior_records
                   (id, action, agent, context, timestamp, hour, day_of_week,
                    is_weekday, preceding_actions, duration_seconds, success)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    record_data["id"],
                    record_data["action"],
                    record_data.get("agent", ""),
                    record_data.get("context", ""),
                    record_data["timestamp"],
                    record_data.get("hour", 0),
                    record_data.get("day_of_week", 0),
                    1 if record_data.get("is_weekday", True) else 0,
                    json.dumps(record_data.get("preceding_actions", [])),
                    record_data.get("duration_seconds", 0.0),
                    1 if record_data.get("success", True) else 0,
                ),
            )

    def get_behaviors(self, limit: int = 100, action: Optional[str] = None,
                      hour: Optional[int] = None, day: Optional[int] = None,
                      start_time: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            query = "SELECT * FROM behavior_records WHERE 1=1"
            params = []
            if action:
                query += " AND action = ?"
                params.append(action)
            if hour is not None:
                query += " AND hour = ?"
                params.append(hour)
            if day is not None:
                query += " AND day_of_week = ?"
                params.append(day)
            if start_time:
                query += " AND timestamp >= ?"
                params.append(start_time)
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)

            rows = conn.execute(query, params).fetchall()
            results = []
            for r in rows:
                d = dict(r)
                d["preceding_actions"] = json.loads(d.get("preceding_actions", "[]"))
                d["is_weekday"] = bool(d.get("is_weekday", 1))
                d["success"] = bool(d.get("success", 1))
                results.append(d)
            return results

    def save_pattern(self, pattern_data: Dict[str, Any]):
        with self._get_connection() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO learned_patterns
                   (id, name, pattern_type, description, actions, frequency,
                    confidence, confidence_score, typical_time, typical_day,
                    context_triggers, average_duration, success_rate,
                    first_seen, last_seen, status, automation_suggestion)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    pattern_data["id"],
                    pattern_data["name"],
                    pattern_data["pattern_type"],
                    pattern_data.get("description", ""),
                    json.dumps(pattern_data.get("actions", [])),
                    pattern_data.get("frequency", 0),
                    pattern_data.get("confidence", "low"),
                    pattern_data.get("confidence_score", 0.0),
                    pattern_data.get("typical_time", ""),
                    pattern_data.get("typical_day", ""),
                    json.dumps(pattern_data.get("context_triggers", [])),
                    pattern_data.get("average_duration", 0.0),
                    pattern_data.get("success_rate", 0.0),
                    pattern_data.get("first_seen", ""),
                    pattern_data.get("last_seen", ""),
                    pattern_data.get("status", "observing"),
                    pattern_data.get("automation_suggestion", ""),
                ),
            )

    def get_patterns(self, pattern_type: Optional[str] = None,
                     status: Optional[str] = None,
                     min_confidence: float = 0.0) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            query = "SELECT * FROM learned_patterns WHERE confidence_score >= ?"
            params = [min_confidence]
            if pattern_type:
                query += " AND pattern_type = ?"
                params.append(pattern_type)
            if status:
                query += " AND status = ?"
                params.append(status)
            query += " ORDER BY confidence_score DESC, frequency DESC"

            rows = conn.execute(query, params).fetchall()
            results = []
            for r in rows:
                d = dict(r)
                d["actions"] = json.loads(d.get("actions", "[]"))
                d["context_triggers"] = json.loads(d.get("context_triggers", "[]"))
                results.append(d)
            return results

    def get_pattern(self, pattern_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM learned_patterns WHERE id = ?", (pattern_id,)
            ).fetchone()
            if row:
                d = dict(row)
                d["actions"] = json.loads(d.get("actions", "[]"))
                d["context_triggers"] = json.loads(d.get("context_triggers", "[]"))
                return d
            return None

    def save_recommendation(self, rec_data: Dict[str, Any]):
        with self._get_connection() as conn:
            conn.execute(
                """INSERT INTO recommendations
                   (id, rec_type, title, description, confidence, pattern_id,
                    suggested_action, suggested_params, reason, dismissed, accepted, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    rec_data["id"],
                    rec_data["rec_type"],
                    rec_data["title"],
                    rec_data.get("description", ""),
                    rec_data.get("confidence", 0.0),
                    rec_data.get("pattern_id", ""),
                    rec_data.get("suggested_action", ""),
                    json.dumps(rec_data.get("suggested_params", {})),
                    rec_data.get("reason", ""),
                    1 if rec_data.get("dismissed", False) else 0,
                    1 if rec_data.get("accepted", False) else 0,
                    rec_data["created_at"],
                ),
            )

    def get_recommendations(self, rec_type: Optional[str] = None,
                            active_only: bool = True, limit: int = 50) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            query = "SELECT * FROM recommendations WHERE 1=1"
            params = []
            if rec_type:
                query += " AND rec_type = ?"
                params.append(rec_type)
            if active_only:
                query += " AND dismissed = 0 AND accepted = 0"
            query += " ORDER BY confidence DESC, created_at DESC LIMIT ?"
            params.append(limit)

            rows = conn.execute(query, params).fetchall()
            results = []
            for r in rows:
                d = dict(r)
                d["suggested_params"] = json.loads(d.get("suggested_params", "{}"))
                d["dismissed"] = bool(d.get("dismissed", 0))
                d["accepted"] = bool(d.get("accepted", 0))
                results.append(d)
            return results

    def update_recommendation(self, rec_id: str, updates: Dict[str, Any]) -> bool:
        with self._get_connection() as conn:
            if "dismissed" in updates:
                conn.execute(
                    "UPDATE recommendations SET dismissed = ? WHERE id = ?",
                    (1 if updates["dismissed"] else 0, rec_id),
                )
            if "accepted" in updates:
                conn.execute(
                    "UPDATE recommendations SET accepted = ? WHERE id = ?",
                    (1 if updates["accepted"] else 0, rec_id),
                )
            return True

    def save_habit(self, habit_data: Dict[str, Any]):
        with self._get_connection() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO user_habits
                   (id, name, description, actions, typical_time, typical_days,
                    frequency_per_week, consistency, duration_minutes, context,
                    automation_potential, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    habit_data["id"],
                    habit_data["name"],
                    habit_data.get("description", ""),
                    json.dumps(habit_data.get("actions", [])),
                    habit_data.get("typical_time", ""),
                    json.dumps(habit_data.get("typical_days", [])),
                    habit_data.get("frequency_per_week", 0.0),
                    habit_data.get("consistency", 0.0),
                    habit_data.get("duration_minutes", 0.0),
                    habit_data.get("context", ""),
                    habit_data.get("automation_potential", 0.0),
                    habit_data.get("created_at", ""),
                ),
            )

    def get_habits(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM user_habits ORDER BY consistency DESC, frequency_per_week DESC LIMIT ?",
                (limit,),
            ).fetchall()
            results = []
            for r in rows:
                d = dict(r)
                d["actions"] = json.loads(d.get("actions", "[]"))
                d["typical_days"] = json.loads(d.get("typical_days", "[]"))
                results.append(d)
            return results

    def save_prediction(self, pred_data: Dict[str, Any]):
        with self._get_connection() as conn:
            conn.execute(
                """INSERT INTO prediction_log
                   (id, predicted_action, predicted_agent, confidence, actual_action, was_correct, timestamp)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    pred_data["id"],
                    pred_data["predicted_action"],
                    pred_data.get("predicted_agent", ""),
                    pred_data.get("confidence", 0.0),
                    pred_data.get("actual_action", ""),
                    1 if pred_data.get("was_correct", False) else 0,
                    pred_data["timestamp"],
                ),
            )

    def get_prediction_accuracy(self, days: int = 7) -> Dict[str, Any]:
        with self._get_connection() as conn:
            total = conn.execute(
                "SELECT COUNT(*) FROM prediction_log WHERE timestamp >= date('now', ?)",
                (f"-{days} days",),
            ).fetchone()[0]
            correct = conn.execute(
                "SELECT COUNT(*) FROM prediction_log WHERE was_correct = 1 AND timestamp >= date('now', ?)",
                (f"-{days} days",),
            ).fetchone()[0]
            return {
                "total": total,
                "correct": correct,
                "accuracy": round(correct / max(total, 1) * 100, 1),
            }

    def get_stats(self) -> Dict[str, Any]:
        with self._get_connection() as conn:
            total_behaviors = conn.execute("SELECT COUNT(*) FROM behavior_records").fetchone()[0]
            total_patterns = conn.execute("SELECT COUNT(*) FROM learned_patterns").fetchone()[0]
            confirmed_patterns = conn.execute(
                "SELECT COUNT(*) FROM learned_patterns WHERE status = 'confirmed'"
            ).fetchone()[0]
            total_habits = conn.execute("SELECT COUNT(*) FROM user_habits").fetchone()[0]
            total_recs = conn.execute("SELECT COUNT(*) FROM recommendations").fetchone()[0]
            accepted_recs = conn.execute(
                "SELECT COUNT(*) FROM recommendations WHERE accepted = 1"
            ).fetchone()[0]

            most_common = conn.execute(
                "SELECT action, COUNT(*) as cnt FROM behavior_records GROUP BY action ORDER BY cnt DESC LIMIT 1"
            ).fetchone()

            most_active_hour = conn.execute(
                "SELECT hour, COUNT(*) as cnt FROM behavior_records GROUP BY hour ORDER BY cnt DESC LIMIT 1"
            ).fetchone()

            most_active_day = conn.execute(
                "SELECT day_of_week, COUNT(*) as cnt FROM behavior_records GROUP BY day_of_week ORDER BY cnt DESC LIMIT 1"
            ).fetchone()

            first_record = conn.execute(
                "SELECT timestamp FROM behavior_records ORDER BY timestamp ASC LIMIT 1"
            ).fetchone()

            learning_days = 0
            if first_record:
                from datetime import datetime
                try:
                    first = datetime.fromisoformat(first_record["timestamp"])
                    learning_days = (datetime.now() - first).days + 1
                except (ValueError, TypeError):
                    pass

            day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

            return {
                "total_behaviors_recorded": total_behaviors,
                "patterns_learned": total_patterns,
                "confirmed_patterns": confirmed_patterns,
                "habits_detected": total_habits,
                "recommendations_made": total_recs,
                "recommendations_accepted": accepted_recs,
                "most_common_action": most_common["action"] if most_common else "",
                "most_active_hour": most_active_hour["hour"] if most_active_hour else 0,
                "most_active_day": day_names[most_active_day["day_of_week"]] if most_active_day else "",
                "learning_days": learning_days,
            }

    def cleanup_old_records(self, days: int = 90) -> int:
        with self._get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM behavior_records WHERE timestamp < date('now', ?)",
                (f"-{days} days",),
            )
            return cursor.rowcount
