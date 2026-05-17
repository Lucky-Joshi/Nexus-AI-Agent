"""
Security Agent
Monitors and protects the system from risky actions and unsafe operations.
Provides risk analysis, permission validation, audit logging, and safe execution.
"""

from typing import Dict, Any, Optional, Callable

from core.base_agent import BaseAgent, AgentStatus
from core.logger import Logger
from core.config import Config

from .models import (
    RiskLevel, ThreatType, PermissionLevel, AuditAction, AlertSeverity,
    SecurityEvent, RiskAssessment, PermissionRule, AuditRecord,
    FileProtectionRule, SecurityAlert, SecurityPolicy,
)
from .storage import SecurityStorage
from .services import (
    RiskAnalyzer, PermissionManager, AuditLogger, SafeExecutor, MonitorService,
)


class SecurityAgent(BaseAgent):
    """Security monitoring and protection agent for NEXUS."""

    def __init__(self):
        super().__init__("security_agent", "System security monitoring, risk analysis, and protection")

        self.logger = Logger().get_logger("SecurityAgent")
        self.config = Config()

        self._storage = SecurityStorage()
        self._policy = self._load_policy()

        self._analyzer = RiskAnalyzer(self._storage, self._policy)
        self._permissions = PermissionManager(self._storage)
        self._audit = AuditLogger(self._storage)
        self._executor = SafeExecutor(
            self._analyzer, self._audit, self._permissions,
            max_risk_level=self._policy.max_risk_level,
        )
        self._monitor = MonitorService(self._storage, self._audit)

        self._monitoring_active = False
        self.logger.info("SecurityAgent initialized")

    def execute(self, command: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        self.status = AgentStatus.BUSY
        try:
            cmd = command.lower()

            if self._matches(cmd, ["analyze", "check risk", "risk check", "scan command", "security check"]):
                return self._handle_analyze(command)
            elif self._matches(cmd, ["block", "allow", "force execute", "override"]):
                return self._handle_override(command)
            elif self._matches(cmd, ["system health", "health check", "system scan", "check system", "system status"]):
                return self._handle_health_check(command)
            elif self._matches(cmd, ["process scan", "scan processes", "suspicious process", "list suspicious"]):
                return self._handle_process_scan(command)
            elif self._matches(cmd, ["start monitoring", "enable monitoring", "start monitor", "monitor start"]):
                return self._handle_start_monitoring(command)
            elif self._matches(cmd, ["stop monitoring", "disable monitoring", "stop monitor", "monitor stop"]):
                return self._handle_stop_monitoring(command)
            elif self._matches(cmd, ["events", "security events", "list events", "show events"]):
                return self._handle_events(command)
            elif self._matches(cmd, ["audit", "audit log", "audit trail", "show audit", "list audit"]):
                return self._handle_audit_log(command)
            elif self._matches(cmd, ["alerts", "security alerts", "list alerts", "show alerts", "active alerts"]):
                return self._handle_alerts(command)
            elif self._matches(cmd, ["permissions", "permission rules", "list permissions", "show permissions"]):
                return self._handle_permissions(command)
            elif self._matches(cmd, ["add permission", "new permission", "create permission"]):
                return self._handle_add_permission(command)
            elif self._matches(cmd, ["remove permission", "delete permission"]):
                return self._handle_remove_permission(command)
            elif self._matches(cmd, ["file protection", "protect file", "protect folder", "file rules"]):
                return self._handle_file_protection(command)
            elif self._matches(cmd, ["add protection", "protect path"]):
                return self._handle_add_protection(command)
            elif self._matches(cmd, ["policy", "security policy", "show policy", "policy status"]):
                return self._handle_policy(command)
            elif self._matches(cmd, ["set policy", "update policy", "change policy"]):
                return self._handle_set_policy(command)
            elif self._matches(cmd, ["stats", "security stats", "security status", "security summary"]):
                return self._handle_stats(command)
            elif self._matches(cmd, ["validate workflow", "workflow security", "check workflow"]):
                return self._handle_validate_workflow(command)
            elif self._matches(cmd, ["execution log", "exec log", "run history"]):
                return self._handle_execution_log(command)
            elif self._matches(cmd, ["security", "security agent", "security help"]):
                return self._handle_help(command)
            else:
                return self._handle_analyze(command)
        except Exception as e:
            return {"success": False, "response": f"Error: {e}", "error": str(e)}
        finally:
            self.status = AgentStatus.IDLE

    def get_capabilities(self) -> list:
        return [
            "analyze_command",
            "override_security",
            "system_health_check",
            "process_scan",
            "start_monitoring",
            "stop_monitoring",
            "list_events",
            "audit_log",
            "list_alerts",
            "manage_permissions",
            "file_protection",
            "policy_management",
            "security_stats",
            "validate_workflow",
            "execution_log",
        ]

    def analyze_command(self, command: str, context: Optional[Dict[str, Any]] = None) -> RiskAssessment:
        """Programmatically analyze a command for risks."""
        return self._analyzer.analyze(command, context)

    def check_permission(self, command: str, actor: str = "user") -> Dict[str, Any]:
        """Check if a command is permitted."""
        return self._permissions.check_permission(command, actor)

    def execute_safely(self, command: str, executor: Callable,
                       actor: str = "user", force: bool = False) -> Dict[str, Any]:
        """Execute a command with security validation."""
        return self._executor.execute_with_validation(command, executor, actor, force=force)

    def validate_workflow(self, workflow_name: str, steps: list) -> Dict[str, Any]:
        """Validate a workflow for security risks."""
        return self._executor.validate_workflow(workflow_name, steps)

    def get_system_health(self) -> Dict[str, Any]:
        """Get current system health status."""
        return self._monitor.check_system_health()

    def scan_processes(self) -> list:
        """Scan for suspicious processes."""
        return self._monitor.scan_processes()

    def start_monitoring(self, interval: int = 30) -> Dict[str, Any]:
        """Start background security monitoring."""
        result = self._monitor.start_monitoring(interval)
        if result["success"]:
            self._monitoring_active = True
        return result

    def stop_monitoring(self) -> Dict[str, Any]:
        """Stop background security monitoring."""
        result = self._monitor.stop_monitoring()
        if result["success"]:
            self._monitoring_active = False
        return result

    def _load_policy(self) -> SecurityPolicy:
        """Load security policy from storage or create default."""
        stored = self._storage.get_policy()
        if stored:
            return SecurityPolicy.from_dict(stored)
        policy = SecurityPolicy(name="default")
        self._storage.save_policy(policy.to_dict())
        return policy

    def _handle_analyze(self, command: str) -> Dict[str, Any]:
        content = self._extract_content(command, ["analyze", "check risk", "risk check", "scan command", "security check"])
        if not content:
            return {
                "success": False,
                "response": "Please provide a command to analyze. Example: 'analyze rm -rf /tmp'",
            }

        assessment = self._analyzer.analyze(content)
        lines = [
            f"Security Analysis for: {content[:80]}",
            f"Risk Level: {assessment.risk_level.value.upper()}",
            f"Risk Score: {assessment.risk_score:.2f}/1.00",
            f"Blocked: {'Yes' if assessment.blocked else 'No'}",
        ]

        if assessment.block_reason:
            lines.append(f"Block Reason: {assessment.block_reason}")

        if assessment.threats:
            lines.append(f"\nThreats Detected ({len(assessment.threats)}):")
            for t in assessment.threats:
                lines.append(f"  - {t.value}")

        if assessment.reasons:
            lines.append(f"\nReasons:")
            for r in assessment.reasons:
                lines.append(f"  - {r}")

        if assessment.suggestions:
            lines.append(f"\nSuggestions:")
            for s in assessment.suggestions:
                lines.append(f"  - {s}")

        perm_check = self._permissions.check_permission(content)
        lines.append(f"\nPermission Check: {'Permitted' if perm_check['permitted'] else 'Denied'}")
        if not perm_check["permitted"]:
            lines.append(f"  Required: {perm_check['required_level']}, Message: {perm_check['message']}")

        self._audit.log(
            action=AuditAction.SECURITY_SCAN,
            actor="user",
            target=content[:100],
            details=f"Risk: {assessment.risk_level.value}, Score: {assessment.risk_score:.2f}",
            risk_level=assessment.risk_level,
        )

        return {"success": True, "response": "\n".join(lines), "data": assessment.to_dict()}

    def _handle_override(self, command: str) -> Dict[str, Any]:
        content = self._extract_content(command, ["block", "allow", "force execute", "override"])
        if not content:
            return {
                "success": False,
                "response": "Please provide a command to override. Example: 'force execute rm -rf /tmp'",
            }

        assessment = self._analyzer.analyze(content)

        def dummy_executor():
            return f"Executed (simulated): {content[:80]}"

        result = self._executor.execute_with_validation(
            content, dummy_executor, actor="user", force=True,
        )

        lines = [
            f"Security Override for: {content[:80]}",
            f"Original Risk: {assessment.risk_level.value.upper()}",
            f"Override: {'Success' if result.get('success') else 'Failed'}",
        ]
        if result.get("block_reason"):
            lines.append(f"Note: {result['block_reason']}")

        return {"success": True, "response": "\n".join(lines), "data": result}

    def _handle_health_check(self, command: str) -> Dict[str, Any]:
        health = self._monitor.check_system_health()

        lines = [
            "System Health Report:",
            f"CPU: {health['cpu_percent']:.1f}%",
            f"Memory: {health['memory_percent']:.1f}% ({health['memory_used_gb']:.1f}GB / {health['memory_total_gb']:.1f}GB)",
            f"Disk: {health['disk_percent']:.1f}% ({health['disk_used_gb']:.1f}GB / {health['disk_total_gb']:.1f}GB)",
            f"Processes: {health['process_count']}",
            f"Network Connections: {health['network_connections']}",
            f"Overall Status: {'Healthy' if health['healthy'] else 'Alerts Detected'}",
        ]

        if health["alerts"]:
            lines.append("\nAlerts:")
            for alert in health["alerts"]:
                lines.append(f"  - {alert}")

        if health["suspicious_processes"]:
            lines.append(f"\nSuspicious Processes ({len(health['suspicious_processes'])}):")
            for proc in health["suspicious_processes"][:5]:
                lines.append(f"  - {proc.get('name', 'unknown')} (PID: {proc.get('pid')})")

        self._audit.log(
            action=AuditAction.SECURITY_SCAN,
            actor="user",
            target="system_health",
            details=f"Status: {'healthy' if health['healthy'] else 'alerts'}",
        )

        return {"success": True, "response": "\n".join(lines), "data": health}

    def _handle_process_scan(self, command: str) -> Dict[str, Any]:
        suspicious = self._monitor.scan_processes()

        if not suspicious:
            return {
                "success": True,
                "response": "No suspicious processes detected.",
                "data": {"count": 0},
            }

        lines = [f"Suspicious Processes Found ({len(suspicious)}):\n"]
        for proc in suspicious[:20]:
            lines.append(f"  PID: {proc['pid']}")
            lines.append(f"  Name: {proc['name']}")
            lines.append(f"  Reason: {proc['reason']}")
            if proc.get("cmdline"):
                lines.append(f"  Command: {proc['cmdline'][:100]}")
            lines.append("")

        self._audit.log(
            action=AuditAction.SECURITY_SCAN,
            actor="user",
            target="process_scan",
            details=f"Found {len(suspicious)} suspicious processes",
            risk_level=RiskLevel.MEDIUM if suspicious else RiskLevel.SAFE,
        )

        return {"success": True, "response": "\n".join(lines), "data": {"processes": suspicious}}

    def _handle_start_monitoring(self, command: str) -> Dict[str, Any]:
        interval = self._extract_number(command, default=30)
        result = self._monitor.start_monitoring(interval)
        self._monitoring_active = result.get("success", False)

        response = result.get("message", "Unknown")
        if result.get("success"):
            response += f" (interval: {interval}s)"

        return {"success": result.get("success", False), "response": response}

    def _handle_stop_monitoring(self, command: str) -> Dict[str, Any]:
        result = self._monitor.stop_monitoring()
        self._monitoring_active = not result.get("success", False)
        return {"success": result.get("success", False), "response": result.get("message", "Unknown")}

    def _handle_events(self, command: str) -> Dict[str, Any]:
        risk_filter = None
        if "critical" in command.lower():
            risk_filter = "critical"
        elif "high" in command.lower():
            risk_filter = "high"

        events = self._storage.get_events(limit=20, risk_level=risk_filter)

        if not events:
            filter_msg = f" ({risk_filter} risk)" if risk_filter else ""
            return {
                "success": True,
                "response": f"No security events found{filter_msg}.",
                "data": {"count": 0},
            }

        lines = [f"Security Events ({len(events)}):\n"]
        for event in events:
            lines.append(f"  [{event['timestamp'][:19]}] {event['risk_level'].upper()} - {event['description']}")
            lines.append(f"    Source: {event['source']}, Type: {event['event_type']}")
            lines.append("")

        return {"success": True, "response": "\n".join(lines), "data": {"events": events}}

    def _handle_audit_log(self, command: str) -> Dict[str, Any]:
        records = self._storage.get_audit_records(limit=30)

        if not records:
            return {
                "success": True,
                "response": "No audit records found.",
                "data": {"count": 0},
            }

        lines = [f"Audit Log ({len(records)} records):\n"]
        for record in records:
            lines.append(f"  [{record['timestamp'][:19]}] {record['action']}")
            lines.append(f"    Actor: {record['actor']}, Target: {record['target'][:60]}")
            if record.get("details"):
                lines.append(f"    Details: {record['details'][:80]}")
            lines.append("")

        return {"success": True, "response": "\n".join(lines), "data": {"records": records}}

    def _handle_alerts(self, command: str) -> Dict[str, Any]:
        unresolved = "unresolved" in command.lower() or "active" in command.lower()
        alerts = self._storage.get_alerts(limit=20, unresolved_only=unresolved)

        if not alerts:
            filter_msg = " unresolved" if unresolved else ""
            return {
                "success": True,
                "response": f"No{filter_msg} security alerts.",
                "data": {"count": 0},
            }

        lines = [f"Security Alerts ({len(alerts)}):\n"]
        for alert in alerts:
            status = "RESOLVED" if alert.get("resolved") else ("ACKNOWLEDGED" if alert.get("acknowledged") else "ACTIVE")
            lines.append(f"  [{alert['severity'].upper()}] [{status}] {alert['title']}")
            lines.append(f"    {alert['message'][:100]}")
            lines.append(f"    Created: {alert['created_at'][:19]}")
            lines.append("")

        return {"success": True, "response": "\n".join(lines), "data": {"alerts": alerts}}

    def _handle_permissions(self, command: str) -> Dict[str, Any]:
        rules = self._permissions.list_rules()

        if not rules:
            return {
                "success": True,
                "response": "No permission rules configured.",
                "data": {"count": 0},
            }

        lines = [f"Permission Rules ({len(rules)}):\n"]
        for rule in rules:
            status = "ENABLED" if rule.enabled else "DISABLED"
            lines.append(f"  [{status}] {rule.name}")
            lines.append(f"    Pattern: {rule.pattern}")
            lines.append(f"    Required: {rule.required_level.value}")
            if rule.description:
                lines.append(f"    Description: {rule.description}")
            lines.append("")

        return {"success": True, "response": "\n".join(lines), "data": {"rules": [r.to_dict() for r in rules]}}

    def _handle_add_permission(self, command: str) -> Dict[str, Any]:
        parts = command.lower().split(None, 3)
        if len(parts) < 4:
            return {
                "success": False,
                "response": "Usage: 'add permission <name> <level> <pattern>'. Example: 'add permission network_config admin netsh'",
            }

        name = parts[2]
        rest = parts[3]
        level_parts = rest.split()
        if level_parts[0] in ("read", "write", "execute", "admin", "system"):
            level = PermissionLevel(level_parts[0])
            pattern = " ".join(level_parts[1:])
        else:
            level = PermissionLevel.ADMIN
            pattern = rest

        rule = PermissionRule(
            name=name,
            pattern=pattern,
            required_level=level,
            description=f"Custom rule: {name}",
        )
        self._permissions.add_rule(rule)

        return {
            "success": True,
            "response": f"Permission rule added: {name} (level: {level.value}, pattern: {pattern})",
        }

    def _handle_remove_permission(self, command: str) -> Dict[str, Any]:
        rule_id = self._extract_id(command)
        if not rule_id:
            return {
                "success": False,
                "response": "Please provide a rule ID. Example: 'remove permission abc12345'",
            }

        success = self._permissions.remove_rule(rule_id)
        if success:
            return {"success": True, "response": f"Permission rule {rule_id} removed."}
        return {"success": False, "response": f"Rule {rule_id} not found."}

    def _handle_file_protection(self, command: str) -> Dict[str, Any]:
        rules = self._storage.get_file_protection_rules()

        if not rules:
            return {
                "success": True,
                "response": "No file protection rules configured. Use 'add protection <path>' to create one.",
                "data": {"count": 0},
            }

        lines = [f"File Protection Rules ({len(rules)}):\n"]
        for rule in rules:
            lines.append(f"  {rule['path_pattern']}")
            lines.append(f"    Level: {rule['protection_level']}")
            if rule.get("description"):
                lines.append(f"    Description: {rule['description']}")
            lines.append("")

        return {"success": True, "response": "\n".join(lines), "data": {"rules": rules}}

    def _handle_add_protection(self, command: str) -> Dict[str, Any]:
        content = self._extract_content(command, ["add protection", "protect path"])
        if not content:
            return {
                "success": False,
                "response": "Please provide a path pattern. Example: 'protect path C:\\Windows\\System32\\*.dll'",
            }

        rule = FileProtectionRule(
            path_pattern=content,
            protection_level="read",
            description=f"Protected: {content}",
        )
        self._storage.save_file_protection_rule(rule.to_dict())

        return {
            "success": True,
            "response": f"File protection rule added: {content}",
        }

    def _handle_policy(self, command: str) -> Dict[str, Any]:
        policy = self._policy

        lines = [
            "Security Policy:",
            f"Name: {policy.name}",
            f"Max Risk Level: {policy.max_risk_level.value}",
            f"Auto-Block Critical: {'Yes' if policy.auto_block_critical else 'No'}",
            f"Audit Enabled: {'Yes' if policy.audit_enabled else 'No'}",
            f"Monitor Processes: {'Yes' if policy.monitor_processes else 'No'}",
            f"Monitor Files: {'Yes' if policy.monitor_files else 'No'}",
            f"Monitor Network: {'Yes' if policy.monitor_network else 'No'}",
            f"Alert on Suspicious: {'Yes' if policy.alert_on_suspicious else 'No'}",
            f"Safe Execution Mode: {'Yes' if policy.safe_execution_mode else 'No'}",
            f"Monitoring Active: {'Yes' if self._monitoring_active else 'No'}",
        ]

        return {"success": True, "response": "\n".join(lines), "data": policy.to_dict()}

    def _handle_set_policy(self, command: str) -> Dict[str, Any]:
        content = self._extract_content(command, ["set policy", "update policy", "change policy"])
        if not content:
            return {
                "success": False,
                "response": "Usage: 'set policy <setting> <value>'. Example: 'set policy max_risk_level high'",
            }

        parts = content.lower().split(None, 1)
        if len(parts) < 2:
            return {"success": False, "response": "Please provide both setting and value."}

        setting, value = parts
        updates = {}

        if setting == "max_risk_level":
            if value in ("safe", "low", "medium", "high", "critical"):
                self._policy.max_risk_level = RiskLevel(value)
                updates["max_risk_level"] = value
            else:
                return {"success": False, "response": f"Invalid risk level: {value}. Use: safe, low, medium, high, critical"}
        elif setting == "auto_block_critical":
            self._policy.auto_block_critical = value in ("true", "yes", "1", "on")
            updates["auto_block_critical"] = self._policy.auto_block_critical
        elif setting == "audit_enabled":
            self._policy.audit_enabled = value in ("true", "yes", "1", "on")
            updates["audit_enabled"] = self._policy.audit_enabled
        elif setting == "monitor_processes":
            self._policy.monitor_processes = value in ("true", "yes", "1", "on")
            updates["monitor_processes"] = self._policy.monitor_processes
        elif setting == "monitor_files":
            self._policy.monitor_files = value in ("true", "yes", "1", "on")
            updates["monitor_files"] = self._policy.monitor_files
        elif setting == "safe_execution_mode":
            self._policy.safe_execution_mode = value in ("true", "yes", "1", "on")
            updates["safe_execution_mode"] = self._policy.safe_execution_mode
        else:
            return {"success": False, "response": f"Unknown setting: {setting}"}

        self._policy.updated_at = datetime.now().isoformat()
        self._storage.save_policy(self._policy.to_dict())

        lines = [f"Policy updated: {setting} = {value}"]
        lines.append(f"Max risk level: {self._policy.max_risk_level.value}")

        return {"success": True, "response": "\n".join(lines), "data": updates}

    def _handle_stats(self, command: str) -> Dict[str, Any]:
        stats = self._storage.get_stats()

        lines = [
            "Security Statistics:",
            f"Total Events: {stats['total_events']}",
            f"Risk Assessments: {stats['total_assessments']}",
            f"Audit Records: {stats['total_audit_records']}",
            f"Total Alerts: {stats['total_alerts']}",
            f"Unresolved Alerts: {stats['unresolved_alerts']}",
            f"Critical Events: {stats['critical_events']}",
            f"High Risk Events: {stats['high_risk_events']}",
            f"Blocked Commands: {stats['blocked_commands']}",
        ]

        return {"success": True, "response": "\n".join(lines), "data": stats}

    def _handle_validate_workflow(self, command: str) -> Dict[str, Any]:
        content = self._extract_content(command, ["validate workflow", "workflow security", "check workflow"])
        if not content:
            return {
                "success": False,
                "response": "Please provide workflow name and steps. Example: 'validate workflow my_workflow step1, step2, step3'",
            }

        parts = content.split(None, 1)
        workflow_name = parts[0]
        steps = [{"command": s.strip()} for s in parts[1].split(",")] if len(parts) > 1 else []

        if not steps:
            return {"success": False, "response": "Please provide at least one workflow step."}

        result = self._executor.validate_workflow(workflow_name, steps)

        lines = [
            f"Workflow Validation: {workflow_name}",
            f"Steps: {result['total_steps']}",
            f"Safe: {'Yes' if result['safe'] else 'No'}",
            f"Max Risk: {result['max_risk']}",
        ]

        if result["blocked_steps"]:
            lines.append(f"\nBlocked Steps ({len(result['blocked_steps'])}):")
            for step in result["blocked_steps"]:
                lines.append(f"  Step {step['step']}: {step['command'][:50]} ({step['block_reason']})")

        return {"success": True, "response": "\n".join(lines), "data": result}

    def _handle_execution_log(self, command: str) -> Dict[str, Any]:
        log = self._executor.get_execution_log(limit=20)

        if not log:
            return {
                "success": True,
                "response": "No execution log entries.",
                "data": {"count": 0},
            }

        lines = [f"Execution Log ({len(log)} entries):\n"]
        for entry in log:
            status = "OK" if entry.get("success") else "FAIL"
            lines.append(f"  [{entry['timestamp'][:19]}] [{status}] {entry['command'][:60]}")
            lines.append(f"    Duration: {entry.get('duration', 0):.2f}s")
            lines.append("")

        return {"success": True, "response": "\n".join(lines), "data": {"log": log}}

    def _handle_help(self, command: str) -> Dict[str, Any]:
        lines = [
            "Security Agent Commands:",
            "",
            "Risk Analysis:",
            "  analyze <command>     - Analyze a command for security risks",
            "  force execute <cmd>   - Execute a command overriding security blocks",
            "",
            "System Monitoring:",
            "  system health         - Check system health status",
            "  process scan          - Scan for suspicious processes",
            "  start monitoring      - Start background security monitoring",
            "  stop monitoring       - Stop background monitoring",
            "",
            "Events & Audit:",
            "  events                - List security events",
            "  events critical       - List only critical events",
            "  audit log             - View audit trail",
            "  alerts                - List active security alerts",
            "",
            "Permissions:",
            "  permissions           - List permission rules",
            "  add permission <n> <l> <p> - Add a permission rule",
            "  remove permission <id>     - Remove a permission rule",
            "",
            "File Protection:",
            "  file protection       - List file protection rules",
            "  add protection <path> - Add a file protection rule",
            "",
            "Policy:",
            "  policy                - Show current security policy",
            "  set policy <setting> <value> - Update policy setting",
            "",
            "Other:",
            "  stats                 - Show security statistics",
            "  validate workflow <name> <steps> - Validate workflow security",
            "  execution log         - View execution log",
        ]

        return {"success": True, "response": "\n".join(lines)}

    @staticmethod
    def _matches(text: str, keywords: list) -> bool:
        return any(kw in text for kw in keywords)

    @staticmethod
    def _extract_content(command: str, prefixes: list) -> str:
        lower = command.lower()
        for prefix in prefixes:
            if lower.startswith(prefix):
                return command[len(prefix):].strip()
            idx = lower.find(prefix)
            if idx >= 0:
                return command[idx + len(prefix):].strip()
        return command.strip()

    @staticmethod
    def _extract_id(command: str) -> str:
        import re
        match = re.search(r'\b([a-f0-9]{8})\b', command)
        return match.group(1) if match else ""

    @staticmethod
    def _extract_number(command: str, default: int = 0) -> int:
        import re
        match = re.search(r'\b(\d+)\b', command)
        return int(match.group(1)) if match else default
