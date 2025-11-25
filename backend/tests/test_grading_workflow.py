"""Tests for simplified grading workflow"""

import pytest
from unittest.mock import AsyncMock, patch
from app.utils.grading_workflow import (
    grade_essay, grade_essay_with_validation, validate_grading_request
)
from app.models.core import EssayType, GradeResponse, DBQLeqBreakdown, SAQBreakdown, RubricItem
from app.models.structured_outputs import (
    DBQGradeOutput, DBQLeqBreakdownOutput, RubricItemOutput
)
from app.exceptions import ValidationError, ProcessingError, APIError


class TestGradingWorkflow:
    """Test simplified grading workflow"""
    
    def test_validate_grading_request_valid(self):
        """Test validation with valid inputs"""
        essay_text = "This is a valid essay with sufficient content for testing purposes."
        essay_type = EssayType.DBQ
        prompt = "Analyze the causes of the American Revolution"
        
        # Should not raise any exception
        validate_grading_request(essay_text, essay_type, prompt)
    
    def test_validate_grading_request_empty_essay(self):
        """Test validation with empty essay"""
        with pytest.raises(ValidationError, match="Essay text cannot be empty"):
            validate_grading_request("", EssayType.DBQ, "Valid prompt")
    
    def test_validate_grading_request_empty_prompt(self):
        """Test validation with empty prompt"""
        with pytest.raises(ValidationError, match="Essay prompt cannot be empty"):
            validate_grading_request("Valid essay text", EssayType.DBQ, "")
    
    def test_validate_grading_request_too_long_essay(self):
        """Test validation with oversized essay"""
        long_essay = "a" * 50001  # Over 50,000 character limit
        with pytest.raises(ValidationError, match="Essay text is too long"):
            validate_grading_request(long_essay, EssayType.DBQ, "Valid prompt")
    
    def test_validate_grading_request_too_long_prompt(self):
        """Test validation with oversized prompt"""
        long_prompt = "a" * 5001  # Over 5,000 character limit
        with pytest.raises(ValidationError, match="Essay prompt is too long"):
            validate_grading_request("Valid essay", EssayType.DBQ, long_prompt)
    
    @pytest.mark.skip(reason="Short essays generate warnings but don't fail - they still get graded")
    @pytest.mark.asyncio
    @patch('app.utils.grading_workflow.create_ai_service')
    async def test_grade_essay_short_essay_validation_failure(self, mock_create_ai_service):
        """Test grading workflow fails with short essay (SKIPPED - behavior changed)"""
        # Setup mock AI service (won't be called due to validation failure)
        mock_ai_service = AsyncMock()
        mock_create_ai_service.return_value = mock_ai_service

        short_essay = "Too short"

        with pytest.raises(ValidationError, match="too short"):
            await grade_essay(short_essay, EssayType.DBQ, "Test prompt")
    
    @pytest.mark.skip(reason="Short essays generate warnings but don't fail - they still get graded")
    @pytest.mark.asyncio
    @patch('app.utils.grading_workflow.create_ai_service')
    async def test_grade_essay_with_validation_short_essay(self, mock_create_ai_service):
        """Test grade_essay_with_validation fails with short essay (SKIPPED - behavior changed)"""
        # Setup mock AI service (won't be called due to validation failure)
        mock_ai_service = AsyncMock()
        mock_create_ai_service.return_value = mock_ai_service

        short_essay = "Too short"

        with pytest.raises(ValidationError, match="Essay text cannot be empty|too short"):
            await grade_essay_with_validation(short_essay, EssayType.DBQ, "Test prompt")
    
    @pytest.mark.asyncio
    @patch('app.utils.grading_workflow.create_ai_service')
    async def test_grade_essay_success_mock_ai(self, mock_create_ai_service):
        """Test successful grading with mocked AI service"""
        # Setup mock AI service with Structured Output response
        mock_ai_service = AsyncMock()

        # Create mock Structured Output (Pydantic model, not JSON string)
        mock_structured_response = DBQGradeOutput(
            score=4,
            max_score=6,
            letter_grade="B",
            overall_feedback="Good essay with clear analysis",
            suggestions=["Add more evidence"],
            breakdown=DBQLeqBreakdownOutput(
                thesis=RubricItemOutput(score=1, max_score=1, feedback="Clear thesis"),
                contextualization=RubricItemOutput(score=1, max_score=1, feedback="Good context"),
                evidence=RubricItemOutput(score=1, max_score=2, feedback="Needs more evidence"),
                analysis=RubricItemOutput(score=1, max_score=2, feedback="Solid analysis")
            )
        )

        mock_ai_service.generate_response.return_value = mock_structured_response
        mock_create_ai_service.return_value = mock_ai_service
        
        # Test essay (minimum 200 words for DBQ)
        essay_text = """The American Revolution was a pivotal moment in world history that fundamentally changed the relationship between Britain and its American colonies. The colonists' decision to rebel against British rule was not made lightly, but emerged from a series of escalating conflicts over taxation, representation, and colonial autonomy that developed over more than a decade.

The roots of the conflict can be traced to the end of the French and Indian War in 1763, when Britain found itself with massive war debts and looked to the American colonies to help pay these costs. The Sugar Act of 1764, the Stamp Act of 1765, and the Tea Act of 1773 all imposed new taxes on the colonists without their consent or representation in Parliament. This violated the traditional British principle that taxation required the consent of the governed, leading to the famous rallying cry of "no taxation without representation."

Colonial resistance took many forms, from economic boycotts and petitions to more dramatic acts of defiance like the Boston Tea Party in 1773. The British government's response was swift and harsh, passing the Coercive Acts (known in America as the Intolerable Acts) in 1774, which further galvanized colonial opposition and helped unite the previously divided colonies in their resistance to British rule.

The Declaration of Independence in 1776 provided the philosophical justification for separation, drawing on Enlightenment ideas about natural rights and government by consent. The revolution demonstrated that determined colonial resistance could overcome imperial power, establishing important precedents for later independence movements worldwide."""
        
        result = await grade_essay(essay_text, EssayType.DBQ, "Analyze the causes of the American Revolution")
        
        assert isinstance(result, GradeResponse)
        assert result.score == 4
        assert result.max_score == 6
        assert result.letter_grade == "B"
        assert "Good essay" in result.overall_feedback
        assert len(result.suggestions) == 1
        
        # Verify AI service was called
        mock_ai_service.generate_response.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('app.utils.grading_workflow.create_ai_service')
    async def test_grade_essay_ai_service_failure(self, mock_create_ai_service):
        """Test grading workflow handles AI service failure"""
        # Setup mock AI service that raises exception
        mock_ai_service = AsyncMock()
        mock_ai_service.generate_response.side_effect = Exception("AI service error")
        mock_create_ai_service.return_value = mock_ai_service
        
        essay_text = """This is a sufficiently long essay for testing purposes that demonstrates how the grading workflow handles AI service failures. The American Revolution was caused by many complex factors that developed over decades of British colonial rule. Economic factors played a central role, including the implementation of new taxes and trade restrictions following the French and Indian War. The Sugar Act of 1764, Stamp Act of 1765, and Tea Act of 1773 imposed financial burdens on colonists without their consent in Parliament.

Political factors were equally important, as colonists increasingly resented their lack of representation in British government while being subject to British laws and taxes. The principle of "no taxation without representation" became a rallying cry that united diverse colonial interests against British policies. Social and cultural factors also contributed as American society developed its own distinct identity separate from British traditions.

Enlightenment ideas about natural rights, government by consent, and the social contract provided intellectual justification for resistance to British authority. Thinkers like John Locke influenced colonial leaders to believe that governments derive their power from the consent of the governed, and that people have the right to alter or abolish governments that fail to protect their rights. These philosophical foundations would later be articulated in the Declaration of Independence and would shape the new American system of government."""
        
        with pytest.raises(APIError, match="Grading workflow failed"):
            await grade_essay(essay_text, EssayType.DBQ, "Test prompt")
    
    @pytest.mark.asyncio
    @patch('app.utils.grading_workflow.create_ai_service')
    async def test_grade_essay_with_validation_integration(self, mock_create_ai_service):
        """Test complete grade_essay_with_validation flow with mock AI service"""
        from app.models.structured_outputs import (
            DBQGradeOutput, DBQLeqBreakdownOutput, RubricItemOutput
        )

        # Setup mock AI service with Structured Output response
        mock_ai_service = AsyncMock()
        mock_structured_response = DBQGradeOutput(
            score=5,
            max_score=6,
            letter_grade="B",
            overall_feedback="Strong analysis of the American Revolution causes",
            suggestions=["Add more contextualization"],
            breakdown=DBQLeqBreakdownOutput(
                thesis=RubricItemOutput(score=1, max_score=1, feedback="Clear thesis"),
                contextualization=RubricItemOutput(score=1, max_score=1, feedback="Good context"),
                evidence=RubricItemOutput(score=2, max_score=2, feedback="Excellent evidence"),
                analysis=RubricItemOutput(score=1, max_score=2, feedback="Strong analysis")
            )
        )
        mock_ai_service.generate_response.return_value = mock_structured_response
        mock_create_ai_service.return_value = mock_ai_service

        essay_text = """The American Revolution emerged from a complex web of economic, political, and ideological factors that developed over more than a decade. The roots of conflict can be traced to the end of the French and Indian War in 1763, when Britain faced massive war debts and looked to the American colonies to help pay these costs. The Sugar Act of 1764, Stamp Act of 1765, and Townshend Acts of 1767 imposed new taxes without colonial representation in Parliament. This violated the traditional British principle that taxation required consent of the governed. Colonial resistance took many forms, from economic boycotts to violent protests like the Boston Tea Party. The British response through the Coercive Acts of 1774 further unified colonial opposition. By 1775, armed conflict had begun at Lexington and Concord, marking the transition from political protest to revolutionary war. The Declaration of Independence in 1776 provided the philosophical justification for separation, drawing on Enlightenment ideas about natural rights and government by consent. The war itself demonstrated that determined colonial resistance could overcome imperial power, establishing precedents for later independence movements worldwide."""

        result = await grade_essay_with_validation(
            essay_text, EssayType.DBQ, "Analyze the causes of the American Revolution"
        )

        # Should get a valid response from mock AI service
        assert isinstance(result, GradeResponse)
        assert result.score == 5
        assert result.max_score == 6  # DBQ max score
        assert result.letter_grade == "B"
        assert isinstance(result.overall_feedback, str)
        assert isinstance(result.suggestions, list)
        assert result.breakdown is not None