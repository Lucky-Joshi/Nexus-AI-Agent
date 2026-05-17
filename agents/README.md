# NEXUS Agents Module

> 21 specialized AI agents organized into categories: Core, Perception, Cognitive, Meta, Infrastructure, and UX.

## Purpose

The `agents` module contains all 21 specialized AI agents that provide NEXUS's capabilities. Each agent is a self-contained module that inherits from `BaseAgent` and implements domain-specific functionality -- from file operations and web research to autonomous planning and inter-agent communication.

## Architecture

```
agents/
├── __init__.py                    # Package exports
├── file_agent/                    # File/folder operations, system info, process management
├── web_agent/                     # Web search, scraping, summarization, research
├── coding_agent/                  # Code generation, explanation, git operations
├── automation_agent/              # Mouse/keyboard automation, workflows, screenshots
├── terminal_agent/                # Terminal command execution, scripting, sessions
├── vision_agent/                  # Screen capture, OCR, window analysis
├── memory_agent/                  # Persistent memory, preferences, workflows
├── knowledge_agent/               # Vector search, document management, semantic retrieval
├── notification_agent/            # Desktop notifications, reminders, focus mode
├── scheduler_agent/               # Task scheduling, cron-like execution, reminders
├── personality_agent/             # Tone, persona, emotion, communication style
├── workflow_agent/                # Workflow modes (Coding, Study, Deep Work, etc.)
├── security_agent/                # Risk analysis, process scanning, audit logging
├── plugin_agent/                  # Plugin lifecycle, sandbox, security scanning
├── workflow_chain_agent/          # Multi-agent chains, templates, async execution
├── analytics_agent/               # Usage tracking, performance metrics, dashboards
├── context_awareness_agent/       # Activity detection, focus monitoring, suggestions
├── learning_agent/                # Pattern detection, behavior analysis, predictions
├── communication_bus_agent/       # Pub/sub event bus, shared state, message broker
├── planner_agent/                 # Goal decomposition, dependency graphs, parallel execution
└── marketplace_agent/             # Agent browsing, installation, verification, reviews
```

### Agent Categories

| Category | Agents | Purpose |
|----------|--------|---------|
| **Core** | `file_agent`, `web_agent`, `coding_agent`, `automation_agent`, `terminal_agent` | Direct user task execution |
| **Perception** | `vision_agent`, `context_awareness_agent` | Screen/window/activity understanding |
| **Cognitive** | `memory_agent`, `knowledge_agent`, `learning_agent` | Persistent memory and pattern learning |
| **Meta** | `planner_agent`, `marketplace_agent`, `workflow_chain_agent` | Multi-agent orchestration |
| **Infrastructure** | `communication_bus_agent`, `analytics_agent`, `security_agent` | System-level services |
| **UX** | `notification_agent`, `scheduler_agent`, `personality_agent`, `workflow_agent`, `plugin_agent` | User experience enhancement |

## Agent Contract

All agents inherit from `BaseAgent` and must implement two abstract methods:

```python
from core.base_agent import BaseAgent, AgentStatus

class MyAgent(BaseAgent):
    def __init__(self):
        super().__init__("my_agent", "Description of capabilities")

    def execute(self, command: str, params: dict = None) -> dict:
        """Execute a command and return a result dict."""
        self.status = AgentStatus.BUSY
        try:
            # Implementation
            return {
                "success": True,
                "response": "Result text",
                "data": {...}  # Optional structured data
            }
        finally:
            self.status = AgentStatus.IDLE

    def get_capabilities(self) -> list:
        """List command keywords this agent understands."""
        return ["capability_1", "capability_2"]
```

### Response Format

Every agent's `execute()` method returns a dictionary:

```python
{
    "success": True,              # Whether execution succeeded
    "response": "Human-readable text",
    "data": {...},                # Optional structured data
    "task_id": "abc12345",        # Set by TaskDispatcher
    "elapsed_seconds": 0.42,      # Set by TaskDispatcher
}
```

