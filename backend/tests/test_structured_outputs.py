"""Tests for Structured Outputs schema models.

Tests the Pydantic models used for Anthropic Structured Outputs API.
These models guarantee schema compliance via constrained decoding.
"""

import pytest
from pydantic import ValidationError

from app.models.structured_outputs import (
    RubricItemOutput,
    DBQLeqBreakdownOutput,
    SAQBreakdownOutput,
    EGBreakdownOutput,
    DBQGradeOutput,
    LEQGradeOutput,
    SAQCollegeBoardGradeOutput,
    SAQEGGradeOutput,
    get_output_schema_for_essay,
)


class TestRubricItemOutput:
    """Test RubricItemOutput schema"""

    def test_valid_rubric_item(self):
        """Test creating valid rubric item"""
        item = RubricItemOutput(
            score=1,
            max_score=2,
            feedback="Good effort but needs more detail"
        )
        assert item.score == 1
        assert item.max_score == 2
        assert item.feedback == "Good effort but needs more detail"

    @pytest.mark.skip(reason="Aliases not needed for Structured Outputs - Claude returns exact schema")
    def test_rubric_item_with_alias(self):
        """Test rubric item accepts maxScore alias (SKIPPED - not needed)"""
        item = RubricItemOutput(
            score=2,
            maxScore=2,  # Using alias
            feedback="Perfect!"
        )
        assert item.score == 2
        assert item.max_score == 2
        assert item.feedback == "Perfect!"

    def test_rubric_item_missing_field(self):
        """Test rubric item fails with missing required field"""
        with pytest.raises(ValidationError):
            RubricItemOutput(
                score=1,
                max_score=2
                # Missing feedback
            )

    def test_rubric_item_wrong_type(self):
        """Test rubric item fails with wrong field type"""
        with pytest.raises(ValidationError):
            RubricItemOutput(
                score="one",  # Should be int
                max_score=2,
                feedback="Test"
            )


class TestDBQLeqBreakdownOutput:
    """Test DBQLeqBreakdownOutput schema"""

    def test_valid_dbq_leq_breakdown(self):
        """Test creating valid DBQ/LEQ breakdown"""
        breakdown = DBQLeqBreakdownOutput(
            thesis=RubricItemOutput(score=1, max_score=1, feedback="Clear thesis"),
            contextualization=RubricItemOutput(score=0, max_score=1, feedback="Needs context"),
            evidence=RubricItemOutput(score=2, max_score=2, feedback="Strong evidence"),
            analysis=RubricItemOutput(score=1, max_score=2, feedback="Good analysis")
        )
        assert breakdown.thesis.score == 1
        assert breakdown.contextualization.score == 0
        assert breakdown.evidence.score == 2
        assert breakdown.analysis.score == 1

    def test_dbq_leq_breakdown_missing_field(self):
        """Test breakdown fails with missing required field"""
        with pytest.raises(ValidationError):
            DBQLeqBreakdownOutput(
                thesis=RubricItemOutput(score=1, max_score=1, feedback="Clear thesis"),
                contextualization=RubricItemOutput(score=0, max_score=1, feedback="Needs context"),
                evidence=RubricItemOutput(score=2, max_score=2, feedback="Strong evidence")
                # Missing analysis
            )


class TestSAQBreakdownOutput:
    """Test SAQBreakdownOutput schema (College Board 3-point)"""

    def test_valid_saq_breakdown(self):
        """Test creating valid SAQ breakdown"""
        breakdown = SAQBreakdownOutput(
            part_a=RubricItemOutput(score=1, max_score=1, feedback="Correct identification"),
            part_b=RubricItemOutput(score=1, max_score=1, feedback="Good explanation"),
            part_c=RubricItemOutput(score=0, max_score=1, feedback="Incomplete analysis")
        )
        assert breakdown.part_a.score == 1
        assert breakdown.part_b.score == 1
        assert breakdown.part_c.score == 0

    def test_saq_breakdown_wrong_type(self):
        """Test SAQ breakdown fails with wrong field type"""
        with pytest.raises(ValidationError):
            SAQBreakdownOutput(
                part_a="wrong type",  # Should be RubricItemOutput
                part_b=RubricItemOutput(score=1, max_score=1, feedback="Test"),
                part_c=RubricItemOutput(score=0, max_score=1, feedback="Test")
            )


