"""
Analytics Agent Storage
SQLite persistence for usage records, performance metrics, resource snapshots,
productivity sessions, and analytics reports.
"""

import sqlite3
import json
import os
from contextlib import contextmanager
from typing import List, Optional, Dict, Any
from pathlib import Path

from core.logger import Logger


class AnalyticsStorage:
    """SQLite storage for analytics agent data."""

    def __init__(self, db_path: Optional[str] = None):
        self.logger = Logger().get_logger("AnalyticsStorage")
        if db_path is None:
            db_path = os.path.join(
                Path(__file__).parent.parent.parent, "data", "analytics.db"
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
                CREATE TABLE IF NOT EXISTS usage_records (
                    id TEXT PRIMARY KEY,
                    agent_name TEXT NOT NULL,
                    action TEXT NOT NULL,
                    command TEXT DEFAULT '',
                    success INTEGER DEFAULT 0,
                    duration REAL DEFAULT 0.0,
                    timestamp TEXT NOT NULL,
                    session_id TEXT DEFAULT '',
                    user_input_length INTEGER DEFAULT 0,
                    output_length INTEGER DEFAULT 0
                );

                CREATE TABLE IF NOT EXISTS agent_performance (
                    agent_name TEXT PRIMARY KEY,
                    total_calls INTEGER DEFAULT 0,
                    successful_calls INTEGER DEFAULT 0,
                    failed_calls INTEGER DEFAULT 0,
                    avg_duration REAL DEFAULT 0.0,
                    min_duration REAL DEFAULT 0.0,
                    max_duration REAL DEFAULT 0.0,
                    total_duration REAL DEFAULT 0.0,
                    success_rate REAL DEFAULT 0.0,
                    last_used TEXT DEFAULT '',
                    first_used TEXT DEFAULT '',
                    error_counts TEXT DEFAULT '{}',
                    hourly_usage TEXT DEFAULT '{}'
                );

                CREATE TABLE IF NOT EXISTS resource_snapshots (
                    id TEXT PRIMARY KEY,
                    cpu_percent REAL DEFAULT 0.0,
                    memory_percent REAL DEFAULT 0.0,
                    memory_used_gb REAL DEFAULT 0.0,
                    memory_total_gb REAL DEFAULT 0.0,
                    disk_percent REAL DEFAULT 0.0,
                    disk_used_gb REAL DEFAULT 0.0,
                    disk_total_gb REAL DEFAULT 0.0,
                    process_count INTEGER DEFAULT 0,
                    network_connections INTEGER DEFAULT 0,
                    uptime_seconds REAL DEFAULT 0.0,
                    timestamp TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS productivity_sessions (
                    id TEXT PRIMARY KEY,
                    start_time TEXT NOT NULL,
                    end_time TEXT DEFAULT '',
                    duration_minutes REAL DEFAULT 0.0,
                    commands_executed INTEGER DEFAULT 0,
                    agents_used TEXT DEFAULT '[]',
                    workflows_run INTEGER DEFAULT 0,
                    tasks_completed INTEGER DEFAULT 0,
                    interruptions INTEGER DEFAULT 0,
                    focus_score REAL DEFAULT 0.0,
                    session_type TEXT DEFAULT 'general'
                );

                CREATE TABLE IF NOT EXISTS analytics_reports (
                    id TEXT PRIMARY KEY,
                    report_type TEXT NOT NULL,
                    time_range TEXT NOT NULL,
                    generated_at TEXT NOT NULL,
                    summary TEXT DEFAULT '',
                    metrics TEXT DEFAULT '{}',
                    trends TEXT DEFAULT '{}',
                    recommendations TEXT DEFAULT '[]'
                );

                CREATE INDEX IF NOT EXISTS idx_usage_timestamp ON usage_records(timestamp);
                CREATE INDEX IF NOT EXISTS idx_usage_agent ON usage_records(agent_name);
                CREATE INDEX IF NOT EXISTS idx_usage_session ON usage_records(session_id);
                CREATE INDEX IF NOT EXISTS idx_resource_timestamp ON resource_snapshots(timestamp);
                CREATE INDEX IF NOT EXISTS idx_productivity_start ON productivity_sessions(start_time);
                CREATE INDEX IF NOT EXISTS idx_reports_type ON analytics_reports(report_type);
            """)
        self.logger.info(f"Analytics storage initialized: {self.db_path}")

    def save_usage_record(self, record_data: Dict[str, Any]):
        with self._get_connection() as conn:
            conn.execute(
                """INSERT INTO usage_records
                   (id, agent_name, action, command, success, duration, timestamp,
                    session_id, user_input_length, output_length)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    record_data["id"],
                    record_data["agent_name"],
                    record_data["action"],
                    record_data.get("command", "")[:200],
                    1 if record_data.get("success", False) else 0,
                    record_data.get("duration", 0.0),
                    record_data["timestamp"],
                    record_data.get("session_id", ""),
                    record_data.get("user_input_length", 0),
                    record_data.get("output_length", 0),
                ),
            )

    def get_usage_records(self, limit: int = 100, agent_name: Optional[str] = None,
                          start_time: Optional[str] = None, end_time: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            query = "SELECT * FROM usage_records WHERE 1=1"
            params = []
            if agent_name:
                query += " AND agent_name = ?"
                params.append(agent_name)
            if start_time:
                query += " AND timestamp >= ?"
                params.append(start_time)
            if end_time:
                query += " AND timestamp <= ?"
                params.append(end_time)
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)

            rows = conn.execute(query, params).fetchall()
            return [dict(r) for r in rows]

    def save_agent_performance(self, perf_data: Dict[str, Any]):
        with self._get_connection() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO agent_performance
                   (agent_name, total_calls, successful_calls, failed_calls,
                    avg_duration, min_duration, max_duration, total_duration,
                    success_rate, last_used, first_used, error_counts, hourly_usage)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    perf_data["agent_name"],
                    perf_data.get("total_calls", 0),
                    perf_data.get("successful_calls", 0),
                    perf_data.get("failed_calls", 0),
                    perf_data.get("avg_duration", 0.0),
                    perf_data.get("min_duration", 0.0),
                    perf_data.get("max_duration", 0.0),
                    perf_data.get("total_duration", 0.0),
                    perf_data.get("success_rate", 0.0),
                    perf_data.get("last_used", ""),
                    perf_data.get("first_used", ""),
                    json.dumps(perf_data.get("error_counts", {})),
                    json.dumps(perf_data.get("hourly_usage", {})),
                ),
            )

    def get_agent_performance(self, agent_name: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            if agent_name:
                rows = conn.execute(
                    "SELECT * FROM agent_performance WHERE agent_name = ?", (agent_name,)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM agent_performance ORDER BY total_calls DESC"
                ).fetchall()
            results = []
            for r in rows:
                d = dict(r)
                d["error_counts"] = json.loads(d.get("error_counts", "{}"))
                d["hourly_usage"] = json.loads(d.get("hourly_usage", "{}"))
                results.append(d)
            return results

    def save_resource_snapshot(self, snapshot_data: Dict[str, Any]):
        with self._get_connection() as conn:
            conn.execute(
                """INSERT INTO resource_snapshots
                   (id, cpu_percent, memory_percent, memory_used_gb, memory_total_gb,
                    disk_percent, disk_used_gb, disk_total_gb, process_count,
                    network_connections, uptime_seconds, timestamp)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    snapshot_data["id"],
                    snapshot_data.get("cpu_percent", 0.0),
                    snapshot_data.get("memory_percent", 0.0),
                    snapshot_data.get("memory_used_gb", 0.0),
                    snapshot_data.get("memory_total_gb", 0.0),
                    snapshot_data.get("disk_percent", 0.0),
                    snapshot_data.get("disk_used_gb", 0.0),
                    snapshot_data.get("disk_total_gb", 0.0),
                    snapshot_data.get("process_count", 0),
                    snapshot_data.get("network_connections", 0),
                    snapshot_data.get("uptime_seconds", 0.0),
                    snapshot_data["timestamp"],
                ),
            )

    def get_resource_snapshots(self, limit: int = 100, start_time: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            if start_time:
                rows = conn.execute(
                    "SELECT * FROM resource_snapshots WHERE timestamp >= ? ORDER BY timestamp DESC LIMIT ?",
                    (start_time, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM resource_snapshots ORDER BY timestamp DESC LIMIT ?",
                    (limit,),
                ).fetchall()
            return [dict(r) for r in rows]

    def save_productivity_session(self, session_data: Dict[str, Any]):
        with self._get_connection() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO productivity_sessions
                   (id, start_time, end_time, duration_minutes, commands_executed,
                    agents_used, workflows_run, tasks_completed, interruptions,
                    focus_score, session_type)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    session_data["id"],
                    session_data["start_time"],
                    session_data.get("end_time", ""),
                    session_data.get("duration_minutes", 0.0),
                    session_data.get("commands_executed", 0),
                    json.dumps(session_data.get("agents_used", [])),
                    session_data.get("workflows_run", 0),
                    session_data.get("tasks_completed", 0),
                    session_data.get("interruptions", 0),
                    session_data.get("focus_score", 0.0),
                    session_data.get("session_type", "general"),
                ),
            )

    def get_productivity_sessions(self, limit: int = 50, session_type: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            if session_type:
                rows = conn.execute(
                    "SELECT * FROM productivity_sessions WHERE session_type = ? ORDER BY start_time DESC LIMIT ?",
                    (session_type, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM productivity_sessions ORDER BY start_time DESC LIMIT ?",
                    (limit,),
                ).fetchall()
            results = []
            for r in rows:
                d = dict(r)
                d["agents_used"] = json.loads(d.get("agents_used", "[]"))
                results.append(d)
            return results

    def save_report(self, report_data: Dict[str, Any]):
        with self._get_connection() as conn:
            conn.execute(
                """INSERT INTO analytics_reports
                   (id, report_type, time_range, generated_at, summary, metrics, trends, recommendations)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    report_data["id"],
                    report_data["report_type"],
                    report_data["time_range"],
                    report_data["generated_at"],
                    report_data.get("summary", ""),
                    json.dumps(report_data.get("metrics", {})),
                    json.dumps(report_data.get("trends", {})),
                    json.dumps(report_data.get("recommendations", [])),
                ),
            )

    def get_reports(self, report_type: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            if report_type:
                rows = conn.execute(
                    "SELECT * FROM analytics_reports WHERE report_type = ? ORDER BY generated_at DESC LIMIT ?",
                    (report_type, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM analytics_reports ORDER BY generated_at DESC LIMIT ?",
                    (limit,),
                ).fetchall()
            results = []
            for r in rows:
                d = dict(r)
                d["metrics"] = json.loads(d.get("metrics", "{}"))
                d["trends"] = json.loads(d.get("trends", "{}"))
                d["recommendations"] = json.loads(d.get("recommendations", "[]"))
                results.append(d)
            return results

    def get_dashboard_data(self) -> Dict[str, Any]:
        with self._get_connection() as conn:
            total_commands = conn.execute("SELECT COUNT(*) FROM usage_records").fetchone()[0]
            total_agents = conn.execute("SELECT COUNT(DISTINCT agent_name) FROM usage_records").fetchone()[0]
            success_count = conn.execute("SELECT COUNT(*) FROM usage_records WHERE success = 1").fetchone()[0]
            avg_duration = conn.execute("SELECT AVG(duration) FROM usage_records WHERE duration > 0").fetchone()[0] or 0.0

            top_agents = conn.execute(
                """SELECT agent_name, COUNT(*) as count, AVG(duration) as avg_dur,
                   SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as rate
                   FROM usage_records GROUP BY agent_name ORDER BY count DESC LIMIT 5"""
            ).fetchall()

            recent = conn.execute(
                "SELECT * FROM usage_records ORDER BY timestamp DESC LIMIT 10"
            ).fetchall()

            latest_resource = conn.execute(
                "SELECT * FROM resource_snapshots ORDER BY timestamp DESC LIMIT 1"
            ).fetchone()

            return {
                "total_commands": total_commands,
                "total_agents_used": total_agents,
                "success_rate": round(success_count / max(total_commands, 1) * 100, 2),
                "avg_response_time": round(avg_duration, 3),
                "top_agents": [dict(r) for r in top_agents],
                "recent_activity": [dict(r) for r in recent],
                "latest_resource": dict(latest_resource) if latest_resource else {},
            }

    def get_usage_stats(self, agent_name: Optional[str] = None,
                        start_time: Optional[str] = None,
                        end_time: Optional[str] = None) -> Dict[str, Any]:
        with self._get_connection() as conn:
            query = "SELECT COUNT(*) as total, AVG(duration) as avg_dur, MAX(duration) as max_dur, MIN(duration) as min_dur, SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as success_count FROM usage_records WHERE 1=1"
            params = []
            if agent_name:
                query += " AND agent_name = ?"
                params.append(agent_name)
            if start_time:
                query += " AND timestamp >= ?"
                params.append(start_time)
            if end_time:
                query += " AND timestamp <= ?"
                params.append(end_time)

            row = conn.execute(query, params).fetchone()
            d = dict(row) if row else {}
            total = d.get("total", 0) or 0
            success_count = d.get("success_count", 0) or 0
            return {
                "total_commands": total,
                "avg_duration": round(d.get("avg_dur", 0) or 0, 3),
                "max_duration": round(d.get("max_dur", 0) or 0, 3),
                "min_duration": round(d.get("min_dur", 0) or 0, 3),
                "success_count": success_count,
                "success_rate": round(success_count / max(total, 1) * 100, 2),
            }

    def get_hourly_distribution(self, agent_name: Optional[str] = None) -> Dict[str, int]:
        with self._get_connection() as conn:
            if agent_name:
                rows = conn.execute(
                    """SELECT strftime('%H', timestamp) as hour, COUNT(*) as count
                       FROM usage_records WHERE agent_name = ?
                       GROUP BY hour ORDER BY hour""",
                    (agent_name,),
                ).fetchall()
            else:
                rows = conn.execute(
                    """SELECT strftime('%H', timestamp) as hour, COUNT(*) as count
                       FROM usage_records GROUP BY hour ORDER BY hour"""
                ).fetchall()
            return {r["hour"]: r["count"] for r in rows}

    def get_daily_activity(self, days: int = 30) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            rows = conn.execute(
                """SELECT date(timestamp) as day, COUNT(*) as commands,
                   AVG(duration) as avg_dur,
                   SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successes
                   FROM usage_records
                   WHERE timestamp >= date('now', ?)
                   GROUP BY day ORDER BY day""",
                (f"-{days} days",),
            ).fetchall()
            return [dict(r) for r in rows]

    def cleanup_old_records(self, days: int = 90) -> int:
        with self._get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM usage_records WHERE timestamp < date('now', ?)",
                (f"-{days} days",),
            )
            return cursor.rowcount
