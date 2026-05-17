"""
Service classes for NEXUS Notification Agent.
Each service handles a specific domain: notification display, queue management,
alert routing, and focus mode logic.
"""

import os
import time
import json
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from core.logger import Logger
from core.config import Config

from .models import (
    Notification, NotificationAction, NotificationStatus,
    NotificationType, Priority, FocusModeConfig, NotificationSummary,
)


class NotificationService:
    """Displays system notifications using platform-specific backends."""

    def __init__(self):
        self.logger = Logger().get_logger("NotificationService")
        self._toaster = None
        self._plyer_available = False
        self._win10toast_available = False
        self._init_backends()

    def _init_backends(self):
        try:
            from win10toast import ToastNotifier
            self._toaster = ToastNotifier()
            self._win10toast_available = True
            self.logger.info("win10toast backend initialized")
        except ImportError:
            self.logger.debug("win10toast not available")

        try:
            import plyer
            self._plyer_available = True
            self.logger.info("plyer backend initialized")
        except ImportError:
            self.logger.debug("plyer not available")

    def show(self, title: str, message: str, duration: int = 5,
             icon_path: Optional[str] = None) -> bool:
        """Show a system notification."""
        if self._win10toast_available:
            return self._show_win10(title, message, duration, icon_path)
        elif self._plyer_available:
            return self._show_plyer(title, message, duration)
        else:
            self.logger.info(f"[NOTIFICATION] {title}: {message}")
            return True

    def _show_win10(self, title: str, message: str, duration: int,
                    icon_path: Optional[str] = None) -> bool:
        try:
            self._toaster.show_toast(
                title, message,
                duration=duration,
                icon_path=icon_path,
                threaded=True,
            )
            return True
        except Exception as e:
            self.logger.error(f"win10toast failed: {e}")
            return False

    def _show_plyer(self, title: str, message: str, duration: int) -> bool:
        try:
            import plyer
            plyer.notification.notify(
                title=title,
                message=message,
                timeout=duration,
            )
            return True
        except Exception as e:
            self.logger.error(f"plyer failed: {e}")
            return False

    def is_available(self) -> bool:
        return self._win10toast_available or self._plyer_available


class NotificationQueue:
    """Thread-safe priority queue for notifications."""

    def __init__(self, max_size: int = 100):
        self.logger = Logger().get_logger("NotificationQueue")
        self._queue: List[Notification] = []
        self._lock = threading.Lock()
        self._max_size = max_size
        self._history: List[Notification] = []
        self._max_history = 500
        self._callbacks: List[Callable] = []

    def enqueue(self, notification: Notification) -> bool:
        """Add a notification to the queue. Returns False if queue is full."""
        with self._lock:
            if len(self._queue) >= self._max_size:
                self.logger.warning("Notification queue full, dropping oldest")
                self._queue.pop(0)

            self._queue.append(notification)
            self._queue.sort(key=lambda n: self._priority_value(n.priority), reverse=True)

            for callback in self._callbacks:
                try:
                    callback(notification, "enqueued")
                except Exception as e:
                    self.logger.error(f"Queue callback error: {e}")

            self.logger.info(f"Enqueued notification: {notification.id} ({notification.priority})")
            return True

    def dequeue(self) -> Optional[Notification]:
        """Get the highest priority notification from the queue."""
        with self._lock:
            if not self._queue:
                return None

            notification = self._queue.pop(0)
            notification.status = NotificationStatus.SHOWING.value
            self._history.append(notification)
            if len(self._history) > self._max_history:
                self._history = self._history[-self._max_history:]

            for callback in self._callbacks:
                try:
                    callback(notification, "dequeued")
                except Exception as e:
                    self.logger.error(f"Queue callback error: {e}")

            return notification

    def peek(self) -> Optional[Notification]:
        """View the highest priority notification without removing it."""
        with self._lock:
            return self._queue[0] if self._queue else None

    def get_pending(self) -> List[Notification]:
        """Get all pending notifications."""
        with self._lock:
            return [n for n in self._queue if n.status == NotificationStatus.PENDING.value]

    def get_history(self, limit: int = 50) -> List[Notification]:
        """Get notification history."""
        with self._lock:
            return self._history[-limit:]

    def clear(self):
        """Clear the queue."""
        with self._lock:
            self._queue.clear()
            self.logger.info("Notification queue cleared")

    def size(self) -> int:
        with self._lock:
            return len(self._queue)

    def pending_count(self) -> int:
        with self._lock:
            return sum(1 for n in self._queue if n.status == NotificationStatus.PENDING.value)

    def on_event(self, callback: Callable):
        """Register a callback for queue events."""
        self._callbacks.append(callback)

    @staticmethod
    def _priority_value(priority: str) -> int:
        return {
            Priority.CRITICAL.value: 4,
            Priority.HIGH.value: 3,
            Priority.NORMAL.value: 2,
            Priority.LOW.value: 1,
        }.get(priority, 2)


