from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QSplitter,
    QStatusBar, QLabel, QFrame,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from core.logger import Logger
from core.config import Config
from ui.themes.dark_theme import get_stylesheet
from ui.sidebar import Sidebar
from ui.chat_widget import ChatWidget
from ui.task_panel import TaskPanel


class MainWindow(QMainWindow):
    """
    Main application window for NEXUS.
    Layout: [Sidebar] | [Chat Area] | [Task/Logs Panel]
    """

    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        self.logger = Logger().get_logger("UI")
        self.config = Config()

        self._setup_window()
        self._setup_ui()
        self._apply_theme()
        self._start_status_timer()

        self.logger.info("MainWindow initialized")

    def _setup_window(self):
        width = self.config.get("ui.window_width", 1400)
        height = self.config.get("ui.window_height", 900)
        self.resize(width, height)
        self.setWindowTitle("NEXUS - AI Operating Companion")
        self.setMinimumSize(1000, 700)

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(1)

        self.sidebar = Sidebar(self.manager)
        splitter.addWidget(self.sidebar)

        self.chat = ChatWidget(self.manager)
        splitter.addWidget(self.chat)

        self.task_panel = TaskPanel(self.manager)
        splitter.addWidget(self.task_panel)

        splitter.setSizes([220, 800, 350])
        main_layout.addWidget(splitter)

        self._setup_status_bar()

    def _setup_status_bar(self):
        status = QStatusBar()
        self.setStatusBar(status)

        self.status_label = QLabel("NEXUS Ready")
        self.status_label.setStyleSheet("color: #8B949E; padding: 4px 8px;")
        status.addWidget(self.status_label)

        self.agent_count_label = QLabel(f"Agents: {len(self.manager.agents)}")
        self.agent_count_label.setStyleSheet("color: #8B949E; padding: 4px 8px;")
        status.addPermanentWidget(self.agent_count_label)

    def _apply_theme(self):
        self.setStyleSheet(get_stylesheet())

    def _start_status_timer(self):
        self._status_timer = QTimer(self)
        self._status_timer.timeout.connect(self._update_status)
        self._status_timer.start(5000)

    def _update_status(self):
        status = self.manager.get_agent_status()
        active = sum(1 for s in status.values() if s["status"] == "idle")
        total = len(status)
        self.status_label.setText(f"NEXUS Ready | {active}/{total} agents available")

    def closeEvent(self, event):
        self.logger.info("MainWindow closing...")
        self.manager.shutdown()
        event.accept()
