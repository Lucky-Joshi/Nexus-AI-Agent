"""
Plugin Registry for the Plugin Management Agent.
Maintains the catalog of all plugins, their states, and capabilities.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.logger import Logger
from core.config import Config

from .models import PluginInfo, PluginMetadata, PluginStatus, PluginEvent, PluginCapability


class PluginRegistry:
    """Registry that tracks all plugins, their states, and capabilities."""

    def __init__(self, registry_path: Optional[str] = None):
        self.logger = Logger().get_logger("PluginRegistry")
        if registry_path is None:
            config = Config()
            registry_path = config.get("plugin_agent.registry_path", "data/plugins/registry.json")
        self._registry_path = Path(__file__).parent.parent.parent / registry_path
        self._registry_path.parent.mkdir(parents=True, exist_ok=True)
        self._plugins: Dict[str, PluginInfo] = {}
        self._events: List[PluginEvent] = []
        self._command_index: Dict[str, str] = {}
        self._hook_index: Dict[str, List[str]] = {}
        self._load_registry()

    def _load_registry(self):
        if self._registry_path.exists():
            try:
                with open(self._registry_path, "r") as f:
                    data = json.load(f)
                for plugin_data in data.get("plugins", []):
                    metadata = PluginMetadata.from_dict(plugin_data["metadata"])
                    info = PluginInfo(
                        metadata=metadata,
                        status=PluginStatus(plugin_data.get("status", "disabled")),
                        module_path=plugin_data.get("module_path", ""),
                        config=plugin_data.get("config", {}),
                    )
                    self._plugins[metadata.name] = info
                    self._rebuild_index(info)
                self.logger.info(f"Registry loaded: {len(self._plugins)} plugins")
            except Exception as e:
                self.logger.error(f"Failed to load registry: {e}")

    def save_registry(self):
        data = {
            "plugins": [info.to_dict() for info in self._plugins.values()],
            "events": [e.to_dict() for e in self._events[-100:]],
        }
        with open(self._registry_path, "w") as f:
            json.dump(data, f, indent=2)

    def register(self, info: PluginInfo):
        """Register a plugin in the registry."""
        self._plugins[info.metadata.name] = info
        self._rebuild_index(info)
        self._log_event(info.metadata.name, "registered", f"Plugin registered: {info.metadata.name}")
        self.save_registry()

    def unregister(self, plugin_name: str) -> bool:
        """Unregister a plugin from the registry."""
        if plugin_name in self._plugins:
            info = self._plugins.pop(plugin_name)
            self._remove_from_index(info)
            self._log_event(plugin_name, "unregistered", f"Plugin unregistered")
            self.save_registry()
            return True
        return False

    def get_plugin(self, plugin_name: str) -> Optional[PluginInfo]:
        return self._plugins.get(plugin_name)

    def get_all_plugins(self) -> List[PluginInfo]:
        return list(self._plugins.values())

    def get_enabled_plugins(self) -> List[PluginInfo]:
        return [p for p in self._plugins.values() if p.status == PluginStatus.ENABLED]

    def get_plugins_by_type(self, plugin_type: str) -> List[PluginInfo]:
        return [p for p in self._plugins.values() if p.metadata.plugin_type.value == plugin_type]

    def get_plugins_by_status(self, status: PluginStatus) -> List[PluginInfo]:
        return [p for p in self._plugins.values() if p.status == status]

    def update_status(self, plugin_name: str, status: PluginStatus, error: str = ""):
        """Update a plugin's status."""
        if plugin_name in self._plugins:
            self._plugins[plugin_name].status = status
            if error:
                self._plugins[plugin_name].error = error
            self._log_event(plugin_name, "status_change", f"Status changed to {status.value}")
            self.save_registry()

    def update_config(self, plugin_name: str, config: Dict[str, Any]):
        """Update a plugin's configuration."""
        if plugin_name in self._plugins:
            self._plugins[plugin_name].config.update(config)
            self._log_event(plugin_name, "config_update", "Configuration updated")
            self.save_registry()

    def resolve_command(self, command: str) -> Optional[str]:
        """Find which plugin handles a command."""
        cmd_lower = command.lower()
        for prefix, plugin_name in self._command_index.items():
            if cmd_lower.startswith(prefix.lower()):
                info = self._plugins.get(plugin_name)
                if info and info.status == PluginStatus.ENABLED:
                    return plugin_name
        return None

    def get_hooks_for_event(self, hook_name: str) -> List[str]:
        """Get all plugins registered for a hook."""
        return self._hook_index.get(hook_name, [])

    def get_events(self, plugin_name: Optional[str] = None, limit: int = 50) -> List[PluginEvent]:
        """Get recent plugin events."""
        events = self._events
        if plugin_name:
            events = [e for e in events if e.plugin_name == plugin_name]
        return events[-limit:]

    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics."""
        by_status = {}
        by_type = {}
        for p in self._plugins.values():
            by_status[p.status.value] = by_status.get(p.status.value, 0) + 1
            by_type[p.metadata.plugin_type.value] = by_type.get(p.metadata.plugin_type.value, 0) + 1

        return {
            "total_plugins": len(self._plugins),
            "by_status": by_status,
            "by_type": by_type,
            "commands_indexed": len(self._command_index),
            "hooks_indexed": len(self._hook_index),
            "total_events": len(self._events),
        }

    def _rebuild_index(self, info: PluginInfo):
        for cap in info.metadata.capabilities:
            if cap.command_prefix:
                self._command_index[cap.command_prefix] = info.metadata.name
            for hook in cap.hooks:
                if hook not in self._hook_index:
                    self._hook_index[hook] = []
                if info.metadata.name not in self._hook_index[hook]:
                    self._hook_index[hook].append(info.metadata.name)

    def _remove_from_index(self, info: PluginInfo):
        for cap in info.metadata.capabilities:
            if cap.command_prefix and self._command_index.get(cap.command_prefix) == info.metadata.name:
                del self._command_index[cap.command_prefix]
            for hook in cap.hooks:
                if hook in self._hook_index:
                    self._hook_index[hook] = [
                        n for n in self._hook_index[hook] if n != info.metadata.name
                    ]

    def _log_event(self, plugin_name: str, event_type: str, message: str = "", details: Dict = None):
        event = PluginEvent(
            plugin_name=plugin_name,
            event_type=event_type,
            message=message,
            details=details or {},
        )
        self._events.append(event)
        if len(self._events) > 500:
            self._events = self._events[-500:]
