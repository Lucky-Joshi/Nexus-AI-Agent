"""
Scheduler Agent for NEXUS.
Manages scheduled tasks, reminders, and automated workflows with persistent storage
and a cron-like execution engine.
"""

import re
from typing import Any, Dict, List, Optional

from core.base_agent import BaseAgent, AgentStatus
from core.logger import Logger
from core.config import Config

from .models import ScheduledTask, Trigger, TaskStatus, TriggerType, ExecutionRecord
from .services import TaskStorage, TriggerParser, ExecutionManager


class SchedulerAgent(BaseAgent):
    """
    Scheduler agent for NEXUS.
    Thin orchestrator that delegates to specialized service classes.
    """

    def __init__(self):
        super().__init__("scheduler_agent", "Task scheduling, reminders, and automated workflows")
        self.logger = Logger().get_logger("SchedulerAgent")
        self.config = Config()

        self._storage = TaskStorage()
        self._trigger_parser = TriggerParser()
        self._executor = ExecutionManager(task_storage=self._storage)
        self._executor.start()

        self.logger.info("SchedulerAgent initialized")

    def set_command_executor(self, executor_func):
        """Set the function that executes commands via AI Manager."""
        self._executor.set_executor(executor_func)

    def execute(self, command: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        self.status = AgentStatus.BUSY
        try:
            cmd = command.lower()

            if self._matches(cmd, ["schedule", "schedule task", "create schedule"]):
                return self._handle_schedule(command)

            elif self._matches(cmd, ["list schedules", "list tasks", "show schedules", "all schedules"]):
                return self._handle_list()

            elif self._matches(cmd, ["run now", "execute now", "run task"]):
                return self._handle_run_now(command)

            elif self._matches(cmd, ["cancel schedule", "delete schedule", "remove task"]):
                return self._handle_cancel(command)

            elif self._matches(cmd, ["pause schedule", "pause task"]):
                return self._handle_pause(command)

            elif self._matches(cmd, ["resume schedule", "resume task"]):
                return self._handle_resume(command)

            elif self._matches(cmd, ["schedule status", "scheduler status", "schedule info"]):
                return self._handle_status()

            elif self._matches(cmd, ["execution history", "task history", "run history"]):
                return self._handle_history(command)

            elif self._matches(cmd, ["schedule reminder", "remind me at", "remind me every"]):
                return self._handle_reminder(command)

            elif self._matches(cmd, ["schedule workflow", "workflow schedule"]):
                return self._handle_workflow_schedule(command)

            else:
                return self._handle_schedule(command)

        except Exception as e:
            self.logger.error(f"SchedulerAgent error: {e}")
            return {
                "success": False,
                "response": f"Scheduler error: {str(e)}",
                "error": str(e),
            }
        finally:
            self.status = AgentStatus.IDLE

    def get_capabilities(self) -> list:
        return [
            "schedule_task",
            "schedule_reminder",
            "schedule_workflow",
            "list_schedules",
            "run_task_now",
            "cancel_schedule",
            "pause_schedule",
            "resume_schedule",
            "schedule_status",
            "execution_history",
        ]

    def _handle_schedule(self, command: str) -> Dict[str, Any]:
        parts = self._parse_schedule_command(command)
        if not parts:
            return {
                "success": False,
                "response": "Usage: 'schedule [command] [trigger]'\nExamples:\n  schedule 'open notepad' at 3:00 PM\n  schedule 'search web for news' every 1 hour\n  schedule 'take screenshot' daily at 9:00 AM",
            }

        task_command, trigger_text = parts
        trigger = self._trigger_parser.parse(trigger_text)

        if not trigger:
            return {
                "success": False,
                "response": f"Could not parse trigger: '{trigger_text}'. Examples: 'at 3:00 PM', 'in 10 minutes', 'every 5 minutes', 'daily at 9:00 AM'",
            }

        task = ScheduledTask(
            name=f"Task: {task_command[:40]}",
            command=task_command,
            description=f"Scheduled: {trigger_text}",
            trigger=trigger,
            agent=self._detect_agent(task_command),
        )

        self._executor._update_next_run(task)
        self._storage.save_task(task)

        next_run = task.next_run_at[:19] if task.next_run_at else "N/A"
        return {
            "success": True,
            "response": f"Task scheduled (ID: {task.id})\nCommand: {task_command}\nTrigger: {trigger_text}\nNext run: {next_run}",
            "data": task.to_dict(),
        }

    def _handle_list(self) -> Dict[str, Any]:
        tasks = self._storage.get_all_tasks()
        if not tasks:
            return {"success": True, "response": "No scheduled tasks."}

        lines = [f"Scheduled tasks ({len(tasks)}):\n"]
        for t in tasks:
            status_icon = {"scheduled": "[S]", "running": "[R]", "completed": "[C]",
                          "failed": "[F]", "paused": "[P]", "cancelled": "[X]"}.get(t.status, "[?]")
            enabled = "" if t.enabled else " (disabled)"
            next_run = t.next_run_at[:19] if t.next_run_at else "N/A"
            lines.append(f"  {status_icon} {t.id} | {t.name}{enabled}")
            lines.append(f"      Next: {next_run} | Runs: {t.trigger.runs_completed if t.trigger else 0}")

        return {
            "success": True,
            "response": "\n".join(lines),
            "data": [t.to_dict() for t in tasks],
        }

    def _handle_run_now(self, command: str) -> Dict[str, Any]:
        task_id = self._extract_id(command)
        if not task_id:
            return {"success": False, "response": "Please provide a task ID."}

        result = self._executor.execute_now(task_id)
        if not result:
            return {"success": False, "response": f"Task {task_id} not found."}

        return {
            "success": True,
            "response": f"Task {task_id} executed. Status: {result['status']}",
            "data": result,
        }

    def _handle_cancel(self, command: str) -> Dict[str, Any]:
        task_id = self._extract_id(command)
        if not task_id:
            return {"success": False, "response": "Please provide a task ID."}

        task = self._storage.get_task(task_id)
        if not task:
            return {"success": False, "response": f"Task {task_id} not found."}

        task.status = TaskStatus.CANCELLED.value
        task.enabled = False
        self._storage.save_task(task)
        return {"success": True, "response": f"Task {task_id} cancelled."}

    def _handle_pause(self, command: str) -> Dict[str, Any]:
        task_id = self._extract_id(command)
        if not task_id:
            return {"success": False, "response": "Please provide a task ID."}

        task = self._storage.get_task(task_id)
        if not task:
            return {"success": False, "response": f"Task {task_id} not found."}

        task.status = TaskStatus.PAUSED.value
        self._storage.save_task(task)
        return {"success": True, "response": f"Task {task_id} paused."}

    def _handle_resume(self, command: str) -> Dict[str, Any]:
        task_id = self._extract_id(command)
        if not task_id:
            return {"success": False, "response": "Please provide a task ID."}

        task = self._storage.get_task(task_id)
        if not task:
            return {"success": False, "response": f"Task {task_id} not found."}

        task.status = TaskStatus.SCHEDULED.value
        task.enabled = True
        self._executor._update_next_run(task)
        return {"success": True, "response": f"Task {task_id} resumed."}

    def _handle_status(self) -> Dict[str, Any]:
        stats = self._storage.get_stats()
        lines = [
            "Scheduler Agent Status:",
            f"  Total tasks: {stats['total_tasks']}",
            f"  Enabled: {stats['enabled']}",
            f"  Scheduled: {stats['scheduled']}",
            f"  Running: {stats['running']}",
            f"  Completed: {stats['completed']}",
            f"  Failed: {stats['failed']}",
            f"  Paused: {stats['paused']}",
            f"  Total executions: {stats['total_executions']}",
        ]
        return {"success": True, "response": "\n".join(lines), "data": stats}

    def _handle_history(self, command: str) -> Dict[str, Any]:
        task_id = self._extract_id(command)
        limit = self._extract_number(command, default=20)
        history = self._storage.get_history(task_id, limit)

        if not history:
            return {"success": True, "response": "No execution history."}

        lines = [f"Execution history ({len(history)}):\n"]
        for r in history[:15]:
            status = "OK" if r.status == "completed" else "FAIL"
            duration = f"{r.duration_seconds:.1f}s"
            lines.append(f"  [{status}] {r.task_name} ({r.started_at[:19]}) - {duration}")
            if r.error:
                lines.append(f"    Error: {r.error[:80]}")

        return {
            "success": True,
            "response": "\n".join(lines),
            "data": [r.to_dict() for r in history],
        }

    def _handle_reminder(self, command: str) -> Dict[str, Any]:
        message = self._extract_content(command, [
            "schedule reminder ", "remind me at ", "remind me every ",
        ])

        if not message:
            return {"success": False, "response": "Please provide a reminder message and time."}

        trigger = self._trigger_parser.parse(message)
        if not trigger:
            return {"success": False, "response": "Could not parse reminder time."}

        task = ScheduledTask(
            name=f"Reminder: {message[:40]}",
            command=f"send notification {message}",
            description=f"Reminder: {message}",
            trigger=trigger,
            agent="notification_agent",
        )

        self._executor._update_next_run(task)
        self._storage.save_task(task)

        next_run = task.next_run_at[:19] if task.next_run_at else "N/A"
        return {
            "success": True,
            "response": f"Reminder scheduled (ID: {task.id})\nMessage: {message}\nNext: {next_run}",
            "data": task.to_dict(),
        }

    def _handle_workflow_schedule(self, command: str) -> Dict[str, Any]:
        message = self._extract_content(command, [
            "schedule workflow ", "workflow schedule ",
        ])

        if not message:
            return {"success": False, "response": "Please provide a workflow name and schedule."}

        trigger = self._trigger_parser.parse(message)
        if not trigger:
            return {"success": False, "response": "Could not parse schedule time."}

        task = ScheduledTask(
            name=f"Workflow: {message[:40]}",
            command=f"run workflow {message}",
            description=f"Scheduled workflow: {message}",
            trigger=trigger,
            agent="automation_agent",
        )

        self._executor._update_next_run(task)
        self._storage.save_task(task)

        next_run = task.next_run_at[:19] if task.next_run_at else "N/A"
        return {
            "success": True,
            "response": f"Workflow scheduled (ID: {task.id})\nWorkflow: {message}\nNext: {next_run}",
            "data": task.to_dict(),
        }

    def schedule_task(self, command: str, trigger_text: str, agent: str = "",
                      params: Dict = None) -> Dict[str, Any]:
        """Programmatic API: schedule a task."""
        trigger = self._trigger_parser.parse(trigger_text)
        if not trigger:
            return {"success": False, "response": f"Invalid trigger: {trigger_text}"}

        task = ScheduledTask(
            name=f"Task: {command[:40]}",
            command=command,
            description=f"Scheduled: {trigger_text}",
            trigger=trigger,
            agent=agent or self._detect_agent(command),
            params=params or {},
        )

        self._executor._update_next_run(task)
        self._storage.save_task(task)
        return {"success": True, "data": task.to_dict()}

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Programmatic API: get task details."""
        task = self._storage.get_task(task_id)
        return task.to_dict() if task else None

    def cancel_task(self, task_id: str) -> bool:
        """Programmatic API: cancel a task."""
        return self._storage.delete_task(task_id)

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
        match = re.search(r"\b([a-f0-9]{8})\b", command.lower())
        return match.group(1) if match else None

    def _parse_schedule_command(self, command: str) -> Optional[tuple]:
        """Parse 'schedule [command] [trigger]' into (command, trigger)."""
        content = self._extract_content(command, [
            "schedule ", "schedule task ", "create schedule ",
        ])
        if not content:
            return None

        trigger_keywords = [" at ", " in ", " every ", " daily ", " weekly ", " on "]
        trigger_idx = len(content)

        for kw in trigger_keywords:
            idx = content.lower().rfind(kw)
            if idx > 0 and idx < trigger_idx:
                trigger_idx = idx

        if trigger_idx < len(content):
            task_cmd = content[:trigger_idx].strip()
            trigger_text = content[trigger_idx:].strip()
            return (task_cmd, trigger_text)

        return None

    def _detect_agent(self, command: str) -> str:
        """Detect which agent should execute the command."""
        cmd = command.lower()
        if any(kw in cmd for kw in ["open", "file", "folder", "system", "cpu"]):
            return "file_agent"
        if any(kw in cmd for kw in ["search", "web", "summarize", "research"]):
            return "web_agent"
        if any(kw in cmd for kw in ["screenshot", "capture"]):
            return "vision_agent"
        if any(kw in cmd for kw in ["code", "generate", "git"]):
            return "coding_agent"
        if any(kw in cmd for kw in ["notification", "notify", "remind"]):
            return "notification_agent"
        if any(kw in cmd for kw in ["workflow", "automate"]):
            return "automation_agent"
        return ""
