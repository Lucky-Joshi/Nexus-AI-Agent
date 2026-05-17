import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path


class Logger:
    """Centralized logging system for NEXUS."""

    _instance = None
    _logger: logging.Logger = None

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
        log_level = config.get("logging.level", "INFO")
        log_file = config.get("logging.file", "logs/nexus.log")
        max_size = config.get("logging.max_size_mb", 10) * 1024 * 1024
        backup_count = config.get("logging.backup_count", 5)

        log_path = Path(__file__).parent.parent / log_file
        os.makedirs(os.path.dirname(log_path), exist_ok=True)

        self._logger = logging.getLogger("NEXUS")
        self._logger.setLevel(getattr(logging, log_level))

        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        file_handler = RotatingFileHandler(
            log_path, maxBytes=max_size, backupCount=backup_count
        )
        file_handler.setFormatter(formatter)
        self._logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self._logger.addHandler(console_handler)

    def get_logger(self, name: str) -> logging.Logger:
        return self._logger.getChild(name)

    @property
    def logger(self) -> logging.Logger:
        return self._logger
