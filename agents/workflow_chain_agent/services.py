"""
Workflow Chain Agent Services
Core engine for multi-agent chain execution, dependency resolution,
condition evaluation, and recovery management.
"""

import re
import time
import json
import threading
from typing import Dict, Any, List, Optional, Callable, Set
from datetime import datetime
from collections import defaultdict, deque

from core.logger import Logger
from core.config import Config

from .models import (
    ChainStep, ChainDefinition, ChainExecution, ExecutionContext,
    StepStatus, ChainStatus, StepCondition, ConditionType,
    ActionType, FailureStrategy,
)
from .storage import ChainStorage


class DependencyGraph:
    """Builds and resolves step dependencies using topological sorting."""

    def __init__(self, steps: List[ChainStep]):
        self.logger = Logger().get_logger("DependencyGraph")
        self._steps = {s.id: s for s in steps}
        self._graph: Dict[str, List[str]] = defaultdict(list)
        self._reverse: Dict[str, List[str]] = defaultdict(list)
        self._build_graph()

    def _build_graph(self):
        for step in self._steps.values():
            for dep in step.depends_on:
                if dep in self._steps:
                    self._graph[dep].append(step.id)
                    self._reverse[step.id].append(dep)

    def get_execution_order(self) -> List[List[str]]:
        """Return execution order as list of parallel groups."""
        in_degree = {sid: len(deps) for sid, deps in self._reverse.items()}
        for sid in self._steps:
            if sid not in in_degree:
                in_degree[sid] = 0

        queue = deque([sid for sid, deg in in_degree.items() if deg == 0])
        levels = []

        while queue:
            level = list(queue)
            levels.append(level)
            next_queue = deque()

            for node in level:
                for neighbor in self._graph.get(node, []):
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        next_queue.append(neighbor)

            queue = next_queue

        if sum(len(l) for l in levels) != len(self._steps):
            self.logger.warning("Cycle detected in dependency graph")
            remaining = set(self._steps.keys()) - set(n for l in levels for n in l)
            levels.append(list(remaining))

        return levels

    def get_dependents(self, step_id: str) -> List[str]:
        return self._graph.get(step_id, [])

    def get_dependencies(self, step_id: str) -> List[str]:
        return self._reverse.get(step_id, [])

    def has_cycle(self) -> bool:
        visited = set()
        rec_stack = set()

        def dfs(node):
            visited.add(node)
            rec_stack.add(node)
            for neighbor in self._graph.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            rec_stack.discard(node)
            return False

        for node in self._steps:
            if node not in visited:
                if dfs(node):
                    return True
        return False

    def get_parallel_groups(self) -> Dict[str, List[str]]:
        groups = {}
        for step in self._steps.values():
            if step.parallel_group:
                if step.parallel_group not in groups:
                    groups[step.parallel_group] = []
                groups[step.parallel_group].append(step.id)
        return groups


class ConditionEvaluator:
    """Evaluates step conditions to determine execution eligibility."""

    def __init__(self, context: ExecutionContext):
        self.logger = Logger().get_logger("ConditionEvaluator")
        self._context = context

    def evaluate(self, condition: Optional[StepCondition]) -> bool:
        if condition is None:
            return True

        result = self._check_condition(condition)
        return not result if condition.negate else result

    def _check_condition(self, condition: StepCondition) -> bool:
        ct = condition.condition_type

        if ct == ConditionType.ALWAYS:
            return True
        if ct == ConditionType.NEVER:
            return False

        if ct == ConditionType.STEP_SUCCESS:
            status = self._context.get_status(condition.target_step)
            return status == StepStatus.COMPLETED

        if ct == ConditionType.STEP_FAILED:
            status = self._context.get_status(condition.target_step)
            return status == StepStatus.FAILED

        if ct == ConditionType.STEP_COMPLETED:
            status = self._context.get_status(condition.target_step)
            return status in (StepStatus.COMPLETED, StepStatus.FAILED)

        if ct == ConditionType.VARIABLE_EXISTS:
            return self._context.get_variable(condition.value) is not None

        if ct == ConditionType.VARIABLE_EQUALS:
            var_val = self._context.get_variable(condition.value, "")
            return str(var_val) == condition.pattern

        if ct == ConditionType.OUTPUT_CONTAINS:
            output = self._context.get_output(condition.target_step, "")
            return condition.pattern.lower() in output.lower()

        if ct == ConditionType.OUTPUT_EQUALS:
            output = self._context.get_output(condition.target_step, "")
            return output.strip().lower() == condition.pattern.strip().lower()

        if ct == ConditionType.OUTPUT_MATCHES:
            output = self._context.get_output(condition.target_step, "")
            return bool(re.search(condition.pattern, output, re.IGNORECASE))

        if ct == ConditionType.TIME_OF_DAY:
            hour = datetime.now().hour
            parts = condition.pattern.split("-")
            if len(parts) == 2:
                start, end = int(parts[0]), int(parts[1])
                return start <= hour < end
            return False

        self.logger.warning(f"Unknown condition type: {ct}")
        return True