## Agent Directory

### File Agent (`file_agent/`)

File and system operations.

| Capability | Example Command |
|------------|-----------------|
| Open applications | `"open notepad"` |
| Create/delete/rename files | `"create file test.txt"` |
| Search files | `"search files for report"` |
| System info | `"system status"` |
| Kill processes | `"kill process chrome"` |
| Organize downloads | `"organize downloads"` |

**Structure:**

```
file_agent/
├── __init__.py
├── agent.py          # FileAgent class
├── services.py       # File operations, system info services
└── utils.py          # Helper utilities
```

### Web Agent (`web_agent/`)

Web research and content extraction.

| Capability | Example Command |
|------------|-----------------|
| Web search | `"search web for Python"` |
| Scrape pages | `"scrape page https://..."` |
| Summarize URLs | `"summarize url https://..."` |
| Research topics | `"research AI trends"` |
| Compare options | `"compare React vs Vue"` |
| Extract keywords | `"extract keywords from article"` |

### Coding Agent (`coding_agent/`)

Code generation, analysis, and git operations.

| Capability | Example Command |
|------------|-----------------|
| Generate code | `"generate code for REST API"` |
| Explain code | `"explain this code: ..."` |
| Debug code | `"debug this error: ..."` |
| Git operations | `"git status"` |
| Analyze repos | `"analyze repository"` |
| Edit files | `"edit file main.py"` |

### Automation Agent (`automation_agent/`)

Desktop automation and workflow execution.

| Capability | Example Command |
|------------|-----------------|
| Screenshot | `"take screenshot"` |
| Mouse/keyboard | `"click at 100,200"` |
| Run workflows | `"start coding mode"` |
| Hotkeys | `"press ctrl+c"` |

### Terminal Agent (`terminal_agent/`)

Terminal command execution and scripting.

| Capability | Example Command |
|------------|-----------------|
| Run commands | `"run python script.py"` |
| Execute scripts | `"run file deploy.bat"` |
| Stream output | `"stream ping google.com"` |
| Session management | `"new session"` |
| Command history | `"command history"` |
| Safety validation | `"check command rm -rf /"` |

### Vision Agent (`vision_agent/`)

Screen capture and visual analysis.

| Capability | Example Command |
|------------|-----------------|
| Screenshot | `"take screenshot"` |
| OCR | `"read text from screen"` |
| Window detection | `"what window is active"` |
| Screen analysis | `"analyze screen"` |
| Monitor info | `"monitor info"` |

### Memory Agent (`memory_agent/`)

Persistent memory and preference storage.

| Capability | Example Command |
|------------|-----------------|
| Save memories | `"remember my project path"` |
| Recall memories | `"what do you remember about Python"` |
| Preferences | `"set preference theme = dark"` |
| Workflow storage | `"save workflow my_routine"` |
| List/clear | `"list memories"` |

### Knowledge Agent (`knowledge_agent/`)

Vector-based knowledge management with ChromaDB.

| Capability | Example Command |
|------------|-----------------|
| Add documents | `"add document about AI"` |
| Semantic search | `"search knowledge for ML"` |
| Tag management | `"tag document 1 with AI"` |
| Summarization | `"summarize document 1"` |
| Index management | `"rebuild index"` |

### Notification Agent (`notification_agent/`)

Desktop notifications and reminders.

| Capability | Example Command |
|------------|-----------------|
| Send notification | `"send notification Hello"` |
| Set reminders | `"set reminder meeting at 3pm"` |
| Focus mode | `"enable focus mode"` |
| Queue management | `"clear notifications"` |
| History | `"notification history"` |

### Scheduler Agent (`scheduler_agent/`)

Task scheduling and timed execution.

| Capability | Example Command |
|------------|-----------------|
| Create schedule | `"schedule task every hour"` |
| List schedules | `"list schedules"` |
| Run now | `"run task backup"` |
| Cancel | `"cancel schedule 1"` |
| Execution history | `"execution history"` |