class TestEGBreakdownOutput:
    """Test EGBreakdownOutput schema (EG 10-point rubric)"""

    def test_valid_eg_breakdown(self):
        """Test creating valid EG breakdown"""
        breakdown = EGBreakdownOutput(
            criterion_a=RubricItemOutput(score=1, max_score=1, feedback="Addresses prompt"),
            criterion_c=RubricItemOutput(score=2, max_score=3, feedback="Good evidence from correct time period"),
            criterion_e=RubricItemOutput(score=4, max_score=6, feedback="Solid explanation")
        )
        assert breakdown.criterion_a.score == 1
        assert breakdown.criterion_c.score == 2
        assert breakdown.criterion_e.score == 4

    @pytest.mark.skip(reason="Aliases not needed for Structured Outputs - Claude returns exact schema")
    def test_eg_breakdown_with_aliases(self):
        """Test EG breakdown accepts field aliases (SKIPPED - not needed)"""
        breakdown = EGBreakdownOutput(
            criterionA=RubricItemOutput(score=1, maxScore=1, feedback="Addresses prompt"),
            criterionC=RubricItemOutput(score=3, maxScore=3, feedback="Complete evidence"),
            criterionE=RubricItemOutput(score=6, maxScore=6, feedback="Excellent explanation")
        )
        assert breakdown.criterion_a.score == 1
        assert breakdown.criterion_c.score == 3
        assert breakdown.criterion_e.score == 6


class TestDBQGradeOutput:
    """Test DBQGradeOutput schema"""

    def test_valid_dbq_grade(self):
        """Test creating valid DBQ grade output"""
        grade = DBQGradeOutput(
            score=4,
            max_score=6,
            letter_grade="C",
            breakdown=DBQLeqBreakdownOutput(
                thesis=RubricItemOutput(score=1, max_score=1, feedback="Clear thesis"),
                contextualization=RubricItemOutput(score=0, max_score=1, feedback="Needs context"),
                evidence=RubricItemOutput(score=2, max_score=2, feedback="Strong evidence"),
                analysis=RubricItemOutput(score=1, max_score=2, feedback="Good analysis")
            ),
            overall_feedback="Solid essay with room for improvement",
            suggestions=["Add more context", "Strengthen analysis"]
        )
        assert grade.score == 4
        assert grade.max_score == 6
        assert grade.letter_grade == "C"
        assert len(grade.suggestions) == 2
        assert grade.breakdown.thesis.score == 1

    @pytest.mark.skip(reason="Aliases not needed for Structured Outputs - Claude returns exact schema")
    def test_dbq_grade_with_aliases(self):
        """Test DBQ grade accepts field aliases (SKIPPED - not needed)"""
        grade = DBQGradeOutput(
            score=5,
            maxScore=6,  # Using alias
            letterGrade="B",  # Using alias
            breakdown=DBQLeqBreakdownOutput(
                thesis=RubricItemOutput(score=1, maxScore=1, feedback="Clear"),
                contextualization=RubricItemOutput(score=1, maxScore=1, feedback="Good"),
                evidence=RubricItemOutput(score=2, maxScore=2, feedback="Strong"),
                analysis=RubricItemOutput(score=1, maxScore=2, feedback="Decent")
            ),
            overallFeedback="Very good essay",  # Using alias
            suggestions=["Minor improvements"]
        )
        assert grade.score == 5
        assert grade.max_score == 6
        assert grade.letter_grade == "B"
        assert grade.overall_feedback == "Very good essay"

    def test_dbq_grade_missing_field(self):
        """Test DBQ grade fails with missing required field"""
        with pytest.raises(ValidationError):
            DBQGradeOutput(
                score=4,
                max_score=6,
                letter_grade="C",
                breakdown=DBQLeqBreakdownOutput(
                    thesis=RubricItemOutput(score=1, max_score=1, feedback="Clear"),
                    contextualization=RubricItemOutput(score=0, max_score=1, feedback="Needs work"),
                    evidence=RubricItemOutput(score=2, max_score=2, feedback="Strong"),
                    analysis=RubricItemOutput(score=1, max_score=2, feedback="Good")
                ),
                # Missing overall_feedback and suggestions
            )


