"""
Plugin Management Services for NEXUS.
Handles plugin lifecycle, dependency checking, version compatibility, and diagnostics.
"""

import os
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from core.logger import Logger
from core.config import Config

from .models import (
    PluginInfo, PluginMetadata, PluginStatus, PluginEvent,
    PluginDependency, PluginCapability, PluginType, SecurityLevel,
)
from .plugin_api import BasePlugin, PluginContext
from .loader import PluginLoader
from .registry import PluginRegistry
from .sandbox import PluginSandbox


class DependencyChecker:
    """Checks and resolves plugin dependencies."""

    def __init__(self):
        self.logger = Logger().get_logger("DependencyChecker")

    def check_dependencies(self, metadata: PluginMetadata) -> Tuple[bool, List[str]]:
        """Check if all dependencies are satisfied."""
        issues = []
        for dep in metadata.dependencies:
            if not self._is_available(dep):
                if dep.required:
                    issues.append(f"Missing required dependency: {dep.name} (version {dep.version})")
                else:
                    issues.append(f"Missing optional dependency: {dep.name}")

        return len(issues) == 0, issues

    def _is_available(self, dep: PluginDependency) -> bool:
        if dep.name.startswith("plugin:"):
            return True
        try:
            import importlib
            module = importlib.import_module(dep.name)
            version = getattr(module, "__version__", None)
            if version and dep.version != "*":
                return self._version_matches(version, dep.version)
            return True
        except ImportError:
            return False

    @staticmethod
    def _version_matches(installed: str, required: str) -> bool:
        if required == "*":
            return True
        installed_parts = [int(x) for x in re.findall(r"\d+", installed)]
        required_parts = [int(x) for x in re.findall(r"\d+", required)]
        if not installed_parts or not required_parts:
            return True
        return installed_parts[0] >= required_parts[0]


class VersionChecker:
    """Checks version compatibility between plugins and NEXUS."""

    def __init__(self, nexus_version: str = "1.0.0"):
        self.logger = Logger().get_logger("VersionChecker")
        self._nexus_version = nexus_version

    def check_compatibility(self, metadata: PluginMetadata) -> Tuple[bool, str]:
        """Check if plugin is compatible with current NEXUS version."""
        min_ver = metadata.min_nexus_version
        max_ver = metadata.max_nexus_version

        if not self._version_gte(self._nexus_version, min_ver):
            return False, f"NEXUS version {self._nexus_version} is below minimum {min_ver}"

        if max_ver != "*" and not self._version_lte(self._nexus_version, max_ver):
            return False, f"NEXUS version {self._nexus_version} exceeds maximum {max_ver}"

        return True, "Compatible"

    @staticmethod
    def _version_gte(v1: str, v2: str) -> bool:
        p1 = [int(x) for x in re.findall(r"\d+", v1)]
        p2 = [int(x) for x in re.findall(r"\d+", v2)]
        return p1 >= p2

    @staticmethod
    def _version_lte(v1: str, v2: str) -> bool:
        p1 = [int(x) for x in re.findall(r"\d+", v1)]
        p2 = [int(x) for x in re.findall(r"\d+", v2)]
        return p1 <= p2


