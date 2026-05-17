"""
Business logic services for the Terminal Agent.
Handles command execution, session management, output streaming, and script running.
"""

import os
import platform
import subprocess
import threading
import time
from datetime import datetime
from queue import Queue
from typing import Any, Callable, Dict, Generator, List, Optional

from core.logger import Logger
from core.config import Config

from .models import TerminalSession, CommandRecord, CommandStatus, SessionStatus
from .storage import TerminalStorage
from .validator import CommandValidator, SafetyLevel


class ExecutionEngine:
    """Executes terminal commands with safety validation and output capture."""

    def __init__(self, validator: CommandValidator, storage: TerminalStorage,
                 default_timeout: int = 30, max_output_size: int = 50000):
        self.logger = Logger().get_logger("ExecutionEngine")
        self._validator = validator
        self._storage = storage
        self._default_timeout = default_timeout
        self._max_output_size = max_output_size
        self._is_windows = platform.system() == "Windows"
        self._running_processes: Dict[str, subprocess.Popen] = {}
        self._lock = threading.Lock()

    def execute(self, command: str, session: Optional[TerminalSession] = None,
                timeout: Optional[int] = None, stream_callback: Optional[Callable] = None,
                force: bool = False) -> CommandRecord:
        """
        Execute a command with full safety validation.
        Returns CommandRecord with output and status.
        """
        working_dir = session.working_directory if session else os.getcwd()
        record = CommandRecord(
            command=command,
            session_id=session.id if session else "",
            working_directory=working_dir,
            stream_mode=stream_callback is not None,
        )

        safety_level, reason = self._validator.validate(command)
        if safety_level == SafetyLevel.BLOCKED and not force:
            record.mark_blocked(reason)
            self._storage.save_command(record)
            self.logger.warning(f"Command blocked: {command} - {reason}")
            return record

        record.is_safe = safety_level != SafetyLevel.DANGEROUS
        record.safety_reason = reason

        try:
            record.mark_running()
            self._storage.save_command(record)

            env = os.environ.copy()
            if session and session.environment:
                env.update(session.environment)

            shell = self._is_windows
            proc = subprocess.Popen(
                command,
                shell=shell,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                cwd=working_dir if os.path.isdir(working_dir) else None,
                env=env,
                text=True,
                errors="replace",
            )

            with self._lock:
                self._running_processes[record.id] = proc

            actual_timeout = timeout or self._default_timeout

            if stream_callback:
                output, error = self._stream_output(proc, stream_callback, actual_timeout)
            else:
                try:
                    stdout, stderr = proc.communicate(timeout=actual_timeout)
                    output = self._truncate_output(stdout or "")
                    error = self._truncate_output(stderr or "")
                except subprocess.TimeoutExpired:
                    proc.kill()
                    stdout, stderr = proc.communicate()
                    record.mark_timeout()
                    record.output = self._truncate_output(stdout or "")
                    record.error = self._truncate_output(stderr or "")
                    self._storage.save_command(record)
                    self.logger.warning(f"Command timed out: {command}")
                    return record

            with self._lock:
                self._running_processes.pop(record.id, None)

            exit_code = proc.returncode or 0
            if exit_code == 0:
                record.mark_completed(exit_code, output)
            else:
                record.mark_failed(error or f"Exit code: {exit_code}", exit_code)
                if output:
                    record.output = output

        except FileNotFoundError:
            record.mark_failed(f"Command not found: {command.split()[0]}")
        except PermissionError:
            record.mark_failed("Permission denied")
        except Exception as e:
            record.mark_failed(str(e))

        self._storage.save_command(record)
        if session:
            session.add_to_history(command)
            session.touch()
        return record

    def kill_process(self, record_id: str) -> bool:
        """Kill a running process by record ID."""
        with self._lock:
            proc = self._running_processes.pop(record_id, None)
        if proc:
            try:
                proc.kill()
                proc.wait(timeout=5)
                return True
            except Exception:
                return False
        return False

    def kill_all(self) -> int:
        """Kill all running processes. Returns count of killed processes."""
        count = 0
        with self._lock:
            procs = list(self._running_processes.items())
            self._running_processes.clear()
        for record_id, proc in procs:
            try:
                proc.kill()
                proc.wait(timeout=5)
                count += 1
            except Exception:
                pass
        return count

    @property
    def running_count(self) -> int:
        return len(self._running_processes)

    @staticmethod
    def _stream_output(proc: subprocess.Popen, callback: Callable, timeout: int) -> tuple:
        output_lines = []
        error_lines = []

        def read_stdout():
            for line in iter(proc.stdout.readline, ""):
                output_lines.append(line)
                callback("stdout", line)

        def read_stderr():
            for line in iter(proc.stderr.readline, ""):
                error_lines.append(line)
                callback("stderr", line)

        t_out = threading.Thread(target=read_stdout, daemon=True)
        t_err = threading.Thread(target=read_stderr, daemon=True)
        t_out.start()
        t_err.start()

        t_out.join(timeout=timeout)
        t_err.join(timeout=timeout)

        if t_out.is_alive() or t_err.is_alive():
            proc.kill()

        return "".join(output_lines), "".join(error_lines)

    @staticmethod
    def _truncate_output(text: str, max_size: int = 50000) -> str:
        if len(text) > max_size:
            return text[:max_size] + f"\n... [output truncated, {len(text) - max_size} chars omitted]"
        return text


