# NEXUS Terminal Module

> Cinematic terminal UI built with Textual: screens, widgets, streaming, commands, and animated loaders.

## Purpose

The `terminal` module provides the complete user interface layer for NEXUS. It transforms the terminal into a rich, interactive environment using the Textual TUI framework, featuring animated startup sequences, multi-screen navigation, real-time streaming responses, a slash command system with autocomplete, and a cohesive dark theme.

## Architecture

```
terminal/
├── __init__.py          # Package exports
├── app.py               # NEXUSTerminalApp -- main Textual application
├── theme.py             # NEXUS_THEME color tokens + full CSS stylesheet
├── loader.py            # CinematicLoader, PhaseTracker, StepTracker
├── commands.py          # CommandRegistry, Command dataclass
├── streaming.py         # StreamingResponse, TypingAnimation
├── widgets.py           # Reusable widgets (Header, StatusBar, Message, etc.)
└── screens/
    ├── __init__.py      # Screen package exports
    ├── dashboard.py     # DashboardScreen -- startup overview
    ├── chat.py          # ChatScreen -- main conversation interface
    └── tasks.py         # TaskScreen -- agent status and task monitor
```

### Screen Navigation

```
                    ┌──────────────┐
                    │  Dashboard   │  (initial screen)
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌──────────┐  ┌────────┐  ┌──────────┐
        │   Chat   │  │ Tasks  │  │ Dashboard│
        │          │  │        │  │ (return) │
        └────┬─────┘  └───┬────┘  └──────────┘
             │            │
             ▼            ▼
         Escape        Escape
         (back)       (back)
```

### Key Bindings

| Key | Action |
|-----|--------|
| `Ctrl+C` | Quit application |
| `Ctrl+D` | Quit application |
| `Ctrl+L` | Clear current screen |
| `Ctrl+K` | Show task monitor |
| `Ctrl+H` | Return to dashboard |
| `Escape` | Go back to previous screen |

## Components

### NEXUSTerminalApp (`app.py`)

The main Textual application that manages screen lifecycle, key bindings, and theme registration.

**Key APIs:**

| Method | Signature | Description |
|--------|-----------|-------------|
| `on_mount` | `on_mount() -> None` | Initialize theme, install screens, push dashboard |
| `action_quit` | `action_quit()` | Shutdown manager and exit |
| `action_clear_screen` | `action_clear_screen()` | Clear chat log on current screen |
| `action_show_tasks` | `action_show_tasks()` | Push task monitor screen |
| `action_show_dashboard` | `action_show_dashboard()` | Push dashboard screen |
| `action_back` | `action_back()` | Pop to previous screen |

**Example:**

```python
from terminal.app import NEXUSTerminalApp
from manager.manager import AIManager

manager = AIManager()
# ... register agents ...

app = NEXUSTerminalApp(manager)
app.run()
```

### CinematicLoader (`loader.py`)

Produces the animated startup sequence with grouped phases, spinners, progress bars, and a summary dashboard.

**Data Model:**

```
CinematicLoader
├── phases: List[StartupPhase]
│   ├── StartupPhase(name, steps, status)
│   │   ├── PhaseStep(name, status, message, duration)
│   │   └── PhaseStep(...)
│   └── StartupPhase(...)
└── render methods (banner, progress, phase lines, dashboard)
```

**Key APIs:**

| Method | Signature | Description |
|--------|-----------|-------------|
| `add_phase` | `add_phase(name: str) -> StartupPhase` | Add a new startup phase |
| `get_phase` | `get_phase(name: str) -> StartupPhase` | Get existing phase or create |
| `run` | `run(init_fn: Callable) -> Any` | Execute init function with animated loader |
| `step_start` | `step_start(step: PhaseStep)` | Mark step as running |
| `step_complete` | `step_complete(step, message?)` | Mark step as successful |
| `step_fail` | `step_fail(step, message?)` | Mark step as failed |
| `step_warn` | `step_warn(step, message?)` | Mark step with warning |
| `step_skip` | `step_skip(step, message?)` | Mark step as skipped |

**PhaseTracker (Context Manager):**

```python
from terminal.loader import CinematicLoader, PhaseTracker, create_default_phases
from rich.console import Console

console = Console()
loader = CinematicLoader(console=console)
phases = create_default_phases(loader)

with PhaseTracker(phases["core"], loader) as tracker:
    with tracker.step("Configuration") as step:
        config = Config()
    with tracker.step("Database") as step:
        db = Database()

manager = loader.run(init_fn=initialize_nexus)
```

**PhaseStatus Values:**

| Status | Icon | Color |
|--------|------|-------|
| `PENDING` | `·` | Gray |
| `RUNNING` | Spinner | Amber |
| `SUCCESS` | `✓` | Green |
| `FAILED` | `✗` | Red |
| `SKIPPED` | `-` | Gray |
| `WARNING` | `!` | Amber |

