# Context Awareness Agent

> Real-time user activity detection, contextual understanding, focus monitoring, workflow suggestions, and adaptive automation for NEXUS.

## Purpose

The Context Awareness Agent continuously monitors and interprets the user's current working context -- active applications, window focus, system load, time of day, and behavioral patterns. It uses this understanding to suggest appropriate workflow modes, trigger adaptive automation, and enable other agents to respond in a contextually relevant manner. This transforms NEXUS from a reactive tool into a proactive assistant that anticipates user needs.

## Architecture

```
context_awareness_agent/
├── __init__.py
├── agent.py              # ContextAwarenessAgent orchestrator
├── models.py             # ActivityType, ContextConfidence, FocusLevel, UserContext, AdaptiveTrigger
├── services.py           # ContextDetector, WorkflowDetector, AdaptiveTriggerSystem, ContextHistory
├── storage.py            # ContextStorage - persistence for context snapshots, rules, triggers
```

### Component Breakdown

| Component | Responsibility |
|-----------|---------------|
| `ContextDetector` | Detects current context by analyzing active window, running apps, system load, and time patterns |
| `WorkflowDetector` | Matches current context against known workflow patterns to suggest appropriate modes |
| `AdaptiveTriggerSystem` | Evaluates context against user-defined triggers and executes automated actions |
| `ContextHistory` | Maintains a timeline of context snapshots for historical analysis and pattern detection |
| `ContextStorage` | Persistent storage for context records, rules, triggers, and session data |

### Context Detection Pipeline

```
┌─────────────────┐
│ Active Window   │  Title, process name, PID, duration
└────────┬────────┘
         │
┌────────┴────────┐
│ Running Apps    │  Process list, categories, memory usage
└────────┬────────┘
         │
┌────────┴────────┐
│ System Load     │  CPU, memory, disk, process count
└────────┬────────┘
         │
┌────────┴────────┐
│ Time Context    │  Hour, day, work hours, weekend
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│   ContextDetector       │  Fuse signals -> ActivityType + FocusLevel
└────────┬────────────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌───────┐ ┌──────────────┐
│ Work- │ │ Adaptive     │
│ flow  │ │ Triggers     │
│ Det.  │ │ System       │
└───────┘ └──────────────┘
```

## Capabilities

### Context Detection

| Command | Description |
|---------|-------------|
| `current context` | Show full context snapshot (activity, focus, window, system) |
| `active window` | Show current active window details |
| `running apps [category]` | List running applications, optionally filtered by category |
| `activity type` | Show detected activity type with confidence |
| `focus level` | Show current focus level and description |
| `system load` | Show CPU, memory, disk, and process information |

### Workflow Suggestions

| Command | Description |
|---------|-------------|
| `suggest workflow` | Suggest workflow mode based on current context |
| `suggest actions` | Show contextual action suggestions |
| `detect workflow` | Detect current workflow pattern |
| `workflow patterns` | List all defined workflow patterns |

### Monitoring

| Command | Description |
|---------|-------------|
| `start monitoring [sec]` | Start continuous context monitoring |
| `stop monitoring` | Stop context monitoring |

### Adaptive Triggers

| Command | Description |
|---------|-------------|
| `triggers` | List all adaptive triggers |
| `add trigger <name>` | Add a new adaptive trigger |
| `toggle trigger <id>` | Enable/disable a trigger |

### History & Sessions

| Command | Description |
|---------|-------------|
| `context history` | Show recent context snapshots |
| `activity summary [days]` | Show activity summary over time |
| `session start [type]` | Start a new context session |
| `session end` | End current context session |

### Rules

| Command | Description |
|---------|-------------|
| `context rules` | List context rules |
| `add rule <definition>` | Add a context rule |
| `delete rule <id>` | Delete a context rule |

### Maintenance

| Command | Description |
|---------|-------------|
| `cleanup [days]` | Clean up old context records |

### Programmatic API

```python
# Get current context
context = context_agent.get_current_context()
print(context.activity.value)        # "coding", "browsing", "meeting", etc.
print(context.focus_level.value)     # "deep", "focused", "moderate", "distracted", "idle"

# Get specific context attributes
activity = context_agent.get_activity_type()
focus = context_agent.get_focus_level()

# Check if a workflow mode should be suggested
suggested_mode = context_agent.should_suggest_mode()
```

## Internal Structure

### User Context Model

