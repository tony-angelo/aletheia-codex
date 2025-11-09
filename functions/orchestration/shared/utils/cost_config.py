"""
Cost monitoring configuration for AletheiaCodex.

Defines cost limits, pricing, and alert thresholds.
"""

from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class CostLimits:
    """Cost limits for different time periods."""
    per_note: float = 0.01  # $0.01 per note
    daily: float = 10.0  # $10 per day
    weekly: float = 50.0  # $50 per week
    monthly: float = 150.0  # $150 per month


@dataclass
class AlertThresholds:
    """Alert thresholds as percentage of limits."""
    warning: float = 0.75  # 75% of limit
    critical: float = 0.90  # 90% of limit
    emergency: float = 1.0  # 100% of limit


# Gemini pricing (per 1M tokens)
GEMINI_PRICING = {
    'gemini-2.0-flash-exp': {
        'input': 0.075,  # $0.075 per 1M input tokens
        'output': 0.30,  # $0.30 per 1M output tokens
    },
    'gemini-1.5-flash': {
        'input': 0.075,
        'output': 0.30,
    },
    'gemini-1.5-pro': {
        'input': 1.25,
        'output': 5.00,
    }
}


# Default cost configuration
DEFAULT_COST_CONFIG = {
    'limits': CostLimits(),
    'thresholds': AlertThresholds(),
    'pricing': GEMINI_PRICING,
    'enabled': True,
    'alert_email': None,  # Set to email address for alerts
}


def get_cost_config(user_id: str = None) -> Dict[str, Any]:
    """
    Get cost configuration for a user.
    
    Args:
        user_id: Optional user ID for user-specific config
        
    Returns:
        Cost configuration dictionary
    """
    # TODO: Implement user-specific configuration from Firestore
    return DEFAULT_COST_CONFIG


def calculate_cost(
    input_tokens: int,
    output_tokens: int,
    model: str = 'gemini-2.0-flash-exp'
) -> float:
    """
    Calculate cost for token usage.
    
    Args:
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        model: Model name
        
    Returns:
        Total cost in USD
    """
    pricing = GEMINI_PRICING.get(model, GEMINI_PRICING['gemini-2.0-flash-exp'])
    
    input_cost = (input_tokens / 1_000_000) * pricing['input']
    output_cost = (output_tokens / 1_000_000) * pricing['output']
    
    return input_cost + output_cost


def check_limit_exceeded(
    current_cost: float,
    limit: float,
    threshold: float = 1.0
) -> bool:
    """
    Check if cost exceeds limit threshold.
    
    Args:
        current_cost: Current accumulated cost
        limit: Cost limit
        threshold: Threshold percentage (default: 1.0 = 100%)
        
    Returns:
        True if threshold exceeded
    """
    return current_cost >= (limit * threshold)


def get_alert_level(
    current_cost: float,
    limit: float,
    thresholds: AlertThresholds = None
) -> str:
    """
    Get alert level based on current cost.
    
    Args:
        current_cost: Current accumulated cost
        limit: Cost limit
        thresholds: Alert thresholds
        
    Returns:
        Alert level: 'none', 'warning', 'critical', or 'emergency'
    """
    if thresholds is None:
        thresholds = AlertThresholds()
    
    percentage = current_cost / limit if limit > 0 else 0
    
    if percentage >= thresholds.emergency:
        return 'emergency'
    elif percentage >= thresholds.critical:
        return 'critical'
    elif percentage >= thresholds.warning:
        return 'warning'
    else:
        return 'none'