### CommandRegistry (`commands.py`)

Slash command parser with registration, execution, autocomplete, and categorized help.

**Command Dataclass:**

```python
@dataclass
class Command:
    name: str
    description: str
    handler: Callable
    aliases: List[str]
    category: str
    requires_args: bool
    arg_description: str
    autocomplete: List[str]
```

**Key APIs:**

| Method | Signature | Description |
|--------|-----------|-------------|
| `register` | `register(name, description, handler, aliases?, category?, ...)` | Register a new command |
| `execute` | `execute(text: str, context?) -> Any` | Parse and execute a command |
| `find_command` | `find_command(text: str) -> Command?` | Find matching command |
| `get_autocomplete` | `get_autocomplete(text: str) -> List[str]` | Get suggestions for partial input |
| `get_help` | `get_help(category?) -> str` | Generate formatted help text |
| `get_all_commands` | `get_all_commands() -> List[Command]` | Get all unique commands |
| `get_categories` | `get_categories() -> List[str]` | Get all category names |

**Example:**

```python
from terminal.commands import CommandRegistry

reg = CommandRegistry()

# Register a command
def status_handler(args, context):
    manager = context.get("manager")
    return {"success": True, "response": "All systems operational"}

reg.register(
    "status",
    "Show system status",
    status_handler,
    aliases=["s", "st"],
    category="system",
)

# Execute
result = reg.execute("/status", context={"manager": manager})

# Autocomplete
suggestions = reg.get_autocomplete("/st")  # ["/status"]

# Help
print(reg.get_help())
print(reg.get_help("system"))  # Category-specific
```

### StreamingResponse (`streaming.py`)

Token-by-token streaming handler for AI responses with typing animation support.

**Key APIs:**

| Method | Signature | Description |
|--------|-----------|-------------|
| `on_chunk` | `on_chunk(callback: Callable[[str], None])` | Register per-token callback |
| `stream_async` | `stream_async(generator) -> AsyncGenerator[str]` | Stream from async generator |
| `stream_sync` | `stream_sync(generator) -> str` | Stream from sync generator, returns full text |
| `reset` | `reset()` | Clear streaming state |
| `full_response` | `property -> str` | Complete accumulated response |
| `is_complete` | `property -> bool` | Whether streaming finished |

**Example:**

```python
from terminal.streaming import StreamingResponse

streamer = StreamingResponse(typing_speed=0.01)

# Register callback to update UI
streamer.on_chunk(lambda token: print(token, end="", flush=True))

# Stream from LLM
full_text = streamer.stream_sync(llm.stream(messages))
print(f"\nFull response: {full_text}")
```

### TypingAnimation (`streaming.py`)

Provides a cursor animation sequence for typing effects.

```python
from terminal.streaming import TypingAnimation

anim = TypingAnimation()
print(anim.next_frame())  # "▏"
print(anim.next_frame())  # "▎"
anim.reset()
```

### Widgets (`widgets.py`)

Reusable Textual widgets for building the terminal UI.

| Widget | Purpose |
|--------|---------|
| `NexusHeader` | Top bar with logo, session ID, agent count, active mode |
| `NexusStatusBar` | Bottom bar with status text, agent counts, task count, clock |
| `NexusAgentPanel` | Grid of all registered agents with status indicators |
| `NexusTaskPanel` | Task list with status icons (running, completed, failed, pending) |
| `NexusMessage` | Chat message panel with role-based styling (user/assistant/system) |
| `NexusDashboard` | Startup dashboard with system stats, agent summary, quick commands |
| `NexusCommandInput` | Command input area with styled prompt |

### Theme (`theme.py`)

Complete visual theme for the terminal UI.

**Color Tokens:**

| Token | Value | Usage |
|-------|-------|-------|
| `primary` | `#00D4FF` | Cyan -- borders, accents, headers |
| `secondary` | `#7B61FF` | Purple -- user messages, links |
| `warning` | `#FFB800` | Amber -- warnings, busy states |
| `error` | `#FF4757` | Red -- errors, failures |
| `success` | `#00E676` | Green -- success, idle states |
| `foreground` | `#E8E8E8` | Light gray -- primary text |
| `background` | `#0A0E17` | Near-black -- screen background |
| `surface` | `#111827` | Dark blue-gray -- panels, bars |
| `panel` | `#1A2332` | Medium dark -- sidebar, cards |

**CSS Layout Regions:**

| Region | Dock | Description |
|--------|------|-------------|
| `#header` | top | Application header bar |
| `#status-bar` | bottom | Status information bar |
| `#sidebar` | left | Navigation sidebar (30 chars) |
| `#command-input` | bottom | Command input area |
| `#task-panel` | right | Task monitor panel (40 chars) |
| `#chat-area` | main | Chat message area |
| `#main-content` | main | Primary content area |

