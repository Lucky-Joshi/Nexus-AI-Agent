"""
NEXUS - Agent Communication Bus
Message broker with priority queue, fault-tolerant delivery, retry logic,
dead letter queue, and message tracking.
"""

import time
import heapq
import threading
from typing import Any, Callable, Dict, List, Optional, Tuple
from queue import PriorityQueue, Empty
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, Future

from core.logger import Logger
from core.config import Config
from .models import (
    BusMessage, MessagePriority, MessageType, DeliveryStatus,
)
from .storage import BusStorage


class DeadLetterQueue:
    """Stores messages that failed delivery after max retries."""

    def __init__(self, max_size: int = 1000):
        self._messages: List[BusMessage] = []
        self._lock = threading.Lock()
        self._max_size = max_size

    def add(self, message: BusMessage, reason: str = ""):
        with self._lock:
            message.metadata["dlq_reason"] = reason
            message.metadata["dlq_timestamp"] = time.time()
            self._messages.append(message)
            if len(self._messages) > self._max_size:
                self._messages.pop(0)

    def get_all(self) -> List[BusMessage]:
        with self._lock:
            return list(self._messages)

    def retry_message(self, message_id: str) -> Optional[BusMessage]:
        with self._lock:
            for i, msg in enumerate(self._messages):
                if msg.id == message_id:
                    msg.retry_count = 0
                    msg.delivery_status = DeliveryStatus.PENDING
                    return self._messages.pop(i)
        return None

    def purge(self) -> int:
        with self._lock:
            count = len(self._messages)
            self._messages.clear()
            return count

    @property
    def size(self) -> int:
        with self._lock:
            return len(self._messages)


