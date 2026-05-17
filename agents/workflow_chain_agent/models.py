"""
Workflow Chain Agent Models
Data structures for multi-agent task chaining, dependency graphs, and execution state.
"""

from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from typing import Optional, Dict, Any, List
import uuid


class StepStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    BLOCKED = "blocked"
    RETRYING = "retrying"
    TIMEOUT = "timeout"


class ChainStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"
    PARTIAL = "partial"


class ActionType(Enum):
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    LOOP = "loop"
    AGENT_CALL = "agent_call"
    COMMAND = "command"
    DELAY = "delay"
    VARIABLE_SET = "variable_set"


class ConditionType(Enum):
    OUTPUT_CONTAINS = "output_contains"
    OUTPUT_EQUALS = "output_equals"
    OUTPUT_MATCHES = "output_matches"
    STEP_SUCCESS = "step_success"
    STEP_FAILED = "step_failed"
    STEP_COMPLETED = "step_completed"
    VARIABLE_EXISTS = "variable_exists"
    VARIABLE_EQUALS = "variable_equals"
    TIME_OF_DAY = "time_of_day"
    ALWAYS = "always"
    NEVER = "never"


class FailureStrategy(Enum):
    ABORT = "abort"
    CONTINUE = "continue"
    RETRY = "retry"
    FALLBACK = "fallback"
    SKIP_BRANCH = "skip_branch"


class LoopType(Enum):
    FIXED = "fixed"
    WHILE = "while"
    FOR_EACH = "for_each"


@dataclass
class ChainStep:
    """A single step in a workflow chain."""
    id: str
    name: str
    agent: str
    command: str
    action_type: ActionType = ActionType.AGENT_CALL
    depends_on: List[str] = field(default_factory=list)
    condition: Optional["StepCondition"] = None
    timeout: int = 60
    max_retries: int = 0
    retry_delay: int = 2
    failure_strategy: FailureStrategy = FailureStrategy.ABORT
    fallback_step: Optional[str] = None
    output_variable: Optional[str] = None
    parallel_group: Optional[str] = None
    description: str = ""
    status: StepStatus = StepStatus.PENDING
    output: str = ""
    error: str = ""
    started_at: str = ""
    completed_at: str = ""
    duration: float = 0.0
    retry_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "agent": self.agent,
            "command": self.command,
            "action_type": self.action_type.value,
            "depends_on": self.depends_on,
            "condition": self.condition.to_dict() if self.condition else None,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "retry_delay": self.retry_delay,
            "failure_strategy": self.failure_strategy.value,
            "fallback_step": self.fallback_step,
            "output_variable": self.output_variable,
            "parallel_group": self.parallel_group,
            "description": self.description,
            "status": self.status.value,
            "output": self.output,
            "error": self.error,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "duration": self.duration,
            "retry_count": self.retry_count,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChainStep":
        condition = None
        if data.get("condition"):
            condition = StepCondition.from_dict(data["condition"])
        return cls(
            id=data["id"],
            name=data.get("name", data["id"]),
            agent=data.get("agent", ""),
            command=data.get("command", ""),
            action_type=ActionType(data.get("action_type", "agent_call")),
            depends_on=data.get("depends_on", []),
            condition=condition,
            timeout=data.get("timeout", 60),
            max_retries=data.get("max_retries", 0),
            retry_delay=data.get("retry_delay", 2),
            failure_strategy=FailureStrategy(data.get("failure_strategy", "abort")),
            fallback_step=data.get("fallback_step"),
            output_variable=data.get("output_variable"),
            parallel_group=data.get("parallel_group"),
            description=data.get("description", ""),
            status=StepStatus(data.get("status", "pending")),
            output=data.get("output", ""),
            error=data.get("error", ""),
            started_at=data.get("started_at", ""),
            completed_at=data.get("completed_at", ""),
            duration=data.get("duration", 0.0),
            retry_count=data.get("retry_count", 0),
        )


