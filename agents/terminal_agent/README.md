# Terminal Agent

> **NEXUS Agent** — Safe terminal command execution with validation, session management, output streaming, and script running.

## Purpose

The Terminal Agent provides a secure interface for executing shell commands, running scripts, and managing terminal sessions within NEXUS. It includes a comprehensive command validator with safety levels, session isolation, real-time output streaming, and full execution history. All commands are validated against blocklists and danger patterns before execution.

## Architecture

```
terminal_agent/
├── __init__.py          # Package initialization
├── agent.py             # Main orchestrator (TerminalAgent)
├── models.py            # Data models (CommandRecord, TerminalSession, Status enums)
├── services.py          # Business logic services
│   ├── ExecutionEngine     # Command execution with subprocess
│   ├── SessionManager      # Multi-session lifecycle management
│   ├── OutputStreamer      # Real-time output streaming
│   └── ScriptRunner        # Script file and Python code execution
├── validator.py         # Command safety validation
│   └── CommandValidator    # Blocklists, danger patterns, safety levels
└── storage.py           # SQLite persistence for sessions and command history
```

The agent uses a layered security model: commands pass through `CommandValidator` before reaching `ExecutionEngine`. Sessions isolate working directories and environment variables. All executions are logged to persistent storage.

## Capabilities

| Capability | Description |
|---|---|
| `run_command` | Execute a terminal command with safety validation |
| `run_script` | Execute a script file (.py, .bat, .ps1, .sh, etc.) |
| `run_python` | Execute Python code directly via subprocess |
| `stream_command` | Run a command with real-time output streaming |
| `new_session` / `switch_session` / `close_session` | Manage isolated terminal sessions |
| `list_sessions` | Show all sessions with status indicators |
| `change_directory` | Set working directory for current session |
| `set_environment` | Set environment variables per session |
| `kill_process` / `kill_all` | Terminate running processes |
| `command_history` | View recent command execution history |
| `search_history` | Search command history by keyword |
| `failed_commands` / `blocked_commands` | View failed or blocked command logs |
| `check_command_safety` | Validate a command without executing |
| `clear_history` | Purge command history |
| `set_timeout` | Configure default command timeout |
| `strict_mode` | Toggle strict safety mode |
| `force_run` | Execute a command bypassing safety blocks |
| `pwd` | Show current working directory |

## Internal Structure

### Data Models (`models.py`)

- **`CommandRecord`** — Full execution record with command, status, output, error, exit code, duration, safety info, and timestamps
- **`TerminalSession`** — Session with name, working directory, status, environment variables, and command history
- **`CommandStatus`** enum: pending, running, completed, failed, blocked, timeout, killed
- **`SessionStatus`** enum: active, idle, closed, error

### Command Validator (`validator.py`)

- **`SafetyLevel`** enum: safe, caution, dangerous, blocked
- **Platform-specific blocklists** — Windows (`format`, `diskpart`, `rd /s /q`, encoded PowerShell, etc.) and Unix (`rm -rf /`, `mkfs`, `dd if=`, etc.)
- **Caution commands** — Package installs, git operations, Docker prune, file deletions, service management
- **Dangerous regex patterns** — 25+ patterns matching fork bombs, disk wipes, privilege escalation, remote code execution
- **Chained command analysis** — Splits `&&`, `||`, `;` chains and validates each part independently
- **Path traversal detection** — Blocks `../`, `..\\`, and URL-encoded variants
- **Allowlist/blocklist management** — Runtime modification of safe and blocked commands

### Services (`services.py`)

- **`ExecutionEngine`** — Subprocess-based execution with timeout, output truncation (50KB), streaming callbacks, process tracking, and thread-safe process management
- **`SessionManager`** — Session CRUD, working directory management, environment variable isolation, persistence across restarts
- **`OutputStreamer`** — Thread-safe queue-based streaming with generator interface for real-time output consumption
- **`ScriptRunner`** — Script execution with extension validation (.py, .bat, .cmd, .ps1, .sh, .js, .ts, .rb, .pl, .php, .exe, .com), Python `-c` inline execution

### Storage

- SQLite persistence for command records and session state
- Indexed queries for history search, failed commands, and blocked commands

## Usage Examples

### Natural Language Commands

```
run dir
run script C:\scripts\deploy.py with args --prod --verbose
run python print("Hello from NEXUS")
stream ping -t google.com
new session name: Build dir: C:\projects
cd C:\projects\myapp
set env NODE_ENV=production
command history 10
check command safety: rm -rf /tmp/cache
force run net stop wuauserv
strict mode on
set timeout 60
```

### Programmatic API

```python
from agents.terminal_agent.agent import TerminalAgent

agent = TerminalAgent()

# Run a command
result = agent.run_command("dir", timeout=10)

# Check safety without executing
safety = agent.check_safety("git push --force")

# Run a script
result = agent.run_script("C:\\scripts\\build.py", args=["--release"])

# Execute Python code
result = agent.run_python("import sys; print(sys.version)")

# Stream a long-running command
result = agent.stream_command("ping -n 4 google.com")
```

## Configuration

| Config Key | Default | Description |
|---|---|---|
| `terminal_agent.strict_mode` | `true` | Unknown commands require caution in strict mode |
| `terminal_agent.default_timeout` | `30` | Default command timeout in seconds |
| `terminal_agent.max_output_size` | `50000` | Maximum output size in bytes before truncation |
| `terminal_agent.script_timeout` | `120` | Default timeout for script execution |

## Security Model

1. **Validation first** — Every command passes through `CommandValidator` before execution
2. **Safety levels** — Commands classified as safe, caution, dangerous, or blocked
3. **Strict mode** — Unknown commands are flagged as caution when enabled
4. **Force override** — `force_run` bypasses blocks but still logs the action
5. **Process tracking** — All running processes tracked by record ID for kill capability
6. **Output truncation** — Large outputs truncated to prevent memory issues
7. **Session isolation** — Each session has its own working directory and environment

## Dependencies

- `subprocess` (built-in) — Command execution
- `psutil` — Process management
- `platform` (built-in) — OS detection for platform-specific rules
- SQLite (built-in) — Session and history persistence