class MessageTracker:
    """Tracks message delivery status and timing."""

    def __init__(self):
        self._messages: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def track(self, message: BusMessage):
        with self._lock:
            self._messages[message.id] = {
                "message": message,
                "status": message.delivery_status.value,
                "sent_at": time.time(),
                "delivered_at": None,
                "acknowledged_at": None,
                "delivery_time_ms": None,
                "retry_count": message.retry_count,
            }

    def update_status(self, message_id: str, status: DeliveryStatus):
        with self._lock:
            if message_id in self._messages:
                entry = self._messages[message_id]
                entry["status"] = status.value
                now = time.time()

                if status == DeliveryStatus.DELIVERED and not entry["delivered_at"]:
                    entry["delivered_at"] = now
                    entry["delivery_time_ms"] = (now - entry["sent_at"]) * 1000
                elif status == DeliveryStatus.ACKNOWLEDGED and not entry["acknowledged_at"]:
                    entry["acknowledged_at"] = now

                entry["retry_count"] = entry["message"].retry_count

    def get_message_info(self, message_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            return self._messages.get(message_id)

    def get_messages_by_status(self, status: DeliveryStatus) -> List[Dict[str, Any]]:
        with self._lock:
            return [
                entry for entry in self._messages.values()
                if entry["status"] == status.value
            ]

    def get_pending_messages(self, older_than_seconds: float = 60) -> List[BusMessage]:
        with self._lock:
            now = time.time()
            pending = []
            for entry in self._messages.values():
                if entry["status"] in (DeliveryStatus.PENDING.value, DeliveryStatus.QUEUED.value, DeliveryStatus.RETRYING.value):
                    if now - entry["sent_at"] > older_than_seconds:
                        pending.append(entry["message"])
            return pending

    def cleanup_resolved(self, older_than_seconds: float = 300):
        with self._lock:
            now = time.time()
            to_remove = []
            for msg_id, entry in self._messages.items():
                if entry["status"] in (DeliveryStatus.ACKNOWLEDGED.value, DeliveryStatus.DELIVERED.value, DeliveryStatus.FAILED.value, DeliveryStatus.EXPIRED.value):
                    if entry["sent_at"] and (now - entry["sent_at"]) > older_than_seconds:
                        to_remove.append(msg_id)
            for msg_id in to_remove:
                del self._messages[msg_id]

    @property
    def total_tracked(self) -> int:
        with self._lock:
            return len(self._messages)


class MessageBroker:
    """
    Priority-based message broker with fault-tolerant delivery.
    Handles message queuing, routing, retry logic, dead letter queue,
    and delivery tracking.
    """

    def __init__(
        self,
        storage: Optional[BusStorage] = None,
        max_workers: int = 8,
        max_queue_size: int = 10000,
        default_ttl: int = 300,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ):
        self.logger = Logger().get_logger("MessageBroker")
        self.config = Config()
        self.storage = storage or BusStorage()

        self._queue: PriorityQueue = PriorityQueue(maxsize=max_queue_size)
        self._max_queue_size = max_queue_size
        self._default_ttl = default_ttl
        self._max_retries = max_retries
        self._retry_delay = retry_delay

        self._executor = ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix="MessageBrokerWorker",
        )
        self._running = True

        self._dead_letter_queue = DeadLetterQueue()
        self._tracker = MessageTracker()

        self._handlers: Dict[str, List[Callable]] = defaultdict(list)
        self._handler_lock = threading.Lock()

        self._stats: Dict[str, int] = {
            "total_enqueued": 0,
            "total_dequeued": 0,
            "total_delivered": 0,
            "total_failed": 0,
            "total_retried": 0,
            "total_expired": 0,
            "total_dlq": 0,
        }
        self._stats_lock = threading.Lock()

        self._processor_thread = threading.Thread(
            target=self._process_loop, daemon=True, name="MessageBrokerProcessor"
        )
        self._processor_thread.start()

        self._retry_thread = threading.Thread(
            target=self._retry_loop, daemon=True, name="MessageBrokerRetry"
        )
        self._retry_thread.start()

        self._cleanup_thread = threading.Thread(
            target=self._cleanup_loop, daemon=True, name="MessageBrokerCleanup"
        )
        self._cleanup_thread.start()

        self.logger.info(
            f"MessageBroker initialized (workers={max_workers}, "
            f"max_queue={max_queue_size}, ttl={default_ttl}, retries={max_retries})"
        )

    def register_handler(self, event_pattern: str, handler: Callable):
        """Register a handler for messages matching an event pattern."""
        with self._handler_lock:
            self._handlers[event_pattern].append(handler)
        self.logger.debug(f"Handler registered for: {event_pattern}")

    def unregister_handler(self, event_pattern: str, handler: Callable) -> bool:
        """Remove a handler for an event pattern."""
        with self._handler_lock:
            if event_pattern in self._handlers:
                try:
                    self._handlers[event_pattern].remove(handler)
                    if not self._handlers[event_pattern]:
                        del self._handlers[event_pattern]
                    return True
                except ValueError:
                    pass
        return False

    def enqueue(
        self,
        message: BusMessage,
    ) -> bool:
        """
        Add a message to the priority queue.
        Returns False if queue is full.
        """
        if message.ttl <= 0:
            message.ttl = self._default_ttl
        if message.max_retries <= 0:
            message.max_retries = self._max_retries

        try:
            message.delivery_status = DeliveryStatus.QUEUED
            priority_tuple = (message.priority.value, message.timestamp, message)
            self._queue.put_nowait(priority_tuple)

            self._tracker.track(message)
            self.storage.save_message(message.to_dict())

            with self._stats_lock:
                self._stats["total_enqueued"] += 1

            self.logger.debug(f"Enqueued: {message.event} (priority={message.priority.name}, sender={message.sender})")
            return True

        except Exception as e:
            self.logger.error(f"Failed to enqueue message: {e}")
            return False

    def send_request(
        self,
        sender: str,
        recipient: str,
        event: str,
        payload: Dict[str, Any],
        priority: MessagePriority = MessagePriority.NORMAL,
        timeout: int = 30,
    ) -> str:
        """Send a request message expecting a response."""
        import uuid
        correlation_id = str(uuid.uuid4())

        message = BusMessage(
            sender=sender,
            recipients=[recipient],
            message_type=MessageType.REQUEST,
            priority=priority,
            event=event,
            payload=payload,
            correlation_id=correlation_id,
            ttl=timeout,
            requires_ack=True,
        )

        self.enqueue(message)
        return correlation_id

    def send_response(
        self,
        sender: str,
        reply_to: str,
        correlation_id: str,
        payload: Dict[str, Any],
        success: bool = True,
        error: str = "",
    ):
        """Send a response to a request message."""
        message = BusMessage(
            sender=sender,
            recipients=[reply_to],
            message_type=MessageType.RESPONSE,
            priority=MessagePriority.HIGH,
            event=f"response:{correlation_id}",
            payload={**payload, "success": success, "error": error},
            correlation_id=correlation_id,
        )

        self.enqueue(message)

    def _process_loop(self):
        """Main processing loop for the message queue."""
        while self._running:
            try:
                priority, timestamp, message = self._queue.get(timeout=0.1)

                if message.is_expired():
                    message.delivery_status = DeliveryStatus.EXPIRED
                    self.storage.update_message_status(message.id, DeliveryStatus.EXPIRED.value)
                    self._tracker.update_status(message.id, DeliveryStatus.EXPIRED)
                    with self._stats_lock:
                        self._stats["total_expired"] += 1
                    self._queue.task_done()
                    continue

                self._executor.submit(self._process_message, message)

            except Empty:
                continue
            except Exception as e:
                self.logger.error(f"Process loop error: {e}")

    def _process_message(self, message: BusMessage):
        """Process a single message through matching handlers."""
        message.delivery_status = DeliveryStatus.DELIVERED
        self._tracker.update_status(message.id, DeliveryStatus.DELIVERED)

        handlers = self._find_matching_handlers(message)

        if not handlers:
            self.logger.debug(f"No handlers for message: {message.event}")
            message.delivery_status = DeliveryStatus.ACKNOWLEDGED
            self._tracker.update_status(message.id, DeliveryStatus.ACKNOWLEDGED)
            self.storage.update_message_status(message.id, DeliveryStatus.ACKNOWLEDGED.value)
            with self._stats_lock:
                self._stats["total_delivered"] += 1
            return

        all_success = True
        for handler in handlers:
            try:
                handler(message)
            except Exception as e:
                all_success = False
                self.logger.error(f"Handler error for {message.event}: {e}")

        if all_success:
            message.delivery_status = DeliveryStatus.ACKNOWLEDGED
            self._tracker.update_status(message.id, DeliveryStatus.ACKNOWLEDGED)
            self.storage.update_message_status(message.id, DeliveryStatus.ACKNOWLEDGED.value)
            with self._stats_lock:
                self._stats["total_delivered"] += 1
        else:
            self._handle_delivery_failure(message)

        with self._stats_lock:
            self._stats["total_dequeued"] += 1

    def _find_matching_handlers(self, message: BusMessage) -> List[Callable]:
        """Find handlers that match the message event."""
        matching = []
        with self._handler_lock:
            for pattern, handlers in self._handlers.items():
                if pattern == "*" or pattern == message.event:
                    matching.extend(handlers)
                elif pattern.endswith(".*") and message.event.startswith(pattern[:-2]):
                    matching.extend(handlers)
                elif pattern.startswith("*.") and message.event.endswith(pattern[2:]):
                    matching.extend(handlers)
        return matching

    def _handle_delivery_failure(self, message: BusMessage):
        """Handle a message that failed delivery."""
        if message.retry_count < message.max_retries:
            message.retry_count += 1
            message.delivery_status = DeliveryStatus.RETRYING
            self._tracker.update_status(message.id, DeliveryStatus.RETRYING)
            self.storage.update_message_status(message.id, DeliveryStatus.RETRYING.value, message.retry_count)

            time.sleep(self._retry_delay * message.retry_count)

            try:
                priority_tuple = (message.priority.value, message.timestamp, message)
                self._queue.put_nowait(priority_tuple)
                with self._stats_lock:
                    self._stats["total_retried"] += 1
                self.logger.debug(f"Retrying message: {message.id} (attempt {message.retry_count})")
            except Exception:
                self._send_to_dlq(message, "Queue full on retry")
        else:
            self._send_to_dlq(message, "Max retries exceeded")

    def _send_to_dlq(self, message: BusMessage, reason: str):
        """Send a message to the dead letter queue."""
        message.delivery_status = DeliveryStatus.FAILED
        self._tracker.update_status(message.id, DeliveryStatus.FAILED)
        self.storage.update_message_status(message.id, DeliveryStatus.FAILED.value, message.retry_count)
        self._dead_letter_queue.add(message, reason)

        with self._stats_lock:
            self._stats["total_failed"] += 1
            self._stats["total_dlq"] += 1

        self.logger.warning(f"Message moved to DLQ: {message.id} (reason: {reason})")

    def _retry_loop(self):
        """Background loop that retries stuck pending messages."""
        while self._running:
            try:
                time.sleep(30)
                pending = self._tracker.get_pending_messages(older_than_seconds=60)
                for message in pending:
                    if message.retry_count < message.max_retries:
                        message.retry_count += 1
                        message.delivery_status = DeliveryStatus.RETRYING
                        try:
                            priority_tuple = (message.priority.value, message.timestamp, message)
                            self._queue.put_nowait(priority_tuple)
                            with self._stats_lock:
                                self._stats["total_retried"] += 1
                            self.logger.info(f"Auto-retried stuck message: {message.id}")
                        except Exception:
                            self._send_to_dlq(message, "Stuck message retry failed")
                    else:
                        self._send_to_dlq(message, "Stuck message max retries")
            except Exception as e:
                self.logger.error(f"Retry loop error: {e}")

    def _cleanup_loop(self):
        """Background loop that cleans up resolved message tracking."""
        while self._running:
            try:
                time.sleep(120)
                self._tracker.cleanup_resolved(older_than_seconds=300)

                expired_count = self.storage.delete_expired_messages()
                if expired_count > 0:
                    with self._stats_lock:
                        self._stats["total_expired"] += expired_count

            except Exception as e:
                self.logger.error(f"Cleanup loop error: {e}")

    def get_dlq_messages(self) -> List[BusMessage]:
        """Get all messages in the dead letter queue."""
        return self._dead_letter_queue.get_all()

    def retry_dlq_message(self, message_id: str) -> bool:
        """Retry a message from the dead letter queue."""
        message = self._dead_letter_queue.retry_message(message_id)
        if message:
            return self.enqueue(message)
        return False

    def purge_dlq(self) -> int:
        """Purge all messages from the dead letter queue."""
        count = self._dead_letter_queue.purge()
        with self._stats_lock:
            self._stats["total_dlq"] -= count
        return count

    def get_message_status(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a tracked message."""
        return self._tracker.get_message_info(message_id)

    def get_stats(self) -> Dict[str, Any]:
        """Get broker statistics."""
        with self._stats_lock:
            stats = dict(self._stats)
        stats["queue_size"] = self._queue.qsize()
        stats["dlq_size"] = self._dead_letter_queue.size
        stats["tracked_messages"] = self._tracker.total_tracked
        return stats

    def shutdown(self, wait: bool = True):
        """Shutdown the message broker."""
        self.logger.info("Shutting down MessageBroker...")
        self._running = False

        if wait:
            self._queue.join()

        self._executor.shutdown(wait=wait)
        self.logger.info("MessageBroker shutdown complete")
