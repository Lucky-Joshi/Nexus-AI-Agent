"""
NEXUS - Autonomous Planner Agent
Data models for goals, plans, tasks, dependencies, and execution tracking.
"""

import uuid
import time
from enum import Enum
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
from datetime import datetime


class PlanStatus(Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskStatus(Enum):
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    BLOCKED = "blocked"
    RETRYING = "retrying"


class TaskPriority(Enum):
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3
    BACKGROUND = 4


class DependencyType(Enum):
    REQUIRED = "required"
    OPTIONAL = "optional"
    CONDITIONAL = "conditional"


class ReplanTrigger(Enum):
    TASK_FAILURE = "task_failure"
    NEW_CONTEXT = "new_context"
    USER_REQUEST = "user_request"
    TIMEOUT = "timeout"
    DEPENDENCY_CHANGE = "dependency_change"
    RESOURCE_UNAVAILABLE = "resource_unavailable"


class GoalType(Enum):
    SIMPLE = "simple"
    MULTI_STEP = "multi_step"
    RECURRING = "recurring"
    CONDITIONAL = "conditional"


@dataclass
class PlanTask:
    """A single task within a plan."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    plan_id: str = ""
    title: str = ""
    description: str = ""
    agent_name: str = ""
    command: str = ""
    params: Dict[str, Any] = field(default_factory=dict)
    priority: TaskPriority = TaskPriority.NORMAL
    status: TaskStatus = TaskStatus.PENDING
    dependencies: List[str] = field(default_factory=list)
    dependency_type: DependencyType = DependencyType.REQUIRED
    estimated_duration: int = 0
    actual_duration: float = 0.0
    max_retries: int = 1
    retry_count: int = 0
    fallback_command: str = ""
    condition: str = ""
    output_variable: str = ""
    result: str = ""
    error_message: str = ""
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "plan_id": self.plan_id,
            "title": self.title,
            "description": self.description,
            "agent_name": self.agent_name,
            "command": self.command,
            "params": str(self.params),
            "priority": self.priority.value,
            "status": self.status.value,
            "dependencies": ",".join(self.dependencies),
            "dependency_type": self.dependency_type.value,
            "estimated_duration": self.estimated_duration,
            "actual_duration": self.actual_duration,
            "max_retries": self.max_retries,
            "retry_count": self.retry_count,
            "fallback_command": self.fallback_command,
            "condition": self.condition,
            "output_variable": self.output_variable,
            "result": self.result,
            "error_message": self.error_message,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "created_at": self.created_at.isoformat(),
            "metadata": str(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PlanTask":
        import ast
        def safe_eval(val, default=None):
            if not val:
                return default
            try:
                return ast.literal_eval(val)
            except (ValueError, SyntaxError):
                return default

        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            plan_id=data.get("plan_id", ""),
            title=data.get("title", ""),
            description=data.get("description", ""),
            agent_name=data.get("agent_name", ""),
            command=data.get("command", ""),
            params=safe_eval(data.get("params"), {}),
            priority=TaskPriority(data.get("priority", 2)),
            status=TaskStatus(data.get("status", "pending")),
            dependencies=[d for d in data.get("dependencies", "").split(",") if d],
            dependency_type=DependencyType(data.get("dependency_type", "required")),
            estimated_duration=data.get("estimated_duration", 0),
            actual_duration=data.get("actual_duration", 0.0),
            max_retries=data.get("max_retries", 1),
            retry_count=data.get("retry_count", 0),
            fallback_command=data.get("fallback_command", ""),
            condition=data.get("condition", ""),
            output_variable=data.get("output_variable", ""),
            result=data.get("result", ""),
            error_message=data.get("error_message", ""),
            started_at=datetime.fromisoformat(data["started_at"]) if data.get("started_at") else None,
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now(),
            metadata=safe_eval(data.get("metadata"), {}),
        )

    def is_ready(self, completed_tasks: Set[str]) -> bool:
        if not self.dependencies:
            return True
        for dep_id in self.dependencies:
            if dep_id not in completed_tasks:
                if self.dependency_type == DependencyType.OPTIONAL:
                    continue
                return False
        return True

    def is_blocked(self, completed_tasks: Set[str], failed_tasks: Set[str]) -> bool:
        for dep_id in self.dependencies:
            if dep_id in failed_tasks:
                if self.dependency_type == DependencyType.REQUIRED:
                    return True
        return False


@dataclass
class Plan:
    """A complete plan composed of tasks."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    goal: str = ""
    description: str = ""
    goal_type: GoalType = GoalType.MULTI_STEP
    status: PlanStatus = PlanStatus.DRAFT
    tasks: List[PlanTask] = field(default_factory=list)
    variables: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    created_by: str = "user"
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    replan_count: int = 0
    last_replan_reason: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "goal": self.goal,
            "description": self.description,
            "goal_type": self.goal_type.value,
            "status": self.status.value,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "total_tasks": self.total_tasks,
            "completed_tasks": self.completed_tasks,
            "failed_tasks": self.failed_tasks,
            "replan_count": self.replan_count,
            "last_replan_reason": self.last_replan_reason,
            "variables": str(self.variables),
            "context": str(self.context),
            "metadata": str(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Plan":
        import ast
        def safe_eval(val, default=None):
            if not val:
                return default
            try:
                return ast.literal_eval(val)
            except (ValueError, SyntaxError):
                return default

        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            goal=data.get("goal", ""),
            description=data.get("description", ""),
            goal_type=GoalType(data.get("goal_type", "multi_step")),
            status=PlanStatus(data.get("status", "draft")),
            created_by=data.get("created_by", "user"),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now(),
            started_at=datetime.fromisoformat(data["started_at"]) if data.get("started_at") else None,
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
            total_tasks=data.get("total_tasks", 0),
            completed_tasks=data.get("completed_tasks", 0),
            failed_tasks=data.get("failed_tasks", 0),
            replan_count=data.get("replan_count", 0),
            last_replan_reason=data.get("last_replan_reason", ""),
            variables=safe_eval(data.get("variables"), {}),
            context=safe_eval(data.get("context"), {}),
            metadata=safe_eval(data.get("metadata"), {}),
        )

    def add_task(self, task: PlanTask):
        task.plan_id = self.id
        self.tasks.append(task)
        self.total_tasks = len(self.tasks)

    def get_task(self, task_id: str) -> Optional[PlanTask]:
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None

    def get_pending_tasks(self) -> List[PlanTask]:
        return [t for t in self.tasks if t.status == TaskStatus.PENDING]

    def get_ready_tasks(self, completed: Set[str]) -> List[PlanTask]:
        return [t for t in self.tasks if t.status == TaskStatus.PENDING and t.is_ready(completed)]

    def get_blocked_tasks(self, completed: Set[str], failed: Set[str]) -> List[PlanTask]:
        return [t for t in self.tasks if t.status == TaskStatus.PENDING and t.is_blocked(completed, failed)]

    def get_progress(self) -> float:
        if self.total_tasks == 0:
            return 0.0
        return round((self.completed_tasks / self.total_tasks) * 100, 1)

    def get_summary(self) -> str:
        lines = [
            f"Plan: {self.goal}",
            f"Status: {self.status.value}",
            f"Progress: {self.get_progress()}% ({self.completed_tasks}/{self.total_tasks} tasks)",
        ]
        if self.failed_tasks > 0:
            lines.append(f"Failed: {self.failed_tasks}")
        if self.replan_count > 0:
            lines.append(f"Replans: {self.replan_count}")
        return "\n".join(lines)


@dataclass
class GoalTemplate:
    """A predefined goal template with a task blueprint."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    description: str = ""
    trigger_keywords: List[str] = field(default_factory=list)
    task_blueprint: List[Dict[str, Any]] = field(default_factory=list)
    is_active: bool = True
    usage_count: int = 0

    def matches_query(self, query: str) -> bool:
        query_lower = query.lower()
        return any(kw in query_lower for kw in self.trigger_keywords)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "trigger_keywords": self.trigger_keywords,
            "task_blueprint": self.task_blueprint,
            "is_active": self.is_active,
            "usage_count": self.usage_count,
        }


@dataclass
class PlanStats:
    """Statistics for the planning system."""
    total_plans: int = 0
    active_plans: int = 0
    completed_plans: int = 0
    failed_plans: int = 0
    total_tasks_executed: int = 0
    total_tasks_failed: int = 0
    avg_tasks_per_plan: float = 0.0
    avg_completion_rate: float = 0.0
    total_replans: int = 0
    plans_today: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_plans": self.total_plans,
            "active_plans": self.active_plans,
            "completed_plans": self.completed_plans,
            "failed_plans": self.failed_plans,
            "total_tasks_executed": self.total_tasks_executed,
            "total_tasks_failed": self.total_tasks_failed,
            "avg_tasks_per_plan": round(self.avg_tasks_per_plan, 1),
            "avg_completion_rate": round(self.avg_completion_rate, 1),
            "total_replans": self.total_replans,
            "plans_today": self.plans_today,
        }
