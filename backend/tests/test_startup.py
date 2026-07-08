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
    "feature_options.json",
    "dependencies.json",
    "rules.json",
    "pricing.json",
    "categories.json",
    "catalog_metadata.json",
    "feature_mappings.json",
    "feature_groups.json",
]


def _write_all_stubs(directory: Path) -> None:
    """Write all required stub files to directory."""
    for filename in ALL_DATA_FILES:
        if filename == "pricing.json":
            content = {
                "catalogue_version": "1.0",
                "currency": "EUR",
                "tax_configuration": {
                    "enabled": True,
                    "tax_name": "VAT",
                    "rate": 18.0
                },
                "pricing_records": []
            }
        elif filename == "catalog_metadata.json":
            content = [{
                "catalogue_version": "1.0",
                "schema_version": "1.0",
                "created_date": "2026-01-01T00:00:00Z",
                "last_updated": "2026-01-01T00:00:00Z",
                "prototype_version": "1.0",
                "supported_schema_versions": ["1.0"],
                "migration_metadata": {}
            }]
        else:
            content = []
        (directory / filename).write_text(json.dumps(content), encoding="utf-8")


class TestValidateDataFiles:
    def test_passes_with_all_valid_files(self, tmp_path: Path) -> None:
        _write_all_stubs(tmp_path)
        # Should not raise
        validate_data_files(str(tmp_path))

    def test_raises_runtime_error_when_file_missing(self, tmp_path: Path) -> None:
        # Create all except one file (e.g., feature_groups.json)
        skipped_file = "feature_groups.json"
        for filename in ALL_DATA_FILES:
            if filename == skipped_file:
                continue
            if filename == "pricing.json":
                content = {
                    "catalogue_version": "1.0",
                    "currency": "EUR",
                    "tax_configuration": {
                        "enabled": True,
                        "tax_name": "VAT",
                        "rate": 18.0
                    },
                    "pricing_records": []
                }
            elif filename == "catalog_metadata.json":
                content = [{
                    "catalogue_version": "1.0",
                    "schema_version": "1.0",
                    "created_date": "2026-01-01T00:00:00Z",
                    "last_updated": "2026-01-01T00:00:00Z",
                    "prototype_version": "1.0",
                    "supported_schema_versions": ["1.0"],
                    "migration_metadata": {}
                }]
            else:
                content = []
            (tmp_path / filename).write_text(json.dumps(content), encoding="utf-8")

        with pytest.raises(RuntimeError) as exc_info:
            validate_data_files(str(tmp_path))

        assert skipped_file in str(exc_info.value)

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
