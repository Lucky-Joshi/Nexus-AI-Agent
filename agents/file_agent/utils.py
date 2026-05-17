"""
Utility functions for the File Agent.
Path resolution, formatting, validation, and cross-platform helpers.
"""

import os
import platform
from pathlib import Path
from typing import Optional


class PathResolver:
    """
    Resolves file paths across common locations.
    Handles ~, environment variables, relative paths, and absolute paths.
    """

    def __init__(self):
        self._home = Path.home()
        self._search_paths = [
            self._home,
            self._home / "Downloads",
            self._home / "Desktop",
            self._home / "Documents",
            self._home / "OneDrive" / "Documents",
            self._home / "Pictures",
            self._home / "Videos",
            Path.cwd(),
        ]

    def resolve(self, path_str: str) -> Optional[Path]:
        """Resolve a path string to an actual Path object."""
        if not path_str or not path_str.strip():
            return None

        cleaned = path_str.strip()

        # Expand environment variables (e.g. %USERPROFILE%)
        cleaned = os.path.expandvars(cleaned)

        # Expand user home (e.g. ~ or ~/Desktop)
        cleaned = os.path.expanduser(cleaned)

        p = Path(cleaned)

        # If absolute and exists, return it
        if p.is_absolute() and p.exists():
            return p.resolve()

        # Search across known locations
        for base in self._search_paths:
            candidate = base / cleaned
            if candidate.exists():
                return candidate.resolve()

        # Return as-is for creation operations
        return p

    def resolve_or_create(self, path_str: str) -> Path:
        """Resolve a path, or return the target for creation."""
        resolved = self.resolve(path_str)
        if resolved:
            return resolved
        return self._home / path_str.strip()

    @property
    def home(self) -> Path:
        return self._home

    @property
    def downloads(self) -> Path:
        return self._home / "Downloads"

    @property
    def desktop(self) -> Path:
        return self._home / "Desktop"

    @property
    def documents(self) -> Path:
        return self._home / "OneDrive" / "Documents" if (self._home / "OneDrive" / "Documents").exists() else self._home / "Documents"

    @property
    def pictures(self) -> Path:
        return self._home / "Pictures"

    @property
    def videos(self) -> Path:
        return self._home / "Videos"

    @property
    def onedrive(self) -> Path:
        return self._home / "OneDrive"

    def get_folder_path(self, folder_name: str) -> Optional[Path]:
        """Get path for common folder shortcuts."""
        folder_map = {
            "desktop": self.desktop,
            "downloads": self.downloads,
            "documents": self.documents,
            "pictures": self.pictures,
            "videos": self.videos,
            "onedrive": self.onedrive,
            "home": self._home,
        }
        return folder_map.get(folder_name.lower().strip())

    def get_all_search_paths(self) -> list:
        return [str(p) for p in self._search_paths]


def format_size(size_bytes: int) -> str:
    """Format byte size to human-readable string."""
    if size_bytes < 1024:
        return f"{size_bytes}B"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.1f}KB"
    elif size_bytes < 1024 ** 3:
        return f"{size_bytes / (1024 ** 2):.1f}MB"
    else:
        return f"{size_bytes / (1024 ** 3):.2f}GB"


def format_path(path: Path) -> str:
    """Format a path for display, shortening home directory."""
    home = Path.home()
    try:
        return str(path.relative_to(home)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def is_safe_path(path: Path, allowed_roots: Optional[list] = None) -> bool:
    """Check if a path is within allowed roots to prevent traversal attacks."""
    if allowed_roots is None:
        allowed_roots = [Path.home()]

    try:
        resolved = path.resolve()
        return any(resolved.is_relative_to(root.resolve()) for root in allowed_roots)
    except (ValueError, OSError):
        return False


def get_file_type(path: Path) -> str:
    """Determine file category by extension."""
    ext = path.suffix.lower()

    type_map = {
        "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".ico", ".tiff"],
        "Documents": [".pdf", ".doc", ".docx", ".txt", ".xls", ".xlsx", ".ppt", ".pptx", ".odt", ".rtf", ".csv"],
        "Archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz"],
        "Installers": [".exe", ".msi", ".dmg", ".pkg", ".deb", ".rpm"],
        "Code": [".py", ".js", ".ts", ".html", ".css", ".json", ".xml", ".yaml", ".yml", ".java", ".cpp", ".c", ".h", ".rb", ".go", ".rs"],
        "Audio": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a"],
        "Video": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm"],
    }

    for category, extensions in type_map.items():
        if ext in extensions:
            return category

    return "Other"


def get_platform() -> str:
    """Return normalized platform name."""
    system = platform.system()
    if system == "Windows":
        return "windows"
    elif system == "Darwin":
        return "macos"
    return "linux"


def get_default_browser() -> str:
    """Return default browser command for the platform."""
    platform_name = get_platform()
    browsers = {
        "windows": "msedge.exe",
        "macos": "open",
        "linux": "firefox",
    }
    return browsers.get(platform_name, "firefox")


def extract_filename(command: str, prefixes: list, suffixes: list) -> str:
    """Extract a filename from a command string using longest-prefix-first matching."""
    text = command.lower().strip()

    sorted_prefixes = sorted(prefixes, key=len, reverse=True)
    for prefix in sorted_prefixes:
        if text.startswith(prefix):
            text = text[len(prefix):]
            break

    sorted_suffixes = sorted(suffixes, key=len, reverse=True)
    for suffix in sorted_suffixes:
        if text.endswith(suffix):
            text = text[: -len(suffix)]

    return text.strip()
