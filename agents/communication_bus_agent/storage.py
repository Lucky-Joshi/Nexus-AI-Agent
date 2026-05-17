"""
NEXUS - Agent Communication Bus
Persistent storage for bus messages, subscriptions, shared state, and event logs.
"""

import json
import sqlite3
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from contextlib import contextmanager
from core.logger import Logger
from core.database import Database


class BusStorage:
    """Handles persistence for communication bus data."""

    def __init__(self):
        self.logger = Logger().get_logger("BusStorage")
        self.db = Database()
        self._initialize_tables()

    def _initialize_tables(self):
        """Create bus-specific tables if they don't exist."""
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS bus_messages (
                id TEXT PRIMARY KEY,
                timestamp REAL NOT NULL,
                sender TEXT NOT NULL,
                recipients TEXT NOT NULL,
                message_type TEXT NOT NULL,
                priority INTEGER NOT NULL DEFAULT 2,
                event TEXT NOT NULL,
                payload TEXT NOT NULL DEFAULT '{}',
                metadata TEXT NOT NULL DEFAULT '{}',
                ttl INTEGER NOT NULL DEFAULT 300,
                delivery_status TEXT NOT NULL DEFAULT 'pending',
                retry_count INTEGER NOT NULL DEFAULT 0,
                max_retries INTEGER NOT NULL DEFAULT 3,
                correlation_id TEXT,
                reply_to TEXT,
                requires_ack INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            )
        """)

        self.db.execute("""
            CREATE TABLE IF NOT EXISTS bus_subscriptions (
                id TEXT PRIMARY KEY,
                agent_name TEXT NOT NULL,
                event_pattern TEXT NOT NULL,
                subscription_type TEXT NOT NULL DEFAULT 'sync',
                scope TEXT NOT NULL DEFAULT 'global',
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL,
                max_invocations INTEGER NOT NULL DEFAULT 0,
                invocation_count INTEGER NOT NULL DEFAULT 0
            )
        """)

        self.db.execute("""
            CREATE TABLE IF NOT EXISTS bus_shared_state (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                owner TEXT NOT NULL DEFAULT '',
                ttl INTEGER NOT NULL DEFAULT 0,
                is_locked INTEGER NOT NULL DEFAULT 0,
                lock_owner TEXT NOT NULL DEFAULT '',
                version INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                access_count INTEGER NOT NULL DEFAULT 0,
                metadata TEXT NOT NULL DEFAULT '{}'
            )
        """)

        self.db.execute("""
            CREATE TABLE IF NOT EXISTS bus_event_log (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                source_agent TEXT NOT NULL,
                target_agent TEXT NOT NULL DEFAULT '',
                event_name TEXT NOT NULL,
                message_id TEXT NOT NULL,
                details TEXT NOT NULL DEFAULT '{}',
                success INTEGER NOT NULL DEFAULT 1,
                error_message TEXT NOT NULL DEFAULT '',
                duration_ms REAL NOT NULL DEFAULT 0.0
            )
        """)

        self.db.execute("""
            CREATE INDEX IF NOT EXISTS idx_bus_messages_event ON bus_messages(event)
        """)
        self.db.execute("""
            CREATE INDEX IF NOT EXISTS idx_bus_messages_sender ON bus_messages(sender)
        """)
        self.db.execute("""
            CREATE INDEX IF NOT EXISTS idx_bus_messages_status ON bus_messages(delivery_status)
        """)
        self.db.execute("""
            CREATE INDEX IF NOT EXISTS idx_bus_messages_created ON bus_messages(created_at)
        """)
        self.db.execute("""
            CREATE INDEX IF NOT EXISTS idx_bus_subscriptions_agent ON bus_subscriptions(agent_name)
        """)
        self.db.execute("""
            CREATE INDEX IF NOT EXISTS idx_bus_subscriptions_active ON bus_subscriptions(is_active)
        """)
        self.db.execute("""
            CREATE INDEX IF NOT EXISTS idx_bus_event_log_type ON bus_event_log(event_type)
        """)
        self.db.execute("""
            CREATE INDEX IF NOT EXISTS idx_bus_event_log_source ON bus_event_log(source_agent)
        """)
        self.db.execute("""
            CREATE INDEX IF NOT EXISTS idx_bus_event_log_timestamp ON bus_event_log(timestamp)
        """)

        self.logger.info("Bus storage tables initialized")

    def save_message(self, message_data: Dict[str, Any]):
        """Save a message to the database."""
        self.db.execute(
            """INSERT OR REPLACE INTO bus_messages
               (id, timestamp, sender, recipients, message_type, priority, event,
                payload, metadata, ttl, delivery_status, retry_count, max_retries,
                correlation_id, reply_to, requires_ack, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                message_data["id"],
                message_data["timestamp"],
                message_data["sender"],
                json.dumps(message_data.get("recipients", [])),
                message_data["message_type"],
                message_data["priority"],
                message_data["event"],
                json.dumps(message_data.get("payload", {})),
                json.dumps(message_data.get("metadata", {})),
                message_data.get("ttl", 300),
                message_data.get("delivery_status", "pending"),
                message_data.get("retry_count", 0),
                message_data.get("max_retries", 3),
                message_data.get("correlation_id"),
                message_data.get("reply_to"),
                1 if message_data.get("requires_ack", False) else 0,
                message_data.get("created_at", datetime.now().isoformat()),
            ),
        )

    def get_message(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a message by ID."""
        row = self.db.fetchone("SELECT * FROM bus_messages WHERE id = ?", (message_id,))
        if row:
            return dict(row)
        return None

    def update_message_status(self, message_id: str, status: str, retry_count: int = None):
        """Update the delivery status of a message."""
        if retry_count is not None:
            self.db.execute(
                "UPDATE bus_messages SET delivery_status = ?, retry_count = ? WHERE id = ?",
                (status, retry_count, message_id),
            )
        else:
            self.db.execute(
                "UPDATE bus_messages SET delivery_status = ? WHERE id = ?",
                (status, message_id),
            )

    def get_messages_by_status(self, status: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get messages with a specific delivery status."""
        rows = self.db.fetchall(
            "SELECT * FROM bus_messages WHERE delivery_status = ? ORDER BY created_at DESC LIMIT ?",
            (status, limit),
        )
        return [dict(row) for row in rows]

    def get_messages_by_agent(self, agent_name: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get messages sent by or to a specific agent."""
        rows = self.db.fetchall(
            """SELECT * FROM bus_messages
               WHERE sender = ? OR recipients LIKE ?
               ORDER BY created_at DESC LIMIT ?""",
            (agent_name, f'%"{agent_name}"%', limit),
        )
        return [dict(row) for row in rows]

    def get_messages_by_event(self, event: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get messages for a specific event type."""
        rows = self.db.fetchall(
            "SELECT * FROM bus_messages WHERE event = ? ORDER BY created_at DESC LIMIT ?",
            (event, limit),
        )
        return [dict(row) for row in rows]

    def delete_expired_messages(self) -> int:
        """Remove expired messages from the database."""
        now = datetime.now().timestamp()
        cursor = self.db.execute(
            "DELETE FROM bus_messages WHERE (timestamp + ttl) < ?",
            (now,),
        )
        deleted = cursor.rowcount if hasattr(cursor, "rowcount") else 0
        if deleted > 0:
            self.logger.debug(f"Deleted {deleted} expired messages")
        return deleted

    def save_subscription(self, sub_data: Dict[str, Any]):
        """Save a subscription to the database."""
        self.db.execute(
            """INSERT OR REPLACE INTO bus_subscriptions
               (id, agent_name, event_pattern, subscription_type, scope,
                is_active, created_at, max_invocations, invocation_count)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                sub_data["id"],
                sub_data["agent_name"],
                sub_data["event_pattern"],
                sub_data.get("subscription_type", "sync"),
                sub_data.get("scope", "global"),
                1 if sub_data.get("is_active", True) else 0,
                sub_data.get("created_at", datetime.now().isoformat()),
                sub_data.get("max_invocations", 0),
                sub_data.get("invocation_count", 0),
            ),
        )

    def get_subscriptions(self, agent_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get subscriptions, optionally filtered by agent."""
        if agent_name:
            rows = self.db.fetchall(
                "SELECT * FROM bus_subscriptions WHERE agent_name = ?",
                (agent_name,),
            )
        else:
            rows = self.db.fetchall("SELECT * FROM bus_subscriptions")
        return [dict(row) for row in rows]

    def update_subscription(self, sub_id: str, updates: Dict[str, Any]):
        """Update a subscription."""
        if "is_active" in updates:
            self.db.execute(
                "UPDATE bus_subscriptions SET is_active = ? WHERE id = ?",
                (1 if updates["is_active"] else 0, sub_id),
            )
        if "invocation_count" in updates:
            self.db.execute(
                "UPDATE bus_subscriptions SET invocation_count = ? WHERE id = ?",
                (updates["invocation_count"], sub_id),
            )

    def delete_subscription(self, sub_id: str):
        """Delete a subscription."""
        self.db.execute("DELETE FROM bus_subscriptions WHERE id = ?", (sub_id,))

    def save_state_entry(self, entry_data: Dict[str, Any]):
        """Save a shared state entry."""
        self.db.execute(
            """INSERT OR REPLACE INTO bus_shared_state
               (key, value, owner, ttl, is_locked, lock_owner, version,
                created_at, updated_at, access_count, metadata)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                entry_data["key"],
                json.dumps(entry_data["value"]),
                entry_data.get("owner", ""),
                entry_data.get("ttl", 0),
                1 if entry_data.get("is_locked", False) else 0,
                entry_data.get("lock_owner", ""),
                entry_data.get("version", 1),
                entry_data.get("created_at", datetime.now().isoformat()),
                entry_data.get("updated_at", datetime.now().isoformat()),
                entry_data.get("access_count", 0),
                json.dumps(entry_data.get("metadata", {})),
            ),
        )

    def get_state_entry(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve a shared state entry by key."""
        row = self.db.fetchone("SELECT * FROM bus_shared_state WHERE key = ?", (key,))
        if row:
            data = dict(row)
            data["value"] = json.loads(data["value"])
            data["metadata"] = json.loads(data["metadata"])
            return data
        return None

    def get_all_state_entries(self) -> List[Dict[str, Any]]:
        """Get all shared state entries."""
        rows = self.db.fetchall("SELECT * FROM bus_shared_state")
        result = []
        for row in rows:
            data = dict(row)
            data["value"] = json.loads(data["value"])
            data["metadata"] = json.loads(data["metadata"])
            result.append(data)
        return result

    def delete_state_entry(self, key: str):
        """Delete a shared state entry."""
        self.db.execute("DELETE FROM bus_shared_state WHERE key = ?", (key,))

    def delete_expired_state_entries(self) -> int:
        """Remove expired state entries."""
        now = datetime.now()
        rows = self.db.fetchall("SELECT * FROM bus_shared_state WHERE ttl > 0")
        deleted = 0
        for row in rows:
            created = datetime.fromisoformat(row["created_at"])
            ttl = row["ttl"]
            if (now - created).total_seconds() > ttl:
                self.db.execute("DELETE FROM bus_shared_state WHERE key = ?", (row["key"],))
                deleted += 1
        if deleted > 0:
            self.logger.debug(f"Deleted {deleted} expired state entries")
        return deleted

    def log_event(self, log_data: Dict[str, Any]):
        """Log an event to the database."""
        self.db.execute(
            """INSERT INTO bus_event_log
               (id, timestamp, event_type, source_agent, target_agent, event_name,
                message_id, details, success, error_message, duration_ms)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                log_data["id"],
                log_data.get("timestamp", datetime.now().isoformat()),
                log_data["event_type"],
                log_data.get("source_agent", ""),
                log_data.get("target_agent", ""),
                log_data.get("event_name", ""),
                log_data.get("message_id", ""),
                json.dumps(log_data.get("details", {})),
                1 if log_data.get("success", True) else 0,
                log_data.get("error_message", ""),
                log_data.get("duration_ms", 0.0),
            ),
        )

    def get_event_logs(
        self,
        event_type: Optional[str] = None,
        source_agent: Optional[str] = None,
        limit: int = 100,
        hours: int = 24,
    ) -> List[Dict[str, Any]]:
        """Retrieve event logs with optional filters."""
        query = "SELECT * FROM bus_event_log WHERE timestamp > ?"
        params: list = [(datetime.now() - timedelta(hours=hours)).isoformat()]

        if event_type:
            query += " AND event_type = ?"
            params.append(event_type)
        if source_agent:
            query += " AND source_agent = ?"
            params.append(source_agent)

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        rows = self.db.fetchall(query, tuple(params))
        result = []
        for row in rows:
            data = dict(row)
            data["details"] = json.loads(data["details"]) if data.get("details") else {}
            result.append(data)
        return result

    def get_event_stats(self, hours: int = 24) -> Dict[str, Any]:
        """Get statistics about event logs."""
        since = (datetime.now() - timedelta(hours=hours)).isoformat()

        total = self.db.fetchone(
            "SELECT COUNT(*) as count FROM bus_event_log WHERE timestamp > ?",
            (since,),
        )

        by_type = self.db.fetchall(
            "SELECT event_type, COUNT(*) as count FROM bus_event_log WHERE timestamp > ? GROUP BY event_type",
            (since,),
        )

        by_source = self.db.fetchall(
            "SELECT source_agent, COUNT(*) as count FROM bus_event_log WHERE timestamp > ? GROUP BY source_agent",
            (since,),
        )

        failed = self.db.fetchone(
            "SELECT COUNT(*) as count FROM bus_event_log WHERE timestamp > ? AND success = 0",
            (since,),
        )

        avg_duration = self.db.fetchone(
            "SELECT AVG(duration_ms) as avg_duration FROM bus_event_log WHERE timestamp > ?",
            (since,),
        )

        return {
            "total_events": total["count"] if total else 0,
            "by_type": {row["event_type"]: row["count"] for row in by_type},
            "by_source": {row["source_agent"]: row["count"] for row in by_source},
            "failed_events": failed["count"] if failed else 0,
            "avg_duration_ms": round(avg_duration["avg_duration"], 2) if avg_duration["avg_duration"] else 0,
        }

    def cleanup_old_logs(self, days: int = 7) -> int:
        """Delete event logs older than specified days."""
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        cursor = self.db.execute(
            "DELETE FROM bus_event_log WHERE timestamp < ?",
            (cutoff,),
        )
        deleted = cursor.rowcount if hasattr(cursor, "rowcount") else 0
        if deleted > 0:
            self.logger.info(f"Cleaned up {deleted} old event logs")
        return deleted
