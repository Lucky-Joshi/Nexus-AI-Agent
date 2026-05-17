"""
NEXUS - Autonomous Planner Agent
PlannerAgent: BaseAgent wrapper that integrates the planning engine,
goal decomposition, dependency resolution, and autonomous task execution
with the AI Manager.
"""

import re
import time
from typing import Any, Callable, Dict, List, Optional

from core.base_agent import BaseAgent, AgentStatus
from core.logger import Logger
from core.config import Config

from .models import (
    Plan, PlanTask, TaskStatus, TaskPriority, PlanStatus, PlanStats,
    ReplanTrigger, GoalType, GoalTemplate,
)
from .storage import PlannerStorage
from .goal_decomposition import GoalDecomposer
from .dependency_graph import DependencyGraph
from .planning_engine import PlanningEngine
from .task_executor import TaskExecutor


class PlannerAgent(BaseAgent):
    """
    Autonomous Planner Agent that breaks large goals into executable
    multi-agent tasks, manages dependencies, executes plans, and
    dynamically replans based on context changes.
    """

    def __init__(self):
        super().__init__(
            name="planner_agent",
            description="Autonomous planner that decomposes goals into multi-agent task chains with dependency resolution and dynamic replanning",
        )
        self.logger = Logger().get_logger("PlannerAgent")
        self.config = Config()

        self._storage = PlannerStorage()
        self._engine = PlanningEngine(storage=self._storage)
        self._executor = TaskExecutor()

        self._ai_manager = None
        self._llm = None

        self._register_handlers()
        self.logger.info("PlannerAgent initialized")

    def set_ai_manager(self, manager):
        """Set reference to the AI Manager for cross-agent execution."""
        self._ai_manager = manager
        self._executor.set_ai_manager(manager)

        if hasattr(manager, "_llm") and manager._llm:
            self._llm = manager._llm
            self._engine.decomposer.llm = self._llm

        self._engine.on_task_update(self._on_task_update)
        self._engine.on_replan(self._on_replan)
        self._executor.on_progress(self._on_execution_progress)

        self.logger.info("PlannerAgent connected to AIManager")

    def _register_handlers(self):
        self._handlers = {
            "plan": self._handle_plan,
            "create plan": self._handle_create_plan,
            "start plan": self._handle_start_plan,
            "stop plan": self._handle_stop_plan,
            "pause plan": self._handle_pause_plan,
            "cancel plan": self._handle_cancel_plan,
            "plan status": self._handle_plan_status,
            "plan progress": self._handle_plan_progress,
            "list plans": self._handle_list_plans,
            "active plans": self._handle_active_plans,
            "plan history": self._handle_plan_history,
            "replan": self._handle_replan,
            "templates": self._handle_templates,
            "add template": self._handle_add_template,
            "stats": self._handle_stats,
            "help": self._handle_help,
        }

    def execute(self, command: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a planner command."""
        self.status = AgentStatus.BUSY
        start_time = time.time()

        try:
            cmd = command.strip().lower()
            handler = self._find_handler(cmd, command)

            if handler:
                result = handler(params or {})
            else:
                result = self._handle_fallback(command, params or {})

            duration_ms = (time.time() - start_time) * 1000
            self.logger.debug(f"Command '{command}' executed in {duration_ms:.0f}ms")
            return result

        except Exception as e:
            self.logger.error(f"Execution error: {e}")
            return {
                "success": False,
                "response": f"Error: {str(e)}",
                "agent": self.name,
            }
        finally:
            self.status = AgentStatus.IDLE

    def _find_handler(self, cmd: str, original: str) -> Optional[Callable]:
        """Find the best matching handler."""
        if cmd in self._handlers:
            return self._handlers[cmd]

        for key, handler in self._handlers.items():
            if cmd.startswith(key):
                return handler

        return None

    def _handle_create_plan(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new plan from a goal."""
        goal = params.get("goal", "")
        context = params.get("context", {})
        created_by = params.get("created_by", "user")

        if not goal:
            return {"success": False, "response": "Goal is required"}

        plan = self._engine.create_plan(goal, context, created_by)

        task_list = "\n".join(
            f"  {i+1}. [{t.priority.name}] {t.title} -> {t.agent_name or 'auto'}"
            for i, t in enumerate(plan.tasks)
        )

        return {
            "success": True,
            "response": f"Plan created: {plan.goal}\n\nTasks:\n{task_list}",
            "data": {
                "plan_id": plan.id,
                "goal": plan.goal,
                "task_count": len(plan.tasks),
                "tasks": [t.to_dict() for t in plan.tasks],
            },
        }

    def _handle_plan(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create and immediately start executing a plan."""
        goal = params.get("goal", "")
        context = params.get("context", {})

        if not goal:
            return {"success": False, "response": "Goal is required"}

        plan = self._engine.create_plan(goal, context)
        self._engine.start_plan(plan.id)

        task_list = "\n".join(
            f"  {i+1}. [{t.priority.name}] {t.title} -> {t.agent_name or 'auto'}"
            for i, t in enumerate(plan.tasks)
        )

        response_lines = [
            f"Plan started: {plan.goal}",
            f"Progress: 0% (0/{len(plan.tasks)} tasks)",
            f"\nTasks:\n{task_list}",
            f"\nExecuting autonomously...",
        ]

        def update_cb(plan_id, task_id, status, result, error):
            p = self._engine.get_plan(plan_id)
            if p:
                self.logger.info(f"  [{status.value}] {p.get_task(task_id).title if p.get_task(task_id) else task_id}")

        success = self._executor.execute_plan(plan, update_callback=update_cb)

        final_plan = self._engine.get_plan(plan.id)
        if final_plan:
            response_lines.append(f"\nExecution {'completed' if success else 'failed'}: {final_plan.get_progress()}%")
            for t in final_plan.tasks:
                status_icon = "+" if t.status == TaskStatus.COMPLETED else "x" if t.status == TaskStatus.FAILED else "-"
                response_lines.append(f"  {status_icon} {t.title}: {t.status.value}")

        return {
            "success": success,
            "response": "\n".join(response_lines),
            "data": {"plan_id": plan.id, "success": success},
        }

    def _handle_start_plan(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Start executing an existing plan."""
        plan_id = params.get("plan_id", "")
        if not plan_id:
            return {"success": False, "response": "Plan ID is required"}

        success = self._engine.start_plan(plan_id)
        if not success:
            return {"success": False, "response": "Plan not found or already active"}

        plan = self._engine.get_plan(plan_id)
        return {
            "success": True,
            "response": f"Plan started: {plan.goal if plan else plan_id}",
            "data": {"plan_id": plan_id},
        }

    def _handle_stop_plan(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Stop current plan execution."""
        if self._executor.is_running:
            self._executor.stop()
            return {"success": True, "response": "Plan execution stopped"}
        return {"success": False, "response": "No active execution"}

    def _handle_pause_plan(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Pause a plan."""
        plan_id = params.get("plan_id", "")
        if not plan_id:
            return {"success": False, "response": "Plan ID is required"}

        success = self._engine.pause_plan(plan_id)
        return {
            "success": success,
            "response": f"Plan {'paused' if success else 'not found'}: {plan_id}",
        }

    def _handle_cancel_plan(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Cancel a plan."""
        plan_id = params.get("plan_id", "")
        if not plan_id:
            return {"success": False, "response": "Plan ID is required"}

        success = self._engine.cancel_plan(plan_id)
        return {
            "success": success,
            "response": f"Plan {'cancelled' if success else 'not found'}: {plan_id}",
        }

    def _handle_plan_status(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get status of a specific plan."""
        plan_id = params.get("plan_id", "")
        if not plan_id:
            return {"success": False, "response": "Plan ID is required"}

        progress = self._engine.get_plan_progress(plan_id)
        if "error" in progress:
            return {"success": False, "response": progress["error"]}

        task_lines = "\n".join(
            f"  {t['title']}: {t['status']}" for t in progress.get("tasks", [])
        )

        return {
            "success": True,
            "response": f"Plan: {progress['goal']}\nStatus: {progress['status']}\nProgress: {progress['progress']}%\n\nTasks:\n{task_lines}",
            "data": progress,
        }

    def _handle_plan_progress(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get plan progress."""
        plan_id = params.get("plan_id", "")
        if not plan_id:
            return {"success": False, "response": "Plan ID is required"}

        progress = self._engine.get_plan_progress(plan_id)
        if "error" in progress:
            return {"success": False, "response": progress["error"]}

        return {
            "success": True,
            "response": f"Progress: {progress['progress']}% ({progress['completed_tasks']}/{progress['total_tasks']} tasks)",
            "data": progress,
        }

    def _handle_list_plans(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List all plans."""
        status = params.get("status")
        limit = params.get("limit", 20)

        if status:
            plans = self._engine.get_recent_plans(limit)
            plans = [p for p in plans if p.status.value == status]
        else:
            plans = self._engine.get_recent_plans(limit)

        plan_lines = "\n".join(
            f"  {p.id}: [{p.status.value}] {p.goal} ({p.get_progress()}%)"
            for p in plans
        )

        return {
            "success": True,
            "response": f"Found {len(plans)} plans:\n\n{plan_lines}" if plans else "No plans found",
            "data": {"plans": [p.to_dict() for p in plans]},
        }

    def _handle_active_plans(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List active plans."""
        plans = self._engine.get_active_plans()
        plan_lines = "\n".join(
            f"  {p.id}: {p.goal} ({p.get_progress()}%)"
            for p in plans
        )

        return {
            "success": True,
            "response": f"Active plans ({len(plans)}):\n\n{plan_lines}" if plans else "No active plans",
            "data": {"active_plans": [p.to_dict() for p in plans]},
        }

    def _handle_plan_history(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get plan execution history."""
        plan_id = params.get("plan_id", "")
        if not plan_id:
            return {"success": False, "response": "Plan ID is required"}

        history = self._storage.get_plan_history(plan_id)
        history_lines = "\n".join(
            f"  {h['timestamp']}: {h['event_type']}" for h in history[:20]
        )

        return {
            "success": True,
            "response": f"Plan history:\n{history_lines}" if history else "No history found",
            "data": {"history": history},
        }

    def _handle_replan(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger replanning for an active plan."""
        plan_id = params.get("plan_id", "")
        reason = params.get("reason", "user requested")

        if not plan_id:
            return {"success": False, "response": "Plan ID is required"}

        new_plan = self._engine.replan(plan_id, ReplanTrigger.USER_REQUEST, reason)
        if not new_plan:
            return {"success": False, "response": "Plan not found or not active"}

        task_list = "\n".join(
            f"  {i+1}. {t.title} -> {t.agent_name}" for i, t in enumerate(new_plan.tasks)
        )

        return {
            "success": True,
            "response": f"Plan replanned ({new_plan.replan_count} replans):\n\nTasks:\n{task_list}",
            "data": {"plan_id": new_plan.id, "replan_count": new_plan.replan_count},
        }

    def _handle_templates(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List available goal templates."""
        templates = self._engine.get_goal_templates()
        template_lines = "\n".join(
            f"  {t['name']}: {t['description']} (keywords: {', '.join(t['trigger_keywords'][:3])})"
            for t in templates
        )

        return {
            "success": True,
            "response": f"Goal templates:\n\n{template_lines}",
            "data": {"templates": templates},
        }

    def _handle_add_template(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add a custom goal template."""
        template_data = params.get("template", {})
        if not template_data:
            return {"success": False, "response": "Template data is required"}

        self._engine.add_goal_template(template_data)
        return {
            "success": True,
            "response": f"Template added: {template_data.get('name', 'unknown')}",
        }

    def _handle_stats(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get planning system statistics."""
        stats = self._engine.get_stats()
        return {
            "success": True,
            "response": "Planning statistics retrieved",
            "data": stats.to_dict(),
        }

    def _handle_fallback(self, command: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle unrecognized commands by attempting to create a plan."""
        cmd_lower = command.lower()

        if len(cmd_lower.split()) >= 3:
            return self._handle_plan({"goal": command, "context": params})

        return {
            "success": False,
            "response": f"Unknown planner command: {command}. Type 'help' for available commands.",
        }

    def _handle_help(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Show available commands."""
        return {
            "success": True,
            "response": """Planner Agent - Available Commands:

PLANNING:
  plan <goal>          - Create and execute a plan autonomously
  create plan <goal>   - Create a plan without executing
  start plan <id>      - Start executing a plan
  stop plan            - Stop current execution
  pause plan <id>      - Pause a plan
  cancel plan <id>     - Cancel a plan
  replan <id>          - Replan an active plan

MONITORING:
  plan status <id>     - Get detailed plan status
  plan progress <id>   - Get plan progress percentage
  list plans           - List all plans
  active plans         - List currently active plans
  plan history <id>    - Get plan execution history

TEMPLATES:
  templates            - List available goal templates
  add template         - Add a custom goal template

STATISTICS:
  stats                - Get planning system statistics""",
        }

    def _on_task_update(self, plan_id: str, task_id: str, status: TaskStatus, result: str):
        """Callback for task status updates."""
        self.logger.info(f"Task update: {task_id} -> {status.value}")

    def _on_replan(self, plan: Plan, trigger: ReplanTrigger, reason: str):
        """Callback for replan events."""
        self.logger.info(f"Plan replanned: {plan.id} (trigger={trigger.value}, reason={reason})")

    def _on_execution_progress(self, plan_id: str, event: str, progress: float, details: Dict):
        """Callback for execution progress."""
        self.logger.info(f"Execution: {plan_id} - {event} ({progress}%)")

    def get_capabilities(self) -> list:
        """Return list of capabilities."""
        return [
            "plan", "create plan", "start plan", "stop plan",
            "pause plan", "cancel plan", "plan status", "plan progress",
            "list plans", "active plans", "plan history", "replan",
            "templates", "add template", "stats",
        ]

    def create_and_execute(self, goal: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Programmatic API: Create and execute a plan."""
        plan = self._engine.create_plan(goal, context or {})
        self._engine.start_plan(plan.id)

        success = self._executor.execute_plan(plan)

        return {
            "plan_id": plan.id,
            "goal": goal,
            "success": success,
            "progress": plan.get_progress(),
            "tasks_completed": plan.completed_tasks,
            "tasks_total": plan.total_tasks,
        }

    def get_plan(self, plan_id: str) -> Optional[Plan]:
        """Programmatic API: Get a plan by ID."""
        return self._engine.get_plan(plan_id)

    def get_active_plans(self) -> List[Plan]:
        """Programmatic API: Get all active plans."""
        return self._engine.get_active_plans()

    def shutdown(self):
        """Shutdown the planner agent."""
        self.logger.info("Shutting down PlannerAgent...")
        self._executor.shutdown(wait=False)
        self.status = AgentStatus.OFFLINE
        self.logger.info("PlannerAgent shutdown complete")
