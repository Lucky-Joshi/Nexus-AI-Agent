from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit,
    QPushButton, QScrollArea, QFrame, QLabel, QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QTextCursor
from core.logger import Logger


class ChatWidget(QWidget):
    """
    Main chat interface for NEXUS.
    Message display area with input field and send button.
    """

    message_sent = pyqtSignal(str)

    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        self.logger = Logger().get_logger("ChatWidget")
        self.setObjectName("chat_area")

        self._setup_ui()
        self._load_history()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QFrame()
        header.setObjectName("glass_panel")
        header.setFixedHeight(50)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(16, 8, 16, 8)

        title = QLabel("Chat")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #00D4FF;")
        header_layout.addWidget(title)

        header_layout.addStretch()

        clear_btn = QPushButton("Clear")
        clear_btn.setObjectName("sidebar_button")
        clear_btn.setFixedWidth(60)
        clear_btn.clicked.connect(self._clear_chat)
        header_layout.addWidget(clear_btn)

        layout.addWidget(header)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet("background: transparent; border: none;")

        self.messages_container = QWidget()
        self.messages_layout = QVBoxLayout(self.messages_container)
        self.messages_layout.setContentsMargins(16, 16, 16, 16)
        self.messages_layout.setSpacing(12)
        self.messages_layout.addStretch()

        self.scroll.setWidget(self.messages_container)
        layout.addWidget(self.scroll)

        input_frame = QFrame()
        input_frame.setObjectName("glass_panel")
        input_frame.setFixedHeight(60)
        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(12, 8, 12, 8)
        input_layout.setSpacing(8)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type a command or message...")
        self.input_field.returnPressed.connect(self._send_message)
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: #0D1117;
                color: #E6EDF3;
                border: 1px solid #30363D;
                border-radius: 8px;
                padding: 8px 14px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #00D4FF;
            }
        """)
        input_layout.addWidget(self.input_field)

        send_btn = QPushButton("Send")
        send_btn.setObjectName("accent_button")
        send_btn.setFixedWidth(70)
        send_btn.clicked.connect(self._send_message)
        input_layout.addWidget(send_btn)

        layout.addWidget(input_frame)

    def _send_message(self):
        text = self.input_field.text().strip()
        if not text:
            return

        self.input_field.clear()
        self._add_message(text, "user")
        self.message_sent.emit(text)

        QTimer.singleShot(100, lambda: self._process_command(text))

    def _process_command(self, command: str):
        try:
            result = self.manager.process_command(command)
            response = result.get("response", "No response")
            self._add_message(response, "assistant", result.get("agent", "nexus"))
        except Exception as e:
            self.logger.error(f"Command processing error: {e}")
            self._add_message(f"Error: {str(e)}", "assistant", "error")

    def _add_message(self, text: str, role: str, agent: str = ""):
        msg_frame = QFrame()
        msg_frame.setObjectName(f"message_{role}")
        msg_frame.setMaximumWidth(700)

        msg_layout = QVBoxLayout(msg_frame)
        msg_layout.setContentsMargins(12, 8, 12, 8)

        header_layout = QHBoxLayout()
        role_label = QLabel(role.upper())
        role_label.setStyleSheet(
            f"font-size: 11px; font-weight: bold; color: {'#00D4FF' if role == 'user' else '#3FB950'};"
        )
        header_layout.addWidget(role_label)

        if agent and agent != "manager":
            agent_label = QLabel(f"[{agent}]")
            agent_label.setStyleSheet("font-size: 10px; color: #8B949E;")
            header_layout.addWidget(agent_label)

        header_layout.addStretch()
        msg_layout.addLayout(header_layout)

        content = QLabel(text)
        content.setWordWrap(True)
        content.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        content.setStyleSheet("font-size: 14px; line-height: 1.5; color: #E6EDF3;")
        content.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        msg_layout.addWidget(content)

        self.messages_layout.insertWidget(self.messages_layout.count() - 1, msg_frame)

        QTimer.singleShot(50, lambda: self.scroll.verticalScrollBar().setValue(
            self.scroll.verticalScrollBar().maximum()
        ))

    def _load_history(self):
        try:
            history = self.manager.get_conversation_history(limit=20)
            for msg in reversed(history):
                self._add_message(msg["content"], msg["role"], msg.get("agent", ""))
        except Exception:
            self._add_message("Welcome to NEXUS. How can I help you?", "assistant", "nexus")

    def _clear_chat(self):
        while self.messages_layout.count() > 1:
            item = self.messages_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.manager.process_command("clear")
        self._add_message("Conversation cleared.", "assistant", "nexus")
