"""
Plugin API for NEXUS.
Defines the base interface that all plugins must implement.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from core.logger import Logger

from .models import PluginMetadata, PluginCapability, PluginType, SecurityLevel


class PluginContext:
    """Context object passed to plugins, providing access to NEXUS services."""

    def __init__(self, config: Dict[str, Any] = None, nexus_api: Any = None):
        self._config = config or {}
        self._nexus_api = nexus_api
        self._data: Dict[str, Any] = {}

    def get_config(self, key: str, default: Any = None) -> Any:
        return self._config.get(key, default)

    def set_config(self, key: str, value: Any):
        self._config[key] = value

    @property
    def config(self) -> Dict[str, Any]:
        return self._config

    def store(self, key: str, value: Any):
        self._data[key] = value

    def retrieve(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def log(self, level: str, message: str):
        if self._nexus_api:
            self._nexus_api.log(level, message)

    def get_agent(self, agent_name: str) -> Optional[Any]:
        if self._nexus_api:
            return self._nexus_api.get_agent(agent_name)
        return None

    def execute_command(self, command: str) -> Dict[str, Any]:
        if self._nexus_api:
            return self._nexus_api.execute_command(command)
        return {"success": False, "response": "NEXUS API not available"}


class BasePlugin(ABC):
    """Abstract base class that all NEXUS plugins must implement."""

    def __init__(self):
        self.logger = Logger().get_logger(f"Plugin.{self.__class__.__name__}")
        self._context: Optional[PluginContext] = None
        self._initialized = False

    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        pass

    def initialize(self, context: PluginContext) -> bool:
        """Called when the plugin is loaded. Override for custom init logic."""
        self._context = context
        self._initialized = True
        self.logger.info(f"Plugin initialized: {self.metadata.name}")
        return True

    def shutdown(self):
        """Called when the plugin is unloaded. Override for cleanup."""
        self._initialized = False
        self.logger.info(f"Plugin shutdown: {self.metadata.name}")

    @abstractmethod
    def execute(self, command: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a plugin command. Must be implemented by subclasses."""
        pass

    def get_capabilities(self) -> List[PluginCapability]:
        """Return list of capabilities this plugin provides."""
        return self.metadata.capabilities

    def handle_hook(self, hook_name: str, data: Any) -> Any:
        """Handle a hook event. Override to respond to NEXUS events."""
        return data

    def validate_command(self, command: str) -> bool:
        """Validate whether this plugin can handle the command."""
        caps = self.get_capabilities()
        cmd_lower = command.lower()
        for cap in caps:
            if cap.command_prefix and cmd_lower.startswith(cap.command_prefix.lower()):
                return True
        return False

    @property
    def is_initialized(self) -> bool:
        return self._initialized

    @property
    def context(self) -> Optional[PluginContext]:
        return self._context


class CommandPlugin(BasePlugin):
    """Base class for command-type plugins."""

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name=self.__class__.__name__,
            plugin_type=PluginType.COMMAND,
            security_level=SecurityLevel.SANDBOXED,
        )

    def execute(self, command: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        cmd = command.lower()
        handlers = self._get_command_handlers()
        for prefix, handler in handlers.items():
            if cmd.startswith(prefix.lower()):
                try:
                    result = handler(command, params)
                    return {"success": True, "response": result, "plugin": self.metadata.name}
                except Exception as e:
                    return {"success": False, "response": f"Plugin error: {str(e)}", "plugin": self.metadata.name}
        return {"success": False, "response": f"Unknown command: {command}", "plugin": self.metadata.name}

    def _get_command_handlers(self) -> Dict[str, callable]:
        """Return dict of command prefix -> handler function."""
        return {}


class ServicePlugin(BasePlugin):
    """Base class for service-type plugins that provide background services."""

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name=self.__class__.__name__,
            plugin_type=PluginType.SERVICE,
            security_level=SecurityLevel.SANDBOXED,
        )

    def start_service(self):
        """Start the background service. Override in subclass."""
        pass

    def stop_service(self):
        """Stop the background service. Override in subclass."""
        pass

    def execute(self, command: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {"success": True, "response": f"Service {self.metadata.name} running", "plugin": self.metadata.name}


class HookPlugin(BasePlugin):
    """Base class for hook-type plugins that respond to NEXUS events."""

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name=self.__class__.__name__,
            plugin_type=PluginType.HOOK,
            security_level=SecurityLevel.SANDBOXED,
        )

    def get_registered_hooks(self) -> List[str]:
        """Return list of hook names this plugin registers for."""
        return []

    def handle_hook(self, hook_name: str, data: Any) -> Any:
        """Handle a hook event."""
        return data

    def execute(self, command: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {"success": True, "response": f"Hook plugin {self.metadata.name}", "plugin": self.metadata.name}
