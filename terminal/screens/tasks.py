"""
NEXUS - Task Screen
Live task panel showing running workflows, active agents, and progress.
"""

from textual.screen import Screen
from textual.widgets import Static, Input
from textual.containers import Container
from textual.app import ComposeResult
from rich.text import Text
from rich.panel import Panel
from rich.console import Group
from rich.table import Table as RichTable
from datetime import datetime

from terminal.widgets import NexusHeader, NexusStatusBar


class TaskScreen(Screen):
    """Screen showing active tasks, agent status, and system info."""

    CSS = """
    TaskScreen {
        background: #0A0E17;
    }

    #task-container {
        width: 100%;
        height: 1fr;
        padding: 0 1;
    }

    #status-bar {
        dock: bottom;
        height: 1;
        background: #111827;
        border-top: solid #00D4FF;
    }

    #header {
        dock: top;
        height: 3;
        background: #111827;
        border-bottom: solid #00D4FF;
    }
    """

    def __init__(self, manager):
        super().__init__()
        self.manager = manager

    def on_mount(self) -> None:
        self._render_tasks()
        self._update_header()
        self._update_status()

    def _update_header(self):
        session = self.manager.session_id if self.manager else "unknown"
        agents = self.manager.get_agent_status() if self.manager else {}
        total = len(agents)
        header = NexusHeader()
        header.session_id = session
        header.agent_count = total
        header.active_mode = "Task Monitor"
        self.query_one("#header", Static).update(header.render())

    def _update_status(self):
        agents = self.manager.get_agent_status() if self.manager else {}
        idle = sum(1 for s in agents.values() if s.get("status") == "idle")
        total = len(agents)
        now = datetime.now().strftime("%H:%M:%S")
        status_text = Text(f"◆ Task Monitor | {idle}/{total} agents idle | {now}", style="#E8E8E8")
        self.query_one("#status-bar", Static).update(Panel(status_text, style="on #111827", border_style="#00D4FF"))

    def _render_tasks(self):
        lines = []

        lines.append(Text(" ACTIVE TASKS", style="bold #00D4FF"))
        lines.append(Text(""))

        tasks = self.manager.get_task_history(limit=20) if self.manager else []
        if tasks:
            table = RichTable.grid(padding=(0, 1))
            table.add_column("Status", width=2)
            table.add_column("Command", ratio=1)
            table.add_column("Agent", width=20)
            table.add_column("Time", width=20)

            for t in tasks[:15]:
                status = t.get("status", "unknown")
                if status == "completed":
                    icon = Text("✓ ", style="#00E676")
                elif status == "failed":
                    icon = Text("✖ ", style="#FF4757")
                elif status == "running":
                    icon = Text("⟳ ", style="#FFB800")
                else:
                    icon = Text("○ ", style="#555555")

                command = t.get("command", "")[:40]
                agent = t.get("agent", "?")[:20]
                time_str = t.get("created_at", "?")[:19] if t.get("created_at") else "?"

                table.add_row(icon, Text(command, style="#E8E8E8"), Text(agent, style="dim #888888"), Text(time_str, style="dim #555555"))

            lines.append(table)
        else:
            lines.append(Text("  No tasks in history", style="dim #555555"))

        lines.append(Text(""))
        lines.append(Text(" AGENT STATUS", style="bold #00D4FF"))
        lines.append(Text(""))

        agents = self.manager.get_agent_status() if self.manager else {}
        if agents:
            table = RichTable.grid(padding=(0, 1))
            table.add_column("Status", width=2)
            table.add_column("Agent", ratio=1)
            table.add_column("Status", width=10)

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
                table.add_row(icon, Text(display_name, style="#E8E8E8"), Text(status.upper(), style=icon.style))

            lines.append(table)

        content = Panel(Group(*lines), border_style="#00D4FF", title="Task Monitor")
        self.query_one("#task-container", Static).update(content)
