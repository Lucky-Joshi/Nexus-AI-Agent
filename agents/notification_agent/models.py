"""
Data models for NEXUS Notification Agent.
Defines structured types for notifications, queues, and alert management.
"""

import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class Priority(Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class NotificationType(Enum):
    SYSTEM = "system"
    TASK = "task"
    REMINDER = "reminder"
    AGENT_STATUS = "agent_status"
    WORKFLOW_COMPLETE = "workflow_complete"
    ERROR = "error"
    INFO = "info"
    WARNING = "warning"


class NotificationStatus(Enum):
    PENDING = "pending"
    SHOWING = "showing"
    DISMISSED = "dismissed"
    ACTIONED = "actioned"
    EXPIRED = "expired"


@dataclass
class NotificationAction:
    """An actionable button/callback for a notification."""
    label: str = ""
    action_id: str = ""
    callback_data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Notification:
    """Core notification unit with metadata for queue management."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str = ""
    message: str = ""
    notification_type: str = NotificationType.INFO.value
    priority: str = Priority.NORMAL.value
    status: str = NotificationStatus.PENDING.value
    source: str = ""
    actions: List[NotificationAction] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    scheduled_at: Optional[str] = None
    expires_at: Optional[str] = None
    dismissed_at: Optional[str] = None
    actioned_at: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_scheduled(self) -> bool:
        return self.scheduled_at is not None

    @property
    def is_expired(self) -> bool:
        if not self.expires_at:
            return False
        return datetime.now().isoformat() > self.expires_at

    @property
    def is_active(self) -> bool:
        return self.status in (NotificationStatus.PENDING.value, NotificationStatus.SHOWING.value)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["is_scheduled"] = self.is_scheduled
        d["is_expired"] = self.is_expired
        d["is_active"] = self.is_active
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Notification":
        known = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in data.items() if k in known}
        actions_data = filtered.pop("actions", [])
        filtered["actions"] = [NotificationAction(**a) if isinstance(a, dict) else a for a in actions_data]
        return cls(**filtered)

    def dismiss(self):
        self.status = NotificationStatus.DISMISSED.value
        self.dismissed_at = datetime.now().isoformat()

    def action(self, action_id: str):
        self.status = NotificationStatus.ACTIONED.value
        self.actioned_at = datetime.now().isoformat()
        self.metadata["actioned_id"] = action_id


@dataclass
class FocusModeConfig:
    """Configuration for focus/silent mode."""
    enabled: bool = False
    allow_critical: bool = True
    allow_from_sources: List[str] = field(default_factory=list)
    allow_from_types: List[str] = field(default_factory=list)
    quiet_hours_start: str = "22:00"
    quiet_hours_end: str = "08:00"
    quiet_hours_enabled: bool = False
    summary_interval_minutes: int = 30

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FocusModeConfig":
        known = {f.name for f in cls.__dataclass_fields__.values()}
        return cls(**{k: v for k, v in data.items() if k in known})


@dataclass
class NotificationSummary:
    """Summary of notifications during focus mode."""
    start_time: str = ""
    end_time: str = ""
    total_count: int = 0
    by_priority: Dict[str, int] = field(default_factory=dict)
    by_type: Dict[str, int] = field(default_factory=dict)
    notifications: List[Notification] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
