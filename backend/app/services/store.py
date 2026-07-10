import threading
from abc import ABC, abstractmethod
from collections import OrderedDict

from app.core.constants import ConfigurationStatus
from app.core.exceptions import ElevatorBaseException
from app.models.domain import Configuration


class StoreLimitExceededError(ElevatorBaseException):
    error_code = "STORE_LIMIT_EXCEEDED"
    http_status = 503

    def __init__(
        self,
        message: str = "Configuration store limit reached. Cannot evict non-DRAFT items.",
    ):
        super().__init__(message)


class BaseConfigurationStore(ABC):
    """Abstract interface for Configuration persistence."""

    @abstractmethod
    def create(self, config: Configuration) -> Configuration:
        pass

    @abstractmethod
    def get(self, configuration_id: str) -> Configuration | None:
        pass

    @abstractmethod
    def update(self, config: Configuration) -> Configuration:
        pass

    @abstractmethod
    def delete(self, configuration_id: str) -> bool:
        pass

    @abstractmethod
    def exists(self, configuration_id: str) -> bool:
        pass

    @abstractmethod
    def list(self, limit: int = 100, offset: int = 0) -> list[Configuration]:
        pass


class InMemoryConfigurationStore(BaseConfigurationStore):
    """
    Thread-safe, bounded in-memory store for Configurations.
    Evicts ONLY the oldest DRAFT configuration when MAX_CONFIGURATIONS is reached.
    """

    def __init__(self, max_configurations: int = 1000):
        self.max_configurations = max_configurations
        self._store: OrderedDict[str, Configuration] = OrderedDict()
        self._lock = threading.Lock()
        self.evictions_count = 0

    def _evict_oldest_draft(self) -> bool:
        """Finds and deletes the oldest DRAFT config. Returns True if evicted, False otherwise."""
        for config_id, config in self._store.items():
            if config.status == ConfigurationStatus.DRAFT:
                del self._store[config_id]
                self.evictions_count += 1
                return True
        return False

    def create(self, config: Configuration) -> Configuration:
        with self._lock:
            if len(self._store) >= self.max_configurations:
                if not self._evict_oldest_draft():
                    raise StoreLimitExceededError()
            self._store[config.configuration_id] = config
            self._store.move_to_end(config.configuration_id)
        return config

    def get(self, configuration_id: str) -> Configuration | None:
        with self._lock:
            config = self._store.get(configuration_id)
            if config:
                # Update LRU position
                self._store.move_to_end(configuration_id)
            return config

    def update(self, config: Configuration) -> Configuration:
        with self._lock:
            # If it's already there, move to end to mark recently used
            if config.configuration_id in self._store:
                self._store.move_to_end(config.configuration_id)
            elif len(self._store) >= self.max_configurations:
                if not self._evict_oldest_draft():
                    raise StoreLimitExceededError()

            self._store[config.configuration_id] = config
        return config

    def delete(self, configuration_id: str) -> bool:
        with self._lock:
            if configuration_id in self._store:
                del self._store[configuration_id]
                return True
            return False

    def exists(self, configuration_id: str) -> bool:
        with self._lock:
            return configuration_id in self._store

    def list(self, limit: int = 100, offset: int = 0) -> list[Configuration]:
        with self._lock:
            # OrderedDict values in insertion order (oldest first, because we move_to_end on access/create)
            # Or we could return reverse so newest is first. Let's return newest first.
            configs = list(reversed(self._store.values()))
            return configs[offset : offset + limit]

    def get_diagnostics(self) -> dict:
        import sys
        from datetime import datetime

        with self._lock:
            total = len(self._store)
            status_counts = {"DRAFT": 0, "VALIDATED": 0, "PRICED": 0, "APPROVED": 0}
            for config in self._store.values():
                status_name = config.status.value
                if status_name in status_counts:
                    status_counts[status_name] += 1

            utilization = (
                (total / self.max_configurations) * 100
                if self.max_configurations > 0
                else 0
            )

            oldest_age = 0
            if total > 0:
                oldest_config = next(iter(self._store.values()))
                if oldest_config.created_at:
                    try:
                        # naive parse ISO 8601
                        dt = datetime.fromisoformat(
                            oldest_config.created_at.replace("Z", "+00:00")
                        )
                        oldest_age = (datetime.now(dt.tzinfo) - dt).total_seconds()
                    except ValueError:
                        pass

            return {
                "store_backend": "InMemoryConfigurationStore",
                "max_capacity": self.max_configurations,
                "current_utilization_percent": round(utilization, 2),
                "total_configurations": total,
                "draft_count": status_counts["DRAFT"],
                "validated_count": status_counts["VALIDATED"],
                "priced_count": status_counts["PRICED"],
                "approved_count": status_counts["APPROVED"],
                "evictions": self.evictions_count,
                "estimated_memory_usage_bytes": sys.getsizeof(self._store),
                "oldest_configuration_age_seconds": round(oldest_age, 2),
            }
