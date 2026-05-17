"""
Workflow Executor for the Workflow Mode Agent.
Executes mode actions with async support, error handling, and progress tracking.
"""

import asyncio
import os
import platform
import subprocess
import threading
import time
import webbrowser
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple

import psutil

from core.logger import Logger

from .models import (
    WorkflowMode, ModeAction, ModeState, ModeSession,
    ActionType, ActionStatus, ModeStatus, ModeCondition, ConditionType,
)
from .storage import WorkflowStorage


class WorkflowExecutor:
    """Executes workflow mode actions with sequencing, parallelism, and error handling."""

    def __init__(self, storage: WorkflowStorage):
        self.logger = Logger().get_logger("WorkflowExecutor")
        self._storage = storage
        self._running = False
        self._cancel_flag = False
        self._progress_callback: Optional[Callable] = None
        self._is_windows = platform.system() == "Windows"
        self._running_pids: Dict[str, int] = {}

    def set_progress_callback(self, callback: Callable):
        self._progress_callback = callback

    def execute_mode(self, mode: WorkflowMode) -> ModeState:
        """Execute all actions in a workflow mode."""
        state = ModeState(
            mode_id=mode.id,
            mode_name=mode.name,
            status=ModeStatus.ACTIVATING,
            started_at=datetime.now().isoformat(),
            total_actions=len(mode.actions),
        )
        self._storage.save_mode_state(state)
        self._running = True
        self._cancel_flag = False

        self.logger.info(f"Executing mode: {mode.name} ({len(mode.actions)} actions)")

        actions = sorted(mode.actions, key=lambda a: a.order)
        groups = self._group_actions(actions)

        for group_name, group_actions in groups.items():
            if self._cancel_flag:
                state.status = ModeStatus.CANCELLED
                state.error = "Mode activation cancelled by user"
                self._storage.save_mode_state(state)
                return state

            if group_name:
                self.logger.info(f"Executing action group: {group_name}")

            if group_actions and group_actions[0].parallel:
                self._execute_parallel(group_actions, state)
            else:
                for action in group_actions:
                    if self._cancel_flag:
                        state.status = ModeStatus.CANCELLED
                        state.error = "Mode activation cancelled by user"
                        self._storage.save_mode_state(state)
                        return state

                    self._execute_action(action, state)

        if not self._cancel_flag:
            state.status = ModeStatus.ACTIVE
            state.activated_at = datetime.now().isoformat()
            state.progress = 100.0

        self._storage.save_mode_state(state)
        self._running = False

        session = ModeSession(
            mode_id=mode.id,
            mode_name=mode.name,
            started_at=state.started_at,
            ended_at=datetime.now().isoformat() if state.status != ModeStatus.ACTIVE else "",
            status=state.status.value,
            actions_completed=state.completed_actions,
            actions_failed=state.failed_actions,
        )
        if session.ended_at:
            try:
                start = datetime.fromisoformat(session.started_at)
                end = datetime.fromisoformat(session.ended_at)
                session.duration_seconds = (end - start).total_seconds()
            except Exception:
                pass
        self._storage.save_session(session)

        return state

    def deactivate_mode(self, mode: WorkflowMode, state: ModeState) -> ModeState:
        """Deactivate a mode: close launched apps, restore settings."""
        state.status = ModeStatus.DEACTIVATING
        self._storage.save_mode_state(state)

        for app in reversed(state.launched_apps):
            self._close_app(app)

        self.logger.info(f"Mode deactivated: {mode.name}")
        state.status = ModeStatus.IDLE
        state.progress = 0.0
        self._storage.save_mode_state(state)
        return state

    def cancel(self):
        """Cancel the current mode activation."""
        self._cancel_flag = True

    @property
    def is_running(self) -> bool:
        return self._running

    def _group_actions(self, actions: List[ModeAction]) -> Dict[str, List[ModeAction]]:
        groups: Dict[str, List[ModeAction]] = {}
        for action in actions:
            group = action.group or f"action_{action.order}"
            if group not in groups:
                groups[group] = []
            groups[group].append(action)
        return groups

    def _execute_action(self, action: ModeAction, state: ModeState):
        """Execute a single action with condition checking and retry logic."""
        if action.condition and not self._check_condition(action.condition):
            action.status = ActionStatus.SKIPPED
            state.skipped_actions += 1
            self._update_progress(state)
            self._log_action(action, state)
            return

        action.status = ActionStatus.RUNNING
        action.started_at = datetime.now().isoformat()
        self._update_progress(state)

        for attempt in range(action.max_retries + 1):
            action.retry_count = attempt
            try:
                success = self._run_action(action)
                if success:
                    action.status = ActionStatus.COMPLETED
                    action.completed_at = datetime.now().isoformat()
                    state.completed_actions += 1

                    if action.action_type == ActionType.LAUNCH_APP:
                        state.launched_apps.append(action.target)
                    elif action.action_type == ActionType.ACTIVATE_AGENT:
                        state.activated_agents.append(action.target)

                    self.logger.info(f"Action completed: {action.name or action.action_type.value}")
                    break
                else:
                    if attempt < action.max_retries:
                        time.sleep(1)
                        continue
                    action.status = ActionStatus.FAILED
                    action.error = "Action returned failure"
                    state.failed_actions += 1
                    self.logger.warning(f"Action failed: {action.name or action.action_type.value}")

            except Exception as e:
                if attempt < action.max_retries:
                    time.sleep(1)
                    continue
                action.status = ActionStatus.FAILED
                action.error = str(e)
                state.failed_actions += 1
                self.logger.error(f"Action error: {action.name or action.action_type.value}: {e}")

        if action.status == ActionStatus.FAILED and action.on_failure == "abort":
            state.status = ModeStatus.ERROR
            state.error = f"Action failed: {action.name or action.action_type.value}"

        self._update_progress(state)
        self._log_action(action, state)

    def _execute_parallel(self, actions: List[ModeAction], state: ModeState):
        """Execute multiple actions in parallel."""
        threads = []
        for action in actions:
            t = threading.Thread(target=self._execute_action, args=(action, state), daemon=True)
            threads.append(t)
            t.start()

        for t in threads:
            t.join(timeout=60)

    def _run_action(self, action: ModeAction) -> bool:
        """Run the actual action based on its type."""
        if action.action_type == ActionType.LAUNCH_APP:
            return self._launch_app(action)
        elif action.action_type == ActionType.CLOSE_APP:
            return self._close_app(action.target)
        elif action.action_type == ActionType.OPEN_URL:
            return self._open_url(action.target)
        elif action.action_type == ActionType.OPEN_FILE:
            return self._open_file(action.target)
        elif action.action_type == ActionType.OPEN_FOLDER:
            return self._open_folder(action.target)
        elif action.action_type == ActionType.RUN_COMMAND:
            return self._run_command(action)
        elif action.action_type == ActionType.ACTIVATE_AGENT:
            return True
        elif action.action_type == ActionType.DEACTIVATE_AGENT:
            return True
        elif action.action_type == ActionType.SET_NOTIFICATIONS:
            return True
        elif action.action_type == ActionType.SET_FOCUS_MODE:
            return True
        elif action.action_type == ActionType.START_TIMER:
            return True
        elif action.action_type == ActionType.CREATE_FILE:
            return self._create_file(action)
        elif action.action_type == ActionType.CREATE_FOLDER:
            return self._create_folder(action)
        elif action.action_type == ActionType.WAIT:
            time.sleep(action.params.get("duration", 1))
            return True
        elif action.action_type == ActionType.CUSTOM:
            return True
        return False

    def _launch_app(self, action: ModeAction) -> bool:
        target = action.target
        params = action.params or {}

        try:
            if target.startswith(("http://", "https://")):
                webbrowser.open(target)
                return True

            if self._is_windows:
                if ":" in target and not target.startswith(("C:", "D:", "E:")):
                    os.startfile(target)
                    return True

                if target.endswith((".exe", ".lnk")) or "\\" in target or "/" in target:
                    if os.path.exists(target):
                        os.startfile(target)
                        return True

                app_map = {
                    "vscode": "code.exe", "visual studio code": "code.exe",
                    "notepad": "notepad.exe", "terminal": "wt.exe",
                    "chrome": "chrome.exe", "edge": "msedge.exe",
                    "firefox": "firefox.exe", "explorer": "explorer.exe",
                    "github desktop": "GitHubDesktop.exe",
                    "figma": "Figma.exe", "photoshop": "Photoshop.exe",
                    "zoom": "Zoom.exe", "teams": "teams.exe",
                    "slack": "slack.exe", "discord": "Discord.exe",
                    "notion": "Notion.exe", "obsidian": "Obsidian.exe",
                    "spotify": "spotify.exe", "calendar": "outlookcal:",
                    "settings": "ms-settings:", "calculator": "calc.exe",
                }

                app_cmd = app_map.get(target.lower(), target)
                os.startfile(app_cmd)
                return True
            else:
                subprocess.Popen(["open" if platform.system() == "Darwin" else "xdg-open", target])
                return True

        except Exception as e:
            self.logger.warning(f"App launch failed: {target}: {e}")
            return False

    def _close_app(self, app_name: str) -> bool:
        try:
            for proc in psutil.process_iter(["pid", "name"]):
                try:
                    if app_name.lower() in proc.info["name"].lower():
                        proc.terminate()
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            return False
        except Exception as e:
            self.logger.warning(f"Close app failed: {app_name}: {e}")
            return False

    def _open_url(self, url: str) -> bool:
        try:
            webbrowser.open(url)
            return True
        except Exception as e:
            self.logger.warning(f"Open URL failed: {url}: {e}")
            return False

    def _open_file(self, path: str) -> bool:
        try:
            if os.path.exists(path):
                if self._is_windows:
                    os.startfile(path)
                else:
                    subprocess.Popen(["open" if platform.system() == "Darwin" else "xdg-open", path])
                return True
            return False
        except Exception as e:
            self.logger.warning(f"Open file failed: {path}: {e}")
            return False

    def _open_folder(self, path: str) -> bool:
        try:
            if os.path.exists(path):
                if self._is_windows:
                    os.startfile(path)
                else:
                    subprocess.Popen(["open" if platform.system() == "Darwin" else "xdg-open", path])
                return True
            return False
        except Exception as e:
            self.logger.warning(f"Open folder failed: {path}: {e}")
            return False

    def _run_command(self, action: ModeAction) -> bool:
        try:
            timeout = action.timeout or 30
            result = subprocess.run(
                action.target,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            self.logger.warning(f"Command timed out: {action.target}")
            return False
        except Exception as e:
            self.logger.warning(f"Command failed: {action.target}: {e}")
            return False

    def _create_file(self, action: ModeAction) -> bool:
        try:
            path = action.target
            content = action.params.get("content", "")
            os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
            with open(path, "w") as f:
                f.write(content)
            return True
        except Exception as e:
            self.logger.warning(f"Create file failed: {action.target}: {e}")
            return False

    def _create_folder(self, action: ModeAction) -> bool:
        try:
            os.makedirs(action.target, exist_ok=True)
            return True
        except Exception as e:
            self.logger.warning(f"Create folder failed: {action.target}: {e}")
            return False

    def _check_condition(self, condition: ModeCondition) -> bool:
        """Check if a condition is met."""
        try:
            if condition.type == ConditionType.APP_RUNNING:
                return self._is_app_running(condition.value)
            elif condition.type == ConditionType.APP_NOT_RUNNING:
                return not self._is_app_running(condition.value)
            elif condition.type == ConditionType.SYSTEM_MEMORY_HIGH:
                return psutil.virtual_memory().percent > condition.threshold
            elif condition.type == ConditionType.SYSTEM_CPU_HIGH:
                return psutil.cpu_percent(interval=0.5) > condition.threshold
            elif condition.type == ConditionType.FOCUS_MODE_ACTIVE:
                return False
            elif condition.type == ConditionType.TIME_OF_DAY:
                hour = datetime.now().hour
                if "-" in condition.value:
                    start, end = condition.value.split("-")
                    return int(start) <= hour <= int(end)
            elif condition.type == ConditionType.CUSTOM:
                return True
            return True
        except Exception as e:
            self.logger.warning(f"Condition check failed: {e}")
            return not condition.invert

    def _is_app_running(self, app_name: str) -> bool:
        for proc in psutil.process_iter(["name"]):
            try:
                if app_name.lower() in proc.info["name"].lower():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False

    def _update_progress(self, state: ModeState):
        if state.total_actions > 0:
            state.progress = (state.completed_actions + state.failed_actions + state.skipped_actions) / state.total_actions * 100
        if self._progress_callback:
            self._progress_callback(state.progress, state.completed_actions, state.total_actions)

    def _log_action(self, action: ModeAction, state: ModeState):
        state.action_states.append({
            "action": action.name or action.action_type.value,
            "status": action.status.value,
            "error": action.error,
            "timestamp": datetime.now().isoformat(),
        })
