"""
Notification Agent for NEXUS.
Manages intelligent desktop notifications and alerts with priority handling,
focus mode, reminders, and actionable notifications.
"""

import re
from typing import Any, Dict, List, Optional

from core.base_agent import BaseAgent, AgentStatus
from core.logger import Logger
from core.config import Config

from .models import (
    Notification, NotificationAction, NotificationType, Priority,
    FocusModeConfig, NotificationStatus,
)
from .services import (
    NotificationService, NotificationQueue, AlertManager,
    FocusModeManager, ReminderScheduler,
)


class NotificationAgent(BaseAgent):
    """
    Notification agent for NEXUS.
    Thin orchestrator that delegates to specialized service classes.
    """

    def __init__(self):
        super().__init__("notification_agent", "Desktop notification management and alerts")
        self.logger = Logger().get_logger("NotificationAgent")
        self.config = Config()

        self._notification = NotificationService()
        self._queue = NotificationQueue()
        self._alert_manager = AlertManager(
            notification_service=self._notification,
            notification_queue=self._queue,
        )
        self._focus_mode = FocusModeManager()
        self._reminders = ReminderScheduler(notification_queue=self._queue)

        self._reminders.start()
        self.logger.info("NotificationAgent initialized")

    def execute(self, command: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        self.status = AgentStatus.BUSY
        try:
            cmd = command.lower()

            if self._matches(cmd, ["send notification", "notify", "show notification", "popup"]):
                return self._handle_send_notification(command)

            elif self._matches(cmd, ["scheduled reminders", "pending reminders", "upcoming reminders"]):
                return self._handle_list_reminders()

            elif self._matches(cmd, ["cancel reminder", "remove reminder"]):
                return self._handle_cancel_reminder(command)

            elif self._matches(cmd, ["set reminder", "remind me", "alarm"]):
                return self._handle_reminder(command)

            elif self._matches(cmd, ["focus mode", "silent mode", "do not disturb", "dnd"]):
                return self._handle_focus_mode(command)

            elif self._matches(cmd, ["notification status", "notification stats", "notification info"]):
                return self._handle_status()

            elif self._matches(cmd, ["pending notifications", "pending alerts", "queue"]):
                return self._handle_pending()

            elif self._matches(cmd, ["notification history", "alert history", "past notifications"]):
                return self._handle_history(command)

            elif self._matches(cmd, ["clear notifications", "clear queue", "dismiss all"]):
                return self._handle_clear()

            elif self._matches(cmd, ["dismiss notification", "dismiss alert"]):
                return self._handle_dismiss(command)

            elif self._matches(cmd, ["test notification", "test alert", "test popup"]):
                return self._handle_test()

            elif self._matches(cmd, ["agent alert", "alert agent", "agent notification"]):
                return self._handle_agent_alert(command)

            elif self._matches(cmd, ["workflow alert", "workflow notification", "workflow complete"]):
                return self._handle_workflow_alert(command)

            elif self._matches(cmd, ["priority", "set priority"]):
                return self._handle_set_priority(command)

            else:
                return self._handle_send_notification(command)

        except Exception as e:
            self.logger.error(f"NotificationAgent error: {e}")
            return {
                "success": False,
                "response": f"Notification error: {str(e)}",
                "error": str(e),
            }
        finally:
            self.status = AgentStatus.IDLE

    def get_capabilities(self) -> list:
        return [
            "send_notification",
            "set_reminder",
            "cancel_reminder",
            "focus_mode",
            "notification_status",
            "pending_notifications",
            "notification_history",
            "clear_notifications",
            "dismiss_notification",
            "test_notification",
            "agent_alert",
            "workflow_alert",
            "list_reminders",
            "set_priority",
        ]

    def _handle_send_notification(self, command: str) -> Dict[str, Any]:
        title = self._extract_content(command, [
            "send notification ", "notify ", "show notification ", "popup ",
            "send notification titled ", "notify with title ",
        ])

        if not title:
            parts = command.split(" ", 2)
            if len(parts) >= 3:
                title = parts[1]
                message = parts[2]
            else:
                return {"success": False, "response": "Please provide a notification message."}
        else:
            message = command[len(title) + len(command.split(title)[0]):].strip()
            if not message:
                message = title
                title = "NEXUS Notification"

        priority = self._extract_priority(command)
        notification = Notification(
            title=title,
            message=message if message != title else message,
            notification_type=NotificationType.INFO.value,
            priority=priority,
            source="user",
        )

        focus_active = self._focus_mode.is_active()
        if focus_active and self._focus_mode.should_suppress(notification):
            self._focus_mode.suppress(notification)
            return {
                "success": True,
                "response": f"Notification queued (focus mode active). Will show when focus mode ends.",
                "data": notification.to_dict(),
            }

        self._alert_manager.process_alert(notification, self._focus_mode.get_config())
        return {
            "success": True,
            "response": f"Notification sent: {title}",
            "data": notification.to_dict(),
        }

    def _handle_reminder(self, command: str) -> Dict[str, Any]:
        message = self._extract_content(command, [
            "set reminder ", "remind me ", "reminder ", "alarm ",
            "set reminder to ", "remind me to ", "remind me in ",
        ])

        if not message:
            return {"success": False, "response": "Please provide a reminder message."}

        delay = self._extract_delay(command)
        if delay is None:
            return {
                "success": False,
                "response": "Please specify a time. Examples: 'in 5 minutes', 'in 1 hour', 'in 30 seconds'",
            }

        priority = self._extract_priority(command)
        reminder_id = self._reminders.add_reminder(
            message=message,
            delay_seconds=delay,
            title="NEXUS Reminder",
            priority=priority,
        )

        time_str = self._format_delay(delay)
        return {
            "success": True,
            "response": f"Reminder set: '{message}' in {time_str} (ID: {reminder_id})",
            "data": {"id": reminder_id, "message": message, "delay": delay},
        }

    def _handle_focus_mode(self, command: str) -> Dict[str, Any]:
        if self._matches(command, ["enable", "on", "start", "activate"]):
            config = self._focus_mode.get_config()

            if self._matches(command, ["critical only"]):
                config.allow_critical = True
                config.allow_from_sources = []
                config.allow_from_types = []
            elif self._matches(command, ["allow"]):
                sources = self._extract_list(command, ["allow ", "from "])
                if sources:
                    config.allow_from_sources = sources

            self._focus_mode.enable(config)
            return {
                "success": True,
                "response": "Focus mode enabled. Only critical notifications will show.",
            }

        if self._matches(command, ["disable", "off", "stop", "deactivate"]):
            self._focus_mode.disable()
            summary = self._focus_mode.get_summary()
            self._focus_mode.clear_suppressed()

            response = "Focus mode disabled."
            if summary.total_count > 0:
                response += f"\nYou missed {summary.total_count} notifications:\n"
                for n in summary.notifications[:10]:
                    response += f"  - [{n.priority}] {n.title}: {n.message[:50]}\n"

            return {"success": True, "response": response}

        if self._matches(command, ["quiet hours"]):
            start = self._extract_time(command, "start")
            end = self._extract_time(command, "end")
            config = self._focus_mode.get_config()
            if start:
                config.quiet_hours_start = start
            if end:
                config.quiet_hours_end = end
            config.quiet_hours_enabled = True
            return {
                "success": True,
                "response": f"Quiet hours set: {config.quiet_hours_start} - {config.quiet_hours_end}",
            }

        config = self._focus_mode.get_config()
        status = "Enabled" if config.enabled else "Disabled"
        quiet = f"Quiet hours: {config.quiet_hours_start}-{config.quiet_hours_end}" if config.quiet_hours_enabled else ""
        return {
            "success": True,
            "response": f"Focus Mode: {status}\n{quiet}\nSuppressed: {len(self._focus_mode._suppressed)} notifications",
        }

    def _handle_status(self) -> Dict[str, Any]:
        queue_size = self._queue.size()
        pending = self._queue.pending_count()
        history = len(self._queue.get_history(limit=1))
        focus = "Active" if self._focus_mode.is_active() else "Inactive"
        notifications_available = self._notification.is_available()

        lines = [
            "Notification Agent Status:",
            f"  Queue: {queue_size} total, {pending} pending",
            f"  Focus Mode: {focus}",
            f"  System Notifications: {'Available' if notifications_available else 'Not available'}",
            f"  Reminder Scheduler: Running",
        ]

        pending_reminders = self._reminders.get_pending()
        if pending_reminders:
            lines.append(f"  Pending Reminders: {len(pending_reminders)}")

        return {
            "success": True,
            "response": "\n".join(lines),
            "data": {
                "queue_size": queue_size,
                "pending": pending,
                "focus_mode": focus,
                "notifications_available": notifications_available,
            },
        }

    def _handle_pending(self) -> Dict[str, Any]:
        pending = self._queue.get_pending()
        if not pending:
            return {"success": True, "response": "No pending notifications."}

        lines = [f"Pending notifications ({len(pending)}):\n"]
        for i, n in enumerate(pending[:20], 1):
            lines.append(f"{i}. [{n.priority}] {n.title}: {n.message[:80]}")

        return {
            "success": True,
            "response": "\n".join(lines),
            "data": [n.to_dict() for n in pending],
        }

    def _handle_history(self, command: str) -> Dict[str, Any]:
        limit = self._extract_number(command, default=20)
        history = self._queue.get_history(limit)

        if not history:
            return {"success": True, "response": "No notification history."}

        lines = [f"Notification history ({len(history)}):\n"]
        for i, n in enumerate(history[:15], 1):
            lines.append(f"{i}. [{n.priority}] {n.title} ({n.status})")
            lines.append(f"   {n.message[:80]}")

        return {
            "success": True,
            "response": "\n".join(lines),
            "data": [n.to_dict() for n in history],
        }

    def _handle_clear(self) -> Dict[str, Any]:
        count = self._queue.size()
        self._queue.clear()
        self._focus_mode.clear_suppressed()
        return {
            "success": True,
            "response": f"Cleared {count} pending notifications.",
        }

    def _handle_dismiss(self, command: str) -> Dict[str, Any]:
        notification_id = self._extract_id(command)
        if not notification_id:
            return {"success": False, "response": "Please provide a notification ID to dismiss."}

        pending = self._queue.get_pending()
        for n in pending:
            if n.id == notification_id:
                n.dismiss()
                return {"success": True, "response": f"Notification {notification_id} dismissed."}

        return {"success": False, "response": f"Notification {notification_id} not found."}

    def _handle_test(self) -> Dict[str, Any]:
        notification = Notification(
            title="NEXUS Test Notification",
            message="This is a test notification from NEXUS.",
            notification_type=NotificationType.INFO.value,
            priority=Priority.NORMAL.value,
            source="test",
        )

        self._notification.show(notification.title, notification.message, 5)
        self._queue.enqueue(notification)

        return {
            "success": True,
            "response": "Test notification sent.",
            "data": notification.to_dict(),
        }

    def _handle_list_reminders(self) -> Dict[str, Any]:
        pending = self._reminders.get_pending()
        if not pending:
            return {"success": True, "response": "No pending reminders."}

        lines = [f"Pending reminders ({len(pending)}):\n"]
        for r in pending:
            lines.append(f"  - [{r['id']}] {r['message']} (at {r['trigger_time'][:19]})")

        return {
            "success": True,
            "response": "\n".join(lines),
            "data": pending,
        }

    def _handle_cancel_reminder(self, command: str) -> Dict[str, Any]:
        reminder_id = self._extract_id(command)
        if not reminder_id:
            return {"success": False, "response": "Please provide a reminder ID to cancel."}

        if self._reminders.cancel(reminder_id):
            return {"success": True, "response": f"Reminder {reminder_id} cancelled."}
        return {"success": False, "response": f"Reminder {reminder_id} not found or already fired."}

    def _handle_agent_alert(self, command: str) -> Dict[str, Any]:
        message = self._extract_content(command, [
            "agent alert ", "alert agent ", "agent notification ",
            "agent alert for ", "alert from ",
        ])

        if not message:
            return {"success": False, "response": "Please provide an alert message."}

        notification = Notification(
            title="Agent Alert",
            message=message,
            notification_type=NotificationType.AGENT_STATUS.value,
            priority=Priority.NORMAL.value,
            source="agent",
        )

        self._alert_manager.process_alert(notification, self._focus_mode.get_config())
        return {
            "success": True,
            "response": f"Agent alert sent: {message[:50]}",
            "data": notification.to_dict(),
        }

    def _handle_workflow_alert(self, command: str) -> Dict[str, Any]:
        message = self._extract_content(command, [
            "workflow alert ", "workflow notification ", "workflow complete ",
            "workflow alert for ", "workflow ",
        ])

        if not message:
            return {"success": False, "response": "Please provide workflow details."}

        notification = Notification(
            title="Workflow Complete",
            message=message,
            notification_type=NotificationType.WORKFLOW_COMPLETE.value,
            priority=Priority.NORMAL.value,
            source="workflow",
            actions=[
                NotificationAction(label="View Details", action_id="view_workflow"),
                NotificationAction(label="Run Again", action_id="rerun_workflow"),
            ],
        )

        self._alert_manager.process_alert(notification, self._focus_mode.get_config())
        return {
            "success": True,
            "response": f"Workflow alert sent: {message[:50]}",
            "data": notification.to_dict(),
        }

    def _handle_set_priority(self, command: str) -> Dict[str, Any]:
        notification_id = self._extract_id(command)
        if not notification_id:
            return {"success": False, "response": "Please provide a notification ID."}

        priority = self._extract_priority(command)
        if not priority:
            return {"success": False, "response": "Please specify a priority: low, normal, high, critical"}

        pending = self._queue.get_pending()
        for n in pending:
            if n.id == notification_id:
                n.priority = priority
                return {"success": True, "response": f"Notification {notification_id} priority set to {priority}."}

        return {"success": False, "response": f"Notification {notification_id} not found."}

    def send_notification(self, title: str, message: str,
                          priority: str = Priority.NORMAL.value,
                          notification_type: str = NotificationType.INFO.value,
                          actions: List[NotificationAction] = None) -> Dict[str, Any]:
        """Programmatic API: send a notification."""
        notification = Notification(
            title=title,
            message=message,
            notification_type=notification_type,
            priority=priority,
            source="api",
            actions=actions or [],
        )
        self._alert_manager.process_alert(notification, self._focus_mode.get_config())
        return notification.to_dict()

    def send_task_reminder(self, task_name: str, delay_seconds: int) -> str:
        """Programmatic API: schedule a task reminder."""
        return self._reminders.add_reminder(
            message=f"Task reminder: {task_name}",
            delay_seconds=delay_seconds,
            title="NEXUS Task Reminder",
        )

    def send_workflow_complete(self, workflow_name: str, steps_completed: int) -> Dict[str, Any]:
        """Programmatic API: send workflow completion alert."""
        return self.send_notification(
            title="Workflow Complete",
            message=f"Workflow '{workflow_name}' completed ({steps_completed} steps).",
            notification_type=NotificationType.WORKFLOW_COMPLETE.value,
            priority=Priority.NORMAL.value,
        )

    def send_error_alert(self, error_message: str, source: str = "") -> Dict[str, Any]:
        """Programmatic API: send error alert."""
        return self.send_notification(
            title="Error Alert",
            message=error_message,
            notification_type=NotificationType.ERROR.value,
            priority=Priority.HIGH.value,
            source=source,
        )

    @staticmethod
    def _matches(text: str, keywords: list) -> bool:
        return any(kw in text for kw in keywords)

    @staticmethod
    def _extract_content(command: str, prefixes: List[str]) -> str:
        cmd_lower = command.lower()
        for prefix in prefixes:
            if cmd_lower.startswith(prefix):
                return command[len(prefix):].strip()
        return ""

    @staticmethod
    def _extract_number(command: str, default: int = 0) -> int:
        match = re.search(r"\b(\d+)\b", command)
        return int(match.group(1)) if match else default

    @staticmethod
    def _extract_id(command: str) -> Optional[str]:
        match = re.search(r"\b([a-f0-9]{8}|reminder_\d+)\b", command.lower())
        return match.group(1) if match else None

    def _extract_priority(self, command: str) -> str:
        cmd = command.lower()
        if "critical" in cmd:
            return Priority.CRITICAL.value
        if "high" in cmd:
            return Priority.HIGH.value
        if "low" in cmd:
            return Priority.LOW.value
        return Priority.NORMAL.value

    def _extract_delay(self, command: str) -> Optional[int]:
        cmd = command.lower()

        match = re.search(r"in\s+(\d+)\s+seconds?", cmd)
        if match:
            return int(match.group(1))

        match = re.search(r"in\s+(\d+)\s+minutes?", cmd)
        if match:
            return int(match.group(1)) * 60

        match = re.search(r"in\s+(\d+)\s+hours?", cmd)
        if match:
            return int(match.group(1)) * 3600

        match = re.search(r"(\d+)\s*(s|sec|m|min|h|hr)", cmd)
        if match:
            value = int(match.group(1))
            unit = match.group(2)
            if unit in ("s", "sec"):
                return value
            elif unit in ("m", "min"):
                return value * 60
            elif unit in ("h", "hr"):
                return value * 3600

        return None

    def _extract_time(self, command: str, keyword: str) -> Optional[str]:
        match = re.search(rf"{keyword}\s+(\d{{1,2}}:\d{{2}})", command.lower())
        return match.group(1) if match else None

    def _extract_list(self, command: str, prefix: str) -> List[str]:
        cmd = command.lower()
        idx = cmd.find(prefix)
        if idx == -1:
            return []
        rest = command[idx + len(prefix):].strip()
        return [item.strip() for item in re.split(r"[,;]", rest) if item.strip()]

    @staticmethod
    def _format_delay(seconds: int) -> str:
        if seconds < 60:
            return f"{seconds} seconds"
        elif seconds < 3600:
            return f"{seconds // 60} minutes"
        else:
            return f"{seconds // 3600} hours"
