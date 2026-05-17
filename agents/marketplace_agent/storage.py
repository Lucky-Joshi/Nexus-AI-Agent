"""
NEXUS - Agent Marketplace System
SQLite persistence for marketplace catalog, installations, reviews, and verification reports.
"""

import json
import sqlite3
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

from core.logger import Logger
from core.database import Database


class MarketplaceStorage:
    """Handles persistence for marketplace data."""

    def __init__(self):
        self.logger = Logger().get_logger("MarketplaceStorage")
        self.db = Database()
        self._initialize_tables()

    def _initialize_tables(self):
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS marketplace_agents (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                display_name TEXT NOT NULL DEFAULT '',
                version TEXT NOT NULL DEFAULT '1.0.0',
                description TEXT NOT NULL DEFAULT '',
                long_description TEXT NOT NULL DEFAULT '',
                author TEXT NOT NULL DEFAULT '',
                author_email TEXT NOT NULL DEFAULT '',
                category TEXT NOT NULL DEFAULT 'utilities',
                tags TEXT NOT NULL DEFAULT '[]',
                icon_url TEXT NOT NULL DEFAULT '',
                homepage TEXT NOT NULL DEFAULT '',
                repository_url TEXT NOT NULL DEFAULT '',
                license TEXT NOT NULL DEFAULT 'MIT',
                min_nexus_version TEXT NOT NULL DEFAULT '1.0.0',
                max_nexus_version TEXT NOT NULL DEFAULT '*',
                dependencies TEXT NOT NULL DEFAULT '[]',
                python_dependencies TEXT NOT NULL DEFAULT '[]',
                file_size INTEGER NOT NULL DEFAULT 0,
                download_url TEXT NOT NULL DEFAULT '',
                checksum TEXT NOT NULL DEFAULT '',
                checksum_algorithm TEXT NOT NULL DEFAULT 'sha256',
                verification_status TEXT NOT NULL DEFAULT 'unverified',
                verified_by TEXT NOT NULL DEFAULT '',
                verified_at TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                download_count INTEGER NOT NULL DEFAULT 0,
                install_count INTEGER NOT NULL DEFAULT 0,
                rating REAL NOT NULL DEFAULT 0.0,
                rating_count INTEGER NOT NULL DEFAULT 0,
                is_featured INTEGER NOT NULL DEFAULT 0,
                is_official INTEGER NOT NULL DEFAULT 0,
                screenshots TEXT NOT NULL DEFAULT '[]',
                changelog TEXT NOT NULL DEFAULT '',
                capabilities TEXT NOT NULL DEFAULT '[]',
                permissions TEXT NOT NULL DEFAULT '[]',
                metadata TEXT NOT NULL DEFAULT '{}'
            )
        """)

        self.db.execute("""
            CREATE TABLE IF NOT EXISTS install_records (
                id TEXT PRIMARY KEY,
                agent_id TEXT NOT NULL,
                agent_name TEXT NOT NULL,
                version TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'not_installed',
                installed_at TEXT,
                updated_at TEXT,
                install_path TEXT NOT NULL DEFAULT '',
                enabled INTEGER NOT NULL DEFAULT 1,
                auto_update INTEGER NOT NULL DEFAULT 1,
                last_check TEXT,
                available_update TEXT NOT NULL DEFAULT '',
                error_message TEXT NOT NULL DEFAULT '',
                install_log TEXT NOT NULL DEFAULT '[]',
                FOREIGN KEY (agent_id) REFERENCES marketplace_agents(id)
            )
        """)

        self.db.execute("""
            CREATE TABLE IF NOT EXISTS agent_reviews (
                id TEXT PRIMARY KEY,
                agent_id TEXT NOT NULL,
                agent_name TEXT NOT NULL,
                user_id TEXT NOT NULL DEFAULT '',
                username TEXT NOT NULL DEFAULT 'anonymous',
                rating INTEGER NOT NULL DEFAULT 0,
                title TEXT NOT NULL DEFAULT '',
                content TEXT NOT NULL DEFAULT '',
                is_helpful INTEGER NOT NULL DEFAULT 0,
                is_not_helpful INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                is_verified_purchase INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (agent_id) REFERENCES marketplace_agents(id)
            )
        """)

        self.db.execute("""
            CREATE TABLE IF NOT EXISTS verification_reports (
                id TEXT PRIMARY KEY,
                agent_id TEXT NOT NULL,
                agent_name TEXT NOT NULL,
                version TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'pending',
                checksum_valid INTEGER NOT NULL DEFAULT 0,
                signature_valid INTEGER NOT NULL DEFAULT 0,
                sandbox_test_passed INTEGER NOT NULL DEFAULT 0,
                dependency_check_passed INTEGER NOT NULL DEFAULT 0,
                compatibility_check_passed INTEGER NOT NULL DEFAULT 0,
                security_scan_passed INTEGER NOT NULL DEFAULT 0,
                issues TEXT NOT NULL DEFAULT '[]',
                warnings TEXT NOT NULL DEFAULT '[]',
                verified_by TEXT NOT NULL DEFAULT '',
                verified_at TEXT NOT NULL,
                report_data TEXT NOT NULL DEFAULT '{}',
                FOREIGN KEY (agent_id) REFERENCES marketplace_agents(id)
            )
        """)

        self.db.execute("CREATE INDEX IF NOT EXISTS idx_ma_name ON marketplace_agents(name)")
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_ma_category ON marketplace_agents(category)")
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_ma_verified ON marketplace_agents(verification_status)")
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_ma_featured ON marketplace_agents(is_featured)")
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_ma_rating ON marketplace_agents(rating)")
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_ir_agent ON install_records(agent_id)")
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_ir_status ON install_records(status)")
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_reviews_agent ON agent_reviews(agent_id)")
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_reviews_rating ON agent_reviews(rating)")
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_vr_agent ON verification_reports(agent_id)")

        self.logger.info("Marketplace storage tables initialized")

    def save_agent(self, agent_data: Dict[str, Any]):
        self.db.execute(
            """INSERT OR REPLACE INTO marketplace_agents
               (id, name, display_name, version, description, long_description,
                author, author_email, category, tags, icon_url, homepage, repository_url,
                license, min_nexus_version, max_nexus_version, dependencies, python_dependencies,
                file_size, download_url, checksum, checksum_algorithm, verification_status,
                verified_by, verified_at, created_at, updated_at, download_count, install_count,
                rating, rating_count, is_featured, is_official, screenshots, changelog,
                capabilities, permissions, metadata)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                agent_data["id"], agent_data["name"], agent_data.get("display_name", ""),
                agent_data.get("version", "1.0.0"), agent_data.get("description", ""),
                agent_data.get("long_description", ""), agent_data.get("author", ""),
                agent_data.get("author_email", ""), agent_data.get("category", "utilities"),
                json.dumps(agent_data.get("tags", [])), agent_data.get("icon_url", ""),
                agent_data.get("homepage", ""), agent_data.get("repository_url", ""),
                agent_data.get("license", "MIT"), agent_data.get("min_nexus_version", "1.0.0"),
                agent_data.get("max_nexus_version", "*"),
                json.dumps(agent_data.get("dependencies", [])),
                json.dumps(agent_data.get("python_dependencies", [])),
                agent_data.get("file_size", 0), agent_data.get("download_url", ""),
                agent_data.get("checksum", ""), agent_data.get("checksum_algorithm", "sha256"),
                agent_data.get("verification_status", "unverified"),
                agent_data.get("verified_by", ""), agent_data.get("verified_at"),
                agent_data.get("created_at", datetime.now().isoformat()),
                agent_data.get("updated_at", datetime.now().isoformat()),
                agent_data.get("download_count", 0), agent_data.get("install_count", 0),
                agent_data.get("rating", 0.0), agent_data.get("rating_count", 0),
                1 if agent_data.get("is_featured", False) else 0,
                1 if agent_data.get("is_official", False) else 0,
                json.dumps(agent_data.get("screenshots", [])),
                agent_data.get("changelog", ""),
                json.dumps(agent_data.get("capabilities", [])),
                json.dumps(agent_data.get("permissions", [])),
                json.dumps(agent_data.get("metadata", {})),
            ),
        )

    def get_agent(self, agent_id: str = None, agent_name: str = None) -> Optional[Dict[str, Any]]:
        if agent_id:
            row = self.db.fetchone("SELECT * FROM marketplace_agents WHERE id = ?", (agent_id,))
        elif agent_name:
            row = self.db.fetchone("SELECT * FROM marketplace_agents WHERE name = ?", (agent_name,))
        else:
            return None
        return dict(row) if row else None

    def get_agents(self, category: str = None, verified_only: bool = False,
                   featured_only: bool = False, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        query = "SELECT * FROM marketplace_agents WHERE 1=1"
        params = []

        if category:
            query += " AND category = ?"
            params.append(category)
        if verified_only:
            query += " AND verification_status = 'verified'"
        if featured_only:
            query += " AND is_featured = 1"

        query += " ORDER BY rating DESC, install_count DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        rows = self.db.fetchall(query, tuple(params))
        return [dict(row) for row in rows]

    def search_agents(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        search_term = f"%{query}%"
        rows = self.db.fetchall(
            """SELECT * FROM marketplace_agents
               WHERE name LIKE ? OR display_name LIKE ? OR description LIKE ? OR tags LIKE ?
               ORDER BY rating DESC, install_count DESC LIMIT ?""",
            (search_term, search_term, search_term, search_term, limit),
        )
        return [dict(row) for row in rows]

    def update_agent_stats(self, agent_id: str, downloads: int = 0, installs: int = 0):
        if downloads > 0:
            self.db.execute(
                "UPDATE marketplace_agents SET download_count = download_count + ? WHERE id = ?",
                (downloads, agent_id),
            )
        if installs > 0:
            self.db.execute(
                "UPDATE marketplace_agents SET install_count = install_count + ? WHERE id = ?",
                (installs, agent_id),
            )

    def save_install_record(self, record_data: Dict[str, Any]):
        self.db.execute(
            """INSERT OR REPLACE INTO install_records
               (id, agent_id, agent_name, version, status, installed_at, updated_at,
                install_path, enabled, auto_update, last_check, available_update,
                error_message, install_log)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                record_data["id"], record_data["agent_id"], record_data["agent_name"],
                record_data.get("version", ""), record_data.get("status", "not_installed"),
                record_data.get("installed_at"), record_data.get("updated_at"),
                record_data.get("install_path", ""),
                1 if record_data.get("enabled", True) else 0,
                1 if record_data.get("auto_update", True) else 0,
                record_data.get("last_check"), record_data.get("available_update", ""),
                record_data.get("error_message", ""),
                json.dumps(record_data.get("install_log", [])),
            ),
        )

    def get_install_record(self, agent_id: str = None, agent_name: str = None) -> Optional[Dict[str, Any]]:
        if agent_id:
            row = self.db.fetchone("SELECT * FROM install_records WHERE agent_id = ?", (agent_id,))
        elif agent_name:
            row = self.db.fetchone("SELECT * FROM install_records WHERE agent_name = ?", (agent_name,))
        else:
            return None
        return dict(row) if row else None

    def get_all_install_records(self) -> List[Dict[str, Any]]:
        rows = self.db.fetchall("SELECT * FROM install_records ORDER BY installed_at DESC")
        return [dict(row) for row in rows]

    def delete_install_record(self, agent_id: str):
        self.db.execute("DELETE FROM install_records WHERE agent_id = ?", (agent_id,))

    def save_review(self, review_data: Dict[str, Any]):
        self.db.execute(
            """INSERT OR REPLACE INTO agent_reviews
               (id, agent_id, agent_name, user_id, username, rating, title, content,
                is_helpful, is_not_helpful, created_at, updated_at, is_verified_purchase)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                review_data["id"], review_data["agent_id"], review_data["agent_name"],
                review_data.get("user_id", ""), review_data.get("username", "anonymous"),
                review_data.get("rating", 0), review_data.get("title", ""),
                review_data.get("content", ""), review_data.get("is_helpful", 0),
                review_data.get("is_not_helpful", 0),
                review_data.get("created_at", datetime.now().isoformat()),
                review_data.get("updated_at", datetime.now().isoformat()),
                1 if review_data.get("is_verified_purchase", False) else 0,
            ),
        )
        self._update_agent_rating(review_data["agent_id"])

    def _update_agent_rating(self, agent_id: str):
        avg = self.db.fetchone(
            "SELECT AVG(rating) as avg_rating, COUNT(*) as count FROM agent_reviews WHERE agent_id = ?",
            (agent_id,),
        )
        if avg and avg["count"] > 0:
            self.db.execute(
                "UPDATE marketplace_agents SET rating = ?, rating_count = ? WHERE id = ?",
                (round(avg["avg_rating"], 2), avg["count"], agent_id),
            )

    def get_reviews(self, agent_id: str, limit: int = 50, sort: str = "newest") -> List[Dict[str, Any]]:
        order = {
            "newest": "created_at DESC",
            "oldest": "created_at ASC",
            "highest_rated": "rating DESC",
            "lowest_rated": "rating ASC",
            "most_helpful": "is_helpful DESC",
        }.get(sort, "created_at DESC")

        rows = self.db.fetchall(
            f"SELECT * FROM agent_reviews WHERE agent_id = ? ORDER BY {order} LIMIT ?",
            (agent_id, limit),
        )
        return [dict(row) for row in rows]

    def save_verification_report(self, report_data: Dict[str, Any]):
        self.db.execute(
            """INSERT OR REPLACE INTO verification_reports
               (id, agent_id, agent_name, version, status, checksum_valid, signature_valid,
                sandbox_test_passed, dependency_check_passed, compatibility_check_passed,
                security_scan_passed, issues, warnings, verified_by, verified_at, report_data)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                report_data["id"], report_data["agent_id"], report_data["agent_name"],
                report_data.get("version", ""), report_data.get("status", "pending"),
                1 if report_data.get("checksum_valid", False) else 0,
                1 if report_data.get("signature_valid", False) else 0,
                1 if report_data.get("sandbox_test_passed", False) else 0,
                1 if report_data.get("dependency_check_passed", False) else 0,
                1 if report_data.get("compatibility_check_passed", False) else 0,
                1 if report_data.get("security_scan_passed", False) else 0,
                json.dumps(report_data.get("issues", [])),
                json.dumps(report_data.get("warnings", [])),
                report_data.get("verified_by", ""),
                report_data.get("verified_at", datetime.now().isoformat()),
                json.dumps(report_data.get("report_data", {})),
            ),
        )

    def get_verification_report(self, agent_id: str) -> Optional[Dict[str, Any]]:
        row = self.db.fetchone(
            "SELECT * FROM verification_reports WHERE agent_id = ? ORDER BY verified_at DESC LIMIT 1",
            (agent_id,),
        )
        return dict(row) if row else None

    def get_stats(self) -> Dict[str, Any]:
        total = self.db.fetchone("SELECT COUNT(*) as count FROM marketplace_agents")
        installed = self.db.fetchone("SELECT COUNT(*) as count FROM install_records WHERE status = 'installed'")
        featured = self.db.fetchone("SELECT COUNT(*) as count FROM marketplace_agents WHERE is_featured = 1")
        official = self.db.fetchone("SELECT COUNT(*) as count FROM marketplace_agents WHERE is_official = 1")
        verified = self.db.fetchone("SELECT COUNT(*) as count FROM marketplace_agents WHERE verification_status = 'verified'")
        downloads = self.db.fetchone("SELECT SUM(download_count) as total FROM marketplace_agents")
        reviews = self.db.fetchone("SELECT COUNT(*) as count FROM agent_reviews")
        avg_rating = self.db.fetchone("SELECT AVG(rating) as avg FROM marketplace_agents WHERE rating > 0")
        updates = self.db.fetchone("SELECT COUNT(*) as count FROM install_records WHERE available_update != ''")

        categories = self.db.fetchall(
            "SELECT category, COUNT(*) as count FROM marketplace_agents GROUP BY category"
        )

        return {
            "total_agents": total["count"] if total else 0,
            "installed_agents": installed["count"] if installed else 0,
            "featured_agents": featured["count"] if featured else 0,
            "official_agents": official["count"] if official else 0,
            "verified_agents": verified["count"] if verified else 0,
            "total_downloads": downloads["total"] if downloads["total"] else 0,
            "total_reviews": reviews["count"] if reviews else 0,
            "avg_rating": round(avg_rating["avg"], 2) if avg_rating["avg"] else 0.0,
            "updates_available": updates["count"] if updates else 0,
            "categories": {row["category"]: row["count"] for row in categories},
        }
