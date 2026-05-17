"""
Workflow engine for the Automation Agent.
Manages workflow definition, execution, and templates.
"""

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
from core.logger import Logger
from .actions import Action, ActionExecutor
from .safety import SafetySystem, StopExecution


@dataclass
class Workflow:
    """Represents a multi-step automation workflow."""
    name: str
    description: str
    steps: List[Action] = field(default_factory=list)
    mode: str = "default"
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "steps": [s.to_dict() for s in self.steps],
            "mode": self.mode,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Workflow":
        steps = [Action.from_dict(s) for s in data.get("steps", [])]
        return cls(
            name=data["name"],
            description=data.get("description", ""),
            steps=steps,
            mode=data.get("mode", "default"),
            tags=data.get("tags", []),
        )

    @classmethod
    def from_steps(cls, name: str, description: str, steps: List[Action], mode: str = "default") -> "Workflow":
        return cls(name=name, description=description, steps=steps, mode=mode)

    @property
    def step_count(self) -> int:
        return len(self.steps)

    def add_step(self, action: Action):
        self.steps.append(action)

    def add_steps(self, actions: List[Action]):
        self.steps.extend(actions)


class WorkflowEngine:
    """Executes and manages automation workflows."""

    def __init__(self, safety_system: SafetySystem = None, screenshots_dir: str = None):
        self.logger = Logger().get_logger("WorkflowEngine")
        self.safety = safety_system or SafetySystem()
        self.executor = ActionExecutor(screenshots_dir=screenshots_dir)
        self._workflows: Dict[str, Workflow] = {}
        self._workflows_path = Path(__file__).parent.parent.parent / "data" / "workflows.json"
        self._workflows_path.parent.mkdir(parents=True, exist_ok=True)
        self._load_workflows()

    def register_workflow(self, workflow: Workflow):
        """Register a workflow for execution."""
        self._workflows[workflow.name.lower()] = workflow
        self.logger.info(f"Registered workflow: {workflow.name} ({workflow.step_count} steps)")

    def execute(self, workflow_name: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a registered workflow by name."""
        name = workflow_name.lower()
        if name not in self._workflows:
            available = ", ".join(self._workflows.keys())
            return {
                "success": False,
                "response": f"Workflow '{workflow_name}' not found. Available: {available}",
            }

        workflow = self._workflows[name]
        return self._run_workflow(workflow, params)

    def execute_custom(self, steps: List[Action], name: str = "custom") -> Dict[str, Any]:
        """Execute a custom workflow from action list."""
        workflow = Workflow(name=name, description=f"Custom workflow", steps=steps)
        return self._run_workflow(workflow)

    def _run_workflow(self, workflow: Workflow, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Run a workflow with safety controls."""
        self.logger.info(f"Executing workflow: {workflow.name} ({workflow.step_count} steps)")
        self.safety.reset()

        results = []
        start_time = time.time()

        for i, step in enumerate(workflow.steps, 1):
            if not self.safety.is_safe_to_continue():
                results.append({
                    "step": i,
                    "success": False,
                    "error": "Execution stopped",
                })
                break

            if not self.safety.pre_execute(step.type, step.params):
                results.append({
                    "step": i,
                    "success": False,
                    "error": "Safety check failed",
                })
                break

            try:
                result = self.executor.execute(step)
                result["step"] = i
                results.append(result)
                self.safety.post_execute()

                if step.delay_after > 0:
                    time.sleep(step.delay_after)

            except StopExecution:
                results.append({
                    "step": i,
                    "success": False,
                    "error": "Emergency stop triggered",
                })
                break
            except Exception as e:
                self.logger.error(f"Workflow step {i} failed: {e}")
                results.append({
                    "step": i,
                    "success": False,
                    "error": str(e),
                    "action_type": step.type,
                })

        elapsed = time.time() - start_time
        success_count = sum(1 for r in results if r.get("success"))
        total = len(results)

        response = f"Workflow '{workflow.name}' completed: {success_count}/{total} steps successful in {elapsed:.1f}s"

        return {
            "success": success_count == total,
            "response": response,
            "data": {
                "workflow": workflow.name,
                "total_steps": total,
                "successful_steps": success_count,
                "elapsed_seconds": round(elapsed, 1),
                "results": results,
            },
        }

    def stop(self, reason: str = "User requested stop"):
        """Trigger emergency stop on running workflow."""
        self.safety.emergency_stop.trigger(reason)

    def list_workflows(self) -> List[Dict[str, Any]]:
        """List all registered workflows."""
        return [
            {
                "name": wf.name,
                "description": wf.description,
                "steps": wf.step_count,
                "mode": wf.mode,
                "tags": wf.tags,
            }
            for wf in self._workflows.values()
        ]

    def get_workflow(self, name: str) -> Optional[Workflow]:
        """Get a workflow by name."""
        return self._workflows.get(name.lower())

    def save_workflows(self):
        """Save custom workflows to disk."""
        data = {name: wf.to_dict() for name, wf in self._workflows.items()}
        try:
            with open(self._workflows_path, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save workflows: {e}")

    def _load_workflows(self):
        """Load workflows from disk."""
        if self._workflows_path.exists():
            try:
                with open(self._workflows_path, "r") as f:
                    data = json.load(f)
                for name, wf_data in data.items():
                    workflow = Workflow.from_dict(wf_data)
                    self._workflows[name.lower()] = workflow
                self.logger.info(f"Loaded {len(self._workflows)} workflows from disk")
            except Exception as e:
                self.logger.error(f"Failed to load workflows: {e}")
