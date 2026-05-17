"""
Example: Quick Notes Plugin
Simple note-taking plugin with JSON storage.
"""

import json
import os
from datetime import datetime
from pathlib import Path

from agents.plugin_agent.plugin_api import CommandPlugin
from agents.plugin_agent.models import PluginMetadata, PluginCapability, PluginType, SecurityLevel


class QuickNotesPlugin(CommandPlugin):
    """Plugin for quick note-taking and retrieval."""

    def __init__(self):
        super().__init__()
        self._notes_file = Path(__file__).parent / "notes.json"
        self._notes = self._load_notes()

    def _load_notes(self):
        if self._notes_file.exists():
            try:
                with open(self._notes_file, "r") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def _save_notes(self):
        with open(self._notes_file, "w") as f:
            json.dump(self._notes, f, indent=2)

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="Quick Notes",
            version="1.0.0",
            description="Quick note-taking and clipboard plugin",
            author="NEXUS",
            plugin_type=PluginType.COMMAND,
            security_level=SecurityLevel.SANDBOXED,
            tags=["notes", "clipboard", "productivity"],
            capabilities=[
                PluginCapability(
                    name="note",
                    description="Save a quick note",
                    command_prefix="note save",
                    permissions=["write_data"],
                ),
                PluginCapability(
                    name="notes",
                    description="List all saved notes",
                    command_prefix="notes list",
                    permissions=["read_data"],
                ),
                PluginCapability(
                    name="search_notes",
                    description="Search saved notes",
                    command_prefix="notes search",
                    permissions=["read_data"],
                ),
            ],
        )

    def _get_command_handlers(self):
        return {
            "note save": self._handle_save,
            "notes list": self._handle_list,
            "notes search": self._handle_search,
        }

    def _handle_save(self, command, params):
        content = command.replace("note save", "").strip()
        if not content:
            return "Please provide note content. Example: 'note save Meeting at 3pm'"

        note = {
            "id": len(self._notes) + 1,
            "content": content,
            "created_at": datetime.now().isoformat()[:19],
        }
        self._notes.append(note)
        self._save_notes()
        return f"Note saved (#{note['id']}): {content[:50]}{'...' if len(content) > 50 else ''}"

    def _handle_list(self, command, params):
        if not self._notes:
            return "No saved notes."

        lines = [f"Saved notes ({len(self._notes)}):\n"]
        for note in self._notes[-20:]:
            lines.append(f"  #{note['id']} [{note['created_at']}] {note['content'][:80]}")
        return "\n".join(lines)

    def _handle_search(self, command, params):
        query = command.replace("notes search", "").strip().lower()
        if not query:
            return "Please provide a search term. Example: 'notes search meeting'"

        results = [n for n in self._notes if query in n["content"].lower()]
        if not results:
            return f"No notes found for '{query}'"

        lines = [f"Found {len(results)} notes for '{query}':\n"]
        for note in results:
            lines.append(f"  #{note['id']} [{note['created_at']}] {note['content'][:80]}")
        return "\n".join(lines)
