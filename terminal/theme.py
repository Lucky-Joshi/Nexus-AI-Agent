"""
NEXUS - Terminal Theme
Futuristic dark theme for Textual terminal UI.
"""

from textual.theme import Theme

NEXUS_THEME = Theme(
    name="nexus",
    primary="#00D4FF",
    secondary="#7B61FF",
    warning="#FFB800",
    error="#FF4757",
    success="#00E676",
    accent="#00D4FF",
    foreground="#E8E8E8",
    background="#0A0E17",
    surface="#111827",
    panel="#1A2332",
    boost="#7B61FF",
)

CSS = """
Screen {
    background: $background;
}

#header {
    dock: top;
    height: 3;
    background: $surface;
    border-bottom: solid $primary;
    padding: 0 1;
}

#header-title {
    color: $primary;
    text-style: bold;
    content-align: center middle;
}

#status-bar {
    dock: bottom;
    height: 1;
    background: $surface;
    border-top: solid $primary;
    padding: 0 1;
}

#sidebar {
    dock: left;
    width: 30;
    background: $panel;
    border-right: solid $primary;
}

#main-content {
    background: $background;
}

#command-input {
    dock: bottom;
    height: 3;
    background: $surface;
    border-top: solid $primary;
    padding: 0 1;
}

#chat-area {
    background: $background;
}

#task-panel {
    dock: right;
    width: 40;
    background: $panel;
    border-left: solid $primary;
}

NexusMessage {
    margin: 1 2;
    padding: 1 2;
    background: $surface;
    border: round $primary;
}

NexusMessage.user {
    border: round $secondary;
    background: #1A1A2E;
}

NexusMessage.assistant {
    border: round $primary;
    background: #0D1B2A;
}

NexusMessage.system {
    border: round $warning;
    background: #1A1500;
}

NexusTaskItem {
    margin: 0 1;
    padding: 0 1;
    height: 2;
}

NexusAgentStatus {
    margin: 0 1;
    padding: 0 1;
    height: 1;
}

ProgressBar {
    background: $surface;
    color: $primary;
}

DataTable {
    background: $surface;
    border: round $primary;
}

DataTable > .datatable--header {
    background: $panel;
    color: $primary;
    text-style: bold;
}

DataTable > .datatable--cursor {
    background: $primary;
    color: $background;
}

Footer {
    background: $surface;
    border-top: solid $primary;
}

Input {
    border: round $primary;
    background: $background;
    color: $foreground;
}

Input:focus {
    border: round $accent;
}

Label {
    color: $foreground;
}

RichLog {
    background: $background;
    color: $foreground;
}

Tree {
    background: $panel;
    color: $foreground;
}

Tree > .tree--guideline {
    color: $primary;
}

Tree > .tree--guideline-selected {
    color: $accent;
}

TabbedContent {
    background: $background;
}

TabbedContent > .tabbed-content--tab-list {
    background: $surface;
}

TabbedContent > .tabbed-content--content {
    background: $background;
}
"""