class RecoveryManager:
    """Manages checkpointing and recovery for interrupted chains."""

    def __init__(self, storage: ChainStorage):
        self.logger = Logger().get_logger("RecoveryManager")
        self._storage = storage

    def save_checkpoint(self, execution: ChainExecution, checkpoint_name: str):
        self._storage.save_checkpoint(
            execution.id,
            execution.chain_id,
            checkpoint_name,
            execution.context.to_dict(),
            execution.step_results,
        )
        self.logger.info(f"Checkpoint saved: {checkpoint_name} for execution {execution.id}")

    def get_recovery_point(self, execution_id: str) -> Optional[Dict[str, Any]]:
        return self._storage.get_latest_checkpoint(execution_id)

    def can_resume(self, execution_id: str) -> bool:
        return self.get_recovery_point(execution_id) is not None

    def restore_from_checkpoint(self, execution: ChainExecution, checkpoint: Dict[str, Any]) -> bool:
        try:
            ctx_data = checkpoint.get("context", {})
            execution.context.variables = ctx_data.get("variables", {})
            execution.context.step_outputs = ctx_data.get("step_outputs", {})
            execution.context.step_statuses = {
                k: StepStatus(v) for k, v in ctx_data.get("step_statuses", {}).items()
            }
            execution.step_results = checkpoint.get("step_results", [])
            execution.update_progress()
            self.logger.info(f"Restored execution {execution.id} from checkpoint")
            return True
        except Exception as e:
            self.logger.error(f"Failed to restore checkpoint: {e}")
            return False


