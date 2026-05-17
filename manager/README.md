# NEXUS Manager Module

> Central orchestration: AI Manager, 3-stage intent Router, and threaded TaskDispatcher.

## Purpose

The `manager` module is the brain of NEXUS. It receives user commands, determines intent through a three-stage routing pipeline, dispatches tasks to the appropriate specialized agent, tracks execution, and maintains conversation history. It is the single entry point through which all user interactions flow before reaching the agent layer.

## Architecture

```
manager/
├── __init__.py       # Package exports
├── manager.py        # AIManager -- central orchestrator
├── router.py         # Router -- 3-stage intent detection (regex -> fuzzy -> LLM)
└── dispatcher.py     # TaskDispatcher -- thread-safe task queue and executor
```

### Component Relationships

```
                    ┌─────────────────┐
                    │   AIManager     │
                    │  (Orchestrator) │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
        ┌──────────┐  ┌──────────┐  ┌──────────────┐
        │  Router  │  │Dispatcher│  │  LLMProvider │
        │(3-stage) │  │(threads) │  │  (core)      │
        └──────────┘  └──────────┘  └──────────────┘
              │              │
              ▼              ▼
        ┌─────────────────────────┐
        │    Registered Agents    │
        │  (21 specialized agents)│
        └─────────────────────────┘
```

## Components

### AIManager (`manager.py`)

The central orchestrator that ties together routing, dispatching, agent management, and conversation persistence.

**Lifecycle:**

1. Initialize LLM provider (Ollama or OpenAI)
2. Create Router with LLM reference
3. Create TaskDispatcher (4-worker thread pool)
4. Register agents via `register_agent()`
5. Process commands via `process_command()`
6. Shutdown gracefully via `shutdown()`

**Key APIs:**

| Method | Signature | Description |
|--------|-----------|-------------|
| `process_command` | `process_command(command: str, session_id?) -> dict` | Main entry point -- route, execute, and respond |
| `register_agent` | `register_agent(agent: BaseAgent)` | Register an agent with the manager |
| `unregister_agent` | `unregister_agent(agent_name: str)` | Remove a registered agent |
| `execute_workflow` | `execute_workflow(steps: List[dict]) -> list` | Run multi-step workflows across agents |
| `get_agent_status` | `get_agent_status() -> dict` | Get status of all registered agents |
| `get_task_history` | `get_task_history(limit: int = 20) -> list` | Query recent task history from DB |
| `get_conversation_history` | `get_conversation_history(session_id?, limit?) -> list` | Query conversation history |
| `shutdown` | `shutdown()` | Graceful shutdown of all components |

**Properties:**

| Property | Type | Description |
|----------|------|-------------|
| `session_id` | `str` | Unique 8-character session identifier |
| `agents` | `Dict[str, BaseAgent]` | Copy of registered agents dict |
| `is_running` | `bool` | Whether the manager is active |

**Response Format:**

```python
{
    "success": True,
    "response": "Here is the result...",
    "agent": "file_agent",
    "intent": "file_operation",
    "task_id": "abc12345",
    "data": {...}  # Optional structured data
}
```

**Example:**

```python
from manager.manager import AIManager
from agents.file_agent import FileAgent

manager = AIManager()
manager.register_agent(FileAgent())

# Process a single command
result = manager.process_command("open notepad")
print(result["response"])

# Execute a multi-step workflow
results = manager.execute_workflow([
    {"agent": "web_agent", "command": "research Python async"},
    {"agent": "coding_agent", "command": "write async example"},
])

# Check agent status
status = manager.get_agent_status()
for name, info in status.items():
    print(f"{name}: {info['status']}")

# Shutdown
manager.shutdown()
```

### Router (`router.py`)

Three-stage intent detection engine that determines which agent should handle a given command.

**Routing Pipeline:**

```
User Input
    │
    ▼
┌─────────────────────┐
│  Stage 1: Regex     │  200+ compiled patterns
│  (confidence >= 0.8)│  Fast, exact matching
└────────┬────────────┘
         │ < 0.8
         ▼
┌─────────────────────┐
│  Stage 2: Fuzzy     │  difflib keyword matching
│  (confidence > 0.65)│  Typo-tolerant
└────────┬────────────┘
         │ <= 0.65
         ▼
┌─────────────────────┐
│  Stage 3: LLM       │  JSON-structured routing
│  (if available)     │  Natural language understanding
└────────┬────────────┘
         │
         ▼
    Route to Agent
```

**Key APIs:**

| Method | Signature | Description |
|--------|-----------|-------------|
| `detect_intent` | `detect_intent(command: str) -> dict` | Run the 3-stage pipeline, return routing decision |

**Routing Decision Format:**

```python
{
    "agent": "web_agent",
    "intent": "web_search",
    "confidence": 0.95,
    "params": {"query": "AI trends"}
}
```

**Confidence Thresholds:**

| Stage | Threshold | Behavior |
|-------|-----------|----------|
| Regex | >= 0.8 | Direct routing, skip remaining stages |
| Fuzzy | > 0.65 | Route if regex failed |
| LLM | Any | Use if both regex and fuzzy are low confidence |

**Example:**

