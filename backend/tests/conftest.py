"""
Pytest fixtures shared across all test modules.

Fixtures defined here:
  - tmp_data_dir  (session scope): temporary directory with valid stub JSON files.
  - client        (session scope): synchronous TestClient using a test app instance.

Design decisions:
  - Session scope avoids creating a new app and TestClient for every test function.
  - DATA_DIR and LOG_DIR are overridden via environment variables before app creation.
  - get_settings.cache_clear() ensures no stale settings from previous runs.
  - The client fixture cleans up environment variables after the session.
"""

import json
import os
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app import create_app
from app.core.config import get_settings


@pytest.fixture(scope="session")
def tmp_data_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """
    Create a temporary data directory populated with valid stub JSON files.

    All five required data files are created so startup validation passes.
    Tests that need custom data should create their own tmp_path fixtures.
    """
    data_dir = tmp_path_factory.mktemp("data")

    stubs: dict[str, list | dict] = {
        "catalog_metadata.json": [{
            "catalogue_version": "1.0",
            "schema_version": "1.0",
            "created_date": "2026-01-01T00:00:00Z",
            "last_updated": "2026-01-01T00:00:00Z",
            "prototype_version": "1.0",
            "supported_schema_versions": ["1.0"],
            "migration_metadata": {}
        }],
        "categories.json": [],
        "feature_groups.json": [],
        "features.json": [],
        "feature_options.json": [],
        "components.json": [],
        "feature_mappings.json": [],
        "dependencies.json": [],
        "rules.json": [],
        "pricing.json": {
            "catalogue_version": "1.0",
            "currency": "EUR",
            "tax_configuration": {
                "enabled": True,
                "tax_name": "VAT",
                "rate": 18.0
            },
            "pricing_records": []
        },
    }

    for filename, content in stubs.items():
        (data_dir / filename).write_text(json.dumps(content), encoding="utf-8")

    return data_dir


@pytest.fixture(scope="session")
def client(tmp_data_dir: Path) -> Generator[TestClient, None, None]:
    """
    Synchronous TestClient with an isolated test app instance.

    The test app uses a temporary data directory so tests never read
    production data files. Settings are overridden via environment variables.
    """
    # Override environment before app creation
    os.environ["DATA_DIR"] = str(tmp_data_dir)
    os.environ["LOG_DIR"] = str(tmp_data_dir / "logs")
    os.environ["LOG_LEVEL"] = "WARNING"  # reduce noise during tests

    # Clear lru_cache so Settings picks up the overridden env vars
    get_settings.cache_clear()

    app = create_app()

    # TestClient as context manager triggers lifespan (startup + shutdown)
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client

    # Teardown: restore environment
    os.environ.pop("DATA_DIR", None)
    os.environ.pop("LOG_DIR", None)
    os.environ.pop("LOG_LEVEL", None)
    get_settings.cache_clear()
