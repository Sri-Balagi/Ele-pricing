"""
Tests for DataLoader.

Coverage:
  - load() returns correct data type
  - load() caches results (same object reference)
  - reload() bypasses cache and returns fresh data
  - reload_all() clears the entire cache
  - Missing file raises DataFileNotFoundException
  - Malformed JSON raises DataFormatException
  - validate_file() returns True/False correctly
  - validate_all() covers all required DataFile enum members
"""

import json
from pathlib import Path

import pytest

from app.core.exceptions import DataFileNotFoundException, DataFormatException
from app.utils.data_loader import DataLoader


@pytest.fixture()
def data_dir(tmp_path: Path) -> Path:
    """Temporary data directory with a mix of valid, empty, and bad files."""
    files = {
        "components.json": [],
        "features.json": [{"id": "F001", "name": "Feature Alpha"}],
        "bad_json.json": "THIS IS NOT { VALID JSON !!!",
    }
    for name, content in files.items():
        if isinstance(content, str):
            (tmp_path / name).write_text(content, encoding="utf-8")
        else:
            (tmp_path / name).write_text(json.dumps(content), encoding="utf-8")
    return tmp_path


@pytest.fixture()
def loader(data_dir: Path) -> DataLoader:
    return DataLoader(data_dir=str(data_dir))


class TestLoad:
    def test_returns_list_for_array_file(self, loader: DataLoader) -> None:
        result = loader.load("components.json")
        assert isinstance(result, list)

    def test_returns_correct_content(self, loader: DataLoader) -> None:
        result = loader.load("features.json")
        assert result == [{"id": "F001", "name": "Feature Alpha"}]

    def test_caches_result_same_object_reference(self, loader: DataLoader) -> None:
        first = loader.load("components.json")
        second = loader.load("components.json")
        assert first is second  # Must be identical object — not a copy

    def test_missing_file_raises_not_found(self, loader: DataLoader) -> None:
        with pytest.raises(DataFileNotFoundException) as exc_info:
            loader.load("does_not_exist.json")
        assert "does_not_exist.json" in exc_info.value.message

    def test_invalid_json_raises_format_error(self, loader: DataLoader) -> None:
        with pytest.raises(DataFormatException) as exc_info:
            loader.load("bad_json.json")
        assert "bad_json.json" in exc_info.value.message

    def test_exception_carries_error_code(self, loader: DataLoader) -> None:
        with pytest.raises(DataFileNotFoundException) as exc_info:
            loader.load("missing.json")
        assert exc_info.value.error_code == "DATA_FILE_NOT_FOUND"

    def test_exception_carries_details(self, loader: DataLoader) -> None:
        with pytest.raises(DataFileNotFoundException) as exc_info:
            loader.load("missing.json")
        assert exc_info.value.details is not None
        assert "path" in exc_info.value.details


class TestReload:
    def test_reload_returns_fresh_data_after_file_change(
        self, loader: DataLoader, data_dir: Path
    ) -> None:
        loader.load("features.json")  # prime cache

        # Overwrite the file with new content
        new_data = [{"id": "F999", "name": "Updated Feature"}]
        (data_dir / "features.json").write_text(json.dumps(new_data), encoding="utf-8")

        result = loader.reload("features.json")
        assert result == new_data

    def test_reload_updates_cache(self, loader: DataLoader, data_dir: Path) -> None:
        loader.load("features.json")
        new_data = [{"id": "F888"}]
        (data_dir / "features.json").write_text(json.dumps(new_data), encoding="utf-8")

        loader.reload("features.json")
        # Subsequent load() should return the reloaded value (from cache)
        assert loader.load("features.json") == new_data


class TestReloadAll:
    def test_reload_all_empties_cache(self, loader: DataLoader) -> None:
        loader.load("components.json")
        loader.load("features.json")
        assert len(loader._cache) == 2

        loader.reload_all()
        assert loader._cache == {}


class TestValidateFile:
    def test_valid_file_returns_true(self, loader: DataLoader) -> None:
        assert loader.validate_file("components.json") is True

    def test_missing_file_returns_false(self, loader: DataLoader) -> None:
        assert loader.validate_file("nonexistent.json") is False

    def test_invalid_json_returns_false(self, loader: DataLoader) -> None:
        assert loader.validate_file("bad_json.json") is False

    def test_validate_file_does_not_populate_cache(self, loader: DataLoader) -> None:
        loader.validate_file("components.json")
        # validate_file reads without caching
        assert "components.json" not in loader._cache


class TestValidateAll:
    def test_returns_dict(self, loader: DataLoader) -> None:
        results = loader.validate_all()
        assert isinstance(results, dict)

    def test_covers_all_required_data_files(self, loader: DataLoader) -> None:
        from app.core.constants import DataFile

        results = loader.validate_all()
        for data_file in DataFile:
            assert data_file.value in results, f"Missing key: {data_file.value}"

    def test_values_are_booleans(self, loader: DataLoader) -> None:
        results = loader.validate_all()
        for filename, ok in results.items():
            assert isinstance(ok, bool), f"Expected bool for {filename}, got {type(ok)}"
