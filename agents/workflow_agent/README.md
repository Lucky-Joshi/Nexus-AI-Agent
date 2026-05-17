# Workflow Agent

> **NEXUS Agent** — Intelligent workflow modes and productivity environments.

## Purpose

The Workflow Agent manages intelligent productivity environments (modes) that automatically prepare the desktop, launch applications, activate agents, and configure settings for specific tasks. Users can activate predefined modes like "Coding", "Meeting", or "Research" with a single command, and create custom modes tailored to their workflows.

## Architecture

```
workflow_agent/
├── __init__.py          # Package initialization
├── agent.py             # Main orchestrator (WorkflowAgent)
├── models.py            # Data models (WorkflowMode, ModeAction, ModeState, ModeSession)
├── executor.py          # Workflow execution engine
│   └── WorkflowExecutor    # Action execution with sequencing, parallelism, and error handling
├── registry.py          # Mode registry
│   └── ModeRegistry        # Preset loading, custom mode management, search
├── storage.py           # SQLite persistence for sessions and state
└── presets/             # JSON mode preset definitions
```

The agent uses a registry-executor pattern: `ModeRegistry` loads and manages mode definitions (from JSON presets and custom user modes), while `WorkflowExecutor` handles the actual activation/deactivation with support for sequential and parallel action execution, conditional actions, retries, and progress tracking.

## Capabilities

| Capability | Description |
|---|---|
| `activate_mode` | Activate a workflow mode by name |
| `deactivate_mode` | Deactivate the current active mode |
| `list_modes` | Show all available workflow modes with details |
| `mode_status` | Show current active mode and progress |
| `cancel_mode` | Cancel mode activation in progress |
| `mode_history` | View recent mode session history |
| `mode_stats` | Workflow mode usage statistics |
| `create_custom_mode` | Create a new custom workflow mode |
| `delete_mode` | Remove a custom mode |
| `mode_info` | Show detailed mode definition |
| `pause_resume_mode` | Pause or resume the current mode |

## Internal Structure

### Data Models (`models.py`)

- **`WorkflowMode`** — Complete mode definition with name, description, category, actions, apps to launch/close, agents to activate/deactivate, URLs to open, notification settings, focus mode, timer, tags, and priority
- **`ModeAction`** — Individual action with type, target, parameters, conditions, timeout, retries, failure policy, ordering, and parallel execution flag
- **`ModeState`** — Runtime state tracking progress, completed/failed/skipped actions, launched apps, activated agents, and errors
- **`ModeSession`** — Session record with start/end times, duration, status, and action counts
- **`ActionType`** enum (18 types): launch_app, close_app, open_url, open_file, open_folder, run_command, activate_agent, deactivate_agent, set_notifications, set_focus_mode, start_timer, stop_timer, create_file, create_folder, set_environment, kill_process, wait, conditional, custom
- **`ModeStatus`** enum: idle, activating, active, deactivating, paused, error, cancelled
- **`ActionStatus`** enum: pending, running, completed, failed, skipped, cancelled
- **`ConditionType`** enum: app_running, app_not_running, system_memory_high, system_cpu_high, focus_mode_active, time_of_day, custom

### Executor (`executor.py`)

- **Action grouping** — Actions grouped by `group` field for batch execution
- **Parallel execution** — Actions marked `parallel: true` run in separate threads
- **Conditional execution** — `ModeCondition` checked before action (app running, CPU/memory thresholds, time of day)
- **Retry logic** — Configurable `max_retries` with 1-second delay between attempts
- **Failure policies** — `on_failure: "continue"` or `"abort"` controls workflow continuation
- **Progress tracking** — Real-time progress percentage with optional callback
- **App launch** — Cross-platform app launching with 20+ Windows app mappings (VS Code, Chrome, Notion, Obsidian, etc.)
- **Deactivation** — Reverses activation: closes launched apps, restores previous settings

### Registry (`registry.py`)

- **Preset loading** — Loads JSON mode definitions from `presets/` directory
- **Alias support** — Modes can have multiple aliases for flexible activation
- **Fuzzy matching** — Partial name and tag matching for mode lookup
- **Custom modes** — User-created modes persisted to storage and loaded on startup
- **Category filtering** — Modes organized by category (productivity, development, etc.)
- **Search** — Search modes by name, description, or tags

### Storage (`storage.py`)

- SQLite tables: `mode_sessions` (history), `mode_state` (current state), `custom_modes` (user-defined modes)
- Indexed by mode ID and start time for efficient queries
- Statistics: total sessions, today/week counts, duration totals, top modes

## Usage Examples

### Natural Language Commands

```
start coding mode
activate meeting
stop mode
list modes
mode status
mode history 5
mode stats
create mode name: Deep Work
delete mode Deep Work
mode info Coding
pause mode
resume mode
```

### Programmatic API

```python
from agents.workflow_agent.agent import WorkflowAgent

agent = WorkflowAgent()

# Activate a mode
result = agent.activate_mode("Coding")

# Check current mode
active = agent.get_active_mode()

# Deactivate
result = agent.deactivate_mode()
```

### Mode Preset Example (JSON)

```json
{
  "name": "Coding",
  "description": "Development environment with IDE, terminal, and documentation",
  "category": "development",
  "apps_to_launch": ["vscode", "terminal"],
  "agents_to_activate": ["coding_agent", "terminal_agent"],
  "focus_mode": true,
  "notifications_mode": "critical_only",
  "actions": [
    {
      "action_type": "open_url",
      "target": "https://docs.python.org",
      "order": 1
    },
    {
      "action_type": "run_command",
      "target": "cd C:\\projects",
      "order": 2
    }
  ],
  "tags": ["development", "programming", "code"],
  "priority": 10
}
```

## Configuration

| Config Key | Default | Description |
|---|---|---|
| `database.path` | `data/nexus.db` | SQLite database for session history |
| Preset directory | `agents/workflow_agent/presets/` | JSON mode preset files |

## Dependencies

- `psutil` — Process management for app launch/close
- `webbrowser` (built-in) — URL opening
- `subprocess` (built-in) — Command execution
- `asyncio` (built-in) — Async execution support
- `platform` (built-in) — Cross-platform app launching
- SQLite (built-in) — Session and state persistence
