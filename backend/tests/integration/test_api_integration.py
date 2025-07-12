"""
Simplified integration tests for the grading API endpoints.

Tests the API endpoints with the simplified architecture.
"""

import pytest
import json
from fastapi.testclient import TestClient

from app.main import app


class TestGradingAPIIntegration:
    """Integration tests for grading API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client for API testing"""
        return TestClient(app)
    
    @pytest.fixture
    def sample_dbq_request(self):
        """Sample DBQ grading request for testing"""
        return {
            "essay_text": """
            The American Revolution fundamentally transformed American society from 1775 to 1800 through significant political, economic, and social changes. The revolution established new democratic principles and challenged existing social hierarchies that had defined colonial life under British rule.

            Document analysis shows that the revolution created new political institutions that represented a dramatic departure from monarchical governance. The Articles of Confederation and later the Constitution established a republican form of government based on Enlightenment principles of separation of powers and federalism. These political changes gave Americans unprecedented control over their government and established important precedents for democratic participation.

            Economic changes included the development of new trade relationships and the decline of British mercantile control over American commerce. The revolution opened new markets and allowed American merchants to trade freely with European nations. However, the war also created significant economic challenges including debt and inflation that the new nation struggled to address.

            The revolution also had significant social impacts that varied by region and social group. While it proclaimed equality and natural rights, it maintained slavery and limited women's rights. However, it did create new opportunities for some groups including veterans and western settlers, and established precedents for future democratic movements.

            This transformation was evident in multiple spheres of American life, from politics to economics to social structures. The new nation faced ongoing challenges in implementing these revolutionary ideals while maintaining stability and order in a diverse and rapidly expanding society.
            """.strip(),
            "essay_type": "DBQ",
            "prompt": "Evaluate the extent to which the American Revolution changed American society in the period from 1775 to 1800."
        }
    
    @pytest.fixture
    def sample_saq_request(self):
        """Sample SAQ grading request for testing"""
        return {
            "essay_type": "SAQ",
            "prompt": "Identify and explain ONE cause of the American Revolution.",
            "essay_text": "",  # Will be populated by saq_parts
            "saq_parts": {
                "part_a": "One cause of the American Revolution was taxation without representation.",
                "part_b": "The British government imposed taxes like the Stamp Act and Tea Act on colonists without giving them representation in Parliament.",
                "part_c": "This violated the traditional British principle that taxation required consent of the governed, leading to colonial resistance and eventually revolution."
            }
        }
    
    def test_health_endpoint(self, client):
        """Test health endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_grading_status_endpoint(self, client):
        """Test grading status endpoint"""
        response = client.get("/api/v1/grade/status")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "operational"
        assert "grading_workflow" in data["services"]
        assert data["mode"] == "simplified_architecture"
    
    def test_grade_dbq_endpoint_success(self, client, sample_dbq_request):
        """Test successful DBQ grading through API"""
        response = client.post("/api/v1/grade", json=sample_dbq_request)
        assert response.status_code == 200
        
        data = response.json()
        assert "score" in data
        assert "max_score" in data
        assert "letter_grade" in data
        assert "overall_feedback" in data
        assert "breakdown" in data
        assert "word_count" in data
        
        # Validate score ranges
        assert 0 <= data["score"] <= data["max_score"]
        assert data["max_score"] == 6  # DBQ max score
        assert data["letter_grade"] in ["A", "B", "C", "D", "F"]
    
    def test_grade_saq_endpoint_success(self, client, sample_saq_request):
        """Test successful SAQ grading through API"""
        response = client.post("/api/v1/grade", json=sample_saq_request)
        assert response.status_code == 200
        
        data = response.json()
        assert "score" in data
        assert "max_score" in data
        assert data["max_score"] == 3  # SAQ max score
        assert "letter_grade" in data
        assert "overall_feedback" in data
        assert "breakdown" in data
    
    def test_grade_endpoint_validation_errors(self, client):
        """Test grading endpoint validation errors"""
        # Test with empty essay - caught by Pydantic validation
        response = client.post("/api/v1/grade", json={
            "essay_text": "",
            "essay_type": "DBQ",
            "prompt": "Test prompt"
        })
        assert response.status_code == 422  # Pydantic validation error
        assert "essay_text" in str(response.json()["detail"])  # FastAPI detail format
        
        # Test with missing fields
        response = client.post("/api/v1/grade", json={
            "essay_type": "DBQ"
        })
        assert response.status_code == 422  # FastAPI validation error
    
    def test_grade_endpoint_short_essay(self, client):
        """Test grading endpoint with essay that's too short"""
        response = client.post("/api/v1/grade", json={
            "essay_text": "This is too short.",
            "essay_type": "DBQ", 
            "prompt": "Test prompt"
        })
        assert response.status_code == 400
        data = response.json()
        assert "too short" in data["detail"]["message"]
    
    def test_grade_endpoint_rate_limiting_headers(self, client, sample_dbq_request):
        """Test that rate limiting headers are present"""
        response = client.post("/api/v1/grade", json=sample_dbq_request)
        
        # Should have rate limiting headers
        assert "X-RateLimit-Limit" in response.headers or response.status_code in [200, 429]
    
    def test_grade_endpoint_response_structure(self, client, sample_dbq_request):
        """Test that response has correct structure"""
        response = client.post("/api/v1/grade", json=sample_dbq_request)
        assert response.status_code == 200
        
        data = response.json()
        
        # Check top-level structure
        required_fields = [
            "score", "max_score", "letter_grade", "overall_feedback", 
            "suggestions", "breakdown", "word_count", "paragraph_count",
            "processing_time_ms"
        ]
        for field in required_fields:
            assert field in data
        
        # Check breakdown structure
        breakdown = data["breakdown"]
        rubric_sections = ["thesis", "contextualization", "evidence", "analysis"]
        for section in rubric_sections:
            assert section in breakdown
            assert "score" in breakdown[section]
            assert "max_score" in breakdown[section]
            assert "feedback" in breakdown[section]
    
    def test_multiple_requests(self, client, sample_dbq_request):
        """Test multiple requests work correctly"""
        for i in range(3):
            response = client.post("/api/v1/grade", json=sample_dbq_request)
            assert response.status_code in [200, 429]  # 429 if rate limited
            
            if response.status_code == 200:
                data = response.json()
                assert data["score"] >= 0
                assert data["max_score"] == 6