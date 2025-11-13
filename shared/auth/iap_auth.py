"""
Identity-Aware Proxy (IAP) Authentication for Cloud Functions.

Provides utilities for validating IAP JWT tokens and extracting
authenticated user information from IAP headers.

IAP adds a signed JWT assertion to requests in the X-Goog-IAP-JWT-Assertion
header. This module validates the JWT signature and extracts user identity.
"""

import logging
import os
from typing import Tuple, Optional
from flask import Request, jsonify
from google.auth.transport import requests
from google.oauth2 import id_token

logger = logging.getLogger(__name__)

# IAP configuration
IAP_ISSUER = "https://cloud.google.com/iap"
IAP_HEADER = "X-Goog-IAP-JWT-Assertion"


def get_expected_audience() -> Optional[str]:
    """
    Get expected IAP audience from environment variable.
    
    The audience should be in the format:
    /projects/<project-number>/apps/<project-id>
    
    Returns:
        Expected audience string or None if not configured
    """
    audience = os.environ.get("IAP_AUDIENCE")
    if not audience:
        logger.warning("IAP_AUDIENCE environment variable not set")
    return audience


def validate_iap_jwt(jwt_token: str, expected_audience: Optional[str] = None) -> dict:
    """
    Validate IAP JWT token signature and claims.
    
    Verifies:
    - JWT signature using Google's public keys
    - Token expiration
    - Issuer is https://cloud.google.com/iap
    - Audience matches expected value (if provided)
    
    Args:
        jwt_token: JWT token from X-Goog-IAP-JWT-Assertion header
        expected_audience: Expected audience claim (optional)
        
    Returns:
        Decoded token containing user information
        
    Raises:
        Exception: If token validation fails
        
    Example:
        >>> token = request.headers.get('X-Goog-IAP-JWT-Assertion')
        >>> decoded = validate_iap_jwt(token, '/projects/123/apps/my-app')
        >>> user_email = decoded.get('email')
    """
    try:
        # Get expected audience from environment if not provided
        if expected_audience is None:
            expected_audience = get_expected_audience()
        
        # Verify token signature and claims using google-auth library
        # This automatically:
        # - Fetches Google's public keys
        # - Verifies signature
        # - Checks expiration
        # - Validates audience (if provided)
        decoded_token = id_token.verify_token(
            jwt_token,
            requests.Request(),
            audience=expected_audience,
            certs_url="https://www.gstatic.com/iap/verify/public_key-jwk"
        )
        
        # Validate issuer
        issuer = decoded_token.get("iss")
        if issuer != IAP_ISSUER:
            raise ValueError(f"Invalid issuer: {issuer}, expected: {IAP_ISSUER}")
        
        # Log successful validation
        user_email = decoded_token.get("email", "unknown")
        logger.info(f"IAP JWT validated successfully for user: {user_email}")
        
        return decoded_token
        
    except ValueError as e:
        logger.warning(f"IAP JWT validation failed: {str(e)}")
        raise Exception(f"Invalid IAP token: {str(e)}")
    except Exception as e:
        logger.error(f"IAP JWT validation error: {str(e)}")
        raise Exception(f"IAP token validation failed: {str(e)}")


def extract_user_from_iap_token(decoded_token: dict) -> str:
    """
    Extract user identifier from decoded IAP token.
    
    Uses email as the primary user identifier for consistency
    with Firebase Authentication.
    
    Args:
        decoded_token: Decoded IAP JWT token
        
    Returns:
        User email address
        
    Raises:
        Exception: If email claim is missing
        
    Example:
        >>> decoded = validate_iap_jwt(token)
        >>> user_id = extract_user_from_iap_token(decoded)
    """
    email = decoded_token.get("email")
    
    if not email:
        logger.error("IAP token missing email claim")
        raise Exception("IAP token missing email claim")
    
    logger.debug(f"Extracted user email from IAP token: {email}")
    return email


def get_user_from_iap(request: Request) -> Tuple[Optional[str], Optional[tuple]]:
    """
    Extract and verify user ID from IAP headers.
    
    Extracts JWT from X-Goog-IAP-JWT-Assertion header, validates it,
    and returns the user email.
    
    Args:
        request: Flask request object
        
    Returns:
        Tuple of (user_id, error_response)
        If successful, error_response is None
        If failed, user_id is None and error_response contains error details
        
    Example:
        user_id, error = get_user_from_iap(request)
        if error:
            return error
        # Use user_id...
    """
    # Check for IAP header
    jwt_token = request.headers.get(IAP_HEADER)
    
    if not jwt_token:
        logger.debug(f"Missing {IAP_HEADER} header")
        return None, (
            jsonify({"error": f"Missing {IAP_HEADER} header"}),
            401,
            {"Access-Control-Allow-Origin": "*"}
        )
    
    # Validate JWT token
    try:
        decoded_token = validate_iap_jwt(jwt_token)
        user_id = extract_user_from_iap_token(decoded_token)
        
        logger.info(f"IAP authentication successful for user: {user_id}")
        return user_id, None
        
    except Exception as e:
        logger.error(f"IAP authentication failed: {str(e)}")
        return None, (
            jsonify({"error": f"IAP authentication failed: {str(e)}"}),
            401,
            {"Access-Control-Allow-Origin": "*"}
        )


# Export public API
__all__ = [
    "validate_iap_jwt",
    "extract_user_from_iap_token",
    "get_user_from_iap",
    "IAP_HEADER",
]