"""
NEXUS - Autonomous Planner Agent
SQLite persistence for plans, tasks, goal templates, and execution history.
"""

import json
import sqlite3
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

from core.logger import Logger
from core.database import Database


class PlannerStorage:
    """Handles persistence for planner data."""

    def __init__(self):
        self.logger = Logger().get_logger("PlannerStorage")
        self.db = Database()
        self._initialize_tables()

    def _initialize_tables(self):
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS plans (
                id TEXT PRIMARY KEY,
                goal TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                goal_type TEXT NOT NULL DEFAULT 'multi_step',
                status TEXT NOT NULL DEFAULT 'draft',
                created_by TEXT NOT NULL DEFAULT 'user',
                created_at TEXT NOT NULL,
                started_at TEXT,
                completed_at TEXT,
                total_tasks INTEGER NOT NULL DEFAULT 0,
                completed_tasks INTEGER NOT NULL DEFAULT 0,
                failed_tasks INTEGER NOT NULL DEFAULT 0,
                replan_count INTEGER NOT NULL DEFAULT 0,
                last_replan_reason TEXT NOT NULL DEFAULT '',
                variables TEXT NOT NULL DEFAULT '{}',
                context TEXT NOT NULL DEFAULT '{}',
                metadata TEXT NOT NULL DEFAULT '{}'
            )
        """)

        self.db.execute("""
            CREATE TABLE IF NOT EXISTS plan_tasks (
                id TEXT PRIMARY KEY,
                plan_id TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                agent_name TEXT NOT NULL DEFAULT '',
                command TEXT NOT NULL,
                params TEXT NOT NULL DEFAULT '{}',
                priority INTEGER NOT NULL DEFAULT 2,
                status TEXT NOT NULL DEFAULT 'pending',
                dependencies TEXT NOT NULL DEFAULT '',
                dependency_type TEXT NOT NULL DEFAULT 'required',
                estimated_duration INTEGER NOT NULL DEFAULT 0,
                actual_duration REAL NOT NULL DEFAULT 0.0,
                max_retries INTEGER NOT NULL DEFAULT 1,
                retry_count INTEGER NOT NULL DEFAULT 0,
                fallback_command TEXT NOT NULL DEFAULT '',
                condition TEXT NOT NULL DEFAULT '',
                output_variable TEXT NOT NULL DEFAULT '',
                result TEXT NOT NULL DEFAULT '',
                error_message TEXT NOT NULL DEFAULT '',
                started_at TEXT,
                completed_at TEXT,
                created_at TEXT NOT NULL,
                metadata TEXT NOT NULL DEFAULT '{}',
                FOREIGN KEY (plan_id) REFERENCES plans(id)
            )
        """)

        self.db.execute("""
            CREATE TABLE IF NOT EXISTS goal_templates (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                trigger_keywords TEXT NOT NULL DEFAULT '[]',
                task_blueprint TEXT NOT NULL DEFAULT '[]',
                is_active INTEGER NOT NULL DEFAULT 1,
                usage_count INTEGER NOT NULL DEFAULT 0
            )
        """)

        self.db.execute("""
            CREATE TABLE IF NOT EXISTS plan_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plan_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                details TEXT NOT NULL DEFAULT '{}',
                timestamp TEXT NOT NULL,
                FOREIGN KEY (plan_id) REFERENCES plans(id)
            )
        """)

        self.db.execute("CREATE INDEX IF NOT EXISTS idx_plans_status ON plans(status)")
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_plans_created ON plans(created_at)")
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_tasks_plan ON plan_tasks(plan_id)")
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_tasks_status ON plan_tasks(status)")
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_tasks_agent ON plan_tasks(agent_name)")
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_history_plan ON plan_history(plan_id)")
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_history_timestamp ON plan_history(timestamp)")

        self.logger.info("Planner storage tables initialized")

    def save_plan(self, plan_data: Dict[str, Any]):
        self.db.execute(
            """INSERT OR REPLACE INTO plans
               (id, goal, description, goal_type, status, created_by, created_at,
                started_at, completed_at, total_tasks, completed_tasks, failed_tasks,
                replan_count, last_replan_reason, variables, context, metadata)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                plan_data["id"], plan_data["goal"], plan_data.get("description", ""),
                plan_data.get("goal_type", "multi_step"), plan_data.get("status", "draft"),
                plan_data.get("created_by", "user"), plan_data.get("created_at", datetime.now().isoformat()),
                plan_data.get("started_at"), plan_data.get("completed_at"),
                plan_data.get("total_tasks", 0), plan_data.get("completed_tasks", 0),
                plan_data.get("failed_tasks", 0), plan_data.get("replan_count", 0),
                plan_data.get("last_replan_reason", ""),
                json.dumps(plan_data.get("variables", {})),
                json.dumps(plan_data.get("context", {})),
                json.dumps(plan_data.get("metadata", {})),
            ),
        )

    def get_plan(self, plan_id: str) -> Optional[Dict[str, Any]]:
        row = self.db.fetchone("SELECT * FROM plans WHERE id = ?", (plan_id,))
        return dict(row) if row else None

    def get_plans(self, status: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        if status:
            rows = self.db.fetchall(
                "SELECT * FROM plans WHERE status = ? ORDER BY created_at DESC LIMIT ?",
                (status, limit),
            )
        else:
            rows = self.db.fetchall("SELECT * FROM plans ORDER BY created_at DESC LIMIT ?", (limit,))
        return [dict(row) for row in rows]

    def delete_plan(self, plan_id: str):
        self.db.execute("DELETE FROM plan_tasks WHERE plan_id = ?", (plan_id,))
        self.db.execute("DELETE FROM plan_history WHERE plan_id = ?", (plan_id,))
        self.db.execute("DELETE FROM plans WHERE id = ?", (plan_id,))

    def save_task(self, task_data: Dict[str, Any]):
        self.db.execute(
            """INSERT OR REPLACE INTO plan_tasks
               (id, plan_id, title, description, agent_name, command, params,
                priority, status, dependencies, dependency_type, estimated_duration,
                actual_duration, max_retries, retry_count, fallback_command,
                condition, output_variable, result, error_message,
                started_at, completed_at, created_at, metadata)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                task_data["id"], task_data["plan_id"], task_data["title"],
                task_data.get("description", ""), task_data.get("agent_name", ""),
                task_data.get("command", ""), json.dumps(task_data.get("params", {})),
                task_data.get("priority", 2), task_data.get("status", "pending"),
                ",".join(task_data.get("dependencies", [])),
                task_data.get("dependency_type", "required"),
                task_data.get("estimated_duration", 0),
                task_data.get("actual_duration", 0.0),
                task_data.get("max_retries", 1), task_data.get("retry_count", 0),
                task_data.get("fallback_command", ""),
                task_data.get("condition", ""), task_data.get("output_variable", ""),
                task_data.get("result", ""), task_data.get("error_message", ""),
                task_data.get("started_at"), task_data.get("completed_at"),
                task_data.get("created_at", datetime.now().isoformat()),
                json.dumps(task_data.get("metadata", {})),
            ),
        )

    def get_tasks(self, plan_id: str) -> List[Dict[str, Any]]:
        rows = self.db.fetchall(
            "SELECT * FROM plan_tasks WHERE plan_id = ? ORDER BY priority, created_at",
            (plan_id,),
        )
        return [dict(row) for row in rows]

    def update_task_status(self, task_id: str, status: str, result: str = "", error: str = "",
                           started_at: str = None, completed_at: str = None,
                           actual_duration: float = None, retry_count: int = None):
        fields = []
        params = []
        fields.append("status = ?")
        params.append(status)
        if result:
            fields.append("result = ?")
            params.append(result)
        if error:
            fields.append("error_message = ?")
            params.append(error)
        if started_at:
            fields.append("started_at = ?")
            params.append(started_at)
        if completed_at:
            fields.append("completed_at = ?")
            params.append(completed_at)
        if actual_duration is not None:
            fields.append("actual_duration = ?")
            params.append(actual_duration)
        if retry_count is not None:
            fields.append("retry_count = ?")
            params.append(retry_count)
        params.append(task_id)

        self.db.execute(f"UPDATE plan_tasks SET {', '.join(fields)} WHERE id = ?", tuple(params))

    def save_goal_template(self, template_data: Dict[str, Any]):
        self.db.execute(
            """INSERT OR REPLACE INTO goal_templates
               (id, name, description, trigger_keywords, task_blueprint, is_active, usage_count)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                template_data["id"], template_data["name"],
                template_data.get("description", ""),
                json.dumps(template_data.get("trigger_keywords", [])),
                json.dumps(template_data.get("task_blueprint", [])),
                1 if template_data.get("is_active", True) else 0,
                template_data.get("usage_count", 0),
            ),
        )

    def get_goal_templates(self, active_only: bool = True) -> List[Dict[str, Any]]:
        if active_only:
            rows = self.db.fetchall("SELECT * FROM goal_templates WHERE is_active = 1")
        else:
            rows = self.db.fetchall("SELECT * FROM goal_templates")
        return [dict(row) for row in rows]

    def log_plan_event(self, plan_id: str, event_type: str, details: Dict[str, Any]):
        self.db.execute(
            "INSERT INTO plan_history (plan_id, event_type, details, timestamp) VALUES (?, ?, ?, ?)",
            (plan_id, event_type, json.dumps(details), datetime.now().isoformat()),
        )

    def get_plan_history(self, plan_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        rows = self.db.fetchall(
            "SELECT * FROM plan_history WHERE plan_id = ? ORDER BY timestamp DESC LIMIT ?",
            (plan_id, limit),
        )
        result = []
        for row in rows:
            data = dict(row)
            data["details"] = json.loads(data["details"]) if data.get("details") else {}
            result.append(data)
        return result

    def get_stats(self) -> Dict[str, Any]:
        total = self.db.fetchone("SELECT COUNT(*) as count FROM plans")
        active = self.db.fetchone("SELECT COUNT(*) as count FROM plans WHERE status = 'active'")
        completed = self.db.fetchone("SELECT COUNT(*) as count FROM plans WHERE status = 'completed'")
        failed = self.db.fetchone("SELECT COUNT(*) as count FROM plans WHERE status = 'failed'")
        today = self.db.fetchone(
            "SELECT COUNT(*) as count FROM plans WHERE created_at >= ?",
            (datetime.now().replace(hour=0, minute=0, second=0).isoformat(),),
        )
        total_tasks = self.db.fetchone("SELECT COUNT(*) as count FROM plan_tasks")
        failed_tasks = self.db.fetchone("SELECT COUNT(*) as count FROM plan_tasks WHERE status = 'failed'")
        total_replans = self.db.fetchone("SELECT SUM(replan_count) as total FROM plans")

        return {
            "total_plans": total["count"] if total else 0,
            "active_plans": active["count"] if active else 0,
            "completed_plans": completed["count"] if completed else 0,
            "failed_plans": failed["count"] if failed else 0,
            "plans_today": today["count"] if today else 0,
            "total_tasks_executed": total_tasks["count"] if total_tasks else 0,
            "total_tasks_failed": failed_tasks["count"] if failed_tasks else 0,
            "total_replans": total_replans["total"] if total_replans["total"] else 0,
        }

    def cleanup_old_plans(self, days: int = 30, status: str = "completed") -> int:
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        rows = self.db.fetchall(
            "SELECT id FROM plans WHERE status = ? AND completed_at < ?",
            (status, cutoff),
        )
        deleted = 0
        for row in rows:
            self.delete_plan(row["id"])
            deleted += 1
        if deleted > 0:
            self.logger.info(f"Cleaned up {deleted} old {status} plans")
        return deleted
