"""
Tests for JSONRepository.

Coverage:
  - get_all() returns a list
  - get_all() returns correct records
  - get_all() returns empty list when file contains empty array
  - get_all() returns empty list when file contains non-array JSON (defensive)
  - get_by_id() returns correct record when ID exists
  - get_by_id() returns None when ID does not exist
  - exists() returns True for known ID
  - exists() returns False for unknown ID
  - Custom id_field is respected
"""

import json
from pathlib import Path

import pytest

from app.repositories.json_repository import JSONRepository
from app.utils.data_loader import DataLoader

SAMPLE_DATA = [
    {"id": "C001", "name": "Standard Motor", "type": "motor"},
    {"id": "C002", "name": "High-Speed Motor", "type": "motor"},
    {"id": "C003", "name": "Safety Brake", "type": "brake"},
]


@pytest.fixture()
def data_dir(tmp_path: Path) -> Path:
    (tmp_path / "components.json").write_text(
        json.dumps(SAMPLE_DATA), encoding="utf-8"
    )
    (tmp_path / "empty.json").write_text("[]", encoding="utf-8")
    (tmp_path / "not_array.json").write_text('{"key": "value"}', encoding="utf-8")
    (tmp_path / "custom_id.json").write_text(
        json.dumps([{"code": "SKU001", "label": "Item A"}]), encoding="utf-8"
    )
    return tmp_path


@pytest.fixture()
def loader(data_dir: Path) -> DataLoader:
    return DataLoader(data_dir=str(data_dir))


@pytest.fixture()
def repo(loader: DataLoader) -> JSONRepository:
    return JSONRepository(filename="components.json", loader=loader)


class TestGetAll:
    def test_returns_list(self, repo: JSONRepository) -> None:
        result = repo.get_all()
        assert isinstance(result, list)

    def test_returns_all_records(self, repo: JSONRepository) -> None:
        result = repo.get_all()
        assert len(result) == 3

    def test_returns_correct_data(self, repo: JSONRepository) -> None:
        result = repo.get_all()
        assert result == SAMPLE_DATA

    def test_empty_file_returns_empty_list(self, loader: DataLoader) -> None:
        repo = JSONRepository(filename="empty.json", loader=loader)
        assert repo.get_all() == []

    def test_non_array_json_returns_empty_list(self, loader: DataLoader) -> None:
        repo = JSONRepository(filename="not_array.json", loader=loader)
        result = repo.get_all()
        assert result == []


class TestGetById:
    def test_returns_record_for_known_id(self, repo: JSONRepository) -> None:
        result = repo.get_by_id("C001")
        assert result is not None
        assert result["id"] == "C001"
        assert result["name"] == "Standard Motor"

    def test_returns_none_for_unknown_id(self, repo: JSONRepository) -> None:
        result = repo.get_by_id("DOES_NOT_EXIST")
        assert result is None

    def test_returns_correct_record_among_multiple(self, repo: JSONRepository) -> None:
        result = repo.get_by_id("C003")
        assert result is not None
        assert result["name"] == "Safety Brake"


class TestExists:
    def test_returns_true_for_known_id(self, repo: JSONRepository) -> None:
        assert repo.exists("C001") is True

    def test_returns_true_for_last_id(self, repo: JSONRepository) -> None:
        assert repo.exists("C003") is True

    def test_returns_false_for_unknown_id(self, repo: JSONRepository) -> None:
        assert repo.exists("C999") is False

    def test_returns_false_for_empty_string(self, repo: JSONRepository) -> None:
        assert repo.exists("") is False


class TestCustomIdField:
    def test_custom_id_field_get_by_id(self, loader: DataLoader) -> None:
        repo = JSONRepository(
            filename="custom_id.json", loader=loader, id_field="code"
        )
        result = repo.get_by_id("SKU001")
        assert result is not None
        assert result["label"] == "Item A"

    def test_custom_id_field_exists(self, loader: DataLoader) -> None:
        repo = JSONRepository(
            filename="custom_id.json", loader=loader, id_field="code"
        )
        assert repo.exists("SKU001") is True
        assert repo.exists("SKU999") is False
