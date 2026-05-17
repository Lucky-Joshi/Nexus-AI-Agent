"""
NEXUS - Terminal UI Widgets
Reusable Textual widgets for the terminal interface.
"""

from textual.widget import Widget
from textual.reactive import reactive
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Static, ProgressBar, DataTable, Tree
from textual.app import ComposeResult
from rich.text import Text
from rich.panel import Panel
from rich.table import Table as RichTable
from rich.console import Group
from datetime import datetime

from core.base_agent import AgentStatus


class NexusHeader(Static):
    """NEXUS header bar with logo and session info."""

    session_id = reactive("")
    agent_count = reactive(0)
    active_mode = reactive("")

    def render(self) -> Panel:
        title = Text(" NEXUS ", style="bold #00D4FF on #111827")
        title.append(" AI Operating Environment", style="dim #7B61FF on #111827")

        info_parts = []
        if self.session_id:
            info_parts.append(f"Session: {self.session_id}")
        if self.agent_count:
            info_parts.append(f"Agents: {self.agent_count}")
        if self.active_mode:
            info_parts.append(f"Mode: {self.active_mode}")

        info = " | ".join(info_parts)
        info_text = Text(info, style="dim #888888 on #111827")

        combined = Group(title, info_text)
        return Panel(combined, style="on #111827", border_style="#00D4FF")


class NexusStatusBar(Static):
    """Status bar showing system info, agent status, and time."""

    status_text = reactive("NEXUS Ready")
    agent_status = reactive({})
    task_count = reactive(0)

    def render(self) -> Panel:
        now = datetime.now().strftime("%H:%M:%S")

        agents = self.agent_status
        idle = sum(1 for s in agents.values() if s == "idle")
        busy = sum(1 for s in agents.values() if s == "busy")
        total = len(agents)

        status_line = Text()
        status_line.append("◆ ", style="#00D4FF")
        status_line.append(f"{self.status_text} ", style="bold #E8E8E8")
        status_line.append(f"| Agents: {idle}/{total} idle ", style="dim #888888")
        if busy > 0:
            status_line.append(f"| {busy} active ", style="#FFB800")
        if self.task_count > 0:
            status_line.append(f"| Tasks: {self.task_count} ", style="#7B61FF")
        status_line.append(f"| {now}", style="dim #555555")

        return Panel(status_line, style="on #111827", border_style="#00D4FF")


class NexusAgentPanel(Static):
    """Panel showing all registered agents and their status."""

    agents = reactive({})

    def render(self) -> Panel:
        if not self.agents:
            return Panel("No agents registered", title="Agents", border_style="#00D4FF")

        table = RichTable.grid(padding=(0, 1))
        table.add_column("Status", width=2)
        table.add_column("Agent", ratio=1)
        table.add_column("Status", justify="right", width=8)

        for name, info in sorted(self.agents.items()):
            status = info.get("status", "idle")
            if status == "idle":
                icon = "●"
                style = "#00E676"
            elif status == "busy":
                icon = "◉"
                style = "#FFB800"
            elif status == "error":
                icon = "✖"
                style = "#FF4757"
            else:
                icon = "○"
                style = "#555555"

            display_name = name.replace("_agent", "").replace("_", " ").title()
            table.add_row(
                Text(icon, style=style),
                Text(display_name, style="#E8E8E8"),
                Text(status.upper(), style=style),
            )

        return Panel(table, title="Agents", border_style="#00D4FF")


class NexusTaskPanel(Static):
    """Panel showing running tasks and their progress."""

    tasks = reactive([])

    def render(self) -> Panel:
        if not self.tasks:
            return Panel("No active tasks", title="Tasks", border_style="#00D4FF")

        table = RichTable.grid(padding=(0, 1))
        table.add_column("Status", width=2)
        table.add_column("Task", ratio=1)
        table.add_column("Agent", width=15)

        for task in self.tasks:
            status = task.get("status", "pending")
            if status == "running":
                icon = "⟳"
                style = "#FFB800"
            elif status == "completed":
                icon = "✓"
                style = "#00E676"
            elif status == "failed":
                icon = "✖"
                style = "#FF4757"
            elif status == "pending":
                icon = "○"
                style = "#555555"
            else:
                icon = "—"
                style = "#555555"

            agent = task.get("agent", "unknown")[:15]
            command = task.get("command", "")[:30]
            table.add_row(
                Text(icon, style=style),
                Text(command, style="#E8E8E8"),
                Text(agent, style="dim #888888"),
            )

        return Panel(table, title="Tasks", border_style="#00D4FF")


