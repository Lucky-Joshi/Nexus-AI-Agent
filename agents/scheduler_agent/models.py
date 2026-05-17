"""
Data models for NEXUS Scheduler Agent.
Defines structured types for scheduled tasks, triggers, and execution history.
"""

import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class TriggerType(Enum):
    ONCE = "once"
    INTERVAL = "interval"
    CRON = "cron"
    DAILY = "daily"
    WEEKLY = "weekly"


class TaskStatus(Enum):
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


@dataclass
class Trigger:
    """Defines when a task should execute."""
    trigger_type: str = TriggerType.ONCE.value
    run_at: Optional[str] = None
    interval_seconds: Optional[int] = None
    cron_expression: Optional[str] = None
    daily_time: Optional[str] = None
    weekly_day: Optional[str] = None
    weekly_time: Optional[str] = None
    max_runs: int = 1
    runs_completed: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Trigger":
        known = {f.name for f in cls.__dataclass_fields__.values()}
        return cls(**{k: v for k, v in data.items() if k in known})


@dataclass
class ScheduledTask:
    """A task scheduled for future execution."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    command: str = ""
    description: str = ""
    trigger: Optional[Trigger] = None
    status: str = TaskStatus.SCHEDULED.value
    agent: str = ""
    params: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_run_at: Optional[str] = None
    next_run_at: Optional[str] = None
    last_result: Optional[str] = None
    error_message: Optional[str] = None
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        if self.trigger:
            d["trigger"] = self.trigger.to_dict()
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ScheduledTask":
        known = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in data.items() if k in known}
        trigger_data = filtered.pop("trigger", None)
        if trigger_data:
            filtered["trigger"] = Trigger.from_dict(trigger_data)
        return cls(**filtered)

    def mark_running(self):
        self.status = TaskStatus.RUNNING.value
        self.last_run_at = datetime.now().isoformat()

    def mark_completed(self, result: str = ""):
        self.status = TaskStatus.COMPLETED.value
        self.last_result = result
        if self.trigger:
            self.trigger.runs_completed += 1

    def mark_failed(self, error: str):
        self.status = TaskStatus.FAILED.value
        self.error_message = error
        if self.trigger:
            self.trigger.runs_completed += 1

    def should_run_again(self) -> bool:
        if not self.enabled:
            return False
        if not self.trigger:
            return False
        if self.trigger.max_runs > 0 and self.trigger.runs_completed >= self.trigger.max_runs:
            return False
        if self.status in (TaskStatus.CANCELLED.value, TaskStatus.PAUSED.value):
            return False
        return True


@dataclass
class ExecutionRecord:
    """Record of a task execution."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    task_id: str = ""
    task_name: str = ""
    started_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    status: str = TaskStatus.RUNNING.value
    result: Optional[str] = None
    error: Optional[str] = None
    duration_seconds: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExecutionRecord":
        known = {f.name for f in cls.__dataclass_fields__.values()}
        return cls(**{k: v for k, v in data.items() if k in known})
