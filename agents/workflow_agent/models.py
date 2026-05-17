"""
Data models for the Workflow Mode Agent.
Defines workflow modes, actions, states, and execution records.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class ModeStatus(Enum):
    """Status of a workflow mode."""
    IDLE = "idle"
    ACTIVATING = "activating"
    ACTIVE = "active"
    DEACTIVATING = "deactivating"
    PAUSED = "paused"
    ERROR = "error"
    CANCELLED = "cancelled"


class ActionType(Enum):
    """Types of actions a mode can execute."""
    LAUNCH_APP = "launch_app"
    CLOSE_APP = "close_app"
    OPEN_URL = "open_url"
    OPEN_FILE = "open_file"
    OPEN_FOLDER = "open_folder"
    RUN_COMMAND = "run_command"
    ACTIVATE_AGENT = "activate_agent"
    DEACTIVATE_AGENT = "deactivate_agent"
    SET_NOTIFICATIONS = "set_notifications"
    SET_FOCUS_MODE = "set_focus_mode"
    START_TIMER = "start_timer"
    STOP_TIMER = "stop_timer"
    CREATE_FILE = "create_file"
    CREATE_FOLDER = "create_folder"
    SET_ENVIRONMENT = "set_environment"
    KILL_PROCESS = "kill_process"
    WAIT = "wait"
    CONDITIONAL = "conditional"
    CUSTOM = "custom"


class ActionStatus(Enum):
    """Status of a single action execution."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"


class ConditionType(Enum):
    """Condition types for conditional actions."""
    APP_RUNNING = "app_running"
    APP_NOT_RUNNING = "app_not_running"
    SYSTEM_MEMORY_HIGH = "system_memory_high"
    SYSTEM_CPU_HIGH = "system_cpu_high"
    FOCUS_MODE_ACTIVE = "focus_mode_active"
    TIME_OF_DAY = "time_of_day"
    CUSTOM = "custom"


@dataclass
class ModeCondition:
    """Condition that must be met for an action to execute."""
    type: ConditionType
    value: str = ""
    threshold: float = 0.0
    invert: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type.value,
            "value": self.value,
            "threshold": self.threshold,
            "invert": self.invert,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModeCondition":
        return cls(
            type=ConditionType(data.get("type", "custom")),
            value=data.get("value", ""),
            threshold=data.get("threshold", 0.0),
            invert=data.get("invert", False),
        )


@dataclass
class ModeAction:
    """A single action within a workflow mode."""
    action_type: ActionType
    name: str = ""
    target: str = ""
    params: Dict[str, Any] = field(default_factory=dict)
    condition: Optional[ModeCondition] = None
    timeout: int = 30
    retry_count: int = 0
    max_retries: int = 1
    on_failure: str = "continue"
    order: int = 0
    parallel: bool = False
    group: str = ""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    status: ActionStatus = ActionStatus.PENDING
    error: str = ""
    started_at: str = ""
    completed_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "action_type": self.action_type.value,
            "name": self.name,
            "target": self.target,
            "params": self.params,
            "condition": self.condition.to_dict() if self.condition else None,
            "timeout": self.timeout,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "on_failure": self.on_failure,
            "order": self.order,
            "parallel": self.parallel,
            "group": self.group,
            "status": self.status.value,
            "error": self.error,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModeAction":
        condition = None
        if data.get("condition"):
            condition = ModeCondition.from_dict(data["condition"])
        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            action_type=ActionType(data.get("action_type", "custom")),
            name=data.get("name", ""),
            target=data.get("target", ""),
            params=data.get("params", {}),
            condition=condition,
            timeout=data.get("timeout", 30),
            retry_count=data.get("retry_count", 0),
            max_retries=data.get("max_retries", 1),
            on_failure=data.get("on_failure", "continue"),
            order=data.get("order", 0),
            parallel=data.get("parallel", False),
            group=data.get("group", ""),
            status=ActionStatus(data.get("status", "pending")),
            error=data.get("error", ""),
            started_at=data.get("started_at", ""),
            completed_at=data.get("completed_at", ""),
        )


