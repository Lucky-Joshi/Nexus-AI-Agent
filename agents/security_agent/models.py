"""
Security Agent Models
Data structures for security monitoring, risk analysis, and audit logging.
"""

from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from typing import Optional, Dict, Any, List
import uuid


class RiskLevel(Enum):
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ThreatType(Enum):
    NONE = "none"
    SUSPICIOUS_COMMAND = "suspicious_command"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    FILE_TAMPERING = "file_tampering"
    NETWORK_ANOMALY = "network_anomaly"
    PROCESS_INJECTION = "process_injection"
    RESOURCE_ABUSE = "resource_abuse"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    MALWARE_INDICATOR = "malware_indicator"
    POLICY_VIOLATION = "policy_violation"


class PermissionLevel(Enum):
    NONE = "none"
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    ADMIN = "admin"
    SYSTEM = "system"


class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AuditAction(Enum):
    COMMAND_EXECUTED = "command_executed"
    COMMAND_BLOCKED = "command_blocked"
    PERMISSION_GRANTED = "permission_granted"
    PERMISSION_DENIED = "permission_denied"
    FILE_ACCESSED = "file_accessed"
    FILE_MODIFIED = "file_modified"
    FILE_DELETED = "file_deleted"
    PROCESS_STARTED = "process_started"
    PROCESS_KILLED = "process_killed"
    WORKFLOW_STARTED = "workflow_started"
    WORKFLOW_COMPLETED = "workflow_completed"
    SECURITY_SCAN = "security_scan"
    POLICY_UPDATED = "policy_updated"
    ALERT_TRIGGERED = "alert_triggered"
    CONFIG_CHANGED = "config_changed"


@dataclass
class SecurityEvent:
    """Represents a security event detected by the monitoring system."""
    event_type: ThreatType
    risk_level: RiskLevel
    source: str
    description: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "event_type": self.event_type.value,
            "risk_level": self.risk_level.value,
            "source": self.source,
            "description": self.description,
            "details": self.details,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SecurityEvent":
        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            event_type=ThreatType(data.get("event_type", "none")),
            risk_level=RiskLevel(data.get("risk_level", "safe")),
            source=data.get("source", "unknown"),
            description=data.get("description", ""),
            details=data.get("details", {}),
            timestamp=data.get("timestamp", datetime.now().isoformat()),
        )


@dataclass
class RiskAssessment:
    """Result of analyzing a command or action for security risks."""
    command: str
    risk_level: RiskLevel
    risk_score: float
    threats: List[ThreatType] = field(default_factory=list)
    reasons: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    blocked: bool = False
    block_reason: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "command": self.command,
            "risk_level": self.risk_level.value,
            "risk_score": self.risk_score,
            "threats": [t.value for t in self.threats],
            "reasons": self.reasons,
            "suggestions": self.suggestions,
            "blocked": self.blocked,
            "block_reason": self.block_reason,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RiskAssessment":
        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            command=data.get("command", ""),
            risk_level=RiskLevel(data.get("risk_level", "safe")),
            risk_score=data.get("risk_score", 0.0),
            threats=[ThreatType(t) for t in data.get("threats", [])],
            reasons=data.get("reasons", []),
            suggestions=data.get("suggestions", []),
            blocked=data.get("blocked", False),
            block_reason=data.get("block_reason", ""),
            timestamp=data.get("timestamp", datetime.now().isoformat()),
        )


@dataclass
class PermissionRule:
    """Defines a permission rule for actions, files, or commands."""
    name: str
    pattern: str
    required_level: PermissionLevel
    description: str = ""
    enabled: bool = True
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "pattern": self.pattern,
            "required_level": self.required_level.value,
            "description": self.description,
            "enabled": self.enabled,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PermissionRule":
        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            name=data.get("name", ""),
            pattern=data.get("pattern", ""),
            required_level=PermissionLevel(data.get("required_level", "none")),
            description=data.get("description", ""),
            enabled=data.get("enabled", True),
            created_at=data.get("created_at", datetime.now().isoformat()),
        )


