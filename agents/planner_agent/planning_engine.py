"""
NEXUS - Autonomous Planner Agent
Core planning engine that orchestrates goal decomposition, dependency resolution,
plan execution, dynamic replanning, and progress tracking.
"""

import time
import threading
from typing import Any, Callable, Dict, List, Optional, Set
from datetime import datetime

from core.logger import Logger
from core.config import Config
from .models import (
    Plan, PlanTask, TaskStatus, TaskPriority, PlanStatus, PlanStats,
    ReplanTrigger, GoalType,
)
from .storage import PlannerStorage
from .goal_decomposition import GoalDecomposer
from .dependency_graph import DependencyGraph


class PlanningEngine:
    """
    Core planning engine that manages the full lifecycle of plans:
    creation -> decomposition -> execution -> monitoring -> replanning -> completion.
    """

    def __init__(self, storage: Optional[PlannerStorage] = None, llm_provider=None):
        self.logger = Logger().get_logger("PlanningEngine")
        self.config = Config()
        self.storage = storage or PlannerStorage()
        self.decomposer = GoalDecomposer(llm_provider=llm_provider)

        self._active_plans: Dict[str, Plan] = {}
        self._plans_lock = threading.RLock()

        self._execution_callbacks: List[Callable] = []
        self._replan_callbacks: List[Callable] = []

        self._stats = PlanStats()
        self._stats_lock = threading.Lock()

        self._load_active_plans()
        self.logger.info("PlanningEngine initialized")

    def _load_active_plans(self):
        """Load any active plans from storage."""
        try:
            plans_data = self.storage.get_plans(status="active")
            for data in plans_data:
                plan = Plan.from_dict(data)
                tasks_data = self.storage.get_tasks(plan.id)
                for td in tasks_data:
                    task = PlanTask.from_dict(td)
                    plan.tasks.append(task)
                self._active_plans[plan.id] = plan
            if self._active_plans:
                self.logger.info(f"Loaded {len(self._active_plans)} active plans from storage")
        except Exception as e:
            self.logger.error(f"Failed to load active plans: {e}")

    def create_plan(self, goal: str, context: Optional[Dict[str, Any]] = None,
                    created_by: str = "user") -> Plan:
        """Create a new plan from a goal."""
        plan = self.decomposer.decompose(goal, context)
        plan.created_by = created_by

        dep_graph = DependencyGraph()
        dep_graph.build_from_tasks(plan.tasks)

        valid, issues = dep_graph.validate()
        if not valid:
            self.logger.warning(f"Plan has dependency issues: {issues}")
            for issue in issues:
                if "Cycle" in issue:
                    plan.metadata["warning"] = "Dependency cycle detected, tasks may not execute in optimal order"

        plan.status = PlanStatus.DRAFT

        self.storage.save_plan(plan.to_dict())
        for task in plan.tasks:
            self.storage.save_task(task.to_dict())
        self.storage.log_plan_event(plan.id, "plan_created", {
            "goal": goal,
            "task_count": len(plan.tasks),
            "context": context,
        })

        with self._stats_lock:
            self._stats.total_plans += 1

        self.logger.info(f"Plan created: {plan.id} ({len(plan.tasks)} tasks) for goal: {goal}")
        return plan

    def start_plan(self, plan_id: str) -> bool:
        """Start executing a plan."""
        with self._plans_lock:
            plan = self._active_plans.get(plan_id)
            if not plan:
                plan_data = self.storage.get_plan(plan_id)
                if not plan_data:
                    return False
                plan = Plan.from_dict(plan_data)
                tasks_data = self.storage.get_tasks(plan_id)
                for td in tasks_data:
                    plan.tasks.append(PlanTask.from_dict(td))
                self._active_plans[plan_id] = plan

            if plan.status == PlanStatus.ACTIVE:
                return False

            plan.status = PlanStatus.ACTIVE
            plan.started_at = datetime.now()
            self.storage.save_plan(plan.to_dict())
            self.storage.log_plan_event(plan_id, "plan_started", {"task_count": len(plan.tasks)})

            with self._stats_lock:
                self._stats.active_plans += 1

            self.logger.info(f"Plan started: {plan_id} ({plan.goal})")
            return True

    def pause_plan(self, plan_id: str) -> bool:
        """Pause a plan."""
        with self._plans_lock:
            plan = self._active_plans.get(plan_id)
            if not plan:
                return False
            plan.status = PlanStatus.PAUSED
            self.storage.save_plan(plan.to_dict())
            self.storage.log_plan_event(plan_id, "plan_paused", {})
            self.logger.info(f"Plan paused: {plan_id}")
            return True

    def cancel_plan(self, plan_id: str) -> bool:
        """Cancel a plan."""
        with self._plans_lock:
            plan = self._active_plans.get(plan_id)
            if not plan:
                return False
            plan.status = PlanStatus.CANCELLED
            plan.completed_at = datetime.now()
            self.storage.save_plan(plan.to_dict())
            self.storage.log_plan_event(plan_id, "plan_cancelled", {})

            with self._plans_lock:
                self._active_plans.pop(plan_id, None)
            with self._stats_lock:
                self._stats.active_plans = max(0, self._stats.active_plans - 1)

            self.logger.info(f"Plan cancelled: {plan_id}")
            return True

    def complete_plan(self, plan_id: str, success: bool = True):
        """Mark a plan as completed or failed."""
        with self._plans_lock:
            plan = self._active_plans.get(plan_id)
            if not plan:
                return
            plan.status = PlanStatus.COMPLETED if success else PlanStatus.FAILED
            plan.completed_at = datetime.now()
            self.storage.save_plan(plan.to_dict())
            self.storage.log_plan_event(plan_id, "plan_completed" if success else "plan_failed", {
                "success": success,
                "progress": plan.get_progress(),
            })

            self._active_plans.pop(plan_id, None)
            with self._stats_lock:
                self._stats.active_plans = max(0, self._stats.active_plans - 1)
                if success:
                    self._stats.completed_plans += 1
                else:
                    self._stats.failed_plans += 1

            self.logger.info(f"Plan {'completed' if success else 'failed'}: {plan_id}")

    def replan(self, plan_id: str, trigger: ReplanTrigger, reason: str = "") -> Optional[Plan]:
        """
        Dynamically replan an active plan based on a trigger.
        Keeps completed tasks, re-decomposes remaining work.
        """
        with self._plans_lock:
            plan = self._active_plans.get(plan_id)
            if not plan:
                return None

            completed_tasks = [t for t in plan.tasks if t.status == TaskStatus.COMPLETED]
            failed_tasks = [t for t in plan.tasks if t.status == TaskStatus.FAILED]
            pending_tasks = [t for t in plan.tasks if t.status in (TaskStatus.PENDING, TaskStatus.BLOCKED)]

            self.logger.info(
                f"Replanning {plan_id} (trigger={trigger.value}): "
                f"{len(completed_tasks)} done, {len(failed_tasks)} failed, {len(pending_tasks)} pending"
            )

            remaining_goal = f"Complete remaining work for: {plan.goal}"
            if failed_tasks:
                remaining_goal += f". Failed tasks: {', '.join(t.title for t in failed_tasks)}"

            context = {
                "completed": {t.title: t.result for t in completed_tasks},
                "failed": {t.title: t.error_message for t in failed_tasks},
                "original_goal": plan.goal,
            }

            new_plan = self.decomposer.decompose(remaining_goal, context)
            new_plan.id = plan_id
            new_plan.status = PlanStatus.ACTIVE
            new_plan.replan_count = plan.replan_count + 1
            new_plan.last_replan_reason = reason or trigger.value
            new_plan.created_at = plan.created_at
            new_plan.started_at = plan.started_at
            new_plan.context = plan.context
            new_plan.variables = plan.variables

            for ct in completed_tasks:
                new_plan.add_task(ct)

            for nt in new_plan.tasks:
                if nt.status == TaskStatus.PENDING:
                    for ct in completed_tasks:
                        if ct.output_variable and ct.output_variable in nt.command:
                            nt.dependencies.append(ct.id)

            self.storage.save_plan(new_plan.to_dict())
            for task in new_plan.tasks:
                self.storage.save_task(task.to_dict())
            self.storage.log_plan_event(plan_id, "plan_replanned", {
                "trigger": trigger.value,
                "reason": reason,
                "new_task_count": len(new_plan.tasks),
            })

            with self._stats_lock:
                self._stats.total_replans += 1

            self._active_plans[plan_id] = new_plan

            for callback in self._replan_callbacks:
                try:
                    callback(new_plan, trigger, reason)
                except Exception as e:
                    self.logger.error(f"Replan callback error: {e}")

            return new_plan

    def update_task_status(self, plan_id: str, task_id: str, status: TaskStatus,
                           result: str = "", error: str = "",
                           started_at: Optional[str] = None,
                           completed_at: Optional[str] = None,
                           actual_duration: float = 0.0) -> bool:
        """Update the status of a task within a plan."""
        with self._plans_lock:
            plan = self._active_plans.get(plan_id)
            if not plan:
                return False

            task = plan.get_task(task_id)
            if not task:
                return False

        task.status = status
        if result:
            task.result = result
        if error:
            task.error_message = error
        if started_at:
            task.started_at = datetime.fromisoformat(started_at)
        if completed_at:
            task.completed_at = datetime.fromisoformat(completed_at)
        if actual_duration > 0:
            task.actual_duration = actual_duration

        self.storage.update_task_status(
            task_id, status.value, result, error,
            started_at, completed_at, actual_duration,
        )

        self.storage.log_plan_event(plan_id, "task_updated", {
            "task_id": task_id,
            "task_title": task.title,
            "status": status.value,
        })

        if status == TaskStatus.COMPLETED:
            with self._plans_lock:
                plan = self._active_plans.get(plan_id)
                if plan:
                    plan.completed_tasks = sum(1 for t in plan.tasks if t.status == TaskStatus.COMPLETED)
                    plan.failed_tasks = sum(1 for t in plan.tasks if t.status == TaskStatus.FAILED)
                    self.storage.save_plan(plan.to_dict())

                    if plan.completed_tasks == plan.total_tasks:
                        self.complete_plan(plan_id, success=True)
                    elif self._all_non_optional_blocked(plan):
                        self.complete_plan(plan_id, success=False)

        if status == TaskStatus.FAILED:
            with self._plans_lock:
                plan = self._active_plans.get(plan_id)
                if plan:
                    plan.failed_tasks = sum(1 for t in plan.tasks if t.status == TaskStatus.FAILED)
                    self.storage.save_plan(plan.to_dict())

        with self._stats_lock:
            self._stats.total_tasks_executed += 1
            if status == TaskStatus.FAILED:
                self._stats.total_tasks_failed += 1

        for callback in self._execution_callbacks:
            try:
                callback(plan_id, task_id, status, result)
            except Exception as e:
                self.logger.error(f"Execution callback error: {e}")

        return True

    def _all_non_optional_blocked(self, plan: Plan) -> bool:
        """Check if all remaining tasks are blocked by failed required dependencies."""
        completed = {t.id for t in plan.tasks if t.status == TaskStatus.COMPLETED}
        failed = {t.id for t in plan.tasks if t.status == TaskStatus.FAILED}

        for task in plan.tasks:
            if task.status == TaskStatus.PENDING:
                if not task.is_blocked(completed, failed):
                    return False
        return True

    def get_plan(self, plan_id: str) -> Optional[Plan]:
        """Get a plan by ID."""
        with self._plans_lock:
            plan = self._active_plans.get(plan_id)
            if plan:
                return plan

        plan_data = self.storage.get_plan(plan_id)
        if not plan_data:
            return None

        plan = Plan.from_dict(plan_data)
        tasks_data = self.storage.get_tasks(plan_id)
        for td in tasks_data:
            plan.tasks.append(PlanTask.from_dict(td))
        return plan

    def get_active_plans(self) -> List[Plan]:
        """Get all active plans."""
        with self._plans_lock:
            return list(self._active_plans.values())

    def get_recent_plans(self, limit: int = 20) -> List[Plan]:
        """Get recent plans from storage."""
        plans_data = self.storage.get_plans(limit=limit)
        return [Plan.from_dict(pd) for pd in plans_data]

    def get_plan_progress(self, plan_id: str) -> Dict[str, Any]:
        """Get detailed progress for a plan."""
        plan = self.get_plan(plan_id)
        if not plan:
            return {"error": "Plan not found"}

        task_details = []
        for task in plan.tasks:
            task_details.append({
                "id": task.id,
                "title": task.title,
                "agent": task.agent_name,
                "status": task.status.value,
                "priority": task.priority.value,
                "result": task.result[:100] if task.result else "",
                "error": task.error_message[:100] if task.error_message else "",
            })

        return {
            "plan_id": plan.id,
            "goal": plan.goal,
            "status": plan.status.value,
            "progress": plan.get_progress(),
            "total_tasks": plan.total_tasks,
            "completed_tasks": plan.completed_tasks,
            "failed_tasks": plan.failed_tasks,
            "replan_count": plan.replan_count,
            "tasks": task_details,
        }

    def on_task_update(self, callback: Callable):
        """Register a callback for task status updates."""
        self._execution_callbacks.append(callback)

    def on_replan(self, callback: Callable):
        """Register a callback for replan events."""
        self._replan_callbacks.append(callback)

    def get_stats(self) -> PlanStats:
        """Get planning system statistics."""
        storage_stats = self.storage.get_stats()
        with self._stats_lock:
            stats = PlanStats(**{**self._stats.to_dict(), **storage_stats})
            if stats.total_plans > 0:
                stats.avg_tasks_per_plan = stats.total_tasks_executed / stats.total_plans
                stats.avg_completion_rate = (stats.completed_plans / stats.total_plans) * 100
            return stats

    def add_goal_template(self, template_data: Dict[str, Any]):
        """Add a custom goal template."""
        from .models import GoalTemplate
        template = GoalTemplate(
            name=template_data.get("name", ""),
            description=template_data.get("description", ""),
            trigger_keywords=template_data.get("trigger_keywords", []),
            task_blueprint=template_data.get("task_blueprint", []),
        )
        self.decomposer.add_template(template)
        self.storage.save_goal_template(template.to_dict())

    def get_goal_templates(self) -> List[Dict[str, Any]]:
        """Get all available goal templates."""
        return self.decomposer.get_templates()

    def cleanup(self, days: int = 30):
        """Clean up old completed plans."""
        deleted = self.storage.cleanup_old_plans(days=days)
        self.logger.info(f"Cleaned up {deleted} old plans")
