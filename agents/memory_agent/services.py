"""
Service classes for NEXUS Memory Agent.
Each service handles a specific domain: memory, preferences, workflows, context.
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from core.logger import Logger
from core.config import Config

from .models import (
    MemoryEntry, MemoryType, MemoryCategory,
    Workflow, WorkflowStep,
    ContextWindow, ContextMessage,
)
from .storage import SQLiteStorage, JSONStorage, VectorStorage
from .retrieval import RetrievalPipeline


class MemoryService:
    """Core memory operations: store, retrieve, search, manage."""

    def __init__(self, sqlite_storage: SQLiteStorage = None, vector_storage: VectorStorage = None):
        self.logger = Logger().get_logger("MemoryService")
        self._sqlite = sqlite_storage or SQLiteStorage()
        self._vector = vector_storage or VectorStorage()
        self._retrieval = RetrievalPipeline()

    def save(self, content: str, memory_type: str = MemoryType.USER_MEMORY.value,
             category: str = MemoryCategory.USER_DATA.value, tags: List[str] = None,
             importance: float = None, metadata: Dict = None) -> MemoryEntry:
        """Save a new memory entry."""
        entry = MemoryEntry(
            content=content,
            memory_type=memory_type,
            category=category,
            tags=tags or [],
            importance=importance or 0.5,
            metadata=metadata or {},
        )

        self._sqlite.save_memory(
            entry.id, entry.content, entry.memory_type, entry.category,
            entry.tags, entry.importance, entry.metadata,
        )

        self._vector.add(entry.id, entry.content)

        self.logger.info(f"Memory saved: {entry.id} ({entry.memory_type}/{entry.category})")
        return entry

    def recall(self, memory_id: str) -> Optional[MemoryEntry]:
        """Recall a specific memory by ID."""
        data = self._sqlite.get_memory(memory_id)
        if not data:
            return None

        self._sqlite.update_memory_access(memory_id)
        entry = MemoryEntry.from_dict(data)
        entry.touch()
        return entry

    def search(self, query: str, memory_type: str = None, category: str = None,
               top_k: int = 10) -> List[MemoryEntry]:
        """Search memories using the retrieval pipeline."""
        candidates = self._sqlite.search_memories(query, memory_type, category, limit=top_k * 2)

        if not candidates:
            return []

        ranked = self._retrieval.retrieve(query, candidates, top_k=top_k,
                                           type_filter=memory_type, category_filter=category)

        return [MemoryEntry.from_dict(r) for r in ranked]

    def list_memories(self, memory_type: str = None, category: str = None,
                      limit: int = 50, offset: int = 0) -> List[MemoryEntry]:
        """List memories with optional filtering."""
        rows = self._sqlite.list_memories(memory_type, category, limit, offset)
        return [MemoryEntry.from_dict(r) for r in rows]

    def delete(self, memory_id: str) -> bool:
        """Delete a memory entry."""
        self._sqlite.delete_memory(memory_id)
        self.logger.info(f"Memory deleted: {memory_id}")
        return True

    def count(self, memory_type: str = None) -> int:
        """Count memories."""
        return self._sqlite.count_memories(memory_type)

    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        total = self._sqlite.count_memories()
        by_type = {}
        for mt in MemoryType:
            count = self._sqlite.count_memories(mt.value)
            if count > 0:
                by_type[mt.value] = count

        return {
            "total_memories": total,
            "by_type": by_type,
            "vector_index_size": self._vector.size(),
            "vector_search_available": self._vector.is_available(),
        }


class PreferenceService:
    """User preference management with JSON + SQLite dual storage."""

    def __init__(self, json_storage: JSONStorage = None, sqlite_storage: SQLiteStorage = None):
        self.logger = Logger().get_logger("PreferenceService")
        self._json = json_storage or JSONStorage()
        self._sqlite = sqlite_storage or SQLiteStorage()

    def get(self, key: str, default: Any = None) -> Any:
        """Get a preference. JSON storage is primary, SQLite is fallback."""
        value = self._json.get_preference(key)
        if value is not None:
            return value

        row = self._sqlite.fetchone("SELECT * FROM preferences WHERE key = ?", (key,))
        if row:
            return dict(row).get("value", default)
        return default

    def set(self, key: str, value: Any, category: str = "user"):
        """Save a preference to both JSON and SQLite."""
        self._json.set_preference(key, value)

        self._sqlite.execute(
            "INSERT OR REPLACE INTO preferences (key, value, updated_at) VALUES (?, ?, ?)",
            (key, str(value), datetime.now().isoformat()),
        )
        self.logger.info(f"Preference saved: {key} = {value}")

    def delete(self, key: str):
        """Delete a preference."""
        self._json.delete_preference(key)
        self._sqlite.execute("DELETE FROM preferences WHERE key = ?", (key,))
        self.logger.info(f"Preference deleted: {key}")

    def get_all(self) -> Dict[str, Any]:
        """Get all preferences."""
        json_prefs = self._json.load_preferences()

        rows = self._sqlite.fetchall("SELECT * FROM preferences")
        sqlite_prefs = {r["key"]: r["value"] for r in rows}

        merged = {**sqlite_prefs, **json_prefs}
        return merged

    def clear_all(self):
        """Clear all preferences."""
        self._json.save_preferences({})
        self._sqlite.execute("DELETE FROM preferences")
        self.logger.info("All preferences cleared")


class WorkflowService:
    """Workflow management: create, save, load, execute."""

    def __init__(self, sqlite_storage: SQLiteStorage = None, json_storage: JSONStorage = None):
        self.logger = Logger().get_logger("WorkflowService")
        self._sqlite = sqlite_storage or SQLiteStorage()
        self._json = json_storage or JSONStorage()

    def create(self, name: str, description: str = "", tags: List[str] = None) -> Workflow:
        """Create a new workflow."""
        return Workflow(name=name, description=description, tags=tags or [])

    def save(self, workflow: Workflow) -> str:
        """Save workflow to both SQLite and JSON."""
        workflow.updated_at = datetime.now().isoformat()
        steps_data = [s.to_dict() for s in workflow.steps]

        self._sqlite.save_workflow(
            workflow.id, workflow.name, workflow.description,
            steps_data, workflow.tags,
        )
        self._json.save_workflow_json(workflow.id, workflow.to_dict())

        self.logger.info(f"Workflow saved: {workflow.id} ({workflow.name})")
        return workflow.id

    def load(self, workflow_id: str) -> Optional[Workflow]:
        """Load a workflow by ID."""
        data = self._sqlite.get_workflow(workflow_id)
        if not data:
            data = self._json.get_workflow_json(workflow_id)
        if not data:
            return None

        workflow = Workflow.from_dict(data)
        return workflow

    def load_by_name(self, name: str) -> Optional[Workflow]:
        """Load a workflow by name."""
        data = self._sqlite.get_workflow_by_name(name)
        if not data:
            all_workflows = self._json.load_workflows()
            for wf_data in all_workflows.values():
                if wf_data.get("name", "").lower() == name.lower():
                    data = wf_data
                    break
        if not data:
            return None

        return Workflow.from_dict(data)

    def list_workflows(self, limit: int = 50) -> List[Workflow]:
        """List all saved workflows."""
        rows = self._sqlite.list_workflows(limit)
        return [Workflow.from_dict(r) for r in rows]

    def delete(self, workflow_id: str):
        """Delete a workflow."""
        self._sqlite.delete_workflow(workflow_id)
        self._json.delete_workflow_json(workflow_id)
        self.logger.info(f"Workflow deleted: {workflow_id}")

    def record_execution(self, workflow_id: str):
        """Increment workflow usage count."""
        self._sqlite.increment_workflow_usage(workflow_id)
        workflow = self.load(workflow_id)
        if workflow:
            workflow.usage_count += 1
            self.save(workflow)

    def get_execution_plan(self, workflow: Workflow) -> List[Dict[str, Any]]:
        """Convert workflow to execution plan for the AI Manager."""
        return [
            {
                "step": s.order,
                "agent": s.agent,
                "command": s.command,
                "description": s.description,
                "params": s.params,
                "timeout": s.timeout,
            }
            for s in workflow.steps
        ]


class ContextManager:
    """
    Manages conversation context with sliding window and importance-based pruning.
    Provides context for LLM prompts and memory-augmented responses.
    """

    def __init__(self, max_size: int = 50, max_tokens: int = 4000):
        self.logger = Logger().get_logger("ContextManager")
        self._windows: Dict[str, ContextWindow] = {}
        self._default_max_size = max_size
        self._default_max_tokens = max_tokens

    def get_window(self, session_id: str) -> ContextWindow:
        """Get or create a context window for a session."""
        if session_id not in self._windows:
            self._windows[session_id] = ContextWindow(
                session_id=session_id,
                max_size=self._default_max_size,
                max_tokens=self._default_max_tokens,
            )
        return self._windows[session_id]

    def add_message(self, session_id: str, role: str, content: str,
                    agent: str = "", importance: float = 0.5):
        """Add a message to the context window."""
        window = self.get_window(session_id)
        window.add(role, content, agent, importance)

    def get_context(self, session_id: str, limit: int = None) -> List[Dict[str, str]]:
        """Get context messages for a session."""
        window = self.get_window(session_id)
        return window.get_messages(limit)

    def get_recent(self, session_id: str, n: int = 10) -> List[ContextMessage]:
        """Get the most recent messages."""
        window = self.get_window(session_id)
        return window.get_recent(n)

    def build_llm_context(self, session_id: str, system_prompt: str = None,
                          max_messages: int = 20) -> List[Dict[str, str]]:
        """
        Build context for LLM API calls.
        Returns: [system, ...messages]
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        window = self.get_window(session_id)
        recent = window.get_messages(limit=max_messages)
        messages.extend(recent)

        return messages

    def summarize_context(self, session_id: str) -> str:
        """Generate a text summary of the current context."""
        window = self.get_window(session_id)
        if window.size() == 0:
            return "No conversation history."

        lines = [f"Session {session_id} ({window.size()} messages):"]
        for msg in window.get_recent(10):
            preview = msg.content[:100]
            lines.append(f"  [{msg.role}] {preview}")

        return "\n".join(lines)

    def clear_session(self, session_id: str):
        """Clear context for a specific session."""
        if session_id in self._windows:
            self._windows[session_id].clear()
            self.logger.info(f"Context cleared for session: {session_id}")

    def clear_all(self):
        """Clear all context windows."""
        for window in self._windows.values():
            window.clear()
        self._windows.clear()
        self.logger.info("All context windows cleared")

    def get_active_sessions(self) -> List[str]:
        """Get list of sessions with active context."""
        return [sid for sid, w in self._windows.items() if w.size() > 0]

    def get_stats(self) -> Dict[str, Any]:
        """Get context manager statistics."""
        return {
            "active_sessions": len(self._windows),
            "total_messages": sum(w.size() for w in self._windows.values()),
            "sessions": {
                sid: {"messages": w.size(), "tokens": int(w.estimate_tokens())}
                for sid, w in self._windows.items()
            },
        }
