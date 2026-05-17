"""
Security Agent Storage
SQLite persistence for security events, audit logs, alerts, and policies.
"""

import sqlite3
import json
import os
from contextlib import contextmanager
from typing import List, Optional, Dict, Any
from pathlib import Path

from core.logger import Logger


class SecurityStorage:
    """SQLite storage for security agent data."""

    def __init__(self, db_path: Optional[str] = None):
        self.logger = Logger().get_logger("SecurityStorage")
        if db_path is None:
            db_path = os.path.join(
                Path(__file__).parent.parent.parent, "data", "security.db"
            )
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
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
                CREATE TABLE IF NOT EXISTS security_events (
                    id TEXT PRIMARY KEY,
                    event_type TEXT NOT NULL,
                    risk_level TEXT NOT NULL,
                    source TEXT NOT NULL,
                    description TEXT NOT NULL,
                    details TEXT DEFAULT '{}',
                    timestamp TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS risk_assessments (
                    id TEXT PRIMARY KEY,
                    command TEXT NOT NULL,
                    risk_level TEXT NOT NULL,
                    risk_score REAL NOT NULL,
                    threats TEXT DEFAULT '[]',
                    reasons TEXT DEFAULT '[]',
                    suggestions TEXT DEFAULT '[]',
                    blocked INTEGER DEFAULT 0,
                    block_reason TEXT DEFAULT '',
                    timestamp TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS permission_rules (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    pattern TEXT NOT NULL,
                    required_level TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    enabled INTEGER DEFAULT 1,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS audit_records (
                    id TEXT PRIMARY KEY,
                    action TEXT NOT NULL,
                    actor TEXT NOT NULL,
                    target TEXT NOT NULL,
                    details TEXT DEFAULT '',
                    risk_level TEXT DEFAULT 'safe',
                    metadata TEXT DEFAULT '{}',
                    timestamp TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS file_protection_rules (
                    id TEXT PRIMARY KEY,
                    path_pattern TEXT NOT NULL,
                    protection_level TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    enabled INTEGER DEFAULT 1,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS security_alerts (
                    id TEXT PRIMARY KEY,
                    severity TEXT NOT NULL,
                    title TEXT NOT NULL,
                    message TEXT NOT NULL,
                    source TEXT DEFAULT '',
                    event_id TEXT DEFAULT '',
                    acknowledged INTEGER DEFAULT 0,
                    resolved INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL,
                    resolved_at TEXT DEFAULT ''
                );

                CREATE TABLE IF NOT EXISTS security_policies (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    max_risk_level TEXT DEFAULT 'medium',
                    auto_block_critical INTEGER DEFAULT 1,
                    audit_enabled INTEGER DEFAULT 1,
                    monitor_processes INTEGER DEFAULT 1,
                    monitor_files INTEGER DEFAULT 1,
                    monitor_network INTEGER DEFAULT 0,
                    alert_on_suspicious INTEGER DEFAULT 1,
                    safe_execution_mode INTEGER DEFAULT 1,
                    updated_at TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_events_timestamp ON security_events(timestamp);
                CREATE INDEX IF NOT EXISTS idx_events_risk ON security_events(risk_level);
                CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_records(timestamp);
                CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_records(action);
                CREATE INDEX IF NOT EXISTS idx_alerts_severity ON security_alerts(severity);
                CREATE INDEX IF NOT EXISTS idx_alerts_resolved ON security_alerts(resolved);
                CREATE INDEX IF NOT EXISTS idx_risk_timestamp ON risk_assessments(timestamp);
            """)
        self.logger.info(f"Security storage initialized: {self.db_path}")

    def save_event(self, event_data: Dict[str, Any]):
        with self._get_connection() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO security_events
                   (id, event_type, risk_level, source, description, details, timestamp)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    event_data["id"],
                    event_data["event_type"],
                    event_data["risk_level"],
                    event_data["source"],
                    event_data["description"],
                    json.dumps(event_data.get("details", {})),
                    event_data["timestamp"],
                ),
            )

    def get_events(self, limit: int = 50, risk_level: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            if risk_level:
                rows = conn.execute(
                    "SELECT * FROM security_events WHERE risk_level = ? ORDER BY timestamp DESC LIMIT ?",
                    (risk_level, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM security_events ORDER BY timestamp DESC LIMIT ?",
                    (limit,),
                ).fetchall()
            return [dict(r) for r in rows]

    def save_assessment(self, assessment_data: Dict[str, Any]):
        with self._get_connection() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO risk_assessments
                   (id, command, risk_level, risk_score, threats, reasons, suggestions,
                    blocked, block_reason, timestamp)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    assessment_data["id"],
                    assessment_data["command"],
                    assessment_data["risk_level"],
                    assessment_data["risk_score"],
                    json.dumps(assessment_data.get("threats", [])),
                    json.dumps(assessment_data.get("reasons", [])),
                    json.dumps(assessment_data.get("suggestions", [])),
                    1 if assessment_data.get("blocked", False) else 0,
                    assessment_data.get("block_reason", ""),
                    assessment_data["timestamp"],
                ),
            )

    def get_assessments(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM risk_assessments ORDER BY timestamp DESC LIMIT ?",
                (limit,),
            ).fetchall()
            results = []
            for r in rows:
                d = dict(r)
                d["threats"] = json.loads(d.get("threats", "[]"))
                d["reasons"] = json.loads(d.get("reasons", "[]"))
                d["suggestions"] = json.loads(d.get("suggestions", "[]"))
                d["blocked"] = bool(d["blocked"])
                results.append(d)
            return results

    def save_permission_rule(self, rule_data: Dict[str, Any]):
        with self._get_connection() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO permission_rules
                   (id, name, pattern, required_level, description, enabled, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    rule_data["id"],
                    rule_data["name"],
                    rule_data["pattern"],
                    rule_data["required_level"],
                    rule_data.get("description", ""),
                    1 if rule_data.get("enabled", True) else 0,
                    rule_data["created_at"],
                ),
            )

    def get_permission_rules(self, enabled_only: bool = True) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            if enabled_only:
                rows = conn.execute(
                    "SELECT * FROM permission_rules WHERE enabled = 1 ORDER BY name"
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM permission_rules ORDER BY name"
                ).fetchall()
            return [dict(r) for r in rows]

    def delete_permission_rule(self, rule_id: str) -> bool:
        with self._get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM permission_rules WHERE id = ?", (rule_id,)
            )
            return cursor.rowcount > 0

    def save_audit_record(self, record_data: Dict[str, Any]):
        with self._get_connection() as conn:
            conn.execute(
                """INSERT INTO audit_records
                   (id, action, actor, target, details, risk_level, metadata, timestamp)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    record_data["id"],
                    record_data["action"],
                    record_data["actor"],
                    record_data["target"],
                    record_data.get("details", ""),
                    record_data.get("risk_level", "safe"),
                    json.dumps(record_data.get("metadata", {})),
                    record_data["timestamp"],
                ),
            )

    def get_audit_records(self, limit: int = 100, action: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            if action:
                rows = conn.execute(
                    "SELECT * FROM audit_records WHERE action = ? ORDER BY timestamp DESC LIMIT ?",
                    (action, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM audit_records ORDER BY timestamp DESC LIMIT ?",
                    (limit,),
                ).fetchall()
            results = []
            for r in rows:
                d = dict(r)
                d["metadata"] = json.loads(d.get("metadata", "{}"))
                results.append(d)
            return results

    def save_file_protection_rule(self, rule_data: Dict[str, Any]):
        with self._get_connection() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO file_protection_rules
                   (id, path_pattern, protection_level, description, enabled, created_at)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    rule_data["id"],
                    rule_data["path_pattern"],
                    rule_data["protection_level"],
                    rule_data.get("description", ""),
                    1 if rule_data.get("enabled", True) else 0,
                    rule_data["created_at"],
                ),
            )

    def get_file_protection_rules(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM file_protection_rules WHERE enabled = 1 ORDER BY path_pattern"
            ).fetchall()
            return [dict(r) for r in rows]

    def delete_file_protection_rule(self, rule_id: str) -> bool:
        with self._get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM file_protection_rules WHERE id = ?", (rule_id,)
            )
            return cursor.rowcount > 0

    def save_alert(self, alert_data: Dict[str, Any]):
        with self._get_connection() as conn:
            conn.execute(
                """INSERT INTO security_alerts
                   (id, severity, title, message, source, event_id, acknowledged, resolved,
                    created_at, resolved_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    alert_data["id"],
                    alert_data["severity"],
                    alert_data["title"],
                    alert_data["message"],
                    alert_data.get("source", ""),
                    alert_data.get("event_id", ""),
                    1 if alert_data.get("acknowledged", False) else 0,
                    1 if alert_data.get("resolved", False) else 0,
                    alert_data["created_at"],
                    alert_data.get("resolved_at", ""),
                ),
            )

    def get_alerts(self, limit: int = 50, unresolved_only: bool = True) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            if unresolved_only:
                rows = conn.execute(
                    "SELECT * FROM security_alerts WHERE resolved = 0 ORDER BY created_at DESC LIMIT ?",
                    (limit,),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM security_alerts ORDER BY created_at DESC LIMIT ?",
                    (limit,),
                ).fetchall()
            return [dict(r) for r in rows]

    def update_alert(self, alert_id: str, updates: Dict[str, Any]) -> bool:
        with self._get_connection() as conn:
            if "acknowledged" in updates:
                conn.execute(
                    "UPDATE security_alerts SET acknowledged = ? WHERE id = ?",
                    (1 if updates["acknowledged"] else 0, alert_id),
                )
            if "resolved" in updates:
                conn.execute(
                    "UPDATE security_alerts SET resolved = ?, resolved_at = ? WHERE id = ?",
                    (1 if updates["resolved"] else 0, updates.get("resolved_at", ""), alert_id),
                )
            return True

    def save_policy(self, policy_data: Dict[str, Any]):
        with self._get_connection() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO security_policies
                   (id, name, description, max_risk_level, auto_block_critical, audit_enabled,
                    monitor_processes, monitor_files, monitor_network, alert_on_suspicious,
                    safe_execution_mode, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    policy_data["id"],
                    policy_data["name"],
                    policy_data.get("description", ""),
                    policy_data.get("max_risk_level", "medium"),
                    1 if policy_data.get("auto_block_critical", True) else 0,
                    1 if policy_data.get("audit_enabled", True) else 0,
                    1 if policy_data.get("monitor_processes", True) else 0,
                    1 if policy_data.get("monitor_files", True) else 0,
                    1 if policy_data.get("monitor_network", False) else 0,
                    1 if policy_data.get("alert_on_suspicious", True) else 0,
                    1 if policy_data.get("safe_execution_mode", True) else 0,
                    policy_data["updated_at"],
                ),
            )

    def get_policy(self, name: str = "default") -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM security_policies WHERE name = ?", (name,)
            ).fetchone()
            if row:
                d = dict(row)
                d["auto_block_critical"] = bool(d["auto_block_critical"])
                d["audit_enabled"] = bool(d["audit_enabled"])
                d["monitor_processes"] = bool(d["monitor_processes"])
                d["monitor_files"] = bool(d["monitor_files"])
                d["monitor_network"] = bool(d["monitor_network"])
                d["alert_on_suspicious"] = bool(d["alert_on_suspicious"])
                d["safe_execution_mode"] = bool(d["safe_execution_mode"])
                return d
            return None

    def get_stats(self) -> Dict[str, Any]:
        with self._get_connection() as conn:
            total_events = conn.execute("SELECT COUNT(*) FROM security_events").fetchone()[0]
            total_assessments = conn.execute("SELECT COUNT(*) FROM risk_assessments").fetchone()[0]
            total_audit = conn.execute("SELECT COUNT(*) FROM audit_records").fetchone()[0]
            total_alerts = conn.execute("SELECT COUNT(*) FROM security_alerts").fetchone()[0]
            unresolved_alerts = conn.execute(
                "SELECT COUNT(*) FROM security_alerts WHERE resolved = 0"
            ).fetchone()[0]
            critical_events = conn.execute(
                "SELECT COUNT(*) FROM security_events WHERE risk_level = 'critical'"
            ).fetchone()[0]
            high_events = conn.execute(
                "SELECT COUNT(*) FROM security_events WHERE risk_level = 'high'"
            ).fetchone()[0]
            blocked_commands = conn.execute(
                "SELECT COUNT(*) FROM risk_assessments WHERE blocked = 1"
            ).fetchone()[0]

            return {
                "total_events": total_events,
                "total_assessments": total_assessments,
                "total_audit_records": total_audit,
                "total_alerts": total_alerts,
                "unresolved_alerts": unresolved_alerts,
                "critical_events": critical_events,
                "high_risk_events": high_events,
                "blocked_commands": blocked_commands,
            }
