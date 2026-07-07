"""
JSONRepository — concrete repository backed by a single JSON array file.

Implements BaseRepository[dict[str, Any]] for the setup and early milestones.
When Pydantic domain models are introduced (Milestone 1+), the generic type
parameter can be updated to a specific model without changing the interface.

Assumptions:
  - The JSON file contains an array of objects.
  - Each object has a unique ID field (default: "id").
  - Data is read via DataLoader (cached — no repeated disk access).

Limitations (acceptable for prototype scale):
  - get_by_id is O(n) linear scan — fine for ≤6000 components.
  - No write operations — this is a read-only repository for now.
    Write support will be added if JSON persistence is required.
"""

import logging
from typing import Any

from app.repositories.base import BaseRepository
from app.utils.data_loader import DataLoader

logger = logging.getLogger(__name__)


class JSONRepository(BaseRepository[dict[str, Any]]):
    """
    Repository that reads from a JSON array file via DataLoader.

    Args:
        filename: JSON data file name (e.g. "components.json").
        loader: Injected DataLoader instance. Enables test isolation via
                a DataLoader pointing at a temporary directory.
        id_field: The dict key used as the unique identifier. Defaults to "id".
    """

    def __init__(
        self,
        filename: str,
        loader: DataLoader,
        id_field: str = "id",
    ) -> None:
        self._filename = filename
        self._loader = loader
        self._id_field = id_field

    # ── BaseRepository Implementation ─────────────────────────────────────────

    def get_all(self) -> list[dict[str, Any]]:
        """Return all records from the JSON file."""
        data = self._loader.load(self._filename)

        if not isinstance(data, list):
            logger.warning(
                "Expected a JSON array in '%s' but got %s. Returning empty list.",
                self._filename,
                type(data).__name__,
            )
            return []

        return data

    def get_by_id(self, record_id: str) -> dict[str, Any] | None:
        """
        Return the first record whose id_field matches record_id.

        Args:
            record_id: The ID value to search for (compared as string).

        Returns:
            Matching record dict, or None if not found.
        """
        for record in self.get_all():
            if str(record.get(self._id_field, "")) == record_id:
                return record
        return None

    def exists(self, record_id: str) -> bool:
        """Return True if a record with record_id exists."""
        return self.get_by_id(record_id) is not None