class PluginLifecycleManager:
    """Manages the full lifecycle of plugins: load, init, enable, disable, unload."""

    def __init__(self, loader: PluginLoader, registry: PluginRegistry):
        self.logger = Logger().get_logger("PluginLifecycleManager")
        self._loader = loader
        self._registry = registry
        self._dep_checker = DependencyChecker()
        self._version_checker = VersionChecker()
        self._sandbox = PluginSandbox()

    def install_plugin(self, plugin_path: str) -> PluginInfo:
        """Install a plugin: validate, load, and register."""
        plugin_path = Path(plugin_path)
        if not plugin_path.exists():
            return PluginInfo(
                metadata=PluginMetadata(name=plugin_path.stem),
                status=PluginStatus.ERROR,
                error=f"Path not found: {plugin_path}",
            )

        info = self._loader.load_plugin(str(plugin_path))
        if not info:
            return PluginInfo(
                metadata=PluginMetadata(name=plugin_path.stem),
                status=PluginStatus.ERROR,
                error="Failed to load plugin",
            )

        dep_ok, dep_issues = self._dep_checker.check_dependencies(info.metadata)
        if not dep_ok:
            info.status = PluginStatus.ERROR
            info.error = "; ".join(dep_issues)
            self._registry.register(info)
            return info

        compat_ok, compat_msg = self._version_checker.check_compatibility(info.metadata)
        if not compat_ok:
            info.status = PluginStatus.ERROR
            info.error = compat_msg
            self._registry.register(info)
            return info

        info.status = PluginStatus.LOADED
        self._registry.register(info)
        return info

    def enable_plugin(self, plugin_name: str) -> PluginInfo:
        """Enable a plugin for use."""
        info = self._registry.get_plugin(plugin_name)
        if not info:
            return PluginInfo(
                metadata=PluginMetadata(name=plugin_name),
                status=PluginStatus.ERROR,
                error="Plugin not found in registry",
            )

        if info.status == PluginStatus.ERROR:
            return info

        plugin = self._loader.get_plugin(plugin_name)
        if plugin:
            context = PluginContext(config=info.config)
            context.store("_module_path", info.module_path)
            if plugin.initialize(context):
                info.status = PluginStatus.ENABLED
                info.enabled_at = datetime.now().isoformat()
                self._registry.update_status(plugin_name, PluginStatus.ENABLED)
                self.logger.info(f"Plugin enabled: {plugin_name}")
            else:
                info.status = PluginStatus.ERROR
                info.error = "Initialization failed"
                self._registry.update_status(plugin_name, PluginStatus.ERROR, "Initialization failed")
        else:
            info = self.install_plugin(info.module_path)
            if info.status != PluginStatus.ERROR:
                info.status = PluginStatus.ENABLED
                info.enabled_at = datetime.now().isoformat()
                self._registry.update_status(plugin_name, PluginStatus.ENABLED)

        return info

    def disable_plugin(self, plugin_name: str) -> PluginInfo:
        """Disable a plugin without unloading it."""
        info = self._registry.get_plugin(plugin_name)
        if not info:
            return PluginInfo(
                metadata=PluginMetadata(name=plugin_name),
                status=PluginStatus.ERROR,
                error="Plugin not found",
            )

        plugin = self._loader.get_plugin(plugin_name)
        if plugin:
            plugin.shutdown()

        info.status = PluginStatus.DISABLED
        info.disabled_at = datetime.now().isoformat()
        self._registry.update_status(plugin_name, PluginStatus.DISABLED)
        self.logger.info(f"Plugin disabled: {plugin_name}")
        return info

    def uninstall_plugin(self, plugin_name: str) -> bool:
        """Uninstall a plugin: disable, unload, and remove from registry."""
        info = self._registry.get_plugin(plugin_name)
        if not info:
            return False

        self.disable_plugin(plugin_name)
        self._loader.unload_plugin(plugin_name)
        self._registry.unregister(plugin_name)

        if info.module_path and os.path.exists(info.module_path):
            try:
                path = Path(info.module_path)
                if path.is_dir():
                    import shutil
                    shutil.rmtree(path)
                else:
                    path.unlink()
                self.logger.info(f"Plugin files removed: {plugin_name}")
            except Exception as e:
                self.logger.warning(f"Failed to remove plugin files: {e}")

        return True

    def reload_plugin(self, plugin_name: str) -> PluginInfo:
        """Hot-reload a plugin."""
        info = self._registry.get_plugin(plugin_name)
        if not info:
            return PluginInfo(
                metadata=PluginMetadata(name=plugin_name),
                status=PluginStatus.ERROR,
                error="Plugin not found",
            )

        was_enabled = info.status == PluginStatus.ENABLED
        context = PluginContext(config=info.config) if was_enabled else None

        new_info = self._loader.reload_plugin(plugin_name, context)
        if new_info:
            if was_enabled:
                new_info.status = PluginStatus.ENABLED
                new_info.enabled_at = datetime.now().isoformat()
            self._registry.register(new_info)
            self.logger.info(f"Plugin reloaded: {plugin_name}")
            return new_info

        info.status = PluginStatus.ERROR
        info.error = "Reload failed"
        self._registry.update_status(plugin_name, PluginStatus.ERROR, "Reload failed")
        return info

    def execute_plugin(self, plugin_name: str, command: str, params: Dict = None) -> Dict[str, Any]:
        """Execute a command through a plugin."""
        plugin = self._loader.get_plugin(plugin_name)
        if not plugin:
            return {"success": False, "response": f"Plugin not loaded: {plugin_name}"}

        info = self._registry.get_plugin(plugin_name)
        if info:
            info.execution_count += 1
            info.last_executed = datetime.now().isoformat()

        try:
            result = plugin.execute(command, params)
            return result
        except Exception as e:
            return {"success": False, "response": f"Plugin execution error: {str(e)}"}

    def trigger_hook(self, hook_name: str, data: Any) -> Dict[str, Any]:
        """Trigger a hook event across all registered plugins."""
        plugin_names = self._registry.get_hooks_for_event(hook_name)
        results = {}
        for name in plugin_names:
            plugin = self._loader.get_plugin(name)
            info = self._registry.get_plugin(name)
            if plugin and info and info.status == PluginStatus.ENABLED:
                try:
                    results[name] = plugin.handle_hook(hook_name, data)
                except Exception as e:
                    results[name] = {"error": str(e)}
        return results

    def get_diagnostics(self) -> Dict[str, Any]:
        """Get diagnostic information about all plugins."""
        diagnostics = {}
        for info in self._registry.get_all_plugins():
            diag = {
                "status": info.status.value,
                "load_time_ms": info.load_time_ms,
                "execution_count": info.execution_count,
                "error": info.error,
                "dependencies_ok": True,
                "compatible": True,
            }
            dep_ok, dep_issues = self._dep_checker.check_dependencies(info.metadata)
            diag["dependencies_ok"] = dep_ok
            diag["dependency_issues"] = dep_issues

            compat_ok, compat_msg = self._version_checker.check_compatibility(info.metadata)
            diag["compatible"] = compat_ok
            diag["compatibility"] = compat_msg

            diagnostics[info.metadata.name] = diag
        return diagnostics