@dataclass
class StepCondition:
    """Condition that determines whether a step should execute."""
    condition_type: ConditionType
    target_step: str = ""
    pattern: str = ""
    value: str = ""
    negate: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "condition_type": self.condition_type.value,
            "target_step": self.target_step,
            "pattern": self.pattern,
            "value": self.value,
            "negate": self.negate,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StepCondition":
        return cls(
            condition_type=ConditionType(data.get("condition_type", "always")),
            target_step=data.get("target_step", ""),
            pattern=data.get("pattern", ""),
            value=data.get("value", ""),
            negate=data.get("negate", False),
        )


@dataclass
class ExecutionContext:
    """Shared context that flows through a chain, carrying outputs and variables."""
    variables: Dict[str, Any] = field(default_factory=dict)
    step_outputs: Dict[str, str] = field(default_factory=dict)
    step_statuses: Dict[str, StepStatus] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def set_variable(self, name: str, value: Any):
        self.variables[name] = value

    def get_variable(self, name: str, default: Any = None) -> Any:
        return self.variables.get(name, default)

    def set_output(self, step_id: str, output: str):
        self.step_outputs[step_id] = output

    def get_output(self, step_id: str, default: str = "") -> str:
        return self.step_outputs.get(step_id, default)

    def set_status(self, step_id: str, status: StepStatus):
        self.step_statuses[step_id] = status

    def get_status(self, step_id: str) -> StepStatus:
        return self.step_statuses.get(step_id, StepStatus.PENDING)

    def resolve_command(self, command: str) -> str:
        """Resolve variable references in a command string."""
        result = command
        for var_name, var_value in self.variables.items():
            result = result.replace(f"{{{{{var_name}}}}}", str(var_value))
        for step_id, output in self.step_outputs.items():
            result = result.replace(f"{{{{{step_id}.output}}}}", str(output))
            result = result.replace(f"{{{{output.{step_id}}}}}", str(output))
        return result

    def to_dict(self) -> Dict[str, Any]:
        return {
            "variables": {k: str(v) for k, v in self.variables.items()},
            "step_outputs": {k: v[:500] for k, v in self.step_outputs.items()},
            "step_statuses": {k: v.value for k, v in self.step_statuses.items()},
            "metadata": self.metadata,
            "created_at": self.created_at,
        }


@dataclass
class ChainDefinition:
    """A complete workflow chain definition."""
    id: str
    name: str
    description: str = ""
    version: str = "1.0.0"
    category: str = "general"
    tags: List[str] = field(default_factory=list)
    steps: List[ChainStep] = field(default_factory=list)
    timeout: int = 300
    max_concurrent: int = 3
    on_failure: FailureStrategy = FailureStrategy.ABORT
    auto_retry: bool = False
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "category": self.category,
            "tags": self.tags,
            "steps": [s.to_dict() for s in self.steps],
            "timeout": self.timeout,
            "max_concurrent": self.max_concurrent,
            "on_failure": self.on_failure.value,
            "auto_retry": self.auto_retry,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "enabled": self.enabled,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChainDefinition":
        steps = [ChainStep.from_dict(s) for s in data.get("steps", [])]
        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            name=data.get("name", "unnamed"),
            description=data.get("description", ""),
            version=data.get("version", "1.0.0"),
            category=data.get("category", "general"),
            tags=data.get("tags", []),
            steps=steps,
            timeout=data.get("timeout", 300),
            max_concurrent=data.get("max_concurrent", 3),
            on_failure=FailureStrategy(data.get("on_failure", "abort")),
            auto_retry=data.get("auto_retry", False),
            created_at=data.get("created_at", datetime.now().isoformat()),
            updated_at=data.get("updated_at", datetime.now().isoformat()),
            enabled=data.get("enabled", True),
        )

    def add_step(self, step: ChainStep):
        self.steps.append(step)

    def get_step(self, step_id: str) -> Optional[ChainStep]:
        for step in self.steps:
            if step.id == step_id:
                return step
        return None