### Personality Agent (`personality_agent/`)

Communication style and persona management.

| Capability | Example Command |
|------------|-----------------|
| Set personality | `"set personality professional"` |
| Adjust tone | `"set tone casual"` |
| Humor level | `"set humor high"` |
| Custom profiles | `"create profile mentor"` |
| Emotion tracking | `"current emotion"` |

### Workflow Agent (`workflow_agent/`)

Preset workflow modes for focused work.

| Capability | Example Command |
|------------|-----------------|
| Start mode | `"start coding mode"` |
| List modes | `"list modes"` |
| Mode status | `"current mode"` |
| Custom modes | `"create mode my_workflow"` |
| Productivity stats | `"mode stats"` |

**Available Modes:** Coding, Study, Deep Work, Content Creation, Meeting, Research, Cybersecurity, Design, Writing, Gaming, AI Development, Project Management.

### Security Agent (`security_agent/`)

Command risk analysis and system security.

| Capability | Example Command |
|------------|-----------------|
| Analyze risk | `"analyze command rm -rf /"` |
| System health | `"system health check"` |
| Process scan | `"scan processes"` |
| Monitor | `"start monitoring"` |
| Audit logs | `"show audit log"` |
| Permissions | `"list permissions"` |
| File protection | `"protect file config.json"` |

### Plugin Agent (`plugin_agent/`)

Plugin lifecycle and sandboxed execution.

| Capability | Example Command |
|------------|-----------------|
| Install plugin | `"install plugin my_plugin"` |
| List plugins | `"list plugins"` |
| Enable/disable | `"enable my_plugin"` |
| Security scan | `"analyze plugin my_plugin"` |
| Run plugin | `"run my_plugin with args"` |

### Workflow Chain Agent (`workflow_chain_agent/`)

Multi-agent execution chains with data passing.

| Capability | Example Command |
|------------|-----------------|
| Run chain | `"run chain research_and_summarize"` |
| Create chain | `"create chain my_chain"` |
| Chain status | `"chain status"` |
| Templates | `"list templates"` |
| Async execution | `"run async my_chain"` |

**Built-in Templates:**

| Template | Description |
|----------|-------------|
| `prepare_coding_workspace` | Sets up file structure, opens editor, initializes project |
| `research_and_summarize` | Web research -> knowledge storage -> summary generation |

### Analytics Agent (`analytics_agent/`)

Usage tracking and performance metrics.

| Capability | Example Command |
|------------|-----------------|
| Dashboard | `"dashboard"` |
| Usage stats | `"usage stats"` |
| Agent performance | `"agent performance"` |
| Resource monitor | `"resource monitor"` |
| Productivity report | `"productivity report"` |
| Session tracking | `"start session"` |

### Context Awareness Agent (`context_awareness_agent/`)

User activity detection and contextual suggestions.

| Capability | Example Command |
|------------|-----------------|
| Current context | `"current context"` |
| Active window | `"active window"` |
| Running apps | `"running apps"` |
| Focus level | `"focus level"` |
| Suggest workflow | `"suggest workflow"` |
| Activity detection | `"detect activity"` |

### Learning Agent (`learning_agent/`)

Behavior pattern analysis and predictions.

| Capability | Example Command |
|------------|-----------------|
| Start learning | `"start learning"` |
| Analyze patterns | `"analyze patterns"` |
| Detected habits | `"my habits"` |
| Recommendations | `"recommendations"` |
| Predict next action | `"predict next"` |
| Generate workflow | `"generate workflow from pattern"` |

### Communication Bus Agent (`communication_bus_agent/`)

Inter-agent pub/sub messaging and shared state.

| Capability | Example Command |
|------------|-----------------|
| Publish event | `"publish event task.completed"` |
| Subscribe | `"subscribe to task.*"` |
| Send message | `"send message to file_agent"` |
| Shared state | `"set state mode = coding"` |
| Event logs | `"event logs"` |
| Dead letter queue | `"dlq messages"` |

