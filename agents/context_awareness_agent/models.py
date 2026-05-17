"""
Context Awareness Agent Models
Data structures for context detection, activity classification, and adaptive triggers.
"""

from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from typing import Optional, Dict, Any, List
import uuid


class ActivityType(Enum):
    CODING = "coding"
    BROWSING = "browsing"
    GAMING = "gaming"
    MEDIA = "media"
    COMMUNICATION = "communication"
    WRITING = "writing"
    STUDYING = "studying"
    DESIGN = "design"
    MEETING = "meeting"
    FILE_MANAGEMENT = "file_management"
    SYSTEM_ADMIN = "system_admin"
    IDLE = "idle"
    UNKNOWN = "unknown"


class ContextConfidence(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class FocusLevel(Enum):
    DEEP = "deep"
    FOCUSED = "focused"
    MODERATE = "moderate"
    DISTRACTED = "distracted"
    IDLE = "idle"


class TriggerAction(Enum):
    SUGGEST_WORKFLOW = "suggest_workflow"
    SILENCE_NOTIFICATIONS = "silence_notifications"
    ACTIVATE_MODE = "activate_mode"
    OPEN_APP = "open_app"
    CLOSE_APP = "close_app"
    SAVE_CONTEXT = "save_context"
    RESTORE_CONTEXT = "restore_context"
    ADAPT_PERSONALITY = "adapt_personality"
    RUN_SCRIPT = "run_script"
    NONE = "none"


@dataclass
class WindowContext:
    """Information about the currently active window."""
    title: str = ""
    process_name: str = ""
    pid: int = 0
    is_minimized: bool = False
    is_visible: bool = True
    duration_seconds: float = 0.0
    switch_count: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title[:100],
            "process_name": self.process_name,
            "pid": self.pid,
            "is_minimized": self.is_minimized,
            "is_visible": self.is_visible,
            "duration_seconds": round(self.duration_seconds, 1),
            "switch_count": self.switch_count,
            "timestamp": self.timestamp,
        }


@dataclass
class RunningApp:
    """Represents a running application."""
    name: str
    pid: int
    cpu_percent: float = 0.0
    memory_mb: float = 0.0
    status: str = "running"
    category: str = "unknown"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "pid": self.pid,
            "cpu_percent": round(self.cpu_percent, 1),
            "memory_mb": round(self.memory_mb, 1),
            "status": self.status,
            "category": self.category,
        }


@dataclass
class SystemLoad:
    """Current system load state."""
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    memory_used_gb: float = 0.0
    disk_percent: float = 0.0
    process_count: int = 0
    network_connections: int = 0
    level: str = "idle"
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cpu_percent": round(self.cpu_percent, 1),
            "memory_percent": round(self.memory_percent, 1),
            "memory_used_gb": round(self.memory_used_gb, 2),
            "disk_percent": round(self.disk_percent, 1),
            "process_count": self.process_count,
            "network_connections": self.network_connections,
            "level": self.level,
            "timestamp": self.timestamp,
        }


@dataclass
class TimeContext:
    """Time-based context information."""
    hour: int = 0
    minute: int = 0
    day_of_week: int = 0
    is_weekday: bool = True
    is_work_hours: bool = False
    period: str = "unknown"
    session_duration_minutes: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "hour": self.hour,
            "minute": self.minute,
            "day_of_week": self.day_of_week,
            "is_weekday": self.is_weekday,
            "is_work_hours": self.is_work_hours,
            "period": self.period,
            "session_duration_minutes": round(self.session_duration_minutes, 1),
        }


@dataclass
class UserContext:
    """Complete snapshot of the user's current context."""
    activity: ActivityType = ActivityType.UNKNOWN
    activity_confidence: ContextConfidence = ContextConfidence.LOW
    focus_level: FocusLevel = FocusLevel.IDLE
    active_window: Optional[WindowContext] = None
    running_apps: List[RunningApp] = field(default_factory=list)
    system_load: Optional[SystemLoad] = None
    time_context: Optional[TimeContext] = None
    session_type: str = "general"
    context_signals: List[str] = field(default_factory=list)
    suggested_actions: List[str] = field(default_factory=list)
    suggested_workflow: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "activity": self.activity.value,
            "activity_confidence": self.activity_confidence.value,
            "focus_level": self.focus_level.value,
            "active_window": self.active_window.to_dict() if self.active_window else None,
            "running_apps": [a.to_dict() for a in self.running_apps[:10]],
            "system_load": self.system_load.to_dict() if self.system_load else None,
            "time_context": self.time_context.to_dict() if self.time_context else None,
            "session_type": self.session_type,
            "context_signals": self.context_signals,
            "suggested_actions": self.suggested_actions,
            "suggested_workflow": self.suggested_workflow,
            "timestamp": self.timestamp,
        }


