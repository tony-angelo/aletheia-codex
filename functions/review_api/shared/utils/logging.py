"""
Enhanced logging utilities for Cloud Functions with Cloud Logging integration.

ENHANCEMENTS:
- Cloud Logging structured format
- Request correlation IDs
- Performance metrics
- Multiple log levels
- Trace context support
"""

import logging
import sys
import json
import time
from typing import Optional, Dict, Any
from datetime import datetime
import traceback

# Global logger cache
_loggers: Dict[str, logging.Logger] = {}

# Request context (for correlation)
_request_context: Dict[str, Any] = {}


class CloudLoggingFormatter(logging.Formatter):
    """
    Formatter for Cloud Logging structured logs.
    
    Outputs JSON format compatible with Cloud Logging's structured log format.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON for Cloud Logging."""
        
        # Base log entry
        log_entry = {
            "severity": record.levelname,
            "message": record.getMessage(),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "logger": record.name,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add request context if available
        if _request_context:
            log_entry["request_context"] = _request_context.copy()
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }
        
        # Add extra fields
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
        
        return json.dumps(log_entry)


class PerformanceLogger:
    """Context manager for logging performance metrics."""
    
    def __init__(self, logger: logging.Logger, operation: str):
        self.logger = logger
        self.operation = operation
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        self.logger.info(f"Starting: {self.operation}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = time.time() - self.start_time
        if exc_type is None:
            self.logger.info(
                f"Completed: {self.operation}",
                extra={'extra_fields': {'duration_seconds': elapsed}}
            )
        else:
            self.logger.error(
                f"Failed: {self.operation}",
                extra={'extra_fields': {'duration_seconds': elapsed}}
            )
        return False


def set_request_context(request_id: Optional[str] = None, **kwargs):
    """
    Set request context for correlation across logs.
    
    Args:
        request_id: Unique request identifier
        **kwargs: Additional context fields
    """
    global _request_context
    _request_context = {
        "request_id": request_id or generate_request_id(),
        **kwargs
    }


def clear_request_context():
    """Clear the request context."""
    global _request_context
    _request_context = {}


def generate_request_id() -> str:
    """Generate a unique request ID."""
    import uuid
    return str(uuid.uuid4())


def get_logger(
    name: str = "aletheia-codex",
    level: int = logging.INFO,
    use_cloud_format: bool = True
) -> logging.Logger:
    """
    Get or create a configured logger.
    
    Args:
        name: Logger name
        level: Logging level (default: INFO)
        use_cloud_format: Use Cloud Logging JSON format (default: True)
        
    Returns:
        Configured logger instance
    """
    # Return cached logger if exists
    if name in _loggers:
        return _loggers[name]
    
    # Create new logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers = []
    
    # Console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    
    # Set formatter based on environment
    if use_cloud_format:
        formatter = CloudLoggingFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    # Cache the logger
    _loggers[name] = logger
    
    return logger


def log_performance(logger: logging.Logger, operation: str):
    """
    Decorator or context manager for logging performance.
    
    Usage as context manager:
        with log_performance(logger, "database_query"):
            # operation here
    
    Usage as decorator:
        @log_performance(logger, "process_document")
        def process_document():
            # operation here
    """
    return PerformanceLogger(logger, operation)


def log_with_context(logger: logging.Logger, level: int, message: str, **context):
    """
    Log a message with additional context fields.
    
    Args:
        logger: Logger instance
        level: Log level (e.g., logging.INFO)
        message: Log message
        **context: Additional context fields
    """
    logger.log(level, message, extra={'extra_fields': context})


# Convenience functions
def log_info(logger: logging.Logger, message: str, **context):
    """Log info message with context."""
    log_with_context(logger, logging.INFO, message, **context)


def log_warning(logger: logging.Logger, message: str, **context):
    """Log warning message with context."""
    log_with_context(logger, logging.WARNING, message, **context)


def log_error(logger: logging.Logger, message: str, **context):
    """Log error message with context."""
    log_with_context(logger, logging.ERROR, message, **context)


def log_debug(logger: logging.Logger, message: str, **context):
    """Log debug message with context."""
    log_with_context(logger, logging.DEBUG, message, **context)


# Usage examples:
#
# Example 1: Basic usage
# logger = get_logger("my-function")
# logger.info("Processing started")
#
# Example 2: With request context
# set_request_context(request_id="abc-123", user_id="user-456")
# logger.info("User action")  # Will include request context
# clear_request_context()
#
# Example 3: Performance logging
# with log_performance(logger, "database_query"):
#     # perform database operation
#
# Example 4: With additional context
# log_info(logger, "Document processed", document_id="doc-123", chunks=10)