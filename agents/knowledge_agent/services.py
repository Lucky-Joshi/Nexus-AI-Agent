"""
Business logic services for the Knowledge Base Agent.
Handles document ingestion, indexing, search, query processing, and summarization.
"""

import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from core.logger import Logger
from core.config import Config
from core.llm_provider import LLMProvider

from .models import (
    KnowledgeDocument, KnowledgeTag, DocumentType, DocumentCategory,
    SearchResult, SummaryResult,
)
from .storage import KnowledgeSQLite, ChromaVectorStore


class TagManager:
    """Manages tags for knowledge documents."""

    def __init__(self, storage: KnowledgeSQLite):
        self.logger = Logger().get_logger("TagManager")
        self._storage = storage

    def add_tag(self, tag_name: str, color: str = "#4A90D9", description: str = "") -> KnowledgeTag:
        tag = self._storage.ensure_tag(tag_name, color, description)
        return tag

    def remove_tag(self, tag_name: str) -> bool:
        return self._storage.delete_tag(tag_name)

    def get_tag(self, tag_name: str) -> Optional[KnowledgeTag]:
        return self._storage.get_tag(tag_name)

    def get_all_tags(self) -> List[KnowledgeTag]:
        return self._storage.get_all_tags()

    def get_documents_by_tag(self, tag_name: str, limit: int = 50) -> List[KnowledgeDocument]:
        return self._storage.get_documents_by_tag(tag_name, limit)

    def add_tags_to_document(self, doc_id: str, tags: List[str]) -> bool:
        doc = self._storage.get_document(doc_id)
        if not doc:
            return False
        for tag in tags:
            if tag not in doc.tags:
                doc.tags.append(tag)
                self._storage.ensure_tag(tag)
                self._storage.increment_tag_usage(tag)
        doc.updated_at = datetime.now().isoformat()
        self._storage.save_document(doc)
        return True

    def remove_tags_from_document(self, doc_id: str, tags: List[str]) -> bool:
        doc = self._storage.get_document(doc_id)
        if not doc:
            return False
        doc.tags = [t for t in doc.tags if t not in tags]
        doc.updated_at = datetime.now().isoformat()
        self._storage.save_document(doc)
        return True

    def get_popular_tags(self, limit: int = 20) -> List[KnowledgeTag]:
        all_tags = self._storage.get_all_tags()
        return sorted(all_tags, key=lambda t: t.usage_count, reverse=True)[:limit]


class DocumentIngestionService:
    """Handles document creation, parsing, and preparation for indexing."""

    def __init__(self, storage: KnowledgeSQLite, tag_manager: TagManager):
        self.logger = Logger().get_logger("DocumentIngestionService")
        self._storage = storage
        self._tag_manager = tag_manager

    def create_document(self, title: str, content: str, doc_type: str = "note",
                        category: str = "general", tags: Optional[List[str]] = None,
                        source: str = "", metadata: Optional[Dict[str, Any]] = None) -> KnowledgeDocument:
        try:
            dt = DocumentType(doc_type)
        except ValueError:
            dt = DocumentType.CUSTOM

        try:
            cat = DocumentCategory(category)
        except ValueError:
            cat = DocumentCategory.GENERAL

        doc = KnowledgeDocument(
            title=title,
            content=content,
            doc_type=dt,
            category=cat,
            tags=tags or [],
            source=source,
            metadata=metadata or {},
            importance=self._calculate_importance(content, tags),
        )

        self._storage.save_document(doc)
        self.logger.info(f"Document created: {doc.id} - {title}")
        return doc

    def import_from_file(self, file_path: str, doc_type: str = "document",
                         category: str = "general", tags: Optional[List[str]] = None) -> Optional[KnowledgeDocument]:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            self.logger.error(f"Failed to read file: {e}")
            return None

        from pathlib import Path
        title = Path(file_path).stem

        doc = self.create_document(
            title=title,
            content=content,
            doc_type=doc_type,
            category=category,
            tags=tags,
            source=file_path,
        )
        return doc

    def batch_import(self, documents: List[Dict[str, Any]]) -> List[KnowledgeDocument]:
        results = []
        for doc_data in documents:
            doc = self.create_document(
                title=doc_data.get("title", "Untitled"),
                content=doc_data.get("content", ""),
                doc_type=doc_data.get("doc_type", "note"),
                category=doc_data.get("category", "general"),
                tags=doc_data.get("tags"),
                source=doc_data.get("source", ""),
                metadata=doc_data.get("metadata"),
            )
            results.append(doc)
        return results

    def _calculate_importance(self, content: str, tags: Optional[List[str]] = None) -> float:
        score = 0.5
        word_count = len(content.split())
        if word_count > 500:
            score += 0.15
        elif word_count > 200:
            score += 0.1
        elif word_count > 50:
            score += 0.05

        if tags:
            score += min(0.1, len(tags) * 0.02)

        has_code = bool(re.search(r"```|def |class |import |function ", content))
        if has_code:
            score += 0.05

        return min(1.0, score)