class ChainEngine:
    """Core execution engine for workflow chains."""

    def __init__(self, storage: ChainStorage, agent_executor: Optional[Callable] = None):
        self.logger = Logger().get_logger("ChainEngine")
        self._storage = storage
        self._agent_executor = agent_executor
        self._recovery = RecoveryManager(storage)
        self._running: Dict[str, bool] = {}
        self._lock = threading.Lock()

    def set_agent_executor(self, executor: Callable):
        self._agent_executor = executor

    def execute_chain(self, chain: ChainDefinition,
                      initial_variables: Optional[Dict[str, Any]] = None,
                      async_mode: bool = False) -> ChainExecution:
        execution = ChainExecution(
            chain_id=chain.id,
            chain_name=chain.name,
            total_steps=len(chain.steps),
        )
        if initial_variables:
            for k, v in initial_variables.items():
                execution.context.set_variable(k, v)

        with self._lock:
            self._running[execution.id] = True

        if async_mode:
            thread = threading.Thread(
                target=self._run_chain,
                args=(chain, execution),
                daemon=True,
            )
            thread.start()
            return execution

        return self._run_chain(chain, execution)

    def _run_chain(self, chain: ChainDefinition, execution: ChainExecution) -> ChainExecution:
        execution.status = ChainStatus.RUNNING
        self._storage.save_execution(execution.to_dict())

        dep_graph = DependencyGraph(chain.steps)
        if dep_graph.has_cycle():
            execution.mark_failed("Circular dependency detected in chain")
            self._storage.save_execution(execution.to_dict())
            return execution

        execution_levels = dep_graph.get_execution_order()
        evaluator = ConditionEvaluator(execution.context)

        try:
            for level_idx, level_steps in enumerate(execution_levels):
                if not self._running.get(execution.id, False):
                    execution.mark_cancelled()
                    self._storage.save_execution(execution.to_dict())
                    return execution

                self.logger.info(
                    f"Chain {chain.name}: executing level {level_idx + 1}/{len(execution_levels)} "
                    f"({len(level_steps)} steps)"
                )

                parallel_groups = self._get_parallel_groups_for_level(chain, level_steps)

                for group_name, group_steps in parallel_groups.items():
                    if group_name:
                        self._execute_parallel(chain, group_steps, execution, evaluator, level_idx)
                    else:
                        for step_id in group_steps:
                            if not self._running.get(execution.id, False):
                                execution.mark_cancelled()
                                self._storage.save_execution(execution.to_dict())
                                return execution
                            self._execute_step(chain, step_id, execution, evaluator)

                self._recovery.save_checkpoint(
                    execution, f"level_{level_idx}"
                )

            failed_count = sum(1 for r in execution.step_results if r.get("status") == "failed")
            if failed_count > 0 and chain.on_failure == FailureStrategy.ABORT:
                execution.mark_failed(f"{failed_count} steps failed")
            else:
                execution.mark_completed()

        except Exception as e:
            execution.mark_failed(str(e))
            self.logger.error(f"Chain execution failed: {e}")

        self._storage.save_execution(execution.to_dict())
        with self._lock:
            self._running.pop(execution.id, None)

        return execution

    def _get_parallel_groups_for_level(self, chain: ChainDefinition,
                                       level_step_ids: List[str]) -> Dict[str, List[str]]:
        groups: Dict[str, List[str]] = {"": []}
        for step_id in level_step_ids:
            step = chain.get_step(step_id)
            if step and step.parallel_group:
                if step.parallel_group not in groups:
                    groups[step.parallel_group] = []
                groups[step.parallel_group].append(step_id)
            else:
                groups[""].append(step_id)
        return groups

    def _execute_parallel(self, chain: ChainDefinition, step_ids: List[str],
                          execution: ChainExecution, evaluator: ConditionEvaluator,
                          level_idx: int):
        threads = []
        results = {}
        results_lock = threading.Lock()

        def run_step(step_id):
            try:
                self._execute_step(chain, step_id, execution, evaluator)
                with results_lock:
                    results[step_id] = execution.context.get_status(step_id)
            except Exception as e:
                with results_lock:
                    results[step_id] = StepStatus.FAILED

        for step_id in step_ids:
            t = threading.Thread(target=run_step, args=(step_id,), daemon=True)
            threads.append(t)
            t.start()

        for t in threads:
            t.join(timeout=chain.timeout)

    def _execute_step(self, chain: ChainDefinition, step_id: str,
                      execution: ChainExecution, evaluator: ConditionEvaluator):
        step = chain.get_step(step_id)
        if not step:
            return

        if step.condition and not evaluator.evaluate(step.condition):
            step.status = StepStatus.SKIPPED
            execution.context.set_status(step_id, StepStatus.SKIPPED)
            execution.step_results.append({
                "step_id": step_id,
                "step_name": step.name,
                "status": "skipped",
                "reason": "condition_not_met",
                "timestamp": datetime.now().isoformat(),
            })
            self.logger.info(f"Step {step.name} skipped (condition not met)")
            return

        dep_statuses = [
            execution.context.get_status(dep)
            for dep in step.depends_on
        ]
        if any(s in (StepStatus.FAILED, StepStatus.BLOCKED) for s in dep_statuses):
            if step.failure_strategy == FailureStrategy.CONTINUE:
                step.status = StepStatus.SKIPPED
                execution.context.set_status(step_id, StepStatus.SKIPPED)
                execution.step_results.append({
                    "step_id": step_id,
                    "status": "skipped",
                    "reason": "dependency_failed_continue",
                    "timestamp": datetime.now().isoformat(),
                })
                return
            else:
                step.status = StepStatus.BLOCKED
                execution.context.set_status(step_id, StepStatus.BLOCKED)
                execution.step_results.append({
                    "step_id": step_id,
                    "status": "blocked",
                    "reason": "dependency_failed",
                    "timestamp": datetime.now().isoformat(),
                })
                return

        retries = 0
        max_retries = step.max_retries

        while retries <= max_retries:
            if retries > 0:
                step.status = StepStatus.RETRYING
                step.retry_count = retries
                self.logger.info(f"Retrying step {step.name} (attempt {retries + 1})")
                time.sleep(step.retry_delay)

            step.status = StepStatus.RUNNING
            step.started_at = datetime.now().isoformat()
            execution.context.set_status(step_id, StepStatus.RUNNING)

            try:
                resolved_command = execution.context.resolve_command(step.command)

                if step.action_type == ActionType.AGENT_CALL:
                    result = self._call_agent(step.agent, resolved_command, step.timeout)
                elif step.action_type == ActionType.COMMAND:
                    result = {"success": True, "response": f"Command executed: {resolved_command}"}
                elif step.action_type == ActionType.VARIABLE_SET:
                    parts = resolved_command.split("=", 1)
                    if len(parts) == 2:
                        execution.context.set_variable(parts[0].strip(), parts[1].strip())
                        result = {"success": True, "response": f"Variable set: {parts[0].strip()}"}
                    else:
                        result = {"success": False, "response": "Invalid variable assignment"}
                elif step.action_type == ActionType.DELAY:
                    delay = int(resolved_command) if resolved_command.isdigit() else 1
                    time.sleep(delay)
                    result = {"success": True, "response": f"Delayed {delay}s"}
                else:
                    result = {"success": False, "response": f"Unknown action type: {step.action_type}"}

                step.completed_at = datetime.now().isoformat()
                try:
                    start = datetime.fromisoformat(step.started_at)
                    end = datetime.fromisoformat(step.completed_at)
                    step.duration = (end - start).total_seconds()
                except (ValueError, TypeError):
                    step.duration = 0.0

                if result.get("success", False):
                    step.status = StepStatus.COMPLETED
                    step.output = result.get("response", "")
                    execution.context.set_output(step_id, step.output)
                    execution.context.set_status(step_id, StepStatus.COMPLETED)

                    if step.output_variable:
                        execution.context.set_variable(step.output_variable, step.output)

                    execution.step_results.append({
                        "step_id": step_id,
                        "step_name": step.name,
                        "agent": step.agent,
                        "status": "completed",
                        "output": step.output[:500],
                        "duration": step.duration,
                        "timestamp": step.completed_at,
                    })
                    self.logger.info(f"Step {step.name} completed ({step.duration:.1f}s)")
                    return
                else:
                    raise Exception(result.get("response", "Step failed"))

            except Exception as e:
                step.error = str(e)
                step.completed_at = datetime.now().isoformat()
                try:
                    start = datetime.fromisoformat(step.started_at)
                    end = datetime.fromisoformat(step.completed_at)
                    step.duration = (end - start).total_seconds()
                except (ValueError, TypeError):
                    step.duration = 0.0

                if retries < max_retries:
                    retries += 1
                    continue

                step.status = StepStatus.FAILED
                execution.context.set_status(step_id, StepStatus.FAILED)
                execution.step_results.append({
                    "step_id": step_id,
                    "step_name": step.name,
                    "agent": step.agent,
                    "status": "failed",
                    "error": step.error[:300],
                    "duration": step.duration,
                    "timestamp": step.completed_at,
                })
                self.logger.error(f"Step {step.name} failed: {e}")

                if step.fallback_step:
                    self.logger.info(f"Executing fallback for step {step.name}")
                    self._execute_step(chain, step.fallback_step, execution, evaluator)

                return

    def _call_agent(self, agent_name: str, command: str, timeout: int) -> Dict[str, Any]:
        if self._agent_executor:
            try:
                return self._agent_executor(agent_name, command)
            except Exception as e:
                return {"success": False, "response": f"Agent execution error: {e}"}
        return {"success": False, "response": f"No agent executor configured for {agent_name}"}

    def cancel_execution(self, execution_id: str):
        with self._lock:
            self._running[execution_id] = False
        self.logger.info(f"Execution {execution_id} cancelled")

    def get_running_executions(self) -> List[str]:
        with self._lock:
            return list(self._running.keys())

    def get_chain_summary(self, execution: ChainExecution) -> str:
        lines = [
            f"Chain: {execution.chain_name}",
            f"Status: {execution.status.value}",
            f"Progress: {execution.completed_steps}/{execution.total_steps} completed",
            f"Failed: {execution.failed_steps}, Skipped: {execution.skipped_steps}",
            f"Duration: {execution.duration:.1f}s",
        ]

        if execution.step_results:
            lines.append("\nStep Results:")
            for r in execution.step_results:
                status_icon = {
                    "completed": "OK",
                    "failed": "FAIL",
                    "skipped": "SKIP",
                    "blocked": "BLOCK",
                }.get(r.get("status", "?"), "?")
                name = r.get("step_name", r.get("step_id", "?"))
                duration = r.get("duration", 0)
                lines.append(f"  [{status_icon}] {name} ({duration:.1f}s)")
                if r.get("error"):
                    lines.append(f"       Error: {r['error'][:80]}")

        if execution.error:
            lines.append(f"\nError: {execution.error}")

        return "\n".join(lines)
