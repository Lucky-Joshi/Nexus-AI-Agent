# Knowledge Agent

> **NEXUS Agent** — Knowledge base, document storage, semantic search, and AI-powered summarization.

## Purpose

The Knowledge Agent serves as NEXUS's internal searchable knowledge system. It provides persistent document storage, hybrid search (keyword + semantic vector), tagging, categorization, and AI-powered summarization capabilities. Other agents use it to retrieve context for queries, and users interact with it to build and query a personal knowledge base.

## Architecture

```
knowledge_agent/
├── __init__.py          # Package initialization
├── agent.py             # Main orchestrator (KnowledgeAgent)
├── models.py            # Data models (Document, Tag, SearchResult, Summary)
├── services.py          # Business logic services
│   ├── TagManager
│   ├── DocumentIngestionService
│   ├── IndexingService
│   ├── SearchEngine
│   ├── QueryEngine
│   └── SummarizationService
└── storage.py           # Persistence backends
    ├── KnowledgeSQLite  # SQLite for metadata/relational data
    └── ChromaVectorStore # ChromaDB for vector embeddings
```

The agent follows a thin-orchestrator pattern: `KnowledgeAgent` delegates to specialized service classes, each with a single responsibility. Storage is split between SQLite (documents, tags, metadata) and ChromaDB (vector embeddings for semantic search).

## Capabilities

| Capability | Description |
|---|---|
| `add_document` | Create documents with title, content, type, category, tags, and source |
| `search_knowledge` | Hybrid search combining semantic (ChromaDB) and keyword (SQLite) strategies |
| `get_document` | Retrieve a document by ID with access tracking |
| `delete_document` | Remove a document and its vector index entry |
| `list_documents` | List all documents with pagination |
| `add_tag` / `remove_tag` | Manage document tags |
| `list_tags` | Show all tags sorted by usage count |
| `summarize_document` | AI-powered summary with key points (LLM or extractive fallback) |
| `summarize_by_tag` | Cross-document synthesis for a tag |
| `index_document` / `index_all` / `rebuild_index` | Manage vector index |
| `import_file` | Import documents from local files |
| `knowledge_stats` | Knowledge base statistics |
| `recent_documents` | Recently added documents |
| `documents_by_tag` / `documents_by_category` | Filtered document lists |
| `get_context_for_query` | **Cross-agent API** — retrieve relevant context for other agents |

## Internal Structure

### Data Models (`models.py`)

- **`KnowledgeDocument`** — Core document with ID, title, content, type, category, tags, source, summary, importance score, and access tracking
- **`KnowledgeTag`** — Tag with name, color, description, and usage count
- **`SearchResult`** — Search result with document, relevance score, match type, and snippets
- **`SummaryResult`** — AI-generated summary with key points and model attribution
- **`DocumentType`** enum: note, article, research, snippet, document, web_page, code, tutorial, reference, custom
- **`DocumentCategory`** enum: general, technical, personal, work, research, reference, project, learning

### Services (`services.py`)

- **`TagManager`** — CRUD for tags, document-tag associations, popularity tracking
- **`DocumentIngestionService`** — Document creation, file import, batch import, importance scoring
- **`IndexingService`** — Vector indexing, batch indexing, index rebuild, index stats
- **`SearchEngine`** — Multi-strategy search: semantic (ChromaDB cosine similarity) + keyword (SQLite LIKE) with hybrid merging (60/40 weighted)
- **`QueryEngine`** — Natural language query parsing, intent extraction, action routing
- **`SummarizationService`** — LLM-powered summarization with extractive fallback, multi-document synthesis, tag/category aggregation

### Storage (`storage.py`)

- **`KnowledgeSQLite`** — SQLite with WAL mode, foreign keys, indexed tables for documents, tags, and document-tag junction
- **`ChromaVectorStore`** — ChromaDB persistent client with SentenceTransformer embeddings (`all-MiniLM-L6-v2` default), cosine similarity, batch operations

## Usage Examples

### Natural Language Commands

```
add document title: Python Tips Python is a versatile language...
search knowledge how to use decorators
get document abc12345
tag document abc12345 with python
summarize document abc12345
index all
import file C:\notes\meeting.md type: document category: work
knowledge stats
recent documents 5
documents by tag python
documents in category technical
```

### Programmatic API

```python
from agents.knowledge_agent.agent import KnowledgeAgent

agent = KnowledgeAgent()

# Add a document
result = agent.add_document(
    title="API Design Patterns",
    content="RESTful APIs follow resource-oriented design...",
    doc_type="article",
    category="technical",
    tags=["api", "design", "rest"],
)

# Search
results = agent.search("API design patterns", limit=5)

# Get context for another agent
context = agent.get_context_for_query("How do I design a REST API?", max_docs=3)

# Summarize
summary = agent.summarize_document("abc12345")
```

## Configuration

| Config Key | Default | Description |
|---|---|---|
| `knowledge_agent.embedding_model` | `all-MiniLM-L6-v2` | SentenceTransformer model for embeddings |
| `knowledge_agent.vector_store_path` | `data/knowledge_vectors` | ChromaDB persistence directory |
| `database.path` | `data/nexus.db` | SQLite database path |
| `llm.use_in_agents` | `true` | Enable LLM for summarization (falls back to extractive if unavailable) |

## Dependencies

- `chromadb` — Vector database for semantic search
- `sentence-transformers` — Embedding model (via ChromaDB)
- SQLite (built-in) — Relational storage
- `core.llm_provider` — Optional LLM for AI summarization
