import uuid
import time
from typing import Dict, Any, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, Future
from threading import Lock
from datetime import datetime
from core.logger import Logger
from core.database import Database
from core.base_agent import BaseAgent, AgentStatus


class TaskDispatcher:
    """
    Thread-safe task queue with execution tracking.
    Handles task submission, execution in thread pool, and state management.
    """

    def __init__(self, max_workers: int = 4):
        self.logger = Logger().get_logger("TaskDispatcher")
        self.db = Database()
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._tasks: Dict[str, Dict[str, Any]] = {}
        self._futures: Dict[str, Future] = {}
        self._lock = Lock()
        self._callbacks: Dict[str, Callable] = {}

    def submit_task(
        self,
        agent: BaseAgent,
        command: str,
        params: Optional[Dict[str, Any]] = None,
        callback: Optional[Callable] = None,
        timeout: int = 60,
    ) -> str:
        """Submit a task for execution. Returns task_id."""
        task_id = str(uuid.uuid4())[:8]

        task = {
            "task_id": task_id,
            "agent": agent.name,
            "command": command,
            "params": params or {},
            "status": "pending",
            "result": None,
            "error": None,
            "created_at": datetime.now().isoformat(),
            "completed_at": None,
            "timeout": timeout,
        }

        with self._lock:
            self._tasks[task_id] = task
            if callback:
                self._callbacks[task_id] = callback

        self.db.execute(
            "INSERT INTO tasks (task_id, status, agent, command) VALUES (?, ?, ?, ?)",
            (task_id, "pending", agent.name, command),
        )

        self.logger.info(f"Task submitted: {task_id} -> {agent.name}")
        return task_id

    def execute_task(self, task_id: str, agent: BaseAgent, command: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a task immediately (blocking). Returns result dict."""
        self._update_task_status(task_id, "running")
        agent.status = AgentStatus.BUSY

        try:
            start_time = time.time()
            result = agent.execute(command, params)
            elapsed = time.time() - start_time

            result["task_id"] = task_id
            result["elapsed_seconds"] = round(elapsed, 2)

            self._update_task_status(task_id, "completed", result)
            self.logger.info(f"Task completed: {task_id} in {elapsed:.2f}s")
            return result

        except Exception as e:
            error_result = {
                "success": False,
                "error": str(e),
                "agent": agent.name,
                "task_id": task_id,
                "recoverable": True,
            }
            self._update_task_status(task_id, "failed", error_result)
            self.logger.error(f"Task failed: {task_id} - {e}")
            return error_result

        finally:
            agent.status = AgentStatus.IDLE

    def execute_async(self, task_id: str, agent: BaseAgent, command: str, params: Optional[Dict[str, Any]] = None) -> str:
        """Execute a task asynchronously in thread pool. Returns task_id."""
        self._update_task_status(task_id, "running")

        future = self._executor.submit(
            self._execute_worker, task_id, agent, command, params
        )
        self._futures[task_id] = future
        future.add_done_callback(lambda f: self._on_task_complete(task_id, f))

        return task_id

    def _execute_worker(self, task_id: str, agent: BaseAgent, command: str, params: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Worker function for thread pool execution."""
        agent.status = AgentStatus.BUSY
        try:
            start_time = time.time()
            result = agent.execute(command, params)
            elapsed = time.time() - start_time

            result["task_id"] = task_id
            result["elapsed_seconds"] = round(elapsed, 2)

            self._update_task_status(task_id, "completed", result)
            self.logger.info(f"Async task completed: {task_id} in {elapsed:.2f}s")
            return result

        except Exception as e:
            error_result = {
                "success": False,
                "error": str(e),
                "agent": agent.name,
                "task_id": task_id,
                "recoverable": True,
            }
            self._update_task_status(task_id, "failed", error_result)
            self.logger.error(f"Async task failed: {task_id} - {e}")
            return error_result

        finally:
            agent.status = AgentStatus.IDLE

    def _on_task_complete(self, task_id: str, future: Future):
        """Callback when async task completes."""
        try:
            result = future.result()
            with self._lock:
                if task_id in self._callbacks:
                    self._callbacks[task_id](result)
        except Exception as e:
            self.logger.error(f"Task callback error for {task_id}: {e}")

    def _update_task_status(self, task_id: str, status: str, result: Optional[Dict] = None):
        """Update task status in memory and database."""
        with self._lock:
            if task_id in self._tasks:
                self._tasks[task_id]["status"] = status
                if result:
                    self._tasks[task_id]["result"] = result
                if status in ("completed", "failed", "cancelled"):
                    self._tasks[task_id]["completed_at"] = datetime.now().isoformat()

        self.db.execute(
            "UPDATE tasks SET status = ?, result = ?, completed_at = ? WHERE task_id = ?",
            (status, str(result) if result else None, datetime.now().isoformat() if status in ("completed", "failed") else None, task_id),
        )

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get the current status of a task."""
        with self._lock:
            return self._tasks.get(task_id)

    def get_active_tasks(self) -> list:
        """Get all active (pending/running) tasks."""
        with self._lock:
            return [t for t in self._tasks.values() if t["status"] in ("pending", "running")]

    def get_all_tasks(self) -> list:
        """Get all tasks."""
        with self._lock:
            return list(self._tasks.values())

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending or running task."""
        with self._lock:
            if task_id in self._futures:
                cancelled = self._futures[task_id].cancel()
                if cancelled:
                    self._update_task_status(task_id, "cancelled")
                    self.logger.info(f"Task cancelled: {task_id}")
                return cancelled
            if task_id in self._tasks and self._tasks[task_id]["status"] == "pending":
                self._update_task_status(task_id, "cancelled")
                return True
        return False

    def shutdown(self, wait: bool = True):
        """Shutdown the dispatcher and wait for running tasks."""
        self.logger.info("Shutting down TaskDispatcher...")
        self._executor.shutdown(wait=wait)
