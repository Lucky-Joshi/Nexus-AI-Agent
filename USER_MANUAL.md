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

---

## 13. TERMINAL UI ARCHITECTURE

### Overview

NEXUS uses the **Textual** framework (version 8.2.6) to build a rich, interactive terminal user interface. Textual provides widgets, screens, themes, and event handling — all rendered in the terminal using Unicode box-drawing characters and ANSI colors.

### Application Structure

The main application is defined in `terminal/app.py`:

```python
class NexusApp(App):
    """Main NEXUS Textual application."""
```

Key components:
- **App class** — Central application with theme registration and screen management
- **Screens** — Dashboard, Chat, and Task Monitor screens
- **Themes** — Registered via `register_theme()` (Textual 8.2.6 API)
- **Widgets** — Custom widgets: NexusHeader, NexusStatusBar, and more

### Screen Management

Screens are explicitly installed rather than using the `SCREENS` dict:

```python
def on_mount(self) -> None:
    dashboard = DashboardScreen(manager=self.manager)
    self.install_screen(dashboard, name="dashboard")
    self.push_screen("dashboard")
```

This pattern ensures:
- Dependencies (like `manager`) are injected before screen instantiation
- Screens are properly registered with the Textual app
- Screen transitions are explicit and predictable

### Available Screens

| Screen | Purpose | Access |
|--------|---------|--------|
| `DashboardScreen` | System overview, quick commands, status | Default screen |
| `ChatScreen` | Conversational interface with streaming | From dashboard or `chat` command |
| `TaskScreen` | Task monitoring, progress tracking | From dashboard or `tasks` command |

### Theme System

Themes are registered using the modern Textual API:

```python
def on_mount(self) -> None:
    self.register_theme(NEXUS_DARK_THEME)
    self.register_theme(NEXUS_LIGHT_THEME)
```

Available themes are defined in `terminal/theme.py`. Each theme specifies:
- Primary, secondary, and accent colors
- Background and surface colors
- Success, warning, error, and info colors
- Border styles

### Widget Hierarchy

```
App
├── Header (NexusHeader → render() → Panel)
├── Main Content (Screen-specific)
│   ├── DashboardScreen
│   │   ├── Status panels
│   │   ├── Quick commands
│   │   └── Activity feed
│   ├── ChatScreen
│   │   ├── Message history
│   │   ├── Input field
│   │   └── Streaming indicator
│   └── TaskScreen
│       ├── Task list
│       ├── Progress bars
│       └── Filter controls
└── Footer (NexusStatusBar → render() → Panel)
```

### Important Textual API Notes

**`Static.update()` requires Rich renderables**  
When updating a `Static` widget, you must pass a Rich renderable or string. Custom widgets that override `render()` must call `.render()` explicitly:

```python
# Correct:
header_widget.update(header.render())

# Incorrect (causes crash):
header_widget.update(header)
```

**`install_screen()` vs `SCREENS` dict**  
Textual supports both patterns, but `install_screen()` is required when you need to inject dependencies:

```python
# Correct (dependency injection):
dashboard = DashboardScreen(manager=self.manager)
self.install_screen(dashboard, name="dashboard")

# Incorrect (no dependency injection):
SCREENS = {"dashboard": DashboardScreen}  # manager not available
```

---

## 14. DASHBOARD SCREEN

### Overview

The Dashboard Screen (`terminal/screens/dashboard.py`) is the default screen shown after startup. It provides a high-level overview of the system and quick access to common commands.

### Layout

```
┌─────────────────────────────────────────────────────┐
│                    NEXUS HEADER                      │
├─────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │   Status    │  │   Agents    │  │   Tasks     │  │
│  │   Panel     │  │   Panel     │  │   Panel     │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  │
│  ┌─────────────────────────────────────────────┐    │
│  │              Quick Commands                  │    │
│  │  • list files    • search web               │    │
│  │  • create workflow    • show tasks          │    │
│  └─────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────┐    │
│  │              Activity Feed                   │    │
│  │  [12:34] File agent: Listed 42 files        │    │
│  │  [12:35] Web agent: Found 15 results        │    │
│  └─────────────────────────────────────────────┘    │
├─────────────────────────────────────────────────────┤
│                    STATUS BAR                        │
└─────────────────────────────────────────────────────┘
```

### Widget Composition

The dashboard uses a `compose()` method to instantiate all widgets:

```python
def compose(self) -> ComposeResult:
    yield Static("NEXUS Dashboard", id="title")
    yield Static(self.build_status_panel(), id="status-panel")
    yield Static(self.build_agents_panel(), id="agents-panel")
    yield Static(self.build_tasks_panel(), id="tasks-panel")
    yield Static(self.build_quick_commands(), id="quick-commands")
    yield Static(self.build_activity_feed(), id="activity-feed")
```

### Status Panel

Shows real-time system information:
- NEXUS version
- LLM provider and model
- Active agent count
- Database status
- Memory usage

### Agents Panel

Lists all loaded agents with their status:
- Agent name
- Status (active, idle, error)
- Last activity timestamp
- Command count

### Tasks Panel

Shows current and recent tasks:
- Task ID
- Description
- Status (pending, running, completed, failed)
- Progress percentage
- Assigned agent

### Quick Commands

Pre-defined commands for common operations:
- `list files` — File agent
- `search web for <query>` — Web agent
- `create workflow` — Workflow agent
- `show tasks` — Task monitor
- `system status` — Analytics agent
- `help` — Show all commands

### Activity Feed

Real-time log of system events:
- Timestamp
- Agent name
- Action description
- Status indicator

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `c` | Open chat screen |
| `t` | Open task monitor |
| `q` | Quick command input |
| `r` | Refresh dashboard |
| `?` | Show help |
| `Ctrl+Q` | Quit NEXUS |

---

## 15. CHAT INTERFACE

### Overview

The Chat Screen (`terminal/screens/chat.py`) provides a conversational interface for interacting with NEXUS agents. It supports streaming responses, message history, and keyboard navigation.

### Layout

```
┌─────────────────────────────────────────────────────┐
│                    NEXUS HEADER                      │
├─────────────────────────────────────────────────────┤
│                                                     │
│  [You] list files in current directory              │
│                                                     │
│  [NEXUS] Here are the files in the current          │
│          directory:                                 │
│          • main.py (2.3 KB)                         │
│          • README.md (5.1 KB)                       │
│          • requirements.txt (1.2 KB)                │
│          ... and 39 more files                      │
│                                                     │
│  [You] search the web for Python 3.12 features      │
│                                                     │
│  [NEXUS] ▌ (streaming...)                           │
│                                                     │
├─────────────────────────────────────────────────────┤
│  > Type your message...                              │
├─────────────────────────────────────────────────────┤
│                    STATUS BAR                        │
└─────────────────────────────────────────────────────┘
```

### Features

- **Streaming Responses** — Responses appear character-by-character as the LLM generates them
- **Message History** — All messages in the current session are preserved
- **Markdown Rendering** — Responses can include formatted code blocks, lists, and headers
- **Input Field** — Text input at the bottom with command history navigation
- **Agent Indicators** — Each response shows which agent handled the request

### Message Flow

1. User types message and presses Enter
2. Message is sent to the router
3. Router determines the appropriate agent
4. Agent processes the request (may call LLM)
5. Response streams back to the chat interface
6. Message is saved to conversation history

### Input Commands

While in the chat input field:
- `Enter` — Send message
- `Up/Down` — Navigate command history
- `Ctrl+C` — Cancel current input
- `Esc` — Clear input field
- `Ctrl+L` — Clear chat history

### Conversation Persistence

Conversations are saved to `data/nexus.db` in the `conversations` table. Each conversation includes:
- Conversation ID (UUID)
- User message
- Agent response
- Timestamp
- Agent name
- Session ID

---

## 16. TASK MONITOR

### Overview

The Task Screen (`terminal/screens/tasks.py`) provides real-time monitoring of all background tasks executed by NEXUS agents.

### Layout

```
┌─────────────────────────────────────────────────────┐
│                    NEXUS HEADER                      │
├─────────────────────────────────────────────────────┤
│  Task Queue: 3 pending | 2 running | 15 completed   │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌─ ID ───────┬─ Status ───┬─ Progress ─┬─ Agent ─┐ │
│  │ task-001   │ Running    │ ████░░ 67% │ File    │ │
│  │ task-002   │ Running    │ ██░░░░ 33% │ Web     │ │
│  │ task-003   │ Pending    │ ░░░░░░  0% │ Coding  │ │
│  │ task-004   │ Completed  │ ██████ 100%│ Memory  │ │
│  │ task-005   │ Failed     │ ███░░░ 50% │ Vision  │ │
│  └────────────┴────────────┴────────────┴─────────┘ │
│                                                     │
├─────────────────────────────────────────────────────┤
│  [F1] Refresh  [F2] Cancel  [F3] Retry  [F5] Clear  │
├─────────────────────────────────────────────────────┤
│                    STATUS BAR                        │
└─────────────────────────────────────────────────────┘
```

### Task States

| State | Description |
|-------|-------------|
| `PENDING` | Task is queued, waiting for execution |
| `QUEUED` | Task has been assigned to an agent |
| `RUNNING` | Task is currently executing |
| `COMPLETED` | Task finished successfully |
| `FAILED` | Task encountered an error |
| `SKIPPED` | Task was skipped (dependency failed) |
| `BLOCKED` | Task is waiting for a dependency |
| `RETRYING` | Task is being retried after failure |

### Task Details

Each task includes:
- **Task ID** — Unique identifier (e.g., `task-001`)
- **Description** — Human-readable task description
- **Status** — Current state (see above)
- **Progress** — Percentage complete (0–100%)
- **Agent** — Assigned agent name
- **Created At** — Timestamp when task was created
- **Started At** — Timestamp when execution began
- **Completed At** — Timestamp when task finished
- **Error Message** — Error details (if failed)
- **Retry Count** — Number of retry attempts

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `F1` | Refresh task list |
| `F2` | Cancel selected task |
| `F3` | Retry failed task |
| `F5` | Clear completed tasks |
| `Tab` | Navigate between tasks |
| `Enter` | View task details |
| `Esc` | Return to dashboard |

### Task Filtering

Tasks can be filtered by:
- Status (all, pending, running, completed, failed)
- Agent (specific agent or all)
- Time range (last hour, last day, all)

---

## 17. THEME SYSTEM

### Overview

NEXUS supports multiple visual themes that control the appearance of the terminal UI. Themes are defined in `terminal/theme.py` and registered with the Textual application.

### Available Themes

#### NEXUS Dark (Default)

```python
NEXUS_DARK_THEME = Theme(
    name="nexus-dark",
    primary="#4A90D9",
    secondary="#50C878",
    accent="#FF6B6B",
    background="#1A1A2E",
    surface="#16213E",
    success="#50C878",
    warning="#FFA500",
    error="#FF6B6B",
    info="#4A90D9",
)
```

- Deep navy background
- Blue primary color
- Green secondary color
- Red accent for errors
- High contrast for readability

#### NEXUS Light

```python
NEXUS_LIGHT_THEME = Theme(
    name="nexus-light",
    primary="#2563EB",
    secondary="#059669",
    accent="#DC2626",
    background="#F8FAFC",
    surface="#FFFFFF",
    success="#059669",
    warning="#D97706",
    error="#DC2626",
    info="#2563EB",
)
```

- Light gray background
- Blue primary color
- Green secondary color
- Red accent for errors
- Clean, professional appearance

### Theme Switching

Themes can be switched at runtime:

```python
# From within the app:
self.app.theme = "nexus-light"

# From configuration:
# config/settings.json
{
  "ui": {
    "theme": "nexus-light"
  }
}
```

### Theme Colors

Each theme defines the following color variables:

| Variable | Purpose |
|----------|---------|
| `primary` | Main UI elements, headers, buttons |
| `secondary` | Secondary elements, accents |
| `accent` | Highlight elements, notifications |
| `background` | Main background color |
| `surface` | Panel/card background |
| `success` | Success indicators, completed tasks |
| `warning` | Warning indicators, pending tasks |
| `error` | Error indicators, failed tasks |
| `info` | Information indicators, help text |

### Custom Themes

You can create custom themes by defining a new `Theme` object and registering it:

```python
from textual.theme import Theme

MY_THEME = Theme(
    name="my-theme",
    primary="#FF00FF",
    secondary="#00FFFF",
    # ... other colors
)

# In your app's on_mount:
self.register_theme(MY_THEME)
```

---

## 18. STREAMING RESPONSES

### Overview

The streaming module (`terminal/streaming.py`) handles real-time streaming of LLM responses to the terminal UI. Instead of waiting for the entire response, characters appear as they are generated.

### How Streaming Works

1. **LLM Provider** sends response chunks via server-sent events (OpenAI) or streaming API (Ollama)
2. **Streaming Handler** receives chunks and yields characters/tokens
3. **UI Widget** updates in real-time, appending new characters
4. **Cursor** blinks at the current position to indicate active streaming

### Implementation

```python
async def stream_response(self, response_generator) -> str:
    """Stream LLM response to UI in real-time."""
    full_response = ""
    async for chunk in response_generator:
        if chunk.choices and chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            full_response += content
            # Update UI widget
            self.message_widget.update(full_response)
    return full_response
```

### Streaming Indicators

While streaming is active:
- A blinking cursor (`▌`) appears at the end of the response
- The status bar shows "Streaming..."
- The input field is disabled until streaming completes

### Streaming Controls

| Action | Key |
|--------|-----|
| Stop streaming | `Ctrl+C` |
| Skip to end | `Space` |

### Fallback Behavior

If streaming is disabled or unavailable:
- The full response is generated before display
- A loading spinner appears during generation
- The response appears all at once when complete

### Performance Considerations

- Streaming updates are throttled to 30 FPS to prevent UI flicker
- Large responses are buffered to prevent memory issues
- Network interruptions trigger automatic retry

---

## 19. KEYBOARD NAVIGATION

### Global Shortcuts

These shortcuts work from any screen:

| Key | Action |
|-----|--------|
| `Ctrl+Q` | Quit NEXUS |
| `Ctrl+L` | Clear current screen |
| `?` | Show help overlay |
| `Esc` | Go back / cancel |

### Dashboard Shortcuts

| Key | Action |
|-----|--------|
| `c` | Open chat screen |
| `t` | Open task monitor |
| `q` | Quick command input |
| `r` | Refresh dashboard |

### Chat Shortcuts

| Key | Action |
|-----|--------|
| `Enter` | Send message |
| `Up/Down` | Navigate message history |
| `Ctrl+C` | Cancel input / stop streaming |
| `Esc` | Clear input |
| `Ctrl+L` | Clear chat history |

### Task Monitor Shortcuts

| Key | Action |
|-----|--------|
| `F1` | Refresh task list |
| `F2` | Cancel selected task |
| `F3` | Retry failed task |
| `F5` | Clear completed tasks |
| `Tab` | Navigate between tasks |
| `Enter` | View task details |

### Focus Management

Textual manages focus automatically:
- Input fields receive focus when navigated to
- Tab/Shift+Tab moves focus between widgets
- Arrow keys navigate within focused lists
- Enter activates the focused button/command

---

## 20. CUSTOM WIDGETS

### Overview

NEXUS defines custom widgets in `terminal/widgets.py` to provide consistent styling and behavior across all screens.

### NexusHeader

A custom header widget that renders a styled panel with the NEXUS title and status:

```python
class NexusHeader(Static):
    def render(self) -> Panel:
        return Panel(
            Align.center("NEXUS — AI Operating Environment"),
            title="NEXUS",
            border_style="primary",
        )
```

**Important**: When updating a `Static` widget containing a `NexusHeader`, you must call `.render()`:

```python
header = NexusHeader()
widget.update(header.render())  # Correct
widget.update(header)           # Wrong — causes crash
```

### NexusStatusBar

A custom status bar widget that shows real-time system information:

```python
class NexusStatusBar(Static):
    def render(self) -> Panel:
        return Panel(
            f"Agents: {active_count} | Tasks: {task_count} | {time}",
            border_style="secondary",
        )
```

### Usage Pattern

All custom widgets follow the same pattern:
1. Extend `Static` from Textual
2. Override `render()` to return a Rich `Panel`
3. Use theme colors for consistent styling
4. Call `.render()` when passing to `update()`

---

## 21. BASE AGENT ARCHITECTURE

### Overview

All 21 agents in NEXUS extend the abstract `BaseAgent` class defined in `core/base_agent.py`. This class provides a common interface, lifecycle management, and utility methods.

### BaseAgent Class

```python
from abc import ABC, abstractmethod
from enum import Enum

class AgentStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    ERROR = "error"
    DISABLED = "disabled"

class BaseAgent(ABC):
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.status = AgentStatus.IDLE
        self.command_count = 0
    
    @abstractmethod
    async def execute(self, command: str, **kwargs) -> dict:
        """Execute a command and return result."""
        pass
    
    @abstractmethod
    def get_commands(self) -> list[str]:
        """Return list of supported commands."""
        pass
    
    def start(self) -> None:
        """Start the agent."""
        self.status = AgentStatus.RUNNING
    
    def stop(self) -> None:
        """Stop the agent."""
        self.status = AgentStatus.IDLE
    
    def get_status(self) -> AgentStatus:
        """Return current agent status."""
        return self.status
```

### Agent Lifecycle

1. **Initialization** — Agent is instantiated with name and description
2. **Registration** — Agent is registered with the AIManager
3. **Command Discovery** — `get_commands()` is called to build the command index
4. **Execution** — `execute()` is called when a command matches the agent
5. **Shutdown** — `stop()` is called during application shutdown

### Result Format

All agents return results in a standard format:

```python
{
    "success": True,
    "data": "...",          # Response data
    "agent": "file_agent",  # Agent name
    "timestamp": "...",     # ISO timestamp
    "error": None           # Error message (if failed)
}
```

### Agent Structure

Each agent is a Python package with a standard structure:

