"""Pytest configuration and fixtures"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Create test client for FastAPI app"""
    return TestClient(app)


@pytest.fixture
def mock_settings():
    """Mock settings for testing"""
    from app.config.settings import Settings
    return Settings(
        environment="test",
        debug=True,
        log_level="DEBUG",
        openai_api_key="test_key",
        anthropic_api_key="test_key"
    )