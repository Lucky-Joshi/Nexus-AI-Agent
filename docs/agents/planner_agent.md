# Planner Agent

> Autonomous goal decomposition, multi-step planning with dependency resolution, parallel task execution, and dynamic replanning for NEXUS.

## Purpose

The Planner Agent transforms high-level user goals into executable multi-agent task plans. It decomposes complex goals into discrete steps, resolves task dependencies using topological sorting, executes tasks in parallel where possible, monitors progress, and dynamically replans when tasks fail or context changes. This enables NEXUS to autonomously tackle complex, multi-step objectives without requiring the user to manually orchestrate each step.

## Architecture

```
planner_agent/
├── __init__.py
├── agent.py              # PlannerAgent orchestrator
├── models.py             # Plan, PlanTask, TaskStatus, TaskPriority, PlanStatus, GoalTemplate
├── planning_engine.py    # PlanningEngine - plan creation, lifecycle, replanning
├── goal_decomposition.py # GoalDecomposer - goal -> subtasks using templates + LLM
├── dependency_graph.py   # DependencyGraph - task dependency resolution
├── task_executor.py      # TaskExecutor - parallel task execution with callbacks
├── storage.py            # PlannerStorage - plan persistence and history
```

### Component Breakdown

| Component | Responsibility |
|-----------|---------------|
| `PlanningEngine` | Core engine managing plan lifecycle: create, start, pause, cancel, replan, and track progress |
| `GoalDecomposer` | Breaks high-level goals into executable subtasks using template matching and LLM-assisted decomposition |
| `DependencyGraph` | Builds and resolves task dependencies using topological sorting to determine execution order |
| `TaskExecutor` | Executes plan tasks, supports parallel execution (up to 3 concurrent), handles callbacks and progress reporting |
| `PlannerStorage` | Persistent storage for plans, task history, goal templates, and execution statistics |

### Architecture Diagram

```
User Goal
    │
    ▼
┌──────────────────┐
│ GoalDecomposer   │  Template matching + Rules + LLM -> subtasks
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ DependencyGraph  │  Topological sort -> execution order
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ PlanningEngine   │  Plan lifecycle management
│                  │  Progress tracking, replanning
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ TaskExecutor     │  Parallel execution (3 concurrent max)
│                  │  Progress callbacks, error handling
└────────┬─────────┘
         │
         ▼
    Results + Dynamic Replan
```

### Execution Flow

```
1. User provides goal: "Research FastAPI and create a project"
2. GoalDecomposer breaks it into tasks:
   - Search web for FastAPI documentation
   - Summarize key concepts
   - Create project structure
   - Initialize git repository
   - Create main.py with boilerplate
3. DependencyGraph determines execution order:
   - Tasks 1-2 can run sequentially
   - Tasks 3-5 depend on task 2 completion
4. TaskExecutor runs tasks, reporting progress
5. If a task fails, PlanningEngine triggers replanning
6. Final results are aggregated and returned
```

## Capabilities

### Planning

| Command | Description |
|---------|-------------|
| `plan <goal>` | Create and immediately execute a plan |
| `create plan <goal>` | Create a plan without executing |
| `start plan <id>` | Start executing an existing plan |
| `stop plan` | Stop current plan execution |
| `pause plan <id>` | Pause a plan |
| `cancel plan <id>` | Cancel a plan |
| `replan <id>` | Replan an active plan |

### Monitoring

| Command | Description |
|---------|-------------|
| `plan status <id>` | Get detailed plan status with task breakdown |
| `plan progress <id>` | Get plan progress percentage |
| `list plans` | List all plans |
| `active plans` | List currently active plans |
| `plan history <id>` | Get plan execution history |

### Templates

| Command | Description |
|---------|-------------|
| `templates` | List available goal templates |
| `add template` | Add a custom goal template |

### Statistics

| Command | Description |
|---------|-------------|
| `stats` | Get planning system statistics |

### Programmatic API

```python
# Create and execute a plan
result = planner_agent.create_and_execute(
    goal="Research FastAPI and create a project",
    context={"language": "python", "framework": "fastapi"},
)

# Get a plan by ID
plan = planner_agent.get_plan("plan_abc123")

# Get all active plans
active = planner_agent.get_active_plans()
```

## Internal Structure

### Plan Model

```python
@dataclass
class Plan:
    id: str
    goal: str
    status: PlanStatus              # draft, active, paused, completed, failed, cancelled
    tasks: list[PlanTask]
    created_at: str
    started_at: str
    completed_at: str
    created_by: str                 # user, system, agent
    replan_count: int
    context: dict

    @property
    def total_tasks(self) -> int: ...
    @property
    def completed_tasks(self) -> int: ...
    def get_progress(self) -> float: ...  # 0-100
    def get_task(self, task_id: str) -> PlanTask: ...
```

### Plan Task Model

