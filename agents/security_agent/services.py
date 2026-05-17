"""
Security Agent Services
Core services for risk analysis, permission management, audit logging,
safe execution, and real-time monitoring.
"""

import re
import os
import time
import psutil
import threading
from typing import Dict, Any, List, Optional, Callable
from pathlib import Path
from datetime import datetime

from core.logger import Logger
from core.config import Config

from .models import (
    RiskLevel, ThreatType, PermissionLevel, AuditAction, AlertSeverity,
    SecurityEvent, RiskAssessment, PermissionRule, AuditRecord,
    FileProtectionRule, SecurityAlert, SecurityPolicy,
)
from .storage import SecurityStorage


class RiskAnalyzer:
    """Analyzes commands and actions for security risks."""

    DANGEROUS_COMMANDS = [
        (r"\brm\s+(-rf?|--force)\b", "Recursive force delete detected", RiskLevel.CRITICAL),
        (r"\bformat\s+[a-zA-Z]:", "Disk format command detected", RiskLevel.CRITICAL),
        (r"\bdel\s+/[fqs]", "Force delete command detected", RiskLevel.CRITICAL),
        (r"\brmdir\s+/s", "Recursive directory removal", RiskLevel.CRITICAL),
        (r"\bshutdown\s+(-s|-r|-a)", "System shutdown/restart command", RiskLevel.HIGH),
        (r"\btaskkill\s+/f", "Force kill process command", RiskLevel.HIGH),
        (r"\bkill\s+-9", "SIGKILL process termination", RiskLevel.HIGH),
        (r"\bnet\s+user\s+.*/add", "User account creation", RiskLevel.HIGH),
        (r"\bnet\s+localgroup\s+.*admin.*\/add", "Admin group modification", RiskLevel.CRITICAL),
        (r"\breg\s+delete", "Registry deletion", RiskLevel.HIGH),
        (r"\breg\s+add.*\/f", "Force registry modification", RiskLevel.HIGH),
        (r"\bicacls\s+.*/grant", "ACL permission modification", RiskLevel.HIGH),
        (r"\bcacls\s+.*/[gep]", "ACL permission modification", RiskLevel.HIGH),
        (r"\battrib\s+.*\+h", "Hidden attribute modification", RiskLevel.MEDIUM),
        (r"\bnetsh\s+.*firewall", "Firewall configuration change", RiskLevel.HIGH),
        (r"\bnetsh\s+.*advfirewall", "Advanced firewall configuration", RiskLevel.HIGH),
        (r"\bschtasks\s+/create", "Scheduled task creation", RiskLevel.MEDIUM),
        (r"\bpowershell\s+.*-enc", "Encoded PowerShell execution", RiskLevel.CRITICAL),
        (r"\bpowershell\s+.*-executionpolicy\s+bypass", "Execution policy bypass", RiskLevel.CRITICAL),
        (r"\bcmd\s+/c.*powershell", "CMD invoking PowerShell", RiskLevel.HIGH),
        (r"\bcurl\s+.*\|\s*(bash|sh|powershell)", "Remote script execution", RiskLevel.CRITICAL),
        (r"\bwget\s+.*\|\s*(bash|sh|powershell)", "Remote script execution", RiskLevel.CRITICAL),
        (r"\bchmod\s+777", "World-writable permission", RiskLevel.HIGH),
        (r"\bchown\s+root", "Ownership change to root", RiskLevel.HIGH),
        (r"\bsudo\s+", "Privilege escalation attempt", RiskLevel.HIGH),
        (r"\bsu\s+root", "Switch to root user", RiskLevel.HIGH),
        (r"\bpython\s+-c\s+.*import\s+os", "Python OS module execution", RiskLevel.MEDIUM),
        (r"\bpython\s+-c\s+.*import\s+subprocess", "Python subprocess execution", RiskLevel.MEDIUM),
        (r"\bexec\s*\(", "Dynamic code execution", RiskLevel.HIGH),
        (r"\beval\s*\(", "Dynamic expression evaluation", RiskLevel.HIGH),
        (r"\b__import__\s*\(", "Dynamic module import", RiskLevel.HIGH),
        (r"\bos\.system\s*\(", "OS system call", RiskLevel.HIGH),
        (r"\bos\.popen\s*\(", "OS pipe execution", RiskLevel.HIGH),
        (r"\bsubprocess\.(call|run|Popen)", "Subprocess execution", RiskLevel.MEDIUM),
        (r"\bmkfs\.", "Filesystem creation", RiskLevel.CRITICAL),
        (r"\bdd\s+if=", "Disk dump/write operation", RiskLevel.CRITICAL),
        (r"\bmount\s+", "Filesystem mount operation", RiskLevel.HIGH),
    ]

    SUSPICIOUS_PATTERNS = [
        (r"\.\./", "Path traversal attempt", RiskLevel.MEDIUM),
        (r"\.\.\\", "Path traversal attempt (Windows)", RiskLevel.MEDIUM),
        (r"%[0-9a-fA-F]{2}", "URL-encoded characters", RiskLevel.LOW),
        (r";\s*(rm|del|format|shutdown)", "Command chaining with dangerous command", RiskLevel.HIGH),
        (r"\|\s*(rm|del|format|shutdown)", "Pipe to dangerous command", RiskLevel.HIGH),
        (r"`[^`]*`", "Command substitution", RiskLevel.MEDIUM),
        (r"\$\(.*\)", "Command substitution", RiskLevel.MEDIUM),
        (r"\btemp\b.*\.(exe|bat|cmd|ps1|vbs|js)", "Executable in temp directory", RiskLevel.HIGH),
        (r"\bdownloads\b.*\.(exe|bat|cmd|ps1|vbs|js)", "Executable in downloads", RiskLevel.MEDIUM),
        (r"\bbase64\s+-d", "Base64 decode execution", RiskLevel.HIGH),
        (r"\bcertutil\s+.*-decode", "Certutil decode (common malware technique)", RiskLevel.CRITICAL),
        (r"\bbitsadmin\s+.*\/transfer", "BITS transfer (living off the land)", RiskLevel.HIGH),
        (r"\bwmic\s+.*process\s+call\s+create", "WMIC process creation", RiskLevel.HIGH),
        (r"\bmshta\s+", "MSHTA execution (common malware technique)", RiskLevel.CRITICAL),
        (r"\brundll32\s+", "Rundll32 execution", RiskLevel.HIGH),
        (r"\bregsvr32\s+", "Regsvr32 execution (common malware technique)", RiskLevel.HIGH),
    ]

    def __init__(self, storage: SecurityStorage, policy: Optional[SecurityPolicy] = None):
        self.logger = Logger().get_logger("RiskAnalyzer")
        self._storage = storage
        self._policy = policy or SecurityPolicy(name="default")
        self._compiled_dangerous = [
            (re.compile(p, re.IGNORECASE), desc, level)
            for p, desc, level in self.DANGEROUS_COMMANDS
        ]
        self._compiled_suspicious = [
            (re.compile(p, re.IGNORECASE), desc, level)
            for p, desc, level in self.SUSPICIOUS_PATTERNS
        ]

    def analyze(self, command: str, context: Optional[Dict[str, Any]] = None) -> RiskAssessment:
        """Analyze a command for security risks."""
        threats = []
        reasons = []
        suggestions = []
        max_risk = RiskLevel.SAFE
        risk_score = 0.0

        for pattern, desc, level in self._compiled_dangerous:
            if pattern.search(command):
                threats.append(ThreatType.SUSPICIOUS_COMMAND)
                reasons.append(f"Dangerous: {desc}")
                risk_score += self._risk_score_value(level)
                if self._risk_level_value(level) > self._risk_level_value(max_risk):
                    max_risk = level
                suggestions.append(f"Avoid using {desc.lower()}")

        for pattern, desc, level in self._compiled_suspicious:
            if pattern.search(command):
                if ThreatType.SUSPICIOUS_COMMAND not in threats:
                    threats.append(ThreatType.SUSPICIOUS_COMMAND)
                reasons.append(f"Suspicious: {desc}")
                risk_score += self._risk_score_value(level) * 0.5
                if self._risk_level_value(level) > self._risk_level_value(max_risk):
                    max_risk = level

        if context:
            source = context.get("source", "")
            if source in ("automation_agent", "terminal_agent", "plugin_agent"):
                risk_score *= 1.2
                reasons.append(f"Automated execution from {source}")

            target_path = context.get("target_path", "")
            if target_path:
                protection_violation = self._check_file_protection(target_path)
                if protection_violation:
                    threats.append(ThreatType.FILE_TAMPERING)
                    reasons.append(f"File protection violation: {protection_violation}")
                    max_risk = RiskLevel.HIGH
                    risk_score += 3.0

        risk_score = min(risk_score, 10.0)
        normalized_score = risk_score / 10.0

        if not threats:
            max_risk = RiskLevel.SAFE
            reasons.append("No security risks detected")
            suggestions.append("Command appears safe to execute")

        blocked = False
        block_reason = ""
        if max_risk == RiskLevel.CRITICAL and self._policy.auto_block_critical:
            blocked = True
            block_reason = "Auto-blocked: Critical risk level"
        elif normalized_score > 0.8:
            blocked = True
            block_reason = f"Auto-blocked: Risk score {normalized_score:.2f} exceeds threshold"

        assessment = RiskAssessment(
            command=command,
            risk_level=max_risk,
            risk_score=normalized_score,
            threats=threats,
            reasons=reasons,
            suggestions=suggestions,
            blocked=blocked,
            block_reason=block_reason,
        )

        self._storage.save_assessment(assessment.to_dict())
        self.logger.info(
            f"Risk assessment: {command[:50]}... -> {max_risk.value} "
            f"(score: {normalized_score:.2f}, blocked: {blocked})"
        )

        return assessment

    def _check_file_protection(self, path: str) -> Optional[str]:
        """Check if a file path violates protection rules."""
        for rule in self._storage.get_file_protection_rules():
            pattern = rule["path_pattern"]
            if re.search(pattern, path, re.IGNORECASE):
                return f"Protected by rule: {rule['description'] or pattern}"
        return None

    @staticmethod
    def _risk_score_value(level: RiskLevel) -> float:
        return {
            RiskLevel.SAFE: 0.0,
            RiskLevel.LOW: 0.5,
            RiskLevel.MEDIUM: 1.5,
            RiskLevel.HIGH: 3.0,
            RiskLevel.CRITICAL: 5.0,
        }.get(level, 0.0)

    @staticmethod
    def _risk_level_value(level: RiskLevel) -> int:
        return {
            RiskLevel.SAFE: 0,
            RiskLevel.LOW: 1,
            RiskLevel.MEDIUM: 2,
            RiskLevel.HIGH: 3,
            RiskLevel.CRITICAL: 4,
        }.get(level, 0)


