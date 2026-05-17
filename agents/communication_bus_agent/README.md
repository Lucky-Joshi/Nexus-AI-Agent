# Communication Bus Agent

> Central pub/sub event bus, message broker, shared state manager, and event logger for inter-agent communication in NEXUS.

## Purpose

The Communication Bus Agent provides the backbone for all inter-agent communication in NEXUS. It implements a publish/subscribe event system with priority-based message routing, direct agent-to-agent messaging, a shared state store with locking, and comprehensive event logging. This enables agents to coordinate, share data, react to events, and maintain consistent state without direct coupling to each other.

## Architecture

```
communication_bus_agent/
├── __init__.py
├── agent.py              # CommunicationBusAgent orchestrator
├── models.py             # BusMessage, MessagePriority, MessageType, EventScope, SubscriptionType
├── event_bus.py          # EventBus - pub/sub with thread pool, priority queue, wildcard patterns
├── message_broker.py     # MessageBroker - direct messaging, delivery tracking, dead letter queue
├── shared_state.py       # SharedStateManager - key-value store with locking and TTL
├── event_logger.py       # EventLogger - persistent event audit trail
├── storage.py            # BusStorage - JSON-based persistence for all bus data
```

### Component Breakdown

| Component | Responsibility |
|-----------|---------------|
| `EventBus` | Core pub/sub system with event publishing, wildcard pattern subscriptions, priority queuing, and thread-pool delivery |
| `MessageBroker` | Direct point-to-point messaging with delivery acknowledgment, retry logic, and dead letter queue (DLQ) |
| `SharedStateManager` | Distributed key-value store with namespace support, TTL, and optimistic locking |
| `EventLogger` | Persistent audit trail of all bus events with filtering, aggregation, and error reporting |
| `BusStorage` | Unified JSON-based persistence layer for messages, subscriptions, state, and logs |

### Architecture Diagram

```
┌─────────────┐     ┌──────────────────────┐     ┌─────────────┐
│  Publisher  │────>│      Event Bus       │────>│ Subscriber  │
│  (Agent A)  │     │  (Priority Queue +   │     │  (Agent B)  │
└─────────────┘     │   Thread Pool)       │     └─────────────┘
                    └──────────┬───────────┘
                               │
                    ┌──────────┴───────────┐
                    │   Message Broker     │
                    │  (Direct Messages +  │
                    │   Dead Letter Queue) │
                    └──────────┬───────────┘
                               │
                    ┌──────────┴───────────┐
                    │  Shared State Store  │
                    │  (Key-Value + Lock)  │
                    └──────────┬───────────┘
                               │
                    ┌──────────┴───────────┐
                    │    Event Logger      │
                    │  (Audit Trail)       │
                    └──────────────────────┘
```

### Message Flow

```
1. Agent A publishes event: "task.completed" with payload {task_id, result}
2. EventBus matches event against subscriptions (supports wildcards: "task.*")
3. Matching subscribers receive the message via callback (sync or async)
4. MessageBroker tracks delivery status (pending -> delivered -> acknowledged)
5. Failed deliveries are retried, then moved to Dead Letter Queue
6. EventLogger records the entire transaction for auditing
```

## Capabilities

### Messaging

| Command | Description |
|---------|-------------|
| `publish` | Publish an event to the bus |
| `broadcast` | Broadcast a message to all agents |
| `send_message` | Send a direct message to a specific agent |
| `message_status` | Check message delivery status |

### Subscriptions

| Command | Description |
|---------|-------------|
| `subscribe` | Subscribe an agent to event patterns |
| `unsubscribe` | Remove a subscription |
| `subscriptions` | List all active subscriptions |

### Shared State

| Command | Description |
|---------|-------------|
| `shared_state_set` | Set a shared state value |
| `shared_state_get` | Get a shared state value |
| `shared_state_delete` | Delete a shared state entry |
| `shared_state_lock` | Lock a state entry (prevent concurrent writes) |
| `shared_state_unlock` | Unlock a state entry |
| `shared_state_list` | List all shared state entries |

### Event Logs

| Command | Description |
|---------|-------------|
| `event_logs` | Get event logs with filtering |
| `event_summary` | Get event summary statistics |
| `agent_activity` | Get activity for a specific agent |
| `communication_flow` | Get communication flow between agents |
| `error_report` | Get error report from event logs |

### Statistics

| Command | Description |
|---------|-------------|
| `stats` | Get comprehensive bus statistics |
| `bus_stats` | Get event bus specific statistics |
| `registered_agents` | List all agents registered on the bus |

### Dead Letter Queue

| Command | Description |
|---------|-------------|
| `dlq_messages` | View messages in the dead letter queue |
| `retry_dlq` | Retry a failed message from DLQ |
| `purge_dlq` | Purge all messages from DLQ |

