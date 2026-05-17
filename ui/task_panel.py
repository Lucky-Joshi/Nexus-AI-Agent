from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QScrollArea, QPushButton, QProgressBar, QTabWidget,
    QTextEdit, QListWidget, QListWidgetItem,
)
from PyQt6.QtCore import Qt, QTimer
from core.logger import Logger


class TaskPanel(QWidget):
    """
    Task and logs panel for NEXUS.
    Shows active tasks, task history, and log console.
    """

    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        self.logger = Logger().get_logger("TaskPanel")
        self.setObjectName("task_panel")
        self.setFixedWidth(350)

        self._setup_ui()
        self._start_refresh_timer()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QFrame()
        header.setObjectName("glass_panel")
        header.setFixedHeight(50)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(16, 8, 16, 8)

        title = QLabel("Tasks & Logs")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #00D4FF;")
        header_layout.addWidget(title)

        header_layout.addStretch()
        layout.addWidget(header)

        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.TabPosition.North)
        self.tabs.setStyleSheet("""
            QTabBar::tab {
                background-color: #21262D;
                color: #8B949E;
                padding: 6px 12px;
                border: none;
            }
            QTabBar::tab:selected {
                background-color: #161B22;
                color: #00D4FF;
            }
        """)

        self._setup_tasks_tab()
        self._setup_agents_tab()
        self._setup_logs_tab()

        layout.addWidget(self.tabs)

    def _setup_tasks_tab(self):
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)
        tab_layout.setContentsMargins(8, 8, 8, 8)

        self.task_list = QListWidget()
        self.task_list.setStyleSheet("""
            QListWidget {
                background: transparent;
                border: none;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #21262D;
                color: #E6EDF3;
            }
            QListWidget::item:selected {
                background-color: #00D4FF22;
                color: #00D4FF;
            }
        """)
        tab_layout.addWidget(self.task_list)

        self.tabs.addTab(tab, "Tasks")

    def _setup_agents_tab(self):
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)
        tab_layout.setContentsMargins(8, 8, 8, 8)

        self.agent_status_container = QWidget()
        self.agent_status_layout = QVBoxLayout(self.agent_status_container)
        self.agent_status_layout.setContentsMargins(0, 0, 0, 0)
        self.agent_status_layout.setSpacing(8)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.agent_status_container)
        scroll.setStyleSheet("background: transparent; border: none;")
        tab_layout.addWidget(scroll)

        self.tabs.addTab(scroll, "Agents")

    def _setup_logs_tab(self):
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)
        tab_layout.setContentsMargins(8, 8, 8, 8)

        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setStyleSheet("""
            QTextEdit {
                background-color: #0D1117;
                color: #8B949E;
                border: 1px solid #30363D;
                border-radius: 6px;
                font-family: 'Cascadia Code', 'Consolas', monospace;
                font-size: 12px;
                padding: 8px;
            }
        """)
        tab_layout.addWidget(self.log_display)

        clear_btn = QPushButton("Clear Logs")
        clear_btn.setObjectName("sidebar_button")
        clear_btn.clicked.connect(self.log_display.clear)
        tab_layout.addWidget(clear_btn)

        self.tabs.addTab(tab, "Logs")

    def _start_refresh_timer(self):
        self._refresh_timer = QTimer(self)
        self._refresh_timer.timeout.connect(self._refresh)
        self._refresh_timer.start(3000)
        self._refresh()

    def _refresh(self):
        self._refresh_tasks()
        self._refresh_agent_status()

    def _refresh_tasks(self):
        tasks = self.manager.get_task_history(limit=10)
        self.task_list.clear()

        for task in tasks:
            status = task.get("status", "unknown")
            agent = task.get("agent", "unknown")
            command = task.get("command", "")[:40]

            status_colors = {
                "completed": "#3FB950",
                "running": "#D29922",
                "failed": "#F85149",
                "pending": "#8B949E",
                "cancelled": "#484F58",
            }
            color = status_colors.get(status, "#8B949E")

            item_text = f"[{status.upper()}] {agent}: {command}"
            item = QListWidgetItem(item_text)
            item.setForeground(color)
            self.task_list.addItem(item)

    def _refresh_agent_status(self):
        while self.agent_status_layout.count() > 0:
            item = self.agent_status_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        status = self.manager.get_agent_status()
        for name, info in status.items():
            agent_frame = QFrame()
            agent_frame.setObjectName("glass_panel")
            agent_layout = QHBoxLayout(agent_frame)
            agent_layout.setContentsMargins(10, 6, 10, 6)

            status_color = {
                "idle": "#3FB950",
                "busy": "#D29922",
                "error": "#F85149",
                "offline": "#484F58",
            }.get(info["status"], "#484F58")

            indicator = QLabel("●")
            indicator.setStyleSheet(f"color: {status_color}; font-size: 14px;")
            agent_layout.addWidget(indicator)

            name_label = QLabel(name.replace("_", " ").title())
            name_label.setStyleSheet("color: #E6EDF3; font-size: 13px;")
            agent_layout.addWidget(name_label)

            agent_layout.addStretch()

            status_label = QLabel(info["status"].upper())
            status_label.setStyleSheet(f"color: {status_color}; font-size: 11px; font-weight: bold;")
            agent_layout.addWidget(status_label)

            self.agent_status_layout.addWidget(agent_frame)

        self.agent_status_layout.addStretch()

    def add_log(self, message: str):
        self.log_display.append(message)