class PermissionManager:
    """Manages permission rules and validates access requests."""

    DEFAULT_RULES = [
        PermissionRule(
            name="system_config_access",
            pattern=r"(regedit|msconfig|services\.msc|gpedit)",
            required_level=PermissionLevel.ADMIN,
            description="Access to system configuration tools",
        ),
        PermissionRule(
            name="network_config",
            pattern=r"(ipconfig.*\/renew|netsh|route\s+add|firewall)",
            required_level=PermissionLevel.ADMIN,
            description="Network configuration changes",
        ),
        PermissionRule(
            name="user_management",
            pattern=r"(net\s+user|net\s+localgroup|whoami|groups)",
            required_level=PermissionLevel.ADMIN,
            description="User and group management",
        ),
        PermissionRule(
            name="file_delete",
            pattern=r"(del\s+|rm\s+|rmdir\s+|Remove-Item)",
            required_level=PermissionLevel.WRITE,
            description="File and directory deletion",
        ),
        PermissionRule(
            name="file_execute",
            pattern=r"\.(exe|bat|cmd|ps1|vbs|msi)\b",
            required_level=PermissionLevel.EXECUTE,
            description="Executable file execution",
        ),
        PermissionRule(
            name="process_management",
            pattern=r"(taskkill|kill|Stop-Process|tasklist|Get-Process)",
            required_level=PermissionLevel.ADMIN,
            description="Process management operations",
        ),
        PermissionRule(
            name="scheduled_tasks",
            pattern=r"(schtasks|at\s+|New-ScheduledTask)",
            required_level=PermissionLevel.ADMIN,
            description="Scheduled task management",
        ),
        PermissionRule(
            name="service_management",
            pattern=r"(sc\s+|net\s+start|net\s+stop|Start-Service|Stop-Service)",
            required_level=PermissionLevel.ADMIN,
            description="Windows service management",
        ),
    ]

    def __init__(self, storage: SecurityStorage):
        self.logger = Logger().get_logger("PermissionManager")
        self._storage = storage
        self._rules: List[PermissionRule] = []
        self._load_rules()

    def _load_rules(self):
        """Load rules from storage or initialize defaults."""
        stored = self._storage.get_permission_rules()
        if stored:
            self._rules = [PermissionRule.from_dict(r) for r in stored]
        else:
            for rule in self.DEFAULT_RULES:
                self._rules.append(rule)
                self._storage.save_permission_rule(rule.to_dict())
        self.logger.info(f"Loaded {len(self._rules)} permission rules")

    def check_permission(self, command: str, actor: str = "user") -> Dict[str, Any]:
        """Check if a command is permitted based on rules."""
        matching_rules = []
        required_level = PermissionLevel.NONE
        highest_rule = None

        for rule in self._rules:
            if not rule.enabled:
                continue
            if re.search(rule.pattern, command, re.IGNORECASE):
                matching_rules.append(rule)
                if self._permission_value(rule.required_level) > self._permission_value(required_level):
                    required_level = rule.required_level
                    highest_rule = rule

        if not matching_rules:
            return {
                "permitted": True,
                "required_level": PermissionLevel.NONE.value,
                "matched_rules": [],
                "message": "No permission rules apply to this command",
            }

        actor_level = self._get_actor_level(actor)
        permitted = self._permission_value(actor_level) >= self._permission_value(required_level)

        rule_names = [r.name for r in matching_rules]
        message = (
            f"Permitted (level: {actor_level.value})"
            if permitted
            else f"Denied: requires {required_level.value}, actor has {actor_level.value}"
        )

        self._storage.save_audit_record(
            AuditRecord(
                action=AuditAction.PERMISSION_GRANTED if permitted else AuditAction.PERMISSION_DENIED,
                actor=actor,
                target=command[:100],
                details=f"Rules: {', '.join(rule_names)}",
                risk_level=RiskLevel.SAFE if permitted else RiskLevel.MEDIUM,
            ).to_dict()
        )

        return {
            "permitted": permitted,
            "required_level": required_level.value,
            "actor_level": actor_level.value,
            "matched_rules": rule_names,
            "highest_rule": highest_rule.name if highest_rule else None,
            "message": message,
        }

    def add_rule(self, rule: PermissionRule) -> bool:
        """Add a new permission rule."""
        self._rules.append(rule)
        self._storage.save_permission_rule(rule.to_dict())
        self.logger.info(f"Added permission rule: {rule.name}")
        return True

    def remove_rule(self, rule_id: str) -> bool:
        """Remove a permission rule by ID."""
        self._rules = [r for r in self._rules if r.id != rule_id]
        return self._storage.delete_permission_rule(rule_id)

    def list_rules(self, enabled_only: bool = True) -> List[PermissionRule]:
        """List all permission rules."""
        if enabled_only:
            return [r for r in self._rules if r.enabled]
        return self._rules

    def set_actor_level(self, actor: str, level: PermissionLevel):
        """Set the permission level for an actor."""
        self._actor_levels[actor] = level

    def _get_actor_level(self, actor: str) -> PermissionLevel:
        """Get the permission level for an actor."""
        return getattr(self, "_actor_levels", {}).get(
            actor, PermissionLevel.READ
        )

    @staticmethod
    def _permission_value(level: PermissionLevel) -> int:
        return {
            PermissionLevel.NONE: 0,
            PermissionLevel.READ: 1,
            PermissionLevel.WRITE: 2,
            PermissionLevel.EXECUTE: 3,
            PermissionLevel.ADMIN: 4,
            PermissionLevel.SYSTEM: 5,
        }.get(level, 0)