```
agent_name/
├── __init__.py          # Package exports
├── agent.py             # Main agent class (extends BaseAgent)
├── models.py            # Pydantic data models
├── services.py          # Business logic services
└── storage.py           # Database/persistence layer
```

### Extending BaseAgent

To create a new agent:

```python
from core.base_agent import BaseAgent, AgentStatus

class MyAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="my_agent",
            description="Description of what my agent does"
        )
    
    async def execute(self, command: str, **kwargs) -> dict:
        if command == "do something":
            result = self._do_something(kwargs)
            return {
                "success": True,
                "data": result,
                "agent": self.name,
                "timestamp": datetime.now().isoformat(),
                "error": None
            }
        return {"success": False, "error": "Unknown command"}
    
    def get_commands(self) -> list[str]:
        return ["do something", "do another thing"]
    
    def _do_something(self, kwargs: dict) -> str:
        # Implementation
        return "Result"
```

---

## 22. AI MANAGER

### Overview

The `AIManager` (`manager/manager.py`) is the central orchestrator of NEXUS. It manages agent lifecycle, handles command routing, and coordinates inter-agent communication.

### Responsibilities

- **Agent Registry** — Discover, load, and register all agents
- **Command Index** — Build a searchable index of all agent commands
- **Request Routing** — Forward user requests to the appropriate agent
- **Lifecycle Management** — Start, stop, and monitor all agents
- **Error Handling** — Catch and report agent failures
- **Metrics Collection** — Track agent performance and usage

### Initialization

```python
class AIManager:
    def __init__(self):
        self.agents: dict[str, BaseAgent] = {}
        self.command_index: dict[str, BaseAgent] = {}
        self.router = Router()
        self.dispatcher = Dispatcher()
    
    async def initialize(self) -> None:
        """Load all agents and build command index."""
        self._discover_agents()
        self._build_command_index()
        self._start_agents()
```

### Agent Discovery

Agents are discovered by scanning the `agents/` directory:

```python
def _discover_agents(self) -> None:
    for agent_dir in os.listdir("agents"):
        if os.path.isdir(f"agents/{agent_dir}"):
            module = importlib.import_module(f"agents.{agent_dir}.agent")
            agent_class = getattr(module, agent_dir.title().replace("_", "") + "Agent")
            agent = agent_class()
            self.agents[agent.name] = agent
```

### Command Index

The command index maps command patterns to agents:

```python
def _build_command_index(self) -> None:
    for agent in self.agents.values():
        for command in agent.get_commands():
            self.command_index[command] = agent
```

### Request Handling

```python
async def handle_request(self, user_input: str) -> dict:
    """Route user input to the appropriate agent."""
    # Stage 1: Router determines intent
    agent = self.router.route(user_input, self.command_index)
    
    # Stage 2: Dispatcher queues the task
    task = await self.dispatcher.dispatch(agent, user_input)
    
    # Stage 3: Agent executes the command
    result = await agent.execute(user_input)
    
    # Stage 4: Result is returned to the UI
    return result
```

### Manager API

| Method | Description |
|--------|-------------|
| `initialize()` | Load all agents, build command index, start agents |
| `handle_request(input)` | Route and execute user input |
| `get_agent(name)` | Get agent by name |
| `get_agents()` | Get all agents |
| `get_commands()` | Get all registered commands |
| `shutdown()` | Stop all agents and clean up |

---

## 23. INTENT ROUTER

### Overview

The Router (`manager/router.py`) implements a 3-stage intent detection pipeline to determine which agent should handle a user request.

### 3-Stage Routing

```
User Input → Stage 1: Regex → Stage 2: Fuzzy → Stage 3: LLM → Agent
```

#### Stage 1: Regex Matching

Fast, pattern-based matching for common commands:

```python
REGEX_PATTERNS = {
    r"list\s+files?": "file_agent",
    r"search\s+web": "web_agent",
    r"create\s+workflow": "workflow_agent",
    r"show\s+tasks?": "scheduler_agent",
    r"system\s+status": "analytics_agent",
    # ... more patterns
}
```

- **Speed**: Instant (microseconds)
- **Accuracy**: High for exact patterns
- **Fallback**: If no match, proceed to Stage 2

#### Stage 2: Fuzzy Matching

Fuzzy string matching for commands that are close to known patterns:

```python
from difflib import SequenceMatcher

def fuzzy_match(input: str, commands: list[str], threshold: float = 0.7) -> str | None:
    best_match = None
    best_score = 0
    for command in commands:
        score = SequenceMatcher(None, input.lower(), command.lower()).ratio()
        if score > best_score and score >= threshold:
            best_score = score
            best_match = command
    return best_match
```

- **Speed**: Fast (milliseconds)
- **Accuracy**: Good for typos and near-matches
- **Fallback**: If no match above threshold, proceed to Stage 3

#### Stage 3: LLM Classification

Uses the LLM to classify ambiguous requests:

```python
async def llm_classify(input: str, agents: list[BaseAgent]) -> BaseAgent:
    prompt = f"""
    Given the user request: "{input}"
    And the available agents: {agent_descriptions}
    Which agent should handle this request?
    """
    response = await llm_provider.generate(prompt)
    return parse_agent_name(response)
```

- **Speed**: Slow (seconds, depends on LLM)
- **Accuracy**: Highest for ambiguous requests
- **Fallback**: If LLM fails, default to terminal agent

### Routing Configuration

The router can be configured in `config/settings.json`:

```json
{
  "router": {
    "fuzzy_threshold": 0.7,
    "enable_llm_routing": true,
    "default_agent": "terminal"
  }
}
```

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `fuzzy_threshold` | float | `0.7` | Minimum similarity score for fuzzy matching |
| `enable_llm_routing` | bool | `true` | Enable LLM-based classification |
| `default_agent` | string | `"terminal"` | Fallback agent if all stages fail |

### Performance

| Stage | Latency | Hit Rate |
|-------|---------|----------|
| Regex | < 1ms | ~60% |
| Fuzzy | < 10ms | ~20% |
| LLM | 1–5s | ~15% |
| Default | < 1ms | ~5% |

---

## 24. TASK DISPATCHER

### Overview

The Dispatcher (`manager/dispatcher.py`) handles asynchronous task execution, managing a priority queue of tasks and distributing them to agents.

### Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Router    │ ──→ │  Dispatcher  │ ──→ │   Agent     │
│  (Intent)   │     │  (Queue)     │     │  (Executor) │
└─────────────┘     └──────────────┘     └─────────────┘
                           │
                    ┌──────┴──────┐
                    │  Task Queue │
                    │  (Priority) │
                    └─────────────┘
```

### Task Queue

Tasks are queued with priority levels:

```python
class TaskPriority(Enum):
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3
    BACKGROUND = 4
```

### Task Structure

```python
@dataclass
class Task:
    id: str
    description: str
    agent: BaseAgent
    command: str
    priority: TaskPriority
    status: TaskStatus
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    result: dict | None
    error: str | None
    retry_count: int
    max_retries: int
```

### Dispatch Flow

1. **Receive Task** — Router sends task to dispatcher
2. **Queue Task** — Task is added to priority queue
3. **Execute Task** — Worker picks up task and calls agent
4. **Track Progress** — Task status is updated in real-time
5. **Return Result** — Result is sent back to the UI
6. **Persist** — Task record is saved to database

### Async Execution

The dispatcher uses `asyncio` for non-blocking execution:

```python
async def dispatch(self, agent: BaseAgent, command: str) -> Task:
    task = Task(
        id=str(uuid.uuid4()),
        agent=agent,
        command=command,
        priority=TaskPriority.NORMAL,
        status=TaskStatus.PENDING,
    )
    self.queue.put_nowait(task)
    return task

async def worker(self) -> None:
    while True:
        task = await self.queue.get()
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now()
        try:
            task.result = await task.agent.execute(task.command)
            task.status = TaskStatus.COMPLETED
        except Exception as e:
            task.error = str(e)
            task.status = TaskStatus.FAILED
        task.completed_at = datetime.now()
        self.queue.task_done()
```

### Concurrency Control

Maximum concurrent tasks are configurable:

```json
{
  "agents": {
    "max_concurrent_tasks": 5
  }
}
```

The dispatcher spawns N worker coroutines based on this setting.

### Retry Logic

Failed tasks are automatically retried:

```python
if task.status == TaskStatus.FAILED and task.retry_count < task.max_retries:
    task.retry_count += 1
    task.status = TaskStatus.PENDING
    self.queue.put_nowait(task)
```

Default: 3 retries with exponential backoff.

---

## 25. LLM PROVIDER

### Overview

The LLM Provider (`core/llm_provider.py`) abstracts the interaction with language models, supporting multiple providers through a unified interface.

### Supported Providers

| Provider | Type | Setup |
|----------|------|-------|
| `ollama` | Local | Install Ollama, pull a model |
| `openai` | Cloud | Set API key in `.env` |
| `custom` | Any OpenAI-compatible API | Set base URL in `.env` |

### Provider Configuration

```json
{
  "llm": {
    "provider": "ollama",
    "model": "llama3",
    "temperature": 0.7,
    "max_tokens": 4096
  }
}
```

### API Methods

| Method | Description |
|--------|-------------|
| `generate(prompt)` | Generate a completion for a prompt |
| `generate_stream(prompt)` | Stream a completion response |
| `chat(messages)` | Chat completion with message history |
| `chat_stream(messages)` | Stream a chat completion |
| `embed(text)` | Generate text embeddings (if supported) |

### Ollama Setup

1. Install Ollama: https://ollama.ai
2. Pull a model: `ollama pull llama3`
3. Start Ollama: `ollama serve`
4. Configure NEXUS:
   ```json
   {
     "llm": {
       "provider": "ollama",
       "model": "llama3"
     }
   }
   ```

### OpenAI Setup

1. Get an API key: https://platform.openai.com
2. Set in `.env`:
   ```env
   OPENAI_API_KEY=sk-...
   OPENAI_MODEL=gpt-4
   ```
3. Configure NEXUS:
   ```json
   {
     "llm": {
       "provider": "openai",
       "model": "gpt-4"
     }
   }
   ```

### Custom Provider

For any OpenAI-compatible API:

```env
OPENAI_BASE_URL=http://your-api:8080/v1
OPENAI_API_KEY=your-key
```

```json
{
  "llm": {
    "provider": "custom",
    "model": "your-model"
  }
}
```

### Streaming Support

The provider supports streaming for real-time responses:

```python
async for chunk in llm_provider.generate_stream(prompt):
    print(chunk.choices[0].delta.content, end="")
```

### Error Handling

The provider handles common errors gracefully:

- **Connection errors** — Retry with exponential backoff
- **Rate limits** — Wait and retry
- **Invalid API key** — Log error, return fallback response
- **Model not found** — Log error, suggest alternatives

---

## 26. CONFIGURATION SYSTEM

### Overview

The Configuration system (`core/config.py`) is a singleton that loads and manages settings from multiple sources.

### Loading Order

1. **Defaults** — Hardcoded in `Config.__init__()`
2. **Environment Variables** — `.env` file
3. **Settings File** — `config/settings.json`

### Singleton Pattern

```python
class Config:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._load_defaults()
        self._load_env()
        self._load_settings_file()
```

### Access Pattern

```python
from core.config import config

# Dot notation for nested keys:
provider = config.get("llm.provider")
theme = config.get("ui.theme")
max_tasks = config.get("agents.max_concurrent_tasks")

# With default value:
model = config.get("llm.model", default="llama3")
```

### Configuration Reloading

The config can be reloaded at runtime:

```python
config.reload()
```

This is useful when the settings file is modified externally.

### Validation

The config validates required keys on load:

```python
required_keys = ["llm.provider", "llm.model"]
for key in required_keys:
    if not self.get(key):
        raise ConfigurationError(f"Missing required config: {key}")
```

---

## 27. LOGGING SYSTEM

### Overview

The Logging system (`core/logger.py`) provides dynamic log level control with separate file and console handlers.

### Features

- **File logging** — Always logs DEBUG level to `data/nexus.log`
- **Console logging** — Dynamically switches between WARNING/INFO/DEBUG
- **Runtime mode switching** — Change log level without restart
- **Output suppression** — Suppress console output during startup

### Log Levels

| Level | Console | File | Use Case |
|-------|---------|------|----------|
| `DEBUG` | DEBUG | DEBUG | Development, troubleshooting |
| `INFO` | INFO | DEBUG | Verbose mode, monitoring |
| `WARNING` | WARNING | DEBUG | Normal operation (default) |
| `ERROR` | ERROR | DEBUG | Error-only mode |

### Mode Switching

```python
from core.logger import logger

# Normal mode (default)
logger.set_mode("normal")    # Console: WARNING

# Verbose mode
logger.set_mode("verbose")   # Console: INFO

# Debug mode
logger.set_mode("debug")     # Console: DEBUG
```

### Output Suppression

During startup, console output is suppressed:

```python
from core.logger import logger

logger.suppress_console()
# ... initialization code ...
logger.enable_console()
```

### Log Format

```
2026-05-18 12:34:56 [INFO] module.name: Message text
```

Components:
- Timestamp (ISO format)
- Log level in brackets
- Module name
- Message text

### Log File

Logs are written to `data/nexus.log`:
- **Rotation**: Logs are not automatically rotated (manual cleanup recommended)
- **Format**: Same as console, but includes DEBUG level
- **Location**: `data/nexus.log`

### CLI Integration

Log level is set based on CLI flags:

```python
# In main.py:
if args.debug:
    logger.set_mode("debug")
elif args.verbose:
    logger.set_mode("verbose")
else:
    logger.set_mode("normal")