class AlertManager:
    """Routes alerts to appropriate channels based on type and priority."""

    def __init__(self, notification_service: NotificationService = None,
                 notification_queue: NotificationQueue = None):
        self.logger = Logger().get_logger("AlertManager")
        self._notification = notification_service or NotificationService()
        self._queue = notification_queue or NotificationQueue()
        self._rules: List[Dict[str, Any]] = self._build_default_rules()

    def _build_default_rules(self) -> List[Dict[str, Any]]:
        return [
            {
                "type": NotificationType.ERROR.value,
                "priority": Priority.CRITICAL.value,
                "show_immediately": True,
                "sound": True,
                "duration": 10,
            },
            {
                "type": NotificationType.ERROR.value,
                "priority": Priority.HIGH.value,
                "show_immediately": True,
                "sound": False,
                "duration": 8,
            },
            {
                "type": NotificationType.WORKFLOW_COMPLETE.value,
                "priority": Priority.NORMAL.value,
                "show_immediately": True,
                "sound": False,
                "duration": 5,
            },
            {
                "type": NotificationType.TASK.value,
                "priority": Priority.NORMAL.value,
                "show_immediately": True,
                "sound": False,
                "duration": 5,
            },
            {
                "type": NotificationType.REMINDER.value,
                "priority": Priority.NORMAL.value,
                "show_immediately": True,
                "sound": True,
                "duration": 10,
            },
            {
                "type": NotificationType.AGENT_STATUS.value,
                "priority": Priority.LOW.value,
                "show_immediately": False,
                "sound": False,
                "duration": 3,
            },
            {
                "type": NotificationType.INFO.value,
                "priority": Priority.LOW.value,
                "show_immediately": False,
                "sound": False,
                "duration": 3,
            },
            {
                "type": NotificationType.WARNING.value,
                "priority": Priority.HIGH.value,
                "show_immediately": True,
                "sound": False,
                "duration": 6,
            },
        ]

    def process_alert(self, notification: Notification, focus_mode: FocusModeConfig = None) -> bool:
        """Process an alert through routing rules and focus mode."""
        if focus_mode and focus_mode.enabled:
            if not self._should_bypass_focus(notification, focus_mode):
                self.logger.info(f"Notification {notification.id} suppressed by focus mode")
                return False

        rule = self._match_rule(notification)
        if not rule:
            self.logger.warning(f"No routing rule for notification type: {notification.notification_type}")
            return False

        if rule["show_immediately"]:
            duration = rule.get("duration", 5)
            self._notification.show(notification.title, notification.message, duration)
            notification.status = NotificationStatus.SHOWING.value

        self._queue.enqueue(notification)
        return True

    def _match_rule(self, notification: Notification) -> Optional[Dict[str, Any]]:
        for rule in self._rules:
            if rule.get("type") == notification.notification_type:
                return rule
            if rule.get("priority") == notification.priority:
                return rule
        return None

    def _should_bypass_focus(self, notification: Notification,
                             focus_mode: FocusModeConfig) -> bool:
        if notification.priority == Priority.CRITICAL.value and focus_mode.allow_critical:
            return True
        if notification.source in focus_mode.allow_from_sources:
            return True
        if notification.notification_type in focus_mode.allow_from_types:
            return True
        return False

    def add_rule(self, notification_type: str, priority: str,
                 show_immediately: bool = True, sound: bool = False,
                 duration: int = 5):
        """Add a custom routing rule."""
        self._rules.append({
            "type": notification_type,
            "priority": priority,
            "show_immediately": show_immediately,
            "sound": sound,
            "duration": duration,
        })
        self.logger.info(f"Added alert rule: {notification_type}/{priority}")


