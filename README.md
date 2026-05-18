# NEXUS

> **A terminal-native AI operating environment.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Textual](https://img.shields.io/badge/UI-Textual-cyan.svg)](https://textual.textualize.io/)
[![Ollama](https://img.shields.io/badge/LLM-Ollama-green.svg)](https://ollama.ai/)
[![OpenAI](https://img.shields.io/badge/LLM-OpenAI-7c3aed.svg)](https://openai.com/)
[![Status](https://img.shields.io/badge/status-active-success.svg)]()

NEXUS is a modular, agentic AI operating environment that runs entirely inside your terminal. It orchestrates 21 specialized AI agents through a central AI Manager, providing file operations, web research, coding assistance, desktop automation, memory management, security monitoring, and much more -- all through a cinematic terminal interface.

---

## Features

- **21 Specialized AI Agents** -- File, Web, Coding, Automation, Vision, Memory, Knowledge, Terminal, Security, Workflow, Plugin, Notification, Scheduler, Personality, Analytics, Context Awareness, Learning, Communication Bus, Planner, Marketplace, and Workflow Chain agents
- **3-Stage Intent Routing** -- Regex patterns (fast) -> Fuzzy matching (typo-tolerant) -> LLM understanding (natural language)
- **Cinematic Terminal UI** -- Animated startup loaders, live dashboards, streaming responses, multi-panel layouts, keyboard navigation
- **Local-First AI** -- Runs on Ollama by default, with OpenAI as an optional cloud fallback
- **Autonomous Planning** -- Goal decomposition, dependency resolution, parallel task execution, dynamic replanning
- **Agent Marketplace** -- Browse, verify, and install community agents with security scanning
- **Inter-Agent Communication** -- Pub/sub event bus, shared state management, dead letter queues
- **Memory & Knowledge** -- Persistent memory, vector search (ChromaDB), semantic retrieval, preference learning
- **Security Layer** -- Command risk analysis, process scanning, audit logging, permission management
- **Workflow Engine** -- Preset modes (Coding, Study, Deep Work, etc.), custom chains, parallel execution

## Quick Start

```bash
# Clone the repository
git clone https://github.com/Lucky-Joshi/Nexus-AI-Agent.git
cd Nexus-AI-Agent

# Install dependencies
pip install -r requirements.txt

# Start Ollama (for local LLM)
ollama serve &
ollama pull llama3

# Launch NEXUS
python main.py
```

## Terminal Experience

```
                  ███╗   ██╗███████╗██╗  ██╗██╗   ██╗███████╗
                  ████╗  ██║██╔════╝╚██╗██╔╝██║   ██║██╔════╝
                  ██╔██╗ ██║█████╗   ╚███╔╝ ██║   ██║███████╗
                  ██║╚██╗██║██╔══╝   ██╔██╗ ██║   ██║╚════██║
                  ██║ ╚████║███████╗██╔╝ ██╗╚██████╔╝███████║
                  ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝
                 AI Operating Environment  •  Terminal-Native
                                    v2.0.0

  [##############################] 100%

 ✓ Core Systems
 ✓ AI Systems
 ✓ Agent Systems
 ✓ Services
 ✓ Finalization

  elapsed 12.3s
───────────────────────────────────────────────────────────────
                         NEXUS ONLINE

  startup    12.3s
  phases     5 / 5
  steps      35 ok, 0 warn, 0 fail

       ✓  Core Systems
       ✓  AI Systems
       ✓  Agent Systems
       ✓  Services
       ✓  Finalization

                      type /help to begin
───────────────────────────────────────────────────────────────
```

## Command Examples

```
> system status                    # Check CPU, RAM, disk usage
> search web for AI agents         # Web research via Web Agent
> generate code for a REST API     # Code generation via Coding Agent
> start coding mode                # Activate workflow mode
> remember my project path         # Save to Memory Agent
> take a screenshot                # Capture screen via Vision Agent
> plan a research workflow         # Autonomous planning via Planner Agent
> browse marketplace               # Discover community agents
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Terminal UI (Textual)                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────────┐ │
│  │Dashboard │  │   Chat   │  │  Tasks   │  │   Loader    │ │
│  └──────────┘  └──────────┘  └──────────┘  └─────────────┘ │
└─────────────────────────────┬───────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────┐
│                      AI Manager                              │
│  ┌────────────┐  ┌──────────┐  ┌─────────────────────────┐ │
│  │  Router    │  │Dispatcher│  │     LLM Provider        │ │
│  │ (3-stage)  │  │          │  │  (Ollama / OpenAI)      │ │
│  └────────────┘  └──────────┘  └─────────────────────────┘ │
└─────────────────────────────┬───────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────┐
│                      Agent Layer (21 agents)                 │
│  File │ Web │ Coding │ Automation │ Vision │ Memory │ ...   │
│  Terminal │ Security │ Workflow │ Plugin │ Knowledge │ ...  │
│  Planner │ Marketplace │ Communication Bus │ Analytics │ ... │
└─────────────────────────────────────────────────────────────┘
```

## Documentation

### Guides

| Document | Path | Description |
|----------|------|-------------|
| Architecture | [docs/architecture.md](docs/architecture.md) | System architecture, diagrams, pipelines |
| Installation | [docs/installation.md](docs/installation.md) | Setup guide, dependencies, configuration |
| Contributing | [docs/contributing.md](docs/contributing.md) | Contribution guidelines, coding standards |
| Development Guide | [docs/development_guide.md](docs/development_guide.md) | Local development, debugging, testing |
| API Reference | [docs/api_reference.md](docs/api_reference.md) | Complete API documentation |

### System Modules

| Module | Path | Description |
|--------|------|-------------|
| Core | [docs/core.md](docs/core.md) | Base agent, config, database, LLM provider, logger |
| Manager | [docs/manager.md](docs/manager.md) | AI Manager, Router (3-stage), Task Dispatcher |
| Terminal | [docs/terminal.md](docs/terminal.md) | Terminal UI, screens, loader, commands, streaming |
| Agents Overview | [docs/agents.md](docs/agents.md) | All 21 agents overview with capabilities |

### Agent Documentation

#### Core Agents
| Agent | Path | Description |
|-------|------|-------------|
| File Agent | [docs/agents/file_agent.md](docs/agents/file_agent.md) | File operations, app launching, system monitoring |
| Web Agent | [docs/agents/web_agent.md](docs/agents/web_agent.md) | Web search, scraping, summarization, research |
| Coding Agent | [docs/agents/coding_agent.md](docs/agents/coding_agent.md) | Code generation, debugging, git operations |
| Automation Agent | [docs/agents/automation_agent.md](docs/agents/automation_agent.md) | Desktop automation, workflows, productivity modes |
| Terminal Agent | [docs/agents/terminal_agent.md](docs/agents/terminal_agent.md) | Safe command execution, sessions, streaming |

#### Perception & Memory
| Agent | Path | Description |
|-------|------|-------------|
| Vision Agent | [docs/agents/vision_agent.md](docs/agents/vision_agent.md) | Screen capture, OCR, window analysis |
| Memory Agent | [docs/agents/memory_agent.md](docs/agents/memory_agent.md) | Persistent memory, preferences, workflows |
| Knowledge Agent | [docs/agents/knowledge_agent.md](docs/agents/knowledge_agent.md) | Knowledge base, vector search, semantic retrieval |

#### UX & Productivity
| Agent | Path | Description |
|-------|------|-------------|
| Workflow Agent | [docs/agents/workflow_agent.md](docs/agents/workflow_agent.md) | Productivity modes (Coding, Study, Deep Work) |
| Notification Agent | [docs/agents/notification_agent.md](docs/agents/notification_agent.md) | Desktop notifications, focus mode, reminders |
| Scheduler Agent | [docs/agents/scheduler_agent.md](docs/agents/scheduler_agent.md) | Task scheduling, natural language triggers |
| Personality Agent | [docs/agents/personality_agent.md](docs/agents/personality_agent.md) | Tone, emotion, adaptive personality |

#### Meta & Infrastructure
| Agent | Path | Description |
|-------|------|-------------|
| Planner Agent | [docs/agents/planner_agent.md](docs/agents/planner_agent.md) | Goal decomposition, autonomous planning |
| Marketplace Agent | [docs/agents/marketplace_agent.md](docs/agents/marketplace_agent.md) | Agent marketplace, verification, installation |
| Workflow Chain Agent | [docs/agents/workflow_chain_agent.md](docs/agents/workflow_chain_agent.md) | Multi-agent chains, parallel execution |
| Communication Bus | [docs/agents/communication_bus_agent.md](docs/agents/communication_bus_agent.md) | Pub/sub event bus, shared state, messaging |
| Plugin Agent | [docs/agents/plugin_agent.md](docs/agents/plugin_agent.md) | Plugin system, sandbox, security |
| Security Agent | [docs/agents/security_agent.md](docs/agents/security_agent.md) | Risk analysis, permissions, audit logging |
| Analytics Agent | [docs/agents/analytics_agent.md](docs/agents/analytics_agent.md) | Usage tracking, performance metrics |
| Context Awareness | [docs/agents/context_awareness_agent.md](docs/agents/context_awareness_agent.md) | Activity detection, workflow suggestions |
| Learning Agent | [docs/agents/learning_agent.md](docs/agents/learning_agent.md) | Pattern learning, behavior prediction |

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.10+ |
| Terminal UI | Textual, Rich |
| LLM | Ollama (local), OpenAI (cloud) |
| Vector Search | ChromaDB, sentence-transformers |
| System | psutil, pyautogui, mss, opencv-python |
| OCR | EasyOCR, pytesseract |
| Storage | SQLite, JSON |
| Notifications | win10toast, plyer |

## License

MIT License -- see [LICENSE](LICENSE) for details.
