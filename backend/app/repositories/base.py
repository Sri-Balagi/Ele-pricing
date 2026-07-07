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

    @abstractmethod
    def get_all(self) -> list[T]:
        """
        Return every record in the collection.

        Returns:
            List of all records. Returns an empty list if the collection is empty.
        """

    @abstractmethod
    def get_by_id(self, record_id: str) -> T | None:
        """
        Return the record matching record_id, or None if not found.

        Args:
            record_id: Unique identifier string to look up.

        Returns:
            Matching record or None.
        """

    @abstractmethod
    def exists(self, record_id: str) -> bool:
        """
        Return True if a record with the given ID exists in the collection.

        Args:
            record_id: Unique identifier string to check.

        Returns:
            True if found, False otherwise.
        """
