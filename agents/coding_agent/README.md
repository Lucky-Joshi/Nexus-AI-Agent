# Coding Agent

> Code generation, analysis, debugging, git operations, and repository inspection for the NEXUS platform.

## Purpose

The Coding Agent provides AI-assisted software development capabilities within the NEXUS multi-agent platform. It generates code in multiple languages, explains and debugs code, executes git commands, analyzes repositories, and runs shell commands. It uses an LLM provider when available, with rule-based fallbacks for offline operation.

## Architecture

```
CodingAgent
├── LLMProvider (optional) — Code generation, explanation, and review
├── Code Generation        — Language detection, stub generation for Python/JS/HTML
├── Code Analysis          — Pattern-based issue detection (security, style, structure)
├── Git Operations         — Subprocess-based git command execution
└── Command Execution      — Safe shell command execution with timeout
```

### Command Routing

```
"generate code for a REST API"     → LLM/stub code generation
"explain this code: def foo()..."  → Code explanation
"debug code: eval(input())"        → Issue analysis
"git status"                       → Git command execution
"analyze repository /path/to/repo" → Repository statistics
"run python main.py"               → Shell command execution
```

## Capabilities

| Category | Operations |
|---|---|
| **Code Generation** | LLM-powered or stub generation for Python, JavaScript, TypeScript, HTML, CSS |
| **Code Explanation** | Structural analysis (imports, functions, classes, loops, conditionals) or LLM explanation |
| **Code Debugging** | Security issue detection (`eval`, `exec`), style checks, bare except detection, line length |
| **Git Operations** | Any git command executed in workspace directory |
| **Repository Analysis** | File type distribution, total file count, total size, skip noisy directories |
| **File Operations** | Read file contents with line numbers, prepare files for editing |
| **Command Execution** | Run shell commands with 30s timeout, stdout/stderr capture |

## Internal Structure

```
coding_agent/
├── __init__.py      — Package exports
└── agent.py         — CodingAgent class (537 lines):
    ├── Language detection    — From description keywords or code patterns
    ├── Code generation       — LLM with code block extraction, language-specific stubs
    ├── Code explanation      — Structural analysis or LLM-powered
    ├── Code review           — Pattern-based security/style/structure checks
    ├── Git integration       — Subprocess git commands with error handling
    ├── Repository analysis   — os.walk with skip-list, file type counting
    └── Command execution     — subprocess.run with timeout and output capture
```

### Key Design Patterns

- **LLM Fallback Chain**: LLM → language-specific stub → generic stub
- **Language Detection**: Regex-based detection from code patterns (`def ` → Python, `function ` → JS)
- **Code Block Extraction**: Parses markdown code blocks from LLM responses
- **Safe Execution**: 30-second timeout on all subprocess calls, output truncation

## Usage Examples

### Natural Language Commands

```python
from agents.coding_agent.agent import CodingAgent

agent = CodingAgent()

# Code generation
agent.execute("generate code for a function that calculates fibonacci numbers")
agent.execute("write code for a Python class that manages a todo list")
agent.execute("create code for an HTML landing page")

# Code explanation
agent.execute("explain def quicksort(arr): return arr if len(arr) <= 1 else ...")

# Debugging
agent.execute("debug code: eval(input('Enter: '))")
agent.execute("fix this: except: pass")

# Git operations
agent.execute("git status")
agent.execute("git log --oneline -10")
agent.execute("git add .")
agent.execute("git commit -m 'fix: update README'")

# Repository analysis
agent.execute("analyze repository C:\\Users\\lucky\\projects\\myapp")

# Command execution
agent.execute("run python -m pytest tests/")
agent.execute("execute npm install")
```

### Programmatic API

```python
# Direct method calls
code = agent.generate_code("sort a list of dictionaries by key", "python")
explanation = agent.explain_code("def factorial(n): return 1 if n <= 1 else n * factorial(n-1)")
agent.edit_file("output.py", "print('hello')")
content = agent.read_file("src/main.py")
result = agent.git_command("diff --stat")
```

## Configuration

| Setting | Default | Description |
|---|---|---|
| `agents.coding_agent.workspace_path` | `~` | Default directory for git and command execution |
| `agents.coding_agent.default_language` | `python` | Fallback language when not detected |
| `llm.use_in_agents` | `true` | Enable LLM-powered code generation and analysis |

### Dependencies

None beyond Python standard library.

### Optional Dependencies

```
LLMProvider     — For AI-powered code generation, explanation, and review
git             — For git operations (must be in PATH)
```

## Capabilities Reference

```
generate_code, explain_code, debug_code, edit_file, git_command,
analyze_repository, run_command, read_file, list_files
```
