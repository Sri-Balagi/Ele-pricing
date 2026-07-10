"""
Tests for CatalogueValidator.

Coverage:
  - Validates correct catalogue data structure.
  - Catches duplicate IDs.
  - Catches missing 'id' fields.
  - Catches invalid foreign keys (Feature -> Category, Feature -> Group, FeatureOption -> Feature, Dependency -> Component).
  - Schema validation catches bad types or missing required fields.
"""

import json
from pathlib import Path

import pytest

from app.utils.catalogue_validator import (
    CatalogueValidationException,
    CatalogueValidator,
)
from app.utils.data_loader import DataLoader


@pytest.fixture
def temp_loader(tmp_path: Path) -> DataLoader:
    """Provides a DataLoader pointing to a temporary, modifiable directory."""
    return DataLoader(data_dir=str(tmp_path))


def write_stubs(directory: Path, overrides: dict = None) -> None:
    """Writes valid stubs, allowing specific files to be overridden."""
    if overrides is None:
        overrides = {}

    stubs = {
        "catalog_metadata.json": [
            {
                "catalogue_version": "1.0",
                "schema_version": "1.0",
                "created_date": "2026-01-01T00:00:00Z",
                "last_updated": "2026-01-01T00:00:00Z",
                "prototype_version": "1.0",
                "supported_schema_versions": ["1.0"],
                "migration_metadata": {},
            }
        ],
        "categories.json": [
            {
                "id": "CAT-A",
                "name": "A",
                "description": "desc",
                "active": True,
                "metadata": {},
            }
        ],
        "feature_groups.json": [
            {
                "id": "GRP-1",
                "name": "Grp",
                "description": "desc",
                "display_order": 1,
                "active": True,
            }
        ],
        "features.json": [
            {
                "id": "F-1",
                "name": "Feat",
                "description": "desc",
                "category_id": "CAT-A",
                "group_id": "GRP-1",
                "required": True,
                "configurable": True,
                "active": True,
                "metadata": {},
            }
        ],
        "feature_options.json": [
            {
                "id": "OPT-1",
                "feature_id": "F-1",
                "display_name": "Opt1",
                "internal_value": 1,
                "description": "",
                "active": True,
                "metadata": {},
            }
        ],
        "components.json": [
            {
                "id": "COMP-1",
                "name": "Comp1",
                "description": "",
                "category": "Mechanical",
                "manufacturer": "Gen",
                "unit": "pcs",
                "specifications": {},
                "active": True,
                "metadata": {},
            }
        ],
        "feature_mappings.json": [
            {
                "id": "MAP-1",
                "feature_option_id": "OPT-1",
                "component_id": "COMP-1",
                "quantity": 1,
                "action": "ADD",
                "active": True,
            }
        ],
        "dependencies.json": [
            {
                "id": "DEP-1",
                "source_id": "OPT-1",
                "target_id": "COMP-1",
                "dependency_type": "REQUIRES",
                "description": "",
                "priority": 100,
                "condition_expression": None,
            }
        ],
        "rules.json": [],
        "pricing.json": {},
    }

    # Apply overrides
    for k, v in overrides.items():
        stubs[k] = v

    for filename, content in stubs.items():
        (directory / filename).write_text(json.dumps(content), encoding="utf-8")


def test_validator_passes_valid_data(tmp_path: Path, temp_loader: DataLoader):
    write_stubs(tmp_path)
    validator = CatalogueValidator(temp_loader)
    validator.validate()  # should not raise


def test_validator_catches_duplicate_id(tmp_path: Path, temp_loader: DataLoader):
    # Create two categories with same ID
    cat_data = [
        {
            "id": "CAT-A",
            "name": "A",
            "description": "desc",
            "active": True,
            "metadata": {},
        },
        {
            "id": "CAT-A",
            "name": "B",
            "description": "desc",
            "active": True,
            "metadata": {},
        },
    ]
    write_stubs(tmp_path, overrides={"categories.json": cat_data})

    validator = CatalogueValidator(temp_loader)
    with pytest.raises(CatalogueValidationException) as exc:
        validator.validate()

    assert "Duplicate ID found for ElevatorCategory: CAT-A" in str(exc.value)


def test_validator_catches_missing_id(tmp_path: Path, temp_loader: DataLoader):
    cat_data = [
        {"name": "A", "description": "desc", "active": True, "metadata": {}},
    ]
    write_stubs(tmp_path, overrides={"categories.json": cat_data})

    validator = CatalogueValidator(temp_loader)
    with pytest.raises(CatalogueValidationException) as exc:
        validator.validate()

    assert "Missing 'id' in a ElevatorCategory record." in str(exc.value)


def test_validator_catches_schema_validation_failure(
    tmp_path: Path, temp_loader: DataLoader
):
    comp_data = [
        {
            "id": "COMP-1",
            "name": "Comp1",
            "description": "",
            "category": "INVALID_CATEGORY",
            "manufacturer": "Gen",
            "unit": "pcs",
            "specifications": {},
            "active": True,
            "metadata": {},
        }
    ]
    write_stubs(tmp_path, overrides={"components.json": comp_data})

    validator = CatalogueValidator(temp_loader)
    with pytest.raises(CatalogueValidationException) as exc:
        validator.validate()

    assert "Schema validation failed for Component" in str(exc.value)


def test_validator_catches_invalid_feature_category_fk(
    tmp_path: Path, temp_loader: DataLoader
):
    feat_data = [
        {
            "id": "F-1",
            "name": "Feat",
            "description": "desc",
            "category_id": "BAD-CAT",
            "group_id": "GRP-1",
            "required": True,
            "configurable": True,
            "active": True,
            "metadata": {},
        }
    ]
    write_stubs(tmp_path, overrides={"features.json": feat_data})

    validator = CatalogueValidator(temp_loader)
    with pytest.raises(CatalogueValidationException) as exc:
        validator.validate()

    assert "Feature 'F-1' references unknown category_id: BAD-CAT" in str(exc.value)


def test_validator_catches_invalid_dependency_fk(
    tmp_path: Path, temp_loader: DataLoader
):
    dep_data = [
        {
            "id": "DEP-1",
            "source_id": "OPT-1",
            "target_id": "BAD-COMP",
            "dependency_type": "REQUIRES",
            "description": "",
            "priority": 100,
            "condition_expression": None,
        }
    ]
    write_stubs(tmp_path, overrides={"dependencies.json": dep_data})

    validator = CatalogueValidator(temp_loader)
    with pytest.raises(CatalogueValidationException) as exc:
        validator.validate()

    assert "Dependency 'DEP-1' references unknown target_id: BAD-COMP" in str(exc.value)


def test_validator_catches_inactive_reference(tmp_path: Path, temp_loader: DataLoader):
    # Mark category inactive
    cat_data = [
        {
            "id": "CAT-A",
            "name": "A",
            "description": "desc",
            "active": False,
            "metadata": {},
        }
    ]
    write_stubs(tmp_path, overrides={"categories.json": cat_data})

    validator = CatalogueValidator(temp_loader)
    with pytest.raises(CatalogueValidationException) as exc:
        validator.validate()

    assert "Feature 'F-1' references inactive category_id: CAT-A" in str(exc.value)
