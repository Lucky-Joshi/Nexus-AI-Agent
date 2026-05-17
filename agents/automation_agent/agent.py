"""
Automation Agent for NEXUS.
Orchestrates ActionExecutor, WorkflowEngine, SafetySystem, and workflow templates.
Handles command parsing and delegates to the appropriate service.
"""

from typing import Any, Dict, Optional, List
from pathlib import Path
from core.base_agent import BaseAgent, AgentStatus
from core.logger import Logger
from core.config import Config
from .actions import Action, ActionExecutor
from .workflow_engine import WorkflowEngine, Workflow
from .safety import SafetySystem
from .templates import get_builtin_workflows


class AutomationAgent(BaseAgent):
    """
    Desktop automation agent for NEXUS.
    Thin orchestrator that delegates to specialized service classes.
    """

    def __init__(self):
        super().__init__("automation_agent", "Desktop automation, workflows, and productivity modes")
        self.logger = Logger().get_logger("AutomationAgent")

        config = Config()
        safety_delay = config.get("agents.automation_agent.safety_delay", 0.5)
        confirm_destructive = config.get("agents.automation_agent.confirm_destructive", True)

        self._safety_system = SafetySystem(
            safety_delay=safety_delay,
            confirm_destructive=confirm_destructive,
        )

        screenshots_dir = str(Path(__file__).parent.parent.parent / "data" / "screenshots")
        self._workflow_engine = WorkflowEngine(
            safety_system=self._safety_system,
            screenshots_dir=screenshots_dir,
        )

        self._register_builtin_workflows()

    def _register_builtin_workflows(self):
        """Register all built-in workflow templates."""
        for workflow in get_builtin_workflows():
            self._workflow_engine.register_workflow(workflow)
        self.logger.info(f"Registered {len(get_builtin_workflows())} built-in workflows")

    def execute(self, command: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Route command to the appropriate service handler."""
        self.status = AgentStatus.BUSY
        try:
            cmd = command.lower()

            if self._matches(cmd, ["screenshot", "screen capture", "capture screen"]):
                return self._handle_screenshot(command)

            elif self._matches(cmd, ["workflow", "preset", "sequence", "mode"]):
                if self._matches(cmd, ["save", "create", "new"]):
                    return self._handle_save_workflow(command)
                elif self._matches(cmd, ["list", "show", "all"]):
                    return self._handle_list_workflows()
                elif self._matches(cmd, ["stop", "cancel", "emergency"]):
                    return self._handle_stop(command)
                else:
                    return self._handle_run_workflow(command)

            elif self._matches(cmd, ["click", "mouse"]):
                return self._handle_click(command)

            elif self._matches(cmd, ["type", "keyboard", "key"]):
                if self._matches(cmd, ["press", "hotkey"]):
                    return self._handle_hotkey(command)
                return self._handle_type(command)

            elif self._matches(cmd, ["launch", "start", "open"]) and self._matches(cmd, ["and", "then", "sequence", "multiple"]):
                return self._handle_launch_sequence(command)

            elif self._matches(cmd, ["move", "position", "cursor"]):
                return self._handle_move_mouse(command)

            elif self._matches(cmd, ["stop", "emergency", "cancel"]):
                return self._handle_stop(command)

            else:
                return self._handle_launch_sequence(command)

        except Exception as e:
            self.logger.error(f"AutomationAgent error: {e}")
            return {
                "success": False,
                "response": f"Automation error: {str(e)}",
                "error": str(e),
            }
        finally:
            self.status = AgentStatus.IDLE

    def get_capabilities(self) -> list:
        return [
            "screenshot",
            "execute_workflow",
            "save_workflow",
            "list_workflows",
            "stop_workflow",
            "click",
            "type_text",
            "press_key",
            "hotkey",
            "move_mouse",
            "launch_sequence",
            "run_command",
        ]

    def _handle_screenshot(self, command: str) -> Dict[str, Any]:
        action = Action.screenshot()
        result = self._workflow_engine.executor.execute(action)

        if result.get("success"):
            return {
                "success": True,
                "response": f"Screenshot saved: {result.get('path', 'unknown')}",
                "data": result,
            }
        return {"success": False, "response": f"Screenshot failed: {result.get('error', 'unknown')}"}

    def _handle_run_workflow(self, command: str) -> Dict[str, Any]:
        workflow_name = command.lower()
        for prefix in [
            "run workflow ", "execute workflow ", "start workflow ",
            "run mode ", "start mode ", "activate ",
            "run ", "execute ", "start ",
            "workflow ", "preset ", "sequence ", "mode ",
        ]:
            if workflow_name.startswith(prefix):
                workflow_name = workflow_name[len(prefix):]
                break

        workflow_name = workflow_name.strip()
        if not workflow_name:
            return self._handle_list_workflows()

        workflow_name = workflow_name.replace(" ", "_").replace("-", "_")

        result = self._workflow_engine.execute(workflow_name)
        return result

    def _handle_save_workflow(self, command: str) -> Dict[str, Any]:
        if ":" not in command:
            return {"success": False, "response": "Usage: save workflow [name]: [step1], [step2], ..."}

        parts = command.split(":", 1)
        name = parts[0].replace("save workflow", "").replace("create workflow", "").strip().lower()
        steps_str = parts[1].strip()
        step_texts = [s.strip() for s in steps_str.split(",") if s.strip()]

        actions = []
        for step_text in step_texts:
            action = self._parse_step(step_text)
            if action:
                actions.append(action)

        if not actions:
            return {"success": False, "response": "No valid steps parsed."}

        workflow = Workflow(
            name=name,
            description=f"Custom workflow: {name}",
            steps=actions,
            mode="custom",
        )
        self._workflow_engine.register_workflow(workflow)
        self._workflow_engine.save_workflows()

        return {
            "success": True,
            "response": f"Workflow '{name}' saved with {len(actions)} steps.",
        }

    def _handle_list_workflows(self) -> Dict[str, Any]:
        workflows = self._workflow_engine.list_workflows()
        if not workflows:
            return {"success": True, "response": "No workflows available."}

        lines = ["Available workflows:"]
        for wf in workflows:
            tags = f" [{', '.join(wf['tags'])}]" if wf.get("tags") else ""
            lines.append(f"  {wf['name']}: {wf['steps']} steps{tags}")
            if wf.get("description"):
                lines.append(f"    {wf['description']}")

        return {
            "success": True,
            "response": "\n".join(lines),
            "data": workflows,
        }

    def _handle_stop(self, command: str) -> Dict[str, Any]:
        self._workflow_engine.stop("User requested stop")
        return {
            "success": True,
            "response": "Emergency stop triggered. Current workflow will halt.",
        }

    def _handle_click(self, command: str) -> Dict[str, Any]:
        cmd = command.lower()
        if "right" in cmd:
            action = Action.click(button="right")
        elif "double" in cmd:
            action = Action.click(clicks=2)
        else:
            action = Action.click()

        result = self._workflow_engine.executor.execute(action)
        return self._action_result(result)

    def _handle_type(self, command: str) -> Dict[str, Any]:
        text = command
        for prefix in ["type ", "type text ", "keyboard "]:
            if text.lower().startswith(prefix):
                text = text[len(prefix):]
                break

        text = text.strip().strip('"').strip("'")
        if not text:
            return {"success": False, "response": "Please provide text to type."}

        action = Action.type_text(text)
        result = self._workflow_engine.executor.execute(action)
        return self._action_result(result)

    def _handle_hotkey(self, command: str) -> Dict[str, Any]:
        keys = command.lower()
        for prefix in ["press ", "hotkey ", "press key "]:
            if keys.startswith(prefix):
                keys = keys[len(prefix):]
                break

        keys = [k.strip() for k in keys.replace("+", ",").split(",") if k.strip()]
        if not keys:
            return {"success": False, "response": "Please specify keys to press."}

        action = Action.hotkey(*keys)
        result = self._workflow_engine.executor.execute(action)
        return self._action_result(result)

    def _handle_move_mouse(self, command: str) -> Dict[str, Any]:
        import re
        coords = re.findall(r"(\d+)", command)
        if len(coords) >= 2:
            x, y = int(coords[0]), int(coords[1])
            action = Action.move_mouse(x, y)
            result = self._workflow_engine.executor.execute(action)
            return self._action_result(result)
        return {"success": False, "response": "Please specify coordinates. Example: 'move mouse to 100, 200'"}

    def _handle_launch_sequence(self, command: str) -> Dict[str, Any]:
        apps = []
        cmd = command.lower()

        app_map = {
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
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
        }

        for app_name, app_cmd in app_map.items():
            if app_name in cmd:
                apps.append((app_name, app_cmd))

        if not apps:
            return {"success": False, "response": "No applications recognized in sequence."}

        actions = []
        for name, cmd in apps:
            actions.append(Action.open_app(name, delay=1.5))

        result = self._workflow_engine.execute_custom(actions, name="launch_sequence")
        return result

    def _parse_step(self, step_text: str) -> Optional[Action]:
        """Parse a text step into an Action object."""
        text = step_text.lower().strip()

        if text.startswith(("open ", "launch ", "start ")):
            app = text.split(" ", 1)[1].strip() if " " in text else text
            return Action.open_app(app)
        elif text.startswith("type "):
            content = text[5:].strip().strip('"').strip("'")
            return Action.type_text(content)
        elif text.startswith("press "):
            key = text[6:].strip()
            return Action.press_key(key)
        elif text.startswith("screenshot"):
            return Action.screenshot()
        elif text.startswith(("wait ", "delay ")):
            import re
            match = re.search(r"(\d+)", text)
            seconds = int(match.group(1)) if match else 2
            return Action.wait(seconds)
        elif text.startswith("click"):
            return Action.click()
        elif text.startswith("move"):
            import re
            coords = re.findall(r"(\d+)", text)
            if len(coords) >= 2:
                return Action.move_mouse(int(coords[0]), int(coords[1]))

        return None

    def _action_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Format an action execution result."""
        if result.get("success"):
            return {
                "success": True,
                "response": result.get("response", "Action completed"),
                "data": result,
            }
        return {
            "success": False,
            "response": f"Action failed: {result.get('error', 'unknown')}",
        }

    @staticmethod
    def _matches(text: str, keywords: list) -> bool:
        """Check if any keyword exists in text."""
        return any(kw in text for kw in keywords)
