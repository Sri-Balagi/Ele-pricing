"""
Tests for startup validation logic.

Coverage:
  - validate_data_files() passes with all 5 files present and valid
  - validate_data_files() raises RuntimeError when any file is missing
  - validate_data_files() raises RuntimeError when any file has invalid JSON
  - Error message includes the problematic filename
"""

import json
from pathlib import Path

import pytest

from app.core.startup import validate_data_files

ALL_DATA_FILES = [
    "components.json",
    "features.json",
    "dependencies.json",
    "rules.json",
    "pricing.json",
]


def _write_all_stubs(directory: Path) -> None:
    """Write all required stub files to directory."""
    for filename in ALL_DATA_FILES:
        content = {} if filename == "pricing.json" else []
        (directory / filename).write_text(json.dumps(content), encoding="utf-8")


class TestValidateDataFiles:
    def test_passes_with_all_valid_files(self, tmp_path: Path) -> None:
        _write_all_stubs(tmp_path)
        # Should not raise
        validate_data_files(str(tmp_path))

    def test_raises_runtime_error_when_file_missing(self, tmp_path: Path) -> None:
        # Create only 4 of the 5 required files
        for filename in ALL_DATA_FILES[:-1]:  # skip pricing.json
            (tmp_path / filename).write_text("[]", encoding="utf-8")

        with pytest.raises(RuntimeError) as exc_info:
            validate_data_files(str(tmp_path))

        assert "pricing.json" in str(exc_info.value)

    def test_raises_runtime_error_when_all_files_missing(self, tmp_path: Path) -> None:
        with pytest.raises(RuntimeError):
            validate_data_files(str(tmp_path))

    def test_raises_runtime_error_for_invalid_json(self, tmp_path: Path) -> None:
        _write_all_stubs(tmp_path)
        # Corrupt one file
        (tmp_path / "rules.json").write_text("{ INVALID JSON }", encoding="utf-8")

        with pytest.raises(RuntimeError) as exc_info:
            validate_data_files(str(tmp_path))

        assert "rules.json" in str(exc_info.value)

    def test_error_message_lists_all_failing_files(self, tmp_path: Path) -> None:
        # Provide no files at all
        with pytest.raises(RuntimeError) as exc_info:
            validate_data_files(str(tmp_path))

        error_text = str(exc_info.value)
        # At least one data filename should appear in the message
        assert any(f in error_text for f in ALL_DATA_FILES)