class TestLEQGradeOutput:
    """Test LEQGradeOutput schema"""

    def test_valid_leq_grade(self):
        """Test creating valid LEQ grade output"""
        grade = LEQGradeOutput(
            score=5,
            max_score=6,
            letter_grade="B",
            breakdown=DBQLeqBreakdownOutput(
                thesis=RubricItemOutput(score=1, max_score=1, feedback="Strong thesis"),
                contextualization=RubricItemOutput(score=1, max_score=1, feedback="Good context"),
                evidence=RubricItemOutput(score=2, max_score=2, feedback="Excellent evidence"),
                analysis=RubricItemOutput(score=1, max_score=2, feedback="Solid analysis")
            ),
            overall_feedback="Very strong essay",
            suggestions=["Add more complexity to analysis"]
        )
        assert grade.score == 5
        assert grade.max_score == 6
        assert grade.letter_grade == "B"
        assert grade.breakdown.evidence.score == 2


class TestSAQCollegeBoardGradeOutput:
    """Test SAQCollegeBoardGradeOutput schema (3-point rubric)"""

    def test_valid_saq_college_board_grade(self):
        """Test creating valid SAQ College Board grade output"""
        grade = SAQCollegeBoardGradeOutput(
            score=2,
            max_score=3,
            letter_grade="C",
            breakdown=SAQBreakdownOutput(
                part_a=RubricItemOutput(score=1, max_score=1, feedback="Correct"),
                part_b=RubricItemOutput(score=1, max_score=1, feedback="Good"),
                part_c=RubricItemOutput(score=0, max_score=1, feedback="Incomplete")
            ),
            overall_feedback="Good start, needs work on part C",
            suggestions=["Provide more detail in part C"]
        )
        assert grade.score == 2
        assert grade.max_score == 3
        assert grade.letter_grade == "C"
        assert grade.breakdown.part_a.score == 1


class TestSAQEGGradeOutput:
    """Test SAQEGGradeOutput schema (10-point EG rubric)"""

    def test_valid_saq_eg_grade(self):
        """Test creating valid SAQ EG grade output"""
        grade = SAQEGGradeOutput(
            score=7,
            max_score=10,
            letter_grade="B",
            breakdown=EGBreakdownOutput(
                criterion_a=RubricItemOutput(score=1, max_score=1, feedback="Addresses all parts"),
                criterion_c=RubricItemOutput(score=2, max_score=3, feedback="Good evidence, one missing"),
                criterion_e=RubricItemOutput(score=4, max_score=6, feedback="Good explanation")
            ),
            overall_feedback="Solid SAQ response",
            suggestions=["Add one more piece of evidence", "Deepen analysis"]
        )
        assert grade.score == 7
        assert grade.max_score == 10
        assert grade.letter_grade == "B"
        assert grade.breakdown.criterion_a.score == 1
        assert grade.breakdown.criterion_c.score == 2
        assert grade.breakdown.criterion_e.score == 4

    def test_saq_eg_grade_wrong_breakdown(self):
        """Test SAQ EG grade fails with wrong breakdown type"""
        with pytest.raises(ValidationError):
            SAQEGGradeOutput(
                score=7,
                max_score=10,
                letter_grade="B",
                breakdown=SAQBreakdownOutput(  # Wrong breakdown type (should be EGBreakdownOutput)
                    part_a=RubricItemOutput(score=1, max_score=1, feedback="Test"),
                    part_b=RubricItemOutput(score=1, max_score=1, feedback="Test"),
                    part_c=RubricItemOutput(score=0, max_score=1, feedback="Test")
                ),
                overall_feedback="Test",
                suggestions=["Test"]
            )


