import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path


class Logger:
    """Centralized logging system for NEXUS."""

    _instance = None
    _logger: logging.Logger = None
    _console_handler = None
    _log_level = "INFO"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._logger is None:
            self._setup_logger()

    def _setup_logger(self):
        from core.config import Config

        config = Config()
        self._log_level = config.get("logging.level", "INFO")
        log_file = config.get("logging.file", "logs/nexus.log")
        max_size = config.get("logging.max_size_mb", 10) * 1024 * 1024
        backup_count = config.get("logging.backup_count", 5)

        log_path = Path(__file__).parent.parent / log_file
        os.makedirs(os.path.dirname(log_path), exist_ok=True)

        self._logger = logging.getLogger("NEXUS")
        self._logger.setLevel(logging.DEBUG)
        self._logger.propagate = False

        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        file_handler = RotatingFileHandler(
            log_path, maxBytes=max_size, backupCount=backup_count
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        self._logger.addHandler(file_handler)

        self._console_handler = logging.StreamHandler()
        self._console_handler.setFormatter(formatter)
        self._console_handler.setLevel(getattr(logging, self._log_level))
        self._logger.addHandler(self._console_handler)

    def set_mode(self, mode: str):
        """Set logging mode: normal, verbose, or debug."""
        if self._console_handler is None:
            return

        if mode == "normal":
            self._console_handler.setLevel(logging.WARNING)
        elif mode == "verbose":
            self._console_handler.setLevel(logging.INFO)
        elif mode == "debug":
            self._console_handler.setLevel(logging.DEBUG)

    def suppress_console(self):
        """Suppress all console output (logs still go to file)."""
        if self._console_handler:
            self._console_handler.setLevel(logging.CRITICAL + 1)

    def enable_console(self, level: str = "INFO"):
        """Enable console output at the specified level."""
        if self._console_handler:
            self._console_handler.setLevel(getattr(logging, level, logging.INFO))

    def get_logger(self, name: str) -> logging.Logger:
        return self._logger.getChild(name)

    @property
    def logger(self) -> logging.Logger:
        return self._logger
