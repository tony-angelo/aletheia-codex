"""
Review API Cloud Functions for AletheiaCodex (with Firebase Authentication).

Provides HTTP endpoints for managing the review queue, including:
- Getting pending items
- Approving/rejecting items
- Batch operations
- User statistics
"""

import functions_framework
import flask
from flask import Request, jsonify
import os
import sys
from typing import Dict, Any
from datetime import datetime

# Add shared directory to path (local to this function)
sys.path.insert(0, os.path.dirname(__file__))

from shared.auth.firebase_auth import require_auth
from shared.review.queue_manager import create_queue_manager
from shared.review.approval_workflow import create_approval_workflow
from shared.review.batch_processor import create_batch_processor
from shared.models.review_item import ReviewItemType
from shared.utils.logging import get_logger

logger = get_logger(__name__)

# Configuration
PROJECT_ID = os.environ.get('GCP_PROJECT', 'aletheia-codex-prod')

# CORS configuration
ALLOWED_ORIGINS = [
    'https://aletheia-codex-prod.web.app',
    'https://aletheiacodex.app',
    'http://localhost:3000'
]

# Initialize managers (lazy initialization)
_queue_manager = None
_approval_workflow = None
_batch_processor = None


def get_queue_manager():
    """Get or create queue manager instance."""
    global _queue_manager
    if _queue_manager is None:
        _queue_manager = create_queue_manager(PROJECT_ID)
    return _queue_manager


def get_approval_workflow():
    """Get or create approval workflow instance."""
    global _approval_workflow
    if _approval_workflow is None:
        _approval_workflow = create_approval_workflow(PROJECT_ID)
    return _approval_workflow


def get_batch_processor():
    """Get or create batch processor instance."""
    global _batch_processor
    if _batch_processor is None:
        _batch_processor = create_batch_processor(PROJECT_ID)
    return _batch_processor


def add_cors_headers(response, origin):
    """Add CORS headers to response."""
    if origin in ALLOWED_ORIGINS:
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        response.headers['Access-Control-Max-Age'] = '3600'
    return response


def cors_response(response_data: Dict[str, Any], status_code: int = 200, origin: str = None):
    """Create response with CORS headers."""
    import json
    
    response_data_str = json.dumps(response_data)
    response = flask.Response(response=response_data_str, status=status_code, mimetype='application/json')
    
    # Add CORS headers if origin is provided
    if origin:
        response = add_cors_headers(response, origin)
    
    return response


@functions_framework.http
@require_auth  # Require Firebase authentication
def handle_request(request: Request) -> flask.Response:
    """
    Main request handler for review API (authenticated).
    
    Routes:
    - GET /review/pending - Get pending review items
    - POST /review/approve - Approve a single item
    - POST /review/reject - Reject a single item
    - POST /review/batch-approve - Batch approve items
    - POST /review/batch-reject - Batch reject items
    - GET /review/stats - Get user statistics
    """
    origin = request.headers.get('Origin')
    
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        return add_cors_headers(response, origin)
    
    try:
        # Get authenticated user ID (set by @require_auth decorator)
        user_id = request.user_id
        logger.info(f"Processing review API request for user: {user_id}")
        
        # Extract route from path
        path = request.path.strip('/')
        
        # Route to appropriate handler
        # Handle both full path (direct call) and stripped path (Firebase Hosting rewrite)
        if (path == 'review/pending' or path == 'pending') and request.method == 'GET':
            return handle_get_pending_items(request, user_id, origin)
        elif (path == 'review/approve' or path == 'approve') and request.method == 'POST':
            return handle_approve_item(request, user_id, origin)
        elif (path == 'review/reject' or path == 'reject') and request.method == 'POST':
            return handle_reject_item(request, user_id, origin)
        elif (path == 'review/batch-approve' or path == 'batch-approve') and request.method == 'POST':
            return handle_batch_approve_items(request, user_id, origin)
        elif (path == 'review/batch-reject' or path == 'batch-reject') and request.method == 'POST':
            return handle_batch_reject_items(request, user_id, origin)
        elif (path == 'review/stats' or path == 'stats') and request.method == 'GET':
            return handle_get_user_stats(request, user_id, origin)
        else:
            return cors_response({
                'success': False,
                'error': {
                    'code': 'NOT_FOUND',
                    'message': f'Endpoint not found: {request.method} {path}'
                }
            }, 404, origin)
    
    except Exception as e:
        logger.error(f"Unhandled error in request handler: {str(e)}", exc_info=True)
        return cors_response({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': f'An internal error occurred: {str(e)}'
            }
        }, 500, origin)


