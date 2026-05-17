"""
NEXUS - Agent Marketplace System
Data models for marketplace agents, reviews, installations, verification, and catalog.
"""

import uuid
import hashlib
from enum import Enum
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
from datetime import datetime


class AgentCategory(Enum):
    PRODUCTIVITY = "productivity"
    DEVELOPMENT = "development"
    AUTOMATION = "automation"
    COMMUNICATION = "communication"
    ANALYTICS = "analytics"
    SECURITY = "security"
    ENTERTAINMENT = "entertainment"
    SYSTEM = "system"
    AI_ML = "ai_ml"
    UTILITIES = "utilities"


class VerificationStatus(Enum):
    UNVERIFIED = "unverified"
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    REVOKED = "revoked"


class InstallStatus(Enum):
    NOT_INSTALLED = "not_installed"
    DOWNLOADING = "downloading"
    VERIFYING = "verifying"
    INSTALLING = "installing"
    INSTALLED = "installed"
    FAILED = "failed"
    UPDATING = "updating"
    DISABLED = "disabled"


class DependencyType(Enum):
    REQUIRED = "required"
    OPTIONAL = "optional"
    CONFLICTS = "conflicts"


class ReviewSort(Enum):
    NEWEST = "newest"
    OLDEST = "oldest"
    HIGHEST_RATED = "highest_rated"
    LOWEST_RATED = "lowest_rated"
    MOST_HELPFUL = "most_helpful"


@dataclass
class MarketplaceDependency:
    """A dependency required by a marketplace agent."""
    name: str
    min_version: str = "0.0.0"
    max_version: str = "*"
    dep_type: DependencyType = DependencyType.REQUIRED

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "min_version": self.min_version,
            "max_version": self.max_version,
            "dep_type": self.dep_type.value,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MarketplaceDependency":
        return cls(
            name=data["name"],
            min_version=data.get("min_version", "0.0.0"),
            max_version=data.get("max_version", "*"),
            dep_type=DependencyType(data.get("dep_type", "required")),
        )


