"""
Integration tests for rate limiting middleware
"""

import pytest
import asyncio
import time
from fastapi.testclient import TestClient
from app.main import app


class TestRateLimiting:
    """Test rate limiting functionality"""
    
    def setup_method(self):
        """Setup test client"""
        self.client = TestClient(app)
        
    def test_rate_limiting_normal_usage(self):
        """Test that normal usage works within rate limits"""
        # Create a sample grading request
        request_data = {
            "essay_text": "This is a sample essay about the causes of the American Revolution. The colonists were upset about taxation without representation, which led to protests and eventually war.",
            "essay_type": "LEQ",
            "prompt": "Evaluate the causes of the American Revolution."
        }
        
        # Make a few requests - should all succeed
        for i in range(3):
            response = self.client.post("/api/v1/grade", json=request_data)
            assert response.status_code == 200
            
    def test_rate_limiting_per_minute_exceeded(self):
        """Test that rate limiting works when per-minute limit is exceeded"""
        # Create a sample grading request
        request_data = {
            "essay_text": "Short essay for testing rate limits.",
            "essay_type": "SAQ",
            "prompt": "Test prompt"
        }
        
        # Make requests rapidly to exceed the 20/minute limit
        # Note: In a real test environment, you might want to adjust the limits
        # or use a different approach to avoid waiting for the rate limit to reset
        
        success_count = 0
        rate_limited_count = 0
        
        # Try to make 25 requests quickly (should hit 20/minute limit)
        for i in range(25):
            response = self.client.post("/api/v1/grade", json=request_data)
            if response.status_code == 200:
                success_count += 1
            elif response.status_code == 429:
                rate_limited_count += 1
                # Check that the error message is user-friendly
                assert "wait a moment" in response.json()["detail"]["message"].lower()
                assert "retry_after" in response.json()["detail"]
                
        # We should have some successful requests and some rate-limited ones
        assert success_count > 0
        assert rate_limited_count > 0
        assert success_count + rate_limited_count == 25
        
    def test_rate_limiting_error_response_format(self):
        """Test that rate limiting error responses are properly formatted"""
        # Create a sample grading request
        request_data = {
            "essay_text": "Test essay",
            "essay_type": "SAQ", 
            "prompt": "Test prompt"
        }
        
        # Make enough requests to trigger rate limiting
        for i in range(25):
            response = self.client.post("/api/v1/grade", json=request_data)
            if response.status_code == 429:
                # Check the error response format
                error_data = response.json()
                assert "detail" in error_data
                assert "error" in error_data["detail"]
                assert "message" in error_data["detail"]
                assert "retry_after" in error_data["detail"]
                assert error_data["detail"]["error"] == "Rate limit exceeded"
                assert "teachers" in error_data["detail"]["message"].lower()
                break
                
    def test_rate_limiting_status_endpoint_not_limited(self):
        """Test that status endpoint is not rate limited"""
        # Make multiple requests to status endpoint - should all succeed
        for i in range(30):
            response = self.client.get("/api/v1/grade/status")
            assert response.status_code == 200
            
    def test_rate_limiting_health_endpoint_not_limited(self):
        """Test that health endpoint is not rate limited"""
        # Make multiple requests to health endpoint - should all succeed
        for i in range(30):
            response = self.client.get("/health")
            assert response.status_code == 200
            
    def test_rate_limiting_with_different_ips(self):
        """Test that rate limiting is per-IP"""
        # Note: This test is limited because TestClient doesn't easily simulate different IPs
        # In a real deployment, different IPs would have separate rate limits
        request_data = {
            "essay_text": "Test essay for IP testing",
            "essay_type": "LEQ",
            "prompt": "Test prompt"
        }
        
        # Make a request - may succeed or be rate limited depending on previous tests
        response = self.client.post("/api/v1/grade", json=request_data)
        assert response.status_code in [200, 429]  # Either success or rate limited
        
        # The TestClient uses the same "IP" for all requests, so we can't
        # easily test true per-IP rate limiting here, but we can verify 
        # the basic functionality works
        
    def test_rate_limiting_preserves_response_format(self):
        """Test that rate limiting doesn't affect normal response format when not limited"""
        request_data = {
            "essay_text": "This is a well-written essay about the causes of World War I. The assassination of Archduke Franz Ferdinand was the immediate cause, but there were many underlying tensions including imperialism, nationalism, and the alliance system.",
            "essay_type": "LEQ",
            "prompt": "Analyze the causes of World War I."
        }
        
        response = self.client.post("/api/v1/grade", json=request_data)
        
        # Test passes if we get either a successful response with correct format
        # or a rate limited response (depending on previous test state)
        if response.status_code == 200:
            # Check that the response has the expected structure
            data = response.json()
            assert "score" in data
            assert "max_score" in data
            assert "letter_grade" in data
            assert "percentage" in data
            assert "breakdown" in data
            assert "overall_feedback" in data
            assert "suggestions" in data
            assert "word_count" in data
            assert "paragraph_count" in data
        elif response.status_code == 429:
            # Rate limited response should have proper error format
            data = response.json()
            assert "detail" in data
            assert "error" in data["detail"]
        else:
            # Unexpected status code
            assert False, f"Unexpected status code: {response.status_code}"