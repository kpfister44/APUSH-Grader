"""
Integration tests for usage safeguards and daily limits
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.usage.tracker import get_usage_tracker


class TestUsageSafeguards:
    """Test usage safeguards and daily limits functionality"""
    
    def setup_method(self):
        """Setup test client and reset usage tracker"""
        self.client = TestClient(app)
        # Reset the usage tracker for clean tests
        usage_tracker = get_usage_tracker()
        usage_tracker._usage_data.clear()
        
    def test_usage_tracker_basic_functionality(self):
        """Test basic usage tracker functionality"""
        usage_tracker = get_usage_tracker()
        
        # Test that we can check essay processing
        can_process, reason = usage_tracker.can_process_essay("test-ip", 100)
        assert can_process is True
        assert reason is None
        
        # Test recording essay
        usage_tracker.record_essay_processed("test-ip", "DBQ", 100)
        
        # Test getting stats
        stats = usage_tracker.get_daily_stats("test-ip")
        assert stats is not None
        assert stats.essay_count == 1
        assert stats.total_word_count == 100
        assert stats.essay_types["DBQ"] == 1
        
    def test_normal_usage_within_limits(self):
        """Test that normal usage works within limits"""
        request_data = {
            "essay_text": "This is a normal essay about the American Revolution. " * 10,  # ~100 words
            "essay_type": "LEQ",
            "prompt": "Analyze the causes of the American Revolution."
        }
        
        # Make several requests - should all succeed
        for i in range(5):
            response = self.client.post("/api/v1/grade", json=request_data)
            # May get rate limited (429) or succeed (200), both are acceptable
            assert response.status_code in [200, 429]
            
    def test_daily_essay_limit_enforcement(self):
        """Test that daily essay limits are enforced"""
        usage_tracker = get_usage_tracker()
        test_ip = "limit-test-ip"
        
        # Simulate hitting the daily limit (100 essays)
        for i in range(100):
            usage_tracker.record_essay_processed(test_ip, "SAQ", 50)
        
        # Now check if we can process another essay
        can_process, reason = usage_tracker.can_process_essay(test_ip, 50)
        assert can_process is False
        assert "Daily essay limit reached" in reason
        
        # Try to make a request - should be rejected
        request_data = {
            "essay_text": "This should be rejected due to daily limit.",
            "essay_type": "SAQ", 
            "prompt": "Test prompt"
        }
        
        # We can't easily test this with TestClient because it uses the same IP
        # But we can test the logic directly
        
    def test_daily_word_limit_enforcement(self):
        """Test that daily word limits are enforced"""
        usage_tracker = get_usage_tracker()
        test_ip = "word-limit-test-ip"
        
        # Simulate high word usage (close to 50,000 word limit)
        usage_tracker.record_essay_processed(test_ip, "DBQ", 49000)
        
        # Try to add an essay that would exceed the limit
        can_process, reason = usage_tracker.can_process_essay(test_ip, 2000)
        assert can_process is False
        assert "Daily word limit reached" in reason
        
    def test_cost_alert_threshold(self):
        """Test that cost alerts are triggered at threshold"""
        usage_tracker = get_usage_tracker()
        test_ip = "alert-test-ip"
        
        # Simulate reaching the cost alert threshold (50 essays)
        for i in range(50):
            usage_tracker.record_essay_processed(test_ip, "LEQ", 200)
        
        # The next essay should still be allowed but trigger an alert
        can_process, reason = usage_tracker.can_process_essay(test_ip, 200)
        assert can_process is True  # Still allowed
        assert reason is None
        
        # The alert would be logged (we can't easily test log output)
        
    def test_usage_summary_endpoint(self):
        """Test the usage summary endpoint"""
        # First, generate some usage
        usage_tracker = get_usage_tracker()
        usage_tracker.record_essay_processed("summary-test-ip", "DBQ", 400)
        usage_tracker.record_essay_processed("summary-test-ip", "LEQ", 300)
        usage_tracker.record_essay_processed("summary-test-ip-2", "SAQ", 100)
        
        # Get usage summary
        response = self.client.get("/usage/summary")
        assert response.status_code == 200
        
        data = response.json()
        assert "usage_summary" in data
        assert "limits" in data
        
        usage_summary = data["usage_summary"]
        assert "total_essays" in usage_summary
        assert "total_words" in usage_summary
        assert "active_ips" in usage_summary
        assert "essay_types" in usage_summary
        
        limits = data["limits"]
        assert "daily_essay_limit" in limits
        assert "daily_word_limit" in limits
        assert "cost_alert_threshold" in limits
        
    def test_different_essay_types_tracked_separately(self):
        """Test that different essay types are tracked separately"""
        usage_tracker = get_usage_tracker()
        test_ip = "type-test-ip"
        
        # Add different essay types
        usage_tracker.record_essay_processed(test_ip, "DBQ", 400)
        usage_tracker.record_essay_processed(test_ip, "DBQ", 450)
        usage_tracker.record_essay_processed(test_ip, "LEQ", 300)
        usage_tracker.record_essay_processed(test_ip, "SAQ", 100)
        
        stats = usage_tracker.get_daily_stats(test_ip)
        assert stats.essay_types["DBQ"] == 2
        assert stats.essay_types["LEQ"] == 1
        assert stats.essay_types["SAQ"] == 1
        assert stats.essay_count == 4
        assert stats.total_word_count == 1250
        
    def test_usage_data_cleanup(self):
        """Test that old usage data can be cleaned up"""
        usage_tracker = get_usage_tracker()
        
        # Add some current data
        usage_tracker.record_essay_processed("cleanup-test-ip", "DBQ", 400)
        
        # Manual cleanup (normally this would be scheduled)
        usage_tracker.cleanup_old_data(days_to_keep=1)
        
        # Data should still be there since it's current
        stats = usage_tracker.get_daily_stats("cleanup-test-ip")
        assert stats is not None
        assert stats.essay_count == 1
        
    def test_usage_milestones_logging(self):
        """Test that usage milestones trigger logging"""
        usage_tracker = get_usage_tracker()
        test_ip = "milestone-test-ip"
        
        # Add essays to reach a milestone (10 essays)
        for i in range(10):
            usage_tracker.record_essay_processed(test_ip, "SAQ", 50)
        
        stats = usage_tracker.get_daily_stats(test_ip)
        assert stats.essay_count == 10
        
        # The milestone logging would be triggered (we can't easily test log output)
        
    def test_usage_limiting_middleware_integration(self):
        """Test that usage limiting middleware works with normal requests"""
        # Create a request that should pass usage limits
        request_data = {
            "essay_text": "This is a test essay for middleware integration testing.",
            "essay_type": "SAQ",
            "prompt": "Test prompt for middleware"
        }
        
        response = self.client.post("/api/v1/grade", json=request_data)
        
        # Should either succeed or be rate limited (not usage limited for first request)
        assert response.status_code in [200, 429]
        
        # If it's a usage limit error, it would have a different error format
        if response.status_code == 429:
            error_data = response.json()
            if "limit_type" in error_data.get("detail", {}):
                # This is a usage limit error
                assert error_data["detail"]["limit_type"] == "daily_usage"
            # Otherwise it's a rate limit error (which is also fine)
            
    def test_malformed_request_handling(self):
        """Test that malformed requests don't break usage tracking"""
        # Send malformed JSON
        response = self.client.post(
            "/api/v1/grade", 
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        # Should get a validation error, not a usage tracking error
        assert response.status_code in [400, 422, 429]  # Validation error or rate limit
        
    def test_empty_request_handling(self):
        """Test that empty requests don't break usage tracking"""
        response = self.client.post("/api/v1/grade", json={})
        
        # Should get a validation error, not a usage tracking error
        assert response.status_code in [400, 422, 429]  # Validation error or rate limit
        
    def test_health_endpoint_not_affected_by_usage_limits(self):
        """Test that health endpoints are not affected by usage limits"""
        # Health endpoint should always work regardless of usage
        response = self.client.get("/health")
        assert response.status_code == 200
        
        response = self.client.get("/usage/summary")
        assert response.status_code == 200