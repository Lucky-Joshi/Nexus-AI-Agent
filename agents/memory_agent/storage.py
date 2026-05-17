"""
Storage layer for NEXUS Memory Agent.
Provides SQLite, JSON, and vector-ready storage backends.
"""

import json
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.logger import Logger
from core.config import Config


class SQLiteStorage:
    """SQLite backend for structured memory data."""

    def __init__(self, db_path: Optional[str] = None):
        self.logger = Logger().get_logger("SQLiteStorage")
        if not db_path:
            config = Config()
            db_path = config.get("database.path", "data/nexus.db")
        self._db_path = str(Path(__file__).parent.parent.parent / db_path)
        os.makedirs(os.path.dirname(self._db_path), exist_ok=True)
        self._initialize()

    def _initialize(self):
        with self._get_connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    memory_type TEXT DEFAULT 'user_memory',
                    category TEXT DEFAULT 'user_data',
                    tags TEXT DEFAULT '[]',
                    importance REAL DEFAULT 0.5,
                    access_count INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT DEFAULT '{}'
                );

                CREATE INDEX IF NOT EXISTS idx_memories_type ON memories(memory_type);
                CREATE INDEX IF NOT EXISTS idx_memories_category ON memories(category);
                CREATE INDEX IF NOT EXISTS idx_memories_importance ON memories(importance DESC);
                CREATE INDEX IF NOT EXISTS idx_memories_updated ON memories(updated_at DESC);

                CREATE TABLE IF NOT EXISTS memory_workflows (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    steps TEXT NOT NULL,
                    tags TEXT DEFAULT '[]',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    usage_count INTEGER DEFAULT 0
                );

                CREATE INDEX IF NOT EXISTS idx_wf_name ON memory_workflows(name);

                CREATE TABLE IF NOT EXISTS conversation_sessions (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    messages TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE INDEX IF NOT EXISTS idx_sessions_id ON conversation_sessions(session_id);
            """)

            try:
                conn.execute("ALTER TABLE memories ADD COLUMN updated_at TEXT DEFAULT CURRENT_TIMESTAMP")
            except Exception:
                pass
            try:
                conn.execute("ALTER TABLE memories ADD COLUMN metadata TEXT DEFAULT '{}'")
            except Exception:
                pass
            try:
                conn.execute("ALTER TABLE memories ADD COLUMN access_count INTEGER DEFAULT 0")
            except Exception:
                pass
        self.logger.info(f"SQLite storage initialized: {self._db_path}")

    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def save_memory(self, memory_id: str, content: str, memory_type: str, category: str,
                    tags: List[str], importance: float, metadata: Dict = None) -> str:
        self.execute(
            """INSERT OR REPLACE INTO memories
               (id, content, memory_type, category, tags, importance, metadata, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (memory_id, content, memory_type, category, json.dumps(tags),
             importance, json.dumps(metadata or {}), datetime.now().isoformat()),
        )
        return memory_id

    def get_memory(self, memory_id: str) -> Optional[Dict]:
        row = self.fetchone("SELECT * FROM memories WHERE id = ?", (memory_id,))
        return self._row_to_dict(row)

    def search_memories(self, query: str, memory_type: str = None, category: str = None,
                        limit: int = 20) -> List[Dict]:
        conditions = []
        params = []

        if query:
            terms = query.split()
            term_conditions = []
            for term in terms:
                term_conditions.append("(content LIKE ? OR tags LIKE ? OR metadata LIKE ?)")
                params.extend([f"%{term}%", f"%{term}%", f"%{term}%"])
            conditions.append("(" + " AND ".join(term_conditions) + ")")
        if memory_type:
            conditions.append("memory_type = ?")
            params.append(memory_type)
        if category:
            conditions.append("category = ?")
            params.append(category)

        where = " AND ".join(conditions) if conditions else "1=1"
        rows = self.fetchall(
            f"SELECT * FROM memories WHERE {where} ORDER BY importance DESC, updated_at DESC LIMIT ?",
            params + [limit],
        )
        return [self._row_to_dict(r) for r in rows]

    def update_memory_access(self, memory_id: str):
        self.execute(
            """UPDATE memories SET access_count = access_count + 1, updated_at = ?
               WHERE id = ?""",
            (datetime.now().isoformat(), memory_id),
        )

    def delete_memory(self, memory_id: str):
        self.execute("DELETE FROM memories WHERE id = ?", (memory_id,))

    def list_memories(self, memory_type: str = None, category: str = None,
                      limit: int = 100, offset: int = 0) -> List[Dict]:
        conditions = []
        params = []
        if memory_type:
            conditions.append("memory_type = ?")
            params.append(memory_type)
        if category:
            conditions.append("category = ?")
            params.append(category)

        where = " AND ".join(conditions) if conditions else "1=1"
        rows = self.fetchall(
            f"SELECT * FROM memories WHERE {where} ORDER BY updated_at DESC LIMIT ? OFFSET ?",
            params + [limit, offset],
        )
        return [self._row_to_dict(r) for r in rows]

    def count_memories(self, memory_type: str = None) -> int:
        if memory_type:
            row = self.fetchone("SELECT COUNT(*) as cnt FROM memories WHERE memory_type = ?", (memory_type,))
        else:
            row = self.fetchone("SELECT COUNT(*) as cnt FROM memories")
        return row["cnt"] if row else 0

    def save_workflow(self, workflow_id: str, name: str, description: str,
                      steps: List[Dict], tags: List[str]) -> str:
        self.execute(
            """INSERT OR REPLACE INTO memory_workflows
               (id, name, description, steps, tags, updated_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (workflow_id, name, description, json.dumps(steps),
             json.dumps(tags), datetime.now().isoformat()),
        )
        return workflow_id

    def get_workflow(self, workflow_id: str) -> Optional[Dict]:
        row = self.fetchone("SELECT * FROM memory_workflows WHERE id = ?", (workflow_id,))
        return self._row_to_dict(row)

    def get_workflow_by_name(self, name: str) -> Optional[Dict]:
        row = self.fetchone("SELECT * FROM memory_workflows WHERE name = ?", (name,))
        return self._row_to_dict(row)

    def list_workflows(self, limit: int = 50) -> List[Dict]:
        rows = self.fetchall("SELECT * FROM memory_workflows ORDER BY updated_at DESC LIMIT ?", (limit,))
        return [self._row_to_dict(r) for r in rows]

    def increment_workflow_usage(self, workflow_id: str):
        self.execute(
            "UPDATE memory_workflows SET usage_count = usage_count + 1, updated_at = ? WHERE id = ?",
            (datetime.now().isoformat(), workflow_id),
        )

    def delete_workflow(self, workflow_id: str):
        self.execute("DELETE FROM memory_workflows WHERE id = ?", (workflow_id,))

    def save_session(self, session_id: str, messages: List[Dict]):
        self.execute(
            """INSERT OR REPLACE INTO conversation_sessions
               (id, session_id, messages, updated_at)
               VALUES (?, ?, ?, ?)""",
            (session_id, session_id, json.dumps(messages), datetime.now().isoformat()),
        )

    def get_session(self, session_id: str) -> Optional[List[Dict]]:
        row = self.fetchone("SELECT * FROM conversation_sessions WHERE session_id = ?", (session_id,))
        if row:
            data = self._row_to_dict(row)
            return json.loads(data.get("messages", "[]"))
        return None

    def delete_session(self, session_id: str):
        self.execute("DELETE FROM conversation_sessions WHERE session_id = ?", (session_id,))

    def execute(self, query: str, params: tuple = ()):
        with self._get_connection() as conn:
            return conn.execute(query, params)

    def fetchone(self, query: str, params: tuple = ()) -> Optional[sqlite3.Row]:
        with self._get_connection() as conn:
            return conn.execute(query, params).fetchone()

    def fetchall(self, query: str, params: tuple = ()) -> list:
        with self._get_connection() as conn:
            return conn.execute(query, params).fetchall()

    def _row_to_dict(self, row) -> Optional[Dict]:
        if not row:
            return None
        d = dict(row)
        if "tags" in d and isinstance(d["tags"], str):
            try:
                d["tags"] = json.loads(d["tags"])
            except (json.JSONDecodeError, TypeError):
                d["tags"] = []
        if "metadata" in d and isinstance(d["metadata"], str):
            try:
                d["metadata"] = json.loads(d["metadata"])
            except (json.JSONDecodeError, TypeError):
                d["metadata"] = {}
        if "steps" in d and isinstance(d["steps"], str):
            try:
                d["steps"] = json.loads(d["steps"])
            except (json.JSONDecodeError, TypeError):
                d["steps"] = []
        return d

    @property
    def db_path(self) -> str:
        return self._db_path


class JSONStorage:
    """JSON file backend for preferences and lightweight config."""

    def __init__(self, storage_dir: Optional[str] = None):
        self.logger = Logger().get_logger("JSONStorage")
        if not storage_dir:
            storage_dir = str(Path(__file__).parent.parent.parent / "data" / "memory")
        self._storage_dir = storage_dir
        os.makedirs(self._storage_dir, exist_ok=True)
        self._preferences_path = os.path.join(self._storage_dir, "preferences.json")
        self._workflows_path = os.path.join(self._storage_dir, "workflows.json")
        self._initialize_files()

    def _initialize_files(self):
        for path in [self._preferences_path, self._workflows_path]:
            if not os.path.exists(path):
                with open(path, "w") as f:
                    json.dump({}, f, indent=2)
        self.logger.info(f"JSON storage initialized: {self._storage_dir}")

    def save_preferences(self, preferences: Dict[str, Any]):
        with open(self._preferences_path, "w") as f:
            json.dump(preferences, f, indent=2)

    def load_preferences(self) -> Dict[str, Any]:
        try:
            with open(self._preferences_path, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def get_preference(self, key: str, default: Any = None) -> Any:
        prefs = self.load_preferences()
        return prefs.get(key, default)

    def set_preference(self, key: str, value: Any):
        prefs = self.load_preferences()
        prefs[key] = value
        self.save_preferences(prefs)

    def delete_preference(self, key: str):
        prefs = self.load_preferences()
        prefs.pop(key, None)
        self.save_preferences(prefs)

    def save_workflows(self, workflows: Dict[str, Any]):
        with open(self._workflows_path, "w") as f:
            json.dump(workflows, f, indent=2)

    def load_workflows(self) -> Dict[str, Any]:
        try:
            with open(self._workflows_path, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def get_workflow_json(self, workflow_id: str) -> Optional[Dict]:
        workflows = self.load_workflows()
        return workflows.get(workflow_id)

    def save_workflow_json(self, workflow_id: str, data: Dict):
        workflows = self.load_workflows()
        workflows[workflow_id] = data
        self.save_workflows(workflows)

    def delete_workflow_json(self, workflow_id: str):
        workflows = self.load_workflows()
        workflows.pop(workflow_id, None)
        self.save_workflows(workflows)

    @property
    def storage_dir(self) -> str:
        return self._storage_dir


class VectorStorage:
    """
    Vector storage backend for semantic similarity search.
    Currently a stub — ready for integration with FAISS, ChromaDB, or similar.
    """

    def __init__(self, storage_dir: Optional[str] = None, embedding_model: str = "local"):
        self.logger = Logger().get_logger("VectorStorage")
        self._available = False
        self._storage_dir = storage_dir or str(Path(__file__).parent.parent.parent / "data" / "vectors")
        self._embedding_model = embedding_model
        self._index = None
        self._documents: Dict[str, str] = {}
        self.logger.info("Vector storage initialized (semantic search not yet enabled)")

    def is_available(self) -> bool:
        return self._available

    def enable(self, backend: str = "faiss"):
        """Enable vector storage with the specified backend."""
        try:
            if backend == "faiss":
                import faiss
                self._index = faiss.IndexFlatL2(384)
                self._available = True
                self.logger.info("FAISS vector storage enabled")
            else:
                self.logger.warning(f"Unknown vector backend: {backend}")
        except ImportError:
            self.logger.warning(f"Backend '{backend}' not available. Install with: pip install faiss-cpu")

    def add(self, memory_id: str, text: str, embedding: Optional[List[float]] = None):
        if not self._available:
            self._documents[memory_id] = text
            return
        if embedding is None:
            embedding = self._compute_embedding(text)
        self._index.add([embedding])
        self._documents[memory_id] = text

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        if not self._available:
            return self._fallback_search(query, top_k)

        embedding = self._compute_embedding(query)
        distances, indices = self._index.search([embedding], top_k)

        results = []
        doc_ids = list(self._documents.keys())
        for i, idx in enumerate(indices[0]):
            if idx < len(doc_ids):
                results.append({
                    "id": doc_ids[idx],
                    "content": self._documents[doc_ids[idx]],
                    "score": float(1.0 - distances[0][i]),
                })
        return results

    def _compute_embedding(self, text: str) -> List[float]:
        """Placeholder — replace with actual embedding model."""
        import hashlib
        h = hashlib.sha256(text.encode()).digest()
        return [float(b) / 255.0 for b in h[:384]]

    def _fallback_search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Simple keyword-based fallback when vector search is unavailable."""
        query_words = set(query.lower().split())
        scored = []
        for mid, text in self._documents.items():
            words = set(text.lower().split())
            overlap = len(query_words & words)
            if overlap > 0:
                scored.append({
                    "id": mid,
                    "content": text,
                    "score": overlap / len(query_words),
                })
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]

    def size(self) -> int:
        return len(self._documents)

    def clear(self):
        self._documents.clear()
        if self._index is not None:
            import faiss
            dim = self._index.d
            self._index = faiss.IndexFlatL2(dim)
