# Contributing Guide

## Getting Started

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Run tests (when available)
5. Commit with conventional messages
6. Push and open a Pull Request

## Code Style

- Follow PEP 8 conventions
- Use type hints for function signatures
- Docstrings for all public classes and methods
- Maximum line length: 120 characters
- Use double quotes for strings

## Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add new agent for email automation
fix: resolve routing confidence threshold bug
docs: update architecture diagrams
refactor: extract LLM provider into separate module
test: add unit tests for router fuzzy matching
chore: update dependencies
```

## Adding a New Agent

1. Create directory: `agents/my_agent/`
2. Required files:
   - `__init__.py` -- Package init
   - `agent.py` -- Agent class extending `BaseAgent`
   - `services.py` -- Business logic services
   - `storage.py` -- Data persistence (if needed)

3. Implement required methods:
```python
from core.base_agent import BaseAgent, AgentStatus

class MyAgent(BaseAgent):
    def __init__(self):
        super().__init__("my_agent", "Description of capabilities")

    def execute(self, command: str, params: dict = None) -> dict:
        # Implement command handling
        return {"success": True, "response": "..."}

    def get_capabilities(self) -> list:
        return ["capability_1", "capability_2"]
```

4. Register in `main.py`:
```python
from agents.my_agent import MyAgent
# ... in initialize_nexus():
manager.register_agent(MyAgent())
```

5. Add routing rules in `manager/router.py`:
```python
{
    "patterns": [r"\b(my keyword)\b"],
    "agent": "my_agent",
    "intent": "my_intent",
}
```

## Architecture Guidelines

- **Single Responsibility**: Each agent handles one domain
- **Thin Agents**: Agents delegate to specialized service classes
- **Thread Safety**: Use locks for shared state
- **Error Handling**: Return structured error dicts, never raise
- **Logging**: Use `Logger().get_logger("ComponentName")`
- **Configuration**: Access via `Config().get("path.to.key")`

## Pull Request Process

1. Update documentation for any changed behavior
2. Ensure all existing tests pass
3. Add tests for new functionality
4. Request review from maintainers
5. Address review comments
6. Squash commits if requested

## Reporting Issues

Include:
- NEXUS version
- Python version
- OS and terminal emulator
- Steps to reproduce
- Expected vs actual behavior
- Relevant log output (`logs/nexus.log`)