class SessionManager:
    """Manages multiple terminal sessions with state persistence."""

    def __init__(self, storage: TerminalStorage):
        self.logger = Logger().get_logger("SessionManager")
        self._storage = storage
        self._sessions: Dict[str, TerminalSession] = {}
        self._load_sessions()

    def _load_sessions(self):
        sessions = self._storage.get_all_sessions(limit=100)
        for s in sessions:
            if s.status == SessionStatus.ACTIVE:
                s.status = SessionStatus.IDLE
            self._sessions[s.id] = s
        self.logger.info(f"Loaded {len(self._sessions)} sessions")

    def create_session(self, name: str = "", working_directory: str = "",
                       environment: Optional[Dict[str, str]] = None) -> TerminalSession:
        if not name:
            name = f"Session {len(self._sessions) + 1}"
        if not working_directory:
            working_directory = os.getcwd()

        session = TerminalSession(
            name=name,
            working_directory=working_directory,
            status=SessionStatus.ACTIVE,
            environment=environment or {},
        )
        self._sessions[session.id] = session
        self._storage.save_session(session)
        self.logger.info(f"Session created: {session.id} - {name}")
        return session

    def get_session(self, session_id: str) -> Optional[TerminalSession]:
        return self._sessions.get(session_id)

    def get_or_default(self) -> TerminalSession:
        """Get the most recent active session or create a new one."""
        for s in self._sessions.values():
            if s.status == SessionStatus.ACTIVE:
                return s
        return self.create_session()

    def get_all_sessions(self, limit: int = 20) -> List[TerminalSession]:
        return list(self._sessions.values())[:limit]

    def close_session(self, session_id: str) -> bool:
        session = self._sessions.get(session_id)
        if not session:
            return False
        session.status = SessionStatus.CLOSED
        self._storage.save_session(session)
        del self._sessions[session_id]
        self.logger.info(f"Session closed: {session_id}")
        return True

    def set_working_directory(self, session_id: str, directory: str) -> bool:
        session = self._sessions.get(session_id)
        if not session:
            return False
        if os.path.isdir(directory):
            session.working_directory = directory
            session.touch()
            self._storage.save_session(session)
            return True
        return False

    def set_environment(self, session_id: str, key: str, value: str) -> bool:
        session = self._sessions.get(session_id)
        if not session:
            return False
        session.environment[key] = value
        session.touch()
        self._storage.save_session(session)
        return True

    def delete_session(self, session_id: str) -> bool:
        self._sessions.pop(session_id, None)
        return self._storage.delete_session(session_id)

    def get_stats(self) -> Dict[str, Any]:
        active = sum(1 for s in self._sessions.values() if s.status == SessionStatus.ACTIVE)
        return {
            "total_sessions": len(self._sessions),
            "active_sessions": active,
        }


class OutputStreamer:
    """Manages real-time output streaming for commands."""

    def __init__(self, max_buffer: int = 1000):
        self.logger = Logger().get_logger("OutputStreamer")
        self._max_buffer = max_buffer
        self._streams: Dict[str, Queue] = {}
        self._active: Dict[str, bool] = {}
        self._lock = threading.Lock()

    def create_stream(self, stream_id: str):
        with self._lock:
            self._streams[stream_id] = Queue(maxsize=self._max_buffer)
            self._active[stream_id] = True

    def push(self, stream_id: str, stream_type: str, data: str):
        with self._lock:
            queue = self._streams.get(stream_id)
        if queue and self._active.get(stream_id, False):
            try:
                queue.put_nowait({"type": stream_type, "data": data, "timestamp": datetime.now().isoformat()})
            except Exception:
                pass

    def get_output(self, stream_id: str, timeout: float = 1.0) -> Optional[Dict]:
        with self._lock:
            queue = self._streams.get(stream_id)
        if queue:
            try:
                return queue.get(timeout=timeout)
            except Exception:
                return None
        return None

    def get_all_pending(self, stream_id: str) -> List[Dict]:
        items = []
        with self._lock:
            queue = self._streams.get(stream_id)
        if queue:
            while not queue.empty():
                try:
                    items.append(queue.get_nowait())
                except Exception:
                    break
        return items

    def close_stream(self, stream_id: str):
        with self._lock:
            self._active[stream_id] = False
            self._streams.pop(stream_id, None)

    def is_active(self, stream_id: str) -> bool:
        return self._active.get(stream_id, False)

    def stream_generator(self, stream_id: str, timeout: float = 0.5) -> Generator[Dict, None, None]:
        """Generator that yields stream items until the stream is closed."""
        while self.is_active(stream_id):
            item = self.get_output(stream_id, timeout)
            if item:
                yield item
            else:
                time.sleep(0.05)


