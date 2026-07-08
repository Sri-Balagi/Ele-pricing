from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_openapi_schema_generation():
    """Verify that OpenAPI schema is generated successfully and correctly shaped."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    
    assert "openapi" in schema
    assert "info" in schema
    assert "paths" in schema
    
    paths = schema["paths"]
    
    # Verify core endpoints are registered in Swagger
    assert "/api/v1/configurations" in paths
    assert "/api/v1/configurations/{configuration_id}" in paths
    assert "/api/v1/configurations/{configuration_id}/validate" in paths
    assert "/api/v1/configurations/{configuration_id}/pricing" in paths
    assert "/api/v1/system/pipeline" in paths
    
    # Check that success and error models are defined
    components = schema.get("components", {}).get("schemas", {})
    assert "APISuccessEnvelope_Configuration_" in components or "APISuccessEnvelope_List_Configuration__" in components or any("APISuccessEnvelope" in k for k in components.keys())
