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

*Continue to Part IV: Multi-Agent Orchestration →*