def handle_get_pending_items(request: Request, user_id: str, origin: str = None) -> flask.Response:
    """
    Handle GET /review/pending requests.
    
    Query parameters:
    - limit: Maximum number of items (default: 50, max: 100)
    - min_confidence: Minimum confidence threshold (default: 0.0)
    - type: Filter by item type (entity/relationship, optional)
    - order_by: Field to order by (default: confidence)
    - descending: Order direction (default: true)
    """
    try:
        # Parse query parameters
        limit = min(int(request.args.get('limit', 50)), 100)
        min_confidence = float(request.args.get('min_confidence', 0.0))
        item_type = request.args.get('type')
        order_by = request.args.get('order_by', 'confidence')
        descending = request.args.get('descending', 'true').lower() == 'true'
        
        # Validate item type
        item_type_enum = None
        if item_type:
            if item_type.lower() == 'entity':
                item_type_enum = ReviewItemType.ENTITY
            elif item_type.lower() == 'relationship':
                item_type_enum = ReviewItemType.RELATIONSHIP
            else:
                return cors_response({
                    'success': False,
                    'error': {
                        'code': 'INVALID_PARAMETER',
                        'message': 'Invalid type parameter. Must be "entity" or "relationship"'
                    }
                }, 400, origin)
        
        # Get pending items
        queue_manager = get_queue_manager()
        items = queue_manager.get_pending_items(
            user_id=user_id,
            limit=limit,
            min_confidence=min_confidence,
            item_type=item_type_enum,
            order_by=order_by,
            descending=descending
        )
        
        # Convert to dictionary format
        items_data = [item.to_dict() for item in items]
        
        return cors_response({
            'success': True,
            'data': {
                'items': items_data,
                'count': len(items_data),
                'filters': {
                    'limit': limit,
                    'min_confidence': min_confidence,
                    'type': item_type,
                    'order_by': order_by,
                    'descending': descending
                }
            }
        }, origin)
        
    except ValueError as e:
        logger.error(f"Invalid parameter in get_pending_items: {str(e)}")
        return cors_response({
            'success': False,
            'error': {
                'code': 'INVALID_PARAMETER',
                'message': str(e)
            }
        }, 400, origin)
    except Exception as e:
        logger.error(f"Error getting pending items: {str(e)}", exc_info=True)
        return cors_response({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Failed to get pending items'
            }
        }, 500, origin)


def handle_approve_item(request: Request, user_id: str, origin: str = None) -> flask.Response:
    """
    Handle POST /review/approve requests.
    
    Body:
    {
        "item_id": "string"
    }
    """
    try:
        # Parse request body
        data = request.get_json()
        if not data or 'item_id' not in data:
            return cors_response({
                'success': False,
                'error': {
                    'code': 'INVALID_REQUEST',
                    'message': 'Missing required field: item_id'
                }
            }, 400, origin)
        
        item_id = data['item_id']
        if not item_id or not item_id.strip():
            return cors_response({
                'success': False,
                'error': {
                    'code': 'INVALID_REQUEST',
                    'message': 'item_id cannot be empty'
                }
            }, 400, origin)
        
        # Get item and verify user owns it (SECURITY CHECK)
        queue_manager = get_queue_manager()
        item = queue_manager.get_item_by_id(item_id)
        
        if not item:
            return cors_response({
                'success': False,
                'error': {
                    'code': 'NOT_FOUND',
                    'message': 'Review item not found'
                }
            }, 404, origin)
        
        # Verify user owns this item
        if item.user_id != user_id:
            logger.warning(f"User {user_id} attempted to approve item owned by {item.user_id}")
            return cors_response({
                'success': False,
                'error': {
                    'code': 'FORBIDDEN',
                    'message': 'You do not have permission to approve this item'
                }
            }, 403, origin)
        
        # Approve item
        approval_workflow = get_approval_workflow()
        success = False
        if item.type == ReviewItemType.ENTITY:
            success = approval_workflow.approve_entity(item_id, user_id)
        else:
            success = approval_workflow.approve_relationship(item_id, user_id)
        
        if success:
            return cors_response({
                'success': True,
                'data': {
                    'item_id': item_id,
                    'approved_at': datetime.utcnow().isoformat()
                }
            }, origin)
        else:
            return cors_response({
                'success': False,
                'error': {
                    'code': 'APPROVAL_FAILED',
                    'message': 'Failed to approve item'
                }
            }, 500, origin)
        
    except Exception as e:
        logger.error(f"Error approving item: {str(e)}", exc_info=True)
        return cors_response({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Failed to approve item'
            }
        }, 500, origin)


