from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, Optional
from threading import Lock


class AgentStatus(Enum):
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"


class BaseAgent(ABC):
    """Abstract base class for all NEXUS agents."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self._status = AgentStatus.IDLE
        self._status_lock = Lock()

    @property
    def status(self) -> AgentStatus:
        with self._status_lock:
            return self._status

    @status.setter
    def status(self, value: AgentStatus):
        with self._status_lock:
            self._status = value

    @abstractmethod
    def execute(self, command: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a command and return result."""
        pass

    @abstractmethod
    def get_capabilities(self) -> list:
        """Return list of capabilities this agent supports."""
        pass

    def is_available(self) -> bool:
        return self.status == AgentStatus.IDLE

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "capabilities": self.get_capabilities(),
        }
