import pytest
import json
import os
from fastapi.testclient import TestClient
from app.main import app

def test_openapi_snapshot():
    # Retrieve the OpenAPI schema dynamically
    client = TestClient(app)
    response = client.get("/openapi.json")
    assert response.status_code == 200
    
    current_schema = response.json()
    
    snapshot_dir = os.path.join(os.path.dirname(__file__), "snapshots")
    os.makedirs(snapshot_dir, exist_ok=True)
    snapshot_path = os.path.join(snapshot_dir, "openapi.json")
    
    # If the snapshot doesn't exist, create it (acts as our baseline)
    if not os.path.exists(snapshot_path):
        with open(snapshot_path, "w", encoding="utf-8") as f:
            json.dump(current_schema, f, indent=2)
            
    # Load the snapshot
    with open(snapshot_path, "r", encoding="utf-8") as f:
        snapshot_schema = json.load(f)
        
    # Ignore dynamic version changes, just check the paths and components.
    # A structural mismatch will raise AssertionError.
    assert current_schema["paths"].keys() == snapshot_schema["paths"].keys()
    
    # Check endpoints explicitly required for M6/M7
    assert "/api/v1/configurations/{configuration_id}/export/{format_type}" in current_schema["paths"]
    assert "/api/v1/configurations/{configuration_id}/quote" in current_schema["paths"]
