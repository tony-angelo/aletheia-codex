"""
Firebase Authentication middleware for Cloud Functions.

Provides decorator and utilities for verifying Firebase ID tokens
and extracting authenticated user information.
"""

import functools
import logging
from typing import Callable, Any, Tuple
from flask import Request, jsonify
import firebase_admin
from firebase_admin import auth, credentials
import os

logger = logging.getLogger(__name__)

# Initialize Firebase Admin SDK (only once)
_firebase_initialized = False

def _initialize_firebase():
    """Initialize Firebase Admin SDK if not already initialized."""
    global _firebase_initialized
    
    if not _firebase_initialized:
        try:
            # Try to initialize with default credentials
            firebase_admin.initialize_app()
            _firebase_initialized = True
            logger.info("Firebase Admin SDK initialized successfully")
        except ValueError as e:
            # Already initialized
            if "already exists" in str(e):
                _firebase_initialized = True
                logger.info("Firebase Admin SDK already initialized")
            else:
                raise
        except Exception as e:
            logger.error(f"Failed to initialize Firebase Admin SDK: {str(e)}")
            raise


def verify_firebase_token(id_token: str) -> dict:
    """
    Verify Firebase ID token and return decoded token.
    
    Args:
        id_token: Firebase ID token from Authorization header
        
    Returns:
        Decoded token containing user information
        
    Raises:
        Exception: If token is invalid or verification fails
    """
    _initialize_firebase()
    
    try:
        # Verify the token
        decoded_token = auth.verify_id_token(id_token)
        logger.info(f"Token verified for user: {decoded_token.get('uid')}")
        return decoded_token
    except auth.InvalidIdTokenError as e:
        logger.warning(f"Invalid ID token: {str(e)}")
        raise Exception("Invalid authentication token")
    except auth.ExpiredIdTokenError as e:
        logger.warning(f"Expired ID token: {str(e)}")
        raise Exception("Authentication token expired")
    except Exception as e:
        logger.error(f"Token verification failed: {str(e)}")
        raise Exception("Authentication failed")


def get_user_id_from_request(request: Request) -> Tuple[str, dict]:
    """
    Extract and verify user ID from request Authorization header.
    
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
    # Get Authorization header
    auth_header = request.headers.get('Authorization')
    
    if not auth_header:
        logger.warning("Missing Authorization header")
        return None, (
            jsonify({'error': 'Missing Authorization header'}),
            401,
            {'Access-Control-Allow-Origin': '*'}
        )
    
    # Check format: "Bearer <token>"
    parts = auth_header.split(' ')
    if len(parts) != 2 or parts[0] != 'Bearer':
        logger.warning(f"Invalid Authorization header format: {auth_header[:20]}...")
        return None, (
            jsonify({'error': 'Invalid Authorization header format. Expected: Bearer <token>'}),
            401,
            {'Access-Control-Allow-Origin': '*'}
        )
    
    id_token = parts[1]
    
    # Verify token
    try:
        decoded_token = verify_firebase_token(id_token)
        user_id = decoded_token.get('uid')
        
        if not user_id:
            logger.error("Token verified but no uid found")
            return None, (
                jsonify({'error': 'Invalid token: missing user ID'}),
                401,
                {'Access-Control-Allow-Origin': '*'}
            )
        
        return user_id, None
        
    except Exception as e:
        logger.error(f"Token verification failed: {str(e)}")
        return None, (
            jsonify({'error': str(e)}),
            401,
            {'Access-Control-Allow-Origin': '*'}
        )


def require_auth(func: Callable) -> Callable:
    """
    Decorator to require Firebase authentication for Cloud Functions.
    
    Verifies Firebase ID token from Authorization header and adds
    user_id to the request object.
    
    Usage:
        @functions_framework.http
        @require_auth
        def my_function(request):
            user_id = request.user_id  # Available after authentication
            # Function logic...
    
    Returns:
        401 Unauthorized if authentication fails
        Otherwise calls the wrapped function
    """
    @functools.wraps(func)
    def wrapper(request: Request, *args, **kwargs) -> Any:
        # Handle CORS preflight
        if request.method == 'OPTIONS':
            headers = {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                'Access-Control-Max-Age': '3600',
            }
            return ('', 204, headers)
        
        # Verify authentication
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
    'require_auth',
    'get_user_id_from_request',
    'verify_firebase_token',
]