@dataclass
class MarketplaceAgent:
    """Represents an agent available in the marketplace."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    display_name: str = ""
    version: str = "1.0.0"
    description: str = ""
    long_description: str = ""
    author: str = ""
    author_email: str = ""
    category: AgentCategory = AgentCategory.UTILITIES
    tags: List[str] = field(default_factory=list)
    icon_url: str = ""
    homepage: str = ""
    repository_url: str = ""
    license: str = "MIT"
    min_nexus_version: str = "1.0.0"
    max_nexus_version: str = "*"
    dependencies: List[MarketplaceDependency] = field(default_factory=list)
    python_dependencies: List[str] = field(default_factory=list)
    file_size: int = 0
    download_url: str = ""
    checksum: str = ""
    checksum_algorithm: str = "sha256"
    verification_status: VerificationStatus = VerificationStatus.UNVERIFIED
    verified_by: str = ""
    verified_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    download_count: int = 0
    install_count: int = 0
    rating: float = 0.0
    rating_count: int = 0
    is_featured: bool = False
    is_official: bool = False
    screenshots: List[str] = field(default_factory=list)
    changelog: str = ""
    capabilities: List[str] = field(default_factory=list)
    permissions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "display_name": self.display_name,
            "version": self.version,
            "description": self.description,
            "long_description": self.long_description,
            "author": self.author,
            "author_email": self.author_email,
            "category": self.category.value,
            "tags": self.tags,
            "icon_url": self.icon_url,
            "homepage": self.homepage,
            "repository_url": self.repository_url,
            "license": self.license,
            "min_nexus_version": self.min_nexus_version,
            "max_nexus_version": self.max_nexus_version,
            "dependencies": [d.to_dict() for d in self.dependencies],
            "python_dependencies": self.python_dependencies,
            "file_size": self.file_size,
            "download_url": self.download_url,
            "checksum": self.checksum,
            "checksum_algorithm": self.checksum_algorithm,
            "verification_status": self.verification_status.value,
            "verified_by": self.verified_by,
            "verified_at": self.verified_at.isoformat() if self.verified_at else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "download_count": self.download_count,
            "install_count": self.install_count,
            "rating": round(self.rating, 2),
            "rating_count": self.rating_count,
            "is_featured": self.is_featured,
            "is_official": self.is_official,
            "screenshots": self.screenshots,
            "changelog": self.changelog,
            "capabilities": self.capabilities,
            "permissions": self.permissions,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MarketplaceAgent":
        import ast
        def safe_parse(val, default=None):
            if val is None:
                return default
            if isinstance(val, (list, dict)):
                return val
            if isinstance(val, str):
                try:
                    return ast.literal_eval(val)
                except (ValueError, SyntaxError):
                    return default
            return default

        deps_data = safe_parse(data.get("dependencies"), [])
        py_deps = safe_parse(data.get("python_dependencies"), [])
        tags = safe_parse(data.get("tags"), [])
        screenshots = safe_parse(data.get("screenshots"), [])
        capabilities = safe_parse(data.get("capabilities"), [])
        permissions = safe_parse(data.get("permissions"), [])
        metadata = safe_parse(data.get("metadata"), {})

        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            name=data.get("name", ""),
            display_name=data.get("display_name", ""),
            version=data.get("version", "1.0.0"),
            description=data.get("description", ""),
            long_description=data.get("long_description", ""),
            author=data.get("author", ""),
            author_email=data.get("author_email", ""),
            category=AgentCategory(data.get("category", "utilities")),
            tags=tags,
            icon_url=data.get("icon_url", ""),
            homepage=data.get("homepage", ""),
            repository_url=data.get("repository_url", ""),
            license=data.get("license", "MIT"),
            min_nexus_version=data.get("min_nexus_version", "1.0.0"),
            max_nexus_version=data.get("max_nexus_version", "*"),
            dependencies=[MarketplaceDependency.from_dict(d) for d in deps_data if isinstance(d, dict)],
            python_dependencies=py_deps if isinstance(py_deps, list) else [],
            file_size=data.get("file_size", 0),
            download_url=data.get("download_url", ""),
            checksum=data.get("checksum", ""),
            checksum_algorithm=data.get("checksum_algorithm", "sha256"),
            verification_status=VerificationStatus(data.get("verification_status", "unverified")),
            verified_by=data.get("verified_by", ""),
            verified_at=datetime.fromisoformat(data["verified_at"]) if data.get("verified_at") else None,
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now(),
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else datetime.now(),
            download_count=data.get("download_count", 0),
            install_count=data.get("install_count", 0),
            rating=data.get("rating", 0.0),
            rating_count=data.get("rating_count", 0),
            is_featured=data.get("is_featured", False),
            is_official=data.get("is_official", False),
            screenshots=screenshots if isinstance(screenshots, list) else [],
            changelog=data.get("changelog", ""),
            capabilities=capabilities if isinstance(capabilities, list) else [],
            permissions=permissions if isinstance(permissions, list) else [],
            metadata=metadata if isinstance(metadata, dict) else {},
        )

    def compute_checksum(self, content: bytes) -> str:
        if self.checksum_algorithm == "sha256":
            return hashlib.sha256(content).hexdigest()
        elif self.checksum_algorithm == "md5":
            return hashlib.md5(content).hexdigest()
        return hashlib.sha256(content).hexdigest()


@dataclass
class InstallRecord:
    """Tracks installation state of a marketplace agent."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    agent_id: str = ""
    agent_name: str = ""
    version: str = ""
    status: InstallStatus = InstallStatus.NOT_INSTALLED
    installed_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    install_path: str = ""
    enabled: bool = True
    auto_update: bool = True
    last_check: Optional[datetime] = None
    available_update: str = ""
    error_message: str = ""
    install_log: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "version": self.version,
            "status": self.status.value,
            "installed_at": self.installed_at.isoformat() if self.installed_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "install_path": self.install_path,
            "enabled": self.enabled,
            "auto_update": self.auto_update,
            "last_check": self.last_check.isoformat() if self.last_check else None,
            "available_update": self.available_update,
            "error_message": self.error_message,
            "install_log": self.install_log,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InstallRecord":
        import ast
        def safe_list(val, default=None):
            if val is None:
                return default
            if isinstance(val, list):
                return val
            if isinstance(val, str):
                try:
                    return ast.literal_eval(val)
                except (ValueError, SyntaxError):
                    return default
            return default

        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            agent_id=data.get("agent_id", ""),
            agent_name=data.get("agent_name", ""),
            version=data.get("version", ""),
            status=InstallStatus(data.get("status", "not_installed")),
            installed_at=datetime.fromisoformat(data["installed_at"]) if data.get("installed_at") else None,
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None,
            install_path=data.get("install_path", ""),
            enabled=data.get("enabled", True),
            auto_update=data.get("auto_update", True),
            last_check=datetime.fromisoformat(data["last_check"]) if data.get("last_check") else None,
            available_update=data.get("available_update", ""),
            error_message=data.get("error_message", ""),
            install_log=safe_list(data.get("install_log"), []),
        )


