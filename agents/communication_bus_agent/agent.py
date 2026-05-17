"""
NEXUS - Agent Communication Bus
CommunicationBusAgent: BaseAgent wrapper that integrates the event bus,
message broker, shared state manager, and event logger with the AI Manager.
"""

import json
import time
from typing import Any, Callable, Dict, List, Optional

from core.base_agent import BaseAgent, AgentStatus
from core.logger import Logger
from core.config import Config

from .models import (
    BusMessage, MessagePriority, MessageType, EventScope, SubscriptionType,
    DeliveryStatus, BusStats,
)
from .storage import BusStorage
from .event_bus import EventBus
from .message_broker import MessageBroker
from .shared_state import SharedStateManager
from .event_logger import EventLogger


class CommunicationBusAgent(BaseAgent):
    """
    Agent that provides the communication bus interface to the AI Manager.
    Wraps EventBus, MessageBroker, SharedStateManager, and EventLogger
    into a single agent with execute() commands.
    """

    def __init__(self):
        super().__init__(
            name="communication_bus_agent",
            description="Central communication bus for inter-agent messaging, event broadcasting, shared state, and event logging",
        )
        self.logger = Logger().get_logger("CommunicationBusAgent")
        self.config = Config()

        self.storage = BusStorage()
        self.event_bus = EventBus(storage=self.storage)
        self.message_broker = MessageBroker(storage=self.storage)
        self.shared_state = SharedStateManager(storage=self.storage)
        self.event_logger = EventLogger(storage=self.storage)

        self._ai_manager = None
        self._agent_handlers: Dict[str, Callable] = {}

        self._register_internal_handlers()
        self.logger.info("CommunicationBusAgent initialized")

    def set_ai_manager(self, manager):
        """Set reference to the AI Manager for cross-agent communication."""
        self._ai_manager = manager
        self._register_all_agents()
        self.logger.info("CommunicationBusAgent connected to AIManager")

    def _register_internal_handlers(self):
        """Register internal command handlers."""
        self._handlers = {
            "publish": self._handle_publish,
            "broadcast": self._handle_broadcast,
            "send_message": self._handle_send_message,
            "subscribe": self._handle_subscribe,
            "unsubscribe": self._handle_unsubscribe,
            "subscriptions": self._handle_list_subscriptions,
            "shared_state_set": self._handle_shared_state_set,
            "shared_state_get": self._handle_shared_state_get,
            "shared_state_delete": self._handle_shared_state_delete,
            "shared_state_lock": self._handle_shared_state_lock,
            "shared_state_unlock": self._handle_shared_state_unlock,
            "shared_state_list": self._handle_shared_state_list,
            "event_logs": self._handle_event_logs,
            "event_summary": self._handle_event_summary,
            "agent_activity": self._handle_agent_activity,
            "communication_flow": self._handle_communication_flow,
            "error_report": self._handle_error_report,
            "stats": self._handle_stats,
            "bus_stats": self._handle_bus_stats,
            "message_status": self._handle_message_status,
            "dlq_messages": self._handle_dlq_messages,
            "retry_dlq": self._handle_retry_dlq,
            "purge_dlq": self._handle_purge_dlq,
            "registered_agents": self._handle_registered_agents,
            "help": self._handle_help,
        }

    def _register_all_agents(self):
        """Register all AI Manager agents with the event bus."""
        if not self._ai_manager:
            return

        for agent_name in self._ai_manager.agents:
            self.event_bus.register_agent(agent_name)
            self.logger.debug(f"Auto-registered agent on bus: {agent_name}")

    def execute(self, command: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a communication bus command."""
        self.status = AgentStatus.BUSY
        start_time = time.time()

        try:
            cmd = command.strip().lower()
            handler = self._handlers.get(cmd)

            if handler:
                result = handler(params or {})
            else:
                result = self._handle_fallback(command, params or {})

            duration_ms = (time.time() - start_time) * 1000
            self.event_logger.log(
                event_type="command",
                event_name=cmd if handler else "fallback",
                source_agent="communication_bus_agent",
                details={"command": command, "params": params},
                success=result.get("success", False),
                duration_ms=duration_ms,
            )

            return result

        except Exception as e:
            self.logger.error(f"Execution error: {e}")
            return {
                "success": False,
                "response": f"Error: {str(e)}",
                "agent": self.name,
            }
        finally:
            self.status = AgentStatus.IDLE

    def _handle_publish(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Publish an event to the bus."""
        event = params.get("event", "")
        payload = params.get("payload", {})
        sender = params.get("sender", "communication_bus_agent")
        priority = MessagePriority(params.get("priority", 2))
        recipients = params.get("recipients", [])
        requires_ack = params.get("requires_ack", False)
        ttl = params.get("ttl", 300)

        if not event:
            return {"success": False, "response": "Event name is required"}

        message_id = self.event_bus.publish(
            event=event,
            payload=payload,
            sender=sender,
            priority=priority,
            recipients=recipients,
            requires_ack=requires_ack,
            ttl=ttl,
        )

        return {
            "success": True,
            "response": f"Event '{event}' published (message_id: {message_id})",
            "data": {"message_id": message_id, "event": event},
        }

    def _handle_broadcast(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Broadcast a message to all agents."""
        event = params.get("event", "")
        payload = params.get("payload", {})
        sender = params.get("sender", "communication_bus_agent")
        priority = MessagePriority(params.get("priority", 2))
        exclude = params.get("exclude", [])
        ttl = params.get("ttl", 300)

        if not event:
            return {"success": False, "response": "Event name is required"}

        message_id = self.event_bus.broadcast(
            sender=sender,
            event=event,
            payload=payload,
            priority=priority,
            exclude=exclude,
            ttl=ttl,
        )

        return {
            "success": True,
            "response": f"Broadcast '{event}' sent to all agents (message_id: {message_id})",
            "data": {"message_id": message_id},
        }

    def _handle_send_message(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Send a direct message to a specific agent."""
        sender = params.get("sender", "communication_bus_agent")
        recipient = params.get("recipient", "")
        event = params.get("event", "")
        payload = params.get("payload", {})
        priority = MessagePriority(params.get("priority", 2))
        requires_ack = params.get("requires_ack", False)

        if not recipient:
            return {"success": False, "response": "Recipient is required"}
        if not event:
            return {"success": False, "response": "Event name is required"}

        message_id = self.event_bus.send_message(
            sender=sender,
            recipient=recipient,
            event=event,
            payload=payload,
            priority=priority,
            requires_ack=requires_ack,
        )

        return {
            "success": True,
            "response": f"Message sent to {recipient} (message_id: {message_id})",
            "data": {"message_id": message_id, "recipient": recipient},
        }

    def _handle_subscribe(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Subscribe an agent to events."""
        agent_name = params.get("agent_name", "")
        event_pattern = params.get("event_pattern", "*")
        sub_type = params.get("type", "sync")
        scope = params.get("scope", "global")

        if not agent_name:
            return {"success": False, "response": "Agent name is required"}

        type_map = {
            "sync": SubscriptionType.SYNC,
            "async": SubscriptionType.ASYNC,
            "once": SubscriptionType.ONCE,
            "conditional": SubscriptionType.CONDITIONAL,
        }
        subscription_type = type_map.get(sub_type, SubscriptionType.SYNC)

        scope_map = {
            "global": EventScope.GLOBAL,
            "agent": EventScope.AGENT,
            "group": EventScope.GROUP,
            "private": EventScope.PRIVATE,
        }
        scope = scope_map.get(scope, EventScope.GLOBAL)

        def default_callback(message: BusMessage):
            self.logger.debug(f"[{agent_name}] Received: {message.event}")

        sub_id = self.event_bus.subscribe(
            agent_name=agent_name,
            event_pattern=event_pattern,
            callback=default_callback,
            subscription_type=subscription_type,
            scope=scope,
        )

        return {
            "success": True,
            "response": f"Agent '{agent_name}' subscribed to '{event_pattern}' (sub_id: {sub_id})",
            "data": {"subscription_id": sub_id, "agent": agent_name, "pattern": event_pattern},
        }

    def _handle_unsubscribe(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Unsubscribe from events."""
        sub_id = params.get("subscription_id", "")
        if not sub_id:
            return {"success": False, "response": "Subscription ID is required"}

        success = self.event_bus.unsubscribe(sub_id)
        return {
            "success": success,
            "response": f"Subscription {'removed' if success else 'not found'}: {sub_id}",
        }

    def _handle_list_subscriptions(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List all subscriptions."""
        agent_name = params.get("agent_name", "")
        if agent_name:
            subs = self.event_bus.get_subscriptions_for_agent(agent_name)
        else:
            subs = []
            for agent in self.event_bus.get_registered_agents():
                subs.extend(self.event_bus.get_subscriptions_for_agent(agent))

        return {
            "success": True,
            "response": f"Found {len(subs)} subscriptions",
            "data": {"subscriptions": subs},
        }

    def _handle_shared_state_set(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Set a shared state value."""
        key = params.get("key", "")
        value = params.get("value")
        owner = params.get("owner", "communication_bus_agent")
        ttl = params.get("ttl", 0)
        namespace = params.get("namespace", "global")

        if not key:
            return {"success": False, "response": "Key is required"}

        success = self.shared_state.set(key, value, owner, ttl, namespace)
        return {
            "success": success,
            "response": f"State {'set' if success else 'failed (locked)'}: {key}",
            "data": {"key": key, "namespace": namespace},
        }

    def _handle_shared_state_get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get a shared state value."""
        key = params.get("key", "")
        namespace = params.get("namespace", "global")

        if not key:
            return {"success": False, "response": "Key is required"}

        value = self.shared_state.get(key, namespace)
        if value is None:
            return {"success": False, "response": f"Key not found: {key}"}

        return {
            "success": True,
            "response": f"State retrieved: {key}",
            "data": {"key": key, "value": value, "namespace": namespace},
        }

    def _handle_shared_state_delete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a shared state value."""
        key = params.get("key", "")
        owner = params.get("owner", "communication_bus_agent")
        namespace = params.get("namespace", "global")

        if not key:
            return {"success": False, "response": "Key is required"}

        success = self.shared_state.delete(key, owner, namespace)
        return {
            "success": success,
            "response": f"State {'deleted' if success else 'not found or locked'}: {key}",
        }

    def _handle_shared_state_lock(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lock a shared state entry."""
        key = params.get("key", "")
        owner = params.get("owner", "communication_bus_agent")
        namespace = params.get("namespace", "global")

        if not key:
            return {"success": False, "response": "Key is required"}

        success = self.shared_state.lock(key, owner, namespace)
        return {
            "success": success,
            "response": f"State {'locked' if success else 'already locked'}: {key}",
        }

    def _handle_shared_state_unlock(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Unlock a shared state entry."""
        key = params.get("key", "")
        owner = params.get("owner", "communication_bus_agent")
        namespace = params.get("namespace", "global")

        if not key:
            return {"success": False, "response": "Key is required"}

        success = self.shared_state.unlock(key, owner, namespace)
        return {
            "success": success,
            "response": f"State {'unlocked' if success else 'not locked by owner'}: {key}",
        }

    def _handle_shared_state_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List all shared state entries."""
        namespace = params.get("namespace", None)
        state = self.shared_state.get_all(namespace)
        return {
            "success": True,
            "response": f"Found {len(state)} state entries",
            "data": {"state": state},
        }

    def _handle_event_logs(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get event logs."""
        event_type = params.get("event_type")
        source_agent = params.get("source_agent")
        limit = params.get("limit", 50)
        hours = params.get("hours", 24)

        logs = self.event_logger.get_logs(
            event_type=event_type,
            source_agent=source_agent,
            limit=limit,
            hours=hours,
        )

        return {
            "success": True,
            "response": f"Found {len(logs)} event logs",
            "data": {"logs": logs},
        }

    def _handle_event_summary(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get event summary."""
        hours = params.get("hours", 24)
        summary = self.event_logger.get_event_summary(hours=hours)
        return {
            "success": True,
            "response": "Event summary retrieved",
            "data": summary,
        }

    def _handle_agent_activity(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get agent activity summary."""
        agent_name = params.get("agent_name", "")
        hours = params.get("hours", 24)

        if not agent_name:
            return {"success": False, "response": "Agent name is required"}

        activity = self.event_logger.get_agent_activity(agent_name, hours)
        return {
            "success": True,
            "response": f"Activity for {agent_name}",
            "data": activity,
        }

    def _handle_communication_flow(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get communication flow between agents."""
        hours = params.get("hours", 24)
        limit = params.get("limit", 20)
        flow = self.event_logger.get_communication_flow(hours=hours, limit=limit)
        return {
            "success": True,
            "response": "Communication flow retrieved",
            "data": {"flow": flow},
        }

    def _handle_error_report(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get error report."""
        hours = params.get("hours", 24)
        errors = self.event_logger.get_error_report(hours=hours)
        return {
            "success": True,
            "response": f"Found {len(errors)} errors",
            "data": {"errors": errors},
        }

    def _handle_stats(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive bus statistics."""
        bus_stats = self.event_bus.get_stats()
        broker_stats = self.message_broker.get_stats()
        state_stats = self.shared_state.get_stats()
        logger_stats = self.event_logger.get_stats()

        return {
            "success": True,
            "response": "Bus statistics retrieved",
            "data": {
                "event_bus": bus_stats.to_dict(),
                "message_broker": broker_stats,
                "shared_state": state_stats,
                "event_logger": logger_stats,
            },
        }

    def _handle_bus_stats(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get event bus statistics."""
        stats = self.event_bus.get_stats()
        return {
            "success": True,
            "response": "Event bus statistics",
            "data": stats.to_dict(),
        }

    def _handle_message_status(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get status of a specific message."""
        message_id = params.get("message_id", "")
        if not message_id:
            return {"success": False, "response": "Message ID is required"}

        status = self.message_broker.get_message_status(message_id)
        if not status:
            stored = self.storage.get_message(message_id)
            if stored:
                return {
                    "success": True,
                    "response": f"Message status: {stored['delivery_status']}",
                    "data": stored,
                }
            return {"success": False, "response": "Message not found"}

        return {
            "success": True,
            "response": f"Message status: {status['status']}",
            "data": status,
        }

    def _handle_dlq_messages(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get messages in the dead letter queue."""
        dlq = self.message_broker.get_dlq_messages()
        return {
            "success": True,
            "response": f"DLQ contains {len(dlq)} messages",
            "data": {
                "messages": [m.to_dict() for m in dlq],
                "count": len(dlq),
            },
        }

    def _handle_retry_dlq(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retry a message from the DLQ."""
        message_id = params.get("message_id", "")
        if not message_id:
            return {"success": False, "response": "Message ID is required"}

        success = self.message_broker.retry_dlq_message(message_id)
        return {
            "success": success,
            "response": f"DLQ message {'retried' if success else 'not found'}",
        }

    def _handle_purge_dlq(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Purge the dead letter queue."""
        count = self.message_broker.purge_dlq()
        return {
            "success": True,
            "response": f"Purged {count} messages from DLQ",
            "data": {"purged_count": count},
        }

    def _handle_registered_agents(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get list of registered agents on the bus."""
        agents = self.event_bus.get_registered_agents()
        return {
            "success": True,
            "response": f"Found {len(agents)} registered agents",
            "data": {"agents": agents},
        }

    def _handle_fallback(self, command: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle unrecognized commands with intelligent routing."""
        cmd_lower = command.lower()

        if any(kw in cmd_lower for kw in ["publish", "emit", "send event"]):
            return self._handle_publish({"event": command, "payload": params})
        if any(kw in cmd_lower for kw in ["broadcast"]):
            return self._handle_broadcast({"event": command, "payload": params})
        if any(kw in cmd_lower for kw in ["subscribe", "listen"]):
            return self._handle_subscribe(params)
        if any(kw in cmd_lower for kw in ["state", "shared"]):
            if any(kw in cmd_lower for kw in ["get", "read"]):
                return self._handle_shared_state_get(params)
            if any(kw in cmd_lower for kw in ["set", "write"]):
                return self._handle_shared_state_set(params)
            if any(kw in cmd_lower for kw in ["list", "show"]):
                return self._handle_shared_state_list(params)
        if any(kw in cmd_lower for kw in ["logs", "history"]):
            return self._handle_event_logs(params)
        if any(kw in cmd_lower for kw in ["stats", "statistics"]):
            return self._handle_stats(params)

        return {
            "success": False,
            "response": f"Unknown communication bus command: {command}. Type 'help' for available commands.",
        }

    def _handle_help(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Show available commands."""
        return {
            "success": True,
            "response": """Communication Bus - Available Commands:

MESSAGING:
  publish          - Publish an event to the bus
  broadcast        - Broadcast to all agents
  send_message     - Send direct message to agent
  message_status   - Check message delivery status

SUBSCRIPTIONS:
  subscribe        - Subscribe agent to events
  unsubscribe      - Remove subscription
  subscriptions    - List all subscriptions

SHARED STATE:
  shared_state_set    - Set shared state value
  shared_state_get    - Get shared state value
  shared_state_delete - Delete shared state entry
  shared_state_lock   - Lock state entry
  shared_state_unlock - Unlock state entry
  shared_state_list   - List all state entries

EVENT LOGS:
  event_logs         - Get event logs
  event_summary      - Get event summary
  agent_activity     - Get agent activity
  communication_flow - Get agent communication flow
  error_report       - Get error report

STATISTICS:
  stats            - Get comprehensive bus stats
  bus_stats        - Get event bus stats
  registered_agents- List registered agents

DEAD LETTER QUEUE:
  dlq_messages     - View DLQ messages
  retry_dlq        - Retry DLQ message
  purge_dlq        - Purge DLQ""",
        }

    def get_capabilities(self) -> list:
        """Return list of capabilities."""
        return [
            "publish", "broadcast", "send_message", "message_status",
            "subscribe", "unsubscribe", "subscriptions",
            "shared_state_set", "shared_state_get", "shared_state_delete",
            "shared_state_lock", "shared_state_unlock", "shared_state_list",
            "event_logs", "event_summary", "agent_activity",
            "communication_flow", "error_report",
            "stats", "bus_stats", "registered_agents",
            "dlq_messages", "retry_dlq", "purge_dlq",
        ]

    def publish_event(
        self,
        event: str,
        payload: Dict[str, Any],
        sender: str = "communication_bus_agent",
        priority: MessagePriority = MessagePriority.NORMAL,
        recipients: Optional[List[str]] = None,
    ) -> str:
        """Programmatic API: Publish an event."""
        return self.event_bus.publish(
            event=event,
            payload=payload,
            sender=sender,
            priority=priority,
            recipients=recipients,
        )

    def send_direct_message(
        self,
        sender: str,
        recipient: str,
        event: str,
        payload: Dict[str, Any],
        priority: MessagePriority = MessagePriority.NORMAL,
    ) -> str:
        """Programmatic API: Send direct message."""
        return self.event_bus.send_message(
            sender=sender,
            recipient=recipient,
            event=event,
            payload=payload,
            priority=priority,
        )

    def set_shared_state(self, key: str, value: Any, owner: str = "", ttl: int = 0):
        """Programmatic API: Set shared state."""
        return self.shared_state.set(key, value, owner, ttl)

    def get_shared_state(self, key: str, default: Any = None) -> Any:
        """Programmatic API: Get shared state."""
        return self.shared_state.get(key, default=default)

    def shutdown(self):
        """Shutdown all bus components."""
        self.logger.info("Shutting down CommunicationBusAgent...")
        self.event_bus.shutdown(wait=False)
        self.message_broker.shutdown(wait=False)
        self.shared_state.shutdown()
        self.event_logger.shutdown()
        self.status = AgentStatus.OFFLINE
        self.logger.info("CommunicationBusAgent shutdown complete")
