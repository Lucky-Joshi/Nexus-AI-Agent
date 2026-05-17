# Automation Agent

> Desktop automation, workflow execution, and productivity modes for the NEXUS platform.

## Purpose

The Automation Agent provides desktop-level automation capabilities within the NEXUS multi-agent platform. It controls mouse and keyboard input, captures screenshots, executes multi-step workflows, and offers pre-built productivity modes (coding, study, work, meeting prep, presentation). Built with a comprehensive safety system including emergency stop, step limits, and safety delays.

## Architecture

```
AutomationAgent (orchestrator)
├── ActionExecutor     — Executes individual actions (keyboard, mouse, apps, screenshots)
├── WorkflowEngine     — Manages workflow definition, execution, persistence
├── SafetySystem       — Emergency stop, step limits, pre/post execution guards
└── Workflow Templates — 7 built-in productivity workflows
```

### Command Routing

```
"screenshot"                      → Action.screenshot()
"run workflow coding_mode"        → WorkflowEngine.execute("coding_mode")
"click right"                     → Action.click(button="right")
"type hello world"                → Action.type_text("hello world")
"press ctrl+c"                    → Action.hotkey("ctrl", "c")
"move mouse to 100, 200"          → Action.move_mouse(100, 200)
"open vscode and terminal"        → Launch sequence workflow
"stop"                            → Emergency stop
```

## Capabilities

| Category | Operations |
|---|---|
| **Mouse Control** | Click (left/right/double), move to coordinates |
| **Keyboard Control** | Type text with configurable interval, press keys, hotkey combinations |
| **Screenshots** | Full-screen capture with auto-save to screenshots directory |
| **Workflow Execution** | Run registered workflows with step-by-step safety checks |
| **Workflow Management** | Save custom workflows, list available, emergency stop |
| **App Sequences** | Launch multiple applications in sequence with delays |
| **Productivity Modes** | Coding, Study, Work, Meeting Prep, Screen Capture, Cleanup, Presentation |

## Internal Structure

```
automation_agent/
├── __init__.py          — Package exports
├── agent.py             — AutomationAgent class: command parsing, 10 handlers (337 lines)
├── actions.py           — Action dataclass + ActionExecutor (203 lines):
│   ├── Action               — 10 action types: open_app, type_text, press_key, hotkey,
│   │                          click, move_mouse, screenshot, wait, run_command
│   └── ActionExecutor       — Dispatches to pyautogui/subprocess handlers
├── workflow_engine.py   — WorkflowEngine + Workflow dataclass (204 lines):
│   ├── Workflow             — Named step sequences with tags and mode
│   └── WorkflowEngine       — Registration, execution, persistence (JSON)
├── safety.py            — SafetySystem + EmergencyStop (108 lines):
│   ├── EmergencyStop        — Thread-safe stop with callbacks
│   └── SafetySystem         — Step limits, safety delays, pre/post guards
└── templates.py         — 7 built-in workflow templates (141 lines)
```

### Key Design Patterns

- **Action Dataclass**: Serializable actions with `to_dict()`/`from_dict()` for persistence
- **Safety-First**: Emergency stop with thread-safe locking, configurable step limits (default 50), safety delays between actions
- **Workflow Persistence**: Custom workflows saved to `data/workflows.json`
- **Template System**: Pre-built workflows for common productivity scenarios

### Built-in Workflows

| Workflow | Steps | Description |
|---|---|---|
| `coding_mode` | 6 | Opens VS Code + Terminal, shows desktop, takes screenshot |
| `study_mode` | 8 | Opens browser + notepad, splits windows side-by-side |
| `work_mode` | 4 | Opens browser + notepad for work tasks |
| `meeting_prep` | 4 | Opens browser + notepad for meeting preparation |
| `screen_capture` | 5 | Takes 3 screenshots at 3-second intervals |
| `cleanup` | 2 | Minimizes all windows (Win+D) |
| `presentation_mode` | 4 | Opens browser in fullscreen (F11) |

## Usage Examples

### Natural Language Commands

```python
from agents.automation_agent.agent import AutomationAgent

agent = AutomationAgent()

# Screenshots
agent.execute("screenshot")

# Mouse control
agent.execute("click")
agent.execute("right click")
agent.execute("double click")
agent.execute("move mouse to 500, 300")

# Keyboard control
agent.execute("type Hello World")
agent.execute("press enter")
agent.execute("press ctrl+c")
agent.execute("press winleft + d")

# Workflow execution
agent.execute("run workflow coding_mode")
agent.execute("start mode study_mode")
agent.execute("execute preset cleanup")

# Custom workflow
agent.execute("save workflow my_routine: open vscode, wait 2, type hello")

# List workflows
agent.execute("list workflows")

# App sequences
agent.execute("open vscode and terminal and browser")

# Emergency stop
agent.execute("stop")
agent.execute("emergency stop")
```

### Programmatic API

```python
from agents.automation_agent.actions import Action
from agents.automation_agent.workflow_engine import Workflow

# Create custom workflow
workflow = Workflow(
    name="morning_routine",
    description="Open work apps",
    steps=[
        Action.open_app("browser", delay=2.0),
        Action.wait(seconds=2),
        Action.open_app("vscode", delay=1.5),
        Action.screenshot(),
    ],
)
agent._workflow_engine.register_workflow(workflow)
agent._workflow_engine.execute("morning_routine")

# Direct action execution
action = Action.hotkey("winleft", "d")
result = agent._workflow_engine.executor.execute(action)
```

## Configuration

| Setting | Default | Description |
|---|---|---|
| `agents.automation_agent.safety_delay` | `0.5` | Seconds between workflow steps |
| `agents.automation_agent.confirm_destructive` | `true` | Require confirmation for destructive actions |

### Dependencies

```
pyautogui       — Mouse and keyboard automation
Pillow          — Screenshot capture (pyautogui dependency)
```

### Optional Dependencies

```
pygetwindow     — Enhanced window tracking (fallback to ctypes available)
```

## Capabilities Reference

```
screenshot, execute_workflow, save_workflow, list_workflows, stop_workflow,
click, type_text, press_key, hotkey, move_mouse, launch_sequence, run_command
```