```python
@dataclass
class PlanTask:
    id: str
    title: str
    description: str
    agent_name: str                 # Target agent for execution
    command: str                    # Command to execute
    status: TaskStatus              # pending, running, completed, failed, skipped
    priority: TaskPriority          # low, normal, high, critical
    dependencies: list[str]         # Task IDs this depends on
    result: str
    error: str
    started_at: str
    completed_at: str
    retry_count: int
    max_retries: int
```

### Task Status States

```
pending ──> running ──> completed
                │
                ├──> failed ──> (retry) ──> running
                │
                └──> skipped
```

### Replan Triggers

| Trigger | Description |
|---------|-------------|
| `task_failure` | A task failed and cannot be retried |
| `context_change` | External context changed, plan is no longer valid |
| `timeout` | Plan execution exceeded timeout |
| `user_request` | User explicitly requested replanning |
| `dependency_change` | Task dependencies changed |

### Goal Templates

Built-in templates for common goal patterns:

| Template | Description | Trigger Keywords |
|----------|-------------|-----------------|
| `research_and_implement` | Research a topic then implement | "research", "learn and build" |
| `setup_project` | Create and configure a new project | "create project", "setup" |
| `debug_and_fix` | Diagnose and fix an issue | "debug", "fix error" |
| `analyze_and_report` | Analyze data and generate report | "analyze", "report" |

## Usage Examples

### Creating and Executing a Plan

```
> plan Research FastAPI and create a project
Plan started: Research FastAPI and create a project
Progress: 0% (0/5 tasks)

Tasks:
  1. [NORMAL] Search web for FastAPI documentation -> web_agent
  2. [NORMAL] Summarize FastAPI key concepts -> coding_agent
  3. [NORMAL] Create project structure -> file_agent
  4. [NORMAL] Initialize git repository -> terminal_agent
  5. [NORMAL] Create main.py with boilerplate -> coding_agent

Executing autonomously...

  [COMPLETED] Search web for FastAPI documentation
  [COMPLETED] Summarize FastAPI key concepts
  [COMPLETED] Create project structure
  [COMPLETED] Initialize git repository
  [COMPLETED] Create main.py with boilerplate

Execution completed: 100%
  + Search web for FastAPI documentation: completed
  + Summarize FastAPI key concepts: completed
  + Create project structure: completed
  + Initialize git repository: completed
  + Create main.py with boilerplate: completed
```

### Checking Plan Status

```
> plan status plan_abc123
Plan: Research FastAPI and create a project
Status: active
Progress: 60%

Tasks:
  Search web for FastAPI documentation: completed
  Summarize FastAPI key concepts: completed
  Create project structure: completed
  Initialize git repository: running
  Create main.py with boilerplate: pending
```

### Replanning

```
> replan plan_abc123
Plan replanned (1 replans):

Tasks:
  1. Search web for FastAPI v2 migration guide -> web_agent
  2. Update project structure for v2 -> file_agent
  3. Migrate main.py to v2 syntax -> coding_agent
```

### Listing Plans

```
> list plans
Found 5 plans:

  plan_abc123: [completed] Research FastAPI and create a project (100%)
  plan_def456: [active] Build REST API with authentication (60%)
  plan_ghi789: [failed] Deploy to production (40%)
  plan_jkl012: [draft] Write unit tests (0%)
  plan_mno345: [paused] Refactor database layer (75%)
```

### Planning Statistics

```
> stats
Planning statistics retrieved
Data: {
  "total_plans": 47,
  "completed_plans": 32,
  "failed_plans": 5,
  "active_plans": 3,
  "avg_tasks_per_plan": 4.2,
  "avg_completion_time": "12.5 minutes",
  "replan_rate": "15%",
  "success_rate": "86%"
}
```

## Configuration

```json
{
  "agents": {
    "planner_agent": {
      "enabled": true,
      "max_parallel_tasks": 3,
      "default_timeout": 300,
      "max_retries": 2,
      "auto_replan": true,
      "use_llm_decomposition": true,
      "max_plans_retained": 50
    }
  }
}
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | bool | `true` | Enable/disable the agent |
| `max_parallel_tasks` | int | `3` | Maximum concurrent task executions |
| `default_timeout` | int | `300` | Default plan timeout in seconds |
| `max_retries` | int | `2` | Maximum retries per failed task |
| `auto_replan` | bool | `true` | Automatically replan on task failure |
| `use_llm_decomposition` | bool | `true` | Use LLM for goal decomposition |
| `max_plans_retained` | int | `50` | Maximum plans to retain in storage |

## Dependencies

| Dependency | Source | Purpose |
|------------|--------|---------|
| `core.base_agent` | Local | BaseAgent, AgentStatus |
| `core.config` | Local | Configuration access |
| `core.logger` | Local | Structured logging |
| `core.llm_provider` | Local | LLM access for goal decomposition |
| `networkx` | external | Dependency graph and topological sorting |