```

---

## 28. DATABASE LAYER

### Overview

The Database layer (`core/database.py`) provides a SQLite wrapper for persistent storage. NEXUS uses multiple SQLite databases for different concerns.

### Database Files

| File | Purpose | Size |
|------|---------|------|
| `data/nexus.db` | Main database (conversations, tasks, security, workflows, analytics) | Variable |
| `data/context.db` | Context awareness data | Variable |
| `data/learning.db` | Learning agent data | Variable |

### Main Database Schema (nexus.db)

#### Conversations

```sql
CREATE TABLE conversations (
    id TEXT PRIMARY KEY,
    user_message TEXT NOT NULL,
    agent_response TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    agent_name TEXT,
    session_id TEXT
);
```

#### Tasks

```sql
CREATE TABLE tasks (
    id TEXT PRIMARY KEY,
    description TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    agent_name TEXT,
    priority INTEGER DEFAULT 2,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    started_at DATETIME,
    completed_at DATETIME,
    result TEXT,
    error TEXT,
    retry_count INTEGER DEFAULT 0
);
```

#### Security Events

```sql
CREATE TABLE security_events (
    id TEXT PRIMARY KEY,
    event_type TEXT NOT NULL,
    severity TEXT,
    description TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    resolved BOOLEAN DEFAULT FALSE
);
```

#### Workflow Chains

```sql
CREATE TABLE workflow_chains (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    status TEXT DEFAULT 'draft',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE workflow_steps (
    id TEXT PRIMARY KEY,
    chain_id TEXT REFERENCES workflow_chains(id),
    agent_name TEXT NOT NULL,
    command TEXT NOT NULL,
    order_index INTEGER,
    status TEXT DEFAULT 'pending'
);
```

#### Analytics

```sql
CREATE TABLE analytics_events (
    id TEXT PRIMARY KEY,
    event_type TEXT NOT NULL,
    data TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### Bus Tables (Communication Bus)

```sql
CREATE TABLE bus_messages (
    id TEXT PRIMARY KEY,
    event_type TEXT NOT NULL,
    data TEXT,
    priority INTEGER DEFAULT 2,
    status TEXT DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE bus_subscriptions (
    id TEXT PRIMARY KEY,
    event_pattern TEXT NOT NULL,
    subscriber TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE bus_shared_state (
    id TEXT PRIMARY KEY,
    key TEXT NOT NULL UNIQUE,
    value TEXT,
    version INTEGER DEFAULT 1,
    namespace TEXT DEFAULT 'default',
    expires_at DATETIME,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE bus_event_log (
    id TEXT PRIMARY KEY,
    event_type TEXT NOT NULL,
    data TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### Planner Tables

```sql
CREATE TABLE plans (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    goal TEXT,
    status TEXT DEFAULT 'draft',
    progress REAL DEFAULT 0.0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE plan_tasks (
    id TEXT PRIMARY KEY,
    plan_id TEXT REFERENCES plans(id),
    description TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    dependencies TEXT,
    agent_name TEXT,
    order_index INTEGER
);

CREATE TABLE goal_templates (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    template_data TEXT
);

CREATE TABLE plan_history (
    id TEXT PRIMARY KEY,
    plan_id TEXT REFERENCES plans(id),
    event_type TEXT NOT NULL,
    data TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### Marketplace Tables

```sql
CREATE TABLE marketplace_agents (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    version TEXT,
    category TEXT,
    author TEXT,
    status TEXT DEFAULT 'available',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE install_records (
    id TEXT PRIMARY KEY,
    agent_id TEXT REFERENCES marketplace_agents(id),
    status TEXT DEFAULT 'installing',
    installed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    install_path TEXT
);

CREATE TABLE agent_reviews (
    id TEXT PRIMARY KEY,
    agent_id TEXT REFERENCES marketplace_agents(id),
    rating INTEGER,
    review TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE verification_reports (
    id TEXT PRIMARY KEY,
    agent_id TEXT REFERENCES marketplace_agents(id),
    status TEXT,
    report_data TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Context Database Schema (context.db)

```sql
CREATE TABLE context_snapshots (
    id TEXT PRIMARY KEY,
    active_window TEXT,
    running_apps TEXT,
    activity_type TEXT,
    focus_level TEXT,
    system_load REAL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE context_patterns (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    pattern_data TEXT
);

CREATE TABLE adaptive_triggers (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    condition TEXT,
    action TEXT,
    enabled BOOLEAN DEFAULT TRUE
);

CREATE TABLE context_sessions (
    id TEXT PRIMARY KEY,
    start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    end_time DATETIME,
    productivity_score REAL
);

CREATE TABLE context_rules (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    condition TEXT,
    action TEXT,
    enabled BOOLEAN DEFAULT TRUE
);
```

### Learning Database Schema (learning.db)

```sql
CREATE TABLE behavior_records (
    id TEXT PRIMARY KEY,
    action TEXT NOT NULL,
    preceding_actions TEXT,
    context TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE learned_patterns (
    id TEXT PRIMARY KEY,
    pattern_type TEXT,
    pattern_data TEXT,
    confidence REAL,
    status TEXT DEFAULT 'observing'
);

CREATE TABLE recommendations (
    id TEXT PRIMARY KEY,
    type TEXT,
    description TEXT,
    status TEXT DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_habits (
    id TEXT PRIMARY KEY,
    habit_type TEXT,
    description TEXT,
    frequency REAL,
    automation_potential REAL
);

CREATE TABLE prediction_log (
    id TEXT PRIMARY KEY,
    prediction TEXT,
    actual TEXT,
    accurate BOOLEAN,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Database Wrapper

The `Database` class provides a simple interface:

```python
from core.database import Database

db = Database("data/nexus.db")

# Execute query
db.execute("INSERT INTO conversations ...")

# Fetch results
results = db.fetch("SELECT * FROM conversations WHERE ...")

# Fetch one result
row = db.fetch_one("SELECT COUNT(*) FROM conversations")
```

### Connection Management

- Connections are opened lazily on first query
- Connections are reused (connection pooling)
- Connections are closed on application shutdown

### Migration

Database migrations are handled manually. When schema changes are needed:
1. Create a migration script
2. Run the script before starting NEXUS
3. Update the schema documentation

---

## 29. EVENT BUS

### Overview

The Event Bus (`agents/communication_bus_agent/event_bus.py`) provides a thread-safe publish/subscribe messaging system for inter-agent communication.

### Architecture

```
Publisher ──→ EventBus ──→ Subscriber 1
                         ──→ Subscriber 2
                         ──→ Subscriber 3 (once)
                         ──→ Subscriber 4 (conditional)
```

### Features

- **Thread-safe** — Uses `threading.Lock` for all operations
- **Async support** — Subscribers can be sync or async functions
- **Pattern matching** — Wildcard patterns for event filtering
- **Priority dispatching** — Subscribers are called in priority order
- **Once subscriptions** — Auto-unsubscribe after first event
- **Conditional subscriptions** — Only fire when condition is met

### Subscribing to Events

```python
# Basic subscription
bus.subscribe("file.created", on_file_created)

# Async subscription
bus.subscribe_async("web.search_complete", on_search_complete)

# One-time subscription
bus.subscribe_once("task.completed", on_task_completed)

# Conditional subscription
bus.subscribe_conditional(
    "agent.error",
    on_critical_error,
    condition=lambda event: event.severity == "critical"
)

# Pattern matching (wildcards)
bus.subscribe("file.*", on_any_file_event)      # file.created, file.deleted, etc.
bus.subscribe("*.error", on_any_error)           # agent.error, task.error, etc.
```

### Publishing Events

```python
# Synchronous publish (waits for all subscribers)
bus.publish("file.created", data={"path": "/tmp/test.txt"})

# Async publish (fire and forget)
await bus.publish_async("web.search_complete", data={"results": [...]})
```

### Event Structure

```python
@dataclass
class BusMessage:
    event_type: str
    data: dict
    priority: MessagePriority
    timestamp: datetime
    source: str
    message_id: str
```

### Message Priorities

| Priority | Value | Use Case |
|----------|-------|----------|
| `CRITICAL` | 0 | System failures, security alerts |
| `HIGH` | 1 | User-facing errors, task failures |
| `NORMAL` | 2 | Regular events, task completions |
| `LOW` | 3 | Background tasks, analytics |
| `BACKGROUND` | 4 | Logging, metrics collection |

### Unsubscribing

```python
# Unsubscribe by handler reference
bus.unsubscribe("file.created", on_file_created)

# Unsubscribe all for an event
bus.unsubscribe_all("file.created")

# Unsubscribe all events for a subscriber
bus.unsubscribe_subscriber(on_file_created)
```

### Thread Safety

The event bus uses a `ThreadPoolExecutor` for dispatching events to subscribers:

```python
with self._lock:
    subscribers = self._subscribers.get(event_type, [])

with ThreadPoolExecutor(max_workers=len(subscribers)) as executor:
    futures = [executor.submit(sub, event) for sub in subscribers]
    for future in as_completed(futures):
        future.result()  # Raises exception if subscriber failed
```

---

## 30. MESSAGE BROKER

### Overview

The Message Broker (`agents/communication_bus_agent/message_broker.py`) provides priority-queued message delivery with retry logic and dead letter handling.

### Features

- **Priority queue** — Messages are dequeued by priority (CRITICAL first)
- **Dead letter queue** — Failed messages are moved to DLQ after max retries
- **Message tracking** — Every message has delivery status tracking
- **Auto-retry** — Failed messages are retried with exponential backoff
- **Auto-cleanup** — Expired messages are automatically removed

### Message Lifecycle

```
PENDING → QUEUED → DELIVERED → ACKNOWLEDGED
                ↓
              FAILED → RETRYING → QUEUED (retry)
                ↓
              EXPIRED → Dead Letter Queue
```

### Delivery Status

| Status | Description |
|--------|-------------|
| `PENDING` | Message created, not yet queued |
| `QUEUED` | Message in priority queue |
| `DELIVERED` | Message sent to subscriber |
| `ACKNOWLEDGED` | Subscriber confirmed receipt |
| `FAILED` | Delivery failed |
| `RETRYING` | Message being retried |
| `EXPIRED` | Message TTL exceeded |

### Sending Messages

```python
broker.send(
    event_type="task.completed",
    data={"task_id": "123", "result": "..."},
    priority=MessagePriority.NORMAL,
    ttl=300  # 5 minutes
)
```

### Receiving Messages

```python
# Blocking receive (waits for message)
message = broker.receive(timeout=10)

# Non-blocking receive
message = broker.receive_nowait()

# Acknowledge receipt
broker.acknowledge(message.message_id)
```

### Dead Letter Queue

Messages that fail after max retries are moved to the DLQ:

```python
dlq = broker.get_dead_letter_queue()
for message in dlq:
    print(f"Failed: {message.event_type} - {message.error}")
```

DLQ capacity: 1000 messages (oldest are dropped when full).

### Auto-Retry Loop

The broker runs a background thread that retries failed messages every 30 seconds:

```python
def _retry_loop(self):
    while self._running:
        for message in self._get_failed_messages():
            if message.retry_count < message.max_retries:
                message.retry_count += 1
                message.status = DeliveryStatus.QUEUED
                self._queue.put(message)
        time.sleep(30)
```

### Auto-Cleanup Loop

Expired messages are cleaned up every 120 seconds:

```python
def _cleanup_loop(self):
    while self._running:
        self._remove_expired_messages()
        time.sleep(120)
```

---

## 31. SHARED STATE MANAGER

### Overview

The Shared State Manager (`agents/communication_bus_agent/shared_state.py`) provides a thread-safe key-value store for inter-agent data sharing.

### Features

- **Thread-safe** — Uses `threading.Lock` for all operations
- **Optimistic concurrency** — Version checking prevents lost updates
- **TTL expiration** — Entries can expire automatically
- **Namespace isolation** — Separate key spaces per namespace
- **Change listeners** — Callbacks on value changes
- **Lock/unlock** — Explicit locking for critical sections

### Basic Operations

```python
# Set a value
state_manager.set("user.preferences.theme", "dark")

# Get a value
theme = state_manager.get("user.preferences.theme")

# Delete a value
state_manager.delete("user.preferences.theme")

# Check if key exists
if state_manager.exists("user.preferences.theme"):
    ...
```

### Namespaces

```python
# Default namespace
state_manager.set("key", "value")

# Custom namespace
state_manager.set("key", "value", namespace="agent_config")
state_manager.get("key", namespace="agent_config")
```

### TTL (Time-To-Live)

```python
# Entry expires after 60 seconds
state_manager.set("session.token", "abc123", ttl=60)

# Check if entry is expired
if state_manager.is_expired("session.token"):
    state_manager.delete("session.token")
```

### Optimistic Concurrency

```python
# Get current version
entry = state_manager.get_entry("counter")
current_version = entry.version

# Update with version check (fails if version changed)
success = state_manager.set("counter", 42, expected_version=current_version)
if not success:
    # Someone else updated, retry
    ...
```

### Lock/Unlock

```python
# Acquire lock
state_manager.lock("critical_resource")
try:
    # Critical section
    value = state_manager.get("critical_resource")
    state_manager.set("critical_resource", value + 1)
finally:
    state_manager.unlock("critical_resource")
```

### Change Listeners

```python
def on_theme_change(key, old_value, new_value):
    print(f"Theme changed from {old_value} to {new_value}")

state_manager.add_listener("user.preferences.theme", on_theme_change)
```

---

## 32. EVENT LOGGER

### Overview

The Event Logger (`agents/communication_bus_agent/event_logger.py`) provides persistent event logging with real-time streaming and analytics.

### Features

- **In-memory buffer** — Deque with 5000 max capacity for fast access
- **Persistent storage** — Events are saved to `data/nexus.db`
- **Real-time streaming** — Listeners receive events as they occur
- **Analytics** — Communication flow analysis, timeline generation
- **Filtering** — Query events by type, time range, source

### Logging Events

```python
logger.log(
    event_type="agent.started",
    data={"agent": "file_agent", "command": "list files"},
    source="ai_manager"
)
```

### Streaming Events

```python
def on_event(event):
    print(f"[{event.timestamp}] {event.event_type}: {event.data}")

logger.add_stream_listener(on_event)
```

### Querying Events

```python
# Get all events
events = logger.get_events()

# Filter by type
events = logger.get_events(event_type="agent.*")

# Filter by time range
events = logger.get_events(
    start_time=datetime.now() - timedelta(hours=1),
    end_time=datetime.now()
)

# Get event count
count = logger.get_event_count()
```

### Analytics

```python
# Communication flow analysis
flow = logger.get_communication_flow()
# Returns: {event_type: count} for each event type

# Timeline generation
timeline = logger.get_timeline()
# Returns: chronological list of events with metadata
```

### Buffer Management

The in-memory buffer is a deque with max 5000 entries:

```python
self._buffer = deque(maxlen=5000)
```

When the buffer is full, the oldest entries are automatically dropped. Persistent storage retains all events.

---

## 33. INTER-AGENT COMMUNICATION

### Overview

Agents communicate through the Communication Bus Agent using three mechanisms:
1. **Event Bus** — Publish/subscribe for notifications
2. **Message Broker** — Priority-queued messages with delivery guarantees
3. **Shared State** — Key-value store for shared data

### Communication Patterns

#### Request-Response

```python
# Agent A sends a request
bus.publish("file.list_request", data={"path": "/tmp"}, priority=HIGH)

# Agent B responds
bus.subscribe("file.list_request", handle_list_request)

def handle_list_request(event):
    files = list_files(event.data["path"])
    bus.publish("file.list_response", data={"files": files})
```

#### Event Broadcasting

```python
# Any agent can broadcast an event
bus.publish("task.completed", data={"task_id": "123"})

# Multiple agents can listen
bus.subscribe("task.completed", notify_user)
bus.subscribe("task.completed", update_analytics)
bus.subscribe("task.completed", trigger_learning)
```

#### Shared Data

```python
# Agent A writes to shared state
state.set("workflow.current_step", "file_analysis")

# Agent B reads from shared state
current_step = state.get("workflow.current_step")
```

### Message Types

| Type | Purpose |
|------|---------|
| `REQUEST` | Request data or action from another agent |
| `RESPONSE` | Reply to a request |
| `EVENT` | Notify about something that happened |
| `COMMAND` | Instruct another agent to do something |
| `NOTIFICATION` | Informational message |
| `ERROR` | Report an error |
| `HEARTBEAT` | Health check signal |
| `BROADCAST` | Message to all agents |

### Communication Flow Example

A multi-agent workflow for "analyze my codebase and create a report":

```
1. User → Router → Planner Agent
2. Planner → Event Bus → "plan.created" event
3. File Agent ← subscribes to "plan.created"
4. File Agent → reads files → Event Bus → "files.analyzed"
5. Coding Agent ← subscribes to "files.analyzed"
6. Coding Agent → analyzes code → Event Bus → "code.analyzed"
7. Analytics Agent ← subscribes to "code.analyzed"
8. Analytics Agent → generates report → Event Bus → "report.generated"
9. Notification Agent ← subscribes to "report.generated"
10. Notification Agent → notifies user
```

---

## 34. WORKFLOW ENGINE

### Overview

The Workflow Agent (`agents/workflow_agent/`) manages user-defined workflows — sequences of commands that can be saved, edited, and executed as a unit.

### What Is a Workflow

A workflow is a named sequence of steps, where each step is a command executed by a specific agent. Workflows can be:
- **Linear** — Steps execute in order
- **Conditional** — Steps execute based on conditions
- **Reusable** — Saved workflows can be run multiple times

### Workflow Structure

```json
{
  "id": "workflow-001",
  "name": "Code Review",
  "description": "Analyze code, check for issues, generate report",
  "steps": [
    {
      "agent": "file_agent",
      "command": "list files",
      "order": 1
    },
    {
      "agent": "coding_agent",
      "command": "analyze code quality",
      "order": 2
    },
    {
      "agent": "analytics_agent",
      "command": "generate report",
      "order": 3
    }
  ],
  "status": "active"
}
```

### Workflow Commands

| Command | Description |
|---------|-------------|
| `create workflow` | Create a new workflow |
| `list workflows` | List all saved workflows |
| `run workflow <name>` | Execute a workflow |
| `edit workflow <name>` | Modify a workflow |
| `delete workflow <name>` | Remove a workflow |
| `workflow status` | Show workflow execution status |

### Workflow Statuses

| Status | Description |
|--------|-------------|
| `draft` | Workflow is being edited |
| `active` | Workflow is ready to run |
| `running` | Workflow is currently executing |
| `completed` | Workflow finished successfully |
| `failed` | Workflow encountered an error |
| `paused` | Workflow is paused |

---

## 35. WORKFLOW CHAINS

### Overview

The Workflow Chain Agent (`agents/workflow_chain_agent/`) manages complex multi-agent execution chains with dependency tracking and error handling.

### Chain Structure

A workflow chain is a directed graph of agent executions:

```
User Request
    ↓
[File Agent] → Read files
    ↓
[Coding Agent] → Analyze code
    ↓
[Analytics Agent] → Generate metrics
    ↓
[Notification Agent] → Send report
```

### Chain Execution

1. **Define Chain** — User or Planner Agent creates a chain
2. **Validate** — Check that all agents exist and commands are valid
3. **Execute** — Run steps in order (respecting dependencies)
4. **Monitor** — Track progress of each step
5. **Handle Errors** — Retry failed steps or replan

### Chain Commands

| Command | Description |
|---------|-------------|
| `create chain` | Create a new workflow chain |
| `list chains` | List all chains |
| `run chain <name>` | Execute a chain |
| `chain status` | Show chain execution status |
| `cancel chain <name>` | Cancel a running chain |

### Error Handling in Chains

If a step fails:
1. **Retry** — The step is retried (up to 3 times)
2. **Fallback** — An alternative command is tried
3. **Skip** — The step is skipped (if marked as optional)
4. **Abort** — The entire chain is aborted

---

## 36. PLANNING ENGINE

### Overview

The Planning Engine (`agents/planner_agent/planning_engine.py`) is the core of autonomous multi-agent orchestration. It decomposes goals into task chains, executes them, monitors progress, and replans when necessary.

### Lifecycle

```
Create → Decompose → Execute → Monitor → Replan → Complete
```

### Planning Process

1. **Goal Input** — User provides a goal (e.g., "prepare for my Python exam")
2. **Template Matching** — Check if a built-in template matches the goal
3. **Decomposition** — Break the goal into subtasks with dependencies
4. **Agent Assignment** — Assign each subtask to the appropriate agent
5. **Execution** — Run tasks respecting dependency order
6. **Monitoring** — Track progress, detect failures
7. **Replanning** — If conditions change, regenerate the plan
8. **Completion** — Report results to the user

### Plan Structure

```python
@dataclass
class Plan:
    id: str
    name: str
    goal: str
    status: PlanStatus  # DRAFT, ACTIVE, PAUSED, COMPLETED, FAILED, CANCELLED
    tasks: list[PlanTask]
    progress: float  # 0.0 to 1.0
    created_at: datetime
    updated_at: datetime
```

### Task Structure

```python
@dataclass
class PlanTask:
    id: str
    plan_id: str
    description: str
    status: TaskStatus  # PENDING, QUEUED, RUNNING, COMPLETED, FAILED, SKIPPED, BLOCKED, RETRYING
    dependencies: list[str]  # Task IDs that must complete first
    agent_name: str
    order_index: int
    result: str | None
    error: str | None
```

### Plan Commands

| Command | Description |
|---------|-------------|
| `create plan <goal>` | Create a new plan for a goal |
| `list plans` | List all plans |
| `run plan <name>` | Execute a plan |
| `pause plan <name>` | Pause a running plan |
| `resume plan <name>` | Resume a paused plan |
| `cancel plan <name>` | Cancel a plan |
| `plan status <name>` | Show plan details and progress |

---

## 37. GOAL DECOMPOSITION

### Overview

The Goal Decomposer (`agents/planner_agent/goal_decomposition.py`) breaks high-level goals into executable tasks using a 3-tier approach.

### 3-Tier Decomposition

```
Goal → Template Matching → Rule-Based → LLM Fallback
```

#### Tier 1: Template Matching

Built-in templates for common goal types:

| Template | Goal Pattern | Tasks Generated |
|----------|-------------|-----------------|
| `exam_preparation` | "prepare for exam", "study for test" | Gather materials, create study plan, practice questions, review weak areas |
| `coding_project` | "build app", "create project" | Plan architecture, set up repo, implement features, test, deploy |
| `meeting_prep` | "prepare for meeting" | Gather agenda, review notes, prepare presentation, send reminders |
| `system_cleanup` | "clean up system", "optimize" | Analyze disk usage, remove temp files, optimize settings, report |
| `research_task` | "research", "learn about" | Define scope, gather sources, analyze, synthesize, report |
| `writing_session` | "write", "draft" | Outline, research, write sections, review, finalize |

#### Tier 2: Rule-Based Decomposition

If no template matches, apply heuristic rules:
- Parse goal for keywords (create, analyze, search, build, etc.)
- Map keywords to agent capabilities
- Generate tasks based on keyword-agent mapping

#### Tier 3: LLM Fallback

If rule-based decomposition fails, use the LLM:

```python
prompt = f"""
Decompose this goal into executable tasks:
Goal: {goal}

Available agents: {agent_descriptions}

Return a list of tasks with agent assignments and dependencies.
"""
```

### Decomposition Output

```json
{
  "goal": "Prepare for my Python exam",
  "template": "exam_preparation",
  "tasks": [
    {
      "description": "Gather study materials",
      "agent": "web_agent",
      "dependencies": []
    },
    {
      "description": "Create study schedule",
      "agent": "scheduler_agent",
      "dependencies": ["task-1"]
    },
    {
      "description": "Generate practice questions",
      "agent": "coding_agent",
      "dependencies": ["task-1"]
    },
    {
      "description": "Review weak areas",
      "agent": "knowledge_agent",
      "dependencies": ["task-2", "task-3"]
    }
  ]
}
```

---

## 38. DEPENDENCY GRAPH

### Overview

The Dependency Graph (`agents/planner_agent/dependency_graph.py`) is a Directed Acyclic Graph (DAG) that manages task ordering, detects cycles, and identifies parallel execution opportunities.

### Features

- **Topological sort** — Determine execution order
- **Cycle detection** — Prevent infinite loops
- **Parallel levels** — Identify tasks that can run simultaneously
- **Ready/blocked detection** — Know which tasks can start now

### Graph Construction

```python
graph = DependencyGraph()

# Add tasks
graph.add_task("task-1", "Gather materials")
graph.add_task("task-2", "Create schedule")
graph.add_task("task-3", "Generate questions")
graph.add_task("task-4", "Review weak areas")

# Add dependencies
graph.add_dependency("task-2", "task-1")  # task-2 depends on task-1
graph.add_dependency("task-3", "task-1")  # task-3 depends on task-1
graph.add_dependency("task-4", "task-2")  # task-4 depends on task-2
graph.add_dependency("task-4", "task-3")  # task-4 depends on task-3
```

### Execution Levels

The graph computes parallel execution levels:

```
Level 0: [task-1]          ← No dependencies, can start immediately
Level 1: [task-2, task-3]  ← Both depend only on task-1, can run in parallel
Level 2: [task-4]          ← Depends on task-2 and task-3
```

### Cycle Detection

```python
if graph.has_cycle():
    raise CycleError("Task dependencies contain a cycle")
```

### Ready Tasks

```python
# Get tasks that can start now (all dependencies completed)
ready_tasks = graph.get_ready_tasks(completed=["task-1"])
# Returns: ["task-2", "task-3"]
```

### Blocked Tasks

```python
# Get tasks that are blocked by incomplete dependencies
blocked_tasks = graph.get_blocked_tasks(completed=[])
# Returns: ["task-2", "task-3", "task-4"]
```

---

## 39. TASK EXECUTOR

### Overview

The Task Executor (`agents/planner_agent/task_executor.py`) handles parallel task execution with dependency-respecting scheduling, retry logic, and variable passing between tasks.

### Features

- **Parallel execution** — ThreadPoolExecutor with configurable max workers (default: 3)
- **Dependency scheduling** — Tasks only start when dependencies are met
- **Retry logic** — Failed tasks are retried with fallback commands
- **Variable passing** — Task results can be passed to subsequent tasks via `{{variable}}` substitution

### Execution Flow

```python
executor = TaskExecutor(max_workers=3)

# Execute a plan
result = executor.execute_plan(plan)

# Result includes:
# - Overall success/failure
# - Per-task results
# - Variables passed between tasks
# - Execution timeline
```

### Variable Passing

Tasks can reference results from previous tasks:

```json
{
  "tasks": [
    {
      "description": "List files in {{directory}}",
      "agent": "file_agent",
      "variables": {"directory": "/tmp"}
    },
    {
      "description": "Analyze {{file_count}} files",
      "agent": "coding_agent",
      "variables": {"file_count": "{{task-1.file_count}}"}
    }
  ]
}
```

Variables are substituted before task execution:
- `{{task-1.file_count}}` → Value from task-1's result
- `{{directory}}` → Static variable defined in the task

### Retry Logic

```python
# Default: 3 retries with fallback commands
task = PlanTask(
    description="Analyze code",
    agent="coding_agent",
    max_retries=3,
    fallback_commands=["scan code", "review code"]
)
```

If the primary command fails:
1. Retry with the same command (up to `max_retries`)
2. Try fallback commands in order
3. Mark as failed if all attempts fail

---

## 40. ASYNC EXECUTION MODEL

### Overview

NEXUS uses asynchronous execution throughout the system to ensure the UI never blocks and tasks run efficiently in parallel.

### Async Layers

| Layer | Technology | Purpose |
|-------|------------|---------|
| UI | Textual (asyncio) | Non-blocking UI updates |
| Agent Execution | asyncio | Parallel agent execution |
| LLM Calls | async OpenAI/Ollama | Streaming responses |
| Event Bus | ThreadPoolExecutor | Parallel subscriber dispatch |
| Task Dispatcher | asyncio | Concurrent task execution |
| File I/O | asyncio/threading | Non-blocking file operations |

### Async Agent Execution

```python
async def handle_request(self, user_input: str) -> dict:
    # Router determines agent (sync)
    agent = self.router.route(user_input, self.command_index)
    
    # Agent executes (async)
    result = await agent.execute(user_input)
    
    return result
```

### Background Tasks

Tasks run in the background without blocking the UI:

```python
async def run_background_task(self):
    while True:
        await self._check_scheduled_tasks()
        await asyncio.sleep(60)  # Check every minute
```

### Concurrency Limits

Maximum concurrent tasks are configurable:

```json
{
  "agents": {
    "max_concurrent_tasks": 5
  }
}
```

The dispatcher respects this limit by using a semaphore:

```python
self._semaphore = asyncio.Semaphore(max_concurrent_tasks)

async def execute_task(self, task):
    async with self._semaphore:
        return await task.agent.execute(task.command)
```

### Thread Safety

Where threading is used (event bus, message broker, shared state), proper synchronization is implemented:

- `threading.Lock` for mutual exclusion
- `threading.RLock` for reentrant locking
- `queue.Queue` for thread-safe message passing
- `concurrent.futures.ThreadPoolExecutor` for parallel execution

---

## 41. CONTEXT AWARENESS

### Overview

The Context Awareness Agent (`agents/context_awareness_agent/`) monitors user activity, detects focus levels, identifies workflows, and triggers adaptive automation.

### Components

| Component | File | Purpose |
|-----------|------|---------|
| `ContextAwarenessAgent` | `agent.py` | Main agent with 24+ command handlers |
| `ActivityClassifier` | `services.py` | Maps apps to activity categories |
| `ContextDetector` | `services.py` | Detects active window, running apps, system load |
| `WorkflowDetector` | `services.py` | Matches activity patterns to known workflows |
| `AdaptiveTriggerSystem` | `services.py` | Automates actions based on context |
| `ContextHistory` | `services.py` | Tracks sessions and productivity |

### Activity Categories

The ActivityClassifier maps applications to 10 categories:

| Category | Example Apps |
|----------|-------------|
| `coding` | VS Code, PyCharm, Vim, Terminal |
| `browsing` | Chrome, Firefox, Safari, Edge |
| `gaming` | Steam, Epic Games, game executables |
| `media` | Spotify, VLC, YouTube (browser) |
| `communication` | Slack, Discord, Teams, Outlook |
| `writing` | Word, Google Docs, Notion |
| `design` | Figma, Photoshop, Illustrator |
| `file_management` | File Explorer, Finder |
| `system_admin` | Task Manager, System Monitor |
| `other` | Anything not categorized |

### Focus Levels

The ContextDetector calculates focus level based on active window, running apps, and system load:

| Level | Description | Indicators |
|-------|-------------|------------|
| `deep` | Fully immersed in work | Single coding app, no distractions |
| `focused` | Concentrated on task | Primary work app, minimal distractions |
| `moderate` | Some distractions | Mix of work and non-work apps |
| `distracted` | High distraction level | Multiple non-work apps, gaming, social media |
| `idle` | No activity detected | No active window, low system load |

### Workflow Patterns

7 built-in workflow patterns:

| Pattern | Trigger Conditions |
|---------|-------------------|
| `Coding Session` | Active window is IDE, coding apps running |
| `Study Session` | Browser with educational sites, document apps |
| `Gaming Session` | Game app active, gaming category |
| `Meeting` | Video conferencing app active |
| `Content Creation` | Design/video editing apps active |
| `Deep Work` | Single app, high focus level, extended duration |
| `Research` | Browser with multiple tabs, note-taking apps |

### Adaptive Triggers

6 default triggers:

| Trigger | Condition | Action |
|---------|-----------|--------|
| `Gaming Silence` | Gaming detected, no audio | Suggest Do Not Disturb |
| `Coding Suggestion` | Coding session > 2 hours | Suggest break |
| `Study Mode` | Study session detected | Block distracting sites |
| `Meeting Focus` | Meeting detected | Silence notifications |
| `Deep Work Evening` | Deep work after 6 PM | Suggest wind-down |
| `Idle Cleanup` | Idle > 30 minutes | Suggest system cleanup |

### Context Commands

| Command | Description |
|---------|-------------|
| `current context` | Show full context snapshot |
| `active window` | Show current active window |
| `running apps` | List running applications |
| `activity type` | Show classified activity type |
| `focus level` | Show current focus level |
| `system load` | Show CPU/memory usage |
| `suggest workflow` | Suggest workflow based on context |
| `suggest actions` | Suggest adaptive actions |
| `start monitoring` | Start context monitoring |
| `stop monitoring` | Stop context monitoring |
| `workflow patterns` | List known workflow patterns |
| `detect workflow` | Detect current workflow |
| `triggers` | List adaptive triggers |
| `add trigger` | Add a new trigger |
| `toggle trigger` | Enable/disable a trigger |
| `context history` | Show context history |
| `activity summary` | Show activity summary |
| `session start` | Start a new session |
| `session end` | End current session |
| `context rules` | List context rules |
| `add rule` | Add a context rule |
| `delete rule` | Remove a context rule |
| `cleanup` | Clean up old context data |

### Database

Context data is stored in `data/context.db` with 5 tables:
- `context_snapshots` — Historical context data
- `context_patterns` — Workflow patterns
- `adaptive_triggers` — Trigger definitions
- `context_sessions` — Session records with productivity scores
- `context_rules` — User-defined rules

---

## 42. ACTIVITY CLASSIFICATION

### Overview

The ActivityClassifier (`agents/context_awareness_agent/services.py`) maps running applications to activity categories using pattern matching on window titles and process names.

### Classification Process

1. **Get Active Window** — Uses `pygetwindow` (Windows) or `ctypes` to get the active window title
2. **Get Running Apps** — Uses `psutil` to enumerate running processes
3. **Pattern Match** — Matches window titles and process names against known patterns
4. **Return Category** — Returns the most likely activity category

### Pattern Examples

```python
CODING_PATTERNS = ["vscode", "pycharm", "vim", "terminal", "code", "sublime"]
BROWSING_PATTERNS = ["chrome", "firefox", "safari", "edge", "brave"]
GAMING_PATTERNS = ["steam", "epic", "unity", "unreal", "game"]
```

### Confidence Scoring

The classifier returns a confidence score (0.0–1.0):

```python
result = classifier.classify(active_window="Visual Studio Code", running_apps=["code", "node"])
# Returns: {"category": "coding", "confidence": 0.95}
```

---

## 43. FOCUS DETECTION

### Overview

Focus detection calculates the user's focus level based on multiple signals.

### Signals

| Signal | Weight | Source |
|--------|--------|--------|
| Active window category | 40% | ActivityClassifier |
| Running app mix | 25% | psutil process list |
| System load | 15% | psutil CPU/memory |
| Time of day | 10% | System clock |
| Session duration | 10% | ContextHistory |

### Calculation

```python
def calculate_focus_level(active_window_category, running_apps, system_load, time_of_day, session_duration):
    score = 0
    
    # Active window weight (40%)
    if active_window_category == "coding":
        score += 0.4
    elif active_window_category == "browsing":
        score += 0.2
    elif active_window_category == "gaming":
        score += 0.0
    
    # Running app mix (25%)
    work_apps = sum(1 for app in running_apps if is_work_app(app))
    score += 0.25 * (work_apps / len(running_apps))
    
    # System load (15%)
    if system_load < 0.5:
        score += 0.15
    elif system_load < 0.8:
        score += 0.1
    
    # Time of day (10%)
    if 9 <= time_of_day.hour <= 17:
        score += 0.1
    
    # Session duration (10%)
    if session_duration > 30:  # minutes
        score += 0.1
    
    # Map score to focus level
    if score >= 0.8:
        return FocusLevel.DEEP
    elif score >= 0.6:
        return FocusLevel.FOCUSED
    elif score >= 0.4:
        return FocusLevel.MODERATE
    elif score >= 0.2:
        return FocusLevel.DISTRACTED
    else:
        return FocusLevel.IDLE
```

---

## 44. WORKFLOW DETECTION

### Overview

The WorkflowDetector (`agents/context_awareness_agent/services.py`) matches current activity patterns to known workflow templates.

### Detection Process

1. **Collect Context** — Get current context snapshot (active window, running apps, activity type)
2. **Match Patterns** — Compare against known workflow patterns
3. **Score Matches** — Calculate match confidence for each pattern
4. **Return Best Match** — Return the highest-confidence workflow (if above threshold)

### Pattern Matching

```python
def detect_workflow(context_snapshot):
    best_match = None
    best_score = 0
    
    for pattern in self.patterns:
        score = pattern.match(context_snapshot)
        if score > best_score and score >= self.threshold:
            best_score = score
            best_match = pattern
    
    return best_match
```

### Workflow Pattern Structure

```python
@dataclass
class ContextPattern:
    name: str
    description: str
    conditions: dict  # {"activity_type": "coding", "focus_level": "deep"}
    min_duration: int  # Minimum minutes to confirm
    actions: list[str]  # Suggested actions
```

---

## 45. ADAPTIVE TRIGGERS

### Overview

The AdaptiveTriggerSystem (`agents/context_awareness_agent/services.py`) automates actions based on context changes.

### Trigger Structure

```python
@dataclass
class AdaptiveTrigger:
    name: str
    condition: str  # Context condition to match
    action: str  # Action to take
    enabled: bool
    cooldown: int  # Minutes between triggers
    last_triggered: datetime | None
```

### Trigger Evaluation

Triggers are evaluated periodically (every 60 seconds by default):

```python
def evaluate_triggers(self, context_snapshot):
    for trigger in self.triggers:
        if not trigger.enabled:
            continue
        if trigger.is_on_cooldown():
            continue
        if trigger.matches(context_snapshot):
            trigger.execute()
            trigger.last_triggered = datetime.now()
```

### Adding Custom Triggers

```
> add trigger
Name: Coding Break Reminder
Condition: activity_type=coding AND session_duration>120
Action: Suggest taking a break
Cooldown: 60 minutes
```

---

## 46. LEARNING ENGINE

### Overview

The Learning Engine (`agents/learning_agent/services.py`) tracks user behavior, detects patterns, generates recommendations, and predicts next actions.

### Components

| Component | File | Purpose |
|-----------|------|---------|
| `LearningAgent` | `agent.py` | Main agent with 18 command handlers |
| `LearningEngine` | `services.py` | Core learning orchestration |
| `BehaviorTracker` | `services.py` | Records actions with context |
| `PatternAnalyzer` | `services.py` | Detects patterns (frequency, sequence, time, contextual) |
| `RecommendationEngine` | `services.py` | Generates personalized recommendations |
| `AdaptiveWorkflowGenerator` | `services.py` | Creates workflows from patterns |

### Learning Lifecycle

```
Record Behavior → Analyze Patterns → Generate Recommendations → User Feedback → Update Model
```

### Pattern Types

| Type | Description | Example |
|------|-------------|---------|
| `frequency` | Actions that occur often | "You run tests 15 times/day" |
| `sequence` | Actions that occur in order | "You always open file → edit → save" |
| `time_based` | Actions at specific times | "You check email at 9 AM daily" |
| `contextual` | Actions in specific contexts | "You use web search when coding" |

### Pattern Lifecycle

Patterns progress through a confidence lifecycle:

```
OBSERVING → LEARNING → CONFIRMED → ACTIVE
```

| Stage | Min Occurrences | Description |
|-------|----------------|-------------|
| `OBSERVING` | 1–2 | Pattern detected, gathering data |
| `LEARNING` | 3–5 | Pattern is emerging, building confidence |
| `CONFIRMED` | 6–10 | Pattern is reliable, ready for recommendations |
| `ACTIVE` | 10+ | Pattern is confirmed, used for predictions |

---

## 47. BEHAVIOR TRACKING

### Overview

The BehaviorTracker (`agents/learning_agent/services.py`) records every action with its preceding context.

### Record Structure

```python
@dataclass
class BehaviorRecord:
    id: str
    action: str  # What the user did
    preceding_actions: list[str]  # What happened before
    context: dict  # Activity type, focus level, time, etc.
    timestamp: datetime
```

### Recording Actions

```python
tracker.record(
    action="run tests",
    preceding_actions=["open file", "edit code", "save file"],
    context={
        "activity_type": "coding",
        "focus_level": "deep",
        "time_of_day": 14,
        "day_of_week": "Monday"
    }
)
```

### Frequency Tracking

The tracker maintains frequency counts:

```python
# How often each action occurs
frequency = tracker.get_action_frequency()
# Returns: {"run tests": 15, "open file": 42, ...}

# Hourly patterns
hourly = tracker.get_hourly_pattern("run tests")
# Returns: {9: 2, 10: 5, 14: 8, ...}

# Daily patterns
daily = tracker.get_daily_pattern("run tests")
# Returns: {"Monday": 5, "Tuesday": 3, ...}
```

---

## 48. PATTERN ANALYSIS

### Overview

The PatternAnalyzer (`agents/learning_agent/services.py`) detects patterns from behavior records.

### Frequency Patterns

```python
patterns = analyzer.detect_frequency_patterns(records)
# Returns: LearnedPattern(
#   type="frequency",
#   action="run tests",
#   frequency=15,
#   confidence=0.85,
#   status="confirmed"
# )
```

### Sequence Patterns

```python
patterns = analyzer.detect_sequence_patterns(records)
# Returns: LearnedPattern(
#   type="sequence",
#   sequence=["open file", "edit code", "save file", "run tests"],
#   confidence=0.92,
#   status="active"
# )
```

### Time-Based Patterns

```python
patterns = analyzer.detect_time_based_patterns(records)
# Returns: LearnedPattern(
#   type="time_based",
#   action="check email",
#   time_pattern={"hour": 9, "days": ["Monday", "Tuesday", ...]},
#   confidence=0.78,
#   status="confirmed"
# )
```

### Contextual Patterns

```python
patterns = analyzer.detect_contextual_patterns(records)
# Returns: LearnedPattern(
#   type="contextual",
#   action="search web",
#   context={"activity_type": "coding", "focus_level": "focused"},
#   confidence=0.70,
#   status="learning"
# )
```

### Auto-Promotion

Patterns are automatically promoted through the lifecycle:

```python
def _promote_pattern(self, pattern):
    if pattern.occurrences >= 10 and pattern.status == "confirmed":
        pattern.status = "active"
    elif pattern.occurrences >= 6 and pattern.status == "learning":
        pattern.status = "confirmed"
    elif pattern.occurrences >= 3 and pattern.status == "observing":
        pattern.status = "learning"
```

---

## 49. RECOMMENDATION ENGINE

### Overview

The RecommendationEngine (`agents/learning_agent/services.py`) generates personalized recommendations based on learned patterns.

### Recommendation Types

| Type | Description | Example |
|------|-------------|---------|
| `workflow` | Suggest a workflow | "Create a workflow for your daily routine" |
| `automation` | Suggest automation | "Automate your test running after saves" |
| `optimization` | Suggest optimization | "You could batch your email checking" |
| `habit` | Suggest habit formation | "Try coding at the same time each day" |
| `app_suggestion` | Suggest an app | "Consider using VS Code for Python" |

### Recommendation Structure

```python
@dataclass
class Recommendation:
    id: str
    type: str  # workflow, automation, optimization, habit, app_suggestion
    description: str
    confidence: float
    based_on: str  # Pattern that triggered this
    status: str  # pending, accepted, dismissed
    created_at: datetime
```

### Generating Recommendations

```python
recommendations = engine.generate_recommendations(patterns)
# Returns: [
#   Recommendation(
#     type="automation",
#     description="Auto-run tests when you save a file",
#     confidence=0.88,
#     based_on="sequence: edit → save → run tests"
#   ),
#   ...
# ]
```

### User Feedback

Users can accept or dismiss recommendations:

```
> accept recommendation 1
> dismiss recommendation 2
```

Accepted recommendations influence future recommendations. Dismissed ones are deprioritized.

---

## 50. PREDICTIVE ACTIONS

### Overview

The AdaptiveWorkflowGenerator (`agents/learning_agent/services.py`) predicts the user's next action and generates workflows from patterns.

### Next Action Prediction

```python
prediction = engine.predict_next_action(current_context)
# Returns: Prediction(
#   action="run tests",
#   confidence=0.82,
#   based_on=["edit code", "save file"],
#   time_relevance=0.9,
#   context_relevance=0.85
# )
```

### Prediction Scoring

Predictions are scored on:
- **Time relevance** — How likely is this action at the current time?
- **Context relevance** — How well does this action match the current context?
- **Pattern confidence** — How confident is the underlying pattern?

### Workflow Generation

```python
workflows = engine.generate_workflows_from_patterns(patterns)
# Returns: [
#   Workflow(
#     name="Morning Routine",
#     steps=[
#       {"agent": "file_agent", "command": "check inbox"},
#       {"agent": "scheduler_agent", "command": "show today's meetings"},
#       {"agent": "terminal_agent", "command": "run system health check"}
#     ]
#   ),
#   ...
# ]
```

### Daily Routine Generation

```python
routine = engine.generate_daily_routine()
# Returns a workflow based on the user's typical daily pattern
```

### Prediction Accuracy Tracking

```python
# Log prediction accuracy
engine.log_prediction(prediction, actual_action="run tests")
# Accuracy is tracked and reported in learning stats
```

### Learning Commands

| Command | Description |
|---------|-------------|
| `start learning` | Enable behavior tracking |
| `stop learning` | Disable behavior tracking |
| `analyze` | Analyze behavior and detect patterns |
| `patterns` | Show learned patterns |
| `habits` | Show detected habits |
| `recommendations` | Show recommendations |
| `accept recommendation <n>` | Accept a recommendation |
| `dismiss recommendation <n>` | Dismiss a recommendation |
| `predict` | Predict next action |
| `behavior history` | Show behavior history |
| `learning stats` | Show learning statistics |
| `generate workflow` | Generate workflow from patterns |
| `daily routine` | Generate daily routine |
| `most common` | Show most common actions |
| `hourly pattern` | Show hourly pattern for an action |
| `daily pattern` | Show daily pattern for an action |
| `prediction accuracy` | Show prediction accuracy |
| `cleanup` | Clean up old learning data |

---

## 51. MEMORY AGENT

### Overview

The Memory Agent (`agents/memory_agent/`) manages long-term memory, semantic search, and conversation history.

### Capabilities

- **Conversation Memory** — Stores and retrieves past conversations
- **Semantic Search** — Search memory by meaning, not just keywords
- **Fact Storage** — Store and retrieve facts
- **Context Recall** — Recall relevant context for current conversation

### Memory Commands

| Command | Description |
|---------|-------------|
| `save memory` | Save a fact or note to memory |
| `search memory` | Search memory semantically |
| `list memories` | List all stored memories |
| `delete memory` | Remove a memory |
| `recall` | Recall relevant memories for context |
| `memory stats` | Show memory statistics |

### Vector Storage

The Memory Agent uses vector embeddings for semantic search:
- Text is converted to embeddings using the LLM provider
- Embeddings are stored in the database
- Search queries are converted to embeddings and compared using cosine similarity

### Memory Structure

```python
@dataclass
class Memory:
    id: str
    content: str
    embedding: list[float]  # Vector embedding
    timestamp: datetime
    tags: list[str]
    importance: float  # 0.0 to 1.0
```

---

## 52. KNOWLEDGE AGENT

### Overview

The Knowledge Agent (`agents/knowledge_agent/`) manages a knowledge base of documents, articles, and reference material.

### Capabilities

- **Document Storage** — Store and organize documents
- **Knowledge Retrieval** — Search and retrieve relevant knowledge
- **Summarization** — Summarize documents
- **Cross-Reference** — Link related knowledge items

### Knowledge Commands

| Command | Description |
|---------|-------------|
| `add knowledge` | Add a document or note to knowledge base |
| `search knowledge` | Search the knowledge base |
| `list knowledge` | List all knowledge items |
| `summarize` | Summarize a knowledge item |
| `delete knowledge` | Remove a knowledge item |
| `knowledge stats` | Show knowledge base statistics |

### Knowledge Structure

```python
@dataclass
class KnowledgeItem:
    id: str
    title: str
    content: str
    source: str  # URL, file path, or manual entry
    tags: list[str]
    created_at: datetime
    updated_at: datetime
```

---

## 53. SEMANTIC SEARCH

### Overview

Semantic search finds results by meaning, not just keyword matching.

### How It Works

1. **Index** — All content is converted to vector embeddings
2. **Query** — Search query is converted to an embedding
3. **Compare** — Cosine similarity finds the most relevant results
4. **Rank** — Results are ranked by similarity score

### Similarity Calculation

```python
def cosine_similarity(a, b):
    dot_product = sum(x * y for x, y in zip(a, b))
    magnitude_a = math.sqrt(sum(x ** 2 for x in a))
    magnitude_b = math.sqrt(sum(x ** 2 for x in b))
    return dot_product / (magnitude_a * magnitude_b)
```

### Search Commands

Both Memory Agent and Knowledge Agent support semantic search:

```
> search memory "how do I run tests"
> search knowledge "Python async patterns"
```

---

## 54. VECTOR STORAGE

### Overview

Vector embeddings are stored in SQLite databases alongside the original text.

### Storage Strategy

```sql
CREATE TABLE memories (
    id TEXT PRIMARY KEY,
    content TEXT NOT NULL,
    embedding TEXT,  -- JSON array of floats
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    tags TEXT,
    importance REAL
);
```

Embeddings are stored as JSON arrays of floats:
```json
[0.123, -0.456, 0.789, ...]
```

### Performance Considerations

- Embedding generation requires an LLM call (slow)
- Embeddings are cached and reused
- Search is fast (cosine similarity on pre-computed vectors)
- For large datasets, consider a dedicated vector database

---

## 55. CONVERSATION HISTORY

### Overview

All conversations are persisted in `data/nexus.db` for future reference.

### Storage

```sql
CREATE TABLE conversations (
    id TEXT PRIMARY KEY,
    user_message TEXT NOT NULL,
    agent_response TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    agent_name TEXT,
    session_id TEXT
);
```

### Retrieval

```
> show conversations      # List recent conversations
> search conversations    # Search conversation history
```

### Session Management

Conversations are grouped by session:
- Each NEXUS launch creates a new session
- Sessions have a unique ID
- Conversations within a session share the same `session_id`

---

*Continue to Part VI: Productivity Tools →*

---

## 56. FILE AGENT

### Overview

The File Agent (`agents/file_agent/`) manages file system operations including browsing, searching, reading, writing, and organizing files.

### Capabilities

- **Directory Listing** — List files and directories
- **File Search** — Search for files by name, extension, or content
- **File Operations** — Read, write, copy, move, delete files
- **File Analysis** — Get file size, type, modification date
- **Directory Tree** — Visualize directory structure

### Commands

| Command | Description |
|---------|-------------|
| `list files` | List files in current directory |
| `search files <pattern>` | Search for files matching pattern |
| `read file <path>` | Read file contents |
| `write file <path>` | Write content to file |
| `copy file <src> <dest>` | Copy a file |
| `move file <src> <dest>` | Move a file |
| `delete file <path>` | Delete a file |
| `file info <path>` | Get file metadata |
| `directory tree` | Show directory tree |

### Safety Features

- **Confirmation** — Destructive operations (delete, overwrite) require confirmation
- **Path Validation** — Paths are validated to prevent directory traversal
- **Size Limits** — Large files are truncated to prevent memory issues

---

## 57. WEB AGENT

### Overview

The Web Agent (`agents/web_agent/`) handles web browsing, searching, and content extraction.

### Capabilities

- **Web Search** — Search the web using search engines
- **Content Extraction** — Extract text from web pages
- **URL Analysis** — Analyze URLs for safety and content type
- **Screenshot Capture** — Capture webpage screenshots (via Playwright)

### Commands

| Command | Description |
|---------|-------------|
| `search web <query>` | Search the web |
| `open url <url>` | Open and extract URL content |
| `summarize url <url>` | Summarize webpage content |
| `screenshot url <url>` | Capture webpage screenshot |

### Playwright Integration

The Web Agent uses Playwright for browser automation:
- Headless browser for content extraction
- JavaScript rendering for dynamic pages
- Screenshot capture for visual content

### Safety Features

- **URL Validation** — URLs are validated before access
- **Timeout** — Requests timeout after 30 seconds
- **Content Filtering** — Malicious content is detected and blocked

---

## 58. CODING AGENT

### Overview

The Coding Agent (`agents/coding_agent/`) assists with code analysis, generation, review, and debugging.

### Capabilities

- **Code Analysis** — Analyze code quality, complexity, and style
- **Code Generation** — Generate code from descriptions
- **Code Review** — Review code for issues and improvements
- **Debugging** — Help debug errors and exceptions
- **Refactoring** — Suggest and perform refactoring

### Commands

| Command | Description |
|---------|-------------|
| `analyze code` | Analyze code quality |
| `generate code <description>` | Generate code from description |
| `review code` | Review code for issues |
| `debug error <error>` | Help debug an error |
| `refactor code` | Suggest refactoring |
| `explain code` | Explain how code works |

### Language Support

The Coding Agent supports multiple programming languages:
- Python, JavaScript, TypeScript, Java, C++, C#, Go, Rust, Ruby, PHP, and more

### Analysis Metrics

- **Complexity** — Cyclomatic complexity of functions
- **Style** — PEP 8, ESLint, or language-specific style checks
- **Security** — Common vulnerability patterns
- **Performance** — Potential performance issues

---

## 59. AUTOMATION AGENT

### Overview

The Automation Agent (`agents/automation_agent/`) creates and manages automated tasks and scripts.

### Capabilities

- **Task Automation** — Automate repetitive tasks
- **Script Generation** — Generate automation scripts
- **Schedule Automation** — Schedule automated tasks
- **GUI Automation** — Automate GUI interactions (via pyautogui)

### Commands

| Command | Description |
|---------|-------------|
| `create automation` | Create a new automation |
| `list automations` | List all automations |
| `run automation <name>` | Execute an automation |
| `delete automation <name>` | Remove an automation |
| `schedule automation` | Schedule an automation |

### GUI Automation

The Automation Agent uses pyautogui for GUI automation:
- Mouse movement and clicking
- Keyboard input
- Screen region detection
- Image-based element recognition

### Safety Features

- **Dry Run** — Automations can be tested in dry-run mode
- **Confirmation** — Destructive automations require confirmation
- **Timeout** — Automations timeout after a configurable duration

---

## 60. SCHEDULER AGENT

### Overview

The Scheduler Agent (`agents/scheduler_agent/`) manages scheduled tasks and reminders.

### Capabilities

- **Task Scheduling** — Schedule tasks for specific times
- **Reminders** — Set reminders for events
- **Recurring Tasks** — Create recurring scheduled tasks
- **Calendar Integration** — Manage calendar events

### Commands

| Command | Description |
|---------|-------------|
| `schedule task` | Schedule a new task |
| `list tasks` | List scheduled tasks |
| `cancel task <id>` | Cancel a scheduled task |
| `set reminder` | Set a reminder |
| `list reminders` | List all reminders |
| `recurring task` | Create a recurring task |

### Schedule Types

| Type | Description | Example |
|------|-------------|---------|
| `one_time` | Runs once at specified time | "Remind me at 3 PM" |
| `daily` | Runs every day at specified time | "Daily standup at 9 AM" |
| `weekly` | Runs every week on specified day | "Weekly review on Friday" |
| `monthly` | Runs every month on specified date | "Monthly report on 1st" |
| `interval` | Runs at regular intervals | "Check email every 30 minutes" |

---

## 61. NOTIFICATION AGENT

### Overview

The Notification Agent (`agents/notification_agent/`) manages system notifications and alerts.

### Capabilities

- **System Notifications** — Display system notifications
- **Alert Management** — Manage alert priorities and delivery
- **Notification History** — Track sent notifications
- **Custom Notifications** — Create custom notification templates

### Commands

| Command | Description |
|---------|-------------|
| `send notification` | Send a notification |
| `list notifications` | List recent notifications |
| `clear notifications` | Clear all notifications |
| `notification settings` | Configure notification preferences |

### Notification Types

| Type | Description | Priority |
|------|-------------|----------|
| `info` | Informational message | Low |
| `warning` | Warning message | Medium |
| `error` | Error alert | High |
| `success` | Success confirmation | Low |
| `reminder` | Reminder notification | Medium |

### Delivery Methods

- **Terminal** — Display in terminal UI
- **System** — OS-level notification (if available)
- **Sound** — Audio alert (if configured)

---

## 62. TERMINAL AGENT

### Overview

The Terminal Agent (`agents/terminal_agent/`) executes shell commands and manages terminal sessions.

### Capabilities

- **Command Execution** — Run shell commands
- **Output Capture** — Capture command output
- **Session Management** — Manage terminal sessions
- **Environment Variables** — Get and set environment variables

### Commands

| Command | Description |
|---------|-------------|
| `run command <cmd>` | Execute a shell command |
| `terminal session` | Start a terminal session |
| `env list` | List environment variables |
| `env get <var>` | Get an environment variable |
| `env set <var> <val>` | Set an environment variable |

### Safety Features

- **Command Validation** — Dangerous commands are blocked or require confirmation
- **Timeout** — Commands timeout after 30 seconds
- **Output Limits** — Output is truncated if too large
- **Sandbox Mode** — Commands can be run in restricted mode

### Blocked Commands

By default, these commands require explicit confirmation:
- `rm -rf /` and similar destructive commands
- `format` and disk operations
- `sudo` commands with elevated privileges
- Network configuration changes

---

## 63. VISION AGENT

### Overview

The Vision Agent (`agents/vision_agent/`) handles image analysis, OCR, and visual content understanding.

### Capabilities

- **Image Analysis** — Analyze images and describe content
- **OCR** — Extract text from images
- **Screenshot Analysis** — Analyze screenshots
- **Image Generation** — Generate images from descriptions (if supported)

### Commands

| Command | Description |
|---------|-------------|
| `analyze image <path>` | Analyze an image |
| `ocr image <path>` | Extract text from image |
| `describe screenshot` | Analyze current screenshot |
| `generate image <description>` | Generate an image |

### Vision Model Support

The Vision Agent uses multimodal LLMs for image analysis:
- GPT-4 Vision (OpenAI)
- LLaVA (Ollama)
- Other vision-capable models

### Image Processing

- Supported formats: PNG, JPEG, GIF, BMP, WebP
- Maximum size: 10 MB per image
- Automatic resizing for large images

---

## 64. SECURITY AGENT

### Overview

The Security Agent (`agents/security_agent/`) monitors system security, detects threats, and manages security policies.

### Capabilities

- **Threat Detection** — Detect security threats
- **Vulnerability Scanning** — Scan for known vulnerabilities
- **Security Policies** — Manage security policies
- **Audit Logging** — Log security events
- **File Integrity** — Monitor file integrity

### Commands

| Command | Description |
|---------|-------------|
| `security scan` | Run a security scan |
| `threat list` | List detected threats |
| `security policies` | Show security policies |
| `audit log` | Show security audit log |
| `file integrity` | Check file integrity |

### Threat Categories

| Category | Description | Severity |
|----------|-------------|----------|
| `malware` | Malicious software detected | Critical |
| `vulnerability` | Known vulnerability found | High |
| `misconfiguration` | Security misconfiguration | Medium |
| `unauthorized_access` | Unauthorized access attempt | High |
| `data_exposure` | Sensitive data exposed | Medium |

### Security Events

Security events are logged to `data/nexus.db`:

```sql
CREATE TABLE security_events (
    id TEXT PRIMARY KEY,
    event_type TEXT NOT NULL,
    severity TEXT,
    description TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    resolved BOOLEAN DEFAULT FALSE
);
```

---

## 65. ANALYTICS AGENT

### Overview

The Analytics Agent (`agents/analytics_agent/`) collects and reports system metrics and usage analytics.

### Capabilities

- **System Metrics** — CPU, memory, disk, network usage
- **Usage Analytics** — Track agent usage, command frequency
- **Performance Reports** — Generate performance reports
- **Trend Analysis** — Identify trends over time

### Commands

| Command | Description |
|---------|-------------|
| `system status` | Show system status |
| `usage report` | Show usage analytics |
| `performance report` | Show performance metrics |
| `trend analysis` | Show trends over time |
| `analytics stats` | Show analytics statistics |

### Metrics Tracked

| Metric | Description |
|--------|-------------|
| `agent_calls` | Number of times each agent was called |
| `command_frequency` | Most frequently used commands |
| `response_times` | Average response time per agent |
| `error_rates` | Error rate per agent |
| `system_load` | CPU, memory, disk usage over time |
| `session_duration` | Average session duration |

### Analytics Events

Analytics events are logged to `data/nexus.db`:

```sql
CREATE TABLE analytics_events (
    id TEXT PRIMARY KEY,
    event_type TEXT NOT NULL,
    data TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## 66. PERSONALITY AGENT

### Overview

The Personality Agent (`agents/personality_agent/`) manages AI personality, tone, and communication style.

### Capabilities

- **Personality Profiles** — Pre-defined personality profiles
- **Custom Personality** — Create custom personality settings
- **Tone Adjustment** — Adjust communication tone
- **Style Learning** — Learn from user communication style

### Commands

| Command | Description |
|---------|-------------|
| `set personality` | Set AI personality |
| `list personalities` | List available personalities |
| `adjust tone` | Adjust communication tone |
| `personality info` | Show current personality |

### Personality Profiles

| Profile | Description |
|---------|-------------|
| `professional` | Formal, concise, business-appropriate |
| `friendly` | Warm, conversational, approachable |
| `technical` | Detailed, precise, jargon-friendly |
| `casual` | Relaxed, informal, conversational |
| `academic` | Scholarly, well-referenced, thorough |

### Tone Settings

| Tone | Description |
|------|-------------|
| `formal` | Professional and respectful |
| `neutral` | Balanced and objective |
| `casual` | Relaxed and friendly |
| `humorous` | Light-hearted and witty |

---

## 67. COMMUNICATION BUS AGENT

### Overview

The Communication Bus Agent (`agents/communication_bus_agent/`) is the central communication hub for inter-agent messaging. See Sections 29–33 for detailed documentation.

### Quick Reference

| Component | Purpose |
|-----------|---------|
| `EventBus` | Thread-safe pub/sub messaging |
| `MessageBroker` | Priority-queued message delivery |
| `SharedStateManager` | Thread-safe key-value store |
| `EventLogger` | Persistent event logging |

### Commands

| Command | Description |
|---------|-------------|
| `bus status` | Show bus status |
| `bus messages` | List recent messages |
| `bus subscriptions` | List active subscriptions |
| `bus shared state` | Show shared state entries |
| `bus events` | Show event log |
| `bus publish` | Publish a message |
| `bus subscribe` | Subscribe to an event |

---

## 68. MARKETPLACE AGENT

### Overview

The Marketplace Agent (`agents/marketplace_agent/`) enables browsing, installing, updating, and verifying community agents.

### Capabilities

- **Browse Agents** — Browse available community agents
- **Install Agents** — Install agents with dependency resolution
- **Update Agents** — Update installed agents
- **Verify Agents** — Security verification before installation
- **Review Agents** — Rate and review agents

### Marketplace API

The marketplace includes 10 seeded agents:

| Agent | Category | Description |
|-------|----------|-------------|
| `weather_agent` | PRODUCTIVITY | Weather forecasts and alerts |
| `email_agent` | COMMUNICATION | Email management and automation |
| `music_agent` | ENTERTAINMENT | Music control and recommendations |
| `git_agent` | DEVELOPMENT | Git operations and workflow |
| `calendar_agent` | PRODUCTIVITY | Calendar management and scheduling |
| `docker_agent` | DEVELOPMENT | Docker container management |
| `network_agent` | SYSTEM | Network diagnostics and monitoring |
| `translation_agent` | COMMUNICATION | Language translation |
| `database_agent` | ANALYTICS | Database query and management |
| `home_automation_agent` | AUTOMATION | Smart home device control |

### Agent Categories

| Category | Description |
|----------|-------------|
| `PRODUCTIVITY` | Productivity and organization tools |
| `DEVELOPMENT` | Development and coding tools |
| `AUTOMATION` | Automation and scripting tools |
| `COMMUNICATION` | Communication and messaging tools |
| `ANALYTICS` | Data analysis and reporting tools |
| `SECURITY` | Security and privacy tools |
| `ENTERTAINMENT` | Entertainment and media tools |
| `SYSTEM` | System administration tools |
| `AI_ML` | AI and machine learning tools |
| `UTILITIES` | General utility tools |

### Verification Process

The AgentVerifier performs 6 checks:

1. **Checksum** — Verify file integrity
2. **Signature** — Verify digital signature
3. **Security Scan** — AST analysis + regex pattern matching
4. **Dependency Check** — Verify all dependencies are available
5. **Compatibility Check** — Verify Python version and platform compatibility
6. **Sandbox Test** — Test execution in sandboxed environment

### Dangerous Import Detection

The security scanner detects 16 dangerous imports:
- `os`, `sys`, `subprocess`, `ctypes`, `socket`, `http`, `urllib`, `requests`, `ftplib`, `smtplib`, `shutil`, `pickle`, `marshal`, `importlib`, `compile`, `exec`

### Suspicious Pattern Detection

The scanner detects 17 suspicious patterns:
- `eval()`, `exec()`, `compile()`, `__import__()`, `getattr()`, `setattr()`, `delattr()`, `globals()`, `locals()`, `vars()`, `dir()`, `open()`, `input()`, `breakpoint()`, `memoryview()`, `super()`, `object`

### Installation Process

```
Download → Verify → Resolve Dependencies → Install → Activate
```

1. **Download** — Fetch agent package from marketplace
2. **Verify** — Run 6-check verification
3. **Resolve Dependencies** — Resolve and install dependencies
4. **Install** — Install to `installed_agents/<agent_name>/`
5. **Activate** — Register with AIManager

### Commands

| Command | Description |
|---------|-------------|
| `browse marketplace` | Browse available agents |
| `search marketplace <query>` | Search marketplace |
| `install agent <name>` | Install an agent |
| `update agent <name>` | Update an installed agent |
| `uninstall agent <name>` | Remove an installed agent |
| `list installed` | List installed agents |
| `verify agent <name>` | Verify an agent's security |
| `agent info <name>` | Show agent details |
| `review agent` | Rate and review an agent |

---

## 69. PLUGIN AGENT

### Overview

The Plugin Agent (`agents/plugin_agent/`) manages plugin lifecycle: discovery, loading, enabling, disabling, and execution.

### Plugin Architecture

Plugins are lightweight extensions that add commands or services to NEXUS without requiring a full agent.

### Plugin Types

| Type | Description |
|------|-------------|
| `COMMAND` | Adds new commands to NEXUS |
| `SERVICE` | Provides a background service |
| `HOOK` | Hooks into system events |
| `AGENT` | Extends agent capabilities |
| `UI` | Adds UI components |
| `MIDDLEWARE` | Intercepts and modifies requests |
| `EXTENSION` | General-purpose extension |

### Plugin Discovery

Plugins are discovered from the `plugins/` directory:

1. **Directory Plugins** — Directories containing `plugin.json` manifest
2. **Single-File Plugins** — `.py` files in the `plugins/` directory

### Plugin Manifest

```json
{
  "name": "Quick Notes",
  "version": "1.0.0",
  "description": "Save and search quick notes",
  "type": "COMMAND",
  "author": "User",
  "commands": ["note save", "notes list", "notes search"],
  "security_level": "SANDBOXED"
}
```

### Plugin Lifecycle

```
Discover → Load → Enable → Execute → Disable → Unload → Uninstall
```

### Commands

| Command | Description |
|---------|-------------|
| `install plugin` | Install a plugin |
| `uninstall plugin` | Remove a plugin |
| `enable plugin` | Enable a disabled plugin |
| `disable plugin` | Disable an enabled plugin |
| `reload plugin` | Reload a plugin |
| `list plugins` | List all plugins |
| `plugin info <name>` | Show plugin details |
| `plugin commands` | List plugin commands |
| `plugin events` | List plugin events |
| `plugin stats` | Show plugin statistics |
| `discover plugins` | Discover new plugins |
| `plugin security` | Show plugin security info |
| `run plugin <name>` | Execute a plugin |

### Sample Plugins

#### Quick Notes (Directory Plugin)

Location: `plugins/quick_notes/`

```
quick_notes/
├── plugin.json      # Manifest
└── plugin.py        # Implementation
```

Commands:
- `note save <text>` — Save a note
- `notes list` — List all notes
- `notes search <query>` — Search notes

Storage: `plugins/quick_notes/notes.json`

#### System Info (Single-File Plugin)

Location: `plugins/system_info_plugin.py`

Commands:
- `sysinfo` — Show system information
- `meminfo` — Show memory information
- `diskinfo` — Show disk information

Uses `psutil` for system monitoring.

---

## 70. PLUGIN DEVELOPMENT

### Overview

This section covers how to develop custom plugins for NEXUS.

### Plugin Base Classes

The Plugin Agent provides abstract base classes in `agents/plugin_agent/plugin_api.py`:

```python
class BasePlugin(ABC):
    """Base class for all plugins."""
    
    def __init__(self, metadata: PluginMetadata):
        self.metadata = metadata
    
    @abstractmethod
    def initialize(self) -> None:
        """Initialize the plugin."""
        pass
    
    @abstractmethod
    def execute(self, command: str, **kwargs) -> dict:
        """Execute a plugin command."""
        pass
    
    @abstractmethod
    def shutdown(self) -> None:
        """Shutdown the plugin."""
        pass

class CommandPlugin(BasePlugin):
    """Plugin that adds commands."""
    
    def get_commands(self) -> list[str]:
        """Return list of supported commands."""
        pass

class ServicePlugin(BasePlugin):
    """Plugin that provides a background service."""
    
    def start_service(self) -> None:
        """Start the background service."""
        pass
    
    def stop_service(self) -> None:
        """Stop the background service."""
        pass

class HookPlugin(BasePlugin):
    """Plugin that hooks into system events."""
    
    def get_hooks(self) -> list[str]:
        """Return list of events to hook into."""
        pass
    
    def on_event(self, event: str, data: dict) -> None:
        """Handle a system event."""
        pass
```

### Creating a Command Plugin

1. **Create Plugin Directory**

```bash
mkdir plugins/my_plugin
```

2. **Create Manifest**

`plugins/my_plugin/plugin.json`:
```json
{
  "name": "My Plugin",
  "version": "1.0.0",
  "description": "Description of my plugin",
  "type": "COMMAND",
  "author": "Your Name",
  "commands": ["my command", "my other command"],
  "security_level": "SANDBOXED"
}
```

3. **Create Implementation**

`plugins/my_plugin/plugin.py`:
```python
from agents.plugin_agent.plugin_api import CommandPlugin

class MyPlugin(CommandPlugin):
    def initialize(self):
        pass
    
    def get_commands(self):
        return ["my command", "my other command"]
    
    def execute(self, command, **kwargs):
        if command == "my command":
            return {"success": True, "data": "Result"}
        elif command == "my other command":
            return {"success": True, "data": "Other result"}
        return {"success": False, "error": "Unknown command"}
    
    def shutdown(self):
        pass
```

4. **Discover and Install**

```
> discover plugins
> install plugin my_plugin
> list plugins
```

### Creating a Single-File Plugin

`plugins/my_single_file_plugin.py`:
```python
from agents.plugin_agent.plugin_api import CommandPlugin
from agents.plugin_agent.models import PluginMetadata

metadata = PluginMetadata(
    name="My Single File Plugin",
    version="1.0.0",
    description="A simple single-file plugin",
    type="COMMAND",
    author="Your Name",
    commands=["hello", "goodbye"],
    security_level="SANDBOXED"
)

class MySingleFilePlugin(CommandPlugin):
    def __init__(self):
        super().__init__(metadata)
    
    def initialize(self):
        pass
    
    def get_commands(self):
        return self.metadata.commands
    
    def execute(self, command, **kwargs):
        if command == "hello":
            return {"success": True, "data": "Hello!"}
        elif command == "goodbye":
            return {"success": True, "data": "Goodbye!"}
        return {"success": False, "error": "Unknown command"}
    
    def shutdown(self):
        pass
```

### Plugin Dependencies

Specify dependencies in the manifest:

```json
{
  "dependencies": ["psutil>=5.0", "requests>=2.28"],
  "python_version": ">=3.10"
}
```

The Plugin Agent checks dependencies before loading.

### Plugin Capabilities

Declare plugin capabilities in the manifest:

```json
{
  "capabilities": [
    {"type": "file_access", "paths": ["/tmp", "./notes"]},
    {"type": "network_access", "domains": ["api.example.com"]},
    {"type": "command_execution", "commands": ["ls", "cat"]}
  ]
}
```

Capabilities are enforced by the sandbox.

---

## 71. PLUGIN SANDBOX

### Overview

The Plugin Sandbox (`agents/plugin_agent/sandbox.py`) provides restricted execution for untrusted plugins.

### Security Levels

| Level | Description |
|-------|-------------|
| `TRUSTED` | Full access to system |
| `SANDBOXED` | Restricted modules and operations |
| `RESTRICTED` | Very limited access |
| `BLOCKED` | Cannot be loaded |

### Allowed Modules (Sandboxed)

28 modules are allowed in sandboxed mode:
- `json`, `csv`, `datetime`, `time`, `math`, `random`, `re`, `string`, `collections`, `itertools`, `functools`, `operator`, `copy`, `typing`, `dataclasses`, `enum`, `abc`, `pathlib`, `os.path`, `stat`, `textwrap`, `unicodedata`, `html`, `xml`, `logging`, `hashlib`, `base64`, `uuid`

### Blocked Modules

23 modules are blocked:
- `os`, `sys`, `subprocess`, `ctypes`, `socket`, `http`, `urllib`, `requests`, `ftplib`, `smtplib`, `shutil`, `pickle`, `marshal`, `importlib`, `compile`, `exec`, `eval`, `__import__`, `threading`, `multiprocessing`, `asyncio`, `concurrent`, `signal`

### Safe Builtins

40 safe built-in functions are available:
- `abs`, `all`, `any`, `bin`, `bool`, `bytes`, `chr`, `dict`, `divmod`, `enumerate`, `filter`, `float`, `format`, `frozenset`, `hex`, `int`, `isinstance`, `issubclass`, `iter`, `len`, `list`, `map`, `max`, `min`, `next`, `oct`, `ord`, `pow`, `print`, `range`, `repr`, `reversed`, `round`, `set`, `slice`, `sorted`, `str`, `sum`, `tuple`, `zip`

### Code Analyzer

The CodeAnalyzer (`agents/plugin_agent/sandbox.py`) performs static analysis:

```python
analyzer = CodeAnalyzer()
result = analyzer.analyze(source_code)

if result.has_dangerous_functions:
    raise SecurityError("Plugin contains dangerous functions")
```

Detects:
- `eval()`, `exec()`, `compile()`, `__import__()`
- Dangerous attributes: `__subclasses__`, `__mro__`, `__globals__`
- Dangerous calls: `open()`, `input()`, `breakpoint()`

### Restricted Importer

The RestrictedImporter prevents loading blocked modules:

```python
importer = RestrictedImporter(allowed_modules=ALLOWED_MODULES)
module = importer.load_module("my_plugin")
```

### Timeout Enforcement

Plugin execution is subject to timeout enforcement:

```python
# Plugin execution timeout (default: 30 seconds)
timeout = config.get("plugins.execution_timeout", default=30)
```

---

*Continue to Part VII: System Management →*

---

## 72. PERFORMANCE OPTIMIZATION

### Overview

NEXUS is designed for performance, but several factors can affect responsiveness.

### Performance Factors

| Factor | Impact | Mitigation |
|--------|--------|------------|
| LLM Provider | High (1–5s per response) | Use local Ollama, enable streaming |
| Agent Count | Medium (startup time) | Disable unused agents |
| Database Size | Low (SQLite is fast) | Regular cleanup of old data |
| UI Complexity | Low (Textual is efficient) | Reduce animation speed |
| Concurrent Tasks | Medium (CPU/memory) | Limit max concurrent tasks |

### Optimization Tips

1. **Use Local LLM** — Ollama is faster than cloud APIs for most tasks
2. **Disable Unused Agents** — Remove agents you don't need from the registry
3. **Limit Concurrent Tasks** — Set `max_concurrent_tasks` to match your CPU cores
4. **Reduce Animation Speed** — Set `animation_speed` to `"fast"` in config
5. **Disable Loader** — Set `show_loader` to `false` for faster startup
6. **Use CLI Mode** — `--cli` mode skips Textual UI initialization
7. **Regular Cleanup** — Clean up old conversations, tasks, and context data

### Monitoring Performance

```
> system status          # Show system metrics
> performance report     # Show performance analytics
> analytics stats        # Show analytics statistics
```

### Memory Management

NEXUS uses minimal memory by default:
- **SQLite** — Efficient disk-based storage
- **Streaming** — Responses are streamed, not buffered
- **Lazy Loading** — Agents are loaded on demand
- **Connection Pooling** — Database connections are reused

For memory-constrained systems:
- Limit concurrent tasks to 1–2
- Disable context monitoring
- Disable learning agent
- Use CLI mode instead of Textual UI

---

## 73. DEPENDENCY MANAGEMENT

### Overview

NEXUS dependencies are managed through `requirements.txt` and per-agent/plugin requirements.

### Core Dependencies

All core dependencies are in `requirements.txt`:

```
textual>=8.2.0
rich>=13.0.0
openai>=1.0.0
pydantic>=2.0.0
psutil>=5.9.0
watchdog>=3.0.0
playwright>=1.40.0
schedule>=1.2.0
colorama>=0.4.6
pygetwindow>=0.0.9; sys_platform == 'win32'
pyautogui>=0.9.54
```

### Agent-Specific Dependencies

Some agents have additional dependencies:
- **Web Agent** — `playwright` (browser automation)
- **Context Awareness** — `pygetwindow` (Windows only), `pyautogui`
- **Automation Agent** — `pyautogui`
- **Vision Agent** — Multimodal LLM support

### Plugin Dependencies

Plugins can specify dependencies in their manifest:

```json
{
  "dependencies": ["psutil>=5.0", "requests>=2.28"]
}
```

Dependencies are checked during plugin loading.

### Installing Dependencies

```bash
# Core dependencies
pip install -r requirements.txt

# Playwright browsers (for Web Agent)
playwright install

# Ollama (for local LLM)
# Visit https://ollama.ai for installation
```

### Dependency Resolution

The Marketplace Agent includes a `DependencyResolver` for agent installation:

```python
resolver = DependencyResolver()
install_order = resolver.resolve(agent_dependencies)
# Returns: topological sort of dependencies
```

Features:
- Recursive dependency resolution
- Version compatibility checking
- Conflict detection
- Topological sort for install order

---

## 74. DEBUGGING & TROUBLESHOOTING

### Overview

This section covers common issues and how to resolve them.

### Debug Mode

Enable debug mode for detailed logging:

```bash
python main.py --debug
```

Debug mode shows:
- DEBUG-level logs
- All stdout/stderr
- Detailed error traces
- Agent loading details
- Database queries

### Verbose Mode

Enable verbose mode for INFO-level logs:

```bash
python main.py --verbose
```

Verbose mode shows:
- INFO-level logs
- All stdout/stderr
- Agent initialization messages
- Task execution details

### Log File

All logs are written to `data/nexus.log` regardless of console mode:

```bash
# View log file
cat data/nexus.log        # macOS/Linux
type data/nexus.log       # Windows

# Follow log in real-time
tail -f data/nexus.log    # macOS/Linux
```

### Common Issues

#### Ollama Connection Error

**Symptom**: `Connection refused` or `Ollama not running`

**Solution**:
1. Ensure Ollama is installed: `ollama --version`
2. Start Ollama: `ollama serve`
3. Pull a model: `ollama pull llama3`
4. Verify URL: `curl http://localhost:11434/api/tags`

#### OpenAI API Error

**Symptom**: `Invalid API key` or `Rate limit exceeded`

**Solution**:
1. Verify API key in `.env`: `OPENAI_API_KEY=sk-...`
2. Check API key validity at https://platform.openai.com
3. Wait for rate limit to reset (usually 1 minute)

#### Textual UI Error

**Symptom**: `Terminal too small` or `Unicode error`

**Solution**:
1. Increase terminal window size
2. Ensure terminal supports Unicode
3. Try CLI mode: `python main.py --cli`

#### Database Error

**Symptom**: `Database locked` or `Table not found`

**Solution**:
1. Close any other processes using the database
2. Delete the database file and restart (data will be lost)
3. Run database migration if schema changed

#### Plugin Loading Error

**Symptom**: `Plugin failed to load` or `Module not found`

**Solution**:
1. Check plugin syntax: `python -m py_compile plugins/my_plugin/plugin.py`
2. Verify manifest: `cat plugins/my_plugin/plugin.json`
3. Check dependencies: `pip install <missing-package>`
4. Check security level: ensure plugin doesn't use blocked modules

#### Agent Not Found

**Symptom**: `Agent not found: <name>`

**Solution**:
1. Verify agent directory exists: `ls agents/<name>/`
2. Check agent.py has correct class name
3. Check agent extends BaseAgent
4. Check for import errors in agent.py

### Diagnostic Commands

```
> system status          # Show system health
> list plugins           # Show plugin status
> list agents            # Show agent status
> bus status             # Show communication bus status
> analytics stats        # Show analytics
```

---

## 75. ERROR HANDLING

### Overview

NEXUS implements comprehensive error handling at every layer.

### Error Types

| Error Type | Source | Handling |
|------------|--------|----------|
| `ConnectionError` | LLM provider, network | Retry with backoff |
| `TimeoutError` | Agent execution, LLM call | Retry or fallback |
| `ValueError` | Invalid input, config | Log error, return fallback |
| `KeyError` | Missing config, data | Use default value |
| `FileNotFoundError` | File operations | Return error message |
| `SecurityError` | Plugin sandbox, security agent | Block operation, log event |
| `CycleError` | Dependency graph | Report error, abort plan |

### Retry Strategy

```python
async def execute_with_retry(func, max_retries=3, backoff=1.0):
    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(backoff * (2 ** attempt))
```

### Fallback Strategy

If an agent fails, the system tries fallback options:

1. **Retry** — Same command, up to 3 times
2. **Fallback Command** — Alternative command for the same agent
3. **Alternative Agent** — Different agent with similar capabilities
4. **Default Response** — Generic error message

### Error Reporting

Errors are:
- Logged to `data/nexus.log`
- Recorded in the task database
- Reported to the user (in user-friendly terms)
- Tracked in analytics for trend analysis

---

## 76. BACKGROUND TASKS

### Overview

NEXUS runs several background tasks continuously:

| Task | Frequency | Purpose |
|------|-----------|---------|
| Context Monitoring | Every 10 seconds | Track user activity and focus |
| Learning Analysis | Every 5 minutes | Analyze behavior patterns |
| Task Retry Loop | Every 30 seconds | Retry failed tasks |
| Message Cleanup | Every 2 minutes | Remove expired messages |
| Scheduled Tasks | Every minute | Check and run scheduled tasks |
| Analytics Collection | Every minute | Collect system metrics |

### Background Task Management

Background tasks run in separate threads or async coroutines:

```python
# Async background task
async def background_task():
    while True:
        await do_something()
        await asyncio.sleep(interval)

# Thread-based background task
def background_thread():
    while running:
        do_something()
        time.sleep(interval)

threading.Thread(target=background_thread, daemon=True).start()
```

### Monitoring Background Tasks

```
> system status          # Show background task status
> tasks                  # Show all tasks (including background)
> analytics stats        # Show background task metrics
```

---

## 77. SESSION MANAGEMENT

### Overview

NEXUS manages user sessions for conversation tracking and context preservation.

### Session Lifecycle

```
Start → Active → (Conversations) → End → Archive
```

### Session Start

A session starts when NEXUS launches:
- Unique session ID is generated (UUID)
- Session record is created in the database
- Context monitoring begins (if enabled)
- Learning tracking begins (if enabled)

### Session End

A session ends when NEXUS exits:
- Session end time is recorded
- Context monitoring stops
- Learning data is saved
- Session is archived

### Session Data

Each session includes:
- Session ID (UUID)
- Start time
- End time
- Conversation count
- Task count
- Agent usage statistics
- Context snapshots (if enabled)

### Session Commands

```
> session start          # Start a new session (manual)
> session end            # End current session (manual)
> session info           # Show current session info
> session history        # Show session history
```

---

## 78. ADVANCED CONFIGURATION

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `NEXUS_LOG_LEVEL` | `WARNING` | Override log level |
| `NEXUS_DATA_DIR` | `./data` | Custom data directory |
| `NEXUS_CONFIG_DIR` | `./config` | Custom config directory |
| `NEXUS_PLUGIN_DIR` | `./plugins` | Custom plugin directory |
| `NEXUS_AGENT_DIR` | `./agents` | Custom agent directory |
| `NEXUS_MAX_TASKS` | `5` | Max concurrent tasks |
| `NEXUS_TASK_TIMEOUT` | `300` | Task timeout in seconds |
| `NEXUS_SHOW_LOADER` | `true` | Show startup loader |
| `NEXUS_THEME` | `nexus-dark` | Default theme |

### Configuration Overrides

Configuration can be overridden at multiple levels:

1. **Environment Variables** — Highest priority
2. **Settings File** — Medium priority
3. **Defaults** — Lowest priority

### Runtime Configuration

Some settings can be changed at runtime:

```python
from core.config import config

# Change LLM provider
config.set("llm.provider", "openai")

# Change theme
config.set("ui.theme", "nexus-light")

# Reload configuration
config.reload()
```

### Configuration Validation

The config validates required keys on load:

```python
required_keys = ["llm.provider", "llm.model"]
for key in required_keys:
    if not config.get(key):
        raise ConfigurationError(f"Missing required config: {key}")
```

---

## 79. BEST PRACTICES

### General

1. **Use Virtual Environments** — Isolate NEXUS dependencies
2. **Keep Ollama Updated** — Latest models have better performance
3. **Regular Backups** — Back up `data/` directory regularly
4. **Monitor Logs** — Check `data/nexus.log` for issues
5. **Clean Up Old Data** — Periodically clean old conversations and tasks

### Security

1. **Never Commit `.env`** — Keep API keys out of version control
2. **Review Plugins** — Always review plugin code before installing
3. **Use Sandboxed Mode** — Run untrusted plugins in sandboxed mode
4. **Enable Security Agent** — Keep security monitoring enabled
5. **Verify Marketplace Agents** — Always verify before installing

### Performance

1. **Use Local LLM** — Ollama is faster for most tasks
2. **Limit Concurrent Tasks** — Match to your CPU cores
3. **Disable Unused Agents** — Reduce startup time and memory
4. **Use CLI Mode for Scripts** — Skip Textual UI overhead
5. **Regular Database Cleanup** — Remove old records

### Development

1. **Follow Agent Structure** — Use the standard agent package layout
2. **Extend BaseAgent** — Always extend the base class
3. **Use Async** — Prefer async operations for I/O
4. **Handle Errors** — Implement comprehensive error handling
5. **Write Tests** — Test agents independently

---

## 80. ARCHITECTURE DECISIONS

### Why Textual?

Textual was chosen over PyQt6 for the primary UI because:
- **Terminal-native** — Works over SSH, in containers, on any platform
- **Lightweight** — Minimal dependencies, fast startup
- **Keyboard-first** — Optimized for power users
- **Rich ecosystem** — Built on Rich, excellent documentation

PyQt6 is available as an alternative interface in `ui/`.

### Why SQLite?

SQLite was chosen over PostgreSQL/MySQL because:
- **Zero configuration** — No database server needed
- **Single file** — Easy to back up and move
- **Fast** — Excellent performance for single-user workloads
- **Built-in** — Part of Python standard library

### Why Multi-Agent?

Multi-agent architecture was chosen over a single monolithic agent because:
- **Specialization** — Each agent excels at its domain
- **Parallelism** — Agents can run concurrently
- **Maintainability** — Agents can be developed and tested independently
- **Extensibility** — New agents can be added without modifying existing ones

### Why 3-Stage Routing?

3-stage routing (Regex → Fuzzy → LLM) was chosen because:
- **Speed** — Regex is instant, fuzzy is fast, LLM is slow
- **Accuracy** — Regex is precise, fuzzy handles typos, LLM handles ambiguity
- **Cost** — Regex and fuzzy are free, LLM costs tokens
- **Reliability** — If LLM fails, regex and fuzzy still work

### Why Event Bus?

Event bus was chosen over direct agent communication because:
- **Decoupling** — Agents don't need to know about each other
- **Scalability** — New agents can subscribe to existing events
- **Flexibility** — Multiple agents can respond to the same event
- **Observability** — All communication is logged and trackable

---

## 81. ROADMAP & FUTURE

### Planned Features

| Feature | Status | Description |
|---------|--------|-------------|
| MCP Server | Planned | Model Context Protocol server for external tool integration |
| Tmux Layouts | Planned | Tmux-style terminal layouts with embedded shell |
| Typing Animations | Planned | Smooth typing animations for responses |
| Markdown Rendering | Planned | Full markdown rendering in chat |
| Voice Input | Planned | Speech-to-text for voice commands |
| Mobile Companion | Planned | Mobile app for remote NEXUS control |
| Cloud Sync | Planned | Sync conversations and settings across devices |
| Agent Marketplace | Planned | Real marketplace for community agents |
| Workflow Editor | Planned | Visual workflow editor |
| Dashboard Widgets | Planned | Customizable dashboard widgets |

### Long-Term Vision

- **Full Autonomy** — NEXUS can accomplish complex goals with minimal user input
- **Cross-Platform** — Run on desktop, server, mobile, and cloud
- **Multi-Modal** — Support text, voice, image, and video input
- **Collaborative** — Multiple users can share a NEXUS instance
- **Self-Improving** — NEXUS learns and improves its own workflows

---

## APPENDIX A: COMPLETE COMMAND REFERENCE

### System Commands

| Command | Agent | Description |
|---------|-------|-------------|
| `help` | System | Show available commands |
| `exit` | System | Exit NEXUS |
| `system status` | Analytics | Show system status |
| `session start` | System | Start a new session |
| `session end` | System | End current session |

### File Agent Commands

| Command | Description |
|---------|-------------|
| `list files` | List files in current directory |
| `search files <pattern>` | Search for files |
| `read file <path>` | Read file contents |
| `write file <path>` | Write to file |
| `copy file <src> <dest>` | Copy a file |
| `move file <src> <dest>` | Move a file |
| `delete file <path>` | Delete a file |
| `file info <path>` | Get file metadata |
| `directory tree` | Show directory tree |

### Web Agent Commands

| Command | Description |
|---------|-------------|
| `search web <query>` | Search the web |
| `open url <url>` | Open and extract URL content |
| `summarize url <url>` | Summarize webpage content |
| `screenshot url <url>` | Capture webpage screenshot |

### Coding Agent Commands

| Command | Description |
|---------|-------------|
| `analyze code` | Analyze code quality |
| `generate code <description>` | Generate code |
| `review code` | Review code |
| `debug error <error>` | Debug an error |
| `refactor code` | Suggest refactoring |
| `explain code` | Explain code |

### Automation Agent Commands

| Command | Description |
|---------|-------------|
| `create automation` | Create automation |
| `list automations` | List automations |
| `run automation <name>` | Execute automation |
| `delete automation <name>` | Remove automation |

### Scheduler Agent Commands

| Command | Description |
|---------|-------------|
| `schedule task` | Schedule a task |
| `list tasks` | List scheduled tasks |
| `cancel task <id>` | Cancel a task |
| `set reminder` | Set a reminder |
| `list reminders` | List reminders |
| `recurring task` | Create recurring task |

### Notification Agent Commands

| Command | Description |
|---------|-------------|
| `send notification` | Send notification |
| `list notifications` | List notifications |
| `clear notifications` | Clear notifications |
| `notification settings` | Configure settings |

### Terminal Agent Commands

| Command | Description |
|---------|-------------|
| `run command <cmd>` | Execute shell command |
| `terminal session` | Start terminal session |
| `env list` | List environment variables |
| `env get <var>` | Get environment variable |
| `env set <var> <val>` | Set environment variable |

### Vision Agent Commands

| Command | Description |
|---------|-------------|
| `analyze image <path>` | Analyze image |
| `ocr image <path>` | Extract text from image |
| `describe screenshot` | Analyze screenshot |
| `generate image <description>` | Generate image |

### Memory Agent Commands

| Command | Description |
|---------|-------------|
| `save memory` | Save to memory |
| `search memory` | Search memory |
| `list memories` | List memories |
| `delete memory` | Delete memory |
| `recall` | Recall memories |
| `memory stats` | Memory statistics |

### Knowledge Agent Commands

| Command | Description |
|---------|-------------|
| `add knowledge` | Add knowledge |
| `search knowledge` | Search knowledge |
| `list knowledge` | List knowledge |
| `summarize` | Summarize item |
| `delete knowledge` | Delete knowledge |
| `knowledge stats` | Knowledge statistics |

### Personality Agent Commands

| Command | Description |
|---------|-------------|
| `set personality` | Set personality |
| `list personalities` | List personalities |
| `adjust tone` | Adjust tone |
| `personality info` | Show current personality |

### Workflow Agent Commands

| Command | Description |
|---------|-------------|
| `create workflow` | Create workflow |
| `list workflows` | List workflows |
| `run workflow <name>` | Execute workflow |
| `edit workflow <name>` | Edit workflow |
| `delete workflow <name>` | Delete workflow |
| `workflow status` | Show workflow status |

### Security Agent Commands

| Command | Description |
|---------|-------------|
| `security scan` | Run security scan |
| `threat list` | List threats |
| `security policies` | Show policies |
| `audit log` | Show audit log |
| `file integrity` | Check file integrity |

### Analytics Agent Commands

| Command | Description |
|---------|-------------|
| `system status` | Show system status |
| `usage report` | Show usage analytics |
| `performance report` | Show performance |
| `trend analysis` | Show trends |
| `analytics stats` | Show statistics |

### Context Awareness Commands

| Command | Description |
|---------|-------------|
| `current context` | Show context snapshot |
| `active window` | Show active window |
| `running apps` | List running apps |
| `activity type` | Show activity type |
| `focus level` | Show focus level |
| `system load` | Show system load |
| `suggest workflow` | Suggest workflow |
| `suggest actions` | Suggest actions |
| `start monitoring` | Start monitoring |
| `stop monitoring` | Stop monitoring |
| `workflow patterns` | List workflow patterns |
| `detect workflow` | Detect current workflow |
| `triggers` | List triggers |
| `add trigger` | Add trigger |
| `toggle trigger` | Toggle trigger |
| `context history` | Show context history |
| `activity summary` | Show activity summary |
| `session start` | Start session |
| `session end` | End session |
| `context rules` | List context rules |
| `add rule` | Add context rule |
| `delete rule` | Delete context rule |
| `cleanup` | Clean up context data |

### Learning Agent Commands

| Command | Description |
|---------|-------------|
| `start learning` | Enable learning |
| `stop learning` | Disable learning |
| `analyze` | Analyze behavior |
| `patterns` | Show patterns |
| `habits` | Show habits |
| `recommendations` | Show recommendations |
| `accept recommendation <n>` | Accept recommendation |
| `dismiss recommendation <n>` | Dismiss recommendation |
| `predict` | Predict next action |
| `behavior history` | Show behavior history |
| `learning stats` | Show learning stats |
| `generate workflow` | Generate workflow |
| `daily routine` | Generate daily routine |
| `most common` | Show most common actions |
| `hourly pattern` | Show hourly pattern |
| `daily pattern` | Show daily pattern |
| `prediction accuracy` | Show prediction accuracy |
| `cleanup` | Clean up learning data |

### Communication Bus Commands

| Command | Description |
|---------|-------------|
| `bus status` | Show bus status |
| `bus messages` | List messages |
| `bus subscriptions` | List subscriptions |
| `bus shared state` | Show shared state |
| `bus events` | Show event log |
| `bus publish` | Publish message |
| `bus subscribe` | Subscribe to event |

### Planner Agent Commands

| Command | Description |
|---------|-------------|
| `create plan <goal>` | Create plan |
| `list plans` | List plans |
| `run plan <name>` | Execute plan |
| `pause plan <name>` | Pause plan |
| `resume plan <name>` | Resume plan |
| `cancel plan <name>` | Cancel plan |
| `plan status <name>` | Show plan status |

### Marketplace Agent Commands

| Command | Description |
|---------|-------------|
| `browse marketplace` | Browse agents |
| `search marketplace <query>` | Search agents |
| `install agent <name>` | Install agent |
| `update agent <name>` | Update agent |
| `uninstall agent <name>` | Uninstall agent |
| `list installed` | List installed agents |
| `verify agent <name>` | Verify agent |
| `agent info <name>` | Show agent info |
| `review agent` | Rate and review |

### Plugin Agent Commands

| Command | Description |
|---------|-------------|
| `install plugin` | Install plugin |
| `uninstall plugin` | Uninstall plugin |
| `enable plugin` | Enable plugin |
| `disable plugin` | Disable plugin |
| `reload plugin` | Reload plugin |
| `list plugins` | List plugins |
| `plugin info <name>` | Show plugin info |
| `plugin commands` | List plugin commands |
| `plugin events` | List plugin events |
| `plugin stats` | Show plugin stats |
| `discover plugins` | Discover plugins |
| `plugin security` | Show security info |
| `run plugin <name>` | Execute plugin |

---

## APPENDIX B: DATABASE SCHEMA REFERENCE

### nexus.db Tables

| Table | Columns | Purpose |
|-------|---------|---------|
| `conversations` | id, user_message, agent_response, timestamp, agent_name, session_id | Conversation history |
| `tasks` | id, description, status, agent_name, priority, created_at, started_at, completed_at, result, error, retry_count | Task tracking |
| `security_events` | id, event_type, severity, description, timestamp, resolved | Security event log |
| `workflow_chains` | id, name, status, created_at, updated_at | Workflow chain definitions |
| `workflow_steps` | id, chain_id, agent_name, command, order_index, status | Workflow chain steps |
| `analytics_events` | id, event_type, data, timestamp | Analytics event log |
| `bus_messages` | id, event_type, data, priority, status, created_at | Bus message storage |
| `bus_subscriptions` | id, event_pattern, subscriber, created_at | Bus subscription records |
| `bus_shared_state` | id, key, value, version, namespace, expires_at, updated_at | Shared state entries |
| `bus_event_log` | id, event_type, data, timestamp | Bus event log |
| `plans` | id, name, goal, status, progress, created_at, updated_at | Plan definitions |
| `plan_tasks` | id, plan_id, description, status, dependencies, agent_name, order_index | Plan tasks |
| `goal_templates` | id, name, description, template_data | Goal templates |
| `plan_history` | id, plan_id, event_type, data, timestamp | Plan event history |
| `marketplace_agents` | id, name, description, version, category, author, status, created_at | Marketplace agent catalog |
| `install_records` | id, agent_id, status, installed_at, install_path | Installation records |
| `agent_reviews` | id, agent_id, rating, review, created_at | Agent reviews |
| `verification_reports` | id, agent_id, status, report_data, created_at | Verification reports |

### context.db Tables

| Table | Columns | Purpose |
|-------|---------|---------|
| `context_snapshots` | id, active_window, running_apps, activity_type, focus_level, system_load, timestamp | Context history |
| `context_patterns` | id, name, description, pattern_data | Workflow patterns |
| `adaptive_triggers` | id, name, condition, action, enabled | Adaptive triggers |
| `context_sessions` | id, start_time, end_time, productivity_score | Session records |
| `context_rules` | id, name, condition, action, enabled | User-defined rules |

### learning.db Tables

| Table | Columns | Purpose |
|-------|---------|---------|
| `behavior_records` | id, action, preceding_actions, context, timestamp | Behavior records |
| `learned_patterns` | id, pattern_type, pattern_data, confidence, status | Learned patterns |
| `recommendations` | id, type, description, status, created_at | Recommendations |
| `user_habits` | id, habit_type, description, frequency, automation_potential | User habits |
| `prediction_log` | id, prediction, actual, accurate, timestamp | Prediction accuracy |

---

## APPENDIX C: API REFERENCE

### Core API

| Module | Class | Methods |
|--------|-------|---------|
| `core/base_agent.py` | `BaseAgent` | `execute()`, `get_commands()`, `start()`, `stop()`, `get_status()` |
| `core/config.py` | `Config` | `get()`, `set()`, `reload()` |
| `core/database.py` | `Database` | `execute()`, `fetch()`, `fetch_one()` |
| `core/llm_provider.py` | `LLMProvider` | `generate()`, `generate_stream()`, `chat()`, `chat_stream()`, `embed()` |
| `core/logger.py` | `Logger` | `set_mode()`, `suppress_console()`, `enable_console()` |

### Manager API

| Module | Class | Methods |
|--------|-------|---------|
| `manager/manager.py` | `AIManager` | `initialize()`, `handle_request()`, `get_agent()`, `get_agents()`, `get_commands()`, `shutdown()` |
| `manager/router.py` | `Router` | `route()` |
| `manager/dispatcher.py` | `Dispatcher` | `dispatch()`, `worker()` |

### Terminal API

| Module | Class | Methods |
|--------|-------|---------|
| `terminal/app.py` | `NexusApp` | `on_mount()` |
| `terminal/loader.py` | `CinematicLoader` | `run()` |
| `terminal/loader.py` | `PhaseTracker` | `advance()` |
| `terminal/loader.py` | `StepTracker` | `advance()` |
| `terminal/streaming.py` | `StreamingHandler` | `stream_response()` |
| `terminal/theme.py` | `Theme` | Theme definitions |
| `terminal/widgets.py` | `NexusHeader` | `render()` |
| `terminal/widgets.py` | `NexusStatusBar` | `render()` |

### Communication API

| Module | Class | Methods |
|--------|-------|---------|
| `communication_bus_agent/event_bus.py` | `EventBus` | `subscribe()`, `subscribe_async()`, `subscribe_once()`, `subscribe_conditional()`, `publish()`, `publish_async()`, `unsubscribe()`, `unsubscribe_all()`, `unsubscribe_subscriber()` |
| `communication_bus_agent/message_broker.py` | `MessageBroker` | `send()`, `receive()`, `receive_nowait()`, `acknowledge()`, `get_dead_letter_queue()` |
| `communication_bus_agent/shared_state.py` | `SharedStateManager` | `set()`, `get()`, `delete()`, `exists()`, `lock()`, `unlock()`, `add_listener()`, `is_expired()`, `get_entry()` |
| `communication_bus_agent/event_logger.py` | `EventLogger` | `log()`, `add_stream_listener()`, `get_events()`, `get_event_count()`, `get_communication_flow()`, `get_timeline()` |

### Planning API

| Module | Class | Methods |
|--------|-------|---------|
| `planner_agent/goal_decomposition.py` | `GoalDecomposer` | `decompose()` |
| `planner_agent/dependency_graph.py` | `DependencyGraph` | `add_task()`, `add_dependency()`, `has_cycle()`, `get_ready_tasks()`, `get_blocked_tasks()` |
| `planner_agent/planning_engine.py` | `PlanningEngine` | `create_plan()`, `execute_plan()`, `replan()` |
| `planner_agent/task_executor.py` | `TaskExecutor` | `execute_plan()` |

### Learning API

| Module | Class | Methods |
|--------|-------|---------|
| `learning_agent/services.py` | `LearningEngine` | `analyze()`, `predict()` |
| `learning_agent/services.py` | `BehaviorTracker` | `record()`, `get_action_frequency()`, `get_hourly_pattern()`, `get_daily_pattern()` |
| `learning_agent/services.py` | `PatternAnalyzer` | `detect_frequency_patterns()`, `detect_sequence_patterns()`, `detect_time_based_patterns()`, `detect_contextual_patterns()` |
| `learning_agent/services.py` | `RecommendationEngine` | `generate_recommendations()` |
| `learning_agent/services.py` | `AdaptiveWorkflowGenerator` | `generate_workflows_from_patterns()`, `generate_daily_routine()`, `predict_next_action()` |

### Plugin API

| Module | Class | Methods |
|--------|-------|---------|
| `plugin_agent/plugin_api.py` | `BasePlugin` | `initialize()`, `execute()`, `shutdown()` |
| `plugin_agent/plugin_api.py` | `CommandPlugin` | `get_commands()` |
| `plugin_agent/plugin_api.py` | `ServicePlugin` | `start_service()`, `stop_service()` |
| `plugin_agent/plugin_api.py` | `HookPlugin` | `get_hooks()`, `on_event()` |
| `plugin_agent/sandbox.py` | `PluginSandbox` | `execute()` |
| `plugin_agent/sandbox.py` | `CodeAnalyzer` | `analyze()` |
| `plugin_agent/loader.py` | `PluginLoader` | `discover()`, `load()` |
| `plugin_agent/registry.py` | `PluginRegistry` | `register()`, `unregister()`, `get_plugin()`, `get_plugins()` |

---

## APPENDIX D: AGENT CATALOG

### Built-In Agents (21)

| # | Agent | Category | Commands | Description |
|---|-------|----------|----------|-------------|
| 1 | File Agent | System | 9 | File system operations |
| 2 | Web Agent | Internet | 4 | Web browsing and content extraction |
| 3 | Coding Agent | Development | 6 | Code analysis and generation |
| 4 | Automation Agent | Automation | 4 | Task automation and scripting |
| 5 | Memory Agent | Intelligence | 6 | Long-term memory and semantic search |
| 6 | Vision Agent | Multimodal | 4 | Image analysis and OCR |
| 7 | Notification Agent | System | 4 | System notifications and alerts |
| 8 | Scheduler Agent | Productivity | 6 | Task scheduling and reminders |
| 9 | Knowledge Agent | Intelligence | 6 | Knowledge base management |
| 10 | Terminal Agent | System | 5 | Shell command execution |
| 11 | Personality Agent | AI | 4 | AI personality and tone |
| 12 | Workflow Agent | Automation | 6 | Workflow management |
| 13 | Security Agent | Security | 5 | Security monitoring and scanning |
| 14 | Workflow Chain Agent | Automation | 5 | Multi-agent execution chains |
| 15 | Analytics Agent | Analytics | 5 | System metrics and analytics |
| 16 | Context Awareness Agent | Intelligence | 24+ | Context monitoring and adaptive automation |
| 17 | Learning Agent | Intelligence | 18 | Behavior tracking and pattern detection |
| 18 | Communication Bus Agent | Infrastructure | 7 | Inter-agent communication |
| 19 | Planner Agent | Intelligence | 7 | Goal decomposition and planning |
| 20 | Marketplace Agent | Extension | 9 | Agent marketplace |
| 21 | Plugin Agent | Extension | 13 | Plugin management |

### Marketplace Agents (10 Seeded)

| # | Agent | Category | Description |
|---|-------|----------|-------------|
| 1 | Weather Agent | Productivity | Weather forecasts and alerts |
| 2 | Email Agent | Communication | Email management |
| 3 | Music Agent | Entertainment | Music control |
| 4 | Git Agent | Development | Git operations |
| 5 | Calendar Agent | Productivity | Calendar management |
| 6 | Docker Agent | Development | Docker container management |
| 7 | Network Agent | System | Network diagnostics |
| 8 | Translation Agent | Communication | Language translation |
| 9 | Database Agent | Analytics | Database query |
| 10 | Home Automation Agent | Automation | Smart home control |

---

## APPENDIX E: GLOSSARY

| Term | Definition |
|------|------------|
| **Agent** | A specialized AI module that handles specific types of requests |
| **Async** | Asynchronous execution; non-blocking operations |
| **Cinematic Loader** | Animated startup sequence with progress tracking |
| **Context** | User's current activity, focus level, and environment |
| **DAG** | Directed Acyclic Graph; used for task dependency management |
| **Dead Letter Queue** | Queue for messages that failed after max retries |
| **Dispatcher** | Component that queues and distributes tasks to agents |
| **Embedding** | Vector representation of text for semantic search |
| **Event Bus** | Publish/subscribe messaging system |
| **Focus Level** | User's concentration level (deep, focused, moderate, distracted, idle) |
| **Hook** | Callback that fires on system events |
| **Intent Routing** | Determining which agent should handle a request |
| **LLM** | Large Language Model |
| **Marketplace** | System for browsing and installing community agents |
| **MCP** | Model Context Protocol |
| **Message Broker** | Priority-queued message delivery system |
| **Multi-Agent** | Architecture using multiple specialized agents |
| **Namespace** | Isolated key space in shared state |
| **Ollama** | Local LLM runner |
| **Pattern** | Detected regularity in user behavior |
| **Phase Tracker** | Component that tracks initialization phases |
| **Plugin** | Lightweight extension that adds commands or services |
| **Pub/Sub** | Publish/Subscribe messaging pattern |
| **Replanning** | Regenerating a plan when conditions change |
| **Router** | Component that routes requests to agents |
| **Sandbox** | Restricted execution environment for plugins |
| **Semantic Search** | Search by meaning, not keywords |
| **Shared State** | Thread-safe key-value store for inter-agent data |
| **Streaming** | Real-time character-by-character response display |
| **Task** | A unit of work assigned to an agent |
| **Terminal-Native** | Runs entirely in the terminal |
| **Textual** | Python framework for terminal UIs |
| **TTL** | Time-To-Live; automatic expiration for data |
| **Vector** | Numerical representation of text for similarity comparison |
| **Workflow** | Sequence of commands executed as a unit |
| **Workflow Chain** | Multi-agent execution chain with dependencies |

---

## APPENDIX F: INDEX

### A
- Activity Classification — §42
- Adaptive Triggers — §45
- Agent Catalog — Appendix D
- Agent Structure — §21
- AI Manager — §22
- Analytics Agent — §65
- Async Execution — §40

### B
- BaseAgent — §21
- Behavior Tracking — §47
- Background Tasks — §76

### C
- Cinematic Loader — §11
- CLI Mode — §12
- Coding Agent — §58
- Command Reference — Appendix A
- Communication Bus — §29, §67
- Configuration — §9, §26, §78
- Context Awareness — §41
- Conversation History — §55

### D
- Database Schema — §28, Appendix B
- Debugging — §74
- Dependency Graph — §38
- Dispatcher — §24

### E
- Error Handling — §75
- Event Bus — §29
- Event Logger — §32

### F
- File Agent — §56
- Focus Detection — §43

### G
- Goal Decomposition — §37

### I
- Installation — §8
- Intent Router — §23
- Inter-Agent Communication — §33

### K
- Knowledge Agent — §52

### L
- Learning Agent — §17, §46
- LLM Provider — §25
- Logging — §27

### M
- Marketplace Agent — §68
- Memory Agent — §51
- Message Broker — §30

### N
- Notification Agent — §61

### P
- Pattern Analysis — §48
- Personality Agent — §66
- Planning Engine — §36
- Plugin Agent — §69
- Plugin Development — §70
- Plugin Sandbox — §71
- Predictive Actions — §50

### R
- Recommendation Engine — §49
- Roadmap — §81

### S
- Scheduler Agent — §60
- Security Agent — §64
- Semantic Search — §53
- Session Management — §77
- Shared State — §31
- Streaming — §18

### T
- Task Dispatcher — §24
- Task Executor — §39
- Task Monitor — §16
- Terminal Agent — §62
- Terminal UI — §13
- Theme System — §17
- Troubleshooting — §74

### V
- Vector Storage — §54
- Vision Agent — §63

### W
- Web Agent — §57
- Workflow Chains — §35
- Workflow Engine — §34

---

*End of NEXUS User Manual*
