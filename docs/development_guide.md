# Development Guide

## Local Development Setup

```bash
# Clone and setup
git clone https://github.com/Lucky-Joshi/Nexus-AI-Agent.git
cd Nexus-AI-Agent
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt

# Install dev dependencies
pip install pytest pytest-asyncio black ruff mypy
```

## Running NEXUS

```bash
# Normal mode (cinematic loader)
python main.py

# Verbose mode (see INFO logs)
python main.py --verbose

# Debug mode (full stack traces, all logs)
python main.py --debug

# Simple CLI (no Textual UI)
python main.py --cli
```

## Debugging

### Enable Debug Logging

Edit `config/settings.json`:
```json
{
  "logging": {
    "level": "DEBUG"
  }
}
```

### Use Python Debugger

```bash
python -m pdb main.py
```

Or add breakpoints:
```python
import pdb; pdb.set_trace()  # Python 3.6-
breakpoint()                  # Python 3.7+
```

### Inspect Agent State

```python
# In a Python shell
from main import initialize_nexus
manager = initialize_nexus()

# List all agents
manager.get_agent_status()

# Check routing
manager.router.detect_intent("search web for python")

# Test agent directly
agent = manager.agents["file_agent"]
agent.execute("system status")
```

## Testing Strategy

### Unit Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_router.py

# Run with coverage
pytest --cov=core --cov=manager --cov=agents tests/
```

### Test Structure

```
tests/
├── test_core/
│   ├── test_config.py
│   ├── test_database.py
│   ├── test_llm_provider.py
│   └── test_logger.py
├── test_manager/
│   ├── test_manager.py
│   ├── test_router.py
│   └── test_dispatcher.py
├── test_agents/
│   ├── test_file_agent.py
│   ├── test_web_agent.py
│   └── ...
└── test_terminal/
    ├── test_commands.py
    └── test_loader.py
```

## Code Quality

### Formatting

```bash
# Format with Black
black .

# Check formatting
black --check .
```

### Linting

```bash
# Lint with Ruff
ruff check .

# Auto-fix
ruff check --fix .
```

### Type Checking

```bash
# Type check with mypy
mypy core/ manager/ agents/ terminal/
```

## Project Structure

```
NEXUS/
├── main.py                    # Entry point
├── config/
│   └── settings.json          # Configuration
├── core/                      # Core infrastructure
│   ├── base_agent.py          # Abstract agent base class
│   ├── config.py              # Configuration manager
│   ├── database.py            # SQLite database engine
│   ├── llm_provider.py        # Ollama/OpenAI abstraction
│   └── logger.py              # Centralized logging
├── manager/                   # Orchestration layer
│   ├── manager.py             # AI Manager (central orchestrator)
│   ├── router.py              # 3-stage intent router
│   └── dispatcher.py          # Task dispatcher
├── agents/                    # 21 specialized agents
│   ├── file_agent/
│   ├── web_agent/
│   ├── coding_agent/
│   ├── automation_agent/
│   ├── vision_agent/
│   ├── memory_agent/
│   ├── knowledge_agent/
│   ├── terminal_agent/
│   ├── personality_agent/
│   ├── workflow_agent/
│   ├── plugin_agent/
│   ├── security_agent/
│   ├── notification_agent/
│   ├── scheduler_agent/
│   ├── workflow_chain_agent/
│   ├── analytics_agent/
│   ├── context_awareness_agent/
│   ├── learning_agent/
│   ├── communication_bus_agent/
│   ├── planner_agent/
│   └── marketplace_agent/
├── terminal/                  # Terminal UI
│   ├── app.py                 # Main Textual application
│   ├── theme.py               # Dark theme CSS
│   ├── loader.py              # Cinematic startup loader
│   ├── commands.py            # Slash command system
│   ├── streaming.py           # Response streaming
│   ├── widgets.py             # Reusable UI widgets
│   └── screens/
│       ├── dashboard.py       # Startup dashboard
│       ├── chat.py            # Main chat interface
│       └── tasks.py           # Task monitor
├── data/                      # Runtime data
│   ├── nexus.db               # Main SQLite database
│   ├── analytics.db           # Analytics data
│   ├── security.db            # Security events
│   ├── context.db             # Context history
│   ├── learning.db            # Learned patterns
│   ├── workflow_chains.db     # Chain executions
│   ├── memory/                # JSON memory files
│   ├── knowledge_vectors/     # ChromaDB vectors
│   └── scheduler/             # Scheduled tasks
├── logs/                      # Log files
│   └── nexus.log              # Application log
└── requirements.txt           # Python dependencies
```

## Adding New Features

### New Workflow Mode

1. Create JSON preset in `agents/workflow_agent/presets/`:
```json
{
  "name": "my_mode",
  "description": "My custom workflow mode",
  "steps": [
    {"agent": "file_agent", "command": "open vscode"},
    {"agent": "terminal_agent", "command": "cd project"}
  ]
}
```

### New Plugin

1. Create file in `agents/plugin_agent/plugins/`:
```python
# plugins/my_plugin.py
def execute(command, params):
    return {"success": True, "response": "Plugin executed"}

def get_capabilities():
    return ["my_command"]
```

### New Routing Rule

Add to `manager/router.py` `_build_rules()`:
```python
{
    "patterns": [r"\b(my keyword)\b"],
    "agent": "target_agent",
    "intent": "my_intent",
}
```

## Performance Tips

- **Reduce LLM calls**: Use regex/fuzzy routing before LLM fallback
- **Batch operations**: Use workflow chains for multi-step tasks
- **Cache results**: Memory agent stores frequent responses
- **Limit concurrent tasks**: Adjust `TaskDispatcher(max_workers=N)`
- **Monitor resources**: Use Analytics Agent dashboard

## Common Issues

| Problem | Solution |
|---------|----------|
| Agents not responding | Check `agent.status` is `IDLE` |
| Routing to wrong agent | Add more specific regex patterns |
| Slow startup | Disable unused agents in config |
| Memory growing | Check event log retention settings |
| Terminal UI glitches | Ensure `textual` is latest version |