**Architecture:**

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  Publisher  │────>│  Event Bus   │────>│ Subscriber  │
│  (Agent A)  │     │  (8 workers) │     │  (Agent B)  │
└─────────────┘     └──────┬───────┘     └─────────────┘
                           │
                    ┌──────┴───────┐
                    │  Shared      │
                    │  State Store │
                    └──────────────┘
```

### Planner Agent (`planner_agent/`)

Autonomous goal decomposition and multi-step planning.

| Capability | Example Command |
|------------|-----------------|
| Create plan | `"plan a research workflow"` |
| Execute plan | `"execute plan abc123"` |
| Plan status | `"plan status"` |
| Replan | `"replan abc123"` |
| Templates | `"list templates"` |
| Goal breakdown | `"break down build a web app"` |

**Architecture:**

```
User Goal
    │
    ▼
┌──────────────────┐
│ GoalDecomposer   │  Template -> Rules -> LLM
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ DependencyGraph  │  Topological sort
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ TaskExecutor     │  Parallel (3 concurrent)
└────────┬─────────┘
         │
         ▼
    Results + Dynamic Replan
```

**Structure:**

```
planner_agent/
├── __init__.py
├── agent.py                 # PlannerAgent class
├── dependency_graph.py      # Task dependency resolution
├── goal_decomposition.py    # Goal -> subtasks
├── models.py                # Plan, Task data models
├── planning_engine.py       # Core planning logic
├── storage.py               # Plan persistence
└── task_executor.py         # Parallel task execution
```

### Marketplace Agent (`marketplace_agent/`)

Agent discovery, installation, and management.

| Capability | Example Command |
|------------|-----------------|
| Browse agents | `"browse marketplace"` |
| Search agents | `"search agents for data"` |
| Install agent | `"install agent data_agent"` |
| Uninstall | `"uninstall agent data_agent"` |
| Verify security | `"verify agent data_agent"` |
| Reviews | `"reviews for data_agent"` |
| Updates | `"check for updates"` |

## Usage Examples

### Creating a Custom Agent

```python
from core.base_agent import BaseAgent, AgentStatus
from core.config import Config
from core.logger import Logger

class WeatherAgent(BaseAgent):
    def __init__(self):
        super().__init__("weather_agent", "Fetch weather data for locations")
        self.logger = Logger().get_logger("WeatherAgent")
        self.config = Config()

    def execute(self, command: str, params: dict = None) -> dict:
        self.status = AgentStatus.BUSY
        try:
            params = params or {}
            command_lower = command.lower()

            if "get weather" in command_lower or "weather" in command_lower:
                location = params.get("location", "unknown")
                return {
                    "success": True,
                    "response": f"Weather in {location}: Sunny, 72F",
                    "data": {"location": location, "temp": 72, "condition": "sunny"},
                }
            elif "forecast" in command_lower:
                return {
                    "success": True,
                    "response": "5-day forecast: Sunny all week",
                }
            else:
                return {
                    "success": False,
                    "response": f"Unknown command: {command}",
                }
        except Exception as e:
            self.logger.error(f"Execution error: {e}")
            return {"success": False, "error": str(e)}
        finally:
            self.status = AgentStatus.IDLE

    def get_capabilities(self) -> list:
        return ["get_weather", "forecast", "weather_alerts"]
```

### Registering and Using an Agent

```python
from manager.manager import AIManager
from agents.weather_agent import WeatherAgent

manager = AIManager()
manager.register_agent(WeatherAgent())

# Process command
result = manager.process_command("get weather for Tokyo")
print(result["response"])
# Output: Weather in Tokyo: Sunny, 72F

# Check capabilities
status = manager.get_agent_status()
print(status["weather_agent"]["capabilities"])
# Output: ["get_weather", "forecast", "weather_alerts"]
```

### Inter-Agent Communication via Bus

```python
from agents.communication_bus_agent.agent import CommunicationBusAgent

bus = CommunicationBusAgent()