```python
@dataclass
class UserContext:
    timestamp: str
    activity: ActivityType           # coding, browsing, meeting, reading, gaming, etc.
    activity_confidence: ContextConfidence  # low, medium, high, very_high
    focus_level: FocusLevel          # deep, focused, moderate, distracted, idle
    session_type: str
    active_window: WindowInfo        # title, process_name, pid, duration
    running_apps: list[AppInfo]      # name, category, memory usage
    system_load: SystemLoadInfo      # cpu, memory, disk percentages
    time_context: TimeContext        # period, is_work_hours, is_weekday
    context_signals: list[str]       # detection signals
    suggested_workflow: str          # e.g., "coding", "research"
    suggested_actions: list[str]     # contextual suggestions
```

### Activity Types

`coding`, `browsing`, `meeting`, `reading`, `writing`, `gaming`, `media`, `communication`, `design`, `development`, `research`, `idle`, `unknown`

### Focus Levels

| Level | Description |
|-------|-------------|
| `deep` | Single task, minimal context switches |
| `focused` | Primary task with occasional switches |
| `moderate` | Multiple tasks, regular switching |
| `distracted` | Browsing, media, or entertainment |
| `idle` | No active window detected |

### Adaptive Trigger Model

```python
@dataclass
class AdaptiveTrigger:
    id: str
    name: str
    description: str
    condition_activity: ActivityType       # Trigger when this activity detected
    condition_apps: list[str]              # Trigger when these apps are running
    condition_time: str                    # Time-based condition
    action: TriggerAction                  # suggest_workflow, silence_notifications, save_context
    action_target: str                     # Target for the action
    enabled: bool
    trigger_count: int                     # How many times fired
```

## Usage Examples

### Current Context

```
> current context
Current Context:
========================================
Activity: coding (high confidence)
Focus Level: deep
Session Type: development
Session Duration: 45.2 minutes

Active Window:
  Title: main.py - Visual Studio Code
  Process: Code.exe
  Duration: 2712s

System Load: moderate
  CPU: 34.2%
  Memory: 61.5%

Suggested Workflow: coding
```

### Workflow Suggestions

```
> suggest workflow
Detected Workflows (2):

  coding_session (85% confidence)
    Suggested: coding
    Description: Active development with IDE and terminal
    Matching apps: Code.exe, terminal.exe

  research_mode (30% confidence)
    Suggested: research
    Description: Browser with documentation tabs
    Matching apps: chrome.exe
```

### Context Monitoring

```
> start monitoring 10
Context monitoring started (interval: 10s)

> context history
Context History (10 snapshots):

  [2026-05-17 14:32:10] coding - Focus: deep
    Window: main.py - Visual Studio Code
    CPU: 34.2%, Apps: 12

  [2026-05-17 14:32:00] coding - Focus: focused
    Window: main.py - Visual Studio Code
    CPU: 28.7%, Apps: 12
```

### Activity Summary

```
> activity summary 7
Activity Summary (Last 7 days)
========================================
Total Sessions: 42
Avg Focus Score: 3.8/5

Activities:
  coding: 18 sessions, Avg 2400s, Total 43200s
  browsing: 12 sessions, Avg 600s, Total 7200s
  communication: 8 sessions, Avg 300s, Total 2400s
  reading: 4 sessions, Avg 900s, Total 3600s
```

## Configuration

```json
{
  "agents": {
    "context_awareness_agent": {
      "enabled": true,
      "monitoring_interval": 10,
      "auto_suggest_workflows": true,
      "history_retention_days": 30,
      "focus_threshold_seconds": 60,
      "app_categories": {
        "development": ["Code.exe", "pycharm.exe", "terminal.exe"],
        "communication": ["Teams.exe", "Slack.exe", "Outlook.exe"],
        "browser": ["chrome.exe", "firefox.exe", "edge.exe"]
      }
    }
  }
}
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | bool | `true` | Enable/disable the agent |
| `monitoring_interval` | int | `10` | Context detection interval in seconds |
| `auto_suggest_workflows` | bool | `true` | Automatically suggest workflow modes |
| `history_retention_days` | int | `30` | How long to retain context history |
| `focus_threshold_seconds` | int | `60` | Minimum time on one window to count as focused |
| `app_categories` | dict | `{}` | Process name to category mappings |

## Dependencies

| Dependency | Source | Purpose |
|------------|--------|---------|
| `core.base_agent` | Local | BaseAgent, AgentStatus |
| `core.config` | Local | Configuration access |
| `core.logger` | Local | Structured logging |
| `psutil` | external | Process and system resource monitoring |
| `threading` | stdlib | Background monitoring thread |
| `time` | stdlib | Timing and intervals |