### Programmatic API

```python
# Publish an event
message_id = comm_bus.publish_event(
    event="task.completed",
    payload={"task_id": "123", "result": "success", "agent": "file_agent"},
    sender="file_agent",
    priority=MessagePriority.HIGH,
)

# Send direct message
message_id = comm_bus.send_direct_message(
    sender="coding_agent",
    recipient="file_agent",
    event="file.save",
    payload={"path": "output.py", "content": "print('hello')"},
)

# Shared state operations
comm_bus.set_shared_state("current_mode", "coding", owner="workflow_agent", ttl=3600)
mode = comm_bus.get_shared_state("current_mode", default="default")

# Subscribe to events
comm_bus.event_bus.subscribe(
    agent_name="notification_agent",
    event_pattern="task.*",
    callback=on_task_event,
    subscription_type=SubscriptionType.ASYNC,
)
```

## Internal Structure

### Bus Message Model

```python
@dataclass
class BusMessage:
    id: str
    event: str
    sender: str
    recipients: list[str]
    payload: dict
    priority: MessagePriority       # low, normal, high, critical
    message_type: MessageType       # event, direct, broadcast
    scope: EventScope               # global, agent, group, private
    timestamp: str
    ttl: int                        # time-to-live in seconds
    requires_ack: bool
    delivery_status: DeliveryStatus # pending, delivered, acknowledged, failed, expired
    retry_count: int
```

### Message Priority Levels

| Priority | Description | Queue Position |
|----------|-------------|----------------|
| `critical` | System-critical events | First |
| `high` | Important notifications | Second |
| `normal` | Standard events | Third |
| `low` | Background events | Last |

### Subscription Types

| Type | Behavior |
|------|----------|
| `sync` | Callback executed in publisher's thread |
| `async` | Callback executed in worker thread pool |
| `once` | Subscription auto-removed after first delivery |
| `conditional` | Delivery based on payload conditions |

### Event Scopes

| Scope | Visibility |
|-------|------------|
| `global` | All subscribed agents receive |
| `agent` | Only the specified agent |
| `group` | Agents in the same group |
| `private` | Only sender and specified recipients |

### Shared State Features

- **Namespaces**: Organize state by category (`global`, `agent_name`, custom)
- **TTL**: Auto-expire state entries after a specified time
- **Locking**: Prevent concurrent writes with optimistic locking
- **Owner tracking**: Know which agent set each value

## Usage Examples

### Publishing Events

```
> publish
Event 'task.completed' published (message_id: msg_a1b2c3d4)
```

### Subscribing to Events

```
> subscribe
Agent 'notification_agent' subscribed to 'task.*' (sub_id: sub_e5f6g7h8)
```

### Shared State

```
> shared_state_set
State set: current_mode (namespace: global)

> shared_state_get
State retrieved: current_mode
Data: {"key": "current_mode", "value": "coding", "namespace": "global"}
```

### Checking Statistics

```
> stats
Bus statistics retrieved
Data: {
  "event_bus": {"published": 1247, "delivered": 1198, "failed": 12},
  "message_broker": {"sent": 456, "acknowledged": 445, "dlq": 3},
  "shared_state": {"entries": 28, "locked": 2},
  "event_logger": {"total_events": 1703, "errors": 15}
}
```

### Dead Letter Queue

```
> dlq_messages
DLQ contains 3 messages

> retry_dlq
DLQ message retried
```

### Event Logs

```
> event_logs
Found 50 event logs
```

## Configuration

```json
{
  "agents": {
    "communication_bus_agent": {
      "enabled": true,
      "max_workers": 8,
      "default_ttl": 300,
      "max_queue_size": 10000,
      "max_retries": 3,
      "retry_delay_seconds": 5,
      "event_log_retention_hours": 168,
      "shared_state_max_entries": 1000
    }
  }
}
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | bool | `true` | Enable/disable the agent |
| `max_workers` | int | `8` | Thread pool size for async event delivery |
| `default_ttl` | int | `300` | Default message time-to-live in seconds |
| `max_queue_size` | int | `10000` | Maximum event queue size |
| `max_retries` | int | `3` | Maximum delivery retry attempts |
| `retry_delay_seconds` | int | `5` | Delay between retry attempts |
| `event_log_retention_hours` | int | `168` | How long to retain event logs (7 days) |
| `shared_state_max_entries` | int | `1000` | Maximum shared state entries |

## Dependencies

| Dependency | Source | Purpose |
|------------|--------|---------|
| `core.base_agent` | Local | BaseAgent, AgentStatus |
| `core.config` | Local | Configuration access |
| `core.logger` | Local | Structured logging |
| `queue` | stdlib | Priority queue for event ordering |
| `threading` | stdlib | Thread pool for async delivery |
| `json` | stdlib | Message serialization |
