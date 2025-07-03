"""
Structured logging service for production-ready logging with JSON format
"""

import json
import logging
import time
from typing import Dict, Any, Optional
from datetime import datetime
from contextvars import ContextVar
from pathlib import Path

# Context variable to store correlation ID across async contexts
correlation_id_var: ContextVar[Optional[str]] = ContextVar('correlation_id', default=None)


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        # Basic log data
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add correlation ID if available
        correlation_id = correlation_id_var.get()
        if correlation_id:
            log_data["correlation_id"] = correlation_id
            
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
            
        # Add extra fields if present (they are added directly to the record)
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                          'filename', 'module', 'exc_info', 'exc_text', 'stack_info',
                          'lineno', 'funcName', 'created', 'msecs', 'relativeCreated',
                          'thread', 'threadName', 'processName', 'process', 'getMessage',
                          'message', 'taskName']:
                log_data[key] = value
            
        return json.dumps(log_data, default=str)


class StructuredLogger:
    """Enhanced logger with structured logging capabilities"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self._setup_logger()
        
    def _setup_logger(self):
        """Setup logger with JSON formatter"""
        # Only setup if not already configured
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(JSONFormatter())
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def info(self, message: str, **kwargs):
        """Log info message with structured data"""
        self.logger.info(message, extra=kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message with structured data"""
        self.logger.error(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message with structured data"""
        self.logger.warning(message, extra=kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log debug message with structured data"""
        self.logger.debug(message, extra=kwargs)
        
    def log_request_start(self, method: str, path: str, client_ip: str, **kwargs):
        """Log the start of an API request"""
        self.info(
            "Request started",
            event_type="request_start",
            http_method=method,
            http_path=path,
            client_ip=client_ip,
            **kwargs
        )
    
    def log_request_end(self, method: str, path: str, status_code: int, 
                       duration_ms: float, **kwargs):
        """Log the end of an API request"""
        self.info(
            "Request completed",
            event_type="request_end",
            http_method=method,
            http_path=path,
            http_status=status_code,
            duration_ms=round(duration_ms, 2),
            **kwargs
        )
    
    def log_essay_grading(self, essay_type: str, word_count: int, 
                         processing_time_ms: float, score: int, max_score: int, **kwargs):
        """Log essay grading events"""
        self.info(
            "Essay graded successfully",
            event_type="essay_graded",
            essay_type=essay_type,
            word_count=word_count,
            processing_time_ms=round(processing_time_ms, 2),
            score=score,
            max_score=max_score,
            percentage=round((score / max_score) * 100, 1) if max_score > 0 else 0,
            **kwargs
        )
    
    def log_ai_service_call(self, service_type: str, duration_ms: float, 
                           success: bool, **kwargs):
        """Log AI service calls"""
        level_method = self.info if success else self.error
        level_method(
            f"AI service call {'completed' if success else 'failed'}",
            event_type="ai_service_call",
            ai_service_type=service_type,
            duration_ms=round(duration_ms, 2),
            success=success,
            **kwargs
        )
    
    def log_error(self, error_type: str, error_message: str, **kwargs):
        """Log application errors with context"""
        self.error(
            f"Application error: {error_message}",
            event_type="application_error",
            error_type=error_type,
            error_message=error_message,
            **kwargs
        )


class PerformanceTimer:
    """Context manager for timing operations"""
    
    def __init__(self, logger: StructuredLogger, operation_name: str, **context):
        self.logger = logger
        self.operation_name = operation_name
        self.context = context
        self.start_time = None
        
    def __enter__(self):
        self.start_time = time.time()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration_ms = (time.time() - self.start_time) * 1000
        
        if exc_type is None:
            self.logger.info(
                f"Operation '{self.operation_name}' completed",
                event_type="operation_completed",
                operation=self.operation_name,
                duration_ms=round(duration_ms, 2),
                **self.context
            )
        else:
            self.logger.error(
                f"Operation '{self.operation_name}' failed",
                event_type="operation_failed",
                operation=self.operation_name,
                duration_ms=round(duration_ms, 2),
                error_type=exc_type.__name__ if exc_type else None,
                **self.context
            )


def get_logger(name: str) -> StructuredLogger:
    """Get a structured logger instance"""
    return StructuredLogger(name)


def set_correlation_id(correlation_id: str):
    """Set correlation ID for the current request context"""
    correlation_id_var.set(correlation_id)


def get_correlation_id() -> Optional[str]:
    """Get the current correlation ID"""
    return correlation_id_var.get()