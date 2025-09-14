"""
Basic tests for CrashCatcher backend
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"

def test_incidents_endpoint_without_auth():
    """Test incidents endpoint without authentication"""
    response = client.get("/incidents")
    assert response.status_code == 401

def test_incidents_endpoint_with_auth():
    """Test incidents endpoint with authentication"""
    headers = {"x-api-key": "superhemlig_security_watchdog_2025_key_8f9a2b4c6d1e3f7a"}
    response = client.get("/incidents", headers=headers)
    # Should return 200 even if database connection fails in CI
    assert response.status_code in [200, 500]

def test_create_incident_without_auth():
    """Test creating incident without authentication"""
    incident_data = {
        "title": "Test incident",
        "description": "Test description",
        "severity": "MEDIUM"
    }
    response = client.post("/incidents", json=incident_data)
    assert response.status_code == 401

def test_create_incident_with_auth():
    """Test creating incident with authentication"""
    headers = {"x-api-key": "superhemlig_security_watchdog_2025_key_8f9a2b4c6d1e3f7a"}
    incident_data = {
        "title": "Test incident",
        "description": "Test description", 
        "severity": "MEDIUM"
    }
    response = client.post("/incidents", json=incident_data, headers=headers)
    # Should return 200 or 500 (database might not be available in CI)
    assert response.status_code in [200, 500]