class FocusModeManager:
    """Manages focus/silent mode with quiet hours and summary generation."""

    def __init__(self, config: FocusModeConfig = None):
        self.logger = Logger().get_logger("FocusModeManager")
        self._config = config or FocusModeConfig()
        self._suppressed: List[Notification] = []
        self._summary_thread: Optional[threading.Thread] = None
        self._running = False

    def enable(self, config: Optional[FocusModeConfig] = None):
        """Enable focus mode."""
        if config:
            self._config = config
        self._config.enabled = True
        self._suppressed.clear()
        self.logger.info("Focus mode enabled")

    def disable(self):
        """Disable focus mode."""
        self._config.enabled = False
        self.logger.info("Focus mode disabled")

    def is_active(self) -> bool:
        """Check if focus mode is currently active."""
        if self._config.enabled:
            return True
        if self._config.quiet_hours_enabled:
            return self._is_quiet_hours()
        return False

    def should_suppress(self, notification: Notification) -> bool:
        """Check if a notification should be suppressed."""
        if not self.is_active():
            return False
        if notification.priority == Priority.CRITICAL.value and self._config.allow_critical:
            return False
        if notification.source in self._config.allow_from_sources:
            return False
        if notification.notification_type in self._config.allow_from_types:
            return False
        return True

    def suppress(self, notification: Notification):
        """Add a notification to the suppressed list."""
        self._suppressed.append(notification)
        self.logger.debug(f"Suppressed notification: {notification.id}")

    def get_summary(self) -> NotificationSummary:
        """Generate a summary of suppressed notifications."""
        summary = NotificationSummary(
            start_time=self._config.quiet_hours_start if self._config.quiet_hours_enabled else "",
            end_time=datetime.now().isoformat(),
            total_count=len(self._suppressed),
        )

        for n in self._suppressed:
            summary.notifications.append(n)
            summary.by_priority[n.priority] = summary.by_priority.get(n.priority, 0) + 1
            summary.by_type[n.notification_type] = summary.by_type.get(n.notification_type, 0) + 1

        return summary

    def clear_suppressed(self):
        """Clear suppressed notifications."""
        self._suppressed.clear()
        self.logger.info("Suppressed notifications cleared")

    def _is_quiet_hours(self) -> bool:
        """Check if current time is within quiet hours."""
        try:
            now = datetime.now()
            start = datetime.strptime(self._config.quiet_hours_start, "%H:%M").time()
            end = datetime.strptime(self._config.quiet_hours_end, "%H:%M").time()
            current = now.time()

            if start <= end:
                return start <= current <= end
            else:
                return current >= start or current <= end
        except Exception:
            return False

    def get_config(self) -> FocusModeConfig:
        return self._config

    def update_config(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)
        self.logger.info(f"Focus mode config updated: {kwargs}")


class ReminderScheduler:
    """Schedules and manages task reminders."""

    def __init__(self, notification_queue: NotificationQueue = None):
        self.logger = Logger().get_logger("ReminderScheduler")
        self._queue = notification_queue or NotificationQueue()
        self._reminders: List[Dict[str, Any]] = []
        self._lock = threading.Lock()
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def add_reminder(self, message: str, delay_seconds: int,
                     title: str = "NEXUS Reminder",
                     priority: str = Priority.NORMAL.value) -> str:
        """Schedule a reminder."""
        reminder_id = f"reminder_{len(self._reminders) + 1}"
        trigger_time = datetime.now() + timedelta(seconds=delay_seconds)

        with self._lock:
            self._reminders.append({
                "id": reminder_id,
                "title": title,
                "message": message,
                "trigger_time": trigger_time.isoformat(),
                "priority": priority,
                "status": "scheduled",
            })

        self.logger.info(f"Reminder scheduled: {reminder_id} in {delay_seconds}s")
        return reminder_id

    def start(self, check_interval: float = 5.0):
        """Start the reminder checker."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._check_loop, args=(check_interval,), daemon=True)
        self._thread.start()
        self.logger.info("Reminder scheduler started")

    def stop(self):
        """Stop the reminder scheduler."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        self.logger.info("Reminder scheduler stopped")

    def _check_loop(self, interval: float):
        """Background loop to check for due reminders."""
        while self._running:
            try:
                self._check_reminders()
            except Exception as e:
                self.logger.error(f"Reminder check error: {e}")
            time.sleep(interval)

    def _check_reminders(self):
        """Check and fire due reminders."""
        now = datetime.now().isoformat()
        with self._lock:
            for reminder in self._reminders:
                if reminder["status"] == "scheduled" and reminder["trigger_time"] <= now:
                    notification = Notification(
                        title=reminder["title"],
                        message=reminder["message"],
                        notification_type=NotificationType.REMINDER.value,
                        priority=reminder["priority"],
                        source="reminder_scheduler",
                    )
                    self._queue.enqueue(notification)
                    reminder["status"] = "fired"
                    self.logger.info(f"Reminder fired: {reminder['id']}")

    def get_pending(self) -> List[Dict[str, Any]]:
        with self._lock:
            return [r for r in self._reminders if r["status"] == "scheduled"]

    def get_history(self) -> List[Dict[str, Any]]:
        with self._lock:
            return [r for r in self._reminders if r["status"] == "fired"]

    def cancel(self, reminder_id: str) -> bool:
        with self._lock:
            for reminder in self._reminders:
                if reminder["id"] == reminder_id and reminder["status"] == "scheduled":
                    reminder["status"] = "cancelled"
                    self.logger.info(f"Reminder cancelled: {reminder_id}")
                    return True
        return False
