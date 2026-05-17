"""
Service classes for NEXUS Scheduler Agent.
Handles scheduling engine, persistent storage, trigger parsing, and execution management.
"""

import json
import os
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from core.logger import Logger
from core.config import Config

from .models import (
    ScheduledTask, Trigger, TriggerType, TaskStatus, ExecutionRecord,
)


class TaskStorage:
    """Persistent storage for scheduled tasks using SQLite and JSON."""

    def __init__(self, storage_dir: Optional[str] = None):
        self.logger = Logger().get_logger("TaskStorage")
        if not storage_dir:
            storage_dir = str(Path(__file__).parent.parent.parent / "data" / "scheduler")
        self._storage_dir = storage_dir
        os.makedirs(self._storage_dir, exist_ok=True)
        self._tasks_path = os.path.join(self._storage_dir, "tasks.json")
        self._history_path = os.path.join(self._storage_dir, "history.json")
        self._tasks: Dict[str, ScheduledTask] = {}
        self._history: List[ExecutionRecord] = []
        self._load()

    def _load(self):
        try:
            if os.path.exists(self._tasks_path):
                with open(self._tasks_path, "r") as f:
                    data = json.load(f)
                    self._tasks = {
                        tid: ScheduledTask.from_dict(t)
                        for tid, t in data.items()
                    }
            if os.path.exists(self._history_path):
                with open(self._history_path, "r") as f:
                    data = json.load(f)
                    self._history = [ExecutionRecord.from_dict(r) for r in data]
        except Exception as e:
            self.logger.error(f"Failed to load task storage: {e}")

    def _save(self):
        try:
            with open(self._tasks_path, "w") as f:
                json.dump(
                    {tid: t.to_dict() for tid, t in self._tasks.items()},
                    f, indent=2,
                )
            with open(self._history_path, "w") as f:
                json.dump([r.to_dict() for r in self._history[-500:]], f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save task storage: {e}")

    def save_task(self, task: ScheduledTask):
        self._tasks[task.id] = task
        self._save()

    def get_task(self, task_id: str) -> Optional[ScheduledTask]:
        return self._tasks.get(task_id)

    def get_all_tasks(self) -> List[ScheduledTask]:
        return list(self._tasks.values())

    def get_enabled_tasks(self) -> List[ScheduledTask]:
        return [t for t in self._tasks.values() if t.enabled]

    def delete_task(self, task_id: str) -> bool:
        if task_id in self._tasks:
            del self._tasks[task_id]
            self._save()
            return True
        return False

    def add_execution(self, record: ExecutionRecord):
        self._history.append(record)
        if len(self._history) > 500:
            self._history = self._history[-500:]
        self._save()

    def get_history(self, task_id: Optional[str] = None, limit: int = 50) -> List[ExecutionRecord]:
        if task_id:
            return [r for r in self._history if r.task_id == task_id][-limit:]
        return self._history[-limit:]

    def get_stats(self) -> Dict[str, Any]:
        tasks = list(self._tasks.values())
        return {
            "total_tasks": len(tasks),
            "enabled": sum(1 for t in tasks if t.enabled),
            "scheduled": sum(1 for t in tasks if t.status == TaskStatus.SCHEDULED.value),
            "running": sum(1 for t in tasks if t.status == TaskStatus.RUNNING.value),
            "completed": sum(1 for t in tasks if t.status == TaskStatus.COMPLETED.value),
            "failed": sum(1 for t in tasks if t.status == TaskStatus.FAILED.value),
            "paused": sum(1 for t in tasks if t.status == TaskStatus.PAUSED.value),
            "total_executions": len(self._history),
        }


class TriggerParser:
    """Parses natural language and structured trigger definitions."""

    @staticmethod
    def parse_once(time_str: str) -> Trigger:
        """Parse 'at 3:00 PM' or 'in 10 minutes'."""
        time_str = time_str.lower().strip()

        if time_str.startswith("at "):
            time_part = time_str[3:].strip()
            run_at = TriggerParser._parse_time(time_part)
            if run_at:
                return Trigger(
                    trigger_type=TriggerType.ONCE.value,
                    run_at=run_at,
                    max_runs=1,
                )

        if time_str.startswith("in "):
            seconds = TriggerParser._parse_duration(time_str[3:])
            if seconds:
                run_at = (datetime.now() + timedelta(seconds=seconds)).isoformat()
                return Trigger(
                    trigger_type=TriggerType.ONCE.value,
                    run_at=run_at,
                    max_runs=1,
                )

        return Trigger(trigger_type=TriggerType.ONCE.value, run_at=time_str, max_runs=1)

    @staticmethod
    def parse_interval(time_str: str) -> Trigger:
        """Parse 'every 5 minutes' or 'every 2 hours'."""
        seconds = TriggerParser._parse_duration(time_str)
        if seconds:
            return Trigger(
                trigger_type=TriggerType.INTERVAL.value,
                interval_seconds=seconds,
                max_runs=0,
            )
        return None

    @staticmethod
    def parse_daily(time_str: str) -> Trigger:
        """Parse 'daily at 9:00 AM' or 'every day at 3 PM'."""
        time_match = None
        for prefix in ["daily at ", "every day at ", "each day at "]:
            if time_str.lower().startswith(prefix):
                time_match = time_str[len(prefix):].strip()
                break

        if not time_match:
            time_match = time_str

        run_time = TriggerParser._parse_time(time_match)
        if run_time:
            return Trigger(
                trigger_type=TriggerType.DAILY.value,
                daily_time=run_time,
                max_runs=0,
            )
        return None

    @staticmethod
    def parse_weekly(time_str: str) -> Trigger:
        """Parse 'every Monday at 9:00 AM' or 'weekly on Friday at 5 PM'."""
        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        day = None
        time_part = None

        lower = time_str.lower()
        for d in days:
            if d in lower:
                day = d
                break

        for prefix in ["at ", "on "]:
            idx = lower.rfind(prefix)
            if idx > 0:
                time_part = time_str[idx + len(prefix):].strip()
                break

        if day:
            run_time = TriggerParser._parse_time(time_part) if time_part else None
            return Trigger(
                trigger_type=TriggerType.WEEKLY.value,
                weekly_day=day,
                weekly_time=run_time,
                max_runs=0,
            )
        return None

    @staticmethod
    def parse_cron(expression: str) -> Trigger:
        """Parse standard cron expression."""
        parts = expression.split()
        if len(parts) == 5:
            return Trigger(
                trigger_type=TriggerType.CRON.value,
                cron_expression=expression,
                max_runs=0,
            )
        return None

    @staticmethod
    def parse(command: str) -> Optional[Trigger]:
        """Auto-detect trigger type from command text."""
        lower = command.lower()

        if any(kw in lower for kw in ["every day", "daily at", "each day"]):
            return TriggerParser.parse_daily(command)

        if any(kw in lower for kw in ["every monday", "every tuesday", "every wednesday",
                                        "every thursday", "every friday", "every saturday",
                                        "every sunday", "weekly on"]):
            return TriggerParser.parse_weekly(command)

        if lower.startswith("every "):
            return TriggerParser.parse_interval(command)

        if any(kw in lower for kw in ["at ", "in "]):
            return TriggerParser.parse_once(command)

        return None

    @staticmethod
    def _parse_time(time_str: str) -> Optional[str]:
        """Parse time string to ISO format."""
        time_str = time_str.strip().lower()

        am_pm = None
        if "am" in time_str:
            am_pm = "am"
            time_str = time_str.replace("am", "").strip()
        elif "pm" in time_str:
            am_pm = "pm"
            time_str = time_str.replace("pm", "").strip()

        parts = time_str.replace(":", " ").split()
        if len(parts) >= 2:
            try:
                hour = int(parts[0])
                minute = int(parts[1])
                if am_pm == "pm" and hour < 12:
                    hour += 12
                elif am_pm == "am" and hour == 12:
                    hour = 0

                now = datetime.now()
                run_at = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                if run_at < now:
                    run_at += timedelta(days=1)
                return run_at.isoformat()
            except ValueError:
                pass

        return None

    @staticmethod
    def _parse_duration(time_str: str) -> Optional[int]:
        """Parse duration string to seconds."""
        time_str = time_str.lower().strip()

        import re
        match = re.search(r"(\d+)\s*(seconds?|minutes?|hours?|days?)", time_str)
        if match:
            value = int(match.group(1))
            unit = match.group(2)
            if unit.startswith("second"):
                return value
            elif unit.startswith("minute"):
                return value * 60
            elif unit.startswith("hour"):
                return value * 3600
            elif unit.startswith("day"):
                return value * 86400

        return None


class ExecutionManager:
    """Manages task execution and recovery."""

    def __init__(self, task_storage: TaskStorage = None):
        self.logger = Logger().get_logger("ExecutionManager")
        self._storage = task_storage or TaskStorage()
        self._executor: Optional[Callable] = None
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._check_interval = 5.0

    def set_executor(self, executor: Callable):
        """Set the function that executes commands via AI Manager."""
        self._executor = executor

    def start(self, check_interval: float = 5.0):
        """Start the execution checker."""
        if self._running:
            return
        self._running = True
        self._check_interval = check_interval
        self._thread = threading.Thread(target=self._check_loop, args=(), daemon=True)
        self._thread.start()
        self.logger.info("Execution manager started")

    def stop(self):
        """Stop the execution checker."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=10)
        self.logger.info("Execution manager stopped")

    def _check_loop(self):
        """Background loop to check for due tasks."""
        while self._running:
            try:
                self._check_due_tasks()
            except Exception as e:
                self.logger.error(f"Execution check error: {e}")
            time.sleep(self._check_interval)

    def _check_due_tasks(self):
        """Check and execute tasks that are due."""
        now = datetime.now()
        tasks = self._storage.get_enabled_tasks()

        for task in tasks:
            if not task.should_run_again():
                continue

            if task.status == TaskStatus.PAUSED.value:
                continue

            trigger = task.trigger
            if not trigger:
                continue

            should_execute = False

            if trigger.trigger_type == TriggerType.ONCE.value:
                if trigger.run_at and datetime.fromisoformat(trigger.run_at) <= now:
                    should_execute = True

            elif trigger.trigger_type == TriggerType.INTERVAL.value:
                if task.last_run_at:
                    last = datetime.fromisoformat(task.last_run_at)
                    if (now - last).total_seconds() >= trigger.interval_seconds:
                        should_execute = True
                else:
                    should_execute = True

            elif trigger.trigger_type == TriggerType.DAILY.value:
                if trigger.daily_time:
                    trigger_time = datetime.fromisoformat(trigger.daily_time)
                    today_trigger = trigger_time.replace(year=now.year, month=now.month, day=now.day)
                    if task.last_run_at:
                        last = datetime.fromisoformat(task.last_run_at)
                        if last.date() < now.date() and now >= today_trigger:
                            should_execute = True
                    elif now >= today_trigger:
                        should_execute = True

            elif trigger.trigger_type == TriggerType.WEEKLY.value:
                if trigger.weekly_day:
                    day_map = {
                        "monday": 0, "tuesday": 1, "wednesday": 2,
                        "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6,
                    }
                    target_day = day_map.get(trigger.weekly_day, -1)
                    if now.weekday() == target_day:
                        if trigger.weekly_time:
                            trigger_time = datetime.fromisoformat(trigger.weekly_time)
                            today_trigger = trigger_time.replace(year=now.year, month=now.month, day=now.day)
                            if task.last_run_at:
                                last = datetime.fromisoformat(task.last_run_at)
                                if last.date() < now.date() and now >= today_trigger:
                                    should_execute = True
                            elif now >= today_trigger:
                                should_execute = True
                        else:
                            should_execute = True

            if should_execute:
                self._execute_task(task)

    def _execute_task(self, task: ScheduledTask):
        """Execute a single task."""
        task.mark_running()
        self._storage.save_task(task)

        record = ExecutionRecord(task_id=task.id, task_name=task.name)

        self.logger.info(f"Executing task: {task.name} ({task.id})")

        try:
            if self._executor:
                result = self._executor(task.command, task.agent, task.params)
                task.mark_completed(str(result)[:500])
                record.status = TaskStatus.COMPLETED.value
                record.result = str(result)[:500]
            else:
                task.mark_completed("No executor configured")
                record.status = TaskStatus.COMPLETED.value
                record.result = "No executor configured"

        except Exception as e:
            task.mark_failed(str(e))
            record.status = TaskStatus.FAILED.value
            record.error = str(e)
            self.logger.error(f"Task execution failed: {task.name}: {e}")

        record.completed_at = datetime.now().isoformat()
        if record.started_at and record.completed_at:
            start = datetime.fromisoformat(record.started_at)
            end = datetime.fromisoformat(record.completed_at)
            record.duration_seconds = (end - start).total_seconds()

        self._storage.add_execution(record)
        self._storage.save_task(task)

        self._update_next_run(task)

    def _update_next_run(self, task: ScheduledTask):
        """Calculate and set the next run time."""
        trigger = task.trigger
        if not trigger or not task.should_run_again():
            task.next_run_at = None
            return

        now = datetime.now()

        if trigger.trigger_type == TriggerType.INTERVAL.value:
            task.next_run_at = (now + timedelta(seconds=trigger.interval_seconds)).isoformat()

        elif trigger.trigger_type == TriggerType.DAILY.value:
            if trigger.daily_time:
                next_time = datetime.fromisoformat(trigger.daily_time)
                next_run = next_time.replace(year=now.year, month=now.month, day=now.day)
                if next_run <= now:
                    next_run += timedelta(days=1)
                task.next_run_at = next_run.isoformat()

        elif trigger.trigger_type == TriggerType.WEEKLY.value:
            if trigger.weekly_day:
                day_map = {
                    "monday": 0, "tuesday": 1, "wednesday": 2,
                    "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6,
                }
                target = day_map.get(trigger.weekly_day, 0)
                days_ahead = target - now.weekday()
                if days_ahead < 0:
                    days_ahead += 7
                next_run = now + timedelta(days=days_ahead)
                if trigger.weekly_time:
                    trigger_time = datetime.fromisoformat(trigger.weekly_time)
                    next_run = next_run.replace(
                        hour=trigger_time.hour, minute=trigger_time.minute,
                        second=0, microsecond=0,
                    )
                task.next_run_at = next_run.isoformat()

        self._storage.save_task(task)

    def execute_now(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Execute a task immediately."""
        task = self._storage.get_task(task_id)
        if not task:
            return None
        self._execute_task(task)
        return {"task_id": task_id, "status": task.status, "result": task.last_result}
