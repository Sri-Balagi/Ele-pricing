import asyncio
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.constants import ConfigurationStatus
from app.schemas.api.v1.requests import CreateConfigurationRequest, UpdateConfigurationRequest
from app.services.store import InMemoryConfigurationStore

def test_health_endpoints(client: TestClient):
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"
    
    resp_ready = client.get("/api/v1/health/ready")
    assert resp_ready.status_code == 200
    assert resp_ready.json()["ready"] is True

def test_system_pipeline_endpoint(client: TestClient):
    resp = client.get("/api/v1/system/pipeline")
    assert resp.status_code == 200
    data = resp.json()
    assert data["ready"] is True
    assert "RuleEngine" in data["registered_engines"]

def test_create_and_get_configuration(client: TestClient):
    payload = CreateConfigurationRequest(selected_category="CAT_1").model_dump()
    resp = client.post("/api/v1/configurations", json=payload)
    
    assert resp.status_code == 201
    data = resp.json()
    assert data["success"] is True
    assert "configuration_id" in data["data"]
    
    config_id = data["data"]["configuration_id"]
    
    # Get config
    get_resp = client.get(f"/api/v1/configurations/{config_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["data"]["configuration_id"] == config_id
    assert get_resp.json()["data"]["status"] == ConfigurationStatus.DRAFT.value

def test_update_configuration(client: TestClient):
    payload = CreateConfigurationRequest(selected_category="CAT_1").model_dump()
    create_resp = client.post("/api/v1/configurations", json=payload).json()
    config_id = create_resp["data"]["configuration_id"]
    
    update_payload = UpdateConfigurationRequest(selected_feature_options=["OPT_1", "OPT_2"]).model_dump()
    update_resp = client.put(f"/api/v1/configurations/{config_id}", json=update_payload)
    
    assert update_resp.status_code == 200
    assert update_resp.json()["data"]["selected_feature_options"] == ["OPT_1", "OPT_2"]

def test_configuration_validation_not_found(client: TestClient):
    resp = client.post("/api/v1/configurations/CFG-NONEXISTENT/validate")
    assert resp.status_code == 404
    assert resp.json()["error_code"] == "NOT_FOUND"

def test_store_eviction_policy(client: TestClient):
    # We can inject a smaller store for testing
    store = InMemoryConfigurationStore(max_configurations=3)
    client.app.state.store = store
    
    for i in range(4):
        payload = CreateConfigurationRequest(selected_category=f"CAT_{i}").model_dump()
        client.post("/api/v1/configurations", json=payload)
    
    # Store max is 3, we pushed 4 DRAFTs. The first one should be evicted.
    list_resp = client.get("/api/v1/configurations?limit=10")
    assert len(list_resp.json()["data"]) == 3
    
    # Restore the store for subsequent tests
    client.app.state.store = InMemoryConfigurationStore(max_configurations=1000)

import concurrent.futures

def test_concurrent_api_operations(client: TestClient):
    # Test 10 concurrent creations
    def create_config():
        payload = CreateConfigurationRequest(selected_category="CAT_1").model_dump()
        return client.post("/api/v1/configurations", json=payload)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(create_config) for _ in range(10)]
        results = [f.result() for f in futures]
    
    for r in results:
        assert r.status_code == 201
    
    config_id = results[0].json()["data"]["configuration_id"]
    
    # Test 10 concurrent gets
    def get_config():
        return client.get(f"/api/v1/configurations/{config_id}")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        get_futures = [executor.submit(get_config) for _ in range(10)]
        get_results = [f.result() for f in get_futures]
        
    for r in get_results:
        assert r.status_code == 200
        
    # Validation is harder to mock without valid data, but we can verify it doesn't crash on repeated calls
    def validate_config():
        return client.post(f"/api/v1/configurations/{config_id}/validate")
        
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        val_futures = [executor.submit(validate_config) for _ in range(5)]
        val_results = [f.result() for f in val_futures]
        
    # Since data might be invalid, it might return 400 (RULE_001 etc.) or 200. We just assert they all return same code
    status_codes = [r.status_code for r in val_results]
    assert len(set(status_codes)) == 1
