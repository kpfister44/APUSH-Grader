"""
Integration tests for health monitoring functionality
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


class TestHealthMonitoring:
    """Test health monitoring functionality"""
    
    def setup_method(self):
        """Setup test client"""
        self.client = TestClient(app)
        
    def test_basic_health_check(self):
        """Test basic health check endpoint"""
        response = self.client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        assert "status" in data
        assert "version" in data
        assert "environment" in data
        assert "services" in data
        
        # Check service fields
        services = data["services"]
        assert "ai_service_type" in services
        assert "ai_service_status" in services
        
        # Status should be healthy for basic setup
        assert data["status"] == "healthy"
        assert data["version"] == "1.0.0"
        
    def test_detailed_health_check(self):
        """Test detailed health check endpoint"""
        response = self.client.get("/health/detailed")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        assert "overall_status" in data
        assert "timestamp" in data
        assert "environment" in data
        assert "version" in data
        assert "service_checks" in data
        assert "configuration" in data
        assert "usage_today" in data
        
        # Check service checks
        service_checks = data["service_checks"]
        assert "service_locator" in service_checks
        assert "api_coordinator" in service_checks
        assert "ai_service" in service_checks
        assert "usage_tracker" in service_checks
        
        # All services should be healthy in test environment
        assert "healthy" in service_checks["service_locator"]
        assert "available" in service_checks["api_coordinator"]
        assert "healthy" in service_checks["ai_service"]
        assert "healthy" in service_checks["usage_tracker"]
        
        # Check configuration
        config = data["configuration"]
        assert "ai_service_type" in config
        assert "environment" in config
        assert "debug" in config
        
        # Check usage data
        usage = data["usage_today"]
        assert "date" in usage
        assert "total_essays" in usage
        assert "total_words" in usage
        assert "active_ips" in usage
        
    def test_usage_summary_endpoint(self):
        """Test usage summary endpoint"""
        response = self.client.get("/usage/summary")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "usage_summary" in data
        assert "limits" in data
        
        limits = data["limits"]
        assert "daily_essay_limit" in limits
        assert "daily_word_limit" in limits
        assert "cost_alert_threshold" in limits
        
        # Check reasonable limits
        assert limits["daily_essay_limit"] == 100
        assert limits["daily_word_limit"] == 50000
        assert limits["cost_alert_threshold"] == 50
        
    def test_health_endpoints_not_rate_limited(self):
        """Test that health endpoints are not affected by rate limiting"""
        # Make multiple requests - should all succeed
        for i in range(10):
            response = self.client.get("/health")
            assert response.status_code == 200
            
            response = self.client.get("/health/detailed")
            assert response.status_code == 200
            
            response = self.client.get("/usage/summary")
            assert response.status_code == 200
            
    def test_health_check_with_mock_ai_service(self):
        """Test health check properly detects mock AI service"""
        response = self.client.get("/health/detailed")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should detect mock AI service
        service_checks = data["service_checks"]
        assert "mock" in service_checks["ai_service"].lower()
        
        # Configuration should show mock
        config = data["configuration"]
        assert config["ai_service_type"] == "mock"
        
    def test_health_check_response_format(self):
        """Test that health check responses have consistent format"""
        # Basic health check
        response = self.client.get("/health")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        
        # Detailed health check
        response = self.client.get("/health/detailed")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        
        # Usage summary
        response = self.client.get("/usage/summary")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        
    def test_health_check_includes_correlation_id(self):
        """Test that health checks include correlation IDs in response headers"""
        response = self.client.get("/health")
        assert "X-Correlation-ID" in response.headers
        
        response = self.client.get("/health/detailed")
        assert "X-Correlation-ID" in response.headers
        
        response = self.client.get("/usage/summary")
        assert "X-Correlation-ID" in response.headers
        
    def test_timestamp_format_in_detailed_health(self):
        """Test that detailed health check has proper timestamp format"""
        response = self.client.get("/health/detailed")
        
        assert response.status_code == 200
        data = response.json()
        
        timestamp = data["timestamp"]
        # Should be ISO format with Z suffix
        assert timestamp.endswith("Z")
        assert "T" in timestamp
        
    def test_service_check_status_values(self):
        """Test that service check status values are reasonable"""
        response = self.client.get("/health/detailed")
        
        assert response.status_code == 200
        data = response.json()
        
        service_checks = data["service_checks"]
        
        # All service checks should have valid status
        for service, status in service_checks.items():
            assert isinstance(status, str)
            assert len(status) > 0
            # Should not have "error" in status for healthy system
            if "error" in status.lower():
                pytest.fail(f"Service {service} has error status: {status}")
                
    def test_overall_status_determination(self):
        """Test that overall status is determined correctly"""
        response = self.client.get("/health/detailed")
        
        assert response.status_code == 200
        data = response.json()
        
        overall_status = data["overall_status"]
        service_checks = data["service_checks"]
        
        # With all services healthy, overall should be healthy
        assert overall_status == "healthy"
        
        # Verify no services report errors
        for service, status in service_checks.items():
            assert "error" not in status.lower()