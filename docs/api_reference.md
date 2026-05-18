# API Reference

## Core Modules

### Config

```python
from core.config import Config

config = Config()  # Singleton

# Get configuration value (dot notation)
value = config.get("llm.provider", "ollama")
value = config.get("agents.file_agent.enabled", True)

# Set and persist configuration value
config.set("llm.ollama.model", "llama3.2")

# Get full config copy
full_config = config.config
```

### Logger

```python
from core.logger import Logger

logger = Logger()  # Singleton
log = logger.get_logger("MyComponent")

log.debug("Debug message")
log.info("Info message")
log.warning("Warning message")
log.error("Error message")

# Change log mode
logger.set_mode("normal")    # WARNING+ to console
logger.set_mode("verbose")   # INFO+ to console
logger.set_mode("debug")     # DEBUG to console

# Suppress console output
logger.suppress_console()

# Enable console at specific level
logger.enable_console("INFO")
```

### Database

```python
from core.database import Database

db = Database()  # Singleton

# Execute query
db.execute("INSERT INTO tasks (command, status) VALUES (?, ?)", ("cmd", "pending"))

# Fetch rows
rows = db.fetchall("SELECT * FROM tasks ORDER BY created_at DESC LIMIT ?", (10,))

# Fetch single row
row = db.fetchone("SELECT COUNT(*) FROM tasks")
```

### LLMProvider

```python
from core.llm_provider import LLMProvider

llm = LLMProvider()

# Chat with messages
response = llm.chat([
    {"role": "system", "content": "You are helpful."},
    {"role": "user", "content": "Hello"},
])

# Generate from prompt
response = llm.generate("Explain Python decorators", system_prompt="Be concise.")

# Stream tokens
for token in llm.stream([{"role": "user", "content": "Write a poem"}]):
    print(token, end="", flush=True)

# Check availability
if llm.is_available():
    print(f"Provider: {llm.get_provider_name()}, Model: {llm.get_model()}")
```

### BaseAgent

```python
from core.base_agent import BaseAgent, AgentStatus

class MyAgent(BaseAgent):
    def __init__(self):
        super().__init__("my_agent", "Agent description")

    def execute(self, command: str, params: dict = None) -> dict:
        return {"success": True, "response": "Done"}

    def get_capabilities(self) -> list:
        return ["command_1", "command_2"]

# Usage
agent = MyAgent()
agent.status          # AgentStatus.IDLE
agent.is_available()  # True
agent.to_dict()       # {"name": ..., "status": ..., ...}
```

## Manager

### AIManager

```python
from manager.manager import AIManager

manager = AIManager()

# Register agent
manager.register_agent(agent)

# Process command (main entry point)
result = manager.process_command("search web for python")
# Returns: {"success": bool, "response": str, "agent": str, "intent": str, "task_id": str}

# Execute multi-step workflow
results = manager.execute_workflow([
    {"agent": "web_agent", "command": "research AI"},
    {"agent": "coding_agent", "command": "implement findings"},
])

# Get agent status
status = manager.get_agent_status()
# Returns: {"agent_name": {"status": "idle", "description": "...", "capabilities": [...]}}

# Get task history
tasks = manager.get_task_history(limit=20)

# Get conversation history
conversations = manager.get_conversation_history(session_id="abc123", limit=50)

# Properties
manager.session_id   # str
manager.agents       # Dict[str, BaseAgent]
manager.is_running   # bool

# Shutdown
manager.shutdown()
```

### Router

```python
from manager.router import Router

router = Router(use_llm=True, llm_provider=llm)

# Detect intent
routing = router.detect_intent("search the web for AI trends")
# Returns: {
#     "agent": "web_agent",
#     "intent": "web_search",
#     "confidence": 0.95,
#     "params": {"query": "AI trends"}
# }
```

### TaskDispatcher

```python
from manager.dispatcher import TaskDispatcher

dispatcher = TaskDispatcher(max_workers=4)

# Submit task
task_id = dispatcher.submit_task(agent, command, params)

# Execute task
result = dispatcher.execute_task(task_id, agent, command, params)

# Shutdown
dispatcher.shutdown(wait=True)
```

## Terminal

### CinematicLoader

