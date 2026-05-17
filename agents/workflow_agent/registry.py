"""
Mode Registry for the Workflow Agent.
Loads mode definitions from JSON presets and custom user modes.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.logger import Logger

from .models import WorkflowMode, ModeAction, ActionType, ModeCondition, ConditionType
from .storage import WorkflowStorage


class ModeRegistry:
    """Registry of all available workflow modes."""

    def __init__(self, presets_dir: Optional[str] = None, storage: Optional[WorkflowStorage] = None):
        self.logger = Logger().get_logger("ModeRegistry")
        if presets_dir is None:
            presets_dir = str(Path(__file__).parent / "presets")
        self._presets_dir = Path(presets_dir)
        self._storage = storage
        self._modes: Dict[str, WorkflowMode] = {}
        self._aliases: Dict[str, str] = {}
        self._load_presets()
        self._load_custom_modes()

    def _load_presets(self):
        """Load all JSON mode presets from the presets directory."""
        if not self._presets_dir.exists():
            self.logger.warning(f"Presets directory not found: {self._presets_dir}")
            return

        for preset_file in self._presets_dir.glob("*.json"):
            try:
                with open(preset_file, "r") as f:
                    data = json.load(f)
                mode = WorkflowMode.from_dict(data)
                self._modes[mode.name.lower()] = mode

                for alias in data.get("aliases", []):
                    self._aliases[alias.lower()] = mode.name.lower()

                self.logger.info(f"Loaded mode preset: {mode.name}")
            except Exception as e:
                self.logger.error(f"Failed to load preset {preset_file}: {e}")

    def _load_custom_modes(self):
        """Load custom user-created modes from storage."""
        if not self._storage:
            return
        try:
            custom_modes = self._storage.get_all_custom_modes()
            for mode in custom_modes:
                if mode.name.lower() not in self._modes:
                    self._modes[mode.name.lower()] = mode
                    self.logger.info(f"Loaded custom mode: {mode.name}")
        except Exception as e:
            self.logger.error(f"Failed to load custom modes: {e}")

    def get_mode(self, name: str) -> Optional[WorkflowMode]:
        """Get a mode by name or alias."""
        name_lower = name.lower().strip()

        if name_lower in self._modes:
            return self._modes[name_lower]

        if name_lower in self._aliases:
            return self._modes[self._aliases[name_lower]]

        for mode_name, mode in self._modes.items():
            if name_lower in mode_name:
                return mode

        for mode_name, mode in self._modes.items():
            if any(alias.lower() == name_lower for alias in mode.tags):
                return mode

        return None

    def get_all_modes(self) -> List[WorkflowMode]:
        """Get all registered modes."""
        return list(self._modes.values())

    def get_modes_by_category(self, category: str) -> List[WorkflowMode]:
        """Get modes filtered by category."""
        return [m for m in self._modes.values() if m.category.lower() == category.lower()]

    def search_modes(self, query: str) -> List[WorkflowMode]:
        """Search modes by name, description, or tags."""
        query_lower = query.lower()
        results = []
        for mode in self._modes.values():
            if (query_lower in mode.name.lower() or
                query_lower in mode.description.lower() or
                any(query_lower in tag.lower() for tag in mode.tags)):
                results.append(mode)
        return results

    def register_mode(self, mode: WorkflowMode):
        """Register a new mode."""
        self._modes[mode.name.lower()] = mode
        if self._storage:
            self._storage.save_custom_mode(mode)
        self.logger.info(f"Registered mode: {mode.name}")

    def unregister_mode(self, name: str) -> bool:
        """Unregister a mode."""
        name_lower = name.lower()
        if name_lower in self._modes:
            del self._modes[name_lower]
            if self._storage:
                self._storage.delete_custom_mode(name)
            return True
        return False

    def get_mode_summary(self) -> List[Dict[str, Any]]:
        """Get a summary of all modes for display."""
        summaries = []
        for mode in sorted(self._modes.values(), key=lambda m: m.priority, reverse=True):
            summaries.append({
                "name": mode.name,
                "description": mode.description,
                "category": mode.category,
                "actions_count": len(mode.actions),
                "apps_count": len(mode.apps_to_launch),
                "agents_count": len(mode.agents_to_activate),
                "tags": mode.tags,
                "enabled": mode.enabled,
            })
        return summaries
