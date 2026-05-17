from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QFrame,
    QScrollArea, QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSignal
from core.logger import Logger
from core.base_agent import AgentStatus


class Sidebar(QWidget):
    """
    Sidebar navigation panel for NEXUS.
    Shows agent list with live status indicators.
    """

    agent_selected = pyqtSignal(str)

    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        self.logger = Logger().get_logger("Sidebar")
        self.setObjectName("sidebar")
        self.setFixedWidth(220)

        self._setup_ui()
        self._load_agents()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        title_frame = QFrame()
        title_frame.setObjectName("glass_panel")
        title_frame.setFixedHeight(60)
        title_layout = QVBoxLayout(title_frame)
        title_layout.setContentsMargins(16, 8, 16, 8)

        title_label = QLabel("NEXUS")
        title_label.setObjectName("accent")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #00D4FF;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.addWidget(title_label)

        subtitle = QLabel("AI Companion")
        subtitle.setObjectName("secondary")
        subtitle.setStyleSheet("font-size: 11px; color: #8B949E;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.addWidget(subtitle)

        layout.addWidget(title_frame)

        separator = QFrame()
        separator.setObjectName("separator")
        separator.setFixedHeight(1)
        layout.addWidget(separator)

        nav_label = QLabel("  AGENTS")
        nav_label.setStyleSheet("color: #484F58; font-size: 11px; font-weight: bold; padding: 12px 0 6px 0;")
        layout.addWidget(nav_label)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet("background: transparent; border: none;")

        self.agent_container = QWidget()
        self.agent_layout = QVBoxLayout(self.agent_container)
        self.agent_layout.setContentsMargins(8, 4, 8, 4)
        self.agent_layout.setSpacing(4)

        self.scroll.setWidget(self.agent_container)
        layout.addWidget(self.scroll)

        self.agent_buttons = {}

    def _load_agents(self):
        agents = [
            ("AI Manager", "manager", "Central orchestrator"),
        ]

        for name, agent_key, desc in self.manager.get_agent_status().items():
            agents.append((name.replace("_", " ").title(), name, desc.get("description", "")))

        for display_name, agent_key, desc in agents:
            btn = self._create_agent_button(display_name, agent_key)
            self.agent_layout.addWidget(btn)
            self.agent_buttons[agent_key] = btn

        self.agent_layout.addStretch()

    def _create_agent_button(self, name: str, agent_key: str) -> QPushButton:
        btn = QPushButton(name)
        btn.setObjectName("sidebar_button")
        btn.setCheckable(True)
        btn.setProperty("agent_key", agent_key)
        btn.clicked.connect(lambda: self._on_agent_clicked(agent_key))

        if agent_key == "manager":
            btn.setChecked(True)

        return btn

    def _on_agent_clicked(self, agent_key: str):
        for key, btn in self.agent_buttons.items():
            if key != agent_key:
                btn.setChecked(False)
        self.agent_selected.emit(agent_key)

    def update_agent_status(self, agent_key: str, status: AgentStatus):
        if agent_key in self.agent_buttons:
            btn = self.agent_buttons[agent_key]
            color_map = {
                AgentStatus.IDLE: "#3FB950",
                AgentStatus.BUSY: "#D29922",
                AgentStatus.ERROR: "#F85149",
                AgentStatus.OFFLINE: "#484F58",
            }
            color = color_map.get(status, "#484F58")
            btn.setStyleSheet(btn.styleSheet() + f"color: {color};")
