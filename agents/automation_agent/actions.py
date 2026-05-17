"""
Action executor for the Automation Agent.
Handles individual automation actions: keyboard, mouse, app launch, screenshots, etc.
"""

import os
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional
from core.logger import Logger


@dataclass
class Action:
    """Represents a single automation action."""
    type: str
    params: Dict[str, Any] = field(default_factory=dict)
    description: str = ""
    delay_after: float = 0.5

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "params": self.params,
            "description": self.description,
            "delay_after": self.delay_after,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Action":
        return cls(
            type=data["type"],
            params=data.get("params", {}),
            description=data.get("description", ""),
            delay_after=data.get("delay_after", 0.5),
        )

    @classmethod
    def open_app(cls, app: str, delay: float = 1.0) -> "Action":
        return cls(type="open_app", params={"app": app}, description=f"Open {app}", delay_after=delay)

    @classmethod
    def type_text(cls, text: str, interval: float = 0.05, delay: float = 0.5) -> "Action":
        return cls(type="type_text", params={"text": text, "interval": interval}, description=f"Type: {text[:30]}", delay_after=delay)

    @classmethod
    def press_key(cls, key: str, delay: float = 0.5) -> "Action":
        return cls(type="press_key", params={"key": key}, description=f"Press {key}", delay_after=delay)

    @classmethod
    def hotkey(cls, *keys: str, delay: float = 0.5) -> "Action":
        return cls(type="hotkey", params={"keys": list(keys)}, description=f"Hotkey: {'+'.join(keys)}", delay_after=delay)

    @classmethod
    def click(cls, x: int = None, y: int = None, button: str = "left", clicks: int = 1, delay: float = 0.5) -> "Action":
        return cls(type="click", params={"x": x, "y": y, "button": button, "clicks": clicks}, description=f"Click at ({x}, {y})", delay_after=delay)

    @classmethod
    def move_mouse(cls, x: int, y: int, delay: float = 0.5) -> "Action":
        return cls(type="move_mouse", params={"x": x, "y": y}, description=f"Move to ({x}, {y})", delay_after=delay)

    @classmethod
    def screenshot(cls, path: str = None, delay: float = 0.5) -> "Action":
        return cls(type="screenshot", params={"path": path}, description="Take screenshot", delay_after=delay)

    @classmethod
    def wait(cls, seconds: float = 2.0) -> "Action":
        return cls(type="wait", params={"seconds": seconds}, description=f"Wait {seconds}s", delay_after=0)

    @classmethod
    def run_command(cls, command: str, delay: float = 1.0) -> "Action":
        return cls(type="run_command", params={"command": command}, description=f"Run: {command[:50]}", delay_after=delay)


class ActionExecutor:
    """Executes individual automation actions."""

    def __init__(self, screenshots_dir: str = None):
        self.logger = Logger().get_logger("ActionExecutor")
        self._screenshots_dir = Path(screenshots_dir) if screenshots_dir else Path(__file__).parent.parent.parent / "data" / "screenshots"
        self._screenshots_dir.mkdir(parents=True, exist_ok=True)

    def execute(self, action: Action) -> Dict[str, Any]:
        """Execute a single action. Returns result dict."""
        handlers = {
            "open_app": self._execute_open_app,
            "type_text": self._execute_type_text,
            "press_key": self._execute_press_key,
            "hotkey": self._execute_hotkey,
            "click": self._execute_click,
            "move_mouse": self._execute_move_mouse,
            "screenshot": self._execute_screenshot,
            "wait": self._execute_wait,
            "run_command": self._execute_run_command,
        }

        handler = handlers.get(action.type)
        if not handler:
            return {"success": False, "error": f"Unknown action type: {action.type}"}

        try:
            result = handler(action.params)
            result["action_type"] = action.type
            result["description"] = action.description
            return result
        except ImportError as e:
            return {"success": False, "error": f"Missing dependency: {str(e)}", "action_type": action.type}
        except Exception as e:
            self.logger.error(f"Action failed ({action.type}): {e}")
            return {"success": False, "error": str(e), "action_type": action.type}

    def _execute_open_app(self, params: dict) -> Dict[str, Any]:
        app = params["app"]
        app_map = {
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "calc": "calc.exe",
            "settings": "ms-settings:",
            "explorer": "explorer.exe",
            "browser": "msedge.exe",
            "chrome": "chrome.exe",
            "edge": "msedge.exe",
            "firefox": "firefox.exe",
            "terminal": "wt.exe",
            "cmd": "cmd.exe",
            "powershell": "pwsh.exe",
            "vscode": "code.exe",
            "code": "code.exe",
            "task manager": "taskmgr.exe",
            "paint": "mspaint.exe",
        }

        app_cmd = app_map.get(app.lower(), app)
        subprocess.Popen(app_cmd, shell=True)
        self.logger.info(f"Opened application: {app_cmd}")
        return {"success": True, "response": f"Opened {app}"}

    def _execute_type_text(self, params: dict) -> Dict[str, Any]:
        import pyautogui
        text = params["text"]
        interval = params.get("interval", 0.05)
        pyautogui.typewrite(text, interval=interval)
        return {"success": True, "response": f"Typed: {text[:50]}"}

    def _execute_press_key(self, params: dict) -> Dict[str, Any]:
        import pyautogui
        key = params["key"]
        pyautogui.press(key)
        return {"success": True, "response": f"Pressed: {key}"}

    def _execute_hotkey(self, params: dict) -> Dict[str, Any]:
        import pyautogui
        keys = params["keys"]
        pyautogui.hotkey(*keys)
        return {"success": True, "response": f"Hotkey: {'+'.join(keys)}"}

    def _execute_click(self, params: dict) -> Dict[str, Any]:
        import pyautogui
        x = params.get("x")
        y = params.get("y")
        button = params.get("button", "left")
        clicks = params.get("clicks", 1)

        if x is not None and y is not None:
            pyautogui.click(x, y, clicks=clicks, button=button)
        else:
            pyautogui.click(clicks=clicks, button=button)

        return {"success": True, "response": f"Clicked at ({x}, {y})"}

    def _execute_move_mouse(self, params: dict) -> Dict[str, Any]:
        import pyautogui
        x = params["x"]
        y = params["y"]
        pyautogui.moveTo(x, y)
        return {"success": True, "response": f"Moved to ({x}, {y})"}

    def _execute_screenshot(self, params: dict) -> Dict[str, Any]:
        import pyautogui
        path = params.get("path")
        if not path:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            path = str(self._screenshots_dir / f"screenshot_{timestamp}.png")

        screenshot = pyautogui.screenshot()
        screenshot.save(path)
        return {"success": True, "response": f"Screenshot saved: {path}", "path": path}

    def _execute_wait(self, params: dict) -> Dict[str, Any]:
        seconds = params.get("seconds", 2.0)
        time.sleep(seconds)
        return {"success": True, "response": f"Waited {seconds}s"}

    def _execute_run_command(self, params: dict) -> Dict[str, Any]:
        command = params["command"]
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        return {
            "success": result.returncode == 0,
            "response": result.stdout.strip()[:500] if result.stdout else "Command executed",
            "returncode": result.returncode,
        }