@dataclass
class ChainExecution:
    """Tracks the execution state of a running or completed chain."""
    chain_id: str
    chain_name: str
    status: ChainStatus = ChainStatus.PENDING
    context: ExecutionContext = field(default_factory=ExecutionContext)
    step_results: List[Dict[str, Any]] = field(default_factory=list)
    started_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: str = ""
    duration: float = 0.0
    total_steps: int = 0
    completed_steps: int = 0
    failed_steps: int = 0
    skipped_steps: int = 0
    error: str = ""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "chain_id": self.chain_id,
            "chain_name": self.chain_name,
            "status": self.status.value,
            "context": self.context.to_dict(),
            "step_results": self.step_results,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "duration": self.duration,
            "total_steps": self.total_steps,
            "completed_steps": self.completed_steps,
            "failed_steps": self.failed_steps,
            "skipped_steps": self.skipped_steps,
            "error": self.error,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChainExecution":
        context_data = data.get("context", {})
        context = ExecutionContext(
            variables=context_data.get("variables", {}),
            step_outputs=context_data.get("step_outputs", {}),
            step_statuses={k: StepStatus(v) for k, v in context_data.get("step_statuses", {}).items()},
            metadata=context_data.get("metadata", {}),
            created_at=context_data.get("created_at", datetime.now().isoformat()),
        )
        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            chain_id=data["chain_id"],
            chain_name=data.get("chain_name", ""),
            status=ChainStatus(data.get("status", "pending")),
            context=context,
            step_results=data.get("step_results", []),
            started_at=data.get("started_at", datetime.now().isoformat()),
            completed_at=data.get("completed_at", ""),
            duration=data.get("duration", 0.0),
            total_steps=data.get("total_steps", 0),
            completed_steps=data.get("completed_steps", 0),
            failed_steps=data.get("failed_steps", 0),
            skipped_steps=data.get("skipped_steps", 0),
            error=data.get("error", ""),
        )

    def update_progress(self):
        """Recalculate progress counters from step_results."""
        self.completed_steps = sum(1 for r in self.step_results if r.get("status") == "completed")
        self.failed_steps = sum(1 for r in self.step_results if r.get("status") == "failed")
        self.skipped_steps = sum(1 for r in self.step_results if r.get("status") == "skipped")

    def mark_completed(self):
        self.status = ChainStatus.COMPLETED
        self.completed_at = datetime.now().isoformat()
        try:
            start = datetime.fromisoformat(self.started_at)
            end = datetime.fromisoformat(self.completed_at)
            self.duration = (end - start).total_seconds()
        except (ValueError, TypeError):
            self.duration = 0.0

    def mark_failed(self, error: str = ""):
        self.status = ChainStatus.FAILED
        self.error = error
        self.completed_at = datetime.now().isoformat()
        try:
            start = datetime.fromisoformat(self.started_at)
            end = datetime.fromisoformat(self.completed_at)
            self.duration = (end - start).total_seconds()
        except (ValueError, TypeError):
            self.duration = 0.0

    def mark_cancelled(self):
        self.status = ChainStatus.CANCELLED
        self.completed_at = datetime.now().isoformat()
        try:
            start = datetime.fromisoformat(self.started_at)
            end = datetime.fromisoformat(self.completed_at)
            self.duration = (end - start).total_seconds()
        except (ValueError, TypeError):
            self.duration = 0.0


@dataclass
class ChainTemplate:
    """Pre-built workflow chain template for quick creation."""
    id: str
    name: str
    description: str
    category: str
    tags: List[str] = field(default_factory=list)
    initial_variables: Dict[str, str] = field(default_factory=dict)
    chain: Optional[ChainDefinition] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "tags": self.tags,
            "initial_variables": self.initial_variables,
            "chain": self.chain.to_dict() if self.chain else None,
        }