class ScriptRunner:
    """Executes script files with validation and output capture."""

    def __init__(self, validator: CommandValidator, storage: TerminalStorage,
                 default_timeout: int = 120):
        self.logger = Logger().get_logger("ScriptRunner")
        self._validator = validator
        self._storage = storage
        self._default_timeout = default_timeout
        self._is_windows = platform.system() == "Windows"
        self._allowed_extensions = {
            ".py", ".bat", ".cmd", ".ps1", ".sh", ".bash",
            ".js", ".ts", ".rb", ".pl", ".php",
            ".exe", ".com",
        }

    def run_script(self, script_path: str, args: Optional[List[str]] = None,
                   working_directory: Optional[str] = None,
                   timeout: Optional[int] = None,
                   session: Optional[TerminalSession] = None) -> CommandRecord:
        """Run a script file with full validation."""
        if not os.path.isfile(script_path):
            record = CommandRecord(
                command=f"script: {script_path}",
                session_id=session.id if session else "",
            )
            record.mark_failed(f"Script not found: {script_path}")
            self._storage.save_command(record)
            return record

        ext = os.path.splitext(script_path)[1].lower()
        if ext not in self._allowed_extensions:
            record = CommandRecord(
                command=f"script: {script_path}",
                session_id=session.id if session else "",
            )
            record.mark_blocked(f"Unsupported script extension: {ext}")
            self._storage.save_command(record)
            return record

        command = self._build_script_command(script_path, args)
        working_dir = working_directory or (session.working_directory if session else os.getcwd())

        record = CommandRecord(
            command=command,
            session_id=session.id if session else "",
            working_directory=working_dir,
        )

        safety_level, reason = self._validator.validate(command)
        if safety_level == SafetyLevel.BLOCKED:
            record.mark_blocked(reason)
            self._storage.save_command(record)
            return record

        try:
            record.mark_running()
            self._storage.save_command(record)

            env = os.environ.copy()
            if session and session.environment:
                env.update(session.environment)

            actual_timeout = timeout or self._default_timeout
            proc = subprocess.Popen(
                command,
                shell=self._is_windows,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                cwd=working_dir if os.path.isdir(working_dir) else None,
                env=env,
                text=True,
                errors="replace",
            )

            try:
                stdout, stderr = proc.communicate(timeout=actual_timeout)
                output = stdout or ""
                error = stderr or ""
                exit_code = proc.returncode or 0

                if exit_code == 0:
                    record.mark_completed(exit_code, output)
                else:
                    record.mark_failed(error or f"Exit code: {exit_code}", exit_code)
                    if output:
                        record.output = output

            except subprocess.TimeoutExpired:
                proc.kill()
                stdout, stderr = proc.communicate()
                record.mark_timeout()
                record.output = stdout or ""
                record.error = stderr or ""

        except Exception as e:
            record.mark_failed(str(e))

        self._storage.save_command(record)
        if session:
            session.add_to_history(command)
            session.touch()
        return record

    def run_python(self, code: str, working_directory: Optional[str] = None,
                   timeout: Optional[int] = None,
                   session: Optional[TerminalSession] = None) -> CommandRecord:
        """Execute Python code directly via subprocess."""
        command = f'python -c "{code}"'
        record = CommandRecord(
            command=command,
            session_id=session.id if session else "",
            working_directory=working_directory or os.getcwd(),
        )

        try:
            record.mark_running()
            self._storage.save_command(record)

            env = os.environ.copy()
            if session and session.environment:
                env.update(session.environment)

            actual_timeout = timeout or 30
            proc = subprocess.Popen(
                ["python", "-c", code],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                cwd=working_directory if working_directory and os.path.isdir(working_directory) else None,
                env=env,
                text=True,
                errors="replace",
            )

            try:
                stdout, stderr = proc.communicate(timeout=actual_timeout)
                exit_code = proc.returncode or 0
                if exit_code == 0:
                    record.mark_completed(exit_code, stdout or "")
                else:
                    record.mark_failed(stderr or f"Exit code: {exit_code}", exit_code)
                    if stdout:
                        record.output = stdout
            except subprocess.TimeoutExpired:
                proc.kill()
                stdout, stderr = proc.communicate()
                record.mark_timeout()
                record.output = stdout or ""
                record.error = stderr or ""

        except Exception as e:
            record.mark_failed(str(e))

        self._storage.save_command(record)
        return record

    def _build_script_command(self, script_path: str, args: Optional[List[str]]) -> str:
        cmd = f'"{script_path}"'
        if args:
            cmd += " " + " ".join(f'"{a}"' for a in args)
        return cmd
