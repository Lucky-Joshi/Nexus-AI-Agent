"""
NEXUS - Agent Communication Bus
Core event bus with publish/subscribe architecture, thread-safe event routing,
and async dispatching.
"""

import re
import time
import threading
from typing import Any, Callable, Dict, List, Optional, Set
from collections import defaultdict
from queue import Queue, Empty
from concurrent.futures import ThreadPoolExecutor, Future

from core.logger import Logger
from core.config import Config
from .models import (
    BusMessage, MessagePriority, MessageType, EventScope, SubscriptionType,
    DeliveryStatus, Subscription, BusStats,
)
from .storage import BusStorage


class EventBus:
    """
    Thread-safe publish/subscribe event bus for inter-agent communication.
    Supports sync/async/once/conditional subscriptions, pattern matching,
    priority-based dispatching, and fault-tolerant delivery.
    """

    def __init__(self, storage: Optional[BusStorage] = None, max_workers: int = 8):
        self.logger = Logger().get_logger("EventBus")
        self.config = Config()
        self.storage = storage or BusStorage()

        self._subscriptions: Dict[str, List[Subscription]] = defaultdict(list)
        self._subscription_lock = threading.RLock()
        self._pattern_cache: Dict[str, re.Pattern] = {}

        self._dispatch_queue: Queue = Queue()
        self._executor = ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix="EventBusWorker",
        )
        self._running = True
        self._dispatcher_thread = threading.Thread(
            target=self._dispatch_loop, daemon=True, name="EventBusDispatcher"
        )
        self._dispatcher_thread.start()

        self._stats = BusStats()
        self._stats_lock = threading.Lock()
        self._start_time = time.time()
        self._delivery_times: List[float] = []
        self._delivery_times_lock = threading.Lock()

        self._agent_registry: Set[str] = set()
        self._agent_registry_lock = threading.Lock()

        self.logger.info(f"EventBus initialized with {max_workers} workers")

    def register_agent(self, agent_name: str):
        """Register an agent with the event bus."""
        with self._agent_registry_lock:
            self._agent_registry.add(agent_name)
        self.logger.debug(f"Agent registered on bus: {agent_name}")

    def unregister_agent(self, agent_name: str):
        """Unregister an agent and remove its subscriptions."""
        with self._agent_registry_lock:
            self._agent_registry.discard(agent_name)
        self.remove_all_subscriptions(agent_name)
        self.logger.debug(f"Agent unregistered from bus: {agent_name}")

    def subscribe(
        self,
        agent_name: str,
        event_pattern: str,
        callback: Callable,
        subscription_type: SubscriptionType = SubscriptionType.SYNC,
        scope: EventScope = EventScope.GLOBAL,
        filter_func: Optional[Callable] = None,
        max_invocations: int = 0,
    ) -> str:
        """
        Subscribe an agent to events matching a pattern.
        Returns subscription ID.
        """
        sub = Subscription(
            agent_name=agent_name,
            event_pattern=event_pattern,
            callback=callback,
            subscription_type=subscription_type,
            scope=scope,
            filter_func=filter_func,
            max_invocations=max_invocations,
        )

        with self._subscription_lock:
            self._subscriptions[event_pattern].append(sub)

        self.storage.save_subscription({
            "id": sub.id,
            "agent_name": sub.agent_name,
            "event_pattern": sub.event_pattern,
            "subscription_type": sub.subscription_type.value,
            "scope": sub.scope.value,
            "is_active": sub.is_active,
            "created_at": sub.created_at.isoformat(),
            "max_invocations": sub.max_invocations,
            "invocation_count": sub.invocation_count,
        })

        with self._stats_lock:
            self._stats.total_subscriptions += 1
            self._stats.active_subscriptions += 1

        self.logger.info(f"Subscription created: {agent_name} -> {event_pattern} [{subscription_type.value}]")
        return sub.id

    def unsubscribe(self, subscription_id: str) -> bool:
        """Remove a subscription by ID."""
        with self._subscription_lock:
            for pattern, subs in self._subscriptions.items():
                for i, sub in enumerate(subs):
                    if sub.id == subscription_id:
                        sub.is_active = False
                        subs.pop(i)
                        self.storage.update_subscription(subscription_id, {"is_active": False})
                        with self._stats_lock:
                            self._stats.active_subscriptions -= 1
                        self.logger.info(f"Subscription removed: {subscription_id}")
                        return True
        return False

    def remove_all_subscriptions(self, agent_name: str):
        """Remove all subscriptions for an agent."""
        removed = 0
        with self._subscription_lock:
            for pattern, subs in list(self._subscriptions.items()):
                active_subs = []
                for sub in subs:
                    if sub.agent_name == agent_name:
                        sub.is_active = False
                        self.storage.update_subscription(sub.id, {"is_active": False})
                        removed += 1
                    else:
                        active_subs.append(sub)
                if active_subs:
                    self._subscriptions[pattern] = active_subs
                else:
                    del self._subscriptions[pattern]

        with self._stats_lock:
            self._stats.active_subscriptions -= removed
        self.logger.info(f"Removed {removed} subscriptions for {agent_name}")

    def publish(
        self,
        event: str,
        payload: Dict[str, Any],
        sender: str = "",
        priority: MessagePriority = MessagePriority.NORMAL,
        recipients: Optional[List[str]] = None,
        requires_ack: bool = False,
        ttl: int = 300,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Publish an event to the bus. Returns message ID.
        """
        message = BusMessage(
            sender=sender,
            recipients=recipients or [],
            message_type=MessageType.EVENT,
            priority=priority,
            event=event,
            payload=payload,
            requires_ack=requires_ack,
            ttl=ttl,
            metadata=metadata or {},
        )

        self._dispatch_queue.put(message)
        self.storage.save_message(message.to_dict())

        with self._stats_lock:
            self._stats.total_events_published += 1
            self._stats.total_messages_sent += 1
            current_size = self._dispatch_queue.qsize()
            self._stats.queue_size = current_size
            if current_size > self._stats.peak_queue_size:
                self._stats.peak_queue_size = current_size

        self.logger.debug(f"Event published: {event} from {sender} (priority: {priority.name})")
        return message.id

    def send_message(
        self,
        sender: str,
        recipient: str,
        event: str,
        payload: Dict[str, Any],
        message_type: MessageType = MessageType.REQUEST,
        priority: MessagePriority = MessagePriority.NORMAL,
        requires_ack: bool = False,
        correlation_id: Optional[str] = None,
        ttl: int = 300,
    ) -> str:
        """
        Send a direct message to a specific agent.
        """
        message = BusMessage(
            sender=sender,
            recipients=[recipient],
            message_type=message_type,
            priority=priority,
            event=event,
            payload=payload,
            requires_ack=requires_ack,
            correlation_id=correlation_id,
            ttl=ttl,
        )

        self._dispatch_queue.put(message)
        self.storage.save_message(message.to_dict())

        with self._stats_lock:
            self._stats.total_messages_sent += 1
            current_size = self._dispatch_queue.qsize()
            self._stats.queue_size = current_size
            if current_size > self._stats.peak_queue_size:
                self._stats.peak_queue_size = current_size

        self.logger.debug(f"Message sent: {sender} -> {recipient} [{event}]")
        return message.id

    def broadcast(
        self,
        sender: str,
        event: str,
        payload: Dict[str, Any],
        priority: MessagePriority = MessagePriority.NORMAL,
        exclude: Optional[List[str]] = None,
        ttl: int = 300,
    ) -> str:
        """
        Broadcast a message to all registered agents.
        """
        message = BusMessage(
            sender=sender,
            message_type=MessageType.BROADCAST,
            priority=priority,
            event=event,
            payload=payload,
            ttl=ttl,
            metadata={"exclude": exclude or []},
        )

        self._dispatch_queue.put(message)
        self.storage.save_message(message.to_dict())

        with self._stats_lock:
            self._stats.total_messages_sent += 1
            current_size = self._dispatch_queue.qsize()
            self._stats.queue_size = current_size
            if current_size > self._stats.peak_queue_size:
                self._stats.peak_queue_size = current_size

        self.logger.info(f"Broadcast: {sender} -> all agents [{event}]")
        return message.id

    def _dispatch_loop(self):
        """Background loop that processes the dispatch queue."""
        while self._running:
            try:
                message = self._dispatch_queue.get(timeout=0.1)
                if message.is_expired():
                    with self._stats_lock:
                        self._stats.expired_messages += 1
                    self.storage.update_message_status(message.id, DeliveryStatus.EXPIRED.value)
                    self._dispatch_queue.task_done()
                    continue

                self._executor.submit(self._deliver_message, message)

            except Empty:
                continue
            except Exception as e:
                self.logger.error(f"Dispatch loop error: {e}")

    def _deliver_message(self, message: BusMessage):
        """Deliver a message to matching subscribers."""
        start_time = time.time()
        message.delivery_status = DeliveryStatus.DELIVERED
        delivered_count = 0
        failed_count = 0

        try:
            matching_subs = self._find_matching_subscriptions(message)

            for sub in matching_subs:
                if message.recipients and sub.agent_name not in message.recipients:
                    exclude = message.metadata.get("exclude", [])
                    if sub.agent_name in exclude:
                        continue

                try:
                    sub.record_invocation()
                    self.storage.update_subscription(sub.id, {"invocation_count": sub.invocation_count})

                    if sub.subscription_type == SubscriptionType.ASYNC:
                        self._executor.submit(self._invoke_callback, sub, message)
                    else:
                        self._invoke_callback(sub, message)

                    delivered_count += 1
                    self.logger.debug(f"Delivered to {sub.agent_name}: {message.event}")

                except Exception as e:
                    failed_count += 1
                    self.logger.error(f"Delivery failed to {sub.agent_name}: {e}")
                    if message.retry_count < message.max_retries:
                        message.retry_count += 1
                        message.delivery_status = DeliveryStatus.RETRYING
                        self._dispatch_queue.put(message)
                        with self._stats_lock:
                            self._stats.total_retries += 1

            if failed_count == 0:
                message.delivery_status = DeliveryStatus.ACKNOWLEDGED
                self.storage.update_message_status(message.id, DeliveryStatus.ACKNOWLEDGED.value)
            elif delivered_count > 0:
                self.storage.update_message_status(message.id, DeliveryStatus.DELIVERED.value)
            else:
                message.delivery_status = DeliveryStatus.FAILED
                self.storage.update_message_status(message.id, DeliveryStatus.FAILED.value)

            with self._stats_lock:
                self._stats.total_messages_received += delivered_count
                self._stats.total_messages_failed += failed_count

            duration_ms = (time.time() - start_time) * 1000
            with self._delivery_times_lock:
                self._delivery_times.append(duration_ms)
                if len(self._delivery_times) > 1000:
                    self._delivery_times = self._delivery_times[-500:]

            self._dispatch_queue.task_done()

        except Exception as e:
            self.logger.error(f"Message delivery error: {e}")
            message.delivery_status = DeliveryStatus.FAILED
            self.storage.update_message_status(message.id, DeliveryStatus.FAILED.value)
            with self._stats_lock:
                self._stats.total_messages_failed += 1
            self._dispatch_queue.task_done()

    def _find_matching_subscriptions(self, message: BusMessage) -> List[Subscription]:
        """Find all subscriptions that match a message."""
        matching = []
        with self._subscription_lock:
            for pattern, subs in self._subscriptions.items():
                for sub in subs:
                    if sub.should_process(message):
                        matching.append(sub)
        return matching

    def _invoke_callback(self, subscription: Subscription, message: BusMessage):
        """Invoke a subscription callback with error handling."""
        if subscription.callback is None:
            return

        try:
            result = subscription.callback(message)
            self.logger.debug(f"Callback executed for {subscription.agent_name}: {message.event}")
            return result
        except Exception as e:
            self.logger.error(f"Callback error for {subscription.agent_name}: {e}")
            raise

    def get_stats(self) -> BusStats:
        """Get current bus statistics."""
        with self._stats_lock:
            self._stats.uptime_seconds = time.time() - self._start_time
            self._stats.queue_size = self._dispatch_queue.qsize()

            minutes = self._stats.uptime_seconds / 60.0
            if minutes > 0:
                self._stats.messages_per_minute = self._stats.total_messages_sent / minutes

            with self._delivery_times_lock:
                if self._delivery_times:
                    self._stats.avg_delivery_time_ms = sum(self._delivery_times) / len(self._delivery_times)

            return BusStats(**self._stats.to_dict())

    def get_registered_agents(self) -> List[str]:
        """Get list of registered agents."""
        with self._agent_registry_lock:
            return list(self._agent_registry)

    def get_subscriptions_for_agent(self, agent_name: str) -> List[Dict[str, Any]]:
        """Get all subscriptions for an agent."""
        with self._subscription_lock:
            result = []
            for pattern, subs in self._subscriptions.items():
                for sub in subs:
                    if sub.agent_name == agent_name:
                        result.append({
                            "id": sub.id,
                            "event_pattern": sub.event_pattern,
                            "type": sub.subscription_type.value,
                            "scope": sub.scope.value,
                            "is_active": sub.is_active,
                            "invocation_count": sub.invocation_count,
                        })
            return result

    def shutdown(self, wait: bool = True):
        """Shutdown the event bus."""
        self.logger.info("Shutting down EventBus...")
        self._running = False

        if wait:
            self._dispatch_queue.join()

        self._executor.shutdown(wait=wait)
        self.logger.info("EventBus shutdown complete")
