"""
Built-in workflow templates for the Automation Agent.
Predefined productivity modes: coding, study, work, and more.
"""

from .actions import Action
from .workflow_engine import Workflow


def get_coding_mode_workflow() -> Workflow:
    """Coding mode: opens VS Code, terminal, and sets up the workspace."""
    return Workflow(
        name="coding_mode",
        description="Opens VS Code, terminal, and prepares coding workspace",
        mode="productivity",
        tags=["coding", "development", "productivity"],
        steps=[
            Action.open_app("vscode", delay=2.0),
            Action.wait(seconds=2),
            Action.open_app("terminal", delay=1.5),
            Action.wait(seconds=1),
            Action.hotkey("winleft", "d"),
            Action.wait(seconds=0.5),
            Action.screenshot(delay=0.5),
        ],
    )


def get_study_mode_workflow() -> Workflow:
    """Study mode: opens browser, note-taking app, and organizes workspace."""
    return Workflow(
        name="study_mode",
        description="Opens browser for research and note-taking application",
        mode="productivity",
        tags=["study", "learning", "productivity"],
        steps=[
            Action.open_app("browser", delay=2.0),
            Action.wait(seconds=2),
            Action.open_app("notepad", delay=1.5),
            Action.wait(seconds=1),
            Action.hotkey("winleft", "left"),
            Action.wait(seconds=0.5),
            Action.hotkey("winleft", "right"),
            Action.wait(seconds=0.5),
            Action.screenshot(delay=0.5),
        ],
    )


def get_work_mode_workflow() -> Workflow:
    """Work mode: opens email, calendar, and communication apps."""
    return Workflow(
        name="work_mode",
        description="Opens email, calendar, and communication tools for work",
        mode="productivity",
        tags=["work", "office", "productivity"],
        steps=[
            Action.open_app("browser", delay=2.0),
            Action.wait(seconds=2),
            Action.open_app("notepad", delay=1.0),
            Action.wait(seconds=1),
            Action.screenshot(delay=0.5),
        ],
    )


def get_meeting_prep_workflow() -> Workflow:
    """Meeting prep: opens calendar, notes, and communication app."""
    return Workflow(
        name="meeting_prep",
        description="Prepares for meetings by opening calendar and notes",
        mode="productivity",
        tags=["meeting", "prep", "productivity"],
        steps=[
            Action.open_app("browser", delay=2.0),
            Action.wait(seconds=2),
            Action.open_app("notepad", delay=1.0),
            Action.wait(seconds=1),
            Action.screenshot(delay=0.5),
        ],
    )


def get_screen_capture_workflow() -> Workflow:
    """Screen capture: takes multiple screenshots with delays."""
    return Workflow(
        name="screen_capture",
        description="Takes multiple screenshots at intervals",
        mode="utility",
        tags=["screenshot", "capture", "utility"],
        steps=[
            Action.screenshot(delay=1.0),
            Action.wait(seconds=3),
            Action.screenshot(delay=1.0),
            Action.wait(seconds=3),
            Action.screenshot(delay=0.5),
        ],
    )


def get_cleanup_workflow() -> Workflow:
    """Cleanup: minimizes all windows and shows desktop."""
    return Workflow(
        name="cleanup",
        description="Minimizes all windows and shows desktop",
        mode="utility",
        tags=["cleanup", "desktop", "utility"],
        steps=[
            Action.hotkey("winleft", "d"),
            Action.wait(seconds=0.5),
        ],
    )


def get_presentation_mode_workflow() -> Workflow:
    """Presentation mode: opens browser in fullscreen."""
    return Workflow(
        name="presentation_mode",
        description="Opens browser and enters fullscreen for presentations",
        mode="productivity",
        tags=["presentation", "display", "productivity"],
        steps=[
            Action.open_app("browser", delay=2.0),
            Action.wait(seconds=2),
            Action.press_key("f11"),
            Action.wait(seconds=0.5),
        ],
    )


def get_builtin_workflows() -> list:
    """Return all built-in workflow templates."""
    return [
        get_coding_mode_workflow(),
        get_study_mode_workflow(),
        get_work_mode_workflow(),
        get_meeting_prep_workflow(),
        get_screen_capture_workflow(),
        get_cleanup_workflow(),
        get_presentation_mode_workflow(),
    ]
