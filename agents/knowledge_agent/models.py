"""
Data models for the Knowledge Base Agent.
Defines document types, tags, search results, and summary structures.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class DocumentType(Enum):
    """Type of knowledge document."""
    NOTE = "note"
    ARTICLE = "article"
    RESEARCH = "research"
    SNIPPET = "snippet"
    DOCUMENT = "document"
    WEB_PAGE = "web_page"
    CODE = "code"
    TUTORIAL = "tutorial"
    REFERENCE = "reference"
    CUSTOM = "custom"


class DocumentCategory(Enum):
    """Category for organizing knowledge."""
    GENERAL = "general"
    TECHNICAL = "technical"
    PERSONAL = "personal"
    WORK = "work"
    RESEARCH = "research"
    REFERENCE = "reference"
    PROJECT = "project"
    LEARNING = "learning"


@dataclass
class KnowledgeTag:
    """Tag for categorizing and filtering documents."""
    name: str
    color: str = "#4A90D9"
    description: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    usage_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "color": self.color,
            "description": self.description,
            "created_at": self.created_at,
            "usage_count": self.usage_count,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeTag":
        return cls(
            name=data["name"],
            color=data.get("color", "#4A90D9"),
            description=data.get("description", ""),
            created_at=data.get("created_at", datetime.now().isoformat()),
            usage_count=data.get("usage_count", 0),
        )


@dataclass
class KnowledgeDocument:
    """Core knowledge document with metadata and content."""
    title: str
    content: str
    doc_type: DocumentType = DocumentType.NOTE
    category: DocumentCategory = DocumentCategory.GENERAL
    tags: List[str] = field(default_factory=list)
    source: str = ""
    summary: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    access_count: int = 0
    last_accessed: str = ""
    importance: float = 0.5
    is_indexed: bool = False
    embedding_id: str = ""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "doc_type": self.doc_type.value,
            "category": self.category.value,
            "tags": self.tags,
            "source": self.source,
            "summary": self.summary,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "access_count": self.access_count,
            "last_accessed": self.last_accessed,
            "importance": self.importance,
            "is_indexed": self.is_indexed,
            "embedding_id": self.embedding_id,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeDocument":
        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            title=data["title"],
            content=data["content"],
            doc_type=DocumentType(data.get("doc_type", "note")),
            category=DocumentCategory(data.get("category", "general")),
            tags=data.get("tags", []),
            source=data.get("source", ""),
            summary=data.get("summary", ""),
            metadata=data.get("metadata", {}),
            created_at=data.get("created_at", datetime.now().isoformat()),
            updated_at=data.get("updated_at", datetime.now().isoformat()),
            access_count=data.get("access_count", 0),
            last_accessed=data.get("last_accessed", ""),
            importance=data.get("importance", 0.5),
            is_indexed=data.get("is_indexed", False),
            embedding_id=data.get("embedding_id", ""),
        )

    def word_count(self) -> int:
        return len(self.content.split())

    def touch(self):
        """Update access metadata."""
        self.access_count += 1
        self.last_accessed = datetime.now().isoformat()


@dataclass
class SearchResult:
    """Result from a knowledge base search."""
    document: KnowledgeDocument
    score: float
    match_type: str = "semantic"
    matched_snippets: List[str] = field(default_factory=list)
    context: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "document": self.document.to_dict(),
            "score": self.score,
            "match_type": self.match_type,
            "matched_snippets": self.matched_snippets,
            "context": self.context,
        }


@dataclass
class SummaryResult:
    """AI-generated summary of knowledge documents."""
    summary: str
    source_documents: List[str] = field(default_factory=list)
    key_points: List[str] = field(default_factory=list)
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    model_used: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "summary": self.summary,
            "source_documents": self.source_documents,
            "key_points": self.key_points,
            "generated_at": self.generated_at,
            "model_used": self.model_used,
        }
