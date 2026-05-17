# Analytics Agent

> System usage tracking, agent performance metrics, productivity analysis, and resource monitoring for NEXUS.

## Purpose

The Analytics Agent provides comprehensive observability into NEXUS operations. It tracks every command execution, measures agent performance, monitors system resources, calculates productivity scores, and generates actionable reports. This data enables users to understand how NEXUS is being used, identify bottlenecks, optimize workflows, and measure the impact of automation over time.

## Architecture

```
analytics_agent/
├── __init__.py
├── agent.py              # AnalyticsAgent orchestrator
├── models.py             # TimeRange, ReportFormat, AnalyticsRecord, PerformanceMetric
├── services.py           # AnalyticsEngine (CommandTracker, PerformanceCollector, Reporter, ResourceMonitor, ProductivityTracker)
├── storage.py            # AnalyticsStorage - SQLite/JSON persistence
```

### Component Breakdown

| Component | Responsibility |
|-----------|---------------|
| `AnalyticsEngine` | Central coordinator that delegates to specialized sub-engines |
| `CommandTracker` | Records every command execution with agent, duration, success/failure, and session context |
| `PerformanceCollector` | Aggregates per-agent metrics: call counts, success rates, error patterns, latency distributions |
| `Reporter` | Generates usage reports, productivity reports, and recommendations based on collected data |
| `ResourceMonitor` | Captures CPU, memory, disk, process count, and network connection snapshots at configurable intervals |
| `ProductivityTracker` | Manages productivity sessions, calculates focus scores, tracks workflows and interruptions |
| `AnalyticsStorage` | Persistent storage for all analytics data with time-range queries and cleanup |

### Data Collection Pipeline

```
Agent Execution
    │
    ▼
┌──────────────────┐
│ CommandTracker   │  Record: agent, command, result, duration, session
└────────┬─────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌───────┐ ┌──────────────┐
│ Perf. │ │ Productivity │
│ Coll. │ │ Tracker      │
└───┬───┘ └──────┬───────┘
    │            │
    ▼            ▼
┌──────────────────────┐
│   AnalyticsStorage   │  Time-series data with queries
└──────────┬───────────┘
           │
           ▼
┌──────────────────┐
│   Reporter       │  Dashboards, reports, recommendations
└──────────────────┘
```

## Capabilities

### Dashboard & Overview

| Command | Description |
|---------|-------------|
| `dashboard` | Show comprehensive analytics dashboard |
| `usage stats [agent]` | Show usage statistics (optionally filtered by agent) |
| `top agents` | Show most frequently used agents |

### Reports

| Command | Description |
|---------|-------------|
| `usage report [day/week/month]` | Generate usage report for time range |
| `productivity report` | Generate productivity analysis report |
| `agent performance` | Show detailed agent performance metrics |
| `reports` | List saved reports |

### Resource Monitoring

| Command | Description |
|---------|-------------|
| `resource monitor` | Show resource usage history |
| `resource snapshot` | Capture current system resources |
| `start monitoring [sec]` | Start continuous resource monitoring |
| `stop monitoring` | Stop resource monitoring |

### Productivity Sessions

| Command | Description |
|---------|-------------|
| `start session [type]` | Start a productivity session |
| `end session [id]` | End a productivity session |
| `session history` | Show past productivity sessions |
| `productivity summary` | Show productivity summary (weekly/monthly) |

### Activity Analysis

| Command | Description |
|---------|-------------|
| `hourly activity` | Show command distribution by hour |
| `daily activity [days]` | Show daily command activity |
| `recent activity [count]` | Show most recent commands |

### Maintenance

| Command | Description |
|---------|-------------|
| `cleanup [days]` | Remove analytics records older than specified days |

### Programmatic API

```python
# Track an agent execution
analytics_agent.track_execution(
    agent_name="file_agent",
    command="open vscode",
    result={"success": True},
    duration=1.23,
    session_id="abc123",
)
```

## Internal Structure

### Dashboard Data Model

```python
@dataclass
class Dashboard:
    total_commands: int
    total_agents_used: int
    active_sessions: int
    avg_response_time: float
    success_rate: float
    productivity_score: float          # 0-10 scale
    top_agents: list[dict]             # agent_name, count, success_rate
    recent_activity: list[dict]        # timestamp, agent, action, success
    resource_usage: dict               # cpu, memory, disk percentages
```

### Performance Metric Model

```python
@dataclass
class AgentPerformance:
    agent_name: str
    total_calls: int
    successful_calls: int
    failed_calls: int
    success_rate: float
    avg_duration: float
    min_duration: float
    max_duration: float
    error_counts: dict[str, int]       # error_message -> count
```

### Resource Snapshot Model

```python
@dataclass
class ResourceSnapshot:
    timestamp: str
    cpu_percent: float
    memory_percent: float
    memory_used_gb: float
    memory_total_gb: float
    disk_percent: float
    disk_used_gb: float
    disk_total_gb: float
    process_count: int
    network_connections: int
    uptime_seconds: int
```

## Usage Examples

### Dashboard

```
> dashboard
NEXUS Analytics Dashboard
========================================
Total Commands: 1,247
Agents Used: 12
Active Sessions: 2
Avg Response Time: 0.842s
Success Rate: 97.3%
Productivity Score: 7.8/10

Top Agents:
  file_agent: 342 calls (98% success)
  web_agent: 218 calls (96% success)
  coding_agent: 187 calls (99% success)

System Resources:
  CPU: 23.4%
  Memory: 61.2%
  Disk: 45.8%
```

### Productivity Session

```
> start session coding
Productivity session started (ID: a1b2c3d4, Type: coding)

... work for 45 minutes ...

> end session a1b2c3d4
Session ended: 45.2 minutes, 23 commands, Focus Score: 8.5/10
```

### Resource Monitoring

```
> start monitoring 60
Resource monitoring started (interval: 60s)

> resource snapshot
Resource Snapshot:
CPU: 34.2%
Memory: 62.1% (16.4GB / 32.0GB)
Disk: 45.8% (228.9GB / 500.0GB)
Processes: 187
Network Connections: 42
Uptime: 12.3h
```

### Performance Report

```
> agent performance
Agent Performance:

  file_agent
    Calls: 342 (Success: 335, Failed: 7)
    Success Rate: 98.0%
    Avg Duration: 0.421s (Min: 0.012s, Max: 3.847s)
    Top Errors: Permission denied(3), File not found(2)
```

## Configuration

```json
{
  "agents": {
    "analytics_agent": {
      "enabled": true,
      "auto_track": true,
      "resource_monitor_interval": 60,
      "retention_days": 90,
      "productivity_enabled": true,
      "dashboard_refresh_seconds": 30
    }
  }
}
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | bool | `true` | Enable/disable the agent |
| `auto_track` | bool | `true` | Automatically track all agent executions |
| `resource_monitor_interval` | int | `60` | Resource snapshot interval in seconds |
| `retention_days` | int | `90` | How long to retain analytics data |
| `productivity_enabled` | bool | `true` | Enable productivity session tracking |
| `dashboard_refresh_seconds` | int | `30` | Dashboard auto-refresh interval |

## Dependencies

| Dependency | Source | Purpose |
|------------|--------|---------|
| `core.base_agent` | Local | BaseAgent, AgentStatus |
| `core.config` | Local | Configuration access |
| `core.logger` | Local | Structured logging |
| `time` | stdlib | Timestamps and duration tracking |
