from functools import wraps
from flask import request, jsonify
from firebase_admin import auth, initialize_app
import logging

logger = logging.getLogger(__name__)

# Initialize Firebase Admin SDK
try:
    initialize_app()
except ValueError:
    # Already initialized
    pass

def require_auth(f):
    """
    Decorator to require Firebase authentication for Cloud Functions.
    
    Usage:
        @require_auth
        def my_function(request):
            user_id = request.user_id  # Available after authentication
            # Function logic
    
    The decorator:
    1. Extracts the Authorization header from the request
    2. Verifies the Firebase ID token
    3. Adds user_id to the request object
    4. Returns 401 if authentication fails
    """
    @wraps(f)
    def decorated_function(request):
        # Get Authorization header
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            logger.warning("Missing Authorization header")
            return jsonify({'error': 'Missing Authorization header'}), 401
        
        # Extract token
        try:
            # Format: "Bearer <token>"
            token = auth_header.split('Bearer ')[1]
        except IndexError:
            logger.warning("Invalid Authorization header format")
            return jsonify({'error': 'Invalid Authorization header format. Expected: Bearer <token>'}), 401
        
        # Verify token
        try:
            decoded_token = auth.verify_id_token(token)
            user_id = decoded_token['uid']
            
            # Add user_id to request for use in function
            request.user_id = user_id
            
            logger.info(f"Authenticated request from user: {user_id}")
            
            # Call the actual function
            return f(request)
            
        except auth.InvalidIdTokenError:
            logger.warning("Invalid Firebase token")
            return jsonify({'error': 'Invalid authentication token'}), 401
        except auth.ExpiredIdTokenError:
            logger.warning("Expired Firebase token")
            return jsonify({'error': 'Authentication token expired. Please sign in again.'}), 401
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}", exc_info=True)
            return jsonify({'error': 'Authentication failed'}), 401
    
    return decorated_function


def get_user_id_from_request(request) -> str:
    """
    Extract and verify user ID from request.
    
    This is a helper function that can be used in functions that need
    the user ID but don't use the @require_auth decorator.
    
    Args:
        request: Flask request object
        
    Returns:
        str: User ID from verified Firebase token
        
    Raises:
        ValueError: If authentication fails
    """
    auth_header = request.headers.get('Authorization')
    
    if not auth_header:
        raise ValueError('Missing Authorization header')
    
    try:
        token = auth_header.split('Bearer ')[1]
    except IndexError:
        raise ValueError('Invalid Authorization header format')
    
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token['uid']
    except auth.InvalidIdTokenError:
        raise ValueError('Invalid authentication token')
    except auth.ExpiredIdTokenError:
        raise ValueError('Authentication token expired')
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}", exc_info=True)
        raise ValueError('Authentication failed')