"""Main response processing coordinator service."""

from abc import ABC, abstractmethod

from app.models.core.essay_types import EssayType
from app.models.core.grade_models import GradeResponse
from app.models.processing.response import ProcessedGradingResult
from app.services.base.base_service import BaseService
from app.services.dependencies.service_locator import ServiceLocator


class ResponseProcessorProtocol(ABC):
    """Protocol for response processing services."""
    
    @abstractmethod
    def process_grading_response(self, response: GradeResponse, essay_type: EssayType) -> ProcessedGradingResult:
        """Process a grading response through validation, formatting, and insights."""
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