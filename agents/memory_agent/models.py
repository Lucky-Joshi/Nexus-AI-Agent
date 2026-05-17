"""
Data models for NEXUS Memory Agent.
Defines structured types for memories, workflows, preferences, and context.
"""

import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class MemoryType(Enum):
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"
    USER_MEMORY = "user_memory"
    SYSTEM = "system"


class MemoryCategory(Enum):
    FACT = "fact"
    PREFERENCE = "preference"
    EVENT = "event"
    CONVERSATION = "conversation"
    WORKFLOW = "workflow"
    CONTEXT = "context"
    USER_DATA = "user_data"
    SYSTEM_CONFIG = "system_config"


@dataclass
class MemoryEntry:
    """Core memory unit with metadata for retrieval and importance scoring."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    content: str = ""
    memory_type: str = MemoryType.USER_MEMORY.value
    category: str = MemoryCategory.USER_DATA.value
    tags: List[str] = field(default_factory=list)
    importance: float = 0.5
    access_count: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryEntry":
        known_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in data.items() if k in known_fields}
        return cls(**filtered)

    def touch(self):
        """Update access count and timestamp."""
        self.access_count += 1
        self.updated_at = datetime.now().isoformat()


@dataclass
class WorkflowStep:
    """Single step in a workflow."""
    order: int = 0
    agent: str = ""
    command: str = ""
    description: str = ""
    params: Dict[str, Any] = field(default_factory=dict)
    timeout: int = 30

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Workflow:
    """Saved workflow with metadata."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    description: str = ""
    steps: List[WorkflowStep] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    usage_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["steps"] = [s.to_dict() if isinstance(s, WorkflowStep) else s for s in self.steps]
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Workflow":
        steps = [WorkflowStep(**s) if isinstance(s, dict) else s for s in data.get("steps", [])]
        known_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in data.items() if k in known_fields}
        filtered["steps"] = steps
        return cls(**filtered)

    def add_step(self, agent: str, command: str, description: str = "", params: Dict = None, timeout: int = 30):
        self.steps.append(WorkflowStep(
            order=len(self.steps),
            agent=agent,
            command=command,
            description=description,
            params=params or {},
            timeout=timeout,
        ))
        self.updated_at = datetime.now().isoformat()


@dataclass
class ContextMessage:
    """Single message in the context window."""
    role: str = ""
    content: str = ""
    session_id: str = ""
    agent: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    importance: float = 0.5

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ContextWindow:
    """Sliding context window with importance-based pruning."""
    session_id: str = ""
    messages: List[ContextMessage] = field(default_factory=list)
    max_size: int = 50
    max_tokens: int = 4000

    def add(self, role: str, content: str, agent: str = "", importance: float = 0.5):
        msg = ContextMessage(
            role=role,
            content=content,
            session_id=self.session_id,
            agent=agent,
            importance=importance,
        )
        self.messages.append(msg)
        self._prune()

    def get_messages(self, limit: int = None) -> List[Dict[str, str]]:
        msgs = self.messages[-limit:] if limit else self.messages
        return [{"role": m.role, "content": m.content} for m in msgs]

    def get_recent(self, n: int = 10) -> List[ContextMessage]:
        return self.messages[-n:]

    def clear(self):
        self.messages.clear()

    def size(self) -> int:
        return len(self.messages)

    def _prune(self):
        if len(self.messages) <= self.max_size:
            return

        self.messages.sort(key=lambda m: m.importance, reverse=True)
        self.messages = self.messages[:self.max_size]
        self.messages.sort(key=lambda m: m.timestamp)

    def estimate_tokens(self) -> int:
        return sum(len(m.content.split()) * 1.3 for m in self.messages)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "message_count": len(self.messages),
            "messages": [m.to_dict() for m in self.messages],
        }