```python
from terminal.loader import CinematicLoader, PhaseTracker, create_default_phases
from rich.console import Console

console = Console()
loader = CinematicLoader(console=console)
phases = create_default_phases(loader)

def init():
    with PhaseTracker(phases["core"], loader) as tracker:
        with tracker.step("Configuration"):
            pass
        with tracker.step("Database"):
            db = Database()
    return manager

manager = loader.run(init_fn=init)
```

### CommandRegistry

```python
from terminal.commands import CommandRegistry

reg = CommandRegistry()

# Register command
reg.register("status", "Show status", handler_fn, category="system")

# Execute command
result = reg.execute("/status", context={"manager": manager})

# Get autocomplete
suggestions = reg.get_autocomplete("/st")

# Get help
help_text = reg.get_help()
help_text = reg.get_help("system")  # Category-specific
```

### StreamingResponse

```python
from terminal.streaming import StreamingResponse, TypingAnimation

streamer = StreamingResponse(typing_speed=0.01)

# Register callback
streamer.on_chunk(lambda token: print(token, end=""))

# Stream async generator
async for token in streamer.stream_async(llm.stream(messages)):
    pass

# Stream sync generator
full = streamer.stream_sync(generator)
```

## Agents

### Agent Registration

```python
from core.base_agent import BaseAgent, AgentStatus

class CustomAgent(BaseAgent):
    def __init__(self):
        super().__init__("custom_agent", "Custom capabilities")

    def execute(self, command: str, params: dict = None) -> dict:
        self.status = AgentStatus.BUSY
        try:
            # Process command
            return {"success": True, "response": "Result"}
        finally:
            self.status = AgentStatus.IDLE

    def get_capabilities(self) -> list:
        return ["custom_action", "another_action"]
```

### Communication Bus

```python
from agents.communication_bus_agent.agent import CommunicationBusAgent

bus = CommunicationBusAgent()

# Publish event
bus.publish_event("task.completed", {"task_id": "123", "result": "ok"})

# Subscribe to events
bus.subscribe("task.*", callback_fn)

# Shared state
bus.set_state("current_mode", "coding")
mode = bus.get_state("current_mode")

# Direct message
bus.send_message("coding_agent", "file_agent", {"file": "main.py"})
```

### Planner

```python
from agents.planner_agent.agent import PlannerAgent

planner = PlannerAgent()

# Create plan
plan = planner.create_plan(
    goal="Research and implement a new feature",
    template="research_and_implement"
)

# Execute plan
result = planner.execute_plan(plan.id)

# Check progress
progress = planner.get_plan_status(plan.id)
```

## Configuration Reference

### Available Config Keys

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `app.name` | str | "NEXUS" | Application name |
| `app.version` | str | "2.0.0" | Application version |
| `llm.provider` | str | "ollama" | LLM provider (ollama/openai) |
| `llm.ollama.base_url` | str | "http://localhost:11434" | Ollama API URL |
| `llm.ollama.model` | str | "llama3" | Ollama model name |
| `llm.ollama.temperature` | float | 0.7 | Generation temperature |
| `llm.ollama.max_tokens` | int | 2048 | Max tokens |
| `llm.openai.api_key` | str | "" | OpenAI API key |
| `llm.openai.model` | str | "gpt-4" | OpenAI model |
| `database.path` | str | "data/nexus.db" | SQLite database path |
| `memory.max_context_length` | int | 50 | Max context messages |
| `logging.level` | str | "INFO" | Log level |
| `logging.file` | str | "logs/nexus.log" | Log file path |
| `terminal.theme` | str | "nexus" | Terminal theme name |
| `terminal.typing_speed` | float | 0.01 | Typing animation speed |

### Agent Config Keys

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `agents.{name}.enabled` | bool | true | Enable/disable agent |
| `agents.terminal_agent.strict_mode` | bool | true | Strict command validation |
| `agents.terminal_agent.default_timeout` | int | 30 | Command timeout (seconds) |
| `agents.knowledge_agent.embedding_model` | str | "all-MiniLM-L6-v2" | Embedding model |
| `agents.communication_bus_agent.max_workers` | int | 8 | Event bus workers |
| `agents.planner_agent.max_parallel_tasks` | int | 3 | Parallel task limit |
| `agents.security_agent.auto_block_critical` | bool | true | Auto-block critical risks |
