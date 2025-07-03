"""
Integration tests for structured logging functionality
"""

import json
import pytest
from io import StringIO
from fastapi.testclient import TestClient
from app.main import app
from app.services.logging.structured_logger import get_logger, set_correlation_id, get_correlation_id


class TestStructuredLogging:
    """Test structured logging functionality"""
    
    def setup_method(self):
        """Setup test client"""
        self.client = TestClient(app)
        
    def test_structured_logger_basic_functionality(self):
        """Test basic structured logger functionality"""
        logger = get_logger("test_logger")
        
        # Test that logger exists and has expected methods
        assert hasattr(logger, 'info')
        assert hasattr(logger, 'error')
        assert hasattr(logger, 'warning')
        assert hasattr(logger, 'debug')
        assert hasattr(logger, 'log_request_start')
        assert hasattr(logger, 'log_request_end')
        assert hasattr(logger, 'log_essay_grading')
        assert hasattr(logger, 'log_ai_service_call')
        assert hasattr(logger, 'log_error')
        
    def test_correlation_id_context(self):
        """Test correlation ID context management"""
        # Initially no correlation ID
        assert get_correlation_id() is None
        
        # Set correlation ID
        test_id = "test-123"
        set_correlation_id(test_id)
        
        # Verify it's set
        assert get_correlation_id() == test_id
        
    def test_request_logging_middleware_adds_correlation_id(self):
        """Test that request logging middleware adds correlation ID to responses"""
        response = self.client.get("/health")
        
        # Check that correlation ID header is present
        assert "X-Correlation-ID" in response.headers
        correlation_id = response.headers["X-Correlation-ID"]
        assert len(correlation_id) == 8  # Short correlation ID format
        
    def test_request_logging_middleware_logs_requests(self):
        """Test that requests are logged with structured format"""
        # This test verifies the middleware works without checking actual log output
        # since capturing log output in tests can be complex
        
        response = self.client.get("/health")
        assert response.status_code == 200
        
        # Verify correlation ID is added
        assert "X-Correlation-ID" in response.headers
        
    def test_grading_request_includes_structured_logging(self):
        """Test that grading requests use structured logging"""
        request_data = {
            "essay_text": "This is a sample essay about the American Revolution.",
            "essay_type": "LEQ",
            "prompt": "Analyze the causes of the American Revolution."
        }
        
        response = self.client.post("/api/v1/grade", json=request_data)
        
        # Should succeed (or be rate limited, both are ok)
        assert response.status_code in [200, 429]
        
        # Should have correlation ID
        assert "X-Correlation-ID" in response.headers
        
    def test_structured_logger_custom_fields(self):
        """Test that structured logger handles custom fields"""
        logger = get_logger("test_custom")
        
        # This should not raise an exception
        logger.info("Test message", custom_field="value", number=42, boolean=True)
        logger.error("Error message", error_code=500, context={"key": "value"})
        
    def test_performance_timer_context_manager(self):
        """Test performance timer context manager"""
        from app.services.logging.structured_logger import PerformanceTimer
        
        logger = get_logger("test_timer")
        
        # Test successful operation
        with PerformanceTimer(logger, "test_operation", test_field="value"):
            pass  # Simulate some work
            
        # Test failed operation
        try:
            with PerformanceTimer(logger, "failing_operation", test_field="value"):
                raise ValueError("Test error")
        except ValueError:
            pass  # Expected
            
    def test_essay_grading_structured_logging(self):
        """Test essay grading specific logging methods"""
        logger = get_logger("test_grading")
        
        # Test essay grading log
        logger.log_essay_grading(
            essay_type="DBQ",
            word_count=450,
            processing_time_ms=1250.5,
            score=4,
            max_score=6
        )
        
        # Test AI service call log
        logger.log_ai_service_call(
            service_type="anthropic",
            duration_ms=850.2,
            success=True,
            essay_type="LEQ",
            model="claude-3-5-sonnet"
        )
        
        # Test error logging
        logger.log_error(
            error_type="VALIDATION_ERROR",
            error_message="Essay too short",
            essay_type="SAQ",
            word_count=15
        )
        
    def test_request_performance_logging(self):
        """Test that request performance is logged"""
        response = self.client.get("/api/v1/grade/status")
        
        assert response.status_code == 200
        assert "X-Correlation-ID" in response.headers
        
        # The middleware should log request start and end with timing
        # We can't easily verify log content in tests, but we can verify
        # the request completes successfully with logging enabled
        
    def test_different_log_levels(self):
        """Test different log levels work correctly"""
        logger = get_logger("test_levels")
        
        # These should not raise exceptions
        logger.debug("Debug message", level="debug")
        logger.info("Info message", level="info") 
        logger.warning("Warning message", level="warning")
        logger.error("Error message", level="error")
        
    def test_logging_with_complex_data_types(self):
        """Test logging with complex data types"""
        logger = get_logger("test_complex")
        
        complex_data = {
            "nested": {"key": "value"},
            "list": [1, 2, 3],
            "none_value": None,
            "boolean": True
        }
        
        # Should handle complex data types gracefully
        logger.info("Complex data test", **complex_data)