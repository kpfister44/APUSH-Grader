"""Main response processing coordinator service."""

import json
from abc import ABC, abstractmethod
from typing import Dict, Any, List

from app.models.core.essay_types import EssayType
from app.models.core.grade_models import GradeResponse
from app.models.processing.response import ProcessedGradingResult
from app.models.processing.preprocessing import PreprocessingResult
from app.services.base.base_service import BaseService
from app.services.dependencies.service_locator import ServiceLocator


class ResponseProcessorProtocol(ABC):
    """Protocol for response processing services."""
    
    @abstractmethod
    def process_grading_response(self, response: GradeResponse, essay_type: EssayType) -> ProcessedGradingResult:
        """Process a grading response through validation, formatting, and insights."""
        pass
    
    @abstractmethod
    def process_response(
        self, 
        raw_response: str, 
        essay_type: EssayType, 
        preprocessing_result: PreprocessingResult
    ) -> GradeResponse:
        """Process raw AI response JSON into a structured GradeResponse."""
        pass


class ResponseProcessor(BaseService, ResponseProcessorProtocol):
    """Main coordinator for processing AI grading responses."""
    
    def __init__(self):
        super().__init__()
        self._service_locator = ServiceLocator()
    
    def process_grading_response(self, response: GradeResponse, essay_type: EssayType) -> ProcessedGradingResult:
        """
        Process a complete grading response through validation, formatting, and insights generation.
        
        Args:
            response: The AI grading response to process
            essay_type: The type of essay that was graded
            
        Returns:
            ProcessedGradingResult with all processing completed
        """
        try:
            self.logger.info(f"Processing grading response for {essay_type.value} essay")
            
            # Get required services
            validator = self._service_locator.get_response_validator()
            formatter = self._service_locator.get_response_formatter()
            insights_generator = self._service_locator.get_insights_generator()
            
            # Step 1: Validate the response
            self.logger.debug("Validating response")
            validation_results = validator.validate_response(response, essay_type)
            
            # Step 2: Generate insights
            self.logger.debug("Generating insights")
            insights = insights_generator.generate_insights(response, essay_type)
            
            # Step 3: Format for display
            self.logger.debug("Formatting for display")
            formatted_text = formatter.format_for_display(response, validation_results)
            
            # Step 4: Create display data
            self.logger.debug("Creating display data")
            display_data = formatter.create_display_data(response, insights)
            
            # Create final result
            processed_result = ProcessedGradingResult(
                original_response=response,
                formatted_text=formatted_text,
                insights=insights,
                validation_issues=validation_results.issues,
                display_data=display_data
            )
            
            self.logger.info(f"Successfully processed response with {len(insights)} insights and {len(validation_results.issues)} validation issues")
            
            return processed_result
            
        except Exception as e:
            self.logger.error(f"Error processing grading response: {e}")
            # Return a minimal result with error information
            return self._create_error_result(response, str(e))
    
    def _create_error_result(self, response: GradeResponse, error_message: str) -> ProcessedGradingResult:
        """Create a minimal processed result when processing fails."""
        from app.models.processing.response import GradingInsight, InsightType, InsightSeverity, GradeDisplayData
        from app.models.processing.display import DisplayColors
        
        error_insight = GradingInsight(
            type=InsightType.WARNING,
            title="Processing Error",
            message=f"Unable to fully process response: {error_message}",
            severity=InsightSeverity.ERROR
        )
        
        display_data = GradeDisplayData(
            score_text=f"{response.score}/{response.max_score}",
            percentage_text=f"{int(response.percentage_score)}%",
            letter_grade=response.letter_grade,
            performance_color=DisplayColors.BEGINNING,
            breakdown_items=[],
            insights=[error_insight]
        )
        
        return ProcessedGradingResult(
            original_response=response,
            formatted_text=f"Error processing response: {error_message}",
            insights=[error_insight],
            validation_issues=[f"Processing error: {error_message}"],
            display_data=display_data
        )
    
    def process_response(
        self, 
        raw_response: str, 
        essay_type: EssayType, 
        preprocessing_result: PreprocessingResult
    ) -> GradeResponse:
        """
        Process raw AI response JSON into a structured GradeResponse.
        
        Args:
            raw_response: Raw JSON string from AI service
            essay_type: The type of essay that was graded
            preprocessing_result: Results from essay preprocessing
            
        Returns:
            Structured GradeResponse object
            
        Raises:
            ProcessingError: If response parsing or validation fails
        """
        try:
            self.logger.debug(f"Processing raw AI response for {essay_type.value}")
            
            # Parse JSON response
            try:
                response_data = json.loads(raw_response)
            except json.JSONDecodeError as e:
                from app.services.base.exceptions import ProcessingError
                raise ProcessingError(f"Invalid JSON response from AI service: {e}")
            
            # Validate required fields
            required_fields = ["score", "maxScore", "breakdown", "overallFeedback", "suggestions"]
            missing_fields = [field for field in required_fields if field not in response_data]
            if missing_fields:
                from app.services.base.exceptions import ProcessingError
                raise ProcessingError(f"Missing required fields in AI response: {missing_fields}")
            
            # Create GradeResponse object
            grade_response = GradeResponse(
                score=response_data["score"],
                max_score=response_data["maxScore"],
                breakdown=response_data["breakdown"],
                overall_feedback=response_data["overallFeedback"],
                suggestions=response_data.get("suggestions", [])
            )
            
            self.logger.info(f"Successfully processed AI response: {grade_response.score}/{grade_response.max_score}")
            return grade_response
            
        except Exception as e:
            self.logger.error(f"Error processing raw AI response: {e}")
            from app.services.base.exceptions import ProcessingError
            raise ProcessingError(f"Failed to process AI response: {str(e)}")