"""
Workflow Chain Agent Storage
SQLite persistence for chain definitions, executions, templates, and recovery state.
"""

import sqlite3
import json
import os
from contextlib import contextmanager
from typing import List, Optional, Dict, Any
from pathlib import Path

from core.logger import Logger


class ChainStorage:
    """SQLite storage for workflow chain agent data."""

    def __init__(self, db_path: Optional[str] = None):
        self.logger = Logger().get_logger("ChainStorage")
        if db_path is None:
            db_path = os.path.join(
                Path(__file__).parent.parent.parent, "data", "workflow_chains.db"
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
                CREATE TABLE IF NOT EXISTS chain_definitions (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    version TEXT DEFAULT '1.0.0',
                    category TEXT DEFAULT 'general',
                    tags TEXT DEFAULT '[]',
                    definition TEXT NOT NULL,
                    timeout INTEGER DEFAULT 300,
                    max_concurrent INTEGER DEFAULT 3,
                    on_failure TEXT DEFAULT 'abort',
                    auto_retry INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    enabled INTEGER DEFAULT 1
                );

                CREATE TABLE IF NOT EXISTS chain_executions (
                    id TEXT PRIMARY KEY,
                    chain_id TEXT NOT NULL,
                    chain_name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    context TEXT DEFAULT '{}',
                    step_results TEXT DEFAULT '[]',
                    started_at TEXT NOT NULL,
                    completed_at TEXT DEFAULT '',
                    duration REAL DEFAULT 0.0,
                    total_steps INTEGER DEFAULT 0,
                    completed_steps INTEGER DEFAULT 0,
                    failed_steps INTEGER DEFAULT 0,
                    skipped_steps INTEGER DEFAULT 0,
                    error TEXT DEFAULT '',
                    FOREIGN KEY (chain_id) REFERENCES chain_definitions(id)
                );

                CREATE TABLE IF NOT EXISTS chain_templates (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    category TEXT NOT NULL,
                    tags TEXT DEFAULT '[]',
                    initial_variables TEXT DEFAULT '{}',
                    definition TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS chain_recovery (
                    id TEXT PRIMARY KEY,
                    execution_id TEXT NOT NULL,
                    chain_id TEXT NOT NULL,
                    checkpoint TEXT NOT NULL,
                    context TEXT NOT NULL,
                    step_results TEXT DEFAULT '[]',
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (execution_id) REFERENCES chain_executions(id)
                );

                CREATE INDEX IF NOT EXISTS idx_executions_chain ON chain_executions(chain_id);
                CREATE INDEX IF NOT EXISTS idx_executions_status ON chain_executions(status);
                CREATE INDEX IF NOT EXISTS idx_executions_started ON chain_executions(started_at);
                CREATE INDEX IF NOT EXISTS idx_recovery_execution ON chain_recovery(execution_id);
                CREATE INDEX IF NOT EXISTS idx_definitions_category ON chain_definitions(category);
                CREATE INDEX IF NOT EXISTS idx_definitions_enabled ON chain_definitions(enabled);
            """)
        self.logger.info(f"Chain storage initialized: {self.db_path}")

    def save_chain(self, chain_data: Dict[str, Any]) -> bool:
        with self._get_connection() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO chain_definitions
                   (id, name, description, version, category, tags, definition,
                    timeout, max_concurrent, on_failure, auto_retry, created_at, updated_at, enabled)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    chain_data["id"],
                    chain_data["name"],
                    chain_data.get("description", ""),
                    chain_data.get("version", "1.0.0"),
                    chain_data.get("category", "general"),
                    json.dumps(chain_data.get("tags", [])),
                    json.dumps(chain_data.get("steps", [])),
                    chain_data.get("timeout", 300),
                    chain_data.get("max_concurrent", 3),
                    chain_data.get("on_failure", "abort"),
                    1 if chain_data.get("auto_retry", False) else 0,
                    chain_data.get("created_at", ""),
                    chain_data.get("updated_at", ""),
                    1 if chain_data.get("enabled", True) else 0,
                ),
            )
            return True

    def get_chain(self, chain_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM chain_definitions WHERE id = ?", (chain_id,)
            ).fetchone()
            if row:
                return self._row_to_chain_dict(dict(row))
            return None

    def get_chain_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM chain_definitions WHERE name = ? AND enabled = 1", (name,)
            ).fetchone()
            if row:
                return self._row_to_chain_dict(dict(row))
            return None

    def get_chains(self, category: Optional[str] = None, enabled_only: bool = True) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            if category:
                rows = conn.execute(
                    "SELECT * FROM chain_definitions WHERE category = ? AND enabled = ? ORDER BY name",
                    (category, 1 if enabled_only else 0),
                ).fetchall()
            elif enabled_only:
                rows = conn.execute(
                    "SELECT * FROM chain_definitions WHERE enabled = 1 ORDER BY name"
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM chain_definitions ORDER BY name"
                ).fetchall()
            return [self._row_to_chain_dict(dict(r)) for r in rows]

    def delete_chain(self, chain_id: str) -> bool:
        with self._get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM chain_definitions WHERE id = ?", (chain_id,)
            )
            return cursor.rowcount > 0

    def save_execution(self, execution_data: Dict[str, Any]) -> bool:
        with self._get_connection() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO chain_executions
                   (id, chain_id, chain_name, status, context, step_results,
                    started_at, completed_at, duration, total_steps,
                    completed_steps, failed_steps, skipped_steps, error)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    execution_data["id"],
                    execution_data["chain_id"],
                    execution_data["chain_name"],
                    execution_data["status"],
                    json.dumps(execution_data.get("context", {})),
                    json.dumps(execution_data.get("step_results", [])),
                    execution_data["started_at"],
                    execution_data.get("completed_at", ""),
                    execution_data.get("duration", 0.0),
                    execution_data.get("total_steps", 0),
                    execution_data.get("completed_steps", 0),
                    execution_data.get("failed_steps", 0),
                    execution_data.get("skipped_steps", 0),
                    execution_data.get("error", ""),
                ),
            )
            return True

    def get_execution(self, execution_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM chain_executions WHERE id = ?", (execution_id,)
            ).fetchone()
            if row:
                return self._row_to_execution_dict(dict(row))
            return None

    def get_executions(self, chain_id: Optional[str] = None,
                       status: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            query = "SELECT * FROM chain_executions WHERE 1=1"
            params = []
            if chain_id:
                query += " AND chain_id = ?"
                params.append(chain_id)
            if status:
                query += " AND status = ?"
                params.append(status)
            query += " ORDER BY started_at DESC LIMIT ?"
            params.append(limit)

            rows = conn.execute(query, params).fetchall()
            return [self._row_to_execution_dict(dict(r)) for r in rows]

    def save_checkpoint(self, execution_id: str, chain_id: str,
                        checkpoint: str, context: Dict[str, Any],
                        step_results: List[Dict[str, Any]]) -> bool:
        with self._get_connection() as conn:
            from datetime import datetime
            conn.execute(
                """INSERT INTO chain_recovery
                   (id, execution_id, chain_id, checkpoint, context, step_results, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    f"{execution_id}_{checkpoint}",
                    execution_id,
                    chain_id,
                    checkpoint,
                    json.dumps(context),
                    json.dumps(step_results),
                    datetime.now().isoformat(),
                ),
            )
            return True

    def get_latest_checkpoint(self, execution_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM chain_recovery WHERE execution_id = ? ORDER BY created_at DESC LIMIT 1",
                (execution_id,),
            ).fetchone()
            if row:
                d = dict(row)
                d["context"] = json.loads(d.get("context", "{}"))
                d["step_results"] = json.loads(d.get("step_results", "[]"))
                return d
            return None

    def save_template(self, template_data: Dict[str, Any]) -> bool:
        with self._get_connection() as conn:
            from datetime import datetime
            conn.execute(
                """INSERT OR REPLACE INTO chain_templates
                   (id, name, description, category, tags, initial_variables, definition, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    template_data["id"],
                    template_data["name"],
                    template_data["description"],
                    template_data["category"],
                    json.dumps(template_data.get("tags", [])),
                    json.dumps(template_data.get("initial_variables", {})),
                    json.dumps(template_data.get("definition", {})),
                    template_data.get("created_at", datetime.now().isoformat()),
                ),
            )
            return True

    def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM chain_templates WHERE id = ?", (template_id,)
            ).fetchone()
            if row:
                d = dict(row)
                d["tags"] = json.loads(d.get("tags", "[]"))
                d["initial_variables"] = json.loads(d.get("initial_variables", "{}"))
                d["definition"] = json.loads(d.get("definition", "{}"))
                return d
            return None

    def get_templates(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            if category:
                rows = conn.execute(
                    "SELECT * FROM chain_templates WHERE category = ? ORDER BY name",
                    (category,),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM chain_templates ORDER BY name"
                ).fetchall()
            results = []
            for r in rows:
                d = dict(r)
                d["tags"] = json.loads(d.get("tags", "[]"))
                d["initial_variables"] = json.loads(d.get("initial_variables", "{}"))
                d["definition"] = json.loads(d.get("definition", "{}"))
                results.append(d)
            return results

    def delete_template(self, template_id: str) -> bool:
        with self._get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM chain_templates WHERE id = ?", (template_id,)
            )
            return cursor.rowcount > 0

    def get_stats(self) -> Dict[str, Any]:
        with self._get_connection() as conn:
            total_chains = conn.execute(
                "SELECT COUNT(*) FROM chain_definitions WHERE enabled = 1"
            ).fetchone()[0]
            total_executions = conn.execute(
                "SELECT COUNT(*) FROM chain_executions"
            ).fetchone()[0]
            completed = conn.execute(
                "SELECT COUNT(*) FROM chain_executions WHERE status = 'completed'"
            ).fetchone()[0]
            failed = conn.execute(
                "SELECT COUNT(*) FROM chain_executions WHERE status = 'failed'"
            ).fetchone()[0]
            running = conn.execute(
                "SELECT COUNT(*) FROM chain_executions WHERE status = 'running'"
            ).fetchone()[0]
            total_templates = conn.execute(
                "SELECT COUNT(*) FROM chain_templates"
            ).fetchone()[0]

            avg_duration = conn.execute(
                "SELECT AVG(duration) FROM chain_executions WHERE status = 'completed' AND duration > 0"
            ).fetchone()[0] or 0.0

            return {
                "total_chains": total_chains,
                "total_executions": total_executions,
                "completed_executions": completed,
                "failed_executions": failed,
                "running_executions": running,
                "total_templates": total_templates,
                "avg_duration_seconds": round(avg_duration, 2),
                "success_rate": round(completed / max(completed + failed, 1) * 100, 1),
            }

    @staticmethod
    def _row_to_chain_dict(row: Dict[str, Any]) -> Dict[str, Any]:
        d = dict(row)
        d["tags"] = json.loads(d.get("tags", "[]"))
        d["steps"] = json.loads(d.get("definition", "[]"))
        d["auto_retry"] = bool(d.get("auto_retry", 0))
        d["enabled"] = bool(d.get("enabled", 1))
        return d

    @staticmethod
    def _row_to_execution_dict(row: Dict[str, Any]) -> Dict[str, Any]:
        d = dict(row)
        d["context"] = json.loads(d.get("context", "{}"))
        d["step_results"] = json.loads(d.get("step_results", "[]"))
        return d
