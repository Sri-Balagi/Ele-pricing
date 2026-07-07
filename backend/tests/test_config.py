"""
Tests for application Settings configuration.

Coverage:
  - Default values are correct
  - Types match expected Python types
  - Enum-constrained fields accept valid values
  - data_dir_path property returns a Path
  - is_production property logic

Note: We instantiate Settings() directly (bypassing lru_cache) so tests
are independent of global state and the cached session-level settings.
"""

from pathlib import Path

from app.core.config import Settings


class TestSettingsDefaults:
    """Verify all default values match the specification."""

    def test_app_name_default(self) -> None:
        s = Settings()
        assert s.APP_NAME == "Elevator Configuration Engine"

    def test_app_version_default(self) -> None:
        s = Settings()
        assert s.APP_VERSION == "0.1.0"

    def test_environment_default(self) -> None:
        s = Settings()
        assert s.ENVIRONMENT == "development"

    def test_debug_default_is_true(self) -> None:
        s = Settings()
        assert s.DEBUG is True

    def test_log_level_default(self) -> None:
        s = Settings()
        assert s.LOG_LEVEL == "INFO"

    def test_log_dir_default(self) -> None:
        s = Settings()
        assert s.LOG_DIR == "logs"

    def test_api_prefix_default(self) -> None:
        s = Settings()
        assert s.API_V1_PREFIX == "/api/v1"

    def test_data_dir_default(self) -> None:
        s = Settings()
        assert s.DATA_DIR == "app/data"

    def test_cors_origins_is_list(self) -> None:
        s = Settings()
        assert isinstance(s.CORS_ORIGINS, list)
        assert len(s.CORS_ORIGINS) > 0


class TestSettingsTypes:
    """Verify field types are as documented."""

    def test_debug_is_bool(self) -> None:
        s = Settings()
        assert isinstance(s.DEBUG, bool)

    def test_log_max_bytes_is_int(self) -> None:
        s = Settings()
        assert isinstance(s.LOG_MAX_BYTES, int)

    def test_log_backup_count_is_int(self) -> None:
        s = Settings()
        assert isinstance(s.LOG_BACKUP_COUNT, int)

    def test_cors_origins_items_are_strings(self) -> None:
        s = Settings()
        for origin in s.CORS_ORIGINS:
            assert isinstance(origin, str)


class TestSettingsProperties:
    """Verify computed properties."""

    def test_data_dir_path_returns_path_object(self) -> None:
        s = Settings()
        assert isinstance(s.data_dir_path, Path)

    def test_data_dir_path_matches_data_dir(self) -> None:
        s = Settings()
        assert s.data_dir_path == Path(s.DATA_DIR)

    def test_is_production_false_in_development(self) -> None:
        s = Settings()
        # Default ENVIRONMENT is "development"
        assert s.is_production is False

    def test_is_production_true_when_set(self) -> None:
        s = Settings(ENVIRONMENT="production")
        assert s.is_production is True


class TestSettingsOverride:
    """Verify that constructor overrides work (used in tests and CI)."""

    def test_override_app_version(self) -> None:
        s = Settings(APP_VERSION="9.9.9")
        assert s.APP_VERSION == "9.9.9"

    def test_override_debug_false(self) -> None:
        s = Settings(DEBUG=False)
        assert s.DEBUG is False

    def test_override_data_dir(self) -> None:
        s = Settings(DATA_DIR="/tmp/test_data")
        assert s.DATA_DIR == "/tmp/test_data"