@dataclass
class ContextPattern:
    """A detected pattern in user behavior."""
    name: str
    description: str
    activity_type: ActivityType
    required_apps: List[str] = field(default_factory=list)
    time_pattern: str = ""
    min_duration_minutes: float = 5.0
    confidence: float = 0.0
    detection_count: int = 0
    last_detected: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "activity_type": self.activity_type.value,
            "required_apps": self.required_apps,
            "time_pattern": self.time_pattern,
            "min_duration_minutes": self.min_duration_minutes,
            "confidence": round(self.confidence, 2),
            "detection_count": self.detection_count,
            "last_detected": self.last_detected,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ContextPattern":
        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            name=data.get("name", ""),
            description=data.get("description", ""),
            activity_type=ActivityType(data.get("activity_type", "unknown")),
            required_apps=data.get("required_apps", []),
            time_pattern=data.get("time_pattern", ""),
            min_duration_minutes=data.get("min_duration_minutes", 5.0),
            confidence=data.get("confidence", 0.0),
            detection_count=data.get("detection_count", 0),
            last_detected=data.get("last_detected", ""),
            created_at=data.get("created_at", datetime.now().isoformat()),
        )


@dataclass
class AdaptiveTrigger:
    """A rule that triggers an action based on context."""
    name: str
    description: str = ""
    condition_activity: Optional[ActivityType] = None
    condition_apps: List[str] = field(default_factory=list)
    condition_time: str = ""
    condition_focus: Optional[FocusLevel] = None
    action: TriggerAction = TriggerAction.NONE
    action_target: str = ""
    action_params: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    trigger_count: int = 0
    last_triggered: str = ""
    cooldown_seconds: int = 300
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "condition_activity": self.condition_activity.value if self.condition_activity else None,
            "condition_apps": self.condition_apps,
            "condition_time": self.condition_time,
            "condition_focus": self.condition_focus.value if self.condition_focus else None,
            "action": self.action.value,
            "action_target": self.action_target,
            "action_params": self.action_params,
            "enabled": self.enabled,
            "trigger_count": self.trigger_count,
            "last_triggered": self.last_triggered,
            "cooldown_seconds": self.cooldown_seconds,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AdaptiveTrigger":
        activity = None
        if data.get("condition_activity"):
            activity = ActivityType(data["condition_activity"])
        focus = None
        if data.get("condition_focus"):
            focus = FocusLevel(data["condition_focus"])
        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            name=data.get("name", ""),
            description=data.get("description", ""),
            condition_activity=activity,
            condition_apps=data.get("condition_apps", []),
            condition_time=data.get("condition_time", ""),
            condition_focus=focus,
            action=TriggerAction(data.get("action", "none")),
            action_target=data.get("action_target", ""),
            action_params=data.get("action_params", {}),
            enabled=data.get("enabled", True),
            trigger_count=data.get("trigger_count", 0),
            last_triggered=data.get("last_triggered", ""),
            cooldown_seconds=data.get("cooldown_seconds", 300),
        )

    def matches_context(self, context: UserContext) -> bool:
        if not self.enabled:
            return False

        if self.condition_activity and context.activity != self.condition_activity:
            return False

        if self.condition_apps:
            app_names = [a.name.lower() for a in context.running_apps]
            if not any(app in app_names for app in self.condition_apps):
                return False

        if self.condition_focus and context.focus_level != self.condition_focus:
            return False

        if self.condition_time:
            hour = datetime.now().hour
            parts = self.condition_time.split("-")
            if len(parts) == 2:
                start, end = int(parts[0]), int(parts[1])
                if not (start <= hour < end):
                    return False

        return True


@dataclass
class ContextSnapshot:
    """Historical context snapshot for pattern analysis."""
    activity: str
    active_window_title: str = ""
    active_process: str = ""
    app_count: int = 0
    focus_level: str = "idle"
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    duration_seconds: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "activity": self.activity,
            "active_window_title": self.active_window_title[:100],
            "active_process": self.active_process,
            "app_count": self.app_count,
            "focus_level": self.focus_level,
            "cpu_percent": self.cpu_percent,
            "memory_percent": self.memory_percent,
            "duration_seconds": round(self.duration_seconds, 1),
            "timestamp": self.timestamp,
        }