@dataclass
class WorkflowMode:
    """A complete workflow mode definition."""
    name: str
    description: str = ""
    icon: str = ""
    category: str = "productivity"
    actions: List[ModeAction] = field(default_factory=list)
    agents_to_activate: List[str] = field(default_factory=list)
    agents_to_deactivate: List[str] = field(default_factory=list)
    apps_to_launch: List[str] = field(default_factory=list)
    apps_to_close: List[str] = field(default_factory=list)
    urls_to_open: List[str] = field(default_factory=list)
    notifications_mode: str = "normal"
    focus_mode: bool = False
    timer_duration: int = 0
    custom_startup: str = ""
    custom_shutdown: str = ""
    priority: int = 0
    system_requirements: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    enabled: bool = True
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "icon": self.icon,
            "category": self.category,
            "actions": [a.to_dict() for a in self.actions],
            "agents_to_activate": self.agents_to_activate,
            "agents_to_deactivate": self.agents_to_deactivate,
            "apps_to_launch": self.apps_to_launch,
            "apps_to_close": self.apps_to_close,
            "urls_to_open": self.urls_to_open,
            "notifications_mode": self.notifications_mode,
            "focus_mode": self.focus_mode,
            "timer_duration": self.timer_duration,
            "custom_startup": self.custom_startup,
            "custom_shutdown": self.custom_shutdown,
            "priority": self.priority,
            "system_requirements": self.system_requirements,
            "tags": self.tags,
            "enabled": self.enabled,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkflowMode":
        actions = [ModeAction.from_dict(a) for a in data.get("actions", [])]
        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            name=data["name"],
            description=data.get("description", ""),
            icon=data.get("icon", ""),
            category=data.get("category", "productivity"),
            actions=actions,
            agents_to_activate=data.get("agents_to_activate", []),
            agents_to_deactivate=data.get("agents_to_deactivate", []),
            apps_to_launch=data.get("apps_to_launch", []),
            apps_to_close=data.get("apps_to_close", []),
            urls_to_open=data.get("urls_to_open", []),
            notifications_mode=data.get("notifications_mode", "normal"),
            focus_mode=data.get("focus_mode", False),
            timer_duration=data.get("timer_duration", 0),
            custom_startup=data.get("custom_startup", ""),
            custom_shutdown=data.get("custom_shutdown", ""),
            priority=data.get("priority", 0),
            system_requirements=data.get("system_requirements", {}),
            tags=data.get("tags", []),
            enabled=data.get("enabled", True),
            created_at=data.get("created_at", datetime.now().isoformat()),
            updated_at=data.get("updated_at", datetime.now().isoformat()),
        )


@dataclass
class ModeState:
    """Runtime state of an active mode."""
    mode_id: str = ""
    mode_name: str = ""
    status: ModeStatus = ModeStatus.IDLE
    started_at: str = ""
    activated_at: str = ""
    progress: float = 0.0
    total_actions: int = 0
    completed_actions: int = 0
    failed_actions: int = 0
    skipped_actions: int = 0
    launched_apps: List[str] = field(default_factory=list)
    activated_agents: List[str] = field(default_factory=list)
    previous_notification_state: str = "normal"
    previous_focus_state: bool = False
    error: str = ""
    action_states: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mode_id": self.mode_id,
            "mode_name": self.mode_name,
            "status": self.status.value,
            "started_at": self.started_at,
            "activated_at": self.activated_at,
            "progress": self.progress,
            "total_actions": self.total_actions,
            "completed_actions": self.completed_actions,
            "failed_actions": self.failed_actions,
            "skipped_actions": self.skipped_actions,
            "launched_apps": self.launched_apps,
            "activated_agents": self.activated_agents,
            "error": self.error,
        }


@dataclass
class ModeSession:
    """A session record of mode usage."""
    mode_id: str
    mode_name: str
    started_at: str = field(default_factory=lambda: datetime.now().isoformat())
    ended_at: str = ""
    duration_seconds: float = 0.0
    status: str = "completed"
    actions_completed: int = 0
    actions_failed: int = 0
    error: str = ""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "mode_id": self.mode_id,
            "mode_name": self.mode_name,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "duration_seconds": self.duration_seconds,
            "status": self.status,
            "actions_completed": self.actions_completed,
            "actions_failed": self.actions_failed,
            "error": self.error,
        }
