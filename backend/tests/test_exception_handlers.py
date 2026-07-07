"""
Tests for global exception handlers.

Coverage:
  - 404 returns ErrorResponse JSON shape
  - 404 success field is False
  - 404 error_code is NOT_FOUND
  - ElevatorBaseException subclasses return correct error_code and HTTP status
  - Response shape matches ErrorResponse schema
"""

from fastapi.testclient import TestClient

from app.core.exceptions import (
    DataFileNotFoundException,
    InvalidComponentException,
)


class TestNotFoundHandler:
    """Tests for the 404 global handler."""

    def test_unknown_route_returns_404(self, client: TestClient) -> None:
        response = client.get("/api/v1/this_route_does_not_exist")
        assert response.status_code == 404

    def test_404_response_success_is_false(self, client: TestClient) -> None:
        data = client.get("/api/v1/nonexistent").json()
        assert data["success"] is False

    def test_404_response_error_code_is_not_found(self, client: TestClient) -> None:
        data = client.get("/api/v1/nonexistent").json()
        assert data["error_code"] == "NOT_FOUND"

    def test_404_response_has_message(self, client: TestClient) -> None:
        data = client.get("/api/v1/nonexistent").json()
        assert isinstance(data["message"], str)
        assert len(data["message"]) > 0

    def test_404_response_has_details_key(self, client: TestClient) -> None:
        data = client.get("/api/v1/nonexistent").json()
        assert "details" in data


class TestErrorResponseSchema:
    """Verify that error responses always match the ErrorResponse schema."""

    def test_404_has_all_required_keys(self, client: TestClient) -> None:
        data = client.get("/api/v1/missing").json()
        assert {"success", "error_code", "message", "details"}.issubset(data.keys())


class TestElevatorExceptions:
    """Tests that ElevatorBaseException subclasses are handled correctly."""

    def test_elevator_exception_has_correct_attributes(self) -> None:
        exc = InvalidComponentException(
            message="Component 'C999' not found.",
            details={"id": "C999"},
        )
        assert exc.error_code == "INVALID_COMPONENT"
        assert exc.http_status == 422
        assert exc.message == "Component 'C999' not found."
        assert exc.details == {"id": "C999"}

    def test_data_file_not_found_error_code(self) -> None:
        exc = DataFileNotFoundException(message="File missing.")
        assert exc.error_code == "DATA_FILE_NOT_FOUND"
        assert exc.http_status == 500

    def test_exception_repr_contains_class_name(self) -> None:
        exc = InvalidComponentException(message="Test error.")
        assert "InvalidComponentException" in repr(exc)

    def test_exception_repr_contains_error_code(self) -> None:
        exc = InvalidComponentException(message="Test error.")
        assert "INVALID_COMPONENT" in repr(exc)
