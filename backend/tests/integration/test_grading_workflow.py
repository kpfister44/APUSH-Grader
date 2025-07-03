"""
End-to-end integration tests for the complete grading workflow.

Tests the entire pipeline: API request → preprocessing → prompt generation → AI simulation → response processing → API response.
"""

import pytest
import json
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.models.core.essay_types import EssayType
from app.models.requests.grading import GradingRequest, GradingResponse
from app.services.api.coordinator import APICoordinator
from app.services.dependencies.service_locator import get_service_locator


class TestGradingWorkflowIntegration:
    """Integration tests for complete grading workflow"""
    
    @pytest.fixture
    def client(self):
        """Create test client for API testing"""
        return TestClient(app)
    
    @pytest.fixture
    def sample_dbq_request(self):
        """Sample DBQ grading request for testing"""
        return {
            "essay_text": """
            The American Revolution fundamentally transformed American society from 1775 to 1800. 
            The revolution established new democratic principles and challenged existing social hierarchies.
            
            Document analysis shows that the revolution created new political institutions. 
            The Articles of Confederation and later the Constitution represented a departure from monarchical rule.
            Economic changes included the development of new trade relationships and the decline of British mercantile control.
            
            The revolution also had significant social impacts. While it proclaimed equality, 
            it maintained slavery and limited women's rights. However, it did create new opportunities 
            for some groups and established precedents for future democratic movements.
            """.strip(),
            "essay_type": "DBQ",
            "prompt": "Evaluate the extent to which the American Revolution changed American society in the period from 1775 to 1800."
        }
    
    @pytest.fixture
    def sample_leq_request(self):
        """Sample LEQ grading request for testing"""
        return {
            "essay_text": """
            The period from 1844 to 1877 saw significant expansion of federal power during the Civil War era.
            This expansion was driven by the necessity of war and the need to address slavery and reconstruction.
            
            Before the Civil War, the federal government had limited power compared to state governments.
            The war changed this dynamic as Lincoln took unprecedented actions including the Emancipation Proclamation
            and suspension of habeas corpus. These actions established new precedents for federal authority.
            
            During Reconstruction, federal power continued to expand through constitutional amendments
            and enforcement acts. However, this expansion faced resistance and was ultimately limited
            by the Compromise of 1877 and subsequent Supreme Court decisions.
            """.strip(),
            "essay_type": "LEQ", 
            "prompt": "Evaluate the extent to which federal power expanded from 1844 to 1877."
        }
    
    @pytest.fixture
    def sample_saq_request(self):
        """Sample SAQ grading request for testing"""
        return {
            "essay_text": """
            A) The Second Great Awakening was a religious revival movement in the early 1800s 
            that emphasized personal salvation and emotional religious experiences.
            
            B) The Second Great Awakening led to increased participation in reform movements.
            For example, many abolitionists like William Lloyd Garrison were motivated by religious beliefs
            about the moral imperative to end slavery. The temperance movement also grew from religious concerns about alcohol's moral effects.
            
            C) The Second Great Awakening was significant because it democratized religion and promoted
            the idea that individuals could work to improve society. This laid the groundwork for later
            progressive movements and reinforced American beliefs in individual agency and social reform.
            """.strip(),
            "essay_type": "SAQ",
            "prompt": "A) Identify ONE way the Second Great Awakening influenced American society. B) Explain how the Second Great Awakening contributed to reform movements. C) Explain the significance of the Second Great Awakening for American democratic ideals."
        }
    
    # API Endpoint Integration Tests
    
    def test_grade_dbq_endpoint_success(self, client, sample_dbq_request):
        """Test successful DBQ grading through API endpoint"""
        response = client.post("/api/v1/grade", json=sample_dbq_request)
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate response structure
        assert "score" in data
        assert "max_score" in data
        assert "percentage" in data
        assert "letter_grade" in data
        assert "performance_level" in data
        assert "breakdown" in data
        assert "overall_feedback" in data
        assert "suggestions" in data
        assert "word_count" in data
        assert "paragraph_count" in data
        
        # Validate DBQ-specific breakdown
        breakdown = data["breakdown"]
        assert "thesis" in breakdown
        assert "contextualization" in breakdown
        assert "evidence" in breakdown
        assert "analysis" in breakdown
        
        # Validate score constraints
        assert 0 <= data["score"] <= 6
        assert data["max_score"] == 6
        assert 0 <= data["percentage"] <= 100
        assert isinstance(data["suggestions"], list)
    
    def test_grade_leq_endpoint_success(self, client, sample_leq_request):
        """Test successful LEQ grading through API endpoint"""
        response = client.post("/api/v1/grade", json=sample_leq_request)
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate LEQ-specific constraints
        assert data["max_score"] == 6
        breakdown = data["breakdown"]
        assert "thesis" in breakdown
        assert "contextualization" in breakdown
        assert "evidence" in breakdown
        assert "analysis" in breakdown
    
    def test_grade_saq_endpoint_success(self, client, sample_saq_request):
        """Test successful SAQ grading through API endpoint"""
        response = client.post("/api/v1/grade", json=sample_saq_request)
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate SAQ-specific constraints
        assert data["max_score"] == 3
        breakdown = data["breakdown"]
        assert "partA" in breakdown
        assert "partB" in breakdown
        assert "partC" in breakdown
    
    def test_grade_endpoint_validation_errors(self, client):
        """Test API endpoint validation error handling"""
        
        # Test empty essay text
        response = client.post("/api/v1/grade", json={
            "essay_text": "",
            "essay_type": "DBQ",
            "prompt": "Test prompt"
        })
        assert response.status_code == 422  # Validation error
        
        # Test invalid essay type
        response = client.post("/api/v1/grade", json={
            "essay_text": "Valid essay text",
            "essay_type": "INVALID",
            "prompt": "Test prompt"
        })
        assert response.status_code == 422  # Validation error
        
        # Test missing required fields
        response = client.post("/api/v1/grade", json={
            "essay_text": "Valid essay text"
            # Missing essay_type and prompt
        })
        assert response.status_code == 422  # Validation error
    
    def test_grading_status_endpoint(self, client):
        """Test grading service status endpoint"""
        response = client.get("/api/v1/grade/status")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert "services" in data
        assert "supported_essay_types" in data
        assert "mode" in data
        
        # Validate service status structure
        services = data["services"]
        assert "api_coordinator" in services
        assert "essay_processor" in services
        assert "prompt_generator" in services
        assert "response_processor" in services
    
    # Service Integration Tests
    
    @pytest.mark.asyncio
    async def test_api_coordinator_workflow(self, sample_dbq_request):
        """Test APICoordinator end-to-end workflow"""
        service_locator = get_service_locator()
        api_coordinator = service_locator.get_api_coordinator()
        
        # Execute complete workflow
        result = await api_coordinator.grade_essay(
            essay_text=sample_dbq_request["essay_text"],
            essay_type=EssayType.DBQ,
            prompt=sample_dbq_request["prompt"]
        )
        
        # Validate result structure
        assert hasattr(result, 'score')
        assert hasattr(result, 'max_score')
        assert hasattr(result, 'breakdown')
        assert hasattr(result, 'overall_feedback')
        assert hasattr(result, 'suggestions')
        
        # Validate DBQ-specific structure
        assert 'thesis' in result.breakdown
        assert 'contextualization' in result.breakdown
        assert 'evidence' in result.breakdown
        assert 'analysis' in result.breakdown
        
        # Validate score constraints
        assert 0 <= result.score <= 6
        assert result.max_score == 6
    
    @pytest.mark.asyncio
    async def test_workflow_with_all_essay_types(self, sample_dbq_request, sample_leq_request, sample_saq_request):
        """Test workflow with all supported essay types"""
        service_locator = get_service_locator()
        api_coordinator = service_locator.get_api_coordinator()
        
        test_cases = [
            (sample_dbq_request, EssayType.DBQ, 6),
            (sample_leq_request, EssayType.LEQ, 6),
            (sample_saq_request, EssayType.SAQ, 3)
        ]
        
        for request_data, essay_type, expected_max_score in test_cases:
            result = await api_coordinator.grade_essay(
                essay_text=request_data["essay_text"],
                essay_type=essay_type,
                prompt=request_data["prompt"]
            )
            
            assert result.max_score == expected_max_score
            assert 0 <= result.score <= expected_max_score
            assert len(result.breakdown) > 0
            assert len(result.overall_feedback) > 0
    
    # Mock AI Response Tests
    
    @pytest.mark.asyncio
    async def test_mock_ai_response_generation(self):
        """Test mock AI response generation for all essay types"""
        service_locator = get_service_locator()
        ai_service = service_locator.get_ai_service()
        
        # Test each essay type's mock response
        essay_types = [EssayType.DBQ, EssayType.LEQ, EssayType.SAQ]
        
        for essay_type in essay_types:
            mock_response = await ai_service.generate_response(
                "System prompt", "User message", essay_type
            )
            
            # Should be valid JSON
            response_data = json.loads(mock_response)
            
            # Validate basic structure
            assert "score" in response_data
            assert "maxScore" in response_data
            assert "breakdown" in response_data
            assert "overallFeedback" in response_data
            assert "suggestions" in response_data
            
            # Validate score constraints
            if essay_type in [EssayType.DBQ, EssayType.LEQ]:
                assert response_data["maxScore"] == 6
                assert 0 <= response_data["score"] <= 6
            else:  # SAQ
                assert response_data["maxScore"] == 3
                assert 0 <= response_data["score"] <= 3
    
    # Error Handling Tests
    
    @pytest.mark.asyncio
    async def test_workflow_error_handling(self):
        """Test error handling in the complete workflow"""
        service_locator = get_service_locator()
        api_coordinator = service_locator.get_api_coordinator()
        
        # Test with invalid essay type (should raise ValueError)
        with pytest.raises(Exception):
            await api_coordinator.grade_essay(
                essay_text="Valid essay text",
                essay_type="INVALID_TYPE",  # This will cause an error
                prompt="Valid prompt"
            )
    
    def test_api_error_response_format(self, client):
        """Test API error response format consistency"""
        # Test with very short essay that should trigger validation
        response = client.post("/api/v1/grade", json={
            "essay_text": "Too short",
            "essay_type": "DBQ", 
            "prompt": "Test prompt"
        })
        
        # Should handle gracefully and return proper error format
        # (The actual behavior depends on validation rules)
        assert response.status_code in [200, 400, 422]
        
        if response.status_code != 200:
            data = response.json()
            assert "detail" in data  # FastAPI error format
    
    # Performance and Load Tests
    
    @pytest.mark.asyncio
    async def test_concurrent_grading_requests(self, sample_dbq_request):
        """Test handling multiple concurrent grading requests"""
        import asyncio
        
        service_locator = get_service_locator()
        api_coordinator = service_locator.get_api_coordinator()
        
        # Create multiple concurrent requests
        tasks = []
        for i in range(5):  # Test with 5 concurrent requests
            task = api_coordinator.grade_essay(
                essay_text=sample_dbq_request["essay_text"],
                essay_type=EssayType.DBQ,
                prompt=sample_dbq_request["prompt"]
            )
            tasks.append(task)
        
        # Execute all requests concurrently
        results = await asyncio.gather(*tasks)
        
        # All should succeed
        assert len(results) == 5
        for result in results:
            assert hasattr(result, 'score')
            assert hasattr(result, 'max_score')
            assert result.max_score == 6
    
    def test_api_response_time(self, client, sample_leq_request):
        """Test API response time is reasonable"""
        import time
        
        start_time = time.time()
        response = client.post("/api/v1/grade", json=sample_leq_request)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 5.0  # Should respond within 5 seconds
        
        # Check that processing_time_ms is included in response
        data = response.json()
        if "processing_time_ms" in data:
            assert isinstance(data["processing_time_ms"], int)
            assert data["processing_time_ms"] > 0
    
    # Data Consistency Tests
    
    def test_response_data_consistency(self, client, sample_dbq_request):
        """Test that response data is internally consistent"""
        response = client.post("/api/v1/grade", json=sample_dbq_request)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check percentage calculation consistency
        expected_percentage = (data["score"] / data["max_score"]) * 100
        assert abs(data["percentage"] - expected_percentage) < 0.1
        
        # Check breakdown scores sum consistently
        breakdown_total = sum(
            section["score"] for section in data["breakdown"].values()
        )
        assert breakdown_total == data["score"]
        
        # Check word count is reasonable
        actual_words = len(sample_dbq_request["essay_text"].split())
        # Allow some variation due to cleaning/processing
        assert abs(data["word_count"] - actual_words) <= 5
    
    # Service Dependencies Integration Tests
    
    def test_service_locator_integration(self):
        """Test that all required services are properly registered and accessible"""
        service_locator = get_service_locator()
        
        # Test that all required services can be resolved
        essay_processor = service_locator.get_essay_processor()
        prompt_generator = service_locator.get_prompt_generator()
        response_processor = service_locator.get_response_processor()
        api_coordinator = service_locator.get_api_coordinator()
        
        # All should be non-None
        assert essay_processor is not None
        assert prompt_generator is not None
        assert response_processor is not None
        assert api_coordinator is not None
        
        # Test that services have expected interfaces
        assert hasattr(essay_processor, 'preprocess_essay')
        assert hasattr(prompt_generator, 'generate_system_prompt')
        assert hasattr(prompt_generator, 'generate_user_message')
        assert hasattr(response_processor, 'process_response')
        assert hasattr(response_processor, 'process_grading_response')
        assert hasattr(api_coordinator, 'grade_essay')
    
    # Cross-Service Integration Tests
    
    @pytest.mark.asyncio
    async def test_prompt_to_response_pipeline(self, sample_leq_request):
        """Test the pipeline from prompt generation to response processing"""
        service_locator = get_service_locator()
        
        # Get individual services
        essay_processor = service_locator.get_essay_processor()
        prompt_generator = service_locator.get_prompt_generator()
        response_processor = service_locator.get_response_processor()
        
        # Execute pipeline step by step
        essay_type = EssayType.LEQ
        
        # Step 1: Preprocess essay
        preprocessing_result = essay_processor.preprocess_essay(
            sample_leq_request["essay_text"], essay_type
        )
        assert preprocessing_result is not None
        
        # Step 2: Generate prompts
        system_prompt = prompt_generator.generate_system_prompt(essay_type)
        user_message = prompt_generator.generate_user_message(
            sample_leq_request["essay_text"],
            essay_type,
            sample_leq_request["prompt"],
            preprocessing_result
        )
        
        assert len(system_prompt) > 100
        assert len(user_message) > 100
        assert "LEQ" in system_prompt
        assert preprocessing_result.cleaned_text in user_message
        
        # Step 3: Simulate AI response
        mock_response = """
        {
            "score": 5,
            "maxScore": 6,
            "breakdown": {
                "thesis": {"score": 1, "maxScore": 1, "feedback": "Clear thesis"},
                "contextualization": {"score": 1, "maxScore": 1, "feedback": "Good context"},
                "evidence": {"score": 2, "maxScore": 2, "feedback": "Strong evidence"},
                "analysis": {"score": 1, "maxScore": 2, "feedback": "Good analysis"}
            },
            "overallFeedback": "Strong essay overall",
            "suggestions": ["Add more sophisticated analysis"]
        }
        """
        
        # Step 4: Process response
        grade_response = response_processor.process_response(
            mock_response, essay_type, preprocessing_result
        )
        
        assert grade_response.score == 5
        assert grade_response.max_score == 6
        assert "thesis" in grade_response.breakdown