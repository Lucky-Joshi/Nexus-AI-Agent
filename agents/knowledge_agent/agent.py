"""
Knowledge Base Agent for NEXUS.
Provides searchable internal knowledge system with document storage, semantic search,
tagging, indexing, and AI-powered summarization.
"""

import re
from typing import Any, Dict, List, Optional

from core.base_agent import BaseAgent, AgentStatus
from core.logger import Logger
from core.config import Config
from core.llm_provider import LLMProvider

from .models import DocumentType, DocumentCategory
from .storage import KnowledgeSQLite, ChromaVectorStore
from .services import (
    DocumentIngestionService, IndexingService, SearchEngine,
    QueryEngine, SummarizationService, TagManager,
)


class KnowledgeAgent(BaseAgent):
    """
    Knowledge Base agent for NEXUS.
    Thin orchestrator delegating to specialized service classes.
    """

    def __init__(self):
        super().__init__("knowledge_agent", "Knowledge base, document storage, semantic search, and summarization")
        self.logger = Logger().get_logger("KnowledgeAgent")
        self.config = Config()

        self._sqlite = KnowledgeSQLite()
        self._vector_store = ChromaVectorStore(
            embedding_model=self.config.get("knowledge_agent.embedding_model", "all-MiniLM-L6-v2")
        )

        self._tag_manager = TagManager(storage=self._sqlite)
        self._ingestion = DocumentIngestionService(storage=self._sqlite, tag_manager=self._tag_manager)
        self._indexing = IndexingService(storage=self._sqlite, vector_store=self._vector_store)
        self._search_engine = SearchEngine(storage=self._sqlite, vector_store=self._vector_store)

        llm = None
        if self.config.get("llm.use_in_agents", True):
            try:
                llm = LLMProvider(self.config)
            except Exception as e:
                self.logger.warning(f"LLM not available for KnowledgeAgent: {e}")

        self._query_engine = QueryEngine(
            storage=self._sqlite, search_engine=self._search_engine, llm_provider=llm
        )
        self._summarization = SummarizationService(storage=self._sqlite, llm_provider=llm)

        self.logger.info(f"KnowledgeAgent initialized (vector store: {'available' if self._vector_store.is_available else 'unavailable'})")

    def execute(self, command: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        self.status = AgentStatus.BUSY
        try:
            cmd = command.lower()

            if self._matches(cmd, ["add document", "add note", "create document", "save knowledge", "store document"]):
                return self._handle_add(command)

            elif self._matches(cmd, ["search knowledge", "search documents", "find document", "knowledge search"]):
                return self._handle_search(command)

            elif self._matches(cmd, ["get document", "show document", "view document", "read document"]):
                return self._handle_get(command)

            elif self._matches(cmd, ["delete document", "remove document"]):
                return self._handle_delete(command)

            elif self._matches(cmd, ["list documents", "list knowledge", "show all documents"]):
                return self._handle_list(command)

            elif self._matches(cmd, ["add tag", "tag document"]):
                return self._handle_add_tag(command)

            elif self._matches(cmd, ["remove tag", "untag"]):
                return self._handle_remove_tag(command)

            elif self._matches(cmd, ["list tags", "show tags", "all tags"]):
                return self._handle_list_tags()

            elif self._matches(cmd, ["summarize document", "summarize", "generate summary"]):
                return self._handle_summarize(command)

            elif self._matches(cmd, ["summarize tag", "tag summary"]):
                return self._handle_summarize_tag(command)

            elif self._matches(cmd, ["index document", "index all", "rebuild index", "reindex"]):
                return self._handle_index(command)

            elif self._matches(cmd, ["import file", "import document", "load file"]):
                return self._handle_import(command)

            elif self._matches(cmd, ["knowledge stats", "knowledge base stats", "kb stats"]):
                return self._handle_stats()

            elif self._matches(cmd, ["recent documents", "recent knowledge", "latest documents"]):
                return self._handle_recent(command)

            elif self._matches(cmd, ["documents by tag", "tagged with"]):
                return self._handle_by_tag(command)

            elif self._matches(cmd, ["documents by category", "category:"]):
                return self._handle_by_category(command)

            else:
                return self._handle_search(command)

        except Exception as e:
            self.logger.error(f"KnowledgeAgent error: {e}")
            return {
                "success": False,
                "response": f"Knowledge base error: {str(e)}",
                "error": str(e),
            }
        finally:
            self.status = AgentStatus.IDLE

    def get_capabilities(self) -> list:
        return [
            "add_document",
            "search_knowledge",
            "get_document",
            "delete_document",
            "list_documents",
            "add_tag",
            "remove_tag",
            "list_tags",
            "summarize_document",
            "summarize_by_tag",
            "index_document",
            "index_all",
            "rebuild_index",
            "import_file",
            "knowledge_stats",
            "recent_documents",
            "documents_by_tag",
            "documents_by_category",
        ]

    def add_document(self, title: str, content: str, doc_type: str = "note",
                     category: str = "general", tags: Optional[List[str]] = None,
                     source: str = "", auto_index: bool = True) -> Dict[str, Any]:
        """Programmatic API: add a document to the knowledge base."""
        doc = self._ingestion.create_document(
            title=title, content=content, doc_type=doc_type,
            category=category, tags=tags, source=source,
        )
        if auto_index and self._vector_store.is_available:
            self._indexing.index_document(doc.id)
        return {"success": True, "data": doc.to_dict()}

    def search(self, query: str, limit: int = 10, use_semantic: bool = True) -> Dict[str, Any]:
        """Programmatic API: search the knowledge base."""
        return self._query_engine.process_query(query, limit)

    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Programmatic API: get a document by ID."""
        doc = self._sqlite.get_document(doc_id)
        return doc.to_dict() if doc else None

    def delete_document(self, doc_id: str) -> bool:
        """Programmatic API: delete a document."""
        self._indexing.remove_from_index(doc_id)
        return self._sqlite.delete_document(doc_id)

    def summarize_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Programmatic API: summarize a document."""
        result = self._summarization.summarize_document(doc_id)
        return result.to_dict() if result else None

    def get_context_for_query(self, query: str, max_docs: int = 3) -> str:
        """Programmatic API: retrieve relevant context for a query (used by other agents)."""
        results = self._search_engine.search(query, limit=max_docs)
        if not results:
            return ""
        context_parts = []
        for r in results:
            doc = r.document
            context_parts.append(f"Document: {doc.title}\n{doc.content[:500]}")
        return "\n\n---\n\n".join(context_parts)

    def _handle_add(self, command: str) -> Dict[str, Any]:
        title = self._extract_field(command, ["title:", "title is"])
        content = self._extract_content(command, [
            "add document", "add note", "create document", "save knowledge", "store document",
        ])

        if not content:
            return {
                "success": False,
                "response": "Usage: 'add document [title: X] [content]'\nExample: 'add document title: Python Tips Python is a versatile language...'",
            }

        if not title:
            title = content[:50] + "..." if len(content) > 50 else content

        doc_type = self._extract_field(command, ["type:", "doc type:"]) or "note"
        category = self._extract_field(command, ["category:", "cat:"]) or "general"
        tags = self._extract_tags(command)
        source = self._extract_field(command, ["source:", "from:"]) or ""

        doc = self._ingestion.create_document(
            title=title, content=content, doc_type=doc_type,
            category=category, tags=tags, source=source,
        )

        indexed = False
        if self._vector_store.is_available:
            indexed = self._indexing.index_document(doc.id)

        response = f"Document added (ID: {doc.id})\nTitle: {doc.title}\nType: {doc.doc_type.value}\nCategory: {doc.category.value}"
        if tags:
            response += f"\nTags: {', '.join(tags)}"
        if indexed:
            response += "\nIndexed: Yes (semantic search enabled)"

        return {
            "success": True,
            "response": response,
            "data": doc.to_dict(),
        }

    def _handle_search(self, command: str) -> Dict[str, Any]:
        query = self._extract_content(command, [
            "search knowledge", "search documents", "find document", "knowledge search",
        ])
        if not query:
            return {"success": False, "response": "Please provide a search query."}

        limit = self._extract_number(command, default=10)
        return self._query_engine.process_query(query, limit)

    def _handle_get(self, command: str) -> Dict[str, Any]:
        doc_id = self._extract_id(command)
        if not doc_id:
            return {"success": False, "response": "Please provide a document ID."}

        doc = self._sqlite.get_document(doc_id)
        if not doc:
            return {"success": False, "response": f"Document {doc_id} not found."}

        lines = [
            f"Document: {doc.title} (ID: {doc.id})",
            f"Type: {doc.doc_type.value} | Category: {doc.category.value}",
            f"Created: {doc.created_at[:19]}",
            f"Access count: {doc.access_count}",
        ]
        if doc.tags:
            lines.append(f"Tags: {', '.join(doc.tags)}")
        if doc.source:
            lines.append(f"Source: {doc.source}")
        if doc.summary:
            lines.append(f"\nSummary: {doc.summary}")
        lines.append(f"\nContent:\n{doc.content[:2000]}")
        if len(doc.content) > 2000:
            lines.append(f"\n... ({len(doc.content) - 2000} more characters)")

        return {
            "success": True,
            "response": "\n".join(lines),
            "data": doc.to_dict(),
        }

    def _handle_delete(self, command: str) -> Dict[str, Any]:
        doc_id = self._extract_id(command)
        if not doc_id:
            return {"success": False, "response": "Please provide a document ID."}

        self._indexing.remove_from_index(doc_id)
        success = self._sqlite.delete_document(doc_id)
        if success:
            return {"success": True, "response": f"Document {doc_id} deleted."}
        return {"success": False, "response": f"Document {doc_id} not found."}

    def _handle_list(self, command: str) -> Dict[str, Any]:
        limit = self._extract_number(command, default=20)
        return self._query_engine.process_query("list all documents", limit)

    def _handle_add_tag(self, command: str) -> Dict[str, Any]:
        doc_id = self._extract_id(command)
        tag_match = re.search(r"(?:tag:|tagged?\s+(?:with\s+)?)([a-zA-Z0-9_-]+)", command.lower())
        tag = tag_match.group(1) if tag_match else None

        if not doc_id or not tag:
            return {
                "success": False,
                "response": "Usage: 'add tag [tag: python] to document [id]'\nExample: 'tag document abc12345 with python'",
            }

        success = self._tag_manager.add_tags_to_document(doc_id, [tag])
        if success:
            return {"success": True, "response": f"Tag '{tag}' added to document {doc_id}."}
        return {"success": False, "response": f"Document {doc_id} not found."}

    def _handle_remove_tag(self, command: str) -> Dict[str, Any]:
        doc_id = self._extract_id(command)
        tag_match = re.search(r"(?:tag:|tagged?\s+(?:with\s+)?)([a-zA-Z0-9_-]+)", command.lower())
        tag = tag_match.group(1) if tag_match else None

        if not doc_id or not tag:
            return {"success": False, "response": "Please provide document ID and tag to remove."}

        success = self._tag_manager.remove_tags_from_document(doc_id, [tag])
        if success:
            return {"success": True, "response": f"Tag '{tag}' removed from document {doc_id}."}
        return {"success": False, "response": f"Document {doc_id} not found."}

    def _handle_list_tags(self) -> Dict[str, Any]:
        tags = self._tag_manager.get_popular_tags(limit=30)
        if not tags:
            return {"success": True, "response": "No tags in knowledge base."}

        lines = [f"Tags ({len(tags)}):\n"]
        for tag in tags:
            lines.append(f"  {tag.name} (used {tag.usage_count} times)")
        return {
            "success": True,
            "response": "\n".join(lines),
            "data": [t.to_dict() for t in tags],
        }

    def _handle_summarize(self, command: str) -> Dict[str, Any]:
        doc_id = self._extract_id(command)
        if not doc_id:
            return {"success": False, "response": "Please provide a document ID to summarize."}

        result = self._summarization.summarize_document(doc_id)
        if not result:
            return {"success": False, "response": f"Document {doc_id} not found."}

        lines = [f"Summary of document {doc_id}:\n"]
        lines.append(result.summary)
        if result.key_points:
            lines.append("\nKey Points:")
            for point in result.key_points:
                lines.append(f"  - {point}")
        lines.append(f"\nModel: {result.model_used}")

        return {
            "success": True,
            "response": "\n".join(lines),
            "data": result.to_dict(),
        }

    def _handle_summarize_tag(self, command: str) -> Dict[str, Any]:
        tag_match = re.search(r"(?:tag:|tagged?\s+(?:with\s+)?)([a-zA-Z0-9_-]+)", command.lower())
        tag = tag_match.group(1) if tag_match else None

        if not tag:
            return {"success": False, "response": "Please specify a tag to summarize."}

        result = self._summarization.summarize_by_tag(tag)
        if not result:
            return {"success": False, "response": f"No documents with tag '{tag}'."}

        lines = [f"Summary of tag '{tag}':\n"]
        lines.append(result.summary)
        if result.key_points:
            lines.append("\nKey Points:")
            for point in result.key_points:
                lines.append(f"  - {point}")
        lines.append(f"\nSources: {len(result.source_documents)} documents")

        return {
            "success": True,
            "response": "\n".join(lines),
            "data": result.to_dict(),
        }

    def _handle_index(self, command: str) -> Dict[str, Any]:
        cmd = command.lower()

        if "rebuild index" in cmd or "reindex" in cmd:
            success = self._indexing.rebuild_index()
            return {
                "success": success,
                "response": "Index rebuilt successfully." if success else "Index rebuild failed.",
            }

        if "index all" in cmd:
            count = self._indexing.index_all_unindexed()
            return {
                "success": True,
                "response": f"Indexed {count} documents." if count else "No unindexed documents found.",
            }

        doc_id = self._extract_id(command)
        if not doc_id:
            return {"success": False, "response": "Please provide a document ID or use 'index all'."}

        success = self._indexing.index_document(doc_id)
        return {
            "success": success,
            "response": f"Document {doc_id} indexed." if success else f"Failed to index document {doc_id}.",
        }

    def _handle_import(self, command: str) -> Dict[str, Any]:
        file_path = self._extract_field(command, ["file:", "path:", "from:"])
        if not file_path:
            path_match = re.search(r"(?:import\s+)(.+?)(?:\s+(?:as|with|type|category|$))", command)
            if path_match:
                file_path = path_match.group(1).strip()

        if not file_path:
            return {"success": False, "response": "Please provide a file path to import."}

        doc_type = self._extract_field(command, ["type:", "doc type:"]) or "document"
        category = self._extract_field(command, ["category:", "cat:"]) or "general"
        tags = self._extract_tags(command)

        doc = self._ingestion.import_from_file(
            file_path=file_path, doc_type=doc_type, category=category, tags=tags,
        )
        if not doc:
            return {"success": False, "response": f"Failed to import file: {file_path}"}

        indexed = False
        if self._vector_store.is_available:
            indexed = self._indexing.index_document(doc.id)

        response = f"File imported (ID: {doc.id})\nTitle: {doc.title}\nWords: {doc.word_count()}"
        if indexed:
            response += "\nIndexed: Yes"

        return {
            "success": True,
            "response": response,
            "data": doc.to_dict(),
        }

    def _handle_stats(self) -> Dict[str, Any]:
        return self._query_engine.process_query("knowledge stats")

    def _handle_recent(self, command: str) -> Dict[str, Any]:
        limit = self._extract_number(command, default=10)
        return self._query_engine.process_query(f"show {limit} recent documents", limit)

    def _handle_by_tag(self, command: str) -> Dict[str, Any]:
        tag_match = re.search(r"(?:tagged with|tag:|tags:|by tag)\s+(\w+)", command.lower())
        tag = tag_match.group(1) if tag_match else None
        if not tag:
            return {"success": False, "response": "Please specify a tag."}
        return self._query_engine.process_query(f"documents tagged with {tag}")

    def _handle_by_category(self, command: str) -> Dict[str, Any]:
        cat_match = re.search(r"(?:category:|in category|by category)\s+(\w+)", command.lower())
        category = cat_match.group(1) if cat_match else None
        if not category:
            return {"success": False, "response": "Please specify a category."}
        return self._query_engine.process_query(f"documents in category {category}")

    @staticmethod
    def _matches(text: str, keywords: list) -> bool:
        return any(kw in text for kw in keywords)

    @staticmethod
    def _extract_content(command: str, prefixes: List[str]) -> str:
        cmd_lower = command.lower()
        for prefix in prefixes:
            if cmd_lower.startswith(prefix):
                return command[len(prefix):].strip()
        return ""

    @staticmethod
    def _extract_field(command: str, prefixes: List[str]) -> Optional[str]:
        cmd_lower = command.lower()
        for prefix in prefixes:
            idx = cmd_lower.find(prefix)
            if idx != -1:
                start = idx + len(prefix)
                rest = command[start:].strip()
                end_match = re.search(r"\s+(?:title:|type:|category:|cat:|tag:|tags:|source:|from:|content:)", rest.lower())
                if end_match:
                    return rest[:end_match.start()].strip()
                return rest.split("\n")[0].strip()
        return None

    @staticmethod
    def _extract_tags(command: str) -> List[str]:
        tags = []
        tag_matches = re.findall(r"(?:tags?:|tagged with)\s*([a-zA-Z0-9_,-]+)", command.lower())
        for match in tag_matches:
            tags.extend([t.strip() for t in match.split(",") if t.strip()])
        return list(set(tags))

    @staticmethod
    def _extract_number(command: str, default: int = 0) -> int:
        match = re.search(r"\b(\d+)\b", command)
        return int(match.group(1)) if match else default

    @staticmethod
    def _extract_id(command: str) -> Optional[str]:
        match = re.search(r"\b([a-f0-9]{8})\b", command.lower())
        return match.group(1) if match else None
