"""
Workflow Mode Agent for NEXUS.
Intelligent productivity environments that automatically prepare the desktop,
applications, workflows, and AI agents for specific tasks.
"""

import re
from typing import Any, Dict, List, Optional

from core.base_agent import BaseAgent, AgentStatus
from core.logger import Logger
from core.config import Config

from .models import WorkflowMode, ModeAction, ActionType, ModeStatus, ModeState
from .storage import WorkflowStorage
from .registry import ModeRegistry
from .executor import WorkflowExecutor


class WorkflowAgent(BaseAgent):
    """
    Workflow Mode agent for NEXUS.
    Orchestrates intelligent productivity environments.
    """

    def __init__(self):
        super().__init__("workflow_agent", "Intelligent workflow modes and productivity environments")
        self.logger = Logger().get_logger("WorkflowAgent")
        self.config = Config()

        self._storage = WorkflowStorage()
        self._registry = ModeRegistry(storage=self._storage)
        self._executor = WorkflowExecutor(storage=self._storage)

        self._active_mode: Optional[WorkflowMode] = None
        self._mode_state: Optional[ModeState] = None

        self.logger.info(f"WorkflowAgent initialized ({len(self._registry.get_all_modes())} modes available)")

    def execute(self, command: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        self.status = AgentStatus.BUSY
        try:
            cmd = command.lower()

            if self._matches(cmd, ["start ", "activate ", "enable ", "launch ", "open ", "prepare "]):
                if self._matches(cmd, ["mode"]):
                    return self._handle_activate(command)
                return self._handle_activate(command)

            elif self._matches(cmd, ["stop ", "deactivate ", "disable ", "exit ", "close "]):
                if self._matches(cmd, ["mode"]):
                    return self._handle_deactivate(command)
                return self._handle_deactivate(command)

            elif self._matches(cmd, ["list modes", "show modes", "all modes", "available modes", "workflow modes"]):
                return self._handle_list_modes()

            elif self._matches(cmd, ["mode status", "current mode", "active mode", "what mode"]):
                return self._handle_status()

            elif self._matches(cmd, ["cancel mode", "stop mode", "abort mode"]):
                return self._handle_cancel()

            elif self._matches(cmd, ["mode history", "session history", "mode sessions"]):
                return self._handle_history(command)

            elif self._matches(cmd, ["mode stats", "workflow stats", "productivity stats"]):
                return self._handle_stats()

            elif self._matches(cmd, ["create mode", "new mode", "custom mode"]):
                return self._handle_create_mode(command)

            elif self._matches(cmd, ["delete mode", "remove mode"]):
                return self._handle_delete_mode(command)

            elif self._matches(cmd, ["mode info", "mode details", "show mode"]):
                return self._handle_mode_info(command)

            elif self._matches(cmd, ["pause mode", "resume mode"]):
                return self._handle_pause(command)

            else:
                return self._handle_activate(command)

        except Exception as e:
            self.logger.error(f"WorkflowAgent error: {e}")
            return {
                "success": False,
                "response": f"Workflow error: {str(e)}",
                "error": str(e),
            }
        finally:
            self.status = AgentStatus.IDLE

    def get_capabilities(self) -> list:
        return [
            "activate_mode",
            "deactivate_mode",
            "list_modes",
            "mode_status",
            "cancel_mode",
            "mode_history",
            "mode_stats",
            "create_custom_mode",
            "delete_mode",
            "mode_info",
            "pause_resume_mode",
        ]

    def activate_mode(self, mode_name: str) -> Dict[str, Any]:
        """Programmatic API: activate a workflow mode."""
        mode = self._registry.get_mode(mode_name)
        if not mode:
            return {"success": False, "response": f"Mode '{mode_name}' not found."}

        if self._active_mode:
            self._deactivate_current()

        state = self._executor.execute_mode(mode)
        self._active_mode = mode
        self._mode_state = state

        if state.status == ModeStatus.ACTIVE:
            return {
                "success": True,
                "response": f"Mode activated: {mode.name}\n{mode.description}\n\nActions: {state.completed_actions}/{state.total_actions} completed",
                "data": state.to_dict(),
            }
        elif state.status == ModeStatus.ERROR:
            return {
                "success": False,
                "response": f"Mode activation failed: {state.error}",
                "data": state.to_dict(),
            }
        return {
            "success": state.status != ModeStatus.CANCELLED,
            "response": f"Mode {state.status.value}: {mode.name}",
            "data": state.to_dict(),
        }

    def deactivate_mode(self) -> Dict[str, Any]:
        """Programmatic API: deactivate current mode."""
        if not self._active_mode:
            return {"success": False, "response": "No active mode."}

        state = self._executor.deactivate_mode(self._active_mode, self._mode_state)
        self._active_mode = None
        self._mode_state = state
        return {"success": True, "response": f"Mode deactivated: {state.mode_name}"}

    def get_active_mode(self) -> Optional[Dict[str, Any]]:
        """Programmatic API: get current active mode."""
        if self._active_mode:
            return self._active_mode.to_dict()
        return None

    def _handle_activate(self, command: str) -> Dict[str, Any]:
        mode_name = self._extract_mode_name(command)
        if not mode_name:
            modes = ", ".join(m.name for m in self._registry.get_all_modes()[:8])
            return {"success": False, "response": f"Please specify a mode. Available: {modes}..."}

        return self.activate_mode(mode_name)

    def _handle_deactivate(self, command: str) -> Dict[str, Any]:
        return self.deactivate_mode()

    def _handle_list_modes(self) -> Dict[str, Any]:
        summaries = self._registry.get_mode_summary()
        if not summaries:
            return {"success": True, "response": "No workflow modes available."}

        lines = ["Available Workflow Modes:\n"]
        for s in summaries:
            icon = ">>" if self._active_mode and self._active_mode.name == s["name"] else "  "
            lines.append(f"  {icon} {s['name']} ({s['category']})")
            lines.append(f"      {s['description']}")
            lines.append(f"      Actions: {s['actions_count']} | Apps: {s['apps_count']} | Agents: {s['agents_count']}")
            if s["tags"]:
                lines.append(f"      Tags: {', '.join(s['tags'])}")
            lines.append("")

        return {"success": True, "response": "\n".join(lines), "data": summaries}

    def _handle_status(self) -> Dict[str, Any]:
        if self._active_mode:
            state = self._mode_state
            lines = [
                f"Active Mode: {self._active_mode.name}",
                f"  {self._active_mode.description}",
                f"  Status: {state.status.value}",
                f"  Progress: {state.progress:.0f}%",
                f"  Actions: {state.completed_actions}/{state.total_actions} completed",
                f"  Apps launched: {len(state.launched_apps)}",
                f"  Agents activated: {len(state.activated_agents)}",
            ]
            if state.error:
                lines.append(f"  Error: {state.error}")
            return {"success": True, "response": "\n".join(lines), "data": state.to_dict()}
        return {"success": True, "response": "No active mode."}

    def _handle_cancel(self) -> Dict[str, Any]:
        if self._executor.is_running:
            self._executor.cancel()
            return {"success": True, "response": "Mode activation cancelled."}
        return {"success": False, "response": "No mode activation in progress."}

    def _handle_history(self, command: str) -> Dict[str, Any]:
        limit = self._extract_number(command, default=10)
        sessions = self._storage.get_recent_sessions(limit)
        if not sessions:
            return {"success": True, "response": "No mode session history."}

        lines = [f"Recent mode sessions ({len(sessions)}):\n"]
        for s in sessions:
            duration = f"{s.duration_seconds:.0f}s" if s.duration_seconds > 0 else "N/A"
            status_icon = {"completed": "[OK]", "error": "[ERR]", "cancelled": "[X]"}.get(s.status, "[?]")
            lines.append(f"  {status_icon} {s.mode_name} | {s.started_at[:16]} | {duration}")
            lines.append(f"      Actions: {s.actions_completed} completed, {s.actions_failed} failed")
        return {"success": True, "response": "\n".join(lines), "data": [s.to_dict() for s in sessions]}

    def _handle_stats(self) -> Dict[str, Any]:
        stats = self._storage.get_stats()
        lines = [
            "Workflow Mode Statistics:",
            f"  Total sessions: {stats['total_sessions']}",
            f"  Today: {stats['today_sessions']}",
            f"  This week: {stats['week_sessions']}",
            f"  Total time: {stats['total_duration_hours']}h",
            f"  Custom modes: {stats['custom_modes']}",
            f"  Active: {stats['active_mode'] or 'None'}",
        ]
        if stats["top_modes"]:
            lines.append("\n  Top modes:")
            for name, count in list(stats["top_modes"].items())[:5]:
                lines.append(f"    {name}: {count} sessions")
        return {"success": True, "response": "\n".join(lines), "data": stats}

    def _handle_create_mode(self, command: str) -> Dict[str, Any]:
        name = self._extract_field(command, ["name:", "named"])
        if not name:
            return {"success": False, "response": "Please provide a mode name. Example: 'create mode name: My Workflow'"}

        mode = WorkflowMode(name=name, description=f"Custom mode: {name}")
        self._registry.register_mode(mode)
        return {"success": True, "response": f"Custom mode created: {name}"}

    def _handle_delete_mode(self, command: str) -> Dict[str, Any]:
        name = self._extract_content(command, ["delete mode ", "remove mode "])
        if not name:
            return {"success": False, "response": "Please specify a mode to delete."}
        success = self._registry.unregister_mode(name)
        if success:
            return {"success": True, "response": f"Mode deleted: {name}"}
        return {"success": False, "response": f"Mode not found: {name}"}

    def _handle_mode_info(self, command: str) -> Dict[str, Any]:
        name = self._extract_content(command, ["mode info ", "mode details ", "show mode "])
        if not name:
            return {"success": False, "response": "Please specify a mode."}

        mode = self._registry.get_mode(name)
        if not mode:
            return {"success": False, "response": f"Mode not found: {name}"}

        lines = [
            f"Mode: {mode.name}",
            f"  {mode.description}",
            f"  Category: {mode.category}",
            f"  Priority: {mode.priority}",
            f"  Tags: {', '.join(mode.tags) if mode.tags else 'None'}",
            f"\n  Apps to launch ({len(mode.apps_to_launch)}):",
        ]
        for app in mode.apps_to_launch:
            lines.append(f"    - {app}")
        lines.append(f"\n  Agents to activate ({len(mode.agents_to_activate)}):")
        for agent in mode.agents_to_activate:
            lines.append(f"    - {agent}")
        lines.append(f"\n  Actions ({len(mode.actions)}):")
        for action in sorted(mode.actions, key=lambda a: a.order):
            lines.append(f"    {action.order}. {action.name or action.action_type.value}: {action.target}")
        return {"success": True, "response": "\n".join(lines), "data": mode.to_dict()}

    def _handle_pause(self, command: str) -> Dict[str, Any]:
        if "pause" in command.lower():
            if self._mode_state and self._mode_state.status == ModeStatus.ACTIVE:
                self._mode_state.status = ModeStatus.PAUSED
                return {"success": True, "response": f"Mode paused: {self._active_mode.name}"}
        elif "resume" in command.lower():
            if self._mode_state and self._mode_state.status == ModeStatus.PAUSED:
                self._mode_state.status = ModeStatus.ACTIVE
                return {"success": True, "response": f"Mode resumed: {self._active_mode.name}"}
        return {"success": False, "response": "No mode to pause/resume."}

    def _deactivate_current(self):
        if self._active_mode and self._mode_state:
            self._executor.deactivate_mode(self._active_mode, self._mode_state)

    def _extract_mode_name(self, command: str) -> Optional[str]:
        cmd_lower = command.lower()
        prefixes = ["start ", "activate ", "enable ", "launch ", "open ", "prepare "]
        suffixes = [" mode", " workflow", " environment"]

        content = cmd_lower
        for prefix in prefixes:
            if content.startswith(prefix):
                content = content[len(prefix):]
                break

        for suffix in suffixes:
            if content.endswith(suffix):
                content = content[:-len(suffix)]

        content = content.strip()
        if not content:
            return None

        mode = self._registry.get_mode(content)
        if mode:
            return mode.name

        return content.title()

    @staticmethod
    def _matches(text: str, keywords: list) -> bool:
        return any(kw in text for kw in keywords)

    @staticmethod
    def _extract_content(command: str, prefixes: list) -> str:
        cmd_lower = command.lower()
        for prefix in prefixes:
            if cmd_lower.startswith(prefix):
                return command[len(prefix):].strip()
        return ""

    @staticmethod
    def _extract_field(command: str, prefixes: list) -> Optional[str]:
        cmd_lower = command.lower()
        for prefix in prefixes:
            idx = cmd_lower.find(prefix)
            if idx != -1:
                return command[idx + len(prefix):].strip().split("\n")[0].strip()
        return None

    @staticmethod
    def _extract_number(command: str, default: int = 0) -> int:
        match = re.search(r"\b(\d+)\b", command)
        return int(match.group(1)) if match else default
