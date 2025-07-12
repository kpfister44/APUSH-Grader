"""
Integration tests for simplified health monitoring functionality
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


class TestHealthMonitoring:
    """Test simplified health monitoring functionality"""
    
    def setup_method(self):
        """Setup test client"""
        self.client = TestClient(app)
        
    def test_basic_health_check(self):
        """Test basic health check endpoint"""
        response = self.client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields for simplified health check
        assert "status" in data
        assert "version" in data
        assert "environment" in data
        assert "services" in data
        
        # Check that status is valid
        assert data["status"] == "healthy"
        
    def test_usage_summary_endpoint(self):
        """Test usage summary endpoint"""
        response = self.client.get("/usage/summary")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return usage summary data
        assert isinstance(data, dict)
        
    def test_health_endpoints_not_rate_limited(self):
        """Test that health endpoints are not affected by rate limiting"""
        # Make multiple requests - should all succeed (health endpoints bypass rate limiting)
        for i in range(10):
            response = self.client.get("/health")
            assert response.status_code == 200
            
            response = self.client.get("/usage/summary")
            assert response.status_code == 200