"""
Plugin Management Agent for NEXUS.
Dynamic loading and management of external plugins/extensions.
"""

import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.base_agent import BaseAgent, AgentStatus
from core.logger import Logger
from core.config import Config

from .models import PluginInfo, PluginStatus, PluginType, SecurityLevel
from .loader import PluginLoader
from .registry import PluginRegistry
from .services import PluginLifecycleManager


class PluginAgent(BaseAgent):
    """
    Plugin Management Agent for NEXUS.
    Manages plugin lifecycle, discovery, installation, and execution.
    """

    def __init__(self):
        super().__init__("plugin_agent", "Plugin management, loading, and lifecycle control")
        self.logger = Logger().get_logger("PluginAgent")
        self.config = Config()

        plugins_dir = self.config.get("plugin_agent.plugins_dir", "")
        if not plugins_dir:
            plugins_dir = str(Path(__file__).parent / "plugins")

        self._loader = PluginLoader(plugins_dir=plugins_dir)
        self._registry = PluginRegistry()
        self._lifecycle = PluginLifecycleManager(
            loader=self._loader,
            registry=self._registry,
        )

        self._auto_load_plugins()
        self.logger.info(f"PluginAgent initialized ({len(self._registry.get_all_plugins())} plugins registered)")

    def execute(self, command: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        self.status = AgentStatus.BUSY
        try:
            cmd = command.lower()

            if self._matches(cmd, ["install plugin", "add plugin", "load plugin"]):
                return self._handle_install(command)

            elif self._matches(cmd, ["uninstall plugin", "remove plugin", "delete plugin"]):
                return self._handle_uninstall(command)

            elif self._matches(cmd, ["enable plugin", "activate plugin", "turn on plugin"]):
                return self._handle_enable(command)

            elif self._matches(cmd, ["disable plugin", "deactivate plugin", "turn off plugin"]):
                return self._handle_disable(command)

            elif self._matches(cmd, ["reload plugin", "hot reload", "refresh plugin"]):
                return self._handle_reload(command)

            elif self._matches(cmd, ["list plugins", "show plugins", "all plugins", "installed plugins"]):
                return self._handle_list(command)

            elif self._matches(cmd, ["plugin status", "plugin info", "plugin details"]):
                return self._handle_info(command)

            elif self._matches(cmd, ["plugin commands", "plugin capabilities"]):
                return self._handle_commands(command)

            elif self._matches(cmd, ["plugin events", "plugin history", "plugin log"]):
                return self._handle_events(command)

            elif self._matches(cmd, ["plugin stats", "plugin diagnostics", "plugin health"]):
                return self._handle_diagnostics()

            elif self._matches(cmd, ["discover plugins", "scan plugins", "find plugins"]):
                return self._handle_discover()

            elif self._matches(cmd, ["plugin security", "security check", "analyze plugin"]):
                return self._handle_security(command)

            elif self._matches(cmd, ["run plugin", "execute plugin", "plugin run"]):
                return self._handle_run(command)

            elif self._matches(cmd, ["plugin help", "plugin guide", "how to plugin"]):
                return self._handle_help()

            else:
                return self._handle_list(command)

        except Exception as e:
            self.logger.error(f"PluginAgent error: {e}")
            return {
                "success": False,
                "response": f"Plugin management error: {str(e)}",
                "error": str(e),
            }
        finally:
            self.status = AgentStatus.IDLE

    def get_capabilities(self) -> list:
        return [
            "install_plugin",
            "uninstall_plugin",
            "enable_plugin",
            "disable_plugin",
            "reload_plugin",
            "list_plugins",
            "plugin_info",
            "plugin_commands",
            "plugin_events",
            "plugin_diagnostics",
            "discover_plugins",
            "security_check",
            "run_plugin",
        ]

    def execute_plugin_command(self, plugin_name: str, command: str,
                               params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Programmatic API: execute a command through a plugin."""
        return self._lifecycle.execute_plugin(plugin_name, command, params)

    def trigger_hook(self, hook_name: str, data: Any) -> Dict[str, Any]:
        """Programmatic API: trigger a hook event."""
        return self._lifecycle.trigger_hook(hook_name, data)

    def get_enabled_plugins(self) -> List[PluginInfo]:
        """Programmatic API: get all enabled plugins."""
        return self._registry.get_enabled_plugins()

    def resolve_plugin_for_command(self, command: str) -> Optional[str]:
        """Programmatic API: find which plugin handles a command."""
        return self._registry.resolve_command(command)

    def _auto_load_plugins(self):
        """Auto-load plugins that were previously enabled."""
        for info in self._registry.get_enabled_plugins():
            if info.module_path and os.path.exists(info.module_path):
                self._lifecycle.enable_plugin(info.metadata.name)

    def _handle_install(self, command: str) -> Dict[str, Any]:
        path = self._extract_path(command)
        if not path:
            return {"success": False, "response": "Please provide a plugin path. Example: 'install plugin C:\\plugins\\my_plugin'"}

        path = Path(path)
        if not path.exists():
            return {"success": False, "response": f"Path not found: {path}"}

        info = self._lifecycle.install_plugin(str(path))
        if info.status == PluginStatus.ERROR:
            return {"success": False, "response": f"Installation failed: {info.error}"}

        lines = [
            f"Plugin installed: {info.metadata.name} v{info.metadata.version}",
            f"  Type: {info.metadata.plugin_type.value}",
            f"  Security: {info.metadata.security_level.value}",
            f"  Load time: {info.load_time_ms:.1f}ms",
        ]
        if info.metadata.capabilities:
            lines.append(f"  Capabilities: {', '.join(c.name for c in info.metadata.capabilities)}")
        return {"success": True, "response": "\n".join(lines), "data": info.to_dict()}

    def _handle_uninstall(self, command: str) -> Dict[str, Any]:
        name = self._extract_name(command)
        if not name:
            return {"success": False, "response": "Please specify a plugin name."}

        success = self._lifecycle.uninstall_plugin(name)
        if success:
            return {"success": True, "response": f"Plugin uninstalled: {name}"}
        return {"success": False, "response": f"Plugin not found: {name}"}

    def _handle_enable(self, command: str) -> Dict[str, Any]:
        name = self._extract_name(command)
        if not name:
            return {"success": False, "response": "Please specify a plugin name."}

        info = self._lifecycle.enable_plugin(name)
        if info.status == PluginStatus.ENABLED:
            return {"success": True, "response": f"Plugin enabled: {name}"}
        return {"success": False, "response": f"Failed to enable: {info.error or info.status.value}"}

    def _handle_disable(self, command: str) -> Dict[str, Any]:
        name = self._extract_name(command)
        if not name:
            return {"success": False, "response": "Please specify a plugin name."}

        info = self._lifecycle.disable_plugin(name)
        return {"success": True, "response": f"Plugin disabled: {name}"}

    def _handle_reload(self, command: str) -> Dict[str, Any]:
        name = self._extract_name(command)
        if not name:
            return {"success": False, "response": "Please specify a plugin name."}

        info = self._lifecycle.reload_plugin(name)
        if info.status != PluginStatus.ERROR:
            return {"success": True, "response": f"Plugin reloaded: {name} ({info.load_time_ms:.1f}ms)"}
        return {"success": False, "response": f"Reload failed: {info.error}"}

    def _handle_list(self, command: str) -> Dict[str, Any]:
        plugins = self._registry.get_all_plugins()
        if not plugins:
            return {"success": True, "response": "No plugins installed."}

        lines = [f"Installed plugins ({len(plugins)}):\n"]
        for p in sorted(plugins, key=lambda x: x.metadata.name):
            status_icon = {
                PluginStatus.ENABLED: "[ON]",
                PluginStatus.DISABLED: "[OFF]",
                PluginStatus.ERROR: "[ERR]",
                PluginStatus.LOADED: "[LD]",
                PluginStatus.INITIALIZED: "[INIT]",
            }.get(p.status, "[??]")

            lines.append(f"  {status_icon} {p.metadata.name} v{p.metadata.version}")
            lines.append(f"      Type: {p.metadata.plugin_type.value} | Security: {p.metadata.security_level.value}")
            if p.metadata.description:
                lines.append(f"      {p.metadata.description}")
            if p.error:
                lines.append(f"      Error: {p.error}")
            lines.append("")

        return {"success": True, "response": "\n".join(lines), "data": [p.to_dict() for p in plugins]}

    def _handle_info(self, command: str) -> Dict[str, Any]:
        name = self._extract_name(command)
        if not name:
            return {"success": False, "response": "Please specify a plugin name."}

        info = self._registry.get_plugin(name)
        if not info:
            return {"success": False, "response": f"Plugin not found: {name}"}

        lines = [
            f"Plugin: {info.metadata.name} v{info.metadata.version}",
            f"  {info.metadata.description}",
            f"  Author: {info.metadata.author}",
            f"  Type: {info.metadata.plugin_type.value}",
            f"  Security: {info.metadata.security_level.value}",
            f"  Status: {info.status.value}",
            f"  Load time: {info.load_time_ms:.1f}ms",
            f"  Executions: {info.execution_count}",
            f"  Path: {info.module_path}",
        ]
        if info.metadata.dependencies:
            lines.append(f"  Dependencies: {', '.join(d.name for d in info.metadata.dependencies)}")
        if info.metadata.capabilities:
            lines.append(f"  Capabilities:")
            for cap in info.metadata.capabilities:
                lines.append(f"    - {cap.name}: {cap.description}")
        if info.metadata.tags:
            lines.append(f"  Tags: {', '.join(info.metadata.tags)}")

        return {"success": True, "response": "\n".join(lines), "data": info.to_dict()}

    def _handle_commands(self, command: str) -> Dict[str, Any]:
        name = self._extract_name(command)
        if not name:
            lines = ["Plugin command prefixes:\n"]
            for info in self._registry.get_enabled_plugins():
                for cap in info.metadata.capabilities:
                    if cap.command_prefix:
                        lines.append(f"  {info.metadata.name}: {cap.command_prefix}")
            return {"success": True, "response": "\n".join(lines)}

        info = self._registry.get_plugin(name)
        if not info:
            return {"success": False, "response": f"Plugin not found: {name}"}

        lines = [f"Commands for {name}:\n"]
        for cap in info.metadata.capabilities:
            lines.append(f"  {cap.command_prefix or cap.name}: {cap.description}")
        return {"success": True, "response": "\n".join(lines)}

    def _handle_events(self, command: str) -> Dict[str, Any]:
        name = self._extract_name(command)
        limit = self._extract_number(command, default=20)
        events = self._registry.get_events(name, limit)
        if not events:
            return {"success": True, "response": "No plugin events."}

        lines = [f"Recent plugin events ({len(events)}):\n"]
        for e in events:
            lines.append(f"  [{e.timestamp[:19]}] {e.plugin_name}: {e.event_type} - {e.message}")
        return {"success": True, "response": "\n".join(lines), "data": [e.to_dict() for e in events]}

    def _handle_diagnostics(self) -> Dict[str, Any]:
        stats = self._registry.get_stats()
        diagnostics = self._lifecycle.get_diagnostics()

        lines = [
            "Plugin System Diagnostics:",
            f"  Total plugins: {stats['total_plugins']}",
            f"  By status: {stats['by_status']}",
            f"  By type: {stats['by_type']}",
            f"  Commands indexed: {stats['commands_indexed']}",
            f"  Hooks indexed: {stats['hooks_indexed']}",
        ]

        error_plugins = [n for n, d in diagnostics.items() if d["status"] == "error"]
        if error_plugins:
            lines.append(f"\n  Error plugins: {', '.join(error_plugins)}")

        return {"success": True, "response": "\n".join(lines), "data": {"stats": stats, "diagnostics": diagnostics}}

    def _handle_discover(self) -> Dict[str, Any]:
        discovered = self._loader.discover_plugins()
        if not discovered:
            return {"success": True, "response": "No plugins found in plugins directory."}

        lines = [f"Discovered plugins ({len(discovered)}):\n"]
        for p in discovered:
            lines.append(f"  {p['name']} ({p['type']})")
            lines.append(f"    Path: {p['path']}")
        return {"success": True, "response": "\n".join(lines), "data": discovered}

    def _handle_security(self, command: str) -> Dict[str, Any]:
        from .sandbox import PluginSandbox, CodeAnalyzer
        name = self._extract_name(command)
        if not name:
            return {"success": False, "response": "Please specify a plugin name."}

        info = self._registry.get_plugin(name)
        if not info:
            return {"success": False, "response": f"Plugin not found: {name}"}

        lines = [
            f"Security analysis for {name}:",
            f"  Security level: {info.metadata.security_level.value}",
            f"  Sandbox: {'Enabled' if info.metadata.security_level != SecurityLevel.TRUSTED else 'Disabled (trusted)'}",
        ]

        if info.module_path:
            try:
                with open(info.module_path, "r") as f:
                    source = f.read()
                analyzer = CodeAnalyzer(info.metadata.security_level)
                warnings = analyzer.analyze(source)
                if warnings:
                    lines.append(f"  Warnings ({len(warnings)}):")
                    for w in warnings:
                        lines.append(f"    - {w}")
                else:
                    lines.append("  No security warnings detected.")
            except Exception as e:
                lines.append(f"  Could not analyze: {e}")

        return {"success": True, "response": "\n".join(lines)}

    def _handle_run(self, command: str) -> Dict[str, Any]:
        parts = command.lower().split(None, 3)
        if len(parts) < 4:
            return {"success": False, "response": "Usage: 'run plugin [name] [command]'"}

        plugin_name = parts[2]
        plugin_cmd = parts[3]
        return self._lifecycle.execute_plugin(plugin_name, plugin_cmd)

    def _handle_help(self) -> Dict[str, Any]:
        lines = [
            "Plugin Management Commands:",
            "  install plugin [path]          - Install a plugin from path",
            "  uninstall plugin [name]        - Remove a plugin",
            "  enable plugin [name]           - Enable a plugin",
            "  disable plugin [name]          - Disable a plugin",
            "  reload plugin [name]           - Hot-reload a plugin",
            "  list plugins                   - Show all plugins",
            "  plugin info [name]             - Show plugin details",
            "  plugin commands [name]         - Show plugin commands",
            "  plugin events [name]           - Show plugin event log",
            "  plugin stats                   - Show diagnostics",
            "  discover plugins               - Scan for plugins",
            "  plugin security [name]         - Analyze plugin security",
            "  run plugin [name] [command]    - Execute plugin command",
        ]
        return {"success": True, "response": "\n".join(lines)}

    @staticmethod
    def _matches(text: str, keywords: list) -> bool:
        return any(kw in text for kw in keywords)

    @staticmethod
    def _extract_path(command: str) -> Optional[str]:
        match = re.search(r"(?:install|add|load)\s+plugin\s+(.+)", command, re.IGNORECASE)
        if match:
            return match.group(1).strip().strip('"').strip("'")
        return None

    @staticmethod
    def _extract_name(command: str) -> Optional[str]:
        match = re.search(r"plugin\s+([a-zA-Z0-9_-]+)", command, re.IGNORECASE)
        if match:
            return match.group(1)
        return None

    @staticmethod
    def _extract_number(command: str, default: int = 0) -> int:
        match = re.search(r"\b(\d+)\b", command)
        return int(match.group(1)) if match else default
