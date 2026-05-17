"""
Analytics Agent Models
Data structures for usage analytics, performance tracking, and productivity metrics.
"""

from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from typing import Optional, Dict, Any, List
import uuid


class MetricType(Enum):
    USAGE = "usage"
    PERFORMANCE = "performance"
    RESOURCE = "resource"
    PRODUCTIVITY = "productivity"
    WORKFLOW = "workflow"
    ERROR = "error"
    RESPONSE_TIME = "response_time"


class TimeRange(Enum):
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"
    ALL = "all"


class ReportFormat(Enum):
    TEXT = "text"
    JSON = "json"
    SUMMARY = "summary"
    DETAILED = "detailed"


@dataclass
class UsageRecord:
    """Tracks a single user interaction or agent usage event."""
    agent_name: str
    action: str
    command: str
    success: bool
    duration: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    session_id: str = ""
    user_input_length: int = 0
    output_length: int = 0
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "agent_name": self.agent_name,
            "action": self.action,
            "command": self.command[:200],
            "success": self.success,
            "duration": self.duration,
            "timestamp": self.timestamp,
            "session_id": self.session_id,
            "user_input_length": self.user_input_length,
            "output_length": self.output_length,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UsageRecord":
        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            agent_name=data.get("agent_name", "unknown"),
            action=data.get("action", ""),
            command=data.get("command", ""),
            success=data.get("success", False),
            duration=data.get("duration", 0.0),
            timestamp=data.get("timestamp", datetime.now().isoformat()),
            session_id=data.get("session_id", ""),
            user_input_length=data.get("user_input_length", 0),
            output_length=data.get("output_length", 0),
        )


@dataclass
class AgentPerformance:
    """Aggregated performance metrics for a single agent."""
    agent_name: str
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    avg_duration: float = 0.0
    min_duration: float = float("inf")
    max_duration: float = 0.0
    total_duration: float = 0.0
    success_rate: float = 0.0
    last_used: str = ""
    first_used: str = ""
    error_counts: Dict[str, int] = field(default_factory=dict)
    hourly_usage: Dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_name": self.agent_name,
            "total_calls": self.total_calls,
            "successful_calls": self.successful_calls,
            "failed_calls": self.failed_calls,
            "avg_duration": round(self.avg_duration, 3),
            "min_duration": round(self.min_duration, 3) if self.min_duration != float("inf") else 0.0,
            "max_duration": round(self.max_duration, 3),
            "total_duration": round(self.total_duration, 3),
            "success_rate": round(self.success_rate, 2),
            "last_used": self.last_used,
            "first_used": self.first_used,
            "error_counts": self.error_counts,
            "hourly_usage": self.hourly_usage,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentPerformance":
        return cls(
            agent_name=data.get("agent_name", "unknown"),
            total_calls=data.get("total_calls", 0),
            successful_calls=data.get("successful_calls", 0),
            failed_calls=data.get("failed_calls", 0),
            avg_duration=data.get("avg_duration", 0.0),
            min_duration=data.get("min_duration", 0.0),
            max_duration=data.get("max_duration", 0.0),
            total_duration=data.get("total_duration", 0.0),
            success_rate=data.get("success_rate", 0.0),
            last_used=data.get("last_used", ""),
            first_used=data.get("first_used", ""),
            error_counts=data.get("error_counts", {}),
            hourly_usage=data.get("hourly_usage", {}),
        )

    def update(self, duration: float, success: bool, error: str = ""):
        self.total_calls += 1
        if success:
            self.successful_calls += 1
        else:
            self.failed_calls += 1
            if error:
                self.error_counts[error[:50]] = self.error_counts.get(error[:50], 0) + 1

        self.total_duration += duration
        self.avg_duration = self.total_duration / self.total_calls
        if duration < self.min_duration:
            self.min_duration = duration
        if duration > self.max_duration:
            self.max_duration = duration
        self.success_rate = (self.successful_calls / self.total_calls * 100) if self.total_calls > 0 else 0.0

        now = datetime.now().isoformat()
        if not self.first_used:
            self.first_used = now
        self.last_used = now

        hour = datetime.now().strftime("%H")
        self.hourly_usage[hour] = self.hourly_usage.get(hour, 0) + 1


