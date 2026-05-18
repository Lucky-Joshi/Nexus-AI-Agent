# Scheduler Agent

> **NEXUS Agent** — Task scheduling, reminders, and automated workflows with persistent storage and cron-like execution.

## Purpose

The Scheduler Agent manages scheduled tasks, reminders, and automated workflows within NEXUS. It supports one-time, interval, daily, weekly, and cron-style triggers with natural language parsing. Tasks are persisted to disk and survive restarts. The agent automatically detects which NEXUS agent should execute each scheduled command and routes execution accordingly.

## Architecture

```
scheduler_agent/
├── __init__.py          # Package initialization
├── agent.py             # Main orchestrator (SchedulerAgent)
├── models.py            # Data models (ScheduledTask, Trigger, ExecutionRecord)
└── services.py          # Scheduling services
    ├── TaskStorage         # JSON-based persistent task and history storage
    ├── TriggerParser       # Natural language and structured trigger parsing
    └── ExecutionManager    # Background execution checker and task runner
```

The agent runs a background execution checker thread that polls every 5 seconds for due tasks. When a task is due, it routes the command to the appropriate NEXUS agent via a configurable executor function. All task state and execution history is persisted to JSON files.

## Capabilities

| Capability | Description |
|---|---|
| `schedule_task` | Schedule a task with natural language trigger |
| `schedule_reminder` | Schedule a reminder (routes to notification_agent) |
| `schedule_workflow` | Schedule a workflow execution (routes to automation_agent) |
| `list_schedules` | List all scheduled tasks with status |
| `run_task_now` | Execute a scheduled task immediately |
| `cancel_schedule` | Cancel and disable a scheduled task |
| `pause_schedule` | Pause a task without deleting it |
| `resume_schedule` | Resume a paused task |
| `schedule_status` | Show scheduler statistics and task counts |
| `execution_history` | View task execution history with timing |

## Internal Structure

### Data Models (`models.py`)

- **`ScheduledTask`** — Task with ID, name, command, description, trigger, status, target agent, parameters, creation time, last/next run times, result, error message, and enabled state
- **`Trigger`** — Trigger definition with type, run time, interval, cron expression, daily/weekly schedule, max runs, and completed run count
- **`ExecutionRecord`** — Execution history entry with task ID, name, start/complete times, status, result, error, and duration
- **`TriggerType`** enum: once, interval, cron, daily, weekly
- **`TaskStatus`** enum: scheduled, running, completed, failed, cancelled, paused

### Services (`services.py`)

- **`TaskStorage`** — JSON-based persistence in `data/scheduler/` directory. Stores tasks (`tasks.json`) and execution history (`history.json`, capped at 500 entries). Auto-saves on every mutation.
- **`TriggerParser`** — Parses natural language and structured triggers:
  - **Once**: `at 3:00 PM`, `in 10 minutes`
  - **Interval**: `every 5 minutes`, `every 2 hours`, `every 3 days`
  - **Daily**: `daily at 9:00 AM`, `every day at 3 PM`
  - **Weekly**: `every Monday at 9:00 AM`, `weekly on Friday at 5 PM`
  - **Cron**: Standard 5-field cron expressions (`0 9 * * 1-5`)
  - Auto-detects trigger type from command text
- **`ExecutionManager`** — Background thread polling every 5 seconds. Checks each enabled task against its trigger type:
  - **Once**: Compares `run_at` timestamp to current time
  - **Interval**: Checks elapsed time since last run
  - **Daily**: Matches today's date and time
  - **Weekly**: Matches day of week and time
  - Routes execution to configured executor function with agent detection
  - Calculates next run time after each execution
  - Supports `execute_now()` for immediate task execution

### Agent Detection

The scheduler automatically detects which agent should handle a command based on keywords:

| Keywords | Target Agent |
|---|---|
| open, file, folder, system, cpu | `file_agent` |
| search, web, summarize, research | `web_agent` |
| screenshot, capture | `vision_agent` |
| code, generate, git | `coding_agent` |
| notification, notify, remind | `notification_agent` |
| workflow, automate | `automation_agent` |

## Usage Examples

### Natural Language Commands

```
schedule 'open notepad' at 3:00 PM
schedule 'search web for news' every 1 hour
schedule 'take screenshot' daily at 9:00 AM
schedule 'run backup' every Monday at 2:00 AM
schedule reminder in 30 minutes to review PR
schedule workflow data-pipeline every day at 6:00 AM
list schedules
run now abc12345
cancel schedule abc12345
pause schedule abc12345
resume schedule abc12345
schedule status
execution history 10
```

### Programmatic API

```python
from agents.scheduler_agent.agent import SchedulerAgent

agent = SchedulerAgent()

# Set the executor function (connects to AI Manager)
agent.set_command_executor(lambda cmd, agt, params: ai_manager.execute(cmd, agt))

# Schedule a task
result = agent.schedule_task(
    command="search web for latest AI news",
    trigger_text="every 2 hours",
    agent="web_agent",
)

# Schedule a reminder
result = agent.schedule_task(
    command="send notification Review deployment logs",
    trigger_text="at 5:00 PM",
    agent="notification_agent",
)

# Run a task immediately
result = agent._executor.execute_now("abc12345")

# Get task details
task = agent.get_task("abc12345")

# Cancel a task
agent.cancel_task("abc12345")
```

### Trigger Examples

```python
from agents.scheduler_agent.services import TriggerParser

# One-time at specific time
trigger = TriggerParser.parse("at 3:00 PM")

# One-time relative
trigger = TriggerParser.parse("in 15 minutes")

# Recurring interval
trigger = TriggerParser.parse("every 30 minutes")

# Daily schedule
trigger = TriggerParser.parse("daily at 9:00 AM")

# Weekly schedule
trigger = TriggerParser.parse("every Friday at 5:00 PM")

# Cron expression
trigger = TriggerParser.parse("0 9 * * 1-5")  # Weekdays at 9 AM
```

## Configuration

| Config Key | Default | Description |
|---|---|---|
| `scheduler.storage_dir` | `data/scheduler/` | Directory for task and history JSON files |
| `scheduler.check_interval` | `5.0` | Background checker polling interval in seconds |
| `scheduler.max_history` | `500` | Maximum execution history entries |

## Persistence

- **Tasks**: `data/scheduler/tasks.json` — All scheduled tasks with full state
- **History**: `data/scheduler/history.json` — Last 500 execution records
- Both files are auto-saved on every mutation and loaded on startup
- Tasks survive agent restarts and maintain their schedule state

## Dependencies

- `threading` (built-in) — Background execution checker thread
- `json` (built-in) — Task and history persistence
- `datetime` (built-in) — Time parsing and scheduling calculations
- No external dependencies required
