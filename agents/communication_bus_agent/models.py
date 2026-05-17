"""
NEXUS - Agent Communication Bus
Data models for inter-agent messaging, events, and shared state.
"""

import uuid
import time
import json
from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime


class MessageType(Enum):
    """Types of messages that can be sent on the bus."""
    REQUEST = "request"
    RESPONSE = "response"
    EVENT = "event"
    COMMAND = "command"
    NOTIFICATION = "notification"
    ERROR = "error"
    HEARTBEAT = "heartbeat"
    BROADCAST = "broadcast"


class MessagePriority(Enum):
    """Priority levels for message processing."""
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3
    BACKGROUND = 4


class EventScope(Enum):
    """Scope of event propagation."""
    GLOBAL = "global"
    AGENT = "agent"
    GROUP = "group"
    PRIVATE = "private"


class SubscriptionType(Enum):
    """Types of subscriptions."""
    SYNC = "sync"
    ASYNC = "async"
    ONCE = "once"
    CONDITIONAL = "conditional"


class DeliveryStatus(Enum):
    """Status of message delivery."""
    PENDING = "pending"
    QUEUED = "queued"
    DELIVERED = "delivered"
    ACKNOWLEDGED = "acknowledged"
    FAILED = "failed"
    EXPIRED = "expired"
    RETRYING = "retrying"


@dataclass
class BusMessage:
    """Represents a message on the communication bus."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)
    sender: str = ""
    recipients: List[str] = field(default_factory=list)
    message_type: MessageType = MessageType.EVENT
    priority: MessagePriority = MessagePriority.NORMAL
    event: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    ttl: int = 300
    delivery_status: DeliveryStatus = DeliveryStatus.PENDING
    retry_count: int = 0
    max_retries: int = 3
    correlation_id: Optional[str] = None
    reply_to: Optional[str] = None
    requires_ack: bool = False
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "sender": self.sender,
            "recipients": self.recipients,
            "message_type": self.message_type.value,
            "priority": self.priority.value,
            "event": self.event,
            "payload": self.payload,
            "metadata": self.metadata,
            "ttl": self.ttl,
            "delivery_status": self.delivery_status.value,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "correlation_id": self.correlation_id,
            "reply_to": self.reply_to,
            "requires_ack": self.requires_ack,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BusMessage":
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            timestamp=data.get("timestamp", time.time()),
            sender=data.get("sender", ""),
            recipients=data.get("recipients", []),
            message_type=MessageType(data.get("message_type", "event")),
            priority=MessagePriority(data.get("priority", 2)),
            event=data.get("event", ""),
            payload=data.get("payload", {}),
            metadata=data.get("metadata", {}),
            ttl=data.get("ttl", 300),
            delivery_status=DeliveryStatus(data.get("delivery_status", "pending")),
            retry_count=data.get("retry_count", 0),
            max_retries=data.get("max_retries", 3),
            correlation_id=data.get("correlation_id"),
            reply_to=data.get("reply_to"),
            requires_ack=data.get("requires_ack", False),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now(),
        )

    def is_expired(self) -> bool:
        return (time.time() - self.timestamp) > self.ttl

    def __lt__(self, other):
        if not isinstance(other, BusMessage):
            return NotImplemented
        if self.priority.value != other.priority.value:
            return self.priority.value < other.priority.value
        return self.timestamp < other.timestamp


@dataclass
class Subscription:
    """Represents a subscription to bus events."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agent_name: str = ""
    event_pattern: str = "*"
    callback: Optional[Callable] = field(default=None, repr=False)
    subscription_type: SubscriptionType = SubscriptionType.SYNC
    scope: EventScope = EventScope.GLOBAL
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    filter_func: Optional[Callable] = field(default=None, repr=False)
    max_invocations: int = 0
    invocation_count: int = 0

    def matches_event(self, event: str) -> bool:
        if self.event_pattern == "*":
            return True
        if self.event_pattern == event:
            return True
        if self.event_pattern.endswith(".*"):
            prefix = self.event_pattern[:-2]
            return event.startswith(prefix + ".")
        if self.event_pattern.startswith("*."):
            suffix = self.event_pattern[2:]
            return event.endswith("." + suffix)
        return False

    def should_process(self, message: BusMessage) -> bool:
        if not self.is_active:
            return False
        if not self.matches_event(message.event):
            return False
        if self.max_invocations > 0 and self.invocation_count >= self.max_invocations:
            return False
        if self.filter_func and not self.filter_func(message):
            return False
        return True

    def record_invocation(self):
        self.invocation_count += 1
        if self.subscription_type == SubscriptionType.ONCE:
            self.is_active = False


@dataclass
class SharedStateEntry:
    """Represents an entry in the shared state manager."""
    key: str
    value: Any
    owner: str = ""
    ttl: int = 0
    is_locked: bool = False
    lock_owner: str = ""
    version: int = 1
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_expired(self) -> bool:
        if self.ttl <= 0:
            return False
        elapsed = (datetime.now() - self.created_at).total_seconds()
        return elapsed > self.ttl

    def to_dict(self) -> Dict[str, Any]:
        return {
            "key": self.key,
            "value": self.value,
            "owner": self.owner,
            "ttl": self.ttl,
            "is_locked": self.is_locked,
            "lock_owner": self.lock_owner,
            "version": self.version,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "access_count": self.access_count,
            "metadata": self.metadata,
        }


@dataclass
class EventLogEntry:
    """Represents a logged event in the event logging system."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    event_type: str = ""
    source_agent: str = ""
    target_agent: str = ""
    event_name: str = ""
    message_id: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    success: bool = True
    error_message: str = ""
    duration_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "event_type": self.event_type,
            "source_agent": self.source_agent,
            "target_agent": self.target_agent,
            "event_name": self.event_name,
            "message_id": self.message_id,
            "details": json.dumps(self.details),
            "success": self.success,
            "error_message": self.error_message,
            "duration_ms": self.duration_ms,
        }


@dataclass
class BusStats:
    """Statistics for the communication bus."""
    total_messages_sent: int = 0
    total_messages_received: int = 0
    total_messages_failed: int = 0
    total_events_published: int = 0
    total_subscriptions: int = 0
    active_subscriptions: int = 0
    queue_size: int = 0
    avg_delivery_time_ms: float = 0.0
    messages_per_minute: float = 0.0
    uptime_seconds: float = 0.0
    peak_queue_size: int = 0
    total_retries: int = 0
    expired_messages: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_messages_sent": self.total_messages_sent,
            "total_messages_received": self.total_messages_received,
            "total_messages_failed": self.total_messages_failed,
            "total_events_published": self.total_events_published,
            "total_subscriptions": self.total_subscriptions,
            "active_subscriptions": self.active_subscriptions,
            "queue_size": self.queue_size,
            "avg_delivery_time_ms": round(self.avg_delivery_time_ms, 2),
            "messages_per_minute": round(self.messages_per_minute, 2),
            "uptime_seconds": round(self.uptime_seconds, 2),
            "peak_queue_size": self.peak_queue_size,
            "total_retries": self.total_retries,
            "expired_messages": self.expired_messages,
        }