class IndexingService:
    """Manages vector indexing of documents for semantic search."""

    def __init__(self, storage: KnowledgeSQLite, vector_store: ChromaVectorStore):
        self.logger = Logger().get_logger("IndexingService")
        self._storage = storage
        self._vector_store = vector_store

    def index_document(self, doc_id: str) -> bool:
        doc = self._storage.get_document(doc_id)
        if not doc:
            return False

        text = self._build_indexable_text(doc)
        metadata = {
            "title": doc.title,
            "doc_type": doc.doc_type.value,
            "category": doc.category.value,
            "tags": ",".join(doc.tags),
            "source": doc.source,
            "created_at": doc.created_at,
            "updated_at": doc.updated_at,
            "importance": doc.importance,
        }

        result = self._vector_store.add_document(doc_id, text, metadata)
        if result:
            self._storage.mark_indexed(doc_id, doc_id)
            self.logger.info(f"Document indexed: {doc_id}")
        return result is not None

    def index_all_unindexed(self, batch_size: int = 50) -> int:
        all_docs = self._storage.get_all_documents(limit=10000)
        indexed_ids = set(self._storage.get_indexed_ids())

        to_index = []
        for doc in all_docs:
            if doc.id not in indexed_ids:
                text = self._build_indexable_text(doc)
                metadata = {
                    "title": doc.title,
                    "doc_type": doc.doc_type.value,
                    "category": doc.category.value,
                    "tags": ",".join(doc.tags),
                    "source": doc.source,
                    "created_at": doc.created_at,
                    "updated_at": doc.updated_at,
                    "importance": doc.importance,
                }
                to_index.append((doc.id, text, metadata))

        if not to_index:
            return 0

        indexed = 0
        for i in range(0, len(to_index), batch_size):
            batch = to_index[i:i + batch_size]
            results = self._vector_store.add_documents(batch)
            for doc_id in results:
                self._storage.mark_indexed(doc_id, doc_id)
            indexed += len(results)

        self.logger.info(f"Indexed {indexed} documents")
        return indexed

    def rebuild_index(self) -> bool:
        all_docs = self._storage.get_all_documents(limit=10000)
        documents = []
        for doc in all_docs:
            text = self._build_indexable_text(doc)
            metadata = {
                "title": doc.title,
                "doc_type": doc.doc_type.value,
                "category": doc.category.value,
                "tags": ",".join(doc.tags),
                "source": doc.source,
                "created_at": doc.created_at,
                "updated_at": doc.updated_at,
                "importance": doc.importance,
            }
            documents.append((doc.id, text, metadata))

        success = self._vector_store.rebuild_index(documents)
        if success:
            for doc_id, _, _ in documents:
                self._storage.mark_indexed(doc_id, doc_id)
        return success

    def remove_from_index(self, doc_id: str) -> bool:
        success = self._vector_store.delete_document(doc_id)
        if success:
            self._storage.mark_not_indexed(doc_id)
        return success

    def get_index_stats(self) -> Dict[str, Any]:
        return {
            "vector_count": self._vector_store.get_document_count(),
            "available": self._vector_store.is_available,
        }

    @staticmethod
    def _build_indexable_text(doc: KnowledgeDocument) -> str:
        parts = [doc.title, doc.content]
        if doc.summary:
            parts.append(doc.summary)
        if doc.tags:
            parts.append("tags: " + ", ".join(doc.tags))
        if doc.source:
            parts.append("source: " + doc.source)
        return "\n".join(parts)


