# Memory Agent

> Persistent memory, user preferences, workflow storage, and conversation context management for the NEXUS platform.

## Purpose

The Memory Agent provides long-term persistence and intelligent retrieval capabilities within the NEXUS multi-agent platform. It manages episodic, semantic, and procedural memories; stores user preferences; persists workflows; and maintains sliding conversation context windows with importance-based pruning. Uses a multi-stage retrieval pipeline combining keyword matching, importance scoring, recency decay, and access frequency boosting.

## Architecture

```
MemoryAgent (orchestrator)
├── MemoryService        — Store, recall, search, and manage memory entries
├── PreferenceService    — User preferences with dual JSON + SQLite storage
├── WorkflowService      — Workflow persistence and execution planning
├── ContextManager       — Sliding conversation context windows per session
├── Storage Layer
│   ├── SQLiteStorage    — Structured data: memories, workflows, sessions
│   ├── JSONStorage      — Preferences and lightweight config
│   └── VectorStorage    — Semantic similarity search (FAISS-ready stub)
└── RetrievalPipeline    — Multi-stage scoring: relevance + importance + recency + access
```

### Data Model

```
MemoryEntry
├── id, content, memory_type (episodic/semantic/procedural/user_memory)
├── category (fact/preference/event/conversation/workflow/context/user_data)
├── tags[], importance (0.0-1.0), access_count
└── created_at, updated_at, metadata{}

ContextWindow
├── session_id, messages[] (ContextMessage)
├── max_size (default 50), max_tokens (default 4000)
└── Importance-based pruning when exceeding limits

Workflow
├── id, name, description, steps[] (WorkflowStep)
├── tags[], usage_count
└── created_at, updated_at
```

## Capabilities

| Category | Operations |
|---|---|
| **Memory Storage** | Save memories with auto-detected type, category, tags, and importance scoring |
| **Memory Retrieval** | Multi-stage search: keyword → relevance → importance → recency → ranking |
| **Preference Management** | Get/set/list/clear preferences with dual JSON + SQLite storage |
| **Workflow Persistence** | Create, save, load, list, and delete workflows with usage tracking |
| **Context Management** | Per-session sliding windows, importance-based pruning, LLM context building |
| **Vector Search** | FAISS-ready vector storage with keyword fallback (semantic search stub) |
| **Statistics** | Memory counts by type, vector index size, active sessions, token estimates |

## Internal Structure

```
memory_agent/
├── __init__.py      — Package exports
├── agent.py         — MemoryAgent class: command parsing, 13 handlers (495 lines)
├── models.py        — Data models (174 lines):
│   ├── MemoryEntry      — Core memory unit with metadata
│   ├── Workflow/Step    — Saved workflow definitions
│   ├── ContextMessage   — Single conversation message
│   └── ContextWindow    — Sliding window with pruning
├── services.py      — Four service classes (341 lines):
│   ├── MemoryService      — CRUD, search via RetrievalPipeline
│   ├── PreferenceService  — Dual storage (JSON primary, SQLite fallback)
│   ├── WorkflowService    — Persistence, execution plans, usage tracking
│   └── ContextManager     — Per-session windows, LLM context building
├── storage.py       — Three storage backends (431 lines):
│   ├── SQLiteStorage      — WAL mode, indexed tables for memories/workflows/sessions
│   ├── JSONStorage        — File-based preferences and workflows
│   └── VectorStorage      — FAISS-ready with keyword fallback
└── retrieval.py     — RetrievalPipeline (187 lines):
    └── 4-stage scoring: relevance (0.45) + importance (0.25) + recency (0.20) + access (0.10)
```

### Key Design Patterns

- **Multi-Stage Retrieval**: Candidates filtered → relevance scored → importance weighted → recency boosted → access frequency adjusted → final ranking
- **Dual Storage**: Preferences stored in both JSON (fast access) and SQLite (queryable)
- **Importance-Based Pruning**: Context windows retain high-importance messages when exceeding limits
- **Temporal Decay**: Exponential half-life decay (168 hours) for recency scoring
- **Vector-Ready Architecture**: `VectorStorage` has FAISS integration stub with hash-based embedding fallback

## Usage Examples

### Natural Language Commands

```python
from agents.memory_agent.agent import MemoryAgent

agent = MemoryAgent()

# Save memories
agent.execute("remember that I prefer dark mode")
agent.execute("save that Python is my primary language")
agent.execute("note: I work from 9am to 5pm")

# Recall memories
agent.execute("what do you know about Python")
agent.execute("recall my preferences")
agent.execute("search memory for work schedule")

# Manage preferences
agent.execute("set preference theme = dark")
agent.execute("get preference theme")
agent.execute("list preferences")

# Workflow management
agent.execute("save workflow morning_routine")
agent.execute("load workflow morning_routine")
agent.execute("list workflows")

# Context management
agent.execute("show context")
agent.execute("recent conversation")

# Memory management
agent.execute("list memories")
agent.execute("list episodic memories")
agent.execute("delete memory abc12345")
agent.execute("clear context")
agent.execute("clear all memories")

# Statistics
agent.execute("memory stats")
```

### Programmatic API

```python
# Direct service access
entry = agent._memory_service.save(
    content="User prefers TypeScript over JavaScript",
    memory_type="semantic",
    category="preference",
    tags=["typescript", "preference"],
    importance=0.8,
)

memories = agent._memory_service.search("TypeScript", top_k=5)
agent._preference_service.set("theme", "dark")
value = agent._preference_service.get("theme")

# Context management (used by AI Manager)
agent.add_message_to_context("session-1", "user", "Hello!", importance=0.5)
context = agent.get_context_for_session("session-1", limit=10)
llm_context = agent.build_llm_context("session-1", system_prompt="You are helpful.")
```

## Configuration

| Setting | Default | Description |
|---|---|---|
| `database.path` | `data/nexus.db` | SQLite database file path |
| `memory.max_context_length` | `50` | Maximum messages per context window |
| `app.session_id` | `default` | Current session identifier |

### Dependencies

```
sqlite3         — Standard library, no install needed
```

### Optional Dependencies

```
faiss-cpu       — For vector-based semantic similarity search
```

## Capabilities Reference

```
remember, recall, search_memories, save_preference, get_preference,
list_preferences, save_workflow, load_workflow, list_workflows,
get_context, list_memories, delete_memory, clear_memory, memory_stats
```
