# NEXUS Core Module

> Foundational infrastructure: configuration, logging, database, LLM abstraction, and the base agent contract.

## Purpose

The `core` module provides the foundational building blocks that every other module in NEXUS depends on. It implements singleton services for configuration management, structured logging, SQLite persistence, a unified LLM provider interface (supporting both Ollama and OpenAI), and the abstract `BaseAgent` class that all 21 specialized agents inherit from.

## Architecture

```
core/
├── __init__.py          # Package exports
├── base_agent.py        # Abstract BaseAgent class, AgentStatus enum
├── config.py            # Singleton Config with dot-notation access
├── database.py          # Singleton SQLite manager with context-managed connections
├── llm_provider.py      # Unified LLM interface (Ollama + OpenAI)
└── logger.py            # Singleton Logger with rotating file + console handlers
```

### Design Patterns

| Pattern | Usage |
|---------|-------|
| **Singleton** | `Config`, `Logger`, `Database` -- one shared instance across the entire application |
| **Abstract Base Class** | `BaseAgent` -- enforces `execute()` and `get_capabilities()` on all agents |
| **Strategy** | `LLMProvider` -- swaps between Ollama and OpenAI strategies transparently |
| **Context Manager** | `Database._get_connection()` -- ensures transactional safety with automatic commit/rollback |

## Components

### Config (`config.py`)

Centralized configuration management with hierarchical JSON storage and dot-notation access.

**Key APIs:**

| Method | Signature | Description |
|--------|-----------|-------------|
| `get` | `get(key: str, default: Any = None) -> Any` | Retrieve a config value by dot-notation key |
| `set` | `set(key: str, value: Any)` | Set and persist a config value |
| `save` | `save()` | Write current config to `config/settings.json` |
| `config` | `property -> dict` | Get a copy of the full configuration dict |

**Example:**

```python
from core.config import Config

config = Config()

# Read nested values
provider = config.get("llm.provider", "ollama")
model = config.get("llm.ollama.model", "llama3")
enabled = config.get("agents.file_agent.enabled", True)

# Write and persist
config.set("llm.ollama.model", "llama3.2")
```

### Logger (`logger.py`)

Structured logging with rotating file handler and configurable console output.

**Key APIs:**

| Method | Signature | Description |
|--------|-----------|-------------|
| `get_logger` | `get_logger(name: str) -> logging.Logger` | Get a child logger scoped to a component |
| `set_mode` | `set_mode(mode: str)` | Set console level: `normal` (WARNING+), `verbose` (INFO+), `debug` (DEBUG+) |
| `suppress_console` | `suppress_console()` | Mute console output (file logging continues) |
| `enable_console` | `enable_console(level: str)` | Re-enable console at a specific log level |

**Example:**

```python
from core.logger import Logger

logger = Logger()
log = logger.get_logger("MyComponent")

log.debug("Detailed debug info")
log.info("System starting up")
log.warning("LLM provider unavailable")
log.error("Database connection failed")

# Switch to verbose mode for more console output
logger.set_mode("verbose")
```

### Database (`database.py`)

Thread-safe SQLite manager with automatic schema initialization and context-managed connections.

**Key APIs:**

| Method | Signature | Description |
|--------|-----------|-------------|
| `execute` | `execute(query: str, params: tuple = ()) -> Cursor` | Execute a single SQL statement |
| `fetchone` | `fetchone(query: str, params: tuple = ()) -> Optional[Row]` | Fetch a single row |
| `fetchall` | `fetchall(query: str, params: tuple = ()) -> list` | Fetch all matching rows |
| `executemany` | `executemany(query: str, params_list: list)` | Execute with multiple parameter sets |
| `db_path` | `property -> str` | Path to the SQLite database file |

**Schema Tables:**

| Table | Purpose |
|-------|---------|
| `conversations` | Chat history with session IDs, roles, timestamps |
| `memory` | Key-value memory entries with categories |
| `tasks` | Task execution records with status tracking |
| `preferences` | User preference key-value store |
| `workflows` | Saved workflow definitions |

**Example:**

```python
from core.database import Database

db = Database()

# Insert
db.execute(
    "INSERT INTO tasks (task_id, status, agent, command) VALUES (?, ?, ?, ?)",
    ("abc123", "pending", "file_agent", "open notepad"),
)

# Query
rows = db.fetchall("SELECT * FROM tasks ORDER BY created_at DESC LIMIT ?", (10,))
for row in rows:
    print(dict(row))
```

### LLMProvider (`llm_provider.py`)

Unified interface for interacting with large language models. Supports Ollama (local) and OpenAI (cloud) with automatic fallback.

**Key APIs:**