# Agent A publishes event
bus.publish_event("task.completed", {
    "task_id": "123",
    "result": "success",
    "agent": "file_agent",
})

# Agent B subscribes
def on_task_complete(event_data):
    print(f"Task {event_data['task_id']} completed by {event_data['agent']}")

bus.subscribe("task.*", on_task_complete)

# Direct message between agents
bus.send_message("coding_agent", "file_agent", {
    "action": "save_file",
    "path": "output.py",
    "content": "print('hello')",
})

# Shared state
bus.set_state("current_mode", "coding")
mode = bus.get_state("current_mode")
```

### Using the Planner for Multi-Step Goals

```python
from agents.planner_agent.agent import PlannerAgent

planner = PlannerAgent()

# Create a plan from a goal
plan = planner.create_plan(
    goal="Research FastAPI and create a project",
    template="research_and_implement",
)

# Execute the plan
result = planner.execute_plan(plan.id)

# Check progress
status = planner.get_plan_status(plan.id)
print(f"Progress: {status['completed_tasks']}/{status['total_tasks']}")
```

## Dependencies

### Common Dependencies (all agents)

| Dependency | Source | Purpose |
|------------|--------|---------|
| `core.base_agent` | Local | BaseAgent, AgentStatus |
| `core.config` | Local | Configuration access |
| `core.logger` | Local | Structured logging |
| `core.llm_provider` | Local | LLM access (for agents using AI) |
| `core.database` | Local | Data persistence |

### Agent-Specific Dependencies

| Agent | Additional Dependencies |
|-------|------------------------|
| `file_agent` | `psutil` |
| `web_agent` | `requests`, `beautifulsoup4`, `duckduckgo-search` |
| `coding_agent` | `gitpython` |
| `automation_agent` | `pyautogui`, `mss` |
| `vision_agent` | `opencv-python`, `easyocr`, `pytesseract`, `mss` |
| `knowledge_agent` | `chromadb`, `sentence-transformers` |
| `notification_agent` | `win10toast` (Windows), `plyer` (cross-platform) |
| `security_agent` | `psutil` |
| `context_awareness_agent` | `psutil` |
| `communication_bus_agent` | `queue`, `threading` (stdlib) |
| `planner_agent` | `networkx` (dependency graphs) |

## Configuration

Each agent can be enabled/disabled and configured via `config/settings.json`:

```json
{
  "agents": {
    "file_agent": {
      "enabled": true,
      "watch_downloads": true
    },
    "web_agent": {
      "enabled": true,
      "default_search_engine": "duckduckgo"
    },
    "coding_agent": {
      "enabled": true,
      "default_language": "python",
      "workspace_path": ""
    },
    "vision_agent": {
      "enabled": true,
      "screenshot_dir": "data/screenshots",
      "ocr_languages": ["en"],
      "use_gpu": false
    },
    "terminal_agent": {
      "enabled": true,
      "strict_mode": true,
      "default_timeout": 30
    },
    "security_agent": {
      "enabled": true,
      "auto_block_critical": true,
      "max_risk_level": "medium"
    },
    "planner_agent": {
      "enabled": true,
      "max_parallel_tasks": 3,
      "default_timeout": 300
    },
    "communication_bus_agent": {
      "enabled": true,
      "max_workers": 8,
      "default_ttl": 300
    }
  }
}
```

See `core/README.md` for the complete configuration reference with all 21 agent settings.

## Adding New Agents

1. **Create agent directory:** `agents/my_agent/`
2. **Create agent class:** `agents/my_agent/agent.py` inheriting from `BaseAgent`
3. **Implement `execute()` and `get_capabilities()`**
4. **Add routing rules** in `manager/router.py` (regex patterns + fuzzy keywords)
5. **Add agent description** in Router's `_build_agent_descriptions()`
6. **Register in `main.py`** `initialize_nexus()` function
7. **Add configuration** in `core/config.py` `_default_config()` under `agents.my_agent`
8. **Add to `requirements.txt`** if new dependencies are needed