### Screens (`screens/`)

| Screen | File | Description |
|--------|------|-------------|
| `DashboardScreen` | `dashboard.py` | Startup overview with system stats, agent summary, and quick commands |
| `ChatScreen` | `chat.py` | Main conversation interface with sidebar and command input |
| `TaskScreen` | `tasks.py` | Task monitor showing agent statuses and active task grid |

## Usage Examples

### Launch with Cinematic Loader

```python
from rich.console import Console
from terminal.loader import CinematicLoader, create_default_phases, PhaseTracker
from terminal.app import NEXUSTerminalApp
from core.config import Config
from core.database import Database
from manager.manager import AIManager

console = Console()
loader = CinematicLoader(console=console)
phases = create_default_phases(loader)

def initialize():
    with PhaseTracker(phases["core"], loader) as tracker:
        with tracker.step("Configuration"):
            config = Config()
        with tracker.step("Database"):
            db = Database()

    with PhaseTracker(phases["ai"], loader) as tracker:
        with tracker.step("AI Manager"):
            manager = AIManager()

    return manager

manager = loader.run(init_fn=initialize)
app = NEXUSTerminalApp(manager)
app.run()
```

### Register and Execute Slash Commands

```python
from terminal.commands import CommandRegistry

reg = CommandRegistry()

def help_handler(args, context):
    manager = context.get("manager")
    return {"success": True, "response": manager._get_help_text()}

def agents_handler(args, context):
    manager = context.get("manager")
    status = manager.get_agent_status()
    lines = [f"  {name}: {info['status']}" for name, info in status.items()]
    return {"success": True, "response": "Agents:\n" + "\n".join(lines)}

reg.register("help", "Show available commands", help_handler,
             aliases=["h", "?"], category="system")
reg.register("agents", "List all agents", agents_handler,
             aliases=["a"], category="system")

# Execute commands
reg.execute("/help", context={"manager": manager})
reg.execute("/agents", context={"manager": manager})

# Autocomplete
reg.get_autocomplete("/he")  # ["/help"]
```

### Stream LLM Response with Typing Animation

```python
from terminal.streaming import StreamingResponse, TypingAnimation

streamer = StreamingResponse(typing_speed=0.01)
animation = TypingAnimation()

# Update UI on each token
def on_token(token):
    print(token, end="", flush=True)

streamer.on_chunk(on_token)

# Stream from LLM
messages = [{"role": "user", "content": "Explain quantum computing"}]
full_response = streamer.stream_sync(llm.stream(messages))
```

## Dependencies

| Dependency | Purpose | Required |
|------------|---------|----------|
| `textual` | TUI framework | Yes |
| `rich` | Rich text rendering, console output | Yes |
| `core.base_agent` | AgentStatus enum for widgets | Yes |
| `core.logger` | Structured logging | Yes |
| `asyncio` | Async streaming support | Yes (stdlib) |
| `dataclasses` | Data model definitions | Yes (stdlib) |

## Configuration

Terminal behavior is controlled via `config/settings.json`:

```json
{
  "terminal": {
    "theme": "nexus",
    "typing_speed": 0.01,
    "show_header": true,
    "show_sidebar": true,
    "show_status_bar": true,
    "auto_complete": true
  }
}
```

| Key | Default | Description |
|-----|---------|-------------|
| `terminal.theme` | `"nexus"` | Textual theme name |
| `terminal.typing_speed` | `0.01` | Seconds between token renders |
| `terminal.show_header` | `true` | Show top header bar |
| `terminal.show_sidebar` | `true` | Show left navigation sidebar |
| `terminal.show_status_bar` | `true` | Show bottom status bar |
| `terminal.auto_complete` | `true` | Enable Tab autocomplete |

## Extending

### Adding a New Screen

```python
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static

class MyCustomScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Static("Custom screen content")

# Register in app
app.install_screen(MyCustomScreen(), name="custom")
app.push_screen("custom")
```

### Adding a New Widget

```python
from textual.widget import Widget
from textual.widgets import Static
from rich.panel import Panel
from rich.text import Text

class MyWidget(Static):
    value = reactive(0)

    def render(self) -> Panel:
        return Panel(
            Text(f"Value: {self.value}", style="bold cyan"),
            title="My Widget",
            border_style="cyan",
        )
```

### Adding a New Command

```python
reg.register(
    "mycommand",
    "Description of my command",
    my_handler_function,
    aliases=["mc"],
    category="custom",
    requires_args=True,
    arg_description="<argument>",
    autocomplete=["option1", "option2"],
)
```
