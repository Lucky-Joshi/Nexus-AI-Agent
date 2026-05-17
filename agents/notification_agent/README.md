# Notification Agent

> **NEXUS Agent** — Desktop notification management, alerts, focus mode, and scheduled reminders.

## Purpose

The Notification Agent manages intelligent desktop notifications and alerts for the NEXUS system. It provides priority-based notification routing, focus mode (do not disturb) with quiet hours, actionable notifications, scheduled reminders, and a thread-safe priority queue. Other agents use it to send status updates, error alerts, and workflow completion notifications.

## Architecture

```
notification_agent/
├── __init__.py          # Package initialization
├── agent.py             # Main orchestrator (NotificationAgent)
├── models.py            # Data models (Notification, FocusModeConfig, etc.)
└── services.py          # Notification services
    ├── NotificationService   # Platform-specific notification display
    ├── NotificationQueue     # Thread-safe priority queue
    ├── AlertManager          # Alert routing rules and focus mode bypass
    ├── FocusModeManager      # Focus/DND mode with quiet hours
    └── ReminderScheduler     # Background reminder scheduler
```

The agent uses a multi-backend notification system: `win10toast` for Windows 10/11 native toasts, `plyer` as a cross-platform fallback, and console logging as a last resort. Notifications flow through a priority queue with configurable routing rules.

## Capabilities

| Capability | Description |
|---|---|
| `send_notification` | Send a desktop notification with title, message, and priority |
| `set_reminder` | Schedule a reminder with natural language time parsing |
| `cancel_reminder` | Cancel a scheduled reminder by ID |
| `focus_mode` | Enable/disable focus mode with configurable bypass rules |
| `notification_status` | Show queue status, focus mode state, and system availability |
| `pending_notifications` | View notifications waiting in the queue |
| `notification_history` | View recent notification history |
| `clear_notifications` | Clear all pending and suppressed notifications |
| `dismiss_notification` | Dismiss a specific notification by ID |
| `test_notification` | Send a test notification to verify system |
| `agent_alert` | Send an agent status alert |
| `workflow_alert` | Send a workflow completion notification with actions |
| `set_priority` | Change priority of a pending notification |
| `list_reminders` | View all pending reminders |

## Internal Structure

### Data Models (`models.py`)

- **`Notification`** — Core notification with ID, title, message, type, priority, status, source, actions, scheduling, expiration, and metadata
- **`NotificationAction`** — Actionable button with label, action ID, and callback data
- **`FocusModeConfig`** — Configuration for focus/DND mode: enabled state, critical bypass, allowed sources/types, quiet hours, summary interval
- **`NotificationSummary`** — Summary of suppressed notifications during focus mode with counts by priority and type
- **`Priority`** enum: low, normal, high, critical
- **`NotificationType`** enum: system, task, reminder, agent_status, workflow_complete, error, info, warning
- **`NotificationStatus`** enum: pending, showing, dismissed, actioned, expired

### Services (`services.py`)

- **`NotificationService`** — Multi-backend display: `win10toast` (Windows native toasts) → `plyer` (cross-platform) → console fallback. Graceful degradation when libraries are unavailable.
- **`NotificationQueue`** — Thread-safe priority queue (max 100 items) with automatic sorting by priority, history tracking (500 entries), and event callbacks. Drops oldest when full.
- **`AlertManager`** — Rule-based routing: 8 default rules mapping notification types to display behavior (immediate/deferred, sound, duration). Focus mode bypass logic for critical notifications and allowed sources.
- **`FocusModeManager`** — Focus/DND mode with quiet hours (configurable start/end time), critical notification bypass, allowed source/type whitelists, suppressed notification tracking, and summary generation.
- **`ReminderScheduler`** — Background thread checking every 5 seconds for due reminders. Supports natural language time parsing (seconds, minutes, hours). Reminders fire as notifications through the queue.

## Usage Examples

### Natural Language Commands

```
send notification Build completed successfully
notify high priority: Server is down
set reminder in 30 minutes to check deployment
remind me in 2 hours to take a break
focus mode on
focus mode off
focus mode quiet hours start 22:00 end 08:00
notification status
pending notifications
notification history 10
clear notifications
dismiss notification abc12345
test notification
agent alert Memory usage above 90%
workflow alert Data pipeline completed 5 of 5 steps
cancel reminder reminder_3
```

### Programmatic API

```python
from agents.notification_agent.agent import NotificationAgent
from agents.notification_agent.models import NotificationAction, Priority, NotificationType

agent = NotificationAgent()

# Send a notification
agent.send_notification(
    title="Build Complete",
    message="All tests passed. Deploy ready.",
    priority=Priority.NORMAL.value,
)

# Send with actions
agent.send_notification(
    title="Deployment Ready",
    message="Build #42 passed all checks.",
    notification_type=NotificationType.WORKFLOW_COMPLETE.value,
    actions=[
        NotificationAction(label="Deploy", action_id="deploy"),
        NotificationAction(label="View Logs", action_id="logs"),
    ],
)

# Schedule a reminder
reminder_id = agent.send_task_reminder("Review PR #42", delay_seconds=3600)

# Send error alert
agent.send_error_alert("Database connection timeout", source="db_monitor")

# Send workflow completion
agent.send_workflow_complete("Data Pipeline", steps_completed=5)
```

## Configuration

| Config Key | Default | Description |
|---|---|---|
| `notification_queue.max_size` | `100` | Maximum notifications in queue |
| `notification_queue.max_history` | `500` | Maximum history entries |
| `focus_mode.quiet_hours_start` | `22:00` | Quiet hours start time |
| `focus_mode.quiet_hours_end` | `08:00` | Quiet hours end time |
| `focus_mode.summary_interval_minutes` | `30` | Summary generation interval |
| `reminder_scheduler.check_interval` | `5.0` | Reminder check interval in seconds |

## Notification Backends

| Backend | Platform | Priority |
|---|---|---|
| `win10toast` | Windows 10/11 | Primary — native toast notifications |
| `plyer` | Cross-platform | Fallback — OS notification center |
| Console | All | Last resort — logged output |

## Dependencies

- `win10toast` (optional) — Windows 10/11 native toast notifications
- `plyer` (optional) — Cross-platform notification library
- `threading` (built-in) — Background reminder scheduler and queue management
- No required external dependencies — gracefully degrades to console logging
