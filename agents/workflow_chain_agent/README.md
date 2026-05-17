# Workflow Chain Agent

> Multi-agent task chaining, autonomous workflow execution, dependency management, and conditional logic for NEXUS.

## Purpose

The Workflow Chain Agent orchestrates complex multi-step workflows by chaining together multiple NEXUS agents in sequence or parallel. It manages data passing between steps, handles dependencies, supports conditional branching, provides checkpoint-based recovery, and includes built-in templates for common workflows like research, coding setup, and system analysis.

## Architecture

```
workflow_chain_agent/
├── __init__.py
├── agent.py              # WorkflowChainAgent orchestrator
├── models.py             # ChainStep, ChainDefinition, ChainExecution, ExecutionContext, ChainTemplate
├── services.py           # ChainEngine, DependencyGraph, ConditionEvaluator, RecoveryManager
├── storage.py            # ChainStorage - persistence for chains, executions, templates
```

### Component Breakdown

| Component | Responsibility |
|-----------|---------------|
| `ChainEngine` | Core execution engine that processes chain definitions, manages step execution, and handles async mode |
| `DependencyGraph` | Resolves step dependencies using topological sorting to determine execution order |
| `ConditionEvaluator` | Evaluates step conditions (output matching, variable checks) for conditional branching |
| `RecoveryManager` | Manages checkpoints, recovery points, and resume-from-failure capabilities |
| `ChainStorage` | JSON-based persistence for chain definitions, execution records, and templates |

### Execution Model

```
Chain Definition
    │
    ▼
┌──────────────────┐
│ DependencyGraph  │  Topological sort -> execution order
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  ChainEngine     │  Execute steps in order
│                  │  Pass output variables between steps
│                  │  Evaluate conditions for branching
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ RecoveryManager  │  Checkpoints for resume capability
└────────┬─────────┘
         │
         ▼
    ChainExecution Result
```

### Variable Passing

Steps can reference outputs from previous steps using template syntax:

```
step1: web_agent -> "search web for {{topic}}"       output: search_results
step2: knowledge_agent -> "analyze {{search_results.output}}"  output: analysis
step3: coding_agent -> "summarize: {{analysis.output}}"
```

## Capabilities

### Chain Execution

| Command | Description |
|---------|-------------|
| `run chain <name>` | Execute a workflow chain synchronously |
| `run async <name>` | Execute a chain asynchronously |
| `cancel chain [id]` | Cancel a running chain execution |
| `chain status [id]` | Check execution status and progress |
| `resume chain <id>` | Resume a failed chain from checkpoint |

### Chain Management

| Command | Description |
|---------|-------------|
| `list chains` | Show all available chains and templates |
| `chain info <name>` | Display chain details and step definitions |
| `create chain <definition>` | Define a new custom chain |
| `delete chain <name>` | Remove a saved chain |

### Templates

| Command | Description |
|---------|-------------|
| `list templates` | Show available chain templates |
| `run template <name>` | Execute a template chain |

### Presets (Built-in Templates)

| Command | Description |
|---------|-------------|
| `prepare coding workspace` | Open VS Code, GitHub, terminal, load recent project |
| `research and summarize` | Web search -> knowledge analysis -> summary generation |
| `analyze system` | System health check -> process scan -> security report |

### History & Analytics

| Command | Description |
|---------|-------------|
| `execution history` | View past chain executions |
| `chain stats` | Show execution statistics and success rates |

### Programmatic API

```python
# Run a chain programmatically
execution = workflow_chain_agent.run_chain(
    chain=chain_definition,
    variables={"topic": "AI trends 2026"},
    async_mode=False,
)

# Cancel a running chain
workflow_chain_agent.cancel_chain(execution_id="abc12345")

# Check execution status
status = workflow_chain_agent.get_chain_status("abc12345")
```

## Internal Structure

### Chain Definition Model

```python
@dataclass
class ChainDefinition:
    id: str
    name: str
    description: str
    category: str                # development, research, security, maintenance
    tags: list[str]
    steps: list[ChainStep]
    timeout: int                 # seconds
    on_failure: FailureStrategy  # abort, continue, retry
    initial_variables: dict
```

### Chain Step Model

```python
@dataclass
class ChainStep:
    id: str
    name: str
    agent: str                   # Target agent name
    command: str                 # Command to execute (with variable templates)
    depends_on: list[str]        # Step IDs that must complete first
    condition: StepCondition     # Optional conditional execution
    output_variable: str         # Name to store this step's output
    timeout: int
    retry_count: int
```

