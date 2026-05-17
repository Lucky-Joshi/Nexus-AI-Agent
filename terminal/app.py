"""
NEXUS - Terminal Application
Main Textual application that orchestrates all terminal screens.
"""

from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Static
from textual.binding import Binding
from textual.containers import Container

from terminal.screens.dashboard import DashboardScreen
from terminal.screens.chat import ChatScreen
from terminal.screens.tasks import TaskScreen
from terminal.theme import NEXUS_THEME, CSS


class NEXUSTerminalApp(App):
    """
    NEXUS Terminal Application.
    A futuristic, terminal-native AI operating environment.
    """

    CSS = CSS

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit", show=True, priority=True),
        Binding("ctrl+d", "quit", "Quit", show=False),
        Binding("ctrl+l", "clear_screen", "Clear", show=True),
        Binding("ctrl+k", "show_tasks", "Tasks", show=True),
        Binding("ctrl+h", "show_dashboard", "Home", show=True),
        Binding("escape", "back", "Back", show=True),
    ]

    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        self.title = "NEXUS"
        self.sub_title = "AI Operating Environment"

    def on_mount(self) -> None:
        self.register_theme(NEXUS_THEME)
        self.theme = "nexus"
        self.install_screen(DashboardScreen(self.manager), name="dashboard")
        self.install_screen(ChatScreen(self.manager), name="chat")
        self.install_screen(TaskScreen(self.manager), name="tasks")
        self.push_screen("dashboard")

    def action_quit(self) -> None:
        """Exit the application."""
        if self.manager:
            self.manager.shutdown()
        self.exit()

    def action_clear_screen(self) -> None:
        """Clear the current screen."""
        current = self.screen
        if hasattr(current, "query_one"):
            try:
                chat_log = current.query_one("#chat-log")
                if hasattr(chat_log, "clear"):
                    chat_log.clear()
            except Exception:
                pass

    def action_show_tasks(self) -> None:
        """Show the task monitor screen."""
        self.push_screen("tasks")

    def action_show_dashboard(self) -> None:
        """Return to the dashboard."""
        self.push_screen("dashboard")

    def action_back(self) -> None:
        """Go back to previous screen."""
        if len(self._screen_stack) > 1:
            self.pop_screen()