class NexusMessage(Static):
    """A single message in the chat area."""

    role = reactive("user")
    content = reactive("")
    agent = reactive("")
    timestamp = reactive("")

    def render(self) -> Panel:
        if self.role == "user":
            border_style = "#7B61FF"
            bg_style = "on #1A1A2E"
            prefix = "YOU"
        elif self.role == "system":
            border_style = "#FFB800"
            bg_style = "on #1A1500"
            prefix = "SYSTEM"
        else:
            border_style = "#00D4FF"
            bg_style = "on #0D1B2A"
            prefix = self.agent.upper() if self.agent else "NEXUS"

        content_text = Text(self.content, style="#E8E8E8")
        header_text = Text(f"{prefix}", style=f"bold {border_style}")

        combined = Group(header_text, content_text)
        return Panel(combined, border_style=border_style, style=bg_style)


class NexusDashboard(Static):
    """Startup dashboard with system overview."""

    stats = reactive({})
    agents = reactive({})
    recent_commands = reactive([])

    def render(self) -> Panel:
        lines = []

        lines.append(Text("╔══════════════════════════════════════════════════════════╗", style="#00D4FF"))
        lines.append(Text("║", style="#00D4FF") + Text("              NEXUS AI Operating Environment              ", style="bold #00D4FF") + Text("║", style="#00D4FF"))
        lines.append(Text("║", style="#00D4FF") + Text("              Terminal-Native AI Companion                ", style="dim #7B61FF") + Text("║", style="#00D4FF"))
        lines.append(Text("╚══════════════════════════════════════════════════════════╝", style="#00D4FF"))
        lines.append(Text(""))

        stats = self.stats
        if stats:
            lines.append(Text(" SYSTEM STATUS", style="bold #00D4FF"))
            lines.append(Text(f"   CPU: {stats.get('cpu', 'N/A')}%  |  RAM: {stats.get('ram', 'N/A')}%  |  Disk: {stats.get('disk', 'N/A')}%", style="#E8E8E8"))
            lines.append(Text(f"   Model: {stats.get('model', 'N/A')}  |  Provider: {stats.get('provider', 'N/A')}", style="#E8E8E8"))
            lines.append(Text(""))

        agents = self.agents
        if agents:
            lines.append(Text(" AGENTS", style="bold #00D4FF"))
            idle = sum(1 for s in agents.values() if s == "idle")
            busy = sum(1 for s in agents.values() if s == "busy")
            lines.append(Text(f"   Total: {len(agents)}  |  Idle: {idle}  |  Active: {busy}", style="#E8E8E8"))
            lines.append(Text(""))

        lines.append(Text(" QUICK COMMANDS", style="bold #00D4FF"))
        lines.append(Text("   /help          Show all commands", style="dim #888888"))
        lines.append(Text("   /status        Show agent status", style="dim #888888"))
        lines.append(Text("   /agents        List all agents", style="dim #888888"))
        lines.append(Text("   /tasks         Show active tasks", style="dim #888888"))
        lines.append(Text("   /modes         List workflow modes", style="dim #888888"))
        lines.append(Text("   /clear         Clear screen", style="dim #888888"))
        lines.append(Text(""))
        lines.append(Text(" Type a command or press / for command palette", style="bold #7B61FF"))

        return Panel(Group(*lines), border_style="#00D4FF", title="Dashboard")


class NexusCommandInput(Static):
    """Command input area with prompt."""

    prompt_text = reactive("nexus> ")

    def render(self) -> Panel:
        prompt = Text(self.prompt_text, style="bold #00D4FF")
        return Panel(prompt, style="on #111827", border_style="#00D4FF")