### Condition Types

| Type | Description | Example |
|------|-------------|---------|
| `OUTPUT_CONTAINS` | Execute if previous step output contains pattern | `if "error" in step1.output` |
| `VARIABLE_EQUALS` | Execute if variable matches value | `if mode == "coding"` |
| `VARIABLE_EXISTS` | Execute if variable is defined | `if results is not None` |
| `ALWAYS` | Always execute (default) | No condition |

### Failure Strategies

| Strategy | Behavior |
|----------|----------|
| `abort` | Stop chain execution immediately |
| `continue` | Skip failed step, continue with next |
| `retry` | Retry failed step up to retry_count |

## Built-in Templates

### Coding Workspace

Sets up a complete development environment:

```
1. Open VS Code          -> file_agent
2. Open GitHub           -> file_agent         (depends on: 1)
3. Open Terminal         -> terminal_agent     (depends on: 1)
4. Load Recent Project   -> file_agent         (depends on: 2, 3)
```

### Research and Summarize

Multi-step research workflow:

```
1. Web Search            -> web_agent          output: search_results
2. Analyze Results       -> knowledge_agent    (depends on: 1) output: analysis
3. Generate Summary      -> coding_agent       (depends on: 2) output: final_summary
```

### Full System Analysis

Security-focused system check:

```
1. System Health         -> security_agent     output: health_report
2. Process Scan          -> security_agent     (depends on: 1) output: scan_results
3. Security Stats        -> security_agent     (depends on: 1)
4. Generate Report       -> coding_agent       (depends on: 2, 3) output: final_report
```

### System Cleanup

Automated maintenance workflow:

```
1. Check Disk Usage      -> file_agent         output: disk_info
2. Check Temp Files      -> file_agent         output: temp_info
3. Clean Temp Files      -> file_agent         (depends on: 2, condition: contains "temp")
4. Verify Cleanup        -> file_agent         (depends on: 3)
```

## Usage Examples

### Running a Preset

```
> research and summarize Python async patterns
Research: Python async patterns
Chain Execution: research_summarize
  [COMPLETED] Web Search -> web_agent (2.3s)
  [COMPLETED] Analyze Results -> knowledge_agent (1.8s)
  [COMPLETED] Generate Summary -> coding_agent (3.1s)
Steps: 3/3 completed | Duration: 7.2s | Status: COMPLETED
```

### Creating a Custom Chain

```
> create chain Deploy App with steps:
  build -> terminal_agent: run npm run build,
  test -> terminal_agent: run npm test (depends on: build),
  deploy -> terminal_agent: run deploy (depends on: test)
Chain 'Deploy App' created with 3 steps (ID: a1b2c3d4)
```

### Async Execution

```
> run async research_summarize
Chain 'research_summarize' started asynchronously. Execution ID: e5f6g7h8
Use 'chain status e5f6g7h8' to check progress.

> chain status e5f6g7h8
  e5f6g7h8: research_summarize - 2/3 steps
```

### Chain Definition Format

```
'create chain MyChain with steps:
 step1 -> file_agent: open vscode,
 step2 -> terminal_agent: new session (depends on: step1),
 step3 -> web_agent: search web for {{step2.output}} (depends on: step2)'
```

## Configuration

```json
{
  "agents": {
    "workflow_chain_agent": {
      "enabled": true,
      "max_concurrent_executions": 5,
      "default_timeout": 300,
      "checkpoint_enabled": true,
      "max_retries": 2,
      "async_worker_count": 3
    }
  }
}
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | bool | `true` | Enable/disable the agent |
| `max_concurrent_executions` | int | `5` | Maximum simultaneous chain executions |
| `default_timeout` | int | `300` | Default chain timeout in seconds |
| `checkpoint_enabled` | bool | `true` | Enable checkpoint-based recovery |
| `max_retries` | int | `2` | Default retry count for failed steps |
| `async_worker_count` | int | `3` | Number of async execution workers |

## Dependencies

| Dependency | Source | Purpose |
|------------|--------|---------|
| `core.base_agent` | Local | BaseAgent, AgentStatus |
| `core.config` | Local | Configuration access |
| `core.logger` | Local | Structured logging |
| `uuid` | stdlib | Unique execution IDs |
| `json` | stdlib | Chain definition serialization |
