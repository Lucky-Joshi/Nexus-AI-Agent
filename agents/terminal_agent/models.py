"""
Data models for the Terminal Agent.
Defines terminal sessions, command records, and execution status.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class CommandStatus(Enum):
    """Status of a command execution."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    TIMEOUT = "timeout"
    KILLED = "killed"


class SessionStatus(Enum):
    """Status of a terminal session."""
    ACTIVE = "active"
    IDLE = "idle"
    CLOSED = "closed"
    ERROR = "error"


@dataclass
class CommandRecord:
    """Record of a single command execution."""
    command: str
    session_id: str = ""
    status: CommandStatus = CommandStatus.PENDING
    output: str = ""
    error: str = ""
    exit_code: int = -1
    started_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: str = ""
    duration_seconds: float = 0.0
    working_directory: str = ""
    is_safe: bool = True
    safety_reason: str = ""
    stream_mode: bool = False

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "command": self.command,
            "session_id": self.session_id,
            "status": self.status.value,
            "output": self.output,
            "error": self.error,
            "exit_code": self.exit_code,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "duration_seconds": self.duration_seconds,
            "working_directory": self.working_directory,
            "is_safe": self.is_safe,
            "safety_reason": self.safety_reason,
            "stream_mode": self.stream_mode,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CommandRecord":
        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            command=data["command"],
            session_id=data.get("session_id", ""),
            status=CommandStatus(data.get("status", "pending")),
            output=data.get("output", ""),
            error=data.get("error", ""),
            exit_code=data.get("exit_code", -1),
            started_at=data.get("started_at", datetime.now().isoformat()),
            completed_at=data.get("completed_at", ""),
            duration_seconds=data.get("duration_seconds", 0.0),
            working_directory=data.get("working_directory", ""),
            is_safe=data.get("is_safe", True),
            safety_reason=data.get("safety_reason", ""),
            stream_mode=data.get("stream_mode", False),
        )

    def mark_running(self):
        self.status = CommandStatus.RUNNING
        self.started_at = datetime.now().isoformat()

    def mark_completed(self, exit_code: int = 0, output: str = ""):
        self.status = CommandStatus.COMPLETED
        self.exit_code = exit_code
        self.output = output
        self.completed_at = datetime.now().isoformat()
        self._calc_duration()

    def mark_failed(self, error: str = "", exit_code: int = 1):
        self.status = CommandStatus.FAILED
        self.exit_code = exit_code
        self.error = error
        self.completed_at = datetime.now().isoformat()
        self._calc_duration()

    def mark_blocked(self, reason: str = ""):
        self.status = CommandStatus.BLOCKED
        self.is_safe = False
        self.safety_reason = reason
        self.completed_at = datetime.now().isoformat()

    def mark_timeout(self):
        self.status = CommandStatus.TIMEOUT
        self.completed_at = datetime.now().isoformat()
        self._calc_duration()

    def mark_killed(self):
        self.status = CommandStatus.KILLED
        self.completed_at = datetime.now().isoformat()
        self._calc_duration()

    def _calc_duration(self):
        try:
            start = datetime.fromisoformat(self.started_at)
            end = datetime.fromisoformat(self.completed_at)
            self.duration_seconds = (end - start).total_seconds()
        except Exception:
            self.duration_seconds = 0.0


@dataclass
class TerminalSession:
    """Represents a terminal session with state and history."""
    name: str
    working_directory: str = ""
    status: SessionStatus = SessionStatus.IDLE
    environment: Dict[str, str] = field(default_factory=dict)
    command_history: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_active: str = field(default_factory=lambda: datetime.now().isoformat())
    max_history: int = 100

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "working_directory": self.working_directory,
            "status": self.status.value,
            "environment": self.environment,
            "command_history": self.command_history,
            "created_at": self.created_at,
            "last_active": self.last_active,
            "max_history": self.max_history,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TerminalSession":
        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            name=data["name"],
            working_directory=data.get("working_directory", ""),
            status=SessionStatus(data.get("status", "idle")),
            environment=data.get("environment", {}),
            command_history=data.get("command_history", []),
            created_at=data.get("created_at", datetime.now().isoformat()),
            last_active=data.get("last_active", datetime.now().isoformat()),
            max_history=data.get("max_history", 100),
        )

    def touch(self):
        self.last_active = datetime.now().isoformat()

    def add_to_history(self, command: str):
        self.command_history.append(command)
        if len(self.command_history) > self.max_history:
            self.command_history = self.command_history[-self.max_history:]

    def get_recent_commands(self, n: int = 10) -> List[str]:
        return self.command_history[-n:]
