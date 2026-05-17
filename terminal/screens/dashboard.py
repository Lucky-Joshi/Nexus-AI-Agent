"""
NEXUS - Dashboard Screen
Startup dashboard with system overview, agent status, and quick commands.
"""

import psutil
from textual.screen import Screen
from textual.widgets import Static, Input
from textual.containers import Container, Vertical
from textual.app import ComposeResult
from rich.text import Text
from rich.panel import Panel
from rich.console import Group
from datetime import datetime

from terminal.widgets import NexusHeader, NexusStatusBar


class DashboardScreen(Screen):
    """Initial dashboard screen shown on NEXUS startup."""

    CSS = """
    DashboardScreen {
        background: #0A0E17;
    }

    #dashboard-container {
        width: 100%;
        height: 100%;
        align: center middle;
    }

    #dashboard-content {
        width: 80%;
        max-width: 90;
        background: #111827;
        border: round #00D4FF;
        padding: 1 2;
    }

    #command-input {
        dock: bottom;
        height: 3;
        margin: 0 2;
        background: #111827;
        border: round #00D4FF;
    }

    #status-bar {
        dock: bottom;
        height: 1;
        background: #111827;
        border-top: solid #00D4FF;
    }
    """

    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        self._session_id = manager.session_id if manager else "unknown"

    def compose(self) -> ComposeResult:
        yield Static("", id="status-bar")
        yield Container(
            Static("", id="dashboard-content"),
            id="dashboard-container",
        )
        yield Input(placeholder="Type a command or /help...", id="command-input")

    def on_mount(self) -> None:
        self._render_dashboard()
        self.query_one("#command-input", Input).focus()

    def _render_dashboard(self):
        """Render the dashboard content."""
        lines = []

        lines.append(Text("╔══════════════════════════════════════════════════════════╗", style="#00D4FF"))
        lines.append(Text("║", style="#00D4FF") + Text("              NEXUS AI Operating Environment              ", style="bold #00D4FF") + Text("║", style="#00D4FF"))
        lines.append(Text("║", style="#00D4FF") + Text("              Terminal-Native AI Companion                ", style="dim #7B61FF") + Text("║", style="#00D4FF"))
        lines.append(Text("╚══════════════════════════════════════════════════════════╝", style="#00D4FF"))
        lines.append(Text(""))

        try:
            cpu = psutil.cpu_percent(interval=0.1)
            ram = psutil.virtual_memory().percent
            disk = psutil.disk_usage("/").percent
        except Exception:
            cpu = ram = disk = 0

        agents = self.manager.get_agent_status() if self.manager else {}
        idle = sum(1 for s in agents.values() if s["status"] == "idle")
        total = len(agents)

        model = "llama3"
        provider = "ollama"
        if self.manager and hasattr(self.manager, "_llm") and self.manager._llm:
            model = self.manager._llm.get_model()
            provider = self.manager._llm.get_provider_name()

        lines.append(Text(" SYSTEM STATUS", style="bold #00D4FF"))
        lines.append(Text(f"   CPU: {cpu}%  |  RAM: {ram}%  |  Disk: {disk}%", style="#E8E8E8"))
        lines.append(Text(f"   Model: {model}  |  Provider: {provider}", style="#E8E8E8"))
        lines.append(Text(f"   Session: {self._session_id}", style="dim #888888"))
        lines.append(Text(""))

        lines.append(Text(" AGENTS", style="bold #00D4FF"))
        lines.append(Text(f"   Total: {total}  |  Idle: {idle}  |  Active: {total - idle}", style="#E8E8E8"))
        lines.append(Text(""))

        lines.append(Text(" QUICK COMMANDS", style="bold #00D4FF"))
        commands = [
            ("/help", "Show all commands"),
            ("/status", "Show agent status"),
            ("/agents", "List all agents"),
            ("/tasks", "Show active tasks"),
            ("/modes", "List workflow modes"),
            ("/clear", "Clear screen"),
            ("start coding mode", "Activate coding workflow"),
            ("system status", "Check system health"),
        ]
        for cmd, desc in commands:
            lines.append(Text(f"   {cmd:<25} {desc}", style="dim #888888"))

        lines.append(Text(""))
        lines.append(Text(" Type a command or press / for command palette", style="bold #7B61FF"))

        content = Panel(Group(*lines), border_style="#00D4FF", title="Dashboard")
        self.query_one("#dashboard-content", Static).update(content)

        now = datetime.now().strftime("%H:%M:%S")
        status_text = Text(f"◆ NEXUS Ready | {idle}/{total} agents | {now}", style="#E8E8E8")
        self.query_one("#status-bar", Static).update(Panel(status_text, style="on #111827", border_style="#00D4FF"))

    def on_input_submitted(self, event: Input.Submitted) -> None:
        command = event.value.strip()
        if not command:
            return

        if command.lower() in ("exit", "quit", "q"):
            self.app.exit()
            return

        if command.lower() == "/clear":
            self._render_dashboard()
            self.query_one("#command-input", Input).value = ""
            return

        self.query_one("#command-input", Input).value = ""
        from terminal.screens.chat import ChatScreen
        self.app.push_screen(ChatScreen(self.manager, initial_command=command))
