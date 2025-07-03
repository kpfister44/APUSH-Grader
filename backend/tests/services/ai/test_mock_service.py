"""Tests for Mock AI Service"""

import pytest
import asyncio
import json

from app.models.core.essay_types import EssayType
from app.services.ai.mock_service import MockAIService
from app.services.base.exceptions import ProcessingError


class TestMockAIService:
    """Test cases for MockAIService"""
    
    @pytest.fixture
    def mock_ai_service(self):
        """Create MockAIService instance for testing"""
        return MockAIService()
    
    @pytest.mark.asyncio
    async def test_generate_response_dbq(self, mock_ai_service):
        """Test DBQ response generation"""
        response = await mock_ai_service.generate_response(
            "system prompt", "user message", EssayType.DBQ
        )
        
        # Parse response and validate structure
        data = json.loads(response)
        assert data["score"] == 4
        assert data["maxScore"] == 6
        assert "breakdown" in data
        assert "thesis" in data["breakdown"]
        assert "contextualization" in data["breakdown"]
        assert "evidence" in data["breakdown"]
        assert "analysis" in data["breakdown"]
        assert "overallFeedback" in data
        assert "suggestions" in data
        assert isinstance(data["suggestions"], list)
    
    @pytest.mark.asyncio
    async def test_generate_response_leq(self, mock_ai_service):
        """Test LEQ response generation"""
        response = await mock_ai_service.generate_response(
            "system prompt", "user message", EssayType.LEQ
        )
        
        # Parse response and validate structure
        data = json.loads(response)
        assert data["score"] == 5
        assert data["maxScore"] == 6
        assert "breakdown" in data
        assert "thesis" in data["breakdown"]
        assert "contextualization" in data["breakdown"]
        assert "evidence" in data["breakdown"]
        assert "analysis" in data["breakdown"]
        assert "overallFeedback" in data
        assert "suggestions" in data
        assert isinstance(data["suggestions"], list)
    
    @pytest.mark.asyncio
    async def test_generate_response_saq(self, mock_ai_service):
        """Test SAQ response generation"""
        response = await mock_ai_service.generate_response(
            "system prompt", "user message", EssayType.SAQ
        )
        
        # Parse response and validate structure
        data = json.loads(response)
        assert data["score"] == 2
        assert data["maxScore"] == 3
        assert "breakdown" in data
        assert "partA" in data["breakdown"]
        assert "partB" in data["breakdown"]
        assert "partC" in data["breakdown"]
        assert "overallFeedback" in data
        assert "suggestions" in data
        assert isinstance(data["suggestions"], list)
    
    @pytest.mark.asyncio
    async def test_generate_response_unknown_type(self, mock_ai_service):
        """Test error handling for unknown essay type"""
        # Create a mock enum-like object that will fail the type checks
        class UnknownType:
            value = "UNKNOWN"
        
        with pytest.raises(ProcessingError, match="Unknown essay type"):
            await mock_ai_service.generate_response(
                "system prompt", "user message", UnknownType()
            )
    
    @pytest.mark.asyncio
    async def test_response_delay(self, mock_ai_service):
        """Test that mock service simulates processing delay"""
        import time
        start_time = time.time()
        
        await mock_ai_service.generate_response(
            "system prompt", "user message", EssayType.DBQ
        )
        
        elapsed_time = time.time() - start_time
        # Should have at least a 0.1 second delay
        assert elapsed_time >= 0.1
    
    def test_validate_configuration(self, mock_ai_service):
        """Test configuration validation (should always pass for mock)"""
        # Should not raise any exceptions
        mock_ai_service._validate_configuration()
    
    @pytest.mark.asyncio
    async def test_consistent_responses(self, mock_ai_service):
        """Test that mock service returns consistent responses"""
        response1 = await mock_ai_service.generate_response(
            "system prompt", "user message", EssayType.DBQ
        )
        response2 = await mock_ai_service.generate_response(
            "system prompt", "user message", EssayType.DBQ
        )
        
        # Responses should be identical for deterministic mock
        assert response1 == response2