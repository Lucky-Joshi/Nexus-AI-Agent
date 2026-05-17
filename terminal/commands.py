"""
NEXUS - Terminal Command System
Slash command parser, registry, autocomplete, and dynamic help.
"""

import re
from typing import Any, Callable, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from core.logger import Logger


@dataclass
class Command:
    """A registered terminal command."""
    name: str
    description: str
    handler: Callable
    aliases: List[str] = field(default_factory=list)
    category: str = "general"
    requires_args: bool = False
    arg_description: str = ""
    autocomplete: List[str] = field(default_factory=list)

    def matches(self, text: str) -> bool:
        text_lower = text.lower().strip()
        if text_lower == self.name.lower():
            return True
        if text_lower.startswith(self.name.lower() + " "):
            return True
        for alias in self.aliases:
            if text_lower == alias.lower() or text_lower.startswith(alias.lower() + " "):
                return True
        return False

    def parse_args(self, text: str) -> str:
        text_lower = text.lower().strip()
        if text_lower == self.name.lower():
            return ""
        if text_lower.startswith(self.name.lower() + " "):
            return text[len(self.name):].strip()
        for alias in self.aliases:
            if text_lower.startswith(alias.lower() + " "):
                return text[len(alias):].strip()
        return ""


class CommandRegistry:
    """Registry for all terminal commands."""

    def __init__(self):
        self.logger = Logger().get_logger("CommandRegistry")
        self._commands: Dict[str, Command] = {}
        self._categories: Dict[str, List[str]] = {}

    def register(self, name: str, description: str, handler: Callable,
                 aliases: List[str] = None, category: str = "general",
                 requires_args: bool = False, arg_description: str = "",
                 autocomplete: List[str] = None):
        """Register a new command."""
        cmd = Command(
            name=name,
            description=description,
            handler=handler,
            aliases=aliases or [],
            category=category,
            requires_args=requires_args,
            arg_description=arg_description,
            autocomplete=autocomplete or [],
        )
        self._commands[name] = cmd
        for alias in (aliases or []):
            self._commands[alias] = cmd

        if category not in self._categories:
            self._categories[category] = []
        if name not in self._categories[category]:
            self._categories[category].append(name)

        self.logger.debug(f"Command registered: /{name} ({category})")

    def find_command(self, text: str) -> Optional[Command]:
        """Find a command that matches the input text."""
        text_lower = text.lower().strip()
        for name, cmd in self._commands.items():
            if cmd.matches(text):
                return cmd
        return None

    def execute(self, text: str, context: Dict[str, Any] = None) -> Any:
        """Execute a command from text input."""
        cmd = self.find_command(text)
        if not cmd:
            return None

        args = cmd.parse_args(text)
        if cmd.requires_args and not args:
            return {
                "success": False,
                "response": f"Command /{cmd.name} requires arguments: {cmd.arg_description}",
            }

        try:
            result = cmd.handler(args, context or {})
            if isinstance(result, dict):
                return result
            return {"success": True, "response": str(result)}
        except Exception as e:
            self.logger.error(f"Command execution error: {e}")
            return {"success": False, "response": f"Error: {str(e)}"}

    def get_autocomplete(self, text: str) -> List[str]:
        """Get autocomplete suggestions for partial input."""
        text_lower = text.lower().strip()
        suggestions = []

        if text_lower.startswith("/"):
            search = text_lower[1:]
            for name, cmd in self._commands.items():
                if name.startswith(search) and name == cmd.name:
                    suggestions.append(f"/{name}")
        else:
            cmd = self.find_command(text)
            if cmd:
                args = cmd.parse_args(text)
                if cmd.autocomplete:
                    for ac in cmd.autocomplete:
                        if ac.lower().startswith(args.lower()):
                            suggestions.append(ac)

        return suggestions[:10]

    def get_help(self, category: str = None) -> str:
        """Generate help text for commands."""
        lines = ["NEXUS Terminal Commands\n" + "=" * 40]

        if category:
            cmds = self._categories.get(category, [])
            if not cmds:
                return f"No commands in category: {category}"
            lines.append(f"\nCategory: {category}\n")
            for name in cmds:
                cmd = self._commands[name]
                alias_str = f" ({', '.join('/' + a for a in cmd.aliases)})" if cmd.aliases else ""
                lines.append(f"  /{name}{alias_str}")
                lines.append(f"    {cmd.description}")
        else:
            for cat, cmds in sorted(self._categories.items()):
                lines.append(f"\n[{cat.upper()}]")
                for name in cmds:
                    cmd = self._commands[name]
                    alias_str = f" ({', '.join('/' + a for a in cmd.aliases)})" if cmd.aliases else ""
                    lines.append(f"  /{name}{alias_str}")
                    lines.append(f"    {cmd.description}")

        lines.append("\n" + "=" * 40)
        lines.append("Type /help [category] for detailed help")
        lines.append("Use Tab for autocomplete")
        return "\n".join(lines)

    def get_all_commands(self) -> List[Command]:
        """Get all unique commands."""
        seen = set()
        unique = []
        for name, cmd in self._commands.items():
            if name not in seen:
                seen.add(name)
                unique.append(cmd)
        return unique

    def get_categories(self) -> List[str]:
        """Get all command categories."""
        return list(self._categories.keys())
