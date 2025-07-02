"""Retry logic with exponential backoff for service operations"""

import asyncio
import functools
import random
from typing import Callable, Type, Union, Tuple, Optional, Any
from app.services.base.exceptions import RateLimitExceededError, NetworkError, ParseError, APIError


def async_retry(
    max_retries: int = 3,
    retry_exceptions: Tuple[Type[Exception], ...] = (RateLimitExceededError, NetworkError),
    backoff_factor: float = 2.0,
    max_delay: float = 60.0,
    jitter: bool = True
):
    """
    Async retry decorator with exponential backoff and jitter
    
    Args:
        max_retries: Maximum number of retry attempts
        retry_exceptions: Tuple of exception types to retry on
        backoff_factor: Multiplier for exponential backoff
        max_delay: Maximum delay between retries in seconds
        jitter: Add random jitter to prevent thundering herd
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    # Don't retry on the last attempt
                    if attempt == max_retries:
                        break
                    
                    # Check if we should retry this exception
                    if not isinstance(e, retry_exceptions):
                        break
                    
                    # Calculate delay with exponential backoff
                    base_delay = backoff_factor ** attempt
                    delay = min(base_delay, max_delay)
                    
                    # Special handling for rate limits
                    if isinstance(e, RateLimitExceededError):
                        delay = min(delay * 2, max_delay)
                    
                    # Add jitter to prevent thundering herd
                    if jitter:
                        delay = delay * (0.5 + random.random() * 0.5)
                    
                    # Log retry attempt
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(
                        f"Attempt {attempt + 1}/{max_retries + 1} failed for {func.__name__}: {e}. "
                        f"Retrying in {delay:.2f}s"
                    )
                    
                    await asyncio.sleep(delay)
            
            # Re-raise the last exception
            raise last_exception
        
        return wrapper
    return decorator


def sync_retry(
    max_retries: int = 3,
    retry_exceptions: Tuple[Type[Exception], ...] = (Exception,),
    backoff_factor: float = 2.0,
    max_delay: float = 60.0,
    jitter: bool = True
):
    """
    Synchronous retry decorator with exponential backoff and jitter
    
    Args:
        max_retries: Maximum number of retry attempts
        retry_exceptions: Tuple of exception types to retry on
        backoff_factor: Multiplier for exponential backoff
        max_delay: Maximum delay between retries in seconds
        jitter: Add random jitter to prevent thundering herd
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import time
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    # Don't retry on the last attempt
                    if attempt == max_retries:
                        break
                    
                    # Check if we should retry this exception
                    if not isinstance(e, retry_exceptions):
                        break
                    
                    # Calculate delay with exponential backoff
                    base_delay = backoff_factor ** attempt
                    delay = min(base_delay, max_delay)
                    
                    # Add jitter to prevent thundering herd
                    if jitter:
                        delay = delay * (0.5 + random.random() * 0.5)
                    
                    # Log retry attempt
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(
                        f"Attempt {attempt + 1}/{max_retries + 1} failed for {func.__name__}: {e}. "
                        f"Retrying in {delay:.2f}s"
                    )
                    
                    time.sleep(delay)
            
            # Re-raise the last exception
            raise last_exception
        
        return wrapper
    return decorator


class RetryConfig:
    """Configuration class for retry behavior"""
    
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        backoff_factor: float = 2.0,
        jitter: bool = True,
        retry_exceptions: Tuple[Type[Exception], ...] = (APIError,)
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.jitter = jitter
        self.retry_exceptions = retry_exceptions
    
    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay for given attempt number"""
        base_delay = self.base_delay * (self.backoff_factor ** attempt)
        delay = min(base_delay, self.max_delay)
        
        if self.jitter:
            delay = delay * (0.5 + random.random() * 0.5)
        
        return delay
    
    def should_retry(self, exception: Exception, attempt: int) -> bool:
        """Check if should retry for given exception and attempt"""
        if attempt >= self.max_retries:
            return False
        
        return isinstance(exception, self.retry_exceptions)


# Common retry configurations
API_RETRY_CONFIG = RetryConfig(
    max_retries=3,
    base_delay=1.0,
    max_delay=30.0,
    backoff_factor=2.0,
    retry_exceptions=(RateLimitExceededError, NetworkError)
)

AGGRESSIVE_RETRY_CONFIG = RetryConfig(
    max_retries=5,
    base_delay=0.5,
    max_delay=60.0,
    backoff_factor=1.5,
    retry_exceptions=(RateLimitExceededError, NetworkError, ParseError)
)

CONSERVATIVE_RETRY_CONFIG = RetryConfig(
    max_retries=2,
    base_delay=2.0,
    max_delay=30.0,
    backoff_factor=3.0,
    retry_exceptions=(NetworkError,)
)