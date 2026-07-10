"""
DataLoader — responsible for loading, caching, and validating JSON data files.

Responsibilities (Single Responsibility Principle):
  - File I/O and JSON parsing ONLY.
  - No business logic, no Pydantic model mapping.
  - Raises domain exceptions, never raw IOError or json.JSONDecodeError.

Cache strategy:
  - Simple dict-based in-memory cache.
  - First call to load() reads from disk; subsequent calls return the cached object.
  - reload() bypasses cache for a single file.
  - reload_all() invalidates the entire cache.

Dependency injection:
  - DataLoader is instantiated with data_dir so it is trivially testable
    using a temporary directory — no monkeypatching needed.
"""

import json
import logging
from pathlib import Path
from typing import Any

from app.core.constants import DataFile
from app.core.exceptions import (
    DataFileNotFoundException,
    DataFormatException,
    DataLoadException,
)

logger = logging.getLogger(__name__)


class DataLoader:
    """
    Load and cache JSON data files from the configured data directory.

    Args:
        data_dir: Path string to the directory containing JSON data files.

    Example:
        loader = DataLoader(data_dir="app/data")
        components = loader.load("components.json")   # list[dict]
        loader.reload("components.json")              # force re-read
        loader.reload_all()                           # clear entire cache
    """

    def __init__(self, data_dir: str) -> None:
        self._data_dir: Path = Path(data_dir)
        self._cache: dict[str, Any] = {}

    # ── Public API ────────────────────────────────────────────────────────────

    def load(self, filename: str) -> list | dict:
        """
        Return parsed JSON content for filename. Result is cached after first call.

        Args:
            filename: Base filename (e.g. "components.json").

        Returns:
            Parsed JSON as a list or dict.

        Raises:
            DataFileNotFoundException: The file does not exist on disk.
            DataFormatException: The file exists but contains invalid JSON.
            DataLoadException: Any other I/O error (permissions, etc.).
        """
        if filename not in self._cache:
            logger.debug("Cache miss — loading from disk: %s", filename)
            self._cache[filename] = self._read(filename)
        else:
            logger.debug("Cache hit: %s", filename)

        return self._cache[filename]

    def reload(self, filename: str) -> list | dict:
        """
        Force a re-read of filename from disk, ignoring any cached value.

        Args:
            filename: Base filename to reload.

        Returns:
            Fresh parsed JSON content.
        """
        logger.info("Reloading data file from disk: %s", filename)
        self._cache.pop(filename, None)
        return self.load(filename)

    def reload_all(self) -> None:
        """Invalidate the entire in-memory cache. All files will be re-read on next access."""
        logger.info(
            "Invalidating entire DataLoader cache (%d entries).", len(self._cache)
        )
        self._cache.clear()

    def validate_file(self, filename: str) -> bool:
        """
        Return True if filename exists and is valid JSON. Does NOT update the cache.

        Args:
            filename: Base filename to validate.

        Returns:
            True if the file can be loaded successfully, False otherwise.
        """
        try:
            self._read(filename)
            return True
        except (
            DataFileNotFoundException,
            DataFormatException,
            DataLoadException,
        ) as exc:
            logger.warning("Validation failed for '%s': %s", filename, exc.message)
            return False

    def validate_all(self) -> dict[str, bool]:
        """
        Validate every required JSON data file listed in DataFile enum.

        Returns:
            Mapping of filename → True/False for each required data file.

        Example:
            {
                "components.json": True,
                "features.json": True,
                "dependencies.json": False,   ← missing or corrupt
                "rules.json": True,
                "pricing.json": True,
            }
        """
        return {
            data_file.value: self.validate_file(data_file.value)
            for data_file in DataFile
        }

    # ── Internal ──────────────────────────────────────────────────────────────

    def _read(self, filename: str) -> list | dict:
        """
        Read and parse a JSON file from the data directory.

        Args:
            filename: Base filename to read.

        Returns:
            Parsed JSON as list or dict.

        Raises:
            DataFileNotFoundException: File path does not exist.
            DataFormatException: File contains invalid JSON.
            DataLoadException: Any unexpected I/O error.
        """
        file_path = self._data_dir / filename

        if not file_path.exists():
            logger.error("Data file not found: %s", file_path)
            raise DataFileNotFoundException(
                message=f"Required data file not found: '{filename}'",
                details={"path": str(file_path)},
            )

        try:
            content = file_path.read_text(encoding="utf-8")
        except OSError as exc:
            logger.error("Failed to read data file '%s': %s", file_path, exc)
            raise DataLoadException(
                message=f"Cannot read data file: '{filename}'",
                details={"path": str(file_path), "os_error": str(exc)},
            ) from exc

        try:
            data = json.loads(content)
        except json.JSONDecodeError as exc:
            logger.error(
                "Invalid JSON in '%s' at line %d, col %d: %s",
                file_path,
                exc.lineno,
                exc.colno,
                exc.msg,
            )
            raise DataFormatException(
                message=f"Malformed JSON in data file: '{filename}'",
                details={
                    "path": str(file_path),
                    "line": exc.lineno,
                    "column": exc.colno,
                    "error": exc.msg,
                },
            ) from exc

        logger.debug("Loaded '%s' (%d bytes).", filename, len(content))
        return data