class SearchEngine:
    """Multi-strategy search engine combining semantic and keyword search."""

    def __init__(self, storage: KnowledgeSQLite, vector_store: ChromaVectorStore):
        self.logger = Logger().get_logger("SearchEngine")
        self._storage = storage
        self._vector_store = vector_store

    def search(self, query: str, limit: int = 10, category: Optional[str] = None,
               doc_type: Optional[str] = None, tags: Optional[List[str]] = None,
               use_semantic: bool = True) -> List[SearchResult]:
        semantic_results = []
        keyword_results = []

        if use_semantic and self._vector_store.is_available:
            semantic_results = self._semantic_search(query, limit * 2)

        keyword_results = self._keyword_search(query, limit * 2, category, doc_type, tags)

        merged = self._merge_results(semantic_results, keyword_results, limit)

        if tags:
            merged = [r for r in merged if any(t in r.document.tags for t in tags)]

        return merged[:limit]

    def _semantic_search(self, query: str, limit: int = 20) -> List[SearchResult]:
        vector_results = self._vector_store.search(query, n_results=limit)
        results = []
        for item in vector_results:
            doc = self._storage.get_document(item["id"])
            if doc:
                results.append(SearchResult(
                    document=doc,
                    score=item["score"],
                    match_type="semantic",
                    context=item["content"][:300] if item["content"] else "",
                ))
        return results

    def _keyword_search(self, query: str, limit: int = 20,
                        category: Optional[str] = None, doc_type: Optional[str] = None,
                        tags: Optional[List[str]] = None) -> List[SearchResult]:
        docs = self._storage.search_documents(query, category, doc_type, tags, limit)
        results = []
        query_lower = query.lower()
        for doc in docs:
            score = self._keyword_score(doc, query_lower)
            snippets = self._extract_snippets(doc.content, query_lower)
            results.append(SearchResult(
                document=doc,
                score=score,
                match_type="keyword",
                matched_snippets=snippets,
            ))
        return results

    def _merge_results(self, semantic: List[SearchResult],
                       keyword: List[SearchResult], limit: int) -> List[SearchResult]:
        seen = set()
        merged = []

        sem_dict = {r.document.id: r for r in semantic}
        kw_dict = {r.document.id: r for r in keyword}

        all_ids = list(sem_dict.keys()) + [k for k in kw_dict if k not in sem_dict]

        for doc_id in all_ids:
            if doc_id in seen:
                continue
            seen.add(doc_id)

            sem_r = sem_dict.get(doc_id)
            kw_r = kw_dict.get(doc_id)

            if sem_r and kw_r:
                combined_score = sem_r.score * 0.6 + kw_r.score * 0.4
                r = SearchResult(
                    document=sem_r.document,
                    score=combined_score,
                    match_type="hybrid",
                    matched_snippets=kw_r.matched_snippets,
                    context=sem_r.context,
                )
            elif sem_r:
                r = sem_r
            else:
                r = kw_r

            merged.append(r)

        merged.sort(key=lambda x: x.score, reverse=True)
        return merged[:limit]

    @staticmethod
    def _keyword_score(doc: KnowledgeDocument, query_lower: str) -> float:
        score = 0.0
        title_lower = doc.title.lower()
        content_lower = doc.content.lower()

        if query_lower in title_lower:
            score += 0.5
        if query_lower in content_lower:
            score += 0.3

        query_words = query_lower.split()
        for word in query_words:
            if word in title_lower:
                score += 0.1
            if word in content_lower:
                score += 0.05

        score += doc.importance * 0.1
        score += min(0.1, doc.access_count * 0.01)

        return min(1.0, score)

    @staticmethod
    def _extract_snippets(content: str, query_lower: str, max_snippets: int = 3,
                          snippet_size: int = 100) -> List[str]:
        snippets = []
        query_words = query_lower.split()
        content_lower = content.lower()

        for word in query_words:
            idx = content_lower.find(word)
            while idx != -1 and len(snippets) < max_snippets:
                start = max(0, idx - snippet_size // 2)
                end = min(len(content), idx + snippet_size // 2)
                snippet = content[start:end].strip()
                if snippet and snippet not in snippets:
                    snippets.append("..." + snippet + "...")
                idx = content_lower.find(word, idx + 1)

        return snippets[:max_snippets]


class QueryEngine:
    """Processes natural language queries and extracts intent/parameters."""

    def __init__(self, storage: KnowledgeSQLite, search_engine: SearchEngine,
                 llm_provider: Optional[LLMProvider] = None):
        self.logger = Logger().get_logger("QueryEngine")
        self._storage = storage
        self._search_engine = search_engine
        self._llm = llm_provider

    def process_query(self, query: str, limit: int = 10) -> Dict[str, Any]:
        query_lower = query.lower()
        params = self._extract_params(query_lower)

        if params.get("action") == "list_all":
            return self._handle_list_all(params, limit)
        elif params.get("action") == "by_tag":
            return self._handle_by_tag(params, limit)
        elif params.get("action") == "by_category":
            return self._handle_by_category(params, limit)
        elif params.get("action") == "recent":
            return self._handle_recent(params, limit)
        elif params.get("action") == "stats":
            return self._handle_stats()
        else:
            return self._handle_search(query, params, limit)

    def _extract_params(self, query_lower: str) -> Dict[str, Any]:
        params = {"action": "search", "query": query_lower}

        if re.search(r"\b(list all|show all|all documents)\b", query_lower):
            params["action"] = "list_all"
        elif re.search(r"\b(tagged with|tag:|tags:|by tag)\b", query_lower):
            params["action"] = "by_tag"
            tag_match = re.search(r"(?:tagged with|tag:|tags:|by tag)\s+(\w+)", query_lower)
            if tag_match:
                params["tag"] = tag_match.group(1)
        elif re.search(r"\b(category:|in category|by category)\b", query_lower):
            params["action"] = "by_category"
            cat_match = re.search(r"(?:category:|in category|by category)\s+(\w+)", query_lower)
            if cat_match:
                params["category"] = cat_match.group(1)
        elif re.search(r"\b(recent|latest|last|newest)\b", query_lower):
            params["action"] = "recent"
            num_match = re.search(r"\b(\d+)\b", query_lower)
            params["limit"] = int(num_match.group(1)) if num_match else 10
        elif re.search(r"\b(stats|statistics|overview)\b", query_lower):
            params["action"] = "stats"

        type_match = re.search(r"\btype:\s*(\w+)", query_lower)
        if type_match:
            params["doc_type"] = type_match.group(1)

        limit_match = re.search(r"\blimit[:\s]*(\d+)\b", query_lower)
        if limit_match:
            params["limit"] = int(limit_match.group(1))

        return params

    def _handle_search(self, query: str, params: Dict[str, Any], limit: int) -> Dict[str, Any]:
        results = self._search_engine.search(
            query=query,
            limit=params.get("limit", limit),
            category=params.get("category"),
            doc_type=params.get("doc_type"),
            tags=[params["tag"]] if "tag" in params else None,
        )

        if not results:
            return {
                "success": True,
                "response": f"No documents found for: '{query}'",
                "count": 0,
                "results": [],
            }

        lines = [f"Found {len(results)} documents for '{query}':\n"]
        for i, r in enumerate(results, 1):
            doc = r.document
            score_pct = int(r.score * 100)
            lines.append(f"  {i}. [{score_pct}%] {doc.title} (ID: {doc.id})")
            lines.append(f"     Type: {doc.doc_type.value} | Category: {doc.category.value}")
            if doc.tags:
                lines.append(f"     Tags: {', '.join(doc.tags)}")
            if doc.summary:
                lines.append(f"     Summary: {doc.summary[:100]}")
            if r.matched_snippets:
                lines.append(f"     Match: {r.matched_snippets[0]}")
            lines.append("")

        return {
            "success": True,
            "response": "\n".join(lines),
            "count": len(results),
            "results": [r.to_dict() for r in results],
        }

    def _handle_list_all(self, params: Dict[str, Any], limit: int) -> Dict[str, Any]:
        docs = self._storage.get_all_documents(limit=params.get("limit", limit))
        if not docs:
            return {"success": True, "response": "No documents in knowledge base."}

        lines = [f"Knowledge base ({len(docs)} documents):\n"]
        for doc in docs:
            lines.append(f"  - {doc.title} (ID: {doc.id}) [{doc.doc_type.value}]")
        return {
            "success": True,
            "response": "\n".join(lines),
            "count": len(docs),
            "results": [d.to_dict() for d in docs],
        }

    def _handle_by_tag(self, params: Dict[str, Any], limit: int) -> Dict[str, Any]:
        tag = params.get("tag", "")
        if not tag:
            return {"success": False, "response": "Please specify a tag. Example: 'show documents tagged with python'"}

        docs = self._storage.get_documents_by_tag(tag, limit)
        if not docs:
            return {"success": True, "response": f"No documents with tag: '{tag}'"}

        lines = [f"Documents tagged '{tag}' ({len(docs)}):\n"]
        for doc in docs:
            lines.append(f"  - {doc.title} (ID: {doc.id})")
        return {
            "success": True,
            "response": "\n".join(lines),
            "count": len(docs),
            "results": [d.to_dict() for d in docs],
        }

    def _handle_by_category(self, params: Dict[str, Any], limit: int) -> Dict[str, Any]:
        category = params.get("category", "")
        if not category:
            return {"success": False, "response": "Please specify a category."}

        docs = self._storage.get_documents_by_category(category, limit)
        if not docs:
            return {"success": True, "response": f"No documents in category: '{category}'"}

        lines = [f"Documents in '{category}' ({len(docs)}):\n"]
        for doc in docs:
            lines.append(f"  - {doc.title} (ID: {doc.id})")
        return {
            "success": True,
            "response": "\n".join(lines),
            "count": len(docs),
            "results": [d.to_dict() for d in docs],
        }

    def _handle_recent(self, params: Dict[str, Any], limit: int) -> Dict[str, Any]:
        docs = self._storage.get_all_documents(limit=params.get("limit", limit))
        if not docs:
            return {"success": True, "response": "No recent documents."}

        lines = [f"Recent documents ({len(docs)}):\n"]
        for doc in docs:
            created = doc.created_at[:19] if doc.created_at else "N/A"
            lines.append(f"  - {doc.title} (ID: {doc.id}) [{created}]")
        return {
            "success": True,
            "response": "\n".join(lines),
            "count": len(docs),
            "results": [d.to_dict() for d in docs],
        }

    def _handle_stats(self) -> Dict[str, Any]:
        stats = self._storage.get_stats()
        lines = [
            "Knowledge Base Statistics:",
            f"  Total documents: {stats['total_documents']}",
            f"  Indexed documents: {stats['indexed_documents']}",
            f"  Total tags: {stats['total_tags']}",
            "",
            "Categories:",
        ]
        for cat, count in stats["categories"].items():
            lines.append(f"  {cat}: {count}")
        lines.append("")
        lines.append("Types:")
        for t, count in stats["types"].items():
            lines.append(f"  {t}: {count}")

        return {"success": True, "response": "\n".join(lines), "data": stats}


class SummarizationService:
    """Generates AI-powered summaries of knowledge documents."""

    def __init__(self, storage: KnowledgeSQLite, llm_provider: Optional[LLMProvider] = None):
        self.logger = Logger().get_logger("SummarizationService")
        self._storage = storage
        self._llm = llm_provider

    def summarize_document(self, doc_id: str) -> Optional[SummaryResult]:
        doc = self._storage.get_document(doc_id)
        if not doc:
            return None

        if not self._llm:
            summary = self._extractive_summary(doc.content, max_sentences=5)
            return SummaryResult(
                summary=summary,
                source_documents=[doc_id],
                key_points=self._extract_key_points(doc.content),
                model_used="extractive",
            )

        prompt = f"Summarize the following document in 3-5 sentences. Then list 3-5 key points as bullet points.\n\nTitle: {doc.title}\n\n{doc.content[:3000]}"

        try:
            response = self._llm.generate(
                prompt=prompt,
                system_prompt="You are a knowledge summarization expert. Provide concise, accurate summaries.",
            )

            summary_text = response.split("\n\n")[0] if "\n\n" in response else response
            key_points = self._parse_key_points(response)

            doc.summary = summary_text
            self._storage.save_document(doc)

            return SummaryResult(
                summary=summary_text,
                source_documents=[doc_id],
                key_points=key_points,
                model_used=self._llm.get_model(),
            )
        except Exception as e:
            self.logger.error(f"LLM summarization failed, falling back: {e}")
            summary = self._extractive_summary(doc.content, max_sentences=5)
            return SummaryResult(
                summary=summary,
                source_documents=[doc_id],
                key_points=self._extract_key_points(doc.content),
                model_used="extractive",
            )

    def summarize_multiple(self, doc_ids: List[str], max_docs: int = 5) -> Optional[SummaryResult]:
        docs = []
        for doc_id in doc_ids[:max_docs]:
            doc = self._storage.get_document(doc_id)
            if doc:
                docs.append(doc)

        if not docs:
            return None

        if not self._llm:
            combined = "\n\n".join([f"## {d.title}\n{d.content[:500]}" for d in docs])
            summary = self._extractive_summary(combined, max_sentences=8)
            return SummaryResult(
                summary=summary,
                source_documents=[d.id for d in docs],
                model_used="extractive",
            )

        combined_context = "\n\n".join([
            f"Document {i+1}: {d.title}\n{d.content[:1000]}"
            for i, d in enumerate(docs)
        ])

        prompt = f"Synthesize a summary of these {len(docs)} related documents. Identify common themes and key insights.\n\n{combined_context[:4000]}"

        try:
            response = self._llm.generate(
                prompt=prompt,
                system_prompt="You are a research synthesis expert. Find connections and summarize themes across multiple documents.",
            )

            return SummaryResult(
                summary=response,
                source_documents=[d.id for d in docs],
                key_points=self._extract_key_points(response),
                model_used=self._llm.get_model(),
            )
        except Exception as e:
            self.logger.error(f"Multi-doc summarization failed: {e}")
            return None

    def summarize_by_tag(self, tag: str, limit: int = 5) -> Optional[SummaryResult]:
        docs = self._storage.get_documents_by_tag(tag, limit)
        if not docs:
            return None
        return self.summarize_multiple([d.id for d in docs])

    def summarize_by_category(self, category: str, limit: int = 5) -> Optional[SummaryResult]:
        docs = self._storage.get_documents_by_category(category, limit)
        if not docs:
            return None
        return self.summarize_multiple([d.id for d in docs])

    @staticmethod
    def _extractive_summary(content: str, max_sentences: int = 5) -> str:
        sentences = re.split(r"(?<=[.!?])\s+", content.replace("\n", " "))
        if len(sentences) <= max_sentences:
            return content[:1000]
        return " ".join(sentences[:max_sentences]) + "..."

    @staticmethod
    def _extract_key_points(content: str) -> List[str]:
        sentences = re.split(r"(?<=[.!?])\s+", content.replace("\n", " "))
        scored = []
        for i, sent in enumerate(sentences):
            score = 0
            sent_lower = sent.lower()
            important_words = ["important", "key", "main", "primary", "essential", "critical",
                              "significant", "must", "should", "need", "require", "result",
                              "conclusion", "therefore", "thus", "hence"]
            for word in important_words:
                if word in sent_lower:
                    score += 1
            if len(sent.split()) > 5:
                score += 0.5
            if i < 3:
                score += 1
            scored.append((score, sent))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [s[1] for s in scored[:5]]

    @staticmethod
    def _parse_key_points(response: str) -> List[str]:
        points = []
        for line in response.split("\n"):
            line = line.strip()
            if line.startswith(("-", "*", "•")) or re.match(r"^\d+[\.\)]\s", line):
                point = re.sub(r"^[-*•]|\d+[\.\)]\s*", "", line).strip()
                if point:
                    points.append(point)
        return points[:5] if points else []
