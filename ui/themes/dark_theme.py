"""
NEXUS - Futuristic Dark Glassmorphism Theme for PyQt6
"""

THEME = {
    "colors": {
        "bg_primary": "#0D1117",
        "bg_secondary": "#161B22",
        "bg_tertiary": "#21262D",
        "bg_hover": "#30363D",
        "bg_active": "#1F6FEB22",
        "accent": "#00D4FF",
        "accent_dim": "#00D4FF44",
        "accent_glow": "#00D4FF11",
        "success": "#3FB950",
        "warning": "#D29922",
        "error": "#F85149",
        "text_primary": "#E6EDF3",
        "text_secondary": "#8B949E",
        "text_muted": "#484F58",
        "border": "#30363D",
        "border_light": "#21262D",
        "glass_bg": "#161B22CC",
        "glass_border": "#30363D88",
    },
    "fonts": {
        "family": "Segoe UI",
        "size": 14,
        "size_small": 12,
        "size_large": 16,
        "size_title": 20,
        "mono": "Cascadia Code",
    },
    "spacing": {
        "padding": 12,
        "margin": 8,
        "gap": 10,
        "radius": 10,
        "radius_small": 6,
        "radius_large": 16,
    },
    "animations": {
        "duration": 200,
        "hover_duration": 100,
    },
}

C = THEME["colors"]
F = THEME["fonts"]
S = THEME["spacing"]


def get_stylesheet() -> str:
    """Generate the complete stylesheet for NEXUS."""
    return f"""
    QMainWindow, QWidget {{
        background-color: {C['bg_primary']};
        color: {C['text_primary']};
        font-family: '{F['family']}';
        font-size: {F['size']}px;
    }}

    QLabel {{
        color: {C['text_primary']};
        background: transparent;
    }}

    QLabel#muted {{
        color: {C['text_muted']};
    }}

    QLabel#secondary {{
        color: {C['text_secondary']};
    }}

    QLabel#accent {{
        color: {C['accent']};
        font-weight: bold;
    }}

    QPushButton {{
        background-color: {C['bg_tertiary']};
        color: {C['text_primary']};
        border: 1px solid {C['border']};
        border-radius: {S['radius_small']}px;
        padding: 8px 16px;
        font-family: '{F['family']}';
        font-size: {F['size_small']}px;
    }}

    QPushButton:hover {{
        background-color: {C['bg_hover']};
        border-color: {C['accent']};
    }}

    QPushButton:pressed {{
        background-color: {C['accent_dim']};
    }}

    QPushButton#accent_button {{
        background-color: {C['accent']};
        color: {C['bg_primary']};
        border: none;
        font-weight: bold;
    }}

    QPushButton#accent_button:hover {{
        background-color: #00B8E6;
    }}

    QPushButton#sidebar_button {{
        background: transparent;
        border: none;
        border-left: 3px solid transparent;
        text-align: left;
        padding: 10px 16px;
        font-size: {F['size']}px;
    }}

    QPushButton#sidebar_button:hover {{
        background-color: {C['bg_hover']};
        border-left-color: {C['accent_dim']};
    }}

    QPushButton#sidebar_button:checked {{
        background-color: {C['bg_active']};
        border-left-color: {C['accent']};
        color: {C['accent']};
    }}

    QLineEdit, QTextEdit, QPlainTextEdit {{
        background-color: {C['bg_secondary']};
        color: {C['text_primary']};
        border: 1px solid {C['border']};
        border-radius: {S['radius_small']}px;
        padding: 8px 12px;
        font-family: '{F['family']}';
        font-size: {F['size']}px;
        selection-background-color: {C['accent_dim']};
    }}

    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
        border-color: {C['accent']};
    }}

    QScrollArea {{
        border: none;
        background-color: transparent;
    }}

    QScrollBar:vertical {{
        background-color: {C['bg_secondary']};
        width: 8px;
        border-radius: 4px;
    }}

    QScrollBar::handle:vertical {{
        background-color: {C['bg_tertiary']};
        border-radius: 4px;
        min-height: 30px;
    }}

    QScrollBar::handle:vertical:hover {{
        background-color: {C['bg_hover']};
    }}

    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}

    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
        background: none;
    }}

    QScrollBar:horizontal {{
        background-color: {C['bg_secondary']};
        height: 8px;
        border-radius: 4px;
    }}

    QScrollBar::handle:horizontal {{
        background-color: {C['bg_tertiary']};
        border-radius: 4px;
        min-width: 30px;
    }}

    QFrame#glass_panel {{
        background-color: {C['glass_bg']};
        border: 1px solid {C['glass_border']};
        border-radius: {S['radius']}px;
    }}

    QFrame#separator {{
        background-color: {C['border']};
        max-height: 1px;
        min-height: 1px;
    }}

    QFrame#sidebar {{
        background-color: {C['bg_secondary']};
        border-right: 1px solid {C['border']};
    }}

    QFrame#task_panel {{
        background-color: {C['bg_secondary']};
        border-left: 1px solid {C['border']};
    }}

    QFrame#chat_area {{
        background-color: {C['bg_primary']};
    }}

    QFrame#message_user {{
        background-color: {C['bg_tertiary']};
        border-radius: {S['radius']}px;
        padding: 12px;
    }}

    QFrame#message_assistant {{
        background-color: {C['bg_secondary']};
        border: 1px solid {C['border']};
        border-radius: {S['radius']}px;
        padding: 12px;
    }}

    QProgressBar {{
        background-color: {C['bg_tertiary']};
        border: none;
        border-radius: 4px;
        height: 6px;
        text-align: center;
    }}

    QProgressBar::chunk {{
        background-color: {C['accent']};
        border-radius: 4px;
    }}

    QTabWidget::pane {{
        border: 1px solid {C['border']};
        border-radius: {S['radius_small']}px;
        background-color: {C['bg_secondary']};
    }}

    QTabBar::tab {{
        background-color: {C['bg_tertiary']};
        color: {C['text_secondary']};
        padding: 8px 16px;
        border-top-left-radius: {S['radius_small']}px;
        border-top-right-radius: {S['radius_small']}px;
    }}

    QTabBar::tab:selected {{
        background-color: {C['bg_secondary']};
        color: {C['accent']};
    }}

    QTabBar::tab:hover {{
        background-color: {C['bg_hover']};
    }}

    QListWidget {{
        background-color: {C['bg_secondary']};
        border: 1px solid {C['border']};
        border-radius: {S['radius_small']}px;
    }}

    QListWidget::item {{
        padding: 8px;
        border-bottom: 1px solid {C['border_light']};
    }}

    QListWidget::item:selected {{
        background-color: {C['accent_dim']};
        color: {C['accent']};
    }}

    QListWidget::item:hover {{
        background-color: {C['bg_hover']};
    }}

    QSplitter::handle {{
        background-color: {C['border']};
    }}

    QSplitter::handle:horizontal {{
        width: 1px;
    }}

    QSplitter::handle:vertical {{
        height: 1px;
    }}

    QToolTip {{
        background-color: {C['bg_tertiary']};
        color: {C['text_primary']};
        border: 1px solid {C['border']};
        border-radius: {S['radius_small']}px;
        padding: 6px;
    }}

    QStatusBar {{
        background-color: {C['bg_secondary']};
        color: {C['text_secondary']};
        border-top: 1px solid {C['border']};
    }}
    """
