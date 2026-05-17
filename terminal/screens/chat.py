"""
NEXUS - Chat Screen
Main command interface with streaming AI responses, slash commands,
and interactive terminal experience.
"""

import asyncio
from textual.screen import Screen
from textual.widgets import Static, Input, RichLog
from textual.containers import Container, Vertical, Horizontal
from textual.app import ComposeResult
from textual.message import Message
from rich.text import Text
from rich.panel import Panel
from rich.console import Group
from rich.markdown import Markdown
from datetime import datetime

from terminal.widgets import NexusHeader, NexusStatusBar, NexusMessage
from terminal.commands import CommandRegistry
from terminal.streaming import StreamingResponse, TypingAnimation


class ChatScreen(Screen):
    """Main chat/command interface with streaming responses."""

    CSS = """
    ChatScreen {
        background: #0A0E17;
    }

    #chat-layout {
        layout: horizontal;
        width: 100%;
        height: 1fr;
    }

    #chat-main {
        width: 1fr;
        height: 100%;
    }

    #chat-log {
        width: 100%;
        height: 1fr;
        background: #0A0E17;
        padding: 0 1;
    }

    #chat-input-container {
        dock: bottom;
        height: 3;
        background: #111827;
        border-top: solid #00D4FF;
        padding: 0 1;
    }

    #chat-input {
        width: 100%;
        background: #0A0E17;
        border: round #00D4FF;
        color: #E8E8E8;
    }

    #chat-input:focus {
        border: round #7B61FF;
    }

    #status-bar {
        dock: bottom;
        height: 1;
        background: #111827;
        border-top: solid #00D4FF;
    }

    #sidebar-panel {
        width: 35;
        background: #111827;
        border-left: solid #00D4FF;
        padding: 0 1;
    }
    """

    def __init__(self, manager, initial_command: str = ""):
        super().__init__()
        self.manager = manager
        self.initial_command = initial_command
        self._command_registry = CommandRegistry()
        self._streaming = StreamingResponse()
        self._typing = TypingAnimation()
        self._message_history = []
        self._setup_commands()

    def _setup_commands(self):
        """Register all slash commands."""
        reg = self._command_registry

        reg.register("help", "Show all commands", self._cmd_help, category="general",
                     autocomplete=["general", "agents", "workflows", "system"])

        reg.register("status", "Show agent status", self._cmd_status, category="system")

        reg.register("agents", "List all agents", self._cmd_agents, category="system")

        reg.register("tasks", "Show active tasks", self._cmd_tasks, category="system")

        reg.register("clear", "Clear chat", self._cmd_clear, category="general")

        reg.register("history", "Show command history", self._cmd_history, category="general")

        reg.register("modes", "List workflow modes", self._cmd_modes, category="workflows")

        reg.register("model", "Show/change LLM model", self._cmd_model, category="system",
                     requires_args=True, arg_description="<model_name>")

        reg.register("back", "Return to dashboard", self._cmd_back, category="general")

    def compose(self) -> ComposeResult:
        yield Static("", id="status-bar")
        yield Container(
            RichLog(id="chat-log", highlight=True, markup=True),
            Container(
                Input(placeholder="Type a command or ask anything...", id="chat-input"),
                id="chat-input-container",
            ),
            id="chat-main",
        )
        yield Static("", id="sidebar-panel")
        yield Static("", id="header")

    def on_mount(self) -> None:
        self._update_header()
        self._update_sidebar()
        self._update_status()

        chat_log = self.query_one("#chat-log", RichLog)
        chat_log.write("")

        if self.initial_command:
            self.query_one("#chat-input", Input).value = self.initial_command
            self._process_command(self.initial_command)
            self.query_one("#chat-input", Input).value = ""

        self.query_one("#chat-input", Input).focus()

    def _update_header(self):
        session = self.manager.session_id if self.manager else "unknown"
        agents = self.manager.get_agent_status() if self.manager else {}
        total = len(agents)
        header = NexusHeader()
        header.session_id = session
        header.agent_count = total
        self.query_one("#header", Static).update(header.render())

    def _update_sidebar(self):
        agents = self.manager.get_agent_status() if self.manager else {}
        lines = [Text(" AGENTS", style="bold #00D4FF"), Text("")]

        for name, info in sorted(agents.items()):
            status = info.get("status", "idle")
            if status == "idle":
                icon = Text("● ", style="#00E676")
            elif status == "busy":
                icon = Text("◉ ", style="#FFB800")
            elif status == "error":
                icon = Text("✖ ", style="#FF4757")
            else:
                icon = Text("○ ", style="#555555")

            display_name = name.replace("_agent", "").replace("_", " ").title()
            lines.append(icon + Text(display_name, style="#E8E8E8"))

        lines.append(Text(""))
        lines.append(Text(" COMMANDS", style="bold #00D4FF"))
        for cmd in self._command_registry.get_all_commands():
            lines.append(Text(f"  /{cmd.name}", style="dim #7B61FF"))

        content = Panel(Group(*lines), border_style="#00D4FF", title="NEXUS")
        self.query_one("#sidebar-panel", Static).update(content)

    def _update_status(self):
        agents = self.manager.get_agent_status() if self.manager else {}
        idle = sum(1 for s in agents.values() if s.get("status") == "idle")
        total = len(agents)
        now = datetime.now().strftime("%H:%M:%S")
        status_text = Text(f"◆ NEXUS | {idle}/{total} agents | Session: {self.manager.session_id if self.manager else 'N/A'} | {now}", style="#E8E8E8")
        self.query_one("#status-bar", Static).update(Panel(status_text, style="on #111827", border_style="#00D4FF"))

    def on_input_submitted(self, event: Input.Submitted) -> None:
        command = event.value.strip()
        if not command:
            return

        self.query_one("#chat-input", Input).value = ""

        if command.lower() in ("exit", "quit", "q"):
            self.app.exit()
            return

        self._process_command(command)

    def _process_command(self, command: str) -> None:
        """Process a user command."""
        chat_log = self.query_one("#chat-log", RichLog)

        self._message_history.append({"role": "user", "content": command, "time": datetime.now()})

        user_msg = NexusMessage()
        user_msg.role = "user"
        user_msg.content = command
        user_msg.timestamp = datetime.now().strftime("%H:%M:%S")
        chat_log.write(user_msg)

        if command.startswith("/"):
            result = self._command_registry.execute(command, {"manager": self.manager})
            if result:
                self._display_response(result.get("response", ""), agent="system")
            else:
                self._dispatch_to_manager(command)
        else:
            self._dispatch_to_manager(command)

        self._update_sidebar()
        self._update_status()

    def _dispatch_to_manager(self, command: str):
        """Dispatch command to AI Manager."""
        try:
            result = self.manager.process_command(command)
            agent = result.get("agent", "NEXUS")
            response = result.get("response", "No response")
            self._display_response(response, agent=agent)

            self._message_history.append({"role": "assistant", "content": response, "agent": agent, "time": datetime.now()})
        except Exception as e:
            self._display_response(f"Error: {str(e)}", agent="system")

    def _display_response(self, response: str, agent: str = "NEXUS"):
        """Display a response in the chat log."""
        chat_log = self.query_one("#chat-log", RichLog)

        msg = NexusMessage()
        msg.role = "assistant"
        msg.content = response
        msg.agent = agent.replace("_agent", "").replace("_", " ").title()
        msg.timestamp = datetime.now().strftime("%H:%M:%S")
        chat_log.write(msg)

    def _cmd_help(self, args: str, context: dict) -> dict:
        if args:
            return {"success": True, "response": self._command_registry.get_help(args)}
        return {"success": True, "response": self._command_registry.get_help()}

    def _cmd_status(self, args: str, context: dict) -> dict:
        manager = context.get("manager")
        if not manager:
            return {"success": False, "response": "Manager not available"}
        status = manager.get_agent_status()
        lines = ["Agent Status:\n"]
        for name, info in sorted(status.items()):
            status_icon = {"idle": "●", "busy": "◉", "error": "✖", "offline": "○"}.get(info["status"], "○")
            display_name = name.replace("_agent", "").replace("_", " ").title()
            lines.append(f"  {status_icon} {display_name}: {info['status']}")
        return {"success": True, "response": "\n".join(lines)}

    def _cmd_agents(self, args: str, context: dict) -> dict:
        manager = context.get("manager")
        if not manager:
            return {"success": False, "response": "Manager not available"}
        status = manager.get_agent_status()
        lines = ["Registered Agents:\n"]
        for name, info in sorted(status.items()):
            caps = info.get("capabilities", [])
            display_name = name.replace("_agent", "").replace("_", " ").title()
            lines.append(f"  {display_name}")
            lines.append(f"    Status: {info['status']}")
            if caps:
                lines.append(f"    Capabilities: {', '.join(caps[:5])}")
            lines.append("")
        return {"success": True, "response": "\n".join(lines)}

    def _cmd_tasks(self, args: str, context: dict) -> dict:
        manager = context.get("manager")
        if not manager:
            return {"success": False, "response": "Manager not available"}
        tasks = manager.get_task_history(limit=20)
        if not tasks:
            return {"success": True, "response": "No tasks in history."}
        lines = ["Recent Tasks:\n"]
        for t in tasks[:10]:
            icon = {"completed": "✓", "failed": "✖", "running": "⟳", "pending": "○"}.get(t.get("status", ""), "—")
            lines.append(f"  {icon} [{t.get('status', '?')}] {t.get('command', '')[:50]}")
            lines.append(f"     Agent: {t.get('agent', '?')} | Time: {t.get('created_at', '?')[:19]}")
        return {"success": True, "response": "\n".join(lines)}

    def _cmd_clear(self, args: str, context: dict) -> dict:
        chat_log = self.query_one("#chat-log", RichLog)
        chat_log.clear()
        return {"success": True, "response": ""}

    def _cmd_history(self, args: str, context: dict) -> dict:
        if not self._message_history:
            return {"success": True, "response": "No command history."}
        lines = ["Command History:\n"]
        for msg in self._message_history[-20:]:
            time_str = msg.get("time", datetime.now()).strftime("%H:%M:%S") if isinstance(msg.get("time"), datetime) else ""
            role = msg.get("role", "?")
            content = msg.get("content", "")[:60]
            lines.append(f"  [{time_str}] {role}: {content}")
        return {"success": True, "response": "\n".join(lines)}

    def _cmd_modes(self, args: str, context: dict) -> dict:
        manager = context.get("manager")
        if not manager:
            return {"success": False, "response": "Manager not available"}
        workflow_agent = manager.agents.get("workflow_agent")
        if not workflow_agent:
            return {"success": False, "response": "Workflow agent not available"}
        try:
            result = workflow_agent.execute("list modes")
            return {"success": True, "response": result.get("response", "No modes available")}
        except Exception as e:
            return {"success": False, "response": f"Error: {str(e)}"}

    def _cmd_model(self, args: str, context: dict) -> dict:
        manager = context.get("manager")
        if not manager:
            return {"success": False, "response": "Manager not available"}
        if hasattr(manager, "_llm") and manager._llm:
            current = manager._llm.get_model()
            provider = manager._llm.get_provider_name()
            return {"success": True, "response": f"Current model: {current} ({provider})"}
        return {"success": False, "response": "LLM not available"}

    def _cmd_back(self, args: str, context: dict) -> dict:
        self.app.pop_screen()
        return {"success": True, "response": ""}