```python
from manager.router import Router
from core.llm_provider import LLMProvider

llm = LLMProvider()
router = Router(use_llm=True, llm_provider=llm)

# Detect intent
routing = router.detect_intent("search the web for AI trends")
print(f"Agent: {routing['agent']}")        # "web_agent"
print(f"Intent: {routing['intent']}")      # "web_search"
print(f"Confidence: {routing['confidence']}")  # 0.95
```

### TaskDispatcher (`dispatcher.py`)

Thread-safe task queue with execution tracking, supporting both synchronous and asynchronous execution.

**Key APIs:**

| Method | Signature | Description |
|--------|-----------|-------------|
| `submit_task` | `submit_task(agent, command, params?, callback?, timeout?) -> str` | Submit a task, returns task_id |
| `execute_task` | `execute_task(task_id, agent, command, params?) -> dict` | Execute immediately (blocking) |
| `execute_async` | `execute_async(task_id, agent, command, params?) -> str` | Execute in thread pool (non-blocking) |
| `get_task_status` | `get_task_status(task_id: str) -> dict?` | Get current task status |
| `get_active_tasks` | `get_active_tasks() -> list` | Get all pending/running tasks |
| `get_all_tasks` | `get_all_tasks() -> list` | Get all tasks |
| `cancel_task` | `cancel_task(task_id: str) -> bool` | Cancel a pending or running task |
| `shutdown` | `shutdown(wait: bool = True)` | Shut down the thread pool |

**Task Lifecycle:**

```
pending → running → completed
                 ↘ failed
                 ↘ cancelled
```

**Example:**

```python
from manager.dispatcher import TaskDispatcher
from agents.file_agent import FileAgent

dispatcher = TaskDispatcher(max_workers=4)
agent = FileAgent()

# Submit and execute synchronously
task_id = dispatcher.submit_task(agent, "open notepad", {})
result = dispatcher.execute_task(task_id, agent, "open notepad", {})
print(f"Completed in {result['elapsed_seconds']}s")

# Execute asynchronously
task_id = dispatcher.submit_task(agent, "system status", {})
dispatcher.execute_async(task_id, agent, "system status", {})

# Check status
status = dispatcher.get_task_status(task_id)
print(status["status"])  # "running" or "completed"

# Shutdown
dispatcher.shutdown(wait=True)
```

## Usage Examples

### Complete Command Processing

```python
from manager.manager import AIManager
from agents.file_agent import FileAgent
from agents.web_agent import WebAgent
from agents.coding_agent import CodingAgent

# Initialize
manager = AIManager()

# Register agents
manager.register_agent(FileAgent())
manager.register_agent(WebAgent())
manager.register_agent(CodingAgent())

# Process commands
commands = [
    "system status",
    "search web for Python best practices",
    "generate code for a REST API",
]

for cmd in commands:
    result = manager.process_command(cmd)
    print(f"[{result['agent'].upper()}] {result['response'][:100]}...")

# Clean up
manager.shutdown()
```

### Workflow Execution

```python
manager = AIManager()
# ... register agents ...

results = manager.execute_workflow([
    {"agent": "web_agent", "command": "research FastAPI vs Flask"},
    {"agent": "coding_agent", "command": "generate FastAPI boilerplate"},
    {"agent": "file_agent", "command": "create file main.py"},
])

for step in results:
    status = "OK" if step["success"] else "FAIL"
    print(f"Step {step['step']}: [{status}] {step['agent']}")
```

### REPL Loop

```python
manager = AIManager()
# ... register agents ...

while manager.is_running:
    command = input("nexus> ").strip()
    if command.lower() in ("exit", "quit"):
        break
    result = manager.process_command(command)
    print(f"\n{result['response']}\n")

manager.shutdown()
```

## Dependencies

| Dependency | Source | Purpose |
|------------|--------|---------|
| `core.base_agent` | Local | Agent interface and status enum |
| `core.config` | Local | Configuration access |
| `core.database` | Local | Task and conversation persistence |
| `core.llm_provider` | Local | LLM access for Stage 3 routing |
| `core.logger` | Local | Structured logging |
| `concurrent.futures` | stdlib | Thread pool for async execution |
| `uuid` | stdlib | Task and session ID generation |
| `re` | stdlib | Regex pattern matching |
| `difflib` | stdlib | Fuzzy keyword matching |

## Configuration

Manager behavior is controlled via `config/settings.json`:

```json
{
  "llm": {
    "provider": "ollama",
    "use_in_agents": true
  },
  "agents": {
    "file_agent": { "enabled": true },
    "web_agent": { "enabled": true }
  }
}
```

| Key | Default | Description |
|-----|---------|-------------|
| `llm.use_in_agents` | `true` | Enable LLM-based routing (Stage 3) |
| `llm.provider` | `"ollama"` | LLM provider for Stage 3 routing |

## Thread Safety

- `TaskDispatcher` uses `threading.Lock` for all task state mutations
- `ThreadPoolExecutor` (4 workers) handles concurrent async execution
- `BaseAgent.status` transitions are thread-safe (locked in core)
- `Database` connections are scoped per-operation (no shared connections)

## Error Handling

| Scenario | Behavior |
|----------|----------|
| No agent matches intent | Falls back to LLM conversation or returns error |
| Agent is busy | Returns "currently busy" message |
| Task execution fails | Returns error dict with `recoverable: True` |
| LLM unavailable | Falls back to offline response or regex/fuzzy routing |
| Agent not found in workflow | Logs warning, continues with remaining steps |
