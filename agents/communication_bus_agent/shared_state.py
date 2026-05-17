"""
NEXUS - Agent Communication Bus
Shared state manager for inter-agent data sharing with thread-safe access,
locking, versioning, TTL, and change notifications.
"""

import time
import threading
from typing import Any, Callable, Dict, List, Optional, Set
from datetime import datetime

from core.logger import Logger
from core.config import Config
from .models import SharedStateEntry
from .storage import BusStorage


class StateChangeListener:
    """Represents a listener for state changes."""

    def __init__(self, key_pattern: str, callback: Callable, agent_name: str = ""):
        self.key_pattern = key_pattern
        self.callback = callback
        self.agent_name = agent_name
        self.is_active = True

    def matches_key(self, key: str) -> bool:
        if self.key_pattern == "*":
            return True
        if self.key_pattern == key:
            return True
        if self.key_pattern.endswith(".*"):
            return key.startswith(self.key_pattern[:-2])
        return False


class SharedStateManager:
    """
    Thread-safe shared state manager for inter-agent data sharing.
    Supports key-value storage with locking, versioning, TTL,
    change notifications, and namespace isolation.
    """

    def __init__(self, storage: Optional[BusStorage] = None):
        self.logger = Logger().get_logger("SharedStateManager")
        self.config = Config()
        self.storage = storage or BusStorage()

        self._store: Dict[str, SharedStateEntry] = {}
        self._lock = threading.RLock()
        self._condition = threading.Condition(self._lock)

        self._listeners: List[StateChangeListener] = []
        self._listener_lock = threading.Lock()

        self._namespaces: Dict[str, Set[str]] = {"global": set()}
        self._namespace_lock = threading.Lock()

        self._access_log: List[Dict[str, Any]] = []
        self._access_log_lock = threading.Lock()
        self._max_access_log = 1000

        self._cleanup_thread = threading.Thread(
            target=self._cleanup_loop, daemon=True, name="SharedStateCleanup"
        )
        self._running = True
        self._cleanup_thread.start()

        self._load_from_storage()
        self.logger.info("SharedStateManager initialized")

    def _load_from_storage(self):
        """Load existing state entries from storage."""
        try:
            entries = self.storage.get_all_state_entries()
            for entry_data in entries:
                entry = SharedStateEntry(
                    key=entry_data["key"],
                    value=entry_data["value"],
                    owner=entry_data.get("owner", ""),
                    ttl=entry_data.get("ttl", 0),
                    is_locked=bool(entry_data.get("is_locked", False)),
                    lock_owner=entry_data.get("lock_owner", ""),
                    version=entry_data.get("version", 1),
                    created_at=datetime.fromisoformat(entry_data["created_at"]),
                    updated_at=datetime.fromisoformat(entry_data["updated_at"]),
                    access_count=entry_data.get("access_count", 0),
                    metadata=entry_data.get("metadata", {}),
                )
                if not entry.is_expired():
                    self._store[entry.key] = entry
                    namespace = entry.metadata.get("namespace", "global")
                    with self._namespace_lock:
                        if namespace not in self._namespaces:
                            self._namespaces[namespace] = set()
                        self._namespaces[namespace].add(entry.key)
            self.logger.info(f"Loaded {len(self._store)} state entries from storage")
        except Exception as e:
            self.logger.error(f"Failed to load state from storage: {e}")

    def set(
        self,
        key: str,
        value: Any,
        owner: str = "",
        ttl: int = 0,
        namespace: str = "global",
        notify: bool = True,
    ) -> bool:
        """
        Set a value in the shared state.
        Returns True if successful, False if key is locked by another owner.
        """
        with self._lock:
            full_key = f"{namespace}:{key}" if namespace != "global" else key

            if full_key in self._store:
                existing = self._store[full_key]
                if existing.is_locked and existing.lock_owner != owner:
                    self.logger.warning(f"Key {full_key} is locked by {existing.lock_owner}")
                    return False
                existing.value = value
                existing.version += 1
                existing.updated_at = datetime.now()
                if ttl > 0:
                    existing.ttl = ttl
                if owner:
                    existing.owner = owner
            else:
                entry = SharedStateEntry(
                    key=full_key,
                    value=value,
                    owner=owner,
                    ttl=ttl,
                    version=1,
                    metadata={"namespace": namespace},
                )
                self._store[full_key] = entry

                with self._namespace_lock:
                    if namespace not in self._namespaces:
                        self._namespaces[namespace] = set()
                    self._namespaces[namespace].add(full_key)

            self.storage.save_state_entry(self._store[full_key].to_dict())
            self._log_access("set", full_key, owner)

        if notify:
            self._notify_listeners(full_key, "set", value)

        self.logger.debug(f"State set: {full_key} (version={self._store[full_key].version})")
        return True

    def get(self, key: str, namespace: str = "global", default: Any = None) -> Any:
        """Get a value from the shared state."""
        full_key = f"{namespace}:{key}" if namespace != "global" else key

        with self._lock:
            if full_key not in self._store:
                return default

            entry = self._store[full_key]

            if entry.is_expired():
                del self._store[full_key]
                self.storage.delete_state_entry(full_key)
                return default

            entry.access_count += 1
            self.storage.save_state_entry(entry.to_dict())
            self._log_access("get", full_key, entry.owner)

            return entry.value

    def delete(self, key: str, owner: str = "", namespace: str = "global") -> bool:
        """Delete a value from the shared state."""
        full_key = f"{namespace}:{key}" if namespace != "global" else key

        with self._lock:
            if full_key not in self._store:
                return False

            entry = self._store[full_key]
            if entry.is_locked and entry.lock_owner != owner:
                self.logger.warning(f"Cannot delete locked key {full_key}")
                return False

            del self._store[full_key]
            self.storage.delete_state_entry(full_key)

            with self._namespace_lock:
                if namespace in self._namespaces:
                    self._namespaces[namespace].discard(full_key)

            self._log_access("delete", full_key, owner)

        self._notify_listeners(full_key, "delete", None)
        self.logger.debug(f"State deleted: {full_key}")
        return True

    def lock(self, key: str, owner: str, namespace: str = "global", timeout: int = 0) -> bool:
        """
        Lock a state entry for exclusive access.
        Returns True if lock acquired, False if already locked.
        """
        full_key = f"{namespace}:{key}" if namespace != "global" else key

        with self._lock:
            if full_key not in self._store:
                self._store[full_key] = SharedStateEntry(key=full_key, value=None, owner=owner)

            entry = self._store[full_key]

            if entry.is_locked:
                if entry.lock_owner == owner:
                    return True
                return False

            entry.is_locked = True
            entry.lock_owner = owner
            entry.version += 1
            entry.updated_at = datetime.now()

            self.storage.save_state_entry(entry.to_dict())
            self.logger.debug(f"State locked: {full_key} by {owner}")
            return True

    def unlock(self, key: str, owner: str, namespace: str = "global") -> bool:
        """Unlock a state entry."""
        full_key = f"{namespace}:{key}" if namespace != "global" else key

        with self._lock:
            if full_key not in self._store:
                return False

            entry = self._store[full_key]
            if entry.lock_owner != owner:
                return False

            entry.is_locked = False
            entry.lock_owner = ""
            entry.version += 1
            entry.updated_at = datetime.now()

            self.storage.save_state_entry(entry.to_dict())
            self.logger.debug(f"State unlocked: {full_key} by {owner}")
            return True

    def update_if_version(
        self, key: str, value: Any, version: int, owner: str = "", namespace: str = "global"
    ) -> bool:
        """
        Optimistic concurrency update.
        Only updates if the current version matches the expected version.
        """
        full_key = f"{namespace}:{key}" if namespace != "global" else key

        with self._lock:
            if full_key not in self._store:
                return False

            entry = self._store[full_key]
            if entry.version != version:
                self.logger.debug(f"Version mismatch for {full_key}: expected {version}, got {entry.version}")
                return False

            if entry.is_locked and entry.lock_owner != owner:
                return False

            entry.value = value
            entry.version += 1
            entry.updated_at = datetime.now()
            if owner:
                entry.owner = owner

            self.storage.save_state_entry(entry.to_dict())
            self._notify_listeners(full_key, "update", value)
            return True

    def get_with_version(self, key: str, namespace: str = "global") -> Optional[Dict[str, Any]]:
        """Get a value along with its version for optimistic concurrency."""
        full_key = f"{namespace}:{key}" if namespace != "global" else key

        with self._lock:
            if full_key not in self._store:
                return None

            entry = self._store[full_key]
            if entry.is_expired():
                del self._store[full_key]
                return None

            return {
                "value": entry.value,
                "version": entry.version,
                "owner": entry.owner,
                "is_locked": entry.is_locked,
                "updated_at": entry.updated_at.isoformat(),
            }

    def exists(self, key: str, namespace: str = "global") -> bool:
        """Check if a key exists and is not expired."""
        full_key = f"{namespace}:{key}" if namespace != "global" else key

        with self._lock:
            if full_key not in self._store:
                return False
            entry = self._store[full_key]
            if entry.is_expired():
                del self._store[full_key]
                return False
            return True

    def get_all(self, namespace: Optional[str] = None) -> Dict[str, Any]:
        """Get all non-expired state entries, optionally filtered by namespace."""
        with self._lock:
            result = {}
            for key, entry in self._store.items():
                if entry.is_expired():
                    continue
                if namespace and entry.metadata.get("namespace") != namespace:
                    continue
                result[key] = {
                    "value": entry.value,
                    "version": entry.version,
                    "owner": entry.owner,
                    "is_locked": entry.is_locked,
                    "access_count": entry.access_count,
                    "updated_at": entry.updated_at.isoformat(),
                }
            return result

    def get_keys(self, namespace: Optional[str] = None) -> List[str]:
        """Get all keys, optionally filtered by namespace."""
        with self._lock:
            keys = []
            for key, entry in self._store.items():
                if entry.is_expired():
                    continue
                if namespace and entry.metadata.get("namespace") != namespace:
                    continue
                keys.append(key)
            return keys

    def add_listener(self, key_pattern: str, callback: Callable, agent_name: str = "") -> str:
        """Add a listener for state changes matching a key pattern."""
        listener = StateChangeListener(key_pattern, callback, agent_name)
        with self._listener_lock:
            self._listeners.append(listener)
        self.logger.debug(f"State listener added: {agent_name} -> {key_pattern}")
        return key_pattern

    def remove_listener(self, callback: Callable):
        """Remove a listener by callback reference."""
        with self._listener_lock:
            self._listeners = [l for l in self._listeners if l.callback != callback]

    def _notify_listeners(self, key: str, action: str, value: Any):
        """Notify all matching listeners of a state change."""
        with self._listener_lock:
            for listener in self._listeners:
                if listener.is_active and listener.matches_key(key):
                    try:
                        listener.callback(key, action, value)
                    except Exception as e:
                        self.logger.error(f"State listener error: {e}")

    def _log_access(self, action: str, key: str, owner: str):
        """Log a state access for analytics."""
        entry = {
            "action": action,
            "key": key,
            "owner": owner,
            "timestamp": time.time(),
        }
        with self._access_log_lock:
            self._access_log.append(entry)
            if len(self._access_log) > self._max_access_log:
                self._access_log = self._access_log[-self._max_access_log // 2:]

    def _cleanup_loop(self):
        """Background loop that removes expired entries."""
        while self._running:
            try:
                time.sleep(60)
                with self._lock:
                    expired_keys = [
                        key for key, entry in self._store.items()
                        if entry.is_expired() and not entry.is_locked
                    ]
                    for key in expired_keys:
                        del self._store[key]
                        self.storage.delete_state_entry(key)
                        self._notify_listeners(key, "expired", None)
                    if expired_keys:
                        self.logger.debug(f"Cleaned up {len(expired_keys)} expired state entries")

                expired_count = self.storage.delete_expired_state_entries()

            except Exception as e:
                self.logger.error(f"State cleanup error: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get shared state statistics."""
        with self._lock:
            total = len(self._store)
            locked = sum(1 for e in self._store.values() if e.is_locked)
            expired = sum(1 for e in self._store.values() if e.is_expired())

        with self._listener_lock:
            active_listeners = sum(1 for l in self._listeners if l.is_active)

        with self._namespace_lock:
            namespaces = dict(self._namespaces)

        return {
            "total_entries": total,
            "locked_entries": locked,
            "expired_entries": expired,
            "active_entries": total - expired,
            "active_listeners": active_listeners,
            "namespaces": {ns: len(keys) for ns, keys in namespaces.items()},
        }

    def shutdown(self):
        """Shutdown the shared state manager."""
        self.logger.info("Shutting down SharedStateManager...")
        self._running = True
        self.logger.info("SharedStateManager shutdown complete")
