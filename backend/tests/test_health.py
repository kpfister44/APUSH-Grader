"""Tests for health check endpoint"""

import pytest
from fastapi.testclient import TestClient


def test_health_endpoint(client: TestClient):
    """Test health check endpoint returns correct response"""
    response = client.get("/health")
    
    assert response.status_code == 200
    
    data = response.json()
    assert "status" in data
    assert "version" in data
    assert "environment" in data
    assert "services" in data
    
    assert data["status"] == "healthy"
    assert data["version"] == "1.0.0"


def test_root_endpoint(client: TestClient):
    """Test root endpoint returns correct response"""
    response = client.get("/")
    
    assert response.status_code == 200
    
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "environment" in data
    
    assert data["message"] == "APUSH Grader API"
    assert data["version"] == "1.0.0"


def test_health_endpoint_structure(client: TestClient):
    """Test health endpoint response structure"""
    response = client.get("/health")
    data = response.json()
    
    # Verify required fields are present
    required_fields = ["status", "version", "environment", "services"]
    for field in required_fields:
        assert field in data
    
    # Verify services structure
    services = data["services"]
    assert isinstance(services, dict)
    
    # Check that API key status is reported
    assert "openai" in services
    assert "anthropic" in services