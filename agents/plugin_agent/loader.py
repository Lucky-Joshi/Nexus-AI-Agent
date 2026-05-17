"""
Plugin Loader for the Plugin Management Agent.
Dynamically discovers, validates, and loads plugins from the filesystem.
"""

import importlib
import importlib.util
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from core.logger import Logger

from .models import PluginMetadata, PluginInfo, PluginStatus, SecurityLevel
from .plugin_api import BasePlugin, PluginContext
from .sandbox import PluginSandbox, CodeAnalyzer


class PluginLoader:
    """Discovers, validates, and loads plugins from the filesystem."""

    def __init__(self, plugins_dir: Optional[str] = None):
        self.logger = Logger().get_logger("PluginLoader")
        if plugins_dir is None:
            plugins_dir = str(Path(__file__).parent / "plugins")
        self._plugins_dir = Path(plugins_dir)
        self._plugins_dir.mkdir(parents=True, exist_ok=True)
        self._loaded_plugins: Dict[str, BasePlugin] = {}
        self._sandbox = PluginSandbox()

    def discover_plugins(self) -> List[Dict[str, Any]]:
        """Scan the plugins directory and return info about all plugins."""
        discovered = []

        if not self._plugins_dir.exists():
            return discovered

        for item in self._plugins_dir.iterdir():
            if item.is_dir() and not item.name.startswith(("_", ".")):
                plugin_info = self._discover_plugin_dir(item)
                if plugin_info:
                    discovered.append(plugin_info)
            elif item.suffix == ".py" and not item.name.startswith(("_", ".")):
                plugin_info = self._discover_plugin_file(item)
                if plugin_info:
                    discovered.append(plugin_info)

        return discovered

    def load_plugin(self, plugin_path: str, context: Optional[PluginContext] = None) -> Optional[PluginInfo]:
        """Load a plugin from a path and initialize it."""
        start_time = time.time()
        plugin_path = Path(plugin_path)

        if not plugin_path.exists():
            self.logger.error(f"Plugin path not found: {plugin_path}")
            return None

        try:
            if plugin_path.is_dir():
                plugin_class, metadata = self._load_from_directory(plugin_path)
            elif plugin_path.suffix == ".py":
                plugin_class, metadata = self._load_from_file(plugin_path)
            else:
                self.logger.error(f"Unsupported plugin format: {plugin_path}")
                return None

            if not plugin_class:
                return None

            instance = plugin_class()

            if not isinstance(instance, BasePlugin):
                self.logger.error(f"Plugin does not extend BasePlugin: {metadata.name}")
                return None

            load_time = (time.time() - start_time) * 1000

            info = PluginInfo(
                metadata=metadata,
                status=PluginStatus.LOADED,
                module_path=str(plugin_path),
                loaded_at=time.strftime("%Y-%m-%dT%H:%M:%S"),
                load_time_ms=load_time,
            )

            if context:
                instance.initialize(context)
                info.status = PluginStatus.INITIALIZED

            self._loaded_plugins[metadata.name] = instance
            self.logger.info(f"Plugin loaded: {metadata.name} ({load_time:.1f}ms)")
            return info

        except Exception as e:
            self.logger.error(f"Failed to load plugin {plugin_path}: {e}")
            return PluginInfo(
                metadata=PluginMetadata(name=plugin_path.stem),
                status=PluginStatus.ERROR,
                module_path=str(plugin_path),
                error=str(e),
            )

    def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a plugin and clean up resources."""
        if plugin_name not in self._loaded_plugins:
            return False

        plugin = self._loaded_plugins[plugin_name]
        try:
            plugin.shutdown()
            del self._loaded_plugins[plugin_name]
            self.logger.info(f"Plugin unloaded: {plugin_name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to unload plugin {plugin_name}: {e}")
            return False

    def reload_plugin(self, plugin_name: str, context: Optional[PluginContext] = None) -> Optional[PluginInfo]:
        """Hot-reload a plugin."""
        if plugin_name not in self._loaded_plugins:
            return None

        old_plugin = self._loaded_plugins[plugin_name]
        module_path = old_plugin.context.retrieve("_module_path", "") if old_plugin.context else ""

        self.unload_plugin(plugin_name)

        if module_path:
            return self.load_plugin(module_path, context)
        return None

    def get_plugin(self, plugin_name: str) -> Optional[BasePlugin]:
        """Get a loaded plugin instance."""
        return self._loaded_plugins.get(plugin_name)

    def get_all_loaded(self) -> Dict[str, BasePlugin]:
        return dict(self._loaded_plugins)

    def _discover_plugin_dir(self, dir_path: Path) -> Optional[Dict[str, Any]]:
        """Discover a plugin from a directory structure."""
        manifest_path = dir_path / "plugin.json"
        if manifest_path.exists():
            try:
                with open(manifest_path, "r") as f:
                    manifest = json.load(f)
                metadata = PluginMetadata.from_dict(manifest)
                return {
                    "name": metadata.name,
                    "path": str(dir_path),
                    "type": "directory",
                    "metadata": metadata.to_dict(),
                    "valid": True,
                }
            except Exception as e:
                self.logger.warning(f"Invalid manifest in {dir_path}: {e}")

        main_py = dir_path / "plugin.py"
        if main_py.exists():
            return {
                "name": dir_path.name,
                "path": str(dir_path),
                "type": "directory",
                "metadata": {"name": dir_path.name, "entry_point": "plugin.py"},
                "valid": True,
            }

        return None

    def _discover_plugin_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Discover a plugin from a single Python file."""
        return {
            "name": file_path.stem,
            "path": str(file_path),
            "type": "file",
            "metadata": {"name": file_path.stem, "entry_point": file_path.name},
            "valid": True,
        }

    def _load_from_directory(self, dir_path: Path) -> Tuple[Optional[type], PluginMetadata]:
        """Load a plugin from a directory with plugin.json manifest."""
        manifest_path = dir_path / "plugin.json"
        main_py = dir_path / "plugin.py"

        metadata = PluginMetadata(name=dir_path.name)
        if manifest_path.exists():
            with open(manifest_path, "r") as f:
                data = json.load(f)
            metadata = PluginMetadata.from_dict(data)

        entry_point = main_py if main_py.exists() else dir_path / (metadata.entry_point or "plugin.py")
        if not entry_point.exists():
            self.logger.error(f"No entry point found in {dir_path}")
            return None, metadata

        return self._load_module(entry_point, metadata)

    def _load_from_file(self, file_path: Path) -> Tuple[Optional[type], PluginMetadata]:
        """Load a plugin from a single Python file."""
        metadata = PluginMetadata(name=file_path.stem, entry_point=file_path.name)
        return self._load_module(file_path, metadata)

    def _load_module(self, file_path: Path, metadata: PluginMetadata) -> Tuple[Optional[type], PluginMetadata]:
        """Load a Python module and extract the plugin class."""
        spec = importlib.util.spec_from_file_location(metadata.name, str(file_path))
        if not spec or not spec.loader:
            self.logger.error(f"Cannot create spec for {file_path}")
            return None, metadata

        module = importlib.util.module_from_spec(spec)
        sys.modules[metadata.name] = module

        try:
            spec.loader.exec_module(module)
        except Exception as e:
            self.logger.error(f"Failed to execute module {file_path}: {e}")
            return None, metadata

        plugin_class = None
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (isinstance(attr, type) and
                issubclass(attr, BasePlugin) and
                attr is not BasePlugin):
                plugin_class = attr
                break

        if not plugin_class:
            self.logger.warning(f"No plugin class found in {file_path}")
            return None, metadata

        return plugin_class, metadata
