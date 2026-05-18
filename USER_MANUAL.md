# NEXUS USER MANUAL

> **The Terminal-Native AI Operating Environment**  
> Version 1.0 — Official Handbook

---

## TABLE OF CONTENTS

### PART I — FOUNDATIONS
1. [Preface](#1-preface)
2. [Vision & Philosophy](#2-vision--philosophy)
3. [What Is NEXUS](#3-what-is-nexus)
4. [Core Principles](#4-core-principles)
5. [System Overview](#5-system-overview)
6. [Architecture at a Glance](#6-architecture-at-a-glance)

### PART II — GETTING STARTED
7. [System Requirements](#7-system-requirements)
8. [Installation](#8-installation)
9. [Configuration](#9-configuration)
10. [First Launch](#10-first-launch)
11. [The Cinematic Startup Experience](#11-the-cinematic-startup-experience)
12. [Command-Line Interface](#12-command-line-interface)

### PART III — THE TERMINAL ENVIRONMENT
13. [Terminal UI Architecture](#13-terminal-ui-architecture)
14. [Dashboard Screen](#14-dashboard-screen)
15. [Chat Interface](#15-chat-interface)
16. [Task Monitor](#16-task-monitor)
17. [Theme System](#17-theme-system)
18. [Streaming Responses](#18-streaming-responses)
19. [Keyboard Navigation](#19-keyboard-navigation)
20. [Custom Widgets](#20-custom-widgets)

### PART IV — CORE SYSTEM
21. [Base Agent Architecture](#21-base-agent-architecture)
22. [AI Manager](#22-ai-manager)
23. [Intent Router](#23-intent-router)
24. [Task Dispatcher](#24-task-dispatcher)
25. [LLM Provider](#25-llm-provider)
26. [Configuration System](#26-configuration-system)
27. [Logging System](#27-logging-system)
28. [Database Layer](#28-database-layer)

### PART V — COMMUNICATION & COORDINATION
29. [Event Bus](#29-event-bus)
30. [Message Broker](#30-message-broker)
31. [Shared State Manager](#31-shared-state-manager)
32. [Event Logger](#32-event-logger)
33. [Inter-Agent Communication](#33-inter-agent-communication)

### PART VI — MULTI-AGENT ORCHESTRATION
34. [Workflow Engine](#34-workflow-engine)
35. [Workflow Chains](#35-workflow-chains)
36. [Planning Engine](#36-planning-engine)
37. [Goal Decomposition](#37-goal-decomposition)
38. [Dependency Graph](#38-dependency-graph)
39. [Task Executor](#39-task-executor)
40. [Async Execution Model](#40-async-execution-model)

### PART VII — INTELLIGENCE LAYER
41. [Context Awareness](#41-context-awareness)
42. [Activity Classification](#42-activity-classification)
43. [Focus Detection](#43-focus-detection)
44. [Workflow Detection](#44-workflow-detection)
45. [Adaptive Triggers](#45-adaptive-triggers)
46. [Learning Engine](#46-learning-engine)
47. [Behavior Tracking](#47-behavior-tracking)
48. [Pattern Analysis](#48-pattern-analysis)
49. [Recommendation Engine](#49-recommendation-engine)
50. [Predictive Actions](#50-predictive-actions)

### PART VIII — MEMORY & KNOWLEDGE
51. [Memory Agent](#51-memory-agent)
52. [Knowledge Agent](#52-knowledge-agent)
53. [Semantic Search](#53-semantic-search)
54. [Vector Storage](#54-vector-storage)
55. [Conversation History](#55-conversation-history)

### PART IX — PRODUCTIVITY TOOLS
56. [File Agent](#56-file-agent)
57. [Web Agent](#57-web-agent)
58. [Coding Agent](#58-coding-agent)
59. [Automation Agent](#59-automation-agent)
60. [Scheduler Agent](#60-scheduler-agent)
61. [Notification Agent](#61-notification-agent)
62. [Terminal Agent](#62-terminal-agent)
63. [Vision Agent](#63-vision-agent)

### PART X — SYSTEM MANAGEMENT
64. [Security Agent](#64-security-agent)
65. [Analytics Agent](#65-analytics-agent)
66. [Personality Agent](#66-personality-agent)
67. [Communication Bus Agent](#67-communication-bus-agent)
68. [Marketplace Agent](#68-marketplace-agent)
69. [Plugin Agent](#69-plugin-agent)
70. [Plugin Development](#70-plugin-development)
71. [Plugin Sandbox](#71-plugin-sandbox)

### PART XI — ADVANCED TOPICS
72. [Performance Optimization](#72-performance-optimization)
73. [Dependency Management](#73-dependency-management)
74. [Debugging & Troubleshooting](#74-debugging--troubleshooting)
75. [Error Handling](#75-error-handling)
76. [Background Tasks](#76-background-tasks)
77. [Session Management](#77-session-management)
78. [Advanced Configuration](#78-advanced-configuration)
79. [Best Practices](#79-best-practices)
80. [Architecture Decisions](#80-architecture-decisions)
81. [Roadmap & Future](#81-roadmap--future)

### APPENDICES
A. [Complete Command Reference](#appendix-a-complete-command-reference)
B. [Database Schema Reference](#appendix-b-database-schema-reference)
C. [API Reference](#appendix-c-api-reference)
D. [Agent Catalog](#appendix-d-agent-catalog)
E. [Glossary](#appendix-e-glossary)
F. [Index](#appendix-f-index)

---

## 1. PREFACE

Welcome to NEXUS — a terminal-native AI operating environment designed to transform how you interact with artificial intelligence. This manual is the definitive reference for understanding, configuring, and mastering every aspect of the system.

NEXUS is not a chatbot. It is not a single-purpose tool. It is an **operating environment** — a coordinated ecosystem of 21 specialized AI agents, a cinematic terminal interface, a multi-agent orchestration engine, and a learning system that adapts to your behavior over time.

### Who This Manual Is For

- **End users** who want to harness AI-powered workflows in their terminal
- **Developers** who want to extend NEXUS with custom agents or plugins
- **System administrators** who need to configure, deploy, and monitor NEXUS
- **Researchers** interested in multi-agent AI orchestration patterns

### How to Use This Manual

This manual is structured in layers. **Parts I–III** cover the fundamentals — what NEXUS is, how to install it, and how to navigate the terminal interface. **Parts IV–X** dive into the architecture, each agent, and the intelligence layer. **Part XI** covers advanced topics, debugging, and best practices. The **Appendices** provide quick-reference material.

You can read linearly from start to finish, or use the table of contents to jump to specific topics. Cross-references throughout point you to related sections.

### Conventions

- `monospace text` — commands, code, configuration keys
- **Bold** — important terms, UI elements
- *Italic* — emphasis, file paths
- `> ` — terminal prompts
- `[Key]` — keyboard shortcuts (e.g., `[Ctrl+Q]`)

---

## 2. VISION & PHILOSOPHY

### The Vision

NEXUS envisions a future where AI is not a destination you visit (a website, an app) but an **environment you inhabit**. Your terminal becomes the control surface for an intelligent system that understands your context, learns your patterns, anticipates your needs, and orchestrates multiple specialized agents to accomplish complex goals.

### Design Philosophy

**Terminal-Native First**  
The terminal is the most efficient interface for power users. NEXUS embraces this with a rich Textual-based UI that provides panels, streaming, keyboard navigation, and cinematic polish — all without leaving your terminal.

**Multi-Agent Orchestration**  
No single model can do everything well. NEXUS decomposes problems across 21 specialized agents, each optimized for a specific domain. A routing engine determines which agent (or chain of agents) should handle each request.

**Context-Aware Intelligence**  
NEXUS monitors your activity, detects your focus level, identifies workflows, and adapts its behavior accordingly. It learns from your patterns and generates personalized recommendations.

**Progressive Disclosure**  
The system hides complexity by default. Normal startup shows a cinematic loader with no raw logs. Advanced users can enable `--verbose` or `--debug` modes to see everything. The dashboard provides a high-level overview; drill down into specific screens for detail.

**Extensibility**  
The plugin system, marketplace, and agent architecture are designed for growth. Anyone can write a plugin, publish an agent, or extend the core.

**Security by Design**  
Every plugin runs in a sandboxed environment. The security agent monitors for threats. The marketplace verifies agents before installation. The communication bus enforces message validation.

---

## 3. WHAT IS NEXUS

NEXUS is a **Python-based, terminal-native AI operating environment** that provides:

- **21 Specialized AI Agents** — File management, web research, coding, automation, memory, vision, notifications, scheduling, knowledge, terminal control, personality, workflows, security, analytics, context awareness, learning, communication bus, planning, marketplace, and plugin management
- **Cinematic Terminal UI** — Animated startup loader, multi-panel dashboard, streaming chat responses, task monitoring, keyboard navigation, and theme support
- **Multi-Agent Orchestration** — 3-stage intent routing (Regex → Fuzzy → LLM), workflow chains, goal decomposition, dependency-aware task execution, and replanning
- **Learning System** — Behavior tracking, pattern detection (frequency, sequence, time-based, contextual), recommendation generation, and predictive actions
- **Context Awareness** — Active window monitoring, activity classification, focus level detection, workflow pattern recognition, and adaptive triggers
- **Communication Infrastructure** — Thread-safe event bus, priority message broker, shared state manager, and persistent event logging
- **Plugin Architecture** — Dynamic plugin loading, sandboxed execution, command/hook registration, and lifecycle management
- **Marketplace** — Browse, install, update, and verify community agents with security scanning

### What NEXUS Is NOT

- **Not a chatbot** — While it has a chat interface, NEXUS is an orchestration engine that routes requests to specialized agents
- **Not a desktop application** — It runs entirely in the terminal using Textual
- **Not a single AI model** — It coordinates multiple agents, each with specific capabilities
- **Not a replacement for your tools** — It integrates with and enhances your existing workflow

---

## 4. CORE PRINCIPLES

1. **Modularity** — Every component is a self-contained module. Agents, plugins, screens, and services can be developed, tested, and deployed independently.

2. **Async-First** — The system uses asynchronous execution wherever possible. Tasks run in the background, responses stream in real-time, and the UI never blocks.

3. **Thread Safety** — The event bus, message broker, shared state manager, and task dispatcher all use proper locking and synchronization.

4. **Persistence** — Conversations, memory, tasks, context snapshots, learning data, and plugin state are all persisted to SQLite databases.

5. **Graceful Degradation** — If an agent fails, the system retries, falls back to alternative agents, or replans the workflow. If the LLM provider is unavailable, regex and fuzzy routing still work.

6. **Observability** — Every action is logged. The analytics agent tracks system metrics. The event logger provides real-time streaming of communication events.

7. **User Control** — You decide what NEXUS monitors, what it learns, what it automates. Adaptive triggers can be toggled. Recommendations can be accepted or dismissed. Plugins can be enabled or disabled.

---

## 5. SYSTEM OVERVIEW

### Directory Structure

```
NEXUS/
├── main.py                    # Entry point with CLI parsing and loader
├── README.md                  # Root documentation index
├── requirements.txt           # Python dependencies
├── LICENSE                    # MIT License
├── .env                       # Environment variables (API keys)
│
├── core/                      # Core system modules
│   ├── __init__.py
│   ├── base_agent.py          # Abstract BaseAgent class
│   ├── config.py              # Singleton configuration loader
│   ├── database.py            # SQLite database wrapper
│   ├── llm_provider.py        # Ollama/OpenAI abstraction
│   └── logger.py              # Dynamic logging system
│
├── manager/                   # Orchestration layer
│   ├── __init__.py
│   ├── manager.py             # AIManager - central orchestrator
│   ├── router.py              # 3-stage intent router
│   └── dispatcher.py          # Async task dispatcher
│
├── terminal/                  # Terminal UI
│   ├── __init__.py
│   ├── app.py                 # Textual application
│   ├── loader.py              # Cinematic startup loader
│   ├── commands.py            # Command routing
│   ├── streaming.py           # Streaming response handler
│   ├── theme.py               # Theme definitions
│   ├── widgets.py             # Custom widgets
│   └── screens/
│       ├── __init__.py
│       ├── dashboard.py       # Startup dashboard
│       ├── chat.py            # Chat interface
│       └── tasks.py           # Task monitor
│
├── agents/                    # 21 specialized AI agents
│   ├── file_agent/
│   ├── web_agent/
│   ├── coding_agent/
│   ├── automation_agent/
│   ├── memory_agent/
│   ├── vision_agent/
│   ├── notification_agent/
│   ├── scheduler_agent/
│   ├── knowledge_agent/
│   ├── terminal_agent/
│   ├── personality_agent/
│   ├── workflow_agent/
│   ├── security_agent/
│   ├── workflow_chain_agent/
│   ├── analytics_agent/
│   ├── context_awareness_agent/
│   ├── learning_agent/
│   ├── communication_bus_agent/
│   ├── planner_agent/
│   ├── marketplace_agent/
│   └── plugin_agent/
│
├── ui/                        # PyQt6 UI (alternative interface)
│   ├── main_window.py
│   ├── chat_widget.py
│   ├── sidebar.py
│   ├── task_panel.py
│   └── themes/dark_theme.py
│
├── config/
│   └── settings.json          # Main configuration file
│
├── data/                      # SQLite databases
│   ├── nexus.db               # Main database
│   ├── context.db             # Context awareness data
│   └── learning.db            # Learning agent data
│
├── plugins/                   # Plugin directory
│   ├── quick_notes/           # Sample directory plugin
│   └── system_info_plugin.py  # Sample single-file plugin
│
├── installed_agents/          # Installed marketplace agents
│   └── weather_agent/
│
└── docs/                      # Centralized documentation (30 files)
    ├── architecture.md
    ├── core.md
    ├── manager.md
    ├── terminal.md
    ├── api_reference.md
    ├── contributing.md
    ├── development_guide.md
    ├── installation.md
    ├── agents.md
    └── agents/                # 21 individual agent docs
```

### Key Directories

| Directory | Purpose |
|-----------|---------|
| `core/` | Abstract base classes, configuration, database, LLM provider, logging |
| `manager/` | AI orchestration, intent routing, task dispatching |
| `terminal/` | Textual UI application, screens, widgets, themes, streaming |
| `agents/` | 21 specialized agent packages, each with agent.py, models.py, services.py, storage.py |
| `ui/` | Alternative PyQt6 desktop interface |
| `config/` | JSON configuration files |
| `data/` | SQLite database files |
| `plugins/` | User-installed plugins |
| `installed_agents/` | Agents installed from the marketplace |
| `docs/` | All documentation (30 markdown files) |

---

## 6. ARCHITECTURE AT A GLANCE

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    TERMINAL UI (Textual)                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────────┐ │
│  │Dashboard │  │   Chat   │  │   Tasks  │  │  Streaming   │ │
│  │ Screen   │  │  Screen  │  │  Screen  │  │  Responses   │ │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └──────┬──────┘ │
│       │              │              │               │        │
│  ┌────┴──────────────┴──────────────┴───────────────┴────┐  │
│  │              Cinematic Startup Loader                  │  │
│  └────────────────────────┬──────────────────────────────┘  │
└───────────────────────────┼─────────────────────────────────┘
                            │
┌───────────────────────────┼─────────────────────────────────┐
│                    AI MANAGER                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │    Router    │  │  Dispatcher  │  │   Task Queue     │  │
│  │ (3-stage)    │→ │  (Async)     │→ │   (Priority)     │  │
│  └──────┬───────┘  └──────────────┘  └────────┬─────────┘  │
│         │                                      │            │
│  ┌──────┴──────────────────────────────────────┴─────────┐  │
│  │                  AGENT REGISTRY                        │  │
│  │  21 Specialized Agents · Plugin System · Marketplace   │  │
│  └────────────────────────┬──────────────────────────────┘  │
└───────────────────────────┼─────────────────────────────────┘
                            │
┌───────────────────────────┼─────────────────────────────────┐
│              COMMUNICATION LAYER                             │
│  ┌──────────┐  ┌──────────────┐  ┌───────────┐  ┌────────┐ │
│  │Event Bus │  │Message Broker│  │Shared State│  │Events  │ │
│  │(Pub/Sub) │  │(Priority Q)  │  │(Key-Value) │  │Logger  │ │
│  └──────────┘  └──────────────┘  └───────────┘  └────────┘ │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────┼─────────────────────────────────┐
│              INTELLIGENCE LAYER                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │   Context    │  │   Learning   │  │    Planning      │  │
│  │  Awareness   │  │   Engine     │  │    Engine        │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────┼─────────────────────────────────┐
│              PERSISTENCE LAYER                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐  │
│  │ nexus.db │  │context.db│  │learning.db│  │  Plugins   │  │
│  │(SQLite)  │  │(SQLite)  │  │(SQLite)  │  │  (JSON)    │  │
│  └──────────┘  └──────────┘  └──────────┘  └────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Request Flow

1. **User Input** → Terminal UI captures command or natural language
2. **Cinematic Loader** → (Startup only) Animated initialization sequence
3. **Router** → 3-stage intent detection: Regex → Fuzzy → LLM
4. **Dispatcher** → Queues task, assigns to appropriate agent(s)
5. **Agent Execution** → Agent processes request, may call other agents
6. **Communication Bus** → Agents communicate via events, messages, shared state
7. **Streaming** → Response streams back to terminal in real-time
8. **Persistence** → Conversation, task, and context data saved to databases
9. **Learning** → Behavior recorded, patterns analyzed, recommendations generated

### Data Flow

```
User Input → Router → Agent → LLM Provider → Response → UI
                    ↓
              Event Bus → Other Agents
                    ↓
              Database → Memory/Context/Learning
                    ↓
              Analytics → Metrics/Reports
```

---

## 7. SYSTEM REQUIREMENTS

### Minimum Requirements

- **Python**: 3.10 or higher
- **RAM**: 4 GB
- **Disk**: 500 MB (excluding LLM models)
- **OS**: Windows, macOS, or Linux
- **Terminal**: Modern terminal emulator with Unicode support

### Recommended Requirements

- **Python**: 3.11 or higher
- **RAM**: 8 GB or more
- **Disk**: 2 GB+ (for local LLM models)
- **Terminal**: Windows Terminal, iTerm2, or GNOME Terminal

### LLM Provider Options

- **Ollama** (local, free) — Recommended for privacy and offline use
- **OpenAI** (cloud, paid) — Recommended for highest quality responses
- **Custom** — Any OpenAI-compatible API endpoint

### Dependencies

All dependencies are listed in `requirements.txt`. Key packages include:

| Package | Purpose |
|---------|---------|
| `textual` | Terminal UI framework |
| `rich` | Rich text and formatting |
| `openai` | OpenAI API client |
| `pydantic` | Data validation |
| `psutil` | System monitoring |
| `watchdog` | File system monitoring |
| `playwright` | Web automation |
| `schedule` | Task scheduling |
| `colorama` | Cross-platform colors |
| `pygetwindow` | Active window detection (Windows) |
| `pyautogui` | GUI automation |

Install all dependencies with:
```bash
pip install -r requirements.txt
```

---

## 8. INSTALLATION

### Step 1: Clone or Download

```bash
cd C:\Users\lucky\OneDrive\Desktop\ai-agents\NEXUS
```

### Step 2: Create Virtual Environment (Recommended)

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment

Create or edit `.env` in the root directory:

```env
# OpenAI Configuration (optional)
OPENAI_API_KEY=your-api-key-here
OPENAI_MODEL=gpt-4

# Ollama Configuration (optional)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3

# Default Provider
DEFAULT_PROVIDER=ollama
```

### Step 5: Configure Settings

Edit `config/settings.json`:

```json
{
  "llm": {
    "provider": "ollama",
    "model": "llama3",
    "temperature": 0.7,
    "max_tokens": 4096
  },
  "ui": {
    "theme": "dark",
    "show_loader": true
  },
  "agents": {
    "default_agent": "terminal",
    "enable_context_monitoring": true,
    "enable_learning": true
  }
}
```

### Step 6: Launch

```bash
python main.py
```

With verbose logging:
```bash
python main.py --verbose
```

With debug logging:
```bash
python main.py --debug
```

CLI mode (no UI):
```bash
python main.py --cli
```

---

## 9. CONFIGURATION

### Configuration File: `config/settings.json`

The main configuration file controls all aspects of NEXUS behavior.

#### LLM Settings

```json
{
  "llm": {
    "provider": "ollama",
    "model": "llama3",
    "temperature": 0.7,
    "max_tokens": 4096,
    "top_p": 1.0,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0
  }
}
```

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `provider` | string | `"ollama"` | LLM provider: `"ollama"`, `"openai"`, or `"custom"` |
| `model` | string | `"llama3"` | Model name (depends on provider) |
| `temperature` | float | `0.7` | Creativity (0.0 = deterministic, 1.0 = creative) |
| `max_tokens` | int | `4096` | Maximum response length |
| `top_p` | float | `1.0` | Nucleus sampling threshold |
| `frequency_penalty` | float | `0.0` | Penalize repeated tokens (-2.0 to 2.0) |
| `presence_penalty` | float | `0.0` | Penalize token presence (-2.0 to 2.0) |

#### UI Settings

```json
{
  "ui": {
    "theme": "dark",
    "show_loader": true,
    "streaming": true,
    "animation_speed": "normal"
  }
}
```

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `theme` | string | `"dark"` | UI theme: `"dark"`, `"light"`, `"nord"`, `"dracula"` |
| `show_loader` | bool | `true` | Show cinematic startup loader |
| `streaming` | bool | `true` | Enable streaming responses |
| `animation_speed` | string | `"normal"` | Animation speed: `"slow"`, `"normal"`, `"fast"` |

#### Agent Settings

```json
{
  "agents": {
    "default_agent": "terminal",
    "enable_context_monitoring": true,
    "enable_learning": true,
    "max_concurrent_tasks": 5,
    "task_timeout": 300
  }
}
```

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `default_agent` | string | `"terminal"` | Default agent for unmatched requests |
| `enable_context_monitoring` | bool | `true` | Enable context awareness agent |
| `enable_learning` | bool | `true` | Enable learning agent |
| `max_concurrent_tasks` | int | `5` | Maximum parallel task execution |
| `task_timeout` | int | `300` | Task timeout in seconds |

### Environment Variables (`.env`)

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | OpenAI API key (required for OpenAI provider) |
| `OPENAI_MODEL` | OpenAI model name (default: `gpt-4`) |
| `OPENAI_BASE_URL` | Custom OpenAI API endpoint |
| `OLLAMA_BASE_URL` | Ollama server URL (default: `http://localhost:11434`) |
| `OLLAMA_MODEL` | Ollama model name (default: `llama3`) |
| `DEFAULT_PROVIDER` | Default LLM provider (default: `ollama`) |
| `NEXUS_LOG_LEVEL` | Override log level: `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `NEXUS_DATA_DIR` | Custom data directory path |
| `NEXUS_CONFIG_DIR` | Custom config directory path |

### Configuration Loading Order

1. **Defaults** — Hardcoded defaults in `core/config.py`
2. **Environment Variables** — `.env` file values
3. **Settings File** — `config/settings.json` values (override defaults and env vars)

The `Config` class is a singleton. Access it from anywhere:

```python
from core.config import config

provider = config.get("llm.provider")
theme = config.get("ui.theme")
```

---

## 10. FIRST LAUNCH

### The Startup Sequence

When you run `python main.py` for the first time:

1. **Cinematic Loader** appears with animated ASCII banner
2. **Phase 1: Core Systems** — Logger, config, database initialized
3. **Phase 2: Agent Registry** — All 21 agents discovered and loaded
4. **Phase 3: Communication** — Event bus, message broker, shared state initialized
5. **Phase 4: Intelligence** — Context awareness, learning engine, planning engine started
6. **Phase 5: UI** — Textual application launched with dashboard screen
7. **Summary Dashboard** shows startup metrics

### What to Expect

- **First launch** may take 10–30 seconds depending on your system
- **Subsequent launches** are faster as databases are already initialized
- **Ollama users** should ensure Ollama is running (`ollama serve`)
- **OpenAI users** should verify their API key in `.env`

### Post-Launch

After the loader completes, you'll see the **Dashboard Screen** with:
- System status overview
- Active agent count
- Recent activity
- Quick commands
- Keyboard shortcuts

Press `[Enter]` on any quick command to execute it, or type a command in the input field at the bottom.

---

## 11. THE CINEMATIC STARTUP EXPERIENCE

### Overview

NEXUS features a cinematic startup sequence that transforms the typically boring initialization process into an engaging, informative experience. The loader uses `rich.live.Live` with 8 FPS refresh rate, custom spinner frames, and animated progress bars.

### Components

#### CinematicLoader

The main loader class that orchestrates the startup sequence:

```python
from terminal.loader import CinematicLoader

loader = CinematicLoader()
loader.run()
```

Features:
- Animated ASCII NEXUS banner
- Custom spinner with 12 frames
- Progress bar with percentage
- Phase and step tracking
- Summary dashboard at completion

#### PhaseTracker

Context manager for tracking initialization phases:

```python
with loader.phase_tracker("Core Systems", total_steps=4) as tracker:
    tracker.advance("Initializing logger...")
    tracker.advance("Loading configuration...")
    tracker.advance("Connecting to database...")
    tracker.advance("Core systems ready!")
```

Features:
- Phase name displayed prominently
- Step counter (e.g., "Step 2/4")
- Progress bar within phase
- Smooth transitions between steps

#### StepTracker

Lightweight tracker for individual steps within a phase:

```python
with loader.step_tracker("Agent Registry") as tracker:
    tracker.advance("Loading file_agent...")
    tracker.advance("Loading web_agent...")
    # ... more agents
```

### Output Suppression

During normal startup, Python warnings and INFO-level logs are suppressed:

```python
from terminal.loader import suppress_output

with suppress_output():
    # Raw stdout/stderr redirected to os.devnull
    initialize_nexus()
# Output restored for Textual UI
```

This ensures a clean, cinematic experience without raw dependency warnings or database initialization messages.

### Verbose/Debug Modes

When launched with `--verbose` or `--debug`, output suppression is disabled:

- **`--verbose`**: Shows INFO-level logs and all stdout/stderr
- **`--debug`**: Shows DEBUG-level logs, all stdout/stderr, and detailed error traces

### Customization

The loader's appearance can be customized in `config/settings.json`:

```json
{
  "ui": {
    "show_loader": true,
    "animation_speed": "normal"
  }
}
```

Set `show_loader` to `false` to skip the cinematic loader entirely.

---

## 12. COMMAND-LINE INTERFACE

### Basic Usage

```bash
python main.py                    # Launch with cinematic loader
python main.py --verbose          # Show INFO logs during startup
python main.py --debug            # Show DEBUG logs during startup
python main.py --cli              # CLI mode (no Textual UI)
python main.py -v                 # Short form of --verbose
python main.py -d                 # Short form of --debug
```

### CLI Flags

| Flag | Short | Description |
|------|-------|-------------|
| `--verbose` | `-v` | Show INFO-level logs and all stdout/stderr during startup |
| `--debug` | `-d` | Show DEBUG-level logs and detailed error traces |
| `--cli` | | Run in CLI mode without Textual UI |

### CLI Mode

When launched with `--cli`, NEXUS runs in a simple command-line mode without the Textual UI:

```bash
python main.py --cli
```

In CLI mode:
- You type commands directly into the terminal
- Responses are printed as plain text
- No panels, themes, or keyboard navigation
- Useful for scripting or remote SSH sessions

### CLI Commands

In CLI mode, you can use any NEXUS command:

```
> help                    # Show available commands
> list files              # File agent: list files in current directory
> search web for Python # Web agent: search the web
> create workflow         # Workflow agent: create a new workflow
> exit                    # Exit NEXUS
```

### Environment Variable Overrides

CLI flags can also be controlled via environment variables:

```bash
NEXUS_LOG_LEVEL=DEBUG python main.py
NEXUS_SHOW_LOADER=false python main.py
```

---

*Continue to Part III: The Terminal Environment →*
