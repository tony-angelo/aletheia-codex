"""Logging utilities for Cloud Functions."""

import logging
import sys
from typing import Optional

_logger: Optional[logging.Logger] = None


def get_logger(name: str = "aletheia-codex") -> logging.Logger:
    """
    Get or create a configured logger.
    
    Args:
        name: Logger name
        
    Returns:
        Configured logger instance
    """
    global _logger
    if _logger is None:
        _logger = logging.getLogger(name)
        _logger.setLevel(logging.INFO)
        
        # Console handler with structured format
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '{"severity": "%(levelname)s", "message": "%(message)s", "logger": "%(name)s"}'
        )
        handler.setFormatter(formatter)
        _logger.addHandler(handler)
    
    return _logger
