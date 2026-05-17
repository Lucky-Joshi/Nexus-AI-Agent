"""
Data models for the Plugin Management Agent.
Defines plugin metadata, states, capabilities, and lifecycle records.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class PluginStatus(Enum):
    """Lifecycle status of a plugin."""
    DISCOVERED = "discovered"
    LOADING = "loading"
    LOADED = "loaded"
    INITIALIZED = "initialized"
    ENABLED = "enabled"
    DISABLED = "disabled"
    ERROR = "error"
    UNLOADING = "unloading"
    UNLOADED = "unloaded"


class PluginType(Enum):
    """Type of plugin."""
    COMMAND = "command"
    SERVICE = "service"
    HOOK = "hook"
    AGENT = "agent"
    UI = "ui"
    MIDDLEWARE = "middleware"
    EXTENSION = "extension"


class SecurityLevel(Enum):
    """Security clearance for plugin execution."""
    TRUSTED = "trusted"
    SANDBOXED = "sandboxed"
    RESTRICTED = "restricted"
    BLOCKED = "blocked"


@dataclass
class PluginDependency:
    """A dependency required by a plugin."""
    name: str
    version: str = "*"
    required: bool = True
    optional: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "version": self.version, "required": self.required}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PluginDependency":
        return cls(
            name=data["name"],
            version=data.get("version", "*"),
            required=data.get("required", True),
        )


@dataclass
class PluginCapability:
    """A capability exposed by a plugin."""
    name: str
    description: str = ""
    command_prefix: str = ""
    hooks: List[str] = field(default_factory=list)
    permissions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "command_prefix": self.command_prefix,
            "hooks": self.hooks,
            "permissions": self.permissions,
        }


@dataclass
class PluginMetadata:
    """Metadata describing a plugin."""
    name: str
    version: str = "1.0.0"
    description: str = ""
    author: str = ""
    plugin_type: PluginType = PluginType.EXTENSION
    security_level: SecurityLevel = SecurityLevel.SANDBOXED
    min_nexus_version: str = "1.0.0"
    max_nexus_version: str = "*"
    dependencies: List[PluginDependency] = field(default_factory=list)
    capabilities: List[PluginCapability] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    homepage: str = ""
    license: str = ""
    entry_point: str = ""
    config_schema: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "plugin_type": self.plugin_type.value,
            "security_level": self.security_level.value,
            "min_nexus_version": self.min_nexus_version,
            "max_nexus_version": self.max_nexus_version,
            "dependencies": [d.to_dict() for d in self.dependencies],
            "capabilities": [c.to_dict() for c in self.capabilities],
            "tags": self.tags,
            "homepage": self.homepage,
            "license": self.license,
            "entry_point": self.entry_point,
            "config_schema": self.config_schema,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PluginMetadata":
        deps = [PluginDependency.from_dict(d) for d in data.get("dependencies", [])]
        caps = [PluginCapability(**c) for c in data.get("capabilities", [])]
        return cls(
            name=data["name"],
            version=data.get("version", "1.0.0"),
            description=data.get("description", ""),
            author=data.get("author", ""),
            plugin_type=PluginType(data.get("plugin_type", "extension")),
            security_level=SecurityLevel(data.get("security_level", "sandboxed")),
            min_nexus_version=data.get("min_nexus_version", "1.0.0"),
            max_nexus_version=data.get("max_nexus_version", "*"),
            dependencies=deps,
            capabilities=caps,
            tags=data.get("tags", []),
            homepage=data.get("homepage", ""),
            license=data.get("license", ""),
            entry_point=data.get("entry_point", ""),
            config_schema=data.get("config_schema", {}),
        )


@dataclass
class PluginInfo:
    """Runtime information about a loaded plugin."""
    metadata: PluginMetadata
    status: PluginStatus = PluginStatus.DISCOVERED
    module_path: str = ""
    loaded_at: str = ""
    enabled_at: str = ""
    disabled_at: str = ""
    error: str = ""
    load_time_ms: float = 0.0
    execution_count: int = 0
    last_executed: str = ""
    config: Dict[str, Any] = field(default_factory=dict)

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "metadata": self.metadata.to_dict(),
            "status": self.status.value,
            "module_path": self.module_path,
            "loaded_at": self.loaded_at,
            "enabled_at": self.enabled_at,
            "disabled_at": self.disabled_at,
            "error": self.error,
            "load_time_ms": self.load_time_ms,
            "execution_count": self.execution_count,
            "config": self.config,
        }


@dataclass
class PluginEvent:
    """Event log entry for plugin lifecycle."""
    plugin_name: str
    event_type: str
    message: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    details: Dict[str, Any] = field(default_factory=dict)

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "plugin_name": self.plugin_name,
            "event_type": self.event_type,
            "message": self.message,
            "timestamp": self.timestamp,
            "details": self.details,
        }