class AuditLogger:
    """Immutable audit logging for security-relevant actions."""

    def __init__(self, storage: SecurityStorage):
        self.logger = Logger().get_logger("AuditLogger")
        self._storage = storage
        self._lock = threading.Lock()

    def log(self, action: AuditAction, actor: str, target: str,
            details: str = "", risk_level: RiskLevel = RiskLevel.SAFE,
            metadata: Optional[Dict[str, Any]] = None) -> AuditRecord:
        """Create an immutable audit record."""
        with self._lock:
            record = AuditRecord(
                action=action,
                actor=actor,
                target=target,
                details=details,
                risk_level=risk_level,
                metadata=metadata or {},
            )
            self._storage.save_audit_record(record.to_dict())
            self.logger.debug(
                f"Audit: {action.value} by {actor} on {target[:50]}"
            )
            return record

    def get_records(self, limit: int = 100,
                    action: Optional[str] = None) -> List[AuditRecord]:
        """Retrieve audit records."""
        records = self._storage.get_audit_records(limit=limit, action=action)
        return [AuditRecord.from_dict(r) for r in records]

    def get_records_by_actor(self, actor: str, limit: int = 50) -> List[AuditRecord]:
        """Get audit records for a specific actor."""
        all_records = self._storage.get_audit_records(limit=limit * 2)
        return [
            AuditRecord.from_dict(r)
            for r in all_records
            if r.get("actor") == actor
        ][:limit]

    def get_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get audit summary for the specified time period."""
        records = self._storage.get_audit_records(limit=1000)
        cutoff = datetime.now().timestamp() - (hours * 3600)

        filtered = []
        for r in records:
            try:
                ts = datetime.fromisoformat(r["timestamp"]).timestamp()
                if ts >= cutoff:
                    filtered.append(r)
            except (ValueError, KeyError):
                continue

        action_counts = {}
        risk_counts = {}
        for r in filtered:
            action = r.get("action", "unknown")
            action_counts[action] = action_counts.get(action, 0) + 1
            risk = r.get("risk_level", "safe")
            risk_counts[risk] = risk_counts.get(risk, 0) + 1

        return {
            "period_hours": hours,
            "total_records": len(filtered),
            "action_counts": action_counts,
            "risk_counts": risk_counts,
        }


class SafeExecutor:
    """Executes commands and workflows with security validation."""

    def __init__(self, risk_analyzer: RiskAnalyzer, audit_logger: AuditLogger,
                 permission_manager: PermissionManager,
                 max_risk_level: RiskLevel = RiskLevel.MEDIUM):
        self.logger = Logger().get_logger("SafeExecutor")
        self._analyzer = risk_analyzer
        self._audit = audit_logger
        self._permissions = permission_manager
        self._max_risk = max_risk_level
        self._execution_log: List[Dict[str, Any]] = []

    def execute_with_validation(self, command: str, executor: Callable,
                                actor: str = "user",
                                context: Optional[Dict[str, Any]] = None,
                                force: bool = False) -> Dict[str, Any]:
        """Execute a command after security validation."""
        assessment = self._analyzer.analyze(command, context)

        self._audit.log(
            action=AuditAction.COMMAND_BLOCKED if assessment.blocked and not force else AuditAction.COMMAND_EXECUTED,
            actor=actor,
            target=command[:100],
            details=f"Risk: {assessment.risk_level.value}, Score: {assessment.risk_score:.2f}",
            risk_level=assessment.risk_level,
            metadata={"assessment_id": assessment.id},
        )

        if assessment.blocked and not force:
            return {
                "success": False,
                "blocked": True,
                "risk_level": assessment.risk_level.value,
                "risk_score": assessment.risk_score,
                "block_reason": assessment.block_reason,
                "threats": [t.value for t in assessment.threats],
                "reasons": assessment.reasons,
                "suggestions": assessment.suggestions,
                "assessment_id": assessment.id,
            }

        if not force and self._risk_level_value(assessment.risk_level) > self._risk_level_value(self._max_risk):
            return {
                "success": False,
                "blocked": True,
                "risk_level": assessment.risk_level.value,
                "risk_score": assessment.risk_score,
                "block_reason": f"Risk level {assessment.risk_level.value} exceeds maximum allowed ({self._max_risk.value})",
                "threats": [t.value for t in assessment.threats],
                "reasons": assessment.reasons,
                "suggestions": assessment.suggestions,
                "assessment_id": assessment.id,
            }

        perm_check = self._permissions.check_permission(command, actor)
        if not perm_check["permitted"] and not force:
            return {
                "success": False,
                "blocked": True,
                "risk_level": assessment.risk_level.value,
                "risk_score": assessment.risk_score,
                "block_reason": perm_check["message"],
                "permission_required": perm_check["required_level"],
                "assessment_id": assessment.id,
            }

        try:
            start_time = time.time()
            result = executor()
            duration = time.time() - start_time

            self._execution_log.append({
                "command": command,
                "actor": actor,
                "success": True,
                "duration": duration,
                "assessment_id": assessment.id,
                "timestamp": datetime.now().isoformat(),
            })

            return {
                "success": True,
                "blocked": False,
                "risk_level": assessment.risk_level.value,
                "risk_score": assessment.risk_score,
                "result": result,
                "duration": duration,
                "assessment_id": assessment.id,
                "reasons": assessment.reasons,
            }
        except Exception as e:
            self._audit.log(
                action=AuditAction.COMMAND_EXECUTED,
                actor=actor,
                target=command[:100],
                details=f"Execution failed: {str(e)}",
                risk_level=assessment.risk_level,
                metadata={"assessment_id": assessment.id, "error": str(e)},
            )
            return {
                "success": False,
                "blocked": False,
                "risk_level": assessment.risk_level.value,
                "risk_score": assessment.risk_score,
                "error": str(e),
                "assessment_id": assessment.id,
                "reasons": assessment.reasons,
            }

    def validate_workflow(self, workflow_name: str, steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate an entire workflow before execution."""
        self._audit.log(
            action=AuditAction.WORKFLOW_STARTED,
            actor="system",
            target=workflow_name,
            details=f"Validating workflow with {len(steps)} steps",
        )

        assessments = []
        max_risk = RiskLevel.SAFE
        blocked_steps = []

        for i, step in enumerate(steps):
            command = step.get("command", step.get("action", ""))
            if not command:
                continue

            assessment = self._analyzer.analyze(command, {"source": "workflow", "workflow": workflow_name})
            assessments.append(assessment)

            if self._risk_level_value(assessment.risk_level) > self._risk_level_value(max_risk):
                max_risk = assessment.risk_level

            if assessment.blocked:
                blocked_steps.append({
                    "step": i,
                    "command": command,
                    "risk_level": assessment.risk_level.value,
                    "block_reason": assessment.block_reason,
                })

        workflow_safe = len(blocked_steps) == 0

        return {
            "workflow": workflow_name,
            "safe": workflow_safe,
            "max_risk": max_risk.value,
            "total_steps": len(steps),
            "blocked_steps": blocked_steps,
            "assessments": [a.to_dict() for a in assessments],
        }

    def get_execution_log(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent execution log entries."""
        return self._execution_log[-limit:]

    @staticmethod
    def _risk_level_value(level: RiskLevel) -> int:
        return {
            RiskLevel.SAFE: 0,
            RiskLevel.LOW: 1,
            RiskLevel.MEDIUM: 2,
            RiskLevel.HIGH: 3,
            RiskLevel.CRITICAL: 4,
        }.get(level, 0)


class MonitorService:
    """Real-time system monitoring for security events."""

    def __init__(self, storage: SecurityStorage, audit_logger: AuditLogger):
        self.logger = Logger().get_logger("MonitorService")
        self._storage = storage
        self._audit = audit_logger
        self._monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._callbacks: List[Callable] = []
        self._baseline_cpu = 0.0
        self._baseline_memory = 0.0
        self._alert_thresholds = {
            "cpu_percent": 90.0,
            "memory_percent": 90.0,
            "disk_percent": 95.0,
            "open_files": 10000,
            "network_connections": 500,
        }

    def start_monitoring(self, interval: int = 30):
        """Start background monitoring."""
        if self._monitoring:
            return {"success": False, "message": "Monitoring already active"}

        self._monitoring = True
        self._baseline_cpu = psutil.cpu_percent(interval=1)
        self._baseline_memory = psutil.virtual_memory().percent

        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval,),
            daemon=True,
        )
        self._monitor_thread.start()
        self.logger.info(f"Security monitoring started (interval: {interval}s)")

        self._audit.log(
            action=AuditAction.SECURITY_SCAN,
            actor="system",
            target="monitor_service",
            details=f"Monitoring started with {interval}s interval",
        )

        return {"success": True, "message": "Security monitoring started"}

    def stop_monitoring(self):
        """Stop background monitoring."""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
        self.logger.info("Security monitoring stopped")

        self._audit.log(
            action=AuditAction.SECURITY_SCAN,
            actor="system",
            target="monitor_service",
            details="Monitoring stopped",
        )

        return {"success": True, "message": "Security monitoring stopped"}

    def add_callback(self, callback: Callable):
        """Add a callback for security events."""
        self._callbacks.append(callback)

    def check_system_health(self) -> Dict[str, Any]:
        """Perform a comprehensive system health check."""
        cpu = psutil.cpu_percent(interval=0.5)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        processes = list(psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]))
        net_connections = psutil.net_connections(kind="inet")

        alerts = []
        risk = RiskLevel.SAFE

        if cpu > self._alert_thresholds["cpu_percent"]:
            alerts.append(f"High CPU usage: {cpu:.1f}%")
            risk = RiskLevel.HIGH

        if memory.percent > self._alert_thresholds["memory_percent"]:
            alerts.append(f"High memory usage: {memory.percent:.1f}%")
            risk = RiskLevel.HIGH

        if disk.percent > self._alert_thresholds["disk_percent"]:
            alerts.append(f"High disk usage: {disk.percent:.1f}%")
            risk = RiskLevel.MEDIUM

        if len(processes) > self._alert_thresholds["open_files"]:
            alerts.append(f"High process count: {len(processes)}")
            risk = RiskLevel.MEDIUM

        suspicious_procs = self._find_suspicious_processes(processes)
        if suspicious_procs:
            alerts.extend(suspicious_procs)
            risk = RiskLevel.HIGH

        return {
            "cpu_percent": cpu,
            "memory_percent": memory.percent,
            "memory_total_gb": memory.total / (1024**3),
            "memory_used_gb": memory.used / (1024**3),
            "disk_percent": disk.percent,
            "disk_total_gb": disk.total / (1024**3),
            "disk_used_gb": disk.used / (1024**3),
            "process_count": len(processes),
            "network_connections": len(net_connections),
            "suspicious_processes": suspicious_procs,
            "alerts": alerts,
            "overall_risk": risk.value,
            "healthy": len(alerts) == 0,
        }

    def scan_processes(self) -> List[Dict[str, Any]]:
        """Scan running processes for suspicious activity."""
        suspicious = []
        suspicious_names = [
            "cmd.exe", "powershell.exe", "pwsh.exe", "wscript.exe",
            "cscript.exe", "mshta.exe", "rundll32.exe", "regsvr32.exe",
            "certutil.exe", "bitsadmin.exe", "wmic.exe", "psexec.exe",
            "mimikatz.exe", "nc.exe", "ncat.exe", "netcat.exe",
        ]

        for proc in psutil.process_iter(["pid", "name", "exe", "cmdline"]):
            try:
                info = proc.info
                name = (info.get("name") or "").lower()

                if name in suspicious_names:
                    suspicious.append({
                        "pid": info.get("pid"),
                        "name": name,
                        "exe": info.get("exe", ""),
                        "cmdline": " ".join(info.get("cmdline") or []),
                        "reason": f"Suspicious process: {name}",
                    })

                cmdline = " ".join(info.get("cmdline") or [])
                if any(kw in cmdline.lower() for kw in ["-enc", "bypass", "hidden", "downloadstring"]):
                    suspicious.append({
                        "pid": info.get("pid"),
                        "name": name,
                        "exe": info.get("exe", ""),
                        "cmdline": cmdline[:200],
                        "reason": "Suspicious command line arguments",
                    })

            except (psutil.AccessDenied, psutil.NoSuchProcess):
                continue

        return suspicious

    def _monitor_loop(self, interval: int):
        """Background monitoring loop."""
        while self._monitoring:
            try:
                health = self.check_system_health()
                if not health["healthy"]:
                    event = SecurityEvent(
                        event_type=ThreatType.RESOURCE_ABUSE,
                        risk_level=RiskLevel(health["overall_risk"]),
                        source="monitor_service",
                        description="System health alert",
                        details=health,
                    )
                    self._storage.save_event(event.to_dict())

                    for callback in self._callbacks:
                        try:
                            callback(event)
                        except Exception:
                            pass

                suspicious = self.scan_processes()
                if suspicious:
                    event = SecurityEvent(
                        event_type=ThreatType.SUSPICIOUS_COMMAND,
                        risk_level=RiskLevel.HIGH,
                        source="monitor_service",
                        description=f"Found {len(suspicious)} suspicious processes",
                        details={"processes": suspicious},
                    )
                    self._storage.save_event(event.to_dict())

            except Exception as e:
                self.logger.error(f"Monitoring error: {e}")

            time.sleep(interval)

    @staticmethod
    def _find_suspicious_processes(processes: List) -> List[str]:
        """Identify suspicious processes."""
        alerts = []
        suspicious_names = {"cmd.exe", "powershell.exe", "mshta.exe", "rundll32.exe"}

        for proc in processes:
            try:
                name = (proc.info.get("name") or "").lower()
                if name in suspicious_names and proc.info.get("cpu_percent", 0) > 50:
                    alerts.append(f"High CPU usage by {name} (PID: {proc.info.get('pid')})")
            except (KeyError, TypeError):
                continue

        return alerts