| Method | Signature | Description |
|--------|-----------|-------------|
| `chat` | `chat(messages: List[Dict], model?, temperature?) -> str` | Send conversation messages, get response |
| `generate` | `generate(prompt: str, system_prompt?, model?, temperature?) -> str` | Single-prompt generation |
| `stream` | `stream(messages: List[Dict], model?, temperature?) -> Generator[str]` | Token-by-token streaming |
| `is_available` | `is_available() -> bool` | Check if the LLM provider is reachable |
| `get_model` | `get_model() -> str` | Get the current model name |
| `get_provider_name` | `get_provider_name() -> str` | Get active provider (`ollama` or `openai`) |

**Example:**

```python
from core.llm_provider import LLMProvider

llm = LLMProvider()

# Simple generation
response = llm.generate("Explain Python decorators", system_prompt="Be concise.")

# Multi-turn chat
response = llm.chat([
    {"role": "system", "content": "You are NEXUS, a helpful AI."},
    {"role": "user", "content": "What can you do?"},
])

# Streaming tokens
for token in llm.stream([{"role": "user", "content": "Write a haiku"}]):
    print(token, end="", flush=True)

# Health check
if llm.is_available():
    print(f"Using {llm.get_provider_name()} with {llm.get_model()}")
```

### BaseAgent (`base_agent.py`)

Abstract base class that defines the contract for all NEXUS agents.

**AgentStatus Enum:**

| Status | Value | Description |
|--------|-------|-------------|
| `IDLE` | `"idle"` | Agent is available for tasks |
| `BUSY` | `"busy"` | Agent is executing a task |
| `ERROR` | `"error"` | Agent encountered an error |
| `OFFLINE` | `"offline"` | Agent has been shut down |

**Key APIs:**

| Method | Signature | Description |
|--------|-----------|-------------|
| `execute` | `execute(command: str, params: dict?) -> dict` | **(abstract)** Execute a command |
| `get_capabilities` | `get_capabilities() -> list` | **(abstract)** List supported capabilities |
| `is_available` | `is_available() -> bool` | Check if agent is idle |
| `to_dict` | `to_dict() -> dict` | Serialize agent state |
| `status` | `property: AgentStatus` | Thread-safe status getter/setter |

**Example -- Creating a Custom Agent:**

```python
from core.base_agent import BaseAgent, AgentStatus

class WeatherAgent(BaseAgent):
    def __init__(self):
        super().__init__("weather_agent", "Fetch weather data")

    def execute(self, command: str, params: dict = None) -> dict:
        self.status = AgentStatus.BUSY
        try:
            # Implementation here
            return {"success": True, "response": "Sunny, 72F"}
        finally:
            self.status = AgentStatus.IDLE

    def get_capabilities(self) -> list:
        return ["get_weather", "forecast"]
```

## Usage Examples

### Full Initialization Sequence

```python
from core.config import Config
from core.logger import Logger
from core.database import Database
from core.llm_provider import LLMProvider

# All singletons -- safe to instantiate anywhere
config = Config()
logger = Logger()
db = Database()
llm = LLMProvider()

log = logger.get_logger("App")
log.info(f"Config loaded: {config.get('app.name')}")
log.info(f"Database at: {db.db_path}")
log.info(f"LLM: {llm.get_provider_name()} / {llm.get_model()}")
```

### Configuration-Driven LLM Setup

```python
config = Config()

# Switch providers at runtime
config.set("llm.provider", "openai")
config.set("llm.openai.api_key", "sk-...")

# LLMProvider reads config on next instantiation
llm = LLMProvider()
```

## Dependencies

| Dependency | Purpose | Required |
|------------|---------|----------|
| `requests` | HTTP client for Ollama API | Yes |
| `openai` | OpenAI SDK (optional fallback) | No |
| Python `sqlite3` | Database engine | Yes (stdlib) |
| Python `logging` | Logging framework | Yes (stdlib) |
| Python `abc` | Abstract base classes | Yes (stdlib) |
| Python `enum` | Enumerations | Yes (stdlib) |

## Configuration

All configuration lives in `config/settings.json`. Core-relevant keys:

```json
{
  "app": {
    "name": "NEXUS",
    "version": "2.0.0",
    "debug": false
  },
  "llm": {
    "provider": "ollama",
    "use_in_agents": true,
    "ollama": {
      "base_url": "http://localhost:11434",
      "model": "llama3",
      "temperature": 0.7,
      "max_tokens": 2048
    },
    "openai": {
      "api_key": "",
      "model": "gpt-4",
      "temperature": 0.7,
      "max_tokens": 2048
    }
  },
  "database": {
    "path": "data/nexus.db",
    "auto_backup": true
  },
  "logging": {
    "level": "INFO",
    "file": "logs/nexus.log",
    "max_size_mb": 10,
    "backup_count": 5
  }
}
```

## Thread Safety

- `BaseAgent.status` uses a `threading.Lock` for concurrent read/write safety
- `Database` uses context managers with automatic commit/rollback per connection
- `Config` auto-saves on every `set()` call (not thread-locked; avoid concurrent writes)
- `Logger` relies on Python's built-in thread-safe logging handlers
