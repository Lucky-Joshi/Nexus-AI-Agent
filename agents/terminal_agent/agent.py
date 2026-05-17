"""
Terminal Agent for NEXUS.
Safely executes terminal and shell commands with validation, session management,
output streaming, and script execution.
"""

import os
import re
from typing import Any, Callable, Dict, Generator, List, Optional

from core.base_agent import BaseAgent, AgentStatus
from core.logger import Logger
from core.config import Config

from .models import TerminalSession, CommandRecord, CommandStatus, SessionStatus
from .validator import CommandValidator, SafetyLevel
from .storage import TerminalStorage
from .services import ExecutionEngine, SessionManager, OutputStreamer, ScriptRunner


class TerminalAgent(BaseAgent):
    """
    Terminal agent for NEXUS.
    Thin orchestrator delegating to specialized service classes.
    """

    def __init__(self):
        super().__init__("terminal_agent", "Terminal command execution, session management, and script running")
        self.logger = Logger().get_logger("TerminalAgent")
        self.config = Config()

        strict_mode = self.config.get("terminal_agent.strict_mode", True)
        default_timeout = self.config.get("terminal_agent.default_timeout", 30)
        max_output = self.config.get("terminal_agent.max_output_size", 50000)

        self._validator = CommandValidator(strict_mode=strict_mode)
        self._storage = TerminalStorage()
        self._executor = ExecutionEngine(
            validator=self._validator,
            storage=self._storage,
            default_timeout=default_timeout,
            max_output_size=max_output,
        )
        self._session_mgr = SessionManager(storage=self._storage)
        self._streamer = OutputStreamer()
        self._script_runner = ScriptRunner(
            validator=self._validator,
            storage=self._storage,
            default_timeout=self.config.get("terminal_agent.script_timeout", 120),
        )

        self._current_session: Optional[TerminalSession] = None
        self._get_default_session()

        self.logger.info(f"TerminalAgent initialized (strict_mode={strict_mode}, timeout={default_timeout}s)")

    def execute(self, command: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        self.status = AgentStatus.BUSY
        try:
            cmd = command.lower()

            if self._matches(cmd, ["run ", "execute ", "exec ", "terminal run", "shell run"]):
                return self._handle_run(command)

            elif self._matches(cmd, ["run script", "execute script", "run file", "exec script"]):
                return self._handle_run_script(command)

            elif self._matches(cmd, ["run python", "exec python", "python code", "run code"]):
                return self._handle_run_python(command)

            elif self._matches(cmd, ["stream ", "stream run", "stream execute"]):
                return self._handle_stream(command)

            elif self._matches(cmd, ["new session", "create session", "open session", "new terminal"]):
                return self._handle_new_session(command)

            elif self._matches(cmd, ["switch session", "use session", "select session"]):
                return self._handle_switch_session(command)

            elif self._matches(cmd, ["close session", "end session", "exit session"]):
                return self._handle_close_session(command)

            elif self._matches(cmd, ["list sessions", "show sessions", "all sessions", "sessions"]):
                return self._handle_list_sessions()

            elif self._matches(cmd, ["cd ", "change dir", "change directory", "set directory"]):
                return self._handle_cd(command)

            elif self._matches(cmd, ["set env", "set environment", "set variable"]):
                return self._handle_set_env(command)

            elif self._matches(cmd, ["kill process", "kill command", "stop command", "stop process"]):
                return self._handle_kill(command)

            elif self._matches(cmd, ["kill all", "stop all", "kill all processes"]):
                return self._handle_kill_all()

            elif self._matches(cmd, ["command history", "history", "recent commands", "terminal history"]):
                return self._handle_history(command)

            elif self._matches(cmd, ["search history", "find command", "search commands"]):
                return self._handle_search_history(command)

            elif self._matches(cmd, ["failed commands", "errors", "command errors"]):
                return self._handle_failed()

            elif self._matches(cmd, ["blocked commands", "safety log", "security log"]):
                return self._handle_blocked()

            elif self._matches(cmd, ["terminal stats", "terminal status", "stats"]):
                return self._handle_stats()

            elif self._matches(cmd, ["check command", "validate command", "is safe", "safety check"]):
                return self._handle_check(command)

            elif self._matches(cmd, ["clear history", "clear terminal", "reset history"]):
                return self._handle_clear_history(command)

            elif self._matches(cmd, ["set timeout", "timeout"]):
                return self._handle_set_timeout(command)

            elif self._matches(cmd, ["strict mode", "safety mode"]):
                return self._handle_strict_mode(command)

            elif self._matches(cmd, ["force run", "force execute", "run force"]):
                return self._handle_force_run(command)

            elif self._matches(cmd, ["pwd", "print working directory", "current directory", "where am i"]):
                return self._handle_pwd()

            else:
                return self._handle_run(command)

        except Exception as e:
            self.logger.error(f"TerminalAgent error: {e}")
            return {
                "success": False,
                "response": f"Terminal error: {str(e)}",
                "error": str(e),
            }
        finally:
            self.status = AgentStatus.IDLE

    def get_capabilities(self) -> list:
        return [
            "run_command",
            "run_script",
            "run_python",
            "stream_command",
            "new_session",
            "switch_session",
            "close_session",
            "list_sessions",
            "change_directory",
            "set_environment",
            "kill_process",
            "kill_all",
            "command_history",
            "search_history",
            "failed_commands",
            "blocked_commands",
            "terminal_stats",
            "check_command_safety",
            "clear_history",
            "set_timeout",
            "strict_mode",
            "force_run",
            "pwd",
        ]

    def run_command(self, command: str, session_id: Optional[str] = None,
                    timeout: Optional[int] = None, force: bool = False) -> Dict[str, Any]:
        """Programmatic API: run a terminal command."""
        session = self._get_session(session_id) if session_id else self._get_default_session()
        record = self._executor.execute(command, session=session, timeout=timeout, force=force)
        return {
            "success": record.status == CommandStatus.COMPLETED,
            "response": self._format_record(record),
            "data": record.to_dict(),
        }

    def stream_command(self, command: str, callback: Optional[Callable] = None,
                       session_id: Optional[str] = None, timeout: Optional[int] = None) -> Dict[str, Any]:
        """Programmatic API: run a command with streaming output."""
        session = self._get_session(session_id) if session_id else self._get_default_session()

        if callback:
            record = self._executor.execute(command, session=session, timeout=timeout, stream_callback=callback)
        else:
            stream_id = f"stream_{record.id}" if hasattr(self, 'record') else f"stream_{command[:8]}"
            self._streamer.create_stream(stream_id)

            def stream_cb(stream_type: str, data: str):
                self._streamer.push(stream_id, stream_type, data)

            record = self._executor.execute(command, session=session, timeout=timeout, stream_callback=stream_cb)
            self._streamer.close_stream(stream_id)

        return {
            "success": record.status == CommandStatus.COMPLETED,
            "response": self._format_record(record),
            "data": record.to_dict(),
        }

    def run_script(self, script_path: str, args: Optional[List[str]] = None,
                   session_id: Optional[str] = None, timeout: Optional[int] = None) -> Dict[str, Any]:
        """Programmatic API: run a script file."""
        session = self._get_session(session_id) if session_id else self._get_default_session()
        record = self._script_runner.run_script(script_path, args=args, session=session, timeout=timeout)
        return {
            "success": record.status == CommandStatus.COMPLETED,
            "response": self._format_record(record),
            "data": record.to_dict(),
        }

    def run_python(self, code: str, session_id: Optional[str] = None,
                   timeout: Optional[int] = None) -> Dict[str, Any]:
        """Programmatic API: execute Python code."""
        session = self._get_session(session_id) if session_id else self._get_default_session()
        record = self._script_runner.run_python(code, session=session, timeout=timeout)
        return {
            "success": record.status == CommandStatus.COMPLETED,
            "response": self._format_record(record),
            "data": record.to_dict(),
        }

    def check_safety(self, command: str) -> Dict[str, Any]:
        """Programmatic API: check command safety without executing."""
        report = self._validator.get_safety_report(command)
        return {
            "success": True,
            "response": f"Safety: {report['safety_level']}\nReason: {report['reason']}",
            "data": report,
        }

    def _handle_run(self, command: str) -> Dict[str, Any]:
        cmd_content = self._extract_content(command, [
            "run ", "execute ", "exec ", "terminal run ", "shell run ",
        ])
        if not cmd_content:
            return {"success": False, "response": "Please provide a command to run. Example: 'run dir'"}

        timeout = self._extract_number(command, default=None)
        record = self._executor.execute(cmd_content, session=self._current_session, timeout=timeout)
        return {
            "success": record.status == CommandStatus.COMPLETED,
            "response": self._format_record(record),
            "data": record.to_dict(),
        }

    def _handle_run_script(self, command: str) -> Dict[str, Any]:
        path = self._extract_field(command, ["script:", "file:", "path:"])
        if not path:
            path_match = re.search(r"(?:run script|execute script|run file|exec script)\s+(.+?)(?:\s+with\s+|\s+args\s+|$)", command)
            if path_match:
                path = path_match.group(1).strip()

        if not path:
            return {"success": False, "response": "Please provide a script path. Example: 'run script C:\\scripts\\test.py'"}

        args = self._extract_args(command, ["with args", "args"])
        timeout = self._extract_number(command, default=None)

        record = self._script_runner.run_script(
            path, args=args, session=self._current_session, timeout=timeout,
        )
        return {
            "success": record.status == CommandStatus.COMPLETED,
            "response": self._format_record(record),
            "data": record.to_dict(),
        }

    def _handle_run_python(self, command: str) -> Dict[str, Any]:
        code = self._extract_content(command, [
            "run python", "exec python", "python code", "run code",
        ])
        if not code:
            return {"success": False, "response": "Please provide Python code. Example: 'run python print(\"hello\")'"}

        timeout = self._extract_number(command, default=None)
        record = self._script_runner.run_python(code, session=self._current_session, timeout=timeout)
        return {
            "success": record.status == CommandStatus.COMPLETED,
            "response": self._format_record(record),
            "data": record.to_dict(),
        }

    def _handle_stream(self, command: str) -> Dict[str, Any]:
        cmd_content = self._extract_content(command, [
            "stream ", "stream run ", "stream execute ",
        ])
        if not cmd_content:
            return {"success": False, "response": "Please provide a command to stream. Example: 'stream ping -t google.com'"}

        stream_id = f"stream_{cmd_content[:8].replace(' ', '_')}"
        self._streamer.create_stream(stream_id)

        def stream_cb(stream_type: str, data: str):
            self._streamer.push(stream_id, stream_type, data)

        timeout = self._extract_number(command, default=None)
        record = self._executor.execute(
            cmd_content, session=self._current_session,
            timeout=timeout, stream_callback=stream_cb,
        )

        output = self._streamer.get_all_pending(stream_id)
        self._streamer.close_stream(stream_id)

        lines = [f"Streamed command: {cmd_content}\n"]
        lines.append(f"Status: {record.status.value}")
        if record.output:
            lines.append(f"\nOutput:\n{record.output[:2000]}")
        if record.error:
            lines.append(f"\nError:\n{record.error[:500]}")
        lines.append(f"\nDuration: {record.duration_seconds:.2f}s")

        return {
            "success": record.status == CommandStatus.COMPLETED,
            "response": "\n".join(lines),
            "data": record.to_dict(),
        }

    def _handle_new_session(self, command: str) -> Dict[str, Any]:
        name = self._extract_field(command, ["name:", "named"]) or None
        directory = self._extract_field(command, ["dir:", "directory:", "in"]) or None

        session = self._session_mgr.create_session(name=name, working_directory=directory)
        self._current_session = session

        return {
            "success": True,
            "response": f"Session created (ID: {session.id})\nName: {session.name}\nDirectory: {session.working_directory}",
            "data": session.to_dict(),
        }

    def _handle_switch_session(self, command: str) -> Dict[str, Any]:
        session_id = self._extract_id(command)
        if not session_id:
            name_match = re.search(r"(?:switch|use|select)\s+session\s+(.+)", command, re.IGNORECASE)
            if name_match:
                name = name_match.group(1).strip()
                for s in self._session_mgr.get_all_sessions():
                    if s.name.lower() == name.lower():
                        session_id = s.id
                        break

        if not session_id:
            return {"success": False, "response": "Please provide a session ID or name."}

        session = self._session_mgr.get_session(session_id)
        if not session:
            return {"success": False, "response": f"Session {session_id} not found."}

        self._current_session = session
        return {
            "success": True,
            "response": f"Switched to session: {session.name} (ID: {session.id})\nDirectory: {session.working_directory}",
            "data": session.to_dict(),
        }

    def _handle_close_session(self, command: str) -> Dict[str, Any]:
        session_id = self._extract_id(command)
        if not session_id and self._current_session:
            session_id = self._current_session.id

        if not session_id:
            return {"success": False, "response": "No active session to close."}

        success = self._session_mgr.close_session(session_id)
        if success:
            if self._current_session and self._current_session.id == session_id:
                self._current_session = self._session_mgr.get_or_default()
            return {"success": True, "response": f"Session {session_id} closed."}
        return {"success": False, "response": f"Session {session_id} not found."}

    def _handle_list_sessions(self) -> Dict[str, Any]:
        sessions = self._session_mgr.get_all_sessions()
        if not sessions:
            return {"success": True, "response": "No terminal sessions."}

        lines = [f"Terminal sessions ({len(sessions)}):\n"]
        for s in sessions:
            current = " <-- current" if self._current_session and s.id == self._current_session.id else ""
            status_icon = {"active": "[A]", "idle": "[I]", "closed": "[C]", "error": "[E]"}.get(s.status.value, "[?]")
            lines.append(f"  {status_icon} {s.id} | {s.name}{current}")
            lines.append(f"      Dir: {s.working_directory} | Commands: {len(s.command_history)}")

        return {
            "success": True,
            "response": "\n".join(lines),
            "data": [s.to_dict() for s in sessions],
        }

    def _handle_cd(self, command: str) -> Dict[str, Any]:
        directory = self._extract_content(command, [
            "cd ", "change dir ", "change directory ", "set directory ",
        ])
        if not directory:
            return {"success": False, "response": "Please provide a directory. Example: 'cd C:\\Users'"}

        directory = directory.strip().strip('"').strip("'")

        if not os.path.isdir(directory):
            return {"success": False, "response": f"Directory not found: {directory}"}

        if self._current_session:
            self._session_mgr.set_working_directory(self._current_session.id, directory)
            self._current_session = self._session_mgr.get_session(self._current_session.id)

        return {
            "success": True,
            "response": f"Working directory set to: {directory}",
        }

    def _handle_set_env(self, command: str) -> Dict[str, Any]:
        env_match = re.search(r"set\s+(?:env|environment|variable)\s+(\w+)\s*[=:]\s*(.+)", command, re.IGNORECASE)
        if not env_match:
            return {"success": False, "response": "Usage: 'set env KEY=value' or 'set environment KEY = value'"}

        key = env_match.group(1)
        value = env_match.group(2).strip()

        if self._current_session:
            self._session_mgr.set_environment(self._current_session.id, key, value)
            return {"success": True, "response": f"Environment variable set: {key}={value}"}
        return {"success": False, "response": "No active session."}

    def _handle_kill(self, command: str) -> Dict[str, Any]:
        record_id = self._extract_id(command)
        if not record_id:
            return {"success": False, "response": "Please provide a command/record ID to kill."}

        success = self._executor.kill_process(record_id)
        if success:
            return {"success": True, "response": f"Process {record_id} killed."}
        return {"success": False, "response": f"Process {record_id} not found or already finished."}

    def _handle_kill_all(self) -> Dict[str, Any]:
        count = self._executor.kill_all()
        return {
            "success": True,
            "response": f"Killed {count} running process(es)." if count else "No running processes to kill.",
        }

    def _handle_history(self, command: str) -> Dict[str, Any]:
        limit = self._extract_number(command, default=20)

        if self._current_session:
            records = self._storage.get_session_commands(self._current_session.id, limit)
        else:
            records = self._storage.get_recent_commands(limit)

        if not records:
            return {"success": True, "response": "No command history."}

        lines = [f"Command history ({len(records)}):\n"]
        for r in records:
            status_icon = {"completed": "[OK]", "failed": "[FAIL]", "blocked": "[BLOCKED]",
                          "timeout": "[TIMEOUT]", "killed": "[KILLED]"}.get(r.status.value, "[?]")
            duration = f"{r.duration_seconds:.1f}s" if r.duration_seconds > 0 else ""
            lines.append(f"  {status_icon} {r.id} | {r.command[:60]}")
            lines.append(f"      {r.started_at[:19]} | {duration}")

        return {
            "success": True,
            "response": "\n".join(lines),
            "data": [r.to_dict() for r in records],
        }

    def _handle_search_history(self, command: str) -> Dict[str, Any]:
        query = self._extract_content(command, [
            "search history ", "find command ", "search commands ",
        ])
        if not query:
            return {"success": False, "response": "Please provide a search term."}

        records = self._storage.search_commands(query, limit=20)
        if not records:
            return {"success": True, "response": f"No commands found for: '{query}'"}

        lines = [f"Found {len(records)} commands for '{query}':\n"]
        for r in records:
            lines.append(f"  [{r.status.value}] {r.command[:80]}")
        return {
            "success": True,
            "response": "\n".join(lines),
            "data": [r.to_dict() for r in records],
        }

    def _handle_failed(self) -> Dict[str, Any]:
        records = self._storage.get_failed_commands(limit=20)
        if not records:
            return {"success": True, "response": "No failed commands."}

        lines = [f"Failed commands ({len(records)}):\n"]
        for r in records:
            lines.append(f"  [{r.started_at[:19]}] {r.command[:60]}")
            lines.append(f"    Error: {r.error[:100]}")
        return {
            "success": True,
            "response": "\n".join(lines),
            "data": [r.to_dict() for r in records],
        }

    def _handle_blocked(self) -> Dict[str, Any]:
        records = self._storage.get_blocked_commands(limit=20)
        if not records:
            return {"success": True, "response": "No blocked commands."}

        lines = [f"Blocked commands ({len(records)}):\n"]
        for r in records:
            lines.append(f"  [{r.started_at[:19]}] {r.command[:60]}")
            lines.append(f"    Reason: {r.safety_reason}")
        return {
            "success": True,
            "response": "\n".join(lines),
            "data": [r.to_dict() for r in records],
        }

    def _handle_stats(self) -> Dict[str, Any]:
        stats = self._storage.get_stats()
        session_stats = self._session_mgr.get_stats()
        stats.update(session_stats)
        stats["running_processes"] = self._executor.running_count
        stats["strict_mode"] = self._validator.strict_mode

        lines = [
            "Terminal Agent Statistics:",
            f"  Total commands: {stats['total_commands']}",
            f"  Completed: {stats['completed_commands']}",
            f"  Failed: {stats['failed_commands']}",
            f"  Blocked: {stats['blocked_commands']}",
            f"  Average duration: {stats['average_duration_seconds']}s",
            f"  Running processes: {stats['running_processes']}",
            f"  Total sessions: {stats['total_sessions']}",
            f"  Active sessions: {stats['active_sessions']}",
            f"  Strict mode: {stats['strict_mode']}",
        ]
        return {"success": True, "response": "\n".join(lines), "data": stats}

    def _handle_check(self, command: str) -> Dict[str, Any]:
        cmd_content = self._extract_content(command, [
            "check command ", "validate command ", "is safe ", "safety check ",
        ])
        if not cmd_content:
            return {"success": False, "response": "Please provide a command to check."}

        report = self._validator.get_safety_report(cmd_content)
        icon = {"safe": "[SAFE]", "caution": "[CAUTION]", "dangerous": "[DANGEROUS]", "blocked": "[BLOCKED]"}
        lines = [
            f"Safety check for: {cmd_content}",
            f"  {icon.get(report['safety_level'], '[?]')} {report['safety_level'].upper()}",
            f"  Reason: {report['reason']}",
            f"  Requires confirmation: {report['requires_confirmation']}",
            f"  Is blocked: {report['is_blocked']}",
        ]
        return {
            "success": True,
            "response": "\n".join(lines),
            "data": report,
        }

    def _handle_clear_history(self, command: str) -> Dict[str, Any]:
        days = self._extract_number(command, default=0)
        count = self._storage.clear_history(older_than_days=days)
        if days > 0:
            return {"success": True, "response": f"Cleared {count} commands older than {days} days."}
        return {"success": True, "response": f"Cleared {count} commands from history."}

    def _handle_set_timeout(self, command: str) -> Dict[str, Any]:
        timeout = self._extract_number(command, default=0)
        if timeout <= 0:
            return {"success": False, "response": "Please provide a timeout in seconds. Example: 'set timeout 60'"}

        self._executor._default_timeout = timeout
        return {"success": True, "response": f"Default timeout set to {timeout} seconds."}

    def _handle_strict_mode(self, command: str) -> Dict[str, Any]:
        if "on" in command.lower() or "enable" in command.lower():
            self._validator.strict_mode = True
            return {"success": True, "response": "Strict mode enabled."}
        elif "off" in command.lower() or "disable" in command.lower():
            self._validator.strict_mode = False
            return {"success": True, "response": "Strict mode disabled."}
        else:
            status = "enabled" if self._validator.strict_mode else "disabled"
            return {"success": True, "response": f"Strict mode is currently {status}. Use 'strict mode on/off' to change."}

    def _handle_force_run(self, command: str) -> Dict[str, Any]:
        cmd_content = self._extract_content(command, [
            "force run ", "force execute ", "run force ",
        ])
        if not cmd_content:
            return {"success": False, "response": "Please provide a command to force run."}

        timeout = self._extract_number(command, default=None)
        record = self._executor.execute(cmd_content, session=self._current_session, timeout=timeout, force=True)
        return {
            "success": record.status == CommandStatus.COMPLETED,
            "response": self._format_record(record),
            "data": record.to_dict(),
        }

    def _handle_pwd(self) -> Dict[str, Any]:
        directory = self._current_session.working_directory if self._current_session else os.getcwd()
        return {
            "success": True,
            "response": f"Current directory: {directory}",
        }

    def _get_default_session(self) -> TerminalSession:
        if not self._current_session:
            self._current_session = self._session_mgr.get_or_default()
        return self._current_session

    def _get_session(self, session_id: str) -> Optional[TerminalSession]:
        return self._session_mgr.get_session(session_id)

    @staticmethod
    def _matches(text: str, keywords: list) -> bool:
        return any(text.startswith(kw) or kw in text for kw in keywords)

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
                start = idx + len(prefix)
                return command[start:].strip().split("\n")[0].strip()
        return None

    @staticmethod
    def _extract_number(command: str, default: int = 0) -> int:
        match = re.search(r"\b(\d+)\b", command)
        return int(match.group(1)) if match else default

    @staticmethod
    def _extract_id(command: str) -> Optional[str]:
        match = re.search(r"\b([a-f0-9]{8})\b", command.lower())
        return match.group(1) if match else None

    @staticmethod
    def _extract_args(command: str, triggers: list) -> List[str]:
        cmd_lower = command.lower()
        for trigger in triggers:
            idx = cmd_lower.find(trigger)
            if idx != -1:
                args_str = command[idx + len(trigger):].strip()
                return [a.strip().strip('"').strip("'") for a in args_str.split() if a.strip()]
        return []

    @staticmethod
    def _format_record(record: CommandRecord) -> str:
        lines = [f"Command: {record.command}"]
        lines.append(f"Status: {record.status.value}")

        if record.status == CommandStatus.BLOCKED:
            lines.append(f"Blocked: {record.safety_reason}")
            return "\n".join(lines)

        if record.output:
            output = record.output[:3000]
            lines.append(f"\nOutput:\n{output}")
            if len(record.output) > 3000:
                lines.append(f"\n... [{len(record.output) - 3000} chars truncated]")

        if record.error:
            lines.append(f"\nError:\n{record.error[:500]}")

        if record.duration_seconds > 0:
            lines.append(f"\nDuration: {record.duration_seconds:.2f}s")
        if record.exit_code >= 0:
            lines.append(f"Exit code: {record.exit_code}")

        return "\n".join(lines)
