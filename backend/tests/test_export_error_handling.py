from fastapi.testclient import TestClient


def test_export_invalid_format(client: TestClient, sample_configuration):
    client.app.state.store.create(sample_configuration)
    response = client.get(
        f"/api/v1/configurations/{sample_configuration.configuration_id}/export/invalid_fmt"
    )
    assert response.status_code == 400


def test_export_not_found(client: TestClient):
    response = client.get("/api/v1/configurations/nonexistent/export/json")
    assert response.status_code == 404


def test_export_draft_configuration(client: TestClient, sample_configuration):
    # Simulate a draft configuration
    from app.core.constants import ConfigurationStatus

    sample_configuration.status = ConfigurationStatus.DRAFT
    client.app.state.store.create(sample_configuration)

    response = client.get(
        f"/api/v1/configurations/{sample_configuration.configuration_id}/export/json"
    )
    assert response.status_code == 400
    assert "finalized" in response.json()["detail"]
