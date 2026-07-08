"""
Abstract base repository interface.

Design rationale:
  - Services depend on BaseRepository[T], not on any concrete implementation.
  - To swap JSON for SQL: implement SQLRepository(BaseRepository[T]).
  - Zero changes required in services, API routes, or test code.
  - Generic[T] provides typed return values for IDE auto-complete.

Note: We use Generic[T] (not PEP 695 syntax) for Python 3.11 compatibility.
      The project targets 3.12 but pip installed 3.11 packages — keep this
      compatible until the runtime is upgraded.

Currently implemented:
  - JSONRepository (json_repository.py)
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """
    Abstract interface for read-access to a data collection.

    Type parameter T represents the item type returned by the repository
    (e.g. dict[str, Any] for the setup phase, Pydantic model in later milestones).
    """

    def __init__(self, model_class=None, data_file=None):
        self.model_class = model_class
        self.data_file = data_file
        
    def get_all(self) -> list[T]:
        if not self.model_class or not self.data_file:
            return []
            
        from app.utils.data_loader import DataLoader
        from app.core.config import get_settings
        
        loader = DataLoader(data_dir=get_settings().DATA_DIR)
        raw_data = loader.load(self.data_file.value)
        
        # If it's a dict (e.g. pricing.json), just return the parsed model in a list or return directly?
        # Wait, if raw_data is a dict, parse it directly. 
        if isinstance(raw_data, dict):
            return self.model_class(**raw_data)
        
        return [self.model_class(**item) for item in raw_data] if isinstance(raw_data, list) else []

    def get_by_id(self, record_id: str) -> T | None:
        records = self.get_all()
        if not isinstance(records, list):
            return records if getattr(records, "id", None) == record_id else None
            
        for record in records:
            if getattr(record, "id", None) == record_id or getattr(record, "entity_id", None) == record_id:
                return record
        return None

    def exists(self, record_id: str) -> bool:
        return self.get_by_id(record_id) is not None