def handle_reject_item(request: Request, user_id: str, origin: str = None) -> flask.Response:
    """
    Handle POST /review/reject requests.
    
    Body:
    {
        "item_id": "string",
        "reason": "string" (optional)
    }
    """
    try:
        # Parse request body
        data = request.get_json()
        if not data or 'item_id' not in data:
            return cors_response({
                'success': False,
                'error': {
                    'code': 'INVALID_REQUEST',
                    'message': 'Missing required field: item_id'
                }
            }, 400, origin)
        
        item_id = data['item_id']
        if not item_id or not item_id.strip():
            return cors_response({
                'success': False,
                'error': {
                    'code': 'INVALID_REQUEST',
                    'message': 'item_id cannot be empty'
                }
            }, 400, origin)
        
        reason = data.get('reason')
        
        # Get item and verify user owns it (SECURITY CHECK)
        queue_manager = get_queue_manager()
        item = queue_manager.get_item_by_id(item_id)
        
        if not item:
            return cors_response({
                'success': False,
                'error': {
                    'code': 'NOT_FOUND',
                    'message': 'Review item not found'
                }
            }, 404, origin)
        
        # Verify user owns this item
        if item.user_id != user_id:
            logger.warning(f"User {user_id} attempted to reject item owned by {item.user_id}")
            return cors_response({
                'success': False,
                'error': {
                    'code': 'FORBIDDEN',
                    'message': 'You do not have permission to reject this item'
                }
            }, 403, origin)
        
        # Reject item
        approval_workflow = get_approval_workflow()
        success = False
        if item.type == ReviewItemType.ENTITY:
            success = approval_workflow.reject_entity(item_id, user_id, reason)
        else:
            success = approval_workflow.reject_relationship(item_id, user_id, reason)
        
        if success:
            return cors_response({
                'success': True,
                'data': {
                    'item_id': item_id,
                    'rejected_at': datetime.utcnow().isoformat(),
                    'reason': reason
                }
            }, origin)
        else:
            return cors_response({
                'success': False,
                'error': {
                    'code': 'REJECTION_FAILED',
                    'message': 'Failed to reject item'
                }
            }, 500, origin)
        
    except Exception as e:
        logger.error(f"Error rejecting item: {str(e)}", exc_info=True)
        return cors_response({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Failed to reject item'
            }
        }, 500, origin)


def handle_batch_approve_items(request: Request, user_id: str, origin: str = None) -> flask.Response:
    """
    Handle POST /review/batch-approve requests.
    
    Body:
    {
        "item_ids": ["string"]
    }
    """
    try:
        # Parse request body
        data = request.get_json()
        if not data or 'item_ids' not in data:
            return cors_response({
                'success': False,
                'error': {
                    'code': 'INVALID_REQUEST',
                    'message': 'Missing required field: item_ids'
                }
            }, 400, origin)
        
        item_ids = data['item_ids']
        if not isinstance(item_ids, list) or len(item_ids) == 0:
            return cors_response({
                'success': False,
                'error': {
                    'code': 'INVALID_REQUEST',
                    'message': 'item_ids must be a non-empty array'
                }
            }, 400, origin)
        
        # Batch approve
        batch_processor = get_batch_processor()
        result = batch_processor.batch_approve(item_ids, user_id)
        
        return cors_response({
            'success': True,
            'data': result.to_dict()
        }, origin)
        
    except Exception as e:
        logger.error(f"Error in batch approve: {str(e)}", exc_info=True)
        return cors_response({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Failed to batch approve items'
            }
        }, 500, origin)


def handle_batch_reject_items(request: Request, user_id: str, origin: str = None) -> flask.Response:
    """
    Handle POST /review/batch-reject requests.
    
    Body:
    {
        "item_ids": ["string"],
        "reason": "string" (optional)
    }
    """
    try:
        # Parse request body
        data = request.get_json()
        if not data or 'item_ids' not in data:
            return cors_response({
                'success': False,
                'error': {
                    'code': 'INVALID_REQUEST',
                    'message': 'Missing required field: item_ids'
                }
            }, 400, origin)
        
        item_ids = data['item_ids']
        if not isinstance(item_ids, list) or len(item_ids) == 0:
            return cors_response({
                'success': False,
                'error': {
                    'code': 'INVALID_REQUEST',
                    'message': 'item_ids must be a non-empty array'
                }
            }, 400, origin)
        
        reason = data.get('reason')
        
        # Batch reject
        batch_processor = get_batch_processor()
        result = batch_processor.batch_reject(item_ids, user_id, reason)
        
        return cors_response({
            'success': True,
            'data': result.to_dict()
        }, origin)
        
    except Exception as e:
        logger.error(f"Error in batch reject: {str(e)}", exc_info=True)
        return cors_response({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Failed to batch reject items'
            }
        }, 500, origin)


def handle_get_user_stats(request: Request, user_id: str, origin: str = None) -> flask.Response:
    """Handle GET /review/stats requests."""
    try:
        # Get user statistics
        queue_manager = get_queue_manager()
        stats = queue_manager.get_user_stats(user_id)
        
        return cors_response({
            'success': True,
            'data': stats.to_dict()
        }, origin)
        
    except Exception as e:
        logger.error(f"Error getting user stats: {str(e)}", exc_info=True)
        return cors_response({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Failed to get user statistics'
            }
        }, 500, origin)