@dataclass
class AgentReview:
    """A user review for a marketplace agent."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    agent_id: str = ""
    agent_name: str = ""
    user_id: str = ""
    username: str = ""
    rating: int = 0
    title: str = ""
    content: str = ""
    is_helpful: int = 0
    is_not_helpful: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    is_verified_purchase: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "user_id": self.user_id,
            "username": self.username,
            "rating": self.rating,
            "title": self.title,
            "content": self.content,
            "is_helpful": self.is_helpful,
            "is_not_helpful": self.is_not_helpful,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "is_verified_purchase": self.is_verified_purchase,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentReview":
        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            agent_id=data.get("agent_id", ""),
            agent_name=data.get("agent_name", ""),
            user_id=data.get("user_id", ""),
            username=data.get("username", ""),
            rating=data.get("rating", 0),
            title=data.get("title", ""),
            content=data.get("content", ""),
            is_helpful=data.get("is_helpful", 0),
            is_not_helpful=data.get("is_not_helpful", 0),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now(),
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else datetime.now(),
            is_verified_purchase=data.get("is_verified_purchase", False),
        )


@dataclass
class VerificationReport:
    """Security verification report for a marketplace agent."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    agent_id: str = ""
    agent_name: str = ""
    version: str = ""
    status: VerificationStatus = VerificationStatus.PENDING
    checksum_valid: bool = False
    signature_valid: bool = False
    sandbox_test_passed: bool = False
    dependency_check_passed: bool = False
    compatibility_check_passed: bool = False
    security_scan_passed: bool = False
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    verified_by: str = ""
    verified_at: datetime = field(default_factory=datetime.now)
    report_data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "version": self.version,
            "status": self.status.value,
            "checksum_valid": self.checksum_valid,
            "signature_valid": self.signature_valid,
            "sandbox_test_passed": self.sandbox_test_passed,
            "dependency_check_passed": self.dependency_check_passed,
            "compatibility_check_passed": self.compatibility_check_passed,
            "security_scan_passed": self.security_scan_passed,
            "issues": self.issues,
            "warnings": self.warnings,
            "verified_by": self.verified_by,
            "verified_at": self.verified_at.isoformat(),
            "report_data": self.report_data,
        }

    @property
    def is_verified(self) -> bool:
        return (
            self.status == VerificationStatus.VERIFIED
            and self.checksum_valid
            and self.security_scan_passed
            and self.compatibility_check_passed
        )


@dataclass
class MarketplaceStats:
    """Statistics for the marketplace system."""
    total_agents: int = 0
    installed_agents: int = 0
    featured_agents: int = 0
    official_agents: int = 0
    verified_agents: int = 0
    total_downloads: int = 0
    total_reviews: int = 0
    avg_rating: float = 0.0
    categories: Dict[str, int] = field(default_factory=dict)
    updates_available: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_agents": self.total_agents,
            "installed_agents": self.installed_agents,
            "featured_agents": self.featured_agents,
            "official_agents": self.official_agents,
            "verified_agents": self.verified_agents,
            "total_downloads": self.total_downloads,
            "total_reviews": self.total_reviews,
            "avg_rating": round(self.avg_rating, 2),
            "categories": self.categories,
            "updates_available": self.updates_available,
        }