@dataclass
class AuditRecord:
    """Immutable log entry for security-relevant actions."""
    action: AuditAction
    actor: str
    target: str
    details: str = ""
    risk_level: RiskLevel = RiskLevel.SAFE
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "action": self.action.value,
            "actor": self.actor,
            "target": self.target,
            "details": self.details,
            "risk_level": self.risk_level.value,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AuditRecord":
        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            action=AuditAction(data.get("action", "command_executed")),
            actor=data.get("actor", "unknown"),
            target=data.get("target", ""),
            details=data.get("details", ""),
            risk_level=RiskLevel(data.get("risk_level", "safe")),
            metadata=data.get("metadata", {}),
            timestamp=data.get("timestamp", datetime.now().isoformat()),
        )


@dataclass
class FileProtectionRule:
    """Rule for protecting specific files or directories from modification."""
    path_pattern: str
    protection_level: str
    description: str = ""
    enabled: bool = True
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "path_pattern": self.path_pattern,
            "protection_level": self.protection_level,
            "description": self.description,
            "enabled": self.enabled,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FileProtectionRule":
        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            path_pattern=data.get("path_pattern", ""),
            protection_level=data.get("protection_level", "read"),
            description=data.get("description", ""),
            enabled=data.get("enabled", True),
            created_at=data.get("created_at", datetime.now().isoformat()),
        )


@dataclass
class SecurityAlert:
    """An alert triggered by the security monitoring system."""
    severity: AlertSeverity
    title: str
    message: str
    source: str = ""
    event_id: str = ""
    acknowledged: bool = False
    resolved: bool = False
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    resolved_at: str = ""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "severity": self.severity.value,
            "title": self.title,
            "message": self.message,
            "source": self.source,
            "event_id": self.event_id,
            "acknowledged": self.acknowledged,
            "resolved": self.resolved,
            "created_at": self.created_at,
            "resolved_at": self.resolved_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SecurityAlert":
        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            severity=AlertSeverity(data.get("severity", "info")),
            title=data.get("title", ""),
            message=data.get("message", ""),
            source=data.get("source", ""),
            event_id=data.get("event_id", ""),
            acknowledged=data.get("acknowledged", False),
            resolved=data.get("resolved", False),
            created_at=data.get("created_at", datetime.now().isoformat()),
            resolved_at=data.get("resolved_at", ""),
        )

    def acknowledge(self):
        self.acknowledged = True

    def resolve(self):
        self.resolved = True
        self.resolved_at = datetime.now().isoformat()


@dataclass
class SecurityPolicy:
    """Global security policy configuration."""
    name: str
    description: str = ""
    max_risk_level: RiskLevel = RiskLevel.MEDIUM
    auto_block_critical: bool = True
    audit_enabled: bool = True
    monitor_processes: bool = True
    monitor_files: bool = True
    monitor_network: bool = False
    alert_on_suspicious: bool = True
    safe_execution_mode: bool = True
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "max_risk_level": self.max_risk_level.value,
            "auto_block_critical": self.auto_block_critical,
            "audit_enabled": self.audit_enabled,
            "monitor_processes": self.monitor_processes,
            "monitor_files": self.monitor_files,
            "monitor_network": self.monitor_network,
            "alert_on_suspicious": self.alert_on_suspicious,
            "safe_execution_mode": self.safe_execution_mode,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SecurityPolicy":
        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            name=data.get("name", "default"),
            description=data.get("description", ""),
            max_risk_level=RiskLevel(data.get("max_risk_level", "medium")),
            auto_block_critical=data.get("auto_block_critical", True),
            audit_enabled=data.get("audit_enabled", True),
            monitor_processes=data.get("monitor_processes", True),
            monitor_files=data.get("monitor_files", True),
            monitor_network=data.get("monitor_network", False),
            alert_on_suspicious=data.get("alert_on_suspicious", True),
            safe_execution_mode=data.get("safe_execution_mode", True),
            updated_at=data.get("updated_at", datetime.now().isoformat()),
        )
