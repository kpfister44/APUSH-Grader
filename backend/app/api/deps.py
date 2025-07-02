"""API dependency injection"""

from typing import Annotated
from functools import lru_cache
from fastapi import Depends
from app.config.settings import Settings, get_settings
from app.services.dependencies.service_locator import get_service_locator, ServiceLocator
from app.services.base.protocols import (
    EssayProcessorProtocol,
    EssayValidatorProtocol,
    TextAnalyzerProtocol
)


@lru_cache()
def get_app_settings() -> Settings:
    """Get application settings dependency"""
    return get_settings()


# Settings dependency
SettingsDep = Annotated[Settings, Depends(get_app_settings)]

# Service locator dependency
ServiceLocatorDep = Annotated[ServiceLocator, Depends(get_service_locator)]

# Service dependencies
def get_essay_processor(locator: ServiceLocatorDep) -> EssayProcessorProtocol:
    return locator.get(EssayProcessorProtocol)

def get_essay_validator(locator: ServiceLocatorDep) -> EssayValidatorProtocol:
    return locator.get(EssayValidatorProtocol)

def get_text_analyzer(locator: ServiceLocatorDep) -> TextAnalyzerProtocol:
    return locator.get(TextAnalyzerProtocol)

EssayProcessorDep = Annotated[EssayProcessorProtocol, Depends(get_essay_processor)]
EssayValidatorDep = Annotated[EssayValidatorProtocol, Depends(get_essay_validator)]
TextAnalyzerDep = Annotated[TextAnalyzerProtocol, Depends(get_text_analyzer)]