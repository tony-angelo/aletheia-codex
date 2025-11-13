"""
Unified Authentication for Cloud Functions.

Provides a single authentication decorator that supports both:
1. Identity-Aware Proxy (IAP) authentication (production)
2. Firebase Authentication (local development)

The decorator checks for IAP headers first, then falls back to Firebase Auth.
This allows the same code to work in both production (with IAP) and
local development (with Firebase Auth).
"""

import functools
import logging
from typing import Callable, Any, Tuple, Optional
from flask import Request, jsonify

# Import authentication modules
from shared.auth import iap_auth
from shared.auth import firebase_auth

logger = logging.getLogger(__name__)


def get_user_id_from_request(request: Request) -> Tuple[Optional[str], Optional[tuple]]:
    """
    Extract and verify user ID from request using IAP or Firebase Auth.
    
    Authentication priority:
    1. IAP (X-Goog-IAP-JWT-Assertion header) - Production
    2. Firebase Auth (Authorization: Bearer header) - Development
    
    Args:
        request: Flask request object
        
    Returns:
        Tuple of (user_id, error_response)
        If successful, error_response is None
        If failed, user_id is None and error_response contains error details
        
    Example:
        user_id, error = get_user_id_from_request(request)
        if error:
            return error
        # Use user_id...
    """
    # Try IAP authentication first (production)
    if iap_auth.IAP_HEADER in request.headers:
        logger.debug("IAP header detected, attempting IAP authentication")
        user_id, error = iap_auth.get_user_from_iap(request)
        
        if user_id:
            logger.info(f"Authenticated via IAP: {user_id}")
            return user_id, None
        
        # IAP header present but validation failed
        logger.warning(f"IAP authentication failed, not falling back to Firebase")
        return None, error
    
    # Fall back to Firebase Auth (local development)
    if "Authorization" in request.headers:
        logger.debug("Authorization header detected, attempting Firebase authentication")
        user_id, error = firebase_auth.get_user_id_from_request(request)
        
        if user_id:
            logger.info(f"Authenticated via Firebase: {user_id}")
            return user_id, None
        
        # Firebase Auth failed
        logger.warning("Firebase authentication failed")
        return None, error
    
    # No authentication headers found
    logger.warning("No authentication headers found (IAP or Firebase)")
    return None, (
        jsonify({"error": "Authentication required. Provide either IAP or Firebase Auth token."}),
        401,
        {"Access-Control-Allow-Origin": "*"}
    )


def require_auth(func: Callable) -> Callable:
    """
    Decorator to require authentication for Cloud Functions.
    
    Supports both IAP and Firebase Authentication with automatic fallback.
    Verifies authentication and adds user_id to the request object.
    
    Authentication priority:
    1. IAP (X-Goog-IAP-JWT-Assertion header) - Production
    2. Firebase Auth (Authorization: Bearer header) - Development
    
    Usage:
        @functions_framework.http
        @require_auth
        def my_function(request):
            user_id = request.user_id  # Available after authentication
            # Function logic...
    
    Returns:
        401 Unauthorized if authentication fails
        Otherwise calls the wrapped function with user_id added to request
        
    Example:
        @functions_framework.http
        @require_auth
        def notes_api(request):
            user_id = request.user_id
            # Process request for authenticated user
            return jsonify({"status": "success"})
    """
    @functools.wraps(func)
    def wrapper(request: Request, *args, **kwargs) -> Any:
        # Handle CORS preflight BEFORE authentication
        if request.method == "OPTIONS":
            headers = {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With, X-Goog-IAP-JWT-Assertion",
                "Access-Control-Max-Age": "3600",
            }
            return ("", 204, headers)
        
        # Verify authentication for all other methods
        user_id, error = get_user_id_from_request(request)
        
        if error:
            return error
        
        # Add user_id to request object for use in function
        request.user_id = user_id
        logger.info(f"Authenticated request from user: {user_id}")
        
        # Call the wrapped function
        return func(request, *args, **kwargs)
    
    return wrapper


# Export public API
__all__ = [
    "require_auth",
    "get_user_id_from_request",
]