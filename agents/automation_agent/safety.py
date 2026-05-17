"""
Safety system for the Automation Agent.
Provides emergency stop, action validation, and execution guards.
"""

import time
import threading
from typing import Callable, Optional
from core.logger import Logger


class EmergencyStop:
    """Thread-safe emergency stop mechanism."""

    def __init__(self):
        self.logger = Logger().get_logger("EmergencyStop")
        self._stopped = False
        self._lock = threading.Lock()
        self._callbacks: list = []

    @property
    def is_stopped(self) -> bool:
        with self._lock:
            return self._stopped

    def trigger(self, reason: str = "User requested stop"):
        """Trigger emergency stop."""
        with self._lock:
            if not self._stopped:
                self._stopped = True
                self.logger.warning(f"EMERGENCY STOP triggered: {reason}")
                for callback in self._callbacks:
                    try:
                        callback(reason)
                    except Exception as e:
                        self.logger.error(f"Stop callback error: {e}")

    def reset(self):
        """Reset the emergency stop."""
        with self._lock:
            self._stopped = False
            self.logger.info("Emergency stop reset")

    def register_callback(self, callback: Callable):
        """Register a callback to run on emergency stop."""
        self._callbacks.append(callback)

    def check(self):
        """Check if stop is triggered. Raises StopExecution if so."""
        if self.is_stopped:
            raise StopExecution("Emergency stop triggered")


class StopExecution(Exception):
    """Raised when execution should be stopped."""
    pass


class SafetySystem:
    """Manages safety controls for automation operations."""

    def __init__(self, safety_delay: float = 0.5, confirm_destructive: bool = True, max_steps: int = 50):
        self.logger = Logger().get_logger("SafetySystem")
        self.safety_delay = safety_delay
        self.confirm_destructive = confirm_destructive
        self.max_steps = max_steps
        self.emergency_stop = EmergencyStop()
        self._step_count = 0
        self._lock = threading.Lock()

    def pre_execute(self, action_type: str, params: dict = None) -> bool:
        """Validate an action before execution. Returns True if safe."""
        if self.emergency_stop.is_stopped:
            return False

        if self._step_count >= self.max_steps:
            self.logger.warning(f"Max steps limit reached ({self.max_steps})")
            return False

        if action_type in ("delete_file", "kill_process", "format_drive"):
            if self.confirm_destructive:
                self.logger.info(f"Destructive action requested: {action_type}")

        return True

    def post_execute(self):
        """Called after each action. Applies safety delay and checks stop."""
        with self._lock:
            self._step_count += 1

        if self.safety_delay > 0:
            time.sleep(self.safety_delay)

        self.emergency_stop.check()

    def reset(self):
        """Reset safety system state."""
        with self._lock:
            self._step_count = 0
        self.emergency_stop.reset()

    @property
    def step_count(self) -> int:
        return self._step_count

    def is_safe_to_continue(self) -> bool:
        """Check if it's safe to continue execution."""
        return not self.emergency_stop.is_stopped and self._step_count < self.max_steps
