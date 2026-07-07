"""
Tests for GET /api/v1/health

Coverage:
  - HTTP status code
  - Response JSON structure
  - Field types and value ranges
  - Enum values
  - Version consistency with settings
"""

from fastapi.testclient import TestClient


class TestHealthStatus:
    """Tests for health endpoint HTTP and response basics."""

    def test_returns_200_ok(self, client: TestClient) -> None:
        response = client.get("/api/v1/health")
        assert response.status_code == 200

    def test_content_type_is_json(self, client: TestClient) -> None:
        response = client.get("/api/v1/health")
        assert "application/json" in response.headers["content-type"]

    def test_response_has_x_request_id_header(self, client: TestClient) -> None:
        response = client.get("/api/v1/health")
        assert "x-request-id" in response.headers

    def test_x_request_id_is_uuid_format(self, client: TestClient) -> None:
        import uuid

        response = client.get("/api/v1/health")
        request_id = response.headers.get("x-request-id", "")
        # Should parse as a valid UUID without raising
        uuid.UUID(request_id)


class TestHealthResponseShape:
    """Tests for the shape and types of health response fields."""

    def test_has_all_required_top_level_keys(self, client: TestClient) -> None:
        data = client.get("/api/v1/health").json()
        required = {"status", "version", "environment", "uptime_seconds", "data_initialized", "data_files"}
        assert required.issubset(data.keys())

    def test_data_files_has_all_required_keys(self, client: TestClient) -> None:
        data = client.get("/api/v1/health").json()
        expected = {"components", "features", "dependencies", "rules", "pricing"}
        assert expected.issubset(data["data_files"].keys())

    def test_status_is_valid_enum_value(self, client: TestClient) -> None:
        data = client.get("/api/v1/health").json()
        assert data["status"] in ("healthy", "degraded", "unhealthy")

    def test_data_initialized_is_boolean(self, client: TestClient) -> None:
        data = client.get("/api/v1/health").json()
        assert isinstance(data["data_initialized"], bool)

    def test_uptime_is_non_negative_number(self, client: TestClient) -> None:
        data = client.get("/api/v1/health").json()
        assert isinstance(data["uptime_seconds"], float | int)
        assert data["uptime_seconds"] >= 0

    def test_version_is_string(self, client: TestClient) -> None:
        data = client.get("/api/v1/health").json()
        assert isinstance(data["version"], str)
        assert len(data["version"]) > 0

    def test_environment_is_string(self, client: TestClient) -> None:
        data = client.get("/api/v1/health").json()
        assert isinstance(data["environment"], str)


class TestHealthResponseValues:
    """Tests for the correctness of health response values."""

    def test_version_matches_settings(self, client: TestClient) -> None:
        from app.core.config import get_settings

        settings = get_settings()
        data = client.get("/api/v1/health").json()
        assert data["version"] == settings.APP_VERSION

    def test_healthy_when_all_data_files_present(self, client: TestClient) -> None:
        # The client fixture provides a valid tmp_data_dir with all 5 files
        data = client.get("/api/v1/health").json()
        assert data["status"] == "healthy"
        assert data["data_initialized"] is True

    def test_all_data_files_true_when_present(self, client: TestClient) -> None:
        data = client.get("/api/v1/health").json()
        for file_key in ("components", "features", "dependencies", "rules", "pricing"):
            assert data["data_files"][file_key] is True, f"Expected {file_key} to be True"
