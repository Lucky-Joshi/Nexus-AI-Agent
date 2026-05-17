"""
Storage backends for the Knowledge Base Agent.
Provides SQLite for metadata/relational data and ChromaDB for vector embeddings.
"""

import json
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from core.logger import Logger
from core.config import Config

from .models import KnowledgeDocument, KnowledgeTag, DocumentType, DocumentCategory


class KnowledgeSQLite:
    """SQLite storage for knowledge documents, tags, and metadata."""

    def __init__(self, db_path: Optional[str] = None):
        self.logger = Logger().get_logger("KnowledgeSQLite")
        if db_path is None:
            config = Config()
            db_path = config.get("database.path", "data/nexus.db")
        self._db_path = str(Path(__file__).parent.parent.parent / db_path)
        os.makedirs(os.path.dirname(self._db_path), exist_ok=True)
        self._initialize()

    def _initialize(self):
        with self._get_connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS knowledge_documents (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    doc_type TEXT DEFAULT 'note',
                    category TEXT DEFAULT 'general',
                    tags TEXT DEFAULT '[]',
                    source TEXT DEFAULT '',
                    summary TEXT DEFAULT '',
                    metadata TEXT DEFAULT '{}',
                    created_at TEXT,
                    updated_at TEXT,
                    access_count INTEGER DEFAULT 0,
                    last_accessed TEXT DEFAULT '',
                    importance REAL DEFAULT 0.5,
                    is_indexed INTEGER DEFAULT 0,
                    embedding_id TEXT DEFAULT ''
                );

                CREATE TABLE IF NOT EXISTS knowledge_tags (
                    name TEXT PRIMARY KEY,
                    color TEXT DEFAULT '#4A90D9',
                    description TEXT DEFAULT '',
                    created_at TEXT,
                    usage_count INTEGER DEFAULT 0
                );

                CREATE TABLE IF NOT EXISTS document_tags (
                    document_id TEXT,
                    tag_name TEXT,
                    PRIMARY KEY (document_id, tag_name),
                    FOREIGN KEY (document_id) REFERENCES knowledge_documents(id) ON DELETE CASCADE,
                    FOREIGN KEY (tag_name) REFERENCES knowledge_tags(name) ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS idx_knowledge_title ON knowledge_documents(title);
                CREATE INDEX IF NOT EXISTS idx_knowledge_category ON knowledge_documents(category);
                CREATE INDEX IF NOT EXISTS idx_knowledge_type ON knowledge_documents(doc_type);
                CREATE INDEX IF NOT EXISTS idx_knowledge_created ON knowledge_documents(created_at);
                CREATE INDEX IF NOT EXISTS idx_knowledge_importance ON knowledge_documents(importance);
                CREATE INDEX IF NOT EXISTS idx_knowledge_access ON knowledge_documents(access_count);
            """)
        self.logger.info("Knowledge SQLite initialized")

    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def save_document(self, doc: KnowledgeDocument) -> bool:
        with self._get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO knowledge_documents
                (id, title, content, doc_type, category, tags, source, summary,
                 metadata, created_at, updated_at, access_count, last_accessed,
                 importance, is_indexed, embedding_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                doc.id, doc.title, doc.content, doc.doc_type.value, doc.category.value,
                json.dumps(doc.tags), doc.source, doc.summary,
                json.dumps(doc.metadata), doc.created_at, doc.updated_at,
                doc.access_count, doc.last_accessed, doc.importance,
                int(doc.is_indexed), doc.embedding_id,
            ))
        for tag_name in doc.tags:
            self.ensure_tag(tag_name)
            self._link_tag(doc.id, tag_name)
        return True

    def get_document(self, doc_id: str) -> Optional[KnowledgeDocument]:
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM knowledge_documents WHERE id = ?", (doc_id,)
            ).fetchone()
        if not row:
            return None
        doc = self._row_to_document(row)
        doc.touch()
        self.save_document(doc)
        return doc

    def get_all_documents(self, limit: int = 100, offset: int = 0) -> List[KnowledgeDocument]:
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM knowledge_documents ORDER BY created_at DESC LIMIT ? OFFSET ?",
                (limit, offset),
            ).fetchall()
        return [self._row_to_document(r) for r in rows]

    def search_documents(self, query: str, category: Optional[str] = None,
                         doc_type: Optional[str] = None, tags: Optional[List[str]] = None,
                         limit: int = 20) -> List[KnowledgeDocument]:
        conditions = []
        params = []

        if query:
            conditions.append("(title LIKE ? OR content LIKE ? OR summary LIKE ?)")
            params.extend([f"%{query}%", f"%{query}%", f"%{query}%"])
        if category:
            conditions.append("category = ?")
            params.append(category)
        if doc_type:
            conditions.append("doc_type = ?")
            params.append(doc_type)

        sql = f"SELECT * FROM knowledge_documents"
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        sql += " ORDER BY importance DESC, access_count DESC, created_at DESC LIMIT ?"
        params.append(limit)

        with self._get_connection() as conn:
            rows = conn.execute(sql, params).fetchall()

        docs = [self._row_to_document(r) for r in rows]

        if tags:
            docs = [d for d in docs if any(t in d.tags for t in tags)]

        return docs

    def get_documents_by_tag(self, tag_name: str, limit: int = 50) -> List[KnowledgeDocument]:
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT kd.* FROM knowledge_documents kd
                JOIN document_tags dt ON kd.id = dt.document_id
                WHERE dt.tag_name = ?
                ORDER BY kd.importance DESC, kd.access_count DESC
                LIMIT ?
            """, (tag_name, limit)).fetchall()
        return [self._row_to_document(r) for r in rows]

    def get_documents_by_category(self, category: str, limit: int = 50) -> List[KnowledgeDocument]:
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM knowledge_documents WHERE category = ? ORDER BY created_at DESC LIMIT ?",
                (category, limit),
            ).fetchall()
        return [self._row_to_document(r) for r in rows]

    def delete_document(self, doc_id: str) -> bool:
        with self._get_connection() as conn:
            cursor = conn.execute("DELETE FROM knowledge_documents WHERE id = ?", (doc_id,))
        return cursor.rowcount > 0

    def update_document(self, doc_id: str, updates: Dict[str, Any]) -> bool:
        doc = self.get_document(doc_id)
        if not doc:
            return False
        for key, value in updates.items():
            if hasattr(doc, key):
                setattr(doc, key, value)
        doc.updated_at = doc.updated_at  # Keep original
        from datetime import datetime
        doc.updated_at = datetime.now().isoformat()
        self.save_document(doc)
        return True

    def get_stats(self) -> Dict[str, Any]:
        with self._get_connection() as conn:
            total = conn.execute("SELECT COUNT(*) FROM knowledge_documents").fetchone()[0]
            indexed = conn.execute("SELECT COUNT(*) FROM knowledge_documents WHERE is_indexed = 1").fetchone()[0]
            total_tags = conn.execute("SELECT COUNT(*) FROM knowledge_tags").fetchone()[0]
            categories = conn.execute(
                "SELECT category, COUNT(*) as cnt FROM knowledge_documents GROUP BY category ORDER BY cnt DESC"
            ).fetchall()
            types = conn.execute(
                "SELECT doc_type, COUNT(*) as cnt FROM knowledge_documents GROUP BY doc_type ORDER BY cnt DESC"
            ).fetchall()

        return {
            "total_documents": total,
            "indexed_documents": indexed,
            "total_tags": total_tags,
            "categories": {r["category"]: r["cnt"] for r in categories},
            "types": {r["doc_type"]: r["cnt"] for r in types},
        }

    def ensure_tag(self, tag_name: str, color: str = "#4A90D9", description: str = "") -> KnowledgeTag:
        existing = self.get_tag(tag_name)
        if existing:
            return existing
        tag = KnowledgeTag(name=tag_name, color=color, description=description)
        self.save_tag(tag)
        return tag

    def save_tag(self, tag: KnowledgeTag) -> bool:
        with self._get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO knowledge_tags (name, color, description, created_at, usage_count)
                VALUES (?, ?, ?, ?, ?)
            """, (tag.name, tag.color, tag.description, tag.created_at, tag.usage_count))
        return True

    def get_tag(self, tag_name: str) -> Optional[KnowledgeTag]:
        with self._get_connection() as conn:
            row = conn.execute("SELECT * FROM knowledge_tags WHERE name = ?", (tag_name,)).fetchone()
        if not row:
            return None
        return KnowledgeTag(
            name=row["name"], color=row["color"], description=row["description"],
            created_at=row["created_at"], usage_count=row["usage_count"],
        )

    def get_all_tags(self) -> List[KnowledgeTag]:
        with self._get_connection() as conn:
            rows = conn.execute("SELECT * FROM knowledge_tags ORDER BY usage_count DESC").fetchall()
        return [KnowledgeTag(
            name=r["name"], color=r["color"], description=r["description"],
            created_at=r["created_at"], usage_count=r["usage_count"],
        ) for r in rows]

    def delete_tag(self, tag_name: str) -> bool:
        with self._get_connection() as conn:
            conn.execute("DELETE FROM document_tags WHERE tag_name = ?", (tag_name,))
            cursor = conn.execute("DELETE FROM knowledge_tags WHERE name = ?", (tag_name,))
        return cursor.rowcount > 0

    def increment_tag_usage(self, tag_name: str):
        with self._get_connection() as conn:
            conn.execute(
                "UPDATE knowledge_tags SET usage_count = usage_count + 1 WHERE name = ?",
                (tag_name,),
            )

    def _link_tag(self, doc_id: str, tag_name: str):
        with self._get_connection() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO document_tags (document_id, tag_name) VALUES (?, ?)",
                (doc_id, tag_name),
            )

    def get_indexed_ids(self) -> List[str]:
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT id FROM knowledge_documents WHERE is_indexed = 1"
            ).fetchall()
        return [r["id"] for r in rows]

    def mark_indexed(self, doc_id: str, embedding_id: str = ""):
        with self._get_connection() as conn:
            conn.execute(
                "UPDATE knowledge_documents SET is_indexed = 1, embedding_id = ? WHERE id = ?",
                (embedding_id, doc_id),
            )

    def mark_not_indexed(self, doc_id: str):
        with self._get_connection() as conn:
            conn.execute(
                "UPDATE knowledge_documents SET is_indexed = 0, embedding_id = '' WHERE id = ?",
                (doc_id,),
            )

    @staticmethod
    def _row_to_document(row) -> KnowledgeDocument:
        return KnowledgeDocument(
            id=row["id"], title=row["title"], content=row["content"],
            doc_type=DocumentType(row["doc_type"]),
            category=DocumentCategory(row["category"]),
            tags=json.loads(row["tags"]),
            source=row["source"], summary=row["summary"],
            metadata=json.loads(row["metadata"]),
            created_at=row["created_at"], updated_at=row["updated_at"],
            access_count=row["access_count"], last_accessed=row["last_accessed"],
            importance=row["importance"], is_indexed=bool(row["is_indexed"]),
            embedding_id=row["embedding_id"],
        )


class ChromaVectorStore:
    """ChromaDB vector store for semantic search and embedding management."""

    def __init__(self, persist_directory: Optional[str] = None, embedding_model: str = "all-MiniLM-L6-v2"):
        self.logger = Logger().get_logger("ChromaVectorStore")
        self._collection_name = "nexus_knowledge"
        self._model_name = embedding_model
        self._client = None
        self._collection = None
        self._embedding_function = None
        self._available = False

        if persist_directory is None:
            config = Config()
            persist_directory = config.get("knowledge_agent.vector_store_path", "data/knowledge_vectors")

        self._persist_dir = str(Path(__file__).parent.parent.parent / persist_directory)
        os.makedirs(self._persist_dir, exist_ok=True)

        try:
            import chromadb
            from chromadb.utils import embedding_functions

            self._client = chromadb.PersistentClient(path=self._persist_dir)
            self._embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=self._model_name
            )

            self._collection = self._client.get_or_create_collection(
                name=self._collection_name,
                embedding_function=self._embedding_function,
                metadata={"hnsw:space": "cosine"},
            )
            self._available = True
            self.logger.info(f"ChromaDB initialized with model: {self._model_name}")
        except Exception as e:
            self.logger.warning(f"ChromaDB not available: {e}")
            self._available = False

    @property
    def is_available(self) -> bool:
        return self._available

    def add_document(self, doc_id: str, text: str, metadata: Optional[Dict[str, Any]] = None) -> Optional[str]:
        if not self._available:
            return None
        try:
            doc_metadata = metadata or {}
            doc_metadata["doc_id"] = doc_id
            doc_metadata["updated_at"] = doc_metadata.get("updated_at", "")

            self._collection.upsert(
                ids=[doc_id],
                documents=[text],
                metadatas=[doc_metadata],
            )
            return doc_id
        except Exception as e:
            self.logger.error(f"Error adding document to ChromaDB: {e}")
            return None

    def add_documents(self, documents: List[Tuple[str, str, Dict[str, Any]]]) -> List[str]:
        if not self._available or not documents:
            return []
        try:
            ids = [d[0] for d in documents]
            texts = [d[1] for d in documents]
            metas = [d[2] for d in documents]

            self._collection.upsert(
                ids=ids,
                documents=texts,
                metadatas=metas,
            )
            return ids
        except Exception as e:
            self.logger.error(f"Error batch adding documents to ChromaDB: {e}")
            return []

    def search(self, query: str, n_results: int = 10,
               where: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        if not self._available:
            return []
        try:
            kwargs = {
                "query_texts": [query],
                "n_results": n_results,
                "include": ["documents", "metadatas", "distances"],
            }
            if where:
                kwargs["where"] = where

            results = self._collection.query(**kwargs)

            if not results["ids"] or not results["ids"][0]:
                return []

            search_results = []
            for i, doc_id in enumerate(results["ids"][0]):
                distance = results["distances"][0][i] if results["distances"] else 1.0
                score = max(0.0, 1.0 - distance)
                search_results.append({
                    "id": doc_id,
                    "content": results["documents"][0][i] if results["documents"] else "",
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "score": score,
                })
            return search_results
        except Exception as e:
            self.logger.error(f"Error searching ChromaDB: {e}")
            return []

    def delete_document(self, doc_id: str) -> bool:
        if not self._available:
            return False
        try:
            self._collection.delete(ids=[doc_id])
            return True
        except Exception as e:
            self.logger.error(f"Error deleting from ChromaDB: {e}")
            return False

    def get_document_count(self) -> int:
        if not self._available:
            return 0
        try:
            return self._collection.count()
        except Exception:
            return 0

    def rebuild_index(self, documents: List[Tuple[str, str, Dict[str, Any]]]):
        if not self._available:
            return False
        try:
            self._collection.delete(where={})
            if documents:
                self.add_documents(documents)
            return True
        except Exception as e:
            self.logger.error(f"Error rebuilding ChromaDB index: {e}")
            return False

    def get_embedding(self, text: str) -> Optional[List[float]]:
        if not self._available or not self._embedding_function:
            return None
        try:
            embeddings = self._embedding_function([text])
            return embeddings[0] if embeddings else None
        except Exception as e:
            self.logger.error(f"Error generating embedding: {e}")
            return None
