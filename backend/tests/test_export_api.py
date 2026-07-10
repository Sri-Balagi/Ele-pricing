from fastapi.testclient import TestClient


def test_export_api_json(client: TestClient, sample_configuration):
    client.app.state.store.create(sample_configuration)

    response = client.get(
        f"/api/v1/configurations/{sample_configuration.configuration_id}/export/json"
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    data = response.json()
    assert data["schema_version"] == "1.0"


def test_export_api_pdf(client: TestClient, sample_configuration):
    client.app.state.store.create(sample_configuration)
    response = client.get(
        f"/api/v1/configurations/{sample_configuration.configuration_id}/export/pdf"
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF-")


def test_export_api_quote(client: TestClient, sample_configuration):
    from app.models.domain import QuoteMetadata, QuoteStatus

    sample_configuration.quote_metadata = QuoteMetadata(
        quote_number="QT-123",
        quote_version=1,
        status=QuoteStatus.DRAFT,
        valid_until="2026-08-08T00:00:00Z",
    )
    client.app.state.store.create(sample_configuration)
    response = client.get(
        f"/api/v1/configurations/{sample_configuration.configuration_id}/quote"
    )

    assert response.status_code == 200
    data = response.json()
    assert "quote_metadata" in data