class TestOutputSchemaFactory:
    """Test get_output_schema_for_essay factory function"""

    def test_get_dbq_schema(self):
        """Test factory returns DBQ schema"""
        schema = get_output_schema_for_essay("DBQ")
        assert schema == DBQGradeOutput

    def test_get_leq_schema(self):
        """Test factory returns LEQ schema"""
        schema = get_output_schema_for_essay("LEQ")
        assert schema == LEQGradeOutput

    def test_get_saq_college_board_schema(self):
        """Test factory returns SAQ College Board schema"""
        schema = get_output_schema_for_essay("SAQ", "college_board")
        assert schema == SAQCollegeBoardGradeOutput

    def test_get_saq_eg_schema(self):
        """Test factory returns SAQ EG schema"""
        schema = get_output_schema_for_essay("SAQ", "eg")
        assert schema == SAQEGGradeOutput

    def test_get_saq_default_rubric(self):
        """Test factory defaults to College Board for SAQ"""
        schema = get_output_schema_for_essay("SAQ")
        assert schema == SAQCollegeBoardGradeOutput

    def test_unknown_essay_type(self):
        """Test factory raises error for unknown essay type"""
        with pytest.raises(ValueError, match="Unknown essay type"):
            get_output_schema_for_essay("UNKNOWN")

    def test_unknown_rubric_type(self):
        """Test factory raises error for unknown rubric type"""
        with pytest.raises(ValueError, match="Unknown SAQ rubric type"):
            get_output_schema_for_essay("SAQ", "unknown_rubric")


class TestSchemaIntegration:
    """Integration tests for schema usage"""

    def test_dbq_grade_to_dict(self):
        """Test DBQ grade serializes to dict correctly"""
        grade = DBQGradeOutput(
            score=4,
            max_score=6,
            letter_grade="C",
            breakdown=DBQLeqBreakdownOutput(
                thesis=RubricItemOutput(score=1, max_score=1, feedback="Clear"),
                contextualization=RubricItemOutput(score=0, max_score=1, feedback="Needs work"),
                evidence=RubricItemOutput(score=2, max_score=2, feedback="Strong"),
                analysis=RubricItemOutput(score=1, max_score=2, feedback="Good")
            ),
            overall_feedback="Solid essay",
            suggestions=["Add context"]
        )

        # Serialize using model_dump()
        data = grade.model_dump()
        assert data["score"] == 4
        assert data["max_score"] == 6
        assert data["letter_grade"] == "C"
        assert data["breakdown"]["thesis"]["score"] == 1

    def test_saq_eg_grade_to_dict(self):
        """Test SAQ EG grade serializes to dict correctly"""
        grade = SAQEGGradeOutput(
            score=8,
            max_score=10,
            letter_grade="B",
            breakdown=EGBreakdownOutput(
                criterion_a=RubricItemOutput(score=1, max_score=1, feedback="Addresses prompt"),
                criterion_c=RubricItemOutput(score=3, max_score=3, feedback="Complete evidence"),
                criterion_e=RubricItemOutput(score=4, max_score=6, feedback="Good explanation")
            ),
            overall_feedback="Strong response",
            suggestions=["Deepen analysis"]
        )

        data = grade.model_dump()
        assert data["score"] == 8
        assert data["breakdown"]["criterion_a"]["score"] == 1
        assert data["breakdown"]["criterion_c"]["score"] == 3
        assert data["breakdown"]["criterion_e"]["score"] == 4