@dataclass
class ResourceSnapshot:
    """Point-in-time system resource usage."""
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    memory_used_gb: float = 0.0
    memory_total_gb: float = 0.0
    disk_percent: float = 0.0
    disk_used_gb: float = 0.0
    disk_total_gb: float = 0.0
    process_count: int = 0
    network_connections: int = 0
    uptime_seconds: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "cpu_percent": self.cpu_percent,
            "memory_percent": self.memory_percent,
            "memory_used_gb": self.memory_used_gb,
            "memory_total_gb": self.memory_total_gb,
            "disk_percent": self.disk_percent,
            "disk_used_gb": self.disk_used_gb,
            "disk_total_gb": self.disk_total_gb,
            "process_count": self.process_count,
            "network_connections": self.network_connections,
            "uptime_seconds": self.uptime_seconds,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ResourceSnapshot":
        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            cpu_percent=data.get("cpu_percent", 0.0),
            memory_percent=data.get("memory_percent", 0.0),
            memory_used_gb=data.get("memory_used_gb", 0.0),
            memory_total_gb=data.get("memory_total_gb", 0.0),
            disk_percent=data.get("disk_percent", 0.0),
            disk_used_gb=data.get("disk_used_gb", 0.0),
            disk_total_gb=data.get("disk_total_gb", 0.0),
            process_count=data.get("process_count", 0),
            network_connections=data.get("network_connections", 0),
            uptime_seconds=data.get("uptime_seconds", 0.0),
            timestamp=data.get("timestamp", datetime.now().isoformat()),
        )


@dataclass
class ProductivitySession:
    """Tracks a focused work session with metrics."""
    start_time: str
    end_time: str = ""
    duration_minutes: float = 0.0
    commands_executed: int = 0
    agents_used: List[str] = field(default_factory=list)
    workflows_run: int = 0
    tasks_completed: int = 0
    interruptions: int = 0
    focus_score: float = 0.0
    session_type: str = "general"
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_minutes": self.duration_minutes,
            "commands_executed": self.commands_executed,
            "agents_used": self.agents_used,
            "workflows_run": self.workflows_run,
            "tasks_completed": self.tasks_completed,
            "interruptions": self.interruptions,
            "focus_score": self.focus_score,
            "session_type": self.session_type,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProductivitySession":
        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            start_time=data.get("start_time", datetime.now().isoformat()),
            end_time=data.get("end_time", ""),
            duration_minutes=data.get("duration_minutes", 0.0),
            commands_executed=data.get("commands_executed", 0),
            agents_used=data.get("agents_used", []),
            workflows_run=data.get("workflows_run", 0),
            tasks_completed=data.get("tasks_completed", 0),
            interruptions=data.get("interruptions", 0),
            focus_score=data.get("focus_score", 0.0),
            session_type=data.get("session_type", "general"),
        )

    def close(self):
        self.end_time = datetime.now().isoformat()
        try:
            start = datetime.fromisoformat(self.start_time)
            end = datetime.fromisoformat(self.end_time)
            self.duration_minutes = (end - start).total_seconds() / 60
        except (ValueError, TypeError):
            self.duration_minutes = 0.0


@dataclass
class AnalyticsReport:
    """Generated analytics report with insights."""
    report_type: str
    time_range: str
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    summary: str = ""
    metrics: Dict[str, Any] = field(default_factory=dict)
    trends: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "report_type": self.report_type,
            "time_range": self.time_range,
            "generated_at": self.generated_at,
            "summary": self.summary,
            "metrics": self.metrics,
            "trends": self.trends,
            "recommendations": self.recommendations,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AnalyticsReport":
        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            report_type=data.get("report_type", ""),
            time_range=data.get("time_range", ""),
            generated_at=data.get("generated_at", datetime.now().isoformat()),
            summary=data.get("summary", ""),
            metrics=data.get("metrics", {}),
            trends=data.get("trends", {}),
            recommendations=data.get("recommendations", []),
        )


@dataclass
class DashboardData:
    """Real-time dashboard data for UI display."""
    total_commands: int = 0
    total_agents_used: int = 0
    active_sessions: int = 0
    avg_response_time: float = 0.0
    success_rate: float = 0.0
    top_agents: List[Dict[str, Any]] = field(default_factory=list)
    recent_activity: List[Dict[str, Any]] = field(default_factory=list)
    resource_usage: Dict[str, Any] = field(default_factory=dict)
    productivity_score: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_commands": self.total_commands,
            "total_agents_used": self.total_agents_used,
            "active_sessions": self.active_sessions,
            "avg_response_time": round(self.avg_response_time, 3),
            "success_rate": round(self.success_rate, 2),
            "top_agents": self.top_agents,
            "recent_activity": self.recent_activity,
            "resource_usage": self.resource_usage,
            "productivity_score": round(self.productivity_score, 2),
            "timestamp": self.timestamp,
        }
