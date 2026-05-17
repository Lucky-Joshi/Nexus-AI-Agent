"""
NEXUS - Agent Communication Bus
Event logging system with persistence, filtering, analytics, and real-time streaming.
"""

import time
import threading
from typing import Any, Callable, Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict, deque

from core.logger import Logger
from core.config import Config
from .models import EventLogEntry, BusMessage
from .storage import BusStorage


class EventLogger:
    """
    Comprehensive event logging system for the communication bus.
    Provides persistent event tracking, filtering, analytics,
    real-time streaming, and automated log rotation.
    """

    def __init__(
        self,
        storage: Optional[BusStorage] = None,
        max_memory_logs: int = 5000,
        auto_cleanup_hours: int = 24,
    ):
        self.logger = Logger().get_logger("EventLogger")
        self.config = Config()
        self.storage = storage or BusStorage()

        self._memory_log: deque = deque(maxlen=max_memory_logs)
        self._memory_log_lock = threading.Lock()

        self._stream_listeners: List[Callable] = []
        self._stream_lock = threading.Lock()

        self._event_counts: Dict[str, int] = defaultdict(int)
        self._agent_counts: Dict[str, int] = defaultdict(int)
        self._error_counts: Dict[str, int] = defaultdict(int)
        self._counts_lock = threading.Lock()

        self._start_time = time.time()
        self._total_logged = 0

        self._cleanup_thread = threading.Thread(
            target=self._cleanup_loop, daemon=True, name="EventLoggerCleanup"
        )
        self._cleanup_interval = auto_cleanup_hours * 3600
        self._running = True
        self._cleanup_thread.start()

        self.logger.info(
            f"EventLogger initialized (max_memory={max_memory_logs}, "
            f"cleanup_interval={auto_cleanup_hours}h)"
        )

    def log(
        self,
        event_type: str,
        event_name: str,
        source_agent: str,
        target_agent: str = "",
        message_id: str = "",
        details: Optional[Dict[str, Any]] = None,
        success: bool = True,
        error_message: str = "",
        duration_ms: float = 0.0,
    ) -> str:
        """
        Log an event. Returns the log entry ID.
        """
        entry = EventLogEntry(
            event_type=event_type,
            event_name=event_name,
            source_agent=source_agent,
            target_agent=target_agent,
            message_id=message_id,
            details=details or {},
            success=success,
            error_message=error_message,
            duration_ms=duration_ms,
        )

        self._memory_log.append(entry)
        self.storage.log_event(entry.to_dict())

        with self._counts_lock:
            self._event_counts[event_type] += 1
            self._agent_counts[source_agent] += 1
            if target_agent:
                self._agent_counts[target_agent] += 1
            if not success:
                self._error_counts[event_name] += 1

        self._total_logged += 1

        self._notify_stream_listeners(entry)

        self.logger.debug(f"Event logged: {event_type}/{event_name} ({source_agent} -> {target_agent})")
        return entry.id

    def log_message(self, message: BusMessage, event_type: str = "message", duration_ms: float = 0.0):
        """Log a bus message event."""
        return self.log(
            event_type=event_type,
            event_name=message.event,
            source_agent=message.sender,
            target_agent=", ".join(message.recipients) if message.recipients else "",
            message_id=message.id,
            details={
                "message_type": message.message_type.value,
                "priority": message.priority.value,
                "payload_keys": list(message.payload.keys()),
            },
            success=message.delivery_status.value in ("delivered", "acknowledged"),
            error_message=message.metadata.get("error", ""),
            duration_ms=duration_ms,
        )

    def log_agent_event(
        self,
        event_name: str,
        source_agent: str,
        target_agent: str = "",
        details: Optional[Dict[str, Any]] = None,
        success: bool = True,
        error_message: str = "",
    ) -> str:
        """Log an agent-specific event."""
        return self.log(
            event_type="agent_event",
            event_name=event_name,
            source_agent=source_agent,
            target_agent=target_agent,
            details=details,
            success=success,
            error_message=error_message,
        )

    def log_system_event(
        self,
        event_name: str,
        details: Optional[Dict[str, Any]] = None,
        success: bool = True,
        error_message: str = "",
    ) -> str:
        """Log a system-level event."""
        return self.log(
            event_type="system_event",
            event_name=event_name,
            source_agent="system",
            details=details,
            success=success,
            error_message=error_message,
        )

    def log_error(
        self,
        event_name: str,
        source_agent: str,
        error_message: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Log an error event."""
        return self.log(
            event_type="error",
            event_name=event_name,
            source_agent=source_agent,
            details=details,
            success=False,
            error_message=error_message,
        )

    def add_stream_listener(self, callback: Callable, event_types: Optional[List[str]] = None):
        """
        Add a listener for real-time event streaming.
        Callback receives EventLogEntry.
        """
        listener = {"callback": callback, "event_types": event_types}
        with self._stream_lock:
            self._stream_listeners.append(listener)
        self.logger.debug(f"Stream listener added (filter: {event_types})")

    def remove_stream_listener(self, callback: Callable):
        """Remove a stream listener."""
        with self._stream_lock:
            self._stream_listeners = [
                l for l in self._stream_listeners if l["callback"] != callback
            ]

    def _notify_stream_listeners(self, entry: EventLogEntry):
        """Notify all stream listeners of a new event."""
        with self._stream_lock:
            for listener in self._stream_listeners:
                try:
                    if listener["event_types"] is None or entry.event_type in listener["event_types"]:
                        listener["callback"](entry)
                except Exception as e:
                    self.logger.error(f"Stream listener error: {e}")

    def get_logs(
        self,
        event_type: Optional[str] = None,
        source_agent: Optional[str] = None,
        target_agent: Optional[str] = None,
        event_name: Optional[str] = None,
        success_only: bool = False,
        error_only: bool = False,
        limit: int = 100,
        hours: int = 24,
    ) -> List[Dict[str, Any]]:
        """Retrieve event logs with comprehensive filtering."""
        return self.storage.get_event_logs(
            event_type=event_type,
            source_agent=source_agent,
            limit=limit,
            hours=hours,
        )

    def get_memory_logs(
        self,
        event_type: Optional[str] = None,
        source_agent: Optional[str] = None,
        limit: int = 100,
    ) -> List[EventLogEntry]:
        """Get logs from in-memory buffer."""
        with self._memory_log_lock:
            logs = list(self._memory_log)

        if event_type:
            logs = [l for l in logs if l.event_type == event_type]
        if source_agent:
            logs = [l for l in logs if l.source_agent == source_agent]

        return logs[-limit:]

    def get_agent_activity(self, agent_name: str, hours: int = 24) -> Dict[str, Any]:
        """Get activity summary for a specific agent."""
        logs = self.get_logs(source_agent=agent_name, hours=hours, limit=1000)

        event_types = defaultdict(int)
        events = defaultdict(int)
        errors = 0
        total_duration = 0.0
        duration_count = 0

        for log in logs:
            event_types[log["event_type"]] += 1
            events[log["event_name"]] += 1
            if not log["success"]:
                errors += 1
            if log["duration_ms"] > 0:
                total_duration += log["duration_ms"]
                duration_count += 1

        return {
            "agent": agent_name,
            "total_events": len(logs),
            "event_types": dict(event_types),
            "top_events": dict(sorted(events.items(), key=lambda x: x[1], reverse=True)[:10]),
            "errors": errors,
            "error_rate": round(errors / len(logs) * 100, 2) if logs else 0,
            "avg_duration_ms": round(total_duration / duration_count, 2) if duration_count > 0 else 0,
            "period_hours": hours,
        }

    def get_event_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get a summary of all events in the specified period."""
        stats = self.storage.get_event_stats(hours=hours)

        with self._counts_lock:
            return {
                **stats,
                "total_logged": self._total_logged,
                "uptime_seconds": round(time.time() - self._start_time, 2),
                "logs_per_minute": round(
                    self._total_logged / ((time.time() - self._start_time) / 60), 2
                ) if (time.time() - self._start_time) > 0 else 0,
            }

    def get_error_report(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get all error events in the specified period."""
        logs = self.get_logs(hours=hours, error_only=True, limit=500)
        return [log for log in logs if not log["success"]]

    def get_communication_flow(
        self, hours: int = 24, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get the communication flow between agents."""
        logs = self.get_logs(hours=hours, limit=limit * 10)

        flows = defaultdict(int)
        for log in logs:
            if log["source_agent"] and log["target_agent"]:
                key = f"{log['source_agent']} -> {log['target_agent']}"
                flows[key] += 1

        sorted_flows = sorted(flows.items(), key=lambda x: x[1], reverse=True)
        return [
            {"flow": flow, "count": count}
            for flow, count in sorted_flows[:limit]
        ]

    def get_timeline(self, hours: int = 24, granularity_minutes: int = 5) -> List[Dict[str, Any]]:
        """Get event timeline with specified granularity."""
        logs = self.get_logs(hours=hours, limit=10000)

        now = datetime.now()
        start = now - timedelta(hours=hours)
        interval = timedelta(minutes=granularity_minutes)

        timeline = []
        current = start

        while current <= now:
            window_end = current + interval
            count = 0
            errors = 0

            for log in logs:
                log_time = datetime.fromisoformat(log["timestamp"])
                if current <= log_time < window_end:
                    count += 1
                    if not log["success"]:
                        errors += 1

            timeline.append({
                "timestamp": current.isoformat(),
                "count": count,
                "errors": errors,
            })
            current = window_end

        return timeline

    def _cleanup_loop(self):
        """Background loop that cleans up old logs."""
        while self._running:
            try:
                time.sleep(self._cleanup_interval)
                retention_days = self.config.get("communication_bus.log_retention_days", 7)
                deleted = self.storage.cleanup_old_logs(days=retention_days)
                if deleted > 0:
                    self.logger.info(f"Cleaned up {deleted} old event logs")
            except Exception as e:
                self.logger.error(f"Event log cleanup error: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get event logger statistics."""
        with self._counts_lock:
            return {
                "total_logged": self._total_logged,
                "event_type_counts": dict(self._event_counts),
                "agent_counts": dict(self._agent_counts),
                "error_counts": dict(self._error_counts),
                "memory_log_size": len(self._memory_log),
                "stream_listeners": len(self._stream_listeners),
                "uptime_seconds": round(time.time() - self._start_time, 2),
            }

    def shutdown(self):
        """Shutdown the event logger."""
        self.logger.info("Shutting down EventLogger...")
        self._running = False
        self.logger.info("EventLogger shutdown complete")
