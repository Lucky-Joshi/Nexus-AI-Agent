"""
NEXUS - Autonomous Planner Agent
Autonomous task executor that runs plan tasks across agents,
handles parallel execution, retries, fallbacks, and progress reporting.
"""

import time
import threading
from typing import Any, Callable, Dict, List, Optional, Set
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, Future, as_completed

from core.logger import Logger
from core.config import Config
from .models import Plan, PlanTask, TaskStatus, TaskPriority, PlanStatus
from .dependency_graph import DependencyGraph


class TaskExecutor:
    """
    Executes plan tasks autonomously across NEXUS agents.
    Supports sequential and parallel execution, retry logic,
    fallback commands, variable passing between tasks, and
    real-time progress callbacks.
    """

    def __init__(self, ai_manager=None, max_parallel: int = 3, default_timeout: int = 300):
        self.logger = Logger().get_logger("TaskExecutor")
        self.config = Config()
        self._ai_manager = ai_manager
        self._max_parallel = max_parallel
        self._default_timeout = default_timeout

        self._executor = ThreadPoolExecutor(
            max_workers=max_parallel,
            thread_name_prefix="PlannerExecutor",
        )
        self._running = False
        self._stop_event = threading.Event()

        self._progress_callbacks: List[Callable] = []
        self._completion_callbacks: List[Callable] = []

        self._current_plan: Optional[Plan] = None
        self._completed_tasks: Set[str] = set()
        self._failed_tasks: Set[str] = set()
        self._variables: Dict[str, Any] = {}
        self._lock = threading.RLock()

        self.logger.info(f"TaskExecutor initialized (parallel={max_parallel}, timeout={default_timeout}s)")

    def set_ai_manager(self, manager):
        """Set reference to AI Manager for agent access."""
        self._ai_manager = manager

    def execute_plan(self, plan: Plan, update_callback: Optional[Callable] = None) -> bool:
        """
        Execute all tasks in a plan respecting dependencies.
        Returns True if all tasks completed successfully.
        """
        self._current_plan = plan
        self._completed_tasks = set()
        self._failed_tasks = set()
        self._variables = dict(plan.variables)
        self._running = True
        self._stop_event.clear()

        dep_graph = DependencyGraph()
        dep_graph.build_from_tasks(plan.tasks)

        self.logger.info(f"Executing plan: {plan.id} ({plan.goal}) - {len(plan.tasks)} tasks")
        self._notify_progress(plan, "started", 0)

        try:
            while self._running and not self._stop_event.is_set():
                ready_tasks = dep_graph.get_ready_tasks(self._completed_tasks, self._failed_tasks)

                if not ready_tasks:
                    blocked = dep_graph.get_blocked_tasks(self._completed_tasks, self._failed_tasks)
                    if blocked:
                        for task in blocked:
                            task.status = TaskStatus.BLOCKED
                            self._notify_progress(plan, "blocked", self._get_progress(plan))
                        self.logger.warning(f"{len(blocked)} tasks blocked by failed dependencies")
                    break

                ready_tasks.sort(key=lambda t: t.priority.value)

                if len(ready_tasks) <= self._max_parallel:
                    futures = {}
                    for task in ready_tasks:
                        future = self._executor.submit(self._execute_task, task, plan)
                        futures[future] = task

                    for future in as_completed(futures, timeout=self._default_timeout):
                        task = futures[future]
                        try:
                            success, result, error = future.result()
                            self._handle_task_result(plan, task, success, result, error, update_callback)
                        except Exception as e:
                            self._handle_task_result(plan, task, False, "", str(e), update_callback)
                else:
                    batch = ready_tasks[:self._max_parallel]
                    futures = {}
                    for task in batch:
                        future = self._executor.submit(self._execute_task, task, plan)
                        futures[future] = task

                    for future in as_completed(futures, timeout=self._default_timeout):
                        task = futures[future]
                        try:
                            success, result, error = future.result()
                            self._handle_task_result(plan, task, success, result, error, update_callback)
                        except Exception as e:
                            self._handle_task_result(plan, task, False, "", str(e), update_callback)

                if self._all_done(plan):
                    break

            all_success = all(t.status == TaskStatus.COMPLETED for t in plan.tasks if t.status != TaskStatus.SKIPPED)
            self._notify_progress(plan, "completed" if all_success else "failed", self._get_progress(plan))
            self.logger.info(f"Plan execution finished: {plan.goal} (success={all_success})")
            return all_success

        except Exception as e:
            self.logger.error(f"Plan execution error: {e}")
            self._notify_progress(plan, "error", self._get_progress(plan))
            return False
        finally:
            self._running = False

    def stop(self):
        """Stop the current plan execution."""
        self._stop_event.set()
        self._running = False
        self.logger.info("Task execution stopped")

    def _execute_task(self, task: PlanTask, plan: Plan) -> tuple:
        """Execute a single task."""
        task.status = TaskStatus.RUNNING
        start_time = time.time()

        self.logger.info(f"Executing task: {task.title} (agent={task.agent_name})")
        self._notify_progress(plan, "running", self._get_progress(plan))

        try:
            command = self._resolve_variables(task.command)

            if self._ai_manager and task.agent_name:
                agent = self._ai_manager.agents.get(task.agent_name)
                if agent:
                    params = task.params.copy()
                    for key, value in self._variables.items():
                        if key not in params:
                            params[key] = value

                    result = agent.execute(command, params)
                    success = result.get("success", False)
                    response = result.get("response", "")
                    error = result.get("error", "") if not success else ""

                    if task.output_variable and success:
                        self._variables[task.output_variable] = response

                    elapsed = time.time() - start_time
                    return success, response, error
                else:
                    return False, "", f"Agent not found: {task.agent_name}"
            else:
                return False, "", "No AI Manager configured"

        except Exception as e:
            elapsed = time.time() - start_time
            return False, "", str(e)

    def _handle_task_result(self, plan: Plan, task: PlanTask, success: bool,
                            result: str, error: str, update_callback: Optional[Callable]):
        """Handle the result of a task execution."""
        with self._lock:
            if success:
                task.status = TaskStatus.COMPLETED
                task.result = result[:500] if result else ""
                self._completed_tasks.add(task.id)
                self.logger.info(f"Task completed: {task.title}")
            else:
                if task.retry_count < task.max_retries:
                    task.retry_count += 1
                    task.status = TaskStatus.RETRYING
                    self.logger.warning(f"Task failed, retrying ({task.retry_count}/{task.max_retries}): {task.title}")
                    return

                if task.fallback_command:
                    self.logger.info(f"Running fallback for: {task.title}")
                    task.command = task.fallback_command
                    task.retry_count = 0
                    success, result, error = self._execute_task(task, plan)
                    if success:
                        task.status = TaskStatus.COMPLETED
                        task.result = result[:500] if result else ""
                        self._completed_tasks.add(task.id)
                        self._notify_progress(plan, "fallback_success", self._get_progress(plan))
                        return

                task.status = TaskStatus.FAILED
                task.error_message = error[:500] if error else "Unknown error"
                self._failed_tasks.add(task.id)
                self.logger.error(f"Task failed: {task.title} - {error}")

            now = datetime.now()
            task.completed_at = now

            if update_callback:
                try:
                    update_callback(plan.id, task.id, task.status, task.result, task.error_message)
                except Exception as e:
                    self.logger.error(f"Update callback error: {e}")

            self._notify_progress(plan, task.status.value, self._get_progress(plan))

    def _resolve_variables(self, command: str) -> str:
        """Replace {{variable}} placeholders with actual values."""
        for key, value in self._variables.items():
            command = command.replace(f"{{{{{key}}}}}", str(value))
        return command

    def _get_progress(self, plan: Plan) -> float:
        """Calculate plan progress percentage."""
        if plan.total_tasks == 0:
            return 0.0
        return round((len(self._completed_tasks) / plan.total_tasks) * 100, 1)

    def _all_done(self, plan: Plan) -> bool:
        """Check if all tasks are done (completed, failed, or skipped)."""
        done_statuses = {
            TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.SKIPPED, TaskStatus.BLOCKED,
        }
        return all(t.status in done_statuses for t in plan.tasks)

    def _notify_progress(self, plan: Plan, event: str, progress: float):
        """Notify progress callbacks."""
        for callback in self._progress_callbacks:
            try:
                callback(plan.id, event, progress, {
                    "completed": len(self._completed_tasks),
                    "failed": len(self._failed_tasks),
                    "total": plan.total_tasks,
                })
            except Exception as e:
                self.logger.error(f"Progress callback error: {e}")

    def on_progress(self, callback: Callable):
        """Register a progress callback."""
        self._progress_callbacks.append(callback)

    def on_completion(self, callback: Callable):
        """Register a completion callback."""
        self._completion_callbacks.append(callback)

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def current_plan(self) -> Optional[Plan]:
        return self._current_plan

    def shutdown(self, wait: bool = True):
        """Shutdown the executor."""
        self.logger.info("Shutting down TaskExecutor...")
        self._running = False
        self._stop_event.set()
        self._executor.shutdown(wait=wait)
        self.logger.info("TaskExecutor shutdown complete")
