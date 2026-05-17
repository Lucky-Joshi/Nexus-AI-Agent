# Security Agent

> **NEXUS Agent** — System security monitoring, risk analysis, permission management, and audit logging.

## Purpose

The Security Agent provides comprehensive security oversight for the NEXUS system. It analyzes commands and actions for risks, enforces permission rules, maintains an immutable audit trail, monitors system health, scans for suspicious processes, and manages a configurable security policy. It acts as the security gatekeeper for all agent operations.

## Architecture

```
security_agent/
├── __init__.py          # Package initialization
├── agent.py             # Main orchestrator (SecurityAgent)
├── models.py            # Data models (SecurityEvent, RiskAssessment, PermissionRule, etc.)
├── services.py          # Core security services
│   ├── RiskAnalyzer        # Command/action risk analysis with pattern matching
│   ├── PermissionManager   # Role-based permission rule enforcement
│   ├── AuditLogger         # Immutable audit trail logging
│   ├── SafeExecutor        # Security-validated command execution
│   └── MonitorService      # Real-time system health and process monitoring
└── storage.py           # SQLite persistence for all security data
```

The agent follows a defense-in-depth approach: risk analysis, permission checks, audit logging, and safe execution are separate layers that work together. The `MonitorService` runs background health checks on a configurable interval.

## Capabilities

| Capability | Description |
|---|---|
| `analyze_command` | Analyze a command for security risks with detailed threat report |
| `override_security` | Execute a command with security override (force) |
| `system_health_check` | Comprehensive system health report (CPU, memory, disk, processes, network) |
| `process_scan` | Scan running processes for suspicious activity |
| `start_monitoring` / `stop_monitoring` | Background security monitoring with configurable interval |
| `list_events` | View security events, filterable by risk level |
| `audit_log` | View immutable audit trail of all security-relevant actions |
| `list_alerts` | View active/resolved security alerts |
| `manage_permissions` | List, add, and remove permission rules |
| `file_protection` | Manage file/directory protection rules |
| `policy_management` | View and update security policy settings |
| `security_stats` | Security statistics dashboard |
| `validate_workflow` | Pre-validate an entire workflow for security risks |
| `execution_log` | View execution history with success/failure status |

## Internal Structure

### Data Models (`models.py`)

- **`SecurityEvent`** — Detected security event with type, risk level, source, and description
- **`RiskAssessment`** — Analysis result with risk level, score, threats, reasons, suggestions, and block decision
- **`PermissionRule`** — Rule with name, regex pattern, required permission level, and enabled state
- **`AuditRecord`** — Immutable log entry with action, actor, target, details, and risk level
- **`FileProtectionRule`** — Path pattern with protection level
- **`SecurityAlert`** — Alert with severity, title, message, acknowledgment, and resolution state
- **`SecurityPolicy`** — Global policy configuration (max risk level, auto-block, monitoring toggles)
- **`RiskLevel`** enum: safe, low, medium, high, critical
- **`ThreatType`** enum: none, suspicious_command, privilege_escalation, file_tampering, network_anomaly, process_injection, resource_abuse, unauthorized_access, malware_indicator, policy_violation
- **`PermissionLevel`** enum: none, read, write, execute, admin, system
- **`AuditAction`** enum: 16 action types covering command execution, file access, process management, workflow lifecycle, and policy changes

### Services (`services.py`)

- **`RiskAnalyzer`** — 30+ dangerous command patterns and 15+ suspicious patterns compiled as regex. Scores threats on a 0-10 scale, normalizes to 0-1. Auto-blocks critical risks. Supports context-aware analysis (source tracking, file protection violation checks).
- **`PermissionManager`** — 8 default permission rules (system config, network, user management, file delete, execute, process management, scheduled tasks, services). Pattern-based rule matching with actor level comparison.
- **`AuditLogger`** — Thread-safe immutable logging with action filtering, actor-based queries, and time-window summaries.
- **`SafeExecutor`** — Executes commands after risk analysis and permission checks. Validates entire workflows step-by-step before execution. Maintains execution log with timing.
- **`MonitorService`** — Background monitoring via `psutil`: CPU, memory, disk, process count, network connections. Suspicious process detection (cmd.exe, powershell.exe, mshta.exe, rundll32.exe, certutil.exe, etc.). Configurable alert thresholds. Event callbacks.

### Storage (`storage.py`)

- SQLite with 7 tables: `security_events`, `risk_assessments`, `permission_rules`, `audit_records`, `file_protection_rules`, `security_alerts`, `security_policies`
- Indexed by timestamp, risk level, severity, and resolution state

## Usage Examples

### Natural Language Commands

```
analyze rm -rf /tmp/cache
system health
process scan
start monitoring 30
events critical
audit log
alerts
permissions
add permission network_config admin netsh
file protection
add protection C:\Windows\System32\*.dll
policy
set policy max_risk_level high
stats
validate workflow deploy step1: git pull, step2: npm install, step3: npm build
execution log
```

### Programmatic API

```python
from agents.security_agent.agent import SecurityAgent

agent = SecurityAgent()

# Analyze a command for risks
assessment = agent.analyze_command("net user hacker P@ss /add")
print(f"Risk: {assessment.risk_level.value}, Score: {assessment.risk_score}")

# Check permissions
perm = agent.check_permission("reg delete HKLM\\Software", actor="user")

# Execute safely
result = agent.execute_safely("dir", lambda: "done", actor="user")

# Get system health
health = agent.get_system_health()

# Scan processes
suspicious = agent.scan_processes()

# Validate a workflow
validation = agent.validate_workflow("deploy", [
    {"command": "git pull"},
    {"command": "npm install"},
    {"command": "npm run build"},
])
```

## Configuration

| Config Key | Default | Description |
|---|---|---|
| `security_policy.max_risk_level` | `medium` | Maximum allowed risk level for execution |
| `security_policy.auto_block_critical` | `true` | Automatically block critical-risk commands |
| `security_policy.audit_enabled` | `true` | Enable audit logging |
| `security_policy.monitor_processes` | `true` | Enable process monitoring |
| `security_policy.monitor_files` | `true` | Enable file monitoring |
| `security_policy.monitor_network` | `false` | Enable network monitoring |
| `security_policy.alert_on_suspicious` | `true` | Generate alerts for suspicious activity |
| `security_policy.safe_execution_mode` | `true` | Require security validation before execution |

## Security Model

1. **Risk analysis** — Every command analyzed against 45+ patterns before execution
2. **Permission enforcement** — Role-based access control with 6 permission levels
3. **Policy-driven** — Global policy controls auto-blocking, monitoring, and audit settings
4. **Immutable audit trail** — All security-relevant actions logged with actor, target, and timestamp
5. **File protection** — Path-based protection rules prevent modification of critical files
6. **Workflow validation** — Entire workflows validated before any step executes
7. **Background monitoring** — Continuous system health and process scanning

## Dependencies

- `psutil` — System monitoring (CPU, memory, disk, processes, network)
- `re` (built-in) — Pattern matching for threat detection
- `threading` (built-in) — Background monitoring thread
- SQLite (built-in) — Persistent security data storage
