"""
Review API Cloud Functions for AletheiaCodex.

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
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

# Add shared directory to path
import sys
sys.path.append('/workspace/aletheia-codex')

from shared.review.queue_manager import create_queue_manager
from shared.review.approval_workflow import create_approval_workflow
from shared.review.batch_processor import create_batch_processor, BatchOperationType
from shared.models.review_item import ReviewItemStatus, ReviewItemType
from shared.utils.logging import get_logger

logger = get_logger(__name__)

# Configuration
PROJECT_ID = os.environ.get('GCP_PROJECT', 'aletheia-codex-prod')
CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:3000,https://aletheia-codex-prod.web.app').split(',')

# Initialize managers (lazy initialization)
_queue_manager = None
_approval_workflow = None
_batch_processor = None

# Create Flask app for local development
app = flask.Flask(__name__)


def get_queue_manager():
    """Get or create queue manager instance."""
    global _queue_manager
    if _queue_manager is None:
        try:
            _queue_manager = create_queue_manager(PROJECT_ID)
        except Exception as e:
            logger.error(f"Failed to create queue manager: {str(e)}")
            # Create a mock queue manager for testing
            _queue_manager = MockQueueManager()
    return _queue_manager


def get_approval_workflow():
    """Get or create approval workflow instance."""
    global _approval_workflow
    if _approval_workflow is None:
        try:
            _approval_workflow = create_approval_workflow(PROJECT_ID)
        except Exception as e:
            logger.error(f"Failed to create approval workflow: {str(e)}")
            # Create a mock approval workflow for testing
            _approval_workflow = MockApprovalWorkflow()
    return _approval_workflow


def get_batch_processor():
    """Get or create batch processor instance."""
    global _batch_processor
    if _batch_processor is None:
        try:
            _batch_processor = create_batch_processor(PROJECT_ID)
        except Exception as e:
            logger.error(f"Failed to create batch processor: {str(e)}")
            # Create a mock batch processor for testing
            _batch_processor = MockBatchProcessor()
    return _batch_processor


class MockQueueManager:
    """Mock queue manager for testing when Firestore is not available."""
    
    def get_pending_items(self, user_id, limit=50, min_confidence=0.0, item_type=None, order_by='confidence', descending=True):
        return []
    
    def get_item_by_id(self, item_id):
        return None
    
    def get_user_stats(self, user_id):
        class MockStats:
            def to_dict(self):
                return {
                    'user_id': user_id,
                    'total_items': 0,
                    'pending_items': 0,
                    'approved_items': 0,
                    'rejected_items': 0,
                    'created_at': '2024-01-01T00:00:00Z',
                    'updated_at': '2024-01-01T00:00:00Z'
                }
        return MockStats()


class MockApprovalWorkflow:
    """Mock approval workflow for testing when Firestore/Neo4j are not available."""
    
    def approve_entity(self, item_id, user_id):
        return False
    
    def approve_relationship(self, item_id, user_id):
        return False
    
    def reject_entity(self, item_id, user_id, reason=None):
        return False
    
    def reject_relationship(self, item_id, user_id, reason=None):
        return False


class MockBatchProcessor:
    """Mock batch processor for testing when Firestore/Neo4j are not available."""
    
    def batch_approve(self, item_ids, user_id):
        class MockResult:
            def to_dict(self):
                return {
                    'operation_id': 'mock-op',
                    'total_items': len(item_ids),
                    'successful_items': 0,
                    'failed_items': len(item_ids),
                    'results': [{'item_id': item_id, 'success': False, 'error': 'Mock error'} for item_id in item_ids],
                    'created_at': '2024-01-01T00:00:00Z',
                    'completed_at': '2024-01-01T00:00:00Z'
                }
        return MockResult()
    
    def batch_reject(self, item_ids, user_id, reason=None):
        class MockResult:
            def to_dict(self):
                return {
                    'operation_id': 'mock-op',
                    'total_items': len(item_ids),
                    'successful_items': 0,
                    'failed_items': len(item_ids),
                    'results': [{'item_id': item_id, 'success': False, 'error': 'Mock error'} for item_id in item_ids],
                    'created_at': '2024-01-01T00:00:00Z',
                    'completed_at': '2024-01-01T00:00:00Z'
                }
        return MockResult()


def cors_response(response_data: Dict[str, Any], status_code: int = 200):
    """Create response with CORS headers."""
    import json
    
    # Create Flask response without using jsonify (which requires app context)
    response_data_str = json.dumps(response_data)
    response = flask.Response(response=response_data_str, status=status_code, mimetype='application/json')
    
    # Add CORS headers
    if flask.request and flask.request.headers.get('Origin') in CORS_ORIGINS:
        response.headers['Access-Control-Allow-Origin'] = flask.request.headers.get('Origin')
    else:
        response.headers['Access-Control-Allow-Origin'] = CORS_ORIGINS[0] if CORS_ORIGINS else '*'
    
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['Access-Control-Max-Age'] = '3600'
    
    return response


def verify_auth_token(request: Request) -> Optional[str]:
    """
    Verify Firebase Auth token and extract user ID.
    
    Args:
        request: Flask request object
        
    Returns:
        User ID if token is valid, None otherwise
    """
    try:
        auth_header = flask.request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            logger.warning("Missing or invalid Authorization header")
            return None
        
        # Extract token
        token = auth_header.split(' ')[1]
        
        # TODO: Implement Firebase Auth token verification
        # For now, return a mock user ID for testing
        # In production, this should verify the token with Firebase Auth
        logger.info(f"Auth token verification for token: {token[:20]}...")
        
        # Mock implementation - replace with real Firebase Auth verification
        if token == 'test-token':
            return 'test-user'
        
        # For development, allow any token and extract a user ID
        # In production, this should be replaced with proper token verification
        try:
            import base64
            import json
            
            # Try to decode as base64 JSON
            decoded = base64.b64decode(token).decode('utf-8')
            token_data = json.loads(decoded)
            return token_data.get('user_id')
        except:
            # Fallback to using the token as user ID for testing
            return token
        
    except Exception as e:
        logger.error(f"Error verifying auth token: {str(e)}")
        return None


@functions_framework.http
def handle_request(request: Request) -> flask.Response:
    return handle_request_internal(request)

@app.route('/', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
def handle_request_internal(path: str = '') -> flask.Response:
    """
    Main request handler for review API.
    
    Routes:
    - GET /review/pending - Get pending review items
    - POST /review/approve - Approve a single item
    - POST /review/reject - Reject a single item
    - POST /review/batch-approve - Batch approve items
    - POST /review/batch-reject - Batch reject items
    - GET /review/stats - Get user statistics
    """
    
    # Handle CORS preflight requests
    if flask.request.method == 'OPTIONS':
        return cors_response({}, 200)
    
    try:
        # Extract route from path
        if path:
            full_path = f'/{path}'
        else:
            full_path = flask.request.path.strip('/')
        
        path = full_path.strip('/')
        
        # Verify authentication for all routes except health check
        if path != 'health':
            user_id = verify_auth_token(request)
            if not user_id:
                return cors_response({
                    'success': False,
                    'error': {
                        'code': 'UNAUTHORIZED',
                        'message': 'Authentication required'
                    }
                }, 401)
        
        # Route to appropriate handler
        if path == 'health':
            return handle_health_check()
        elif path == 'review/pending' and flask.flask.request.method == 'GET':
            return handle_get_pending_items(flask.request, user_id)
        elif path == 'review/approve' and flask.request.method == 'POST':
            return handle_approve_item(flask.request, user_id)
        elif path == 'review/reject' and flask.request.method == 'POST':
            return handle_reject_item(flask.request, user_id)
        elif path == 'review/batch-approve' and flask.request.method == 'POST':
            return handle_batch_approve_items(flask.request, user_id)
        elif path == 'review/batch-reject' and flask.request.method == 'POST':
            return handle_batch_reject_items(flask.request, user_id)
        elif path == 'review/stats' and flask.request.method == 'GET':
            return handle_get_user_stats(flask.request, user_id)
        else:
            return cors_response({
                'success': False,
                'error': {
                    'code': 'NOT_FOUND',
                    'message': f'Endpoint not found: {flask.request.method} {path}'
                }
            }, 404)
    
    except Exception as e:
        logger.error(f"Unhandled error in request handler: {str(e)}")
        logger.error(f"Exception type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return cors_response({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': f'An internal error occurred: {str(e)}'
            }
        }, 500)


def handle_health_check() -> flask.Response:
    """Handle health check requests."""
    return cors_response({
        'success': True,
        'data': {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0',
            'service': 'review-api'
        }
    })


def handle_get_pending_items(request: Request, user_id: str) -> flask.Response:
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
        limit = min(int(flask.request.args.get('limit', 50)), 100)
        min_confidence = float(flask.request.args.get('min_confidence', 0.0))
        item_type = flask.request.args.get('type')
        order_by = flask.request.args.get('order_by', 'confidence')
        descending = flask.request.args.get('descending', 'true').lower() == 'true'
        
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
                }, 400)
        
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
        })
        
    except ValueError as e:
        logger.error(f"Invalid parameter in get_pending_items: {str(e)}")
        return cors_response({
            'success': False,
            'error': {
                'code': 'INVALID_PARAMETER',
                'message': str(e)
            }
        }, 400)
    except Exception as e:
        logger.error(f"Error getting pending items: {str(e)}")
        return cors_response({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Failed to get pending items'
            }
        }, 500)


def handle_approve_item(request: Request, user_id: str) -> flask.Response:
    """
    Handle POST /review/approve requests.
    
    Body:
    {
        "item_id": "string"
    }
    """
    try:
        # Parse request body
        data = flask.request.get_json()
        if not data or 'item_id' not in data:
            return cors_response({
                'success': False,
                'error': {
                    'code': 'INVALID_REQUEST',
                    'message': 'Missing required field: item_id'
                }
            }, 400)
        
        item_id = data['item_id']
        if not item_id or not item_id.strip():
            return cors_response({
                'success': False,
                'error': {
                    'code': 'INVALID_REQUEST',
                    'message': 'item_id cannot be empty'
                }
            }, 400)
        
        # Approve item
        approval_workflow = get_approval_workflow()
        item = get_queue_manager().get_item_by_id(item_id)
        
        if not item:
            return cors_response({
                'success': False,
                'error': {
                    'code': 'NOT_FOUND',
                    'message': 'Review item not found'
                }
            }, 404)
        
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
            })
        else:
            return cors_response({
                'success': False,
                'error': {
                    'code': 'APPROVAL_FAILED',
                    'message': 'Failed to approve item'
                }
            }, 500)
        
    except ValueError as e:
        logger.error(f"Validation error in approve_item: {str(e)}")
        return cors_response({
            'success': False,
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': str(e)
            }
        }, 400)
    except Exception as e:
        logger.error(f"Error approving item: {str(e)}")
        return cors_response({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Failed to approve item'
            }
        }, 500)


def handle_reject_item(request: Request, user_id: str) -> flask.Response:
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
        data = flask.request.get_json()
        if not data or 'item_id' not in data:
            return cors_response({
                'success': False,
                'error': {
                    'code': 'INVALID_REQUEST',
                    'message': 'Missing required field: item_id'
                }
            }, 400)
        
        item_id = data['item_id']
        if not item_id or not item_id.strip():
            return cors_response({
                'success': False,
                'error': {
                    'code': 'INVALID_REQUEST',
                    'message': 'item_id cannot be empty'
                }
            }, 400)
        
        reason = data.get('reason')
        
        # Reject item
        approval_workflow = get_approval_workflow()
        item = get_queue_manager().get_item_by_id(item_id)
        
        if not item:
            return cors_response({
                'success': False,
                'error': {
                    'code': 'NOT_FOUND',
                    'message': 'Review item not found'
                }
            }, 404)
        
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
            })
        else:
            return cors_response({
                'success': False,
                'error': {
                    'code': 'REJECTION_FAILED',
                    'message': 'Failed to reject item'
                }
            }, 500)
        
    except ValueError as e:
        logger.error(f"Validation error in reject_item: {str(e)}")
        return cors_response({
            'success': False,
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': str(e)
            }
        }, 400)
    except Exception as e:
        logger.error(f"Error rejecting item: {str(e)}")
        return cors_response({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Failed to reject item'
            }
        }, 500)


def handle_batch_approve_items(request: Request, user_id: str) -> flask.Response:
    """
    Handle POST /review/batch-approve requests.
    
    Body:
    {
        "item_ids": ["string"]
    }
    """
    try:
        # Parse request body
        data = flask.request.get_json()
        if not data or 'item_ids' not in data:
            return cors_response({
                'success': False,
                'error': {
                    'code': 'INVALID_REQUEST',
                    'message': 'Missing required field: item_ids'
                }
            }, 400)
        
        item_ids = data['item_ids']
        if not isinstance(item_ids, list) or len(item_ids) == 0:
            return cors_response({
                'success': False,
                'error': {
                    'code': 'INVALID_REQUEST',
                    'message': 'item_ids must be a non-empty array'
                }
            }, 400)
        
        # Batch approve
        batch_processor = get_batch_processor()
        result = batch_processor.batch_approve(item_ids, user_id)
        
        return cors_response({
            'success': True,
            'data': result.to_dict()
        })
        
    except ValueError as e:
        logger.error(f"Validation error in batch_approve: {str(e)}")
        return cors_response({
            'success': False,
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': str(e)
            }
        }, 400)
    except Exception as e:
        logger.error(f"Error in batch approve: {str(e)}")
        return cors_response({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Failed to batch approve items'
            }
        }, 500)


def handle_batch_reject_items(request: Request, user_id: str) -> flask.Response:
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
        data = flask.request.get_json()
        if not data or 'item_ids' not in data:
            return cors_response({
                'success': False,
                'error': {
                    'code': 'INVALID_REQUEST',
                    'message': 'Missing required field: item_ids'
                }
            }, 400)
        
        item_ids = data['item_ids']
        if not isinstance(item_ids, list) or len(item_ids) == 0:
            return cors_response({
                'success': False,
                'error': {
                    'code': 'INVALID_REQUEST',
                    'message': 'item_ids must be a non-empty array'
                }
            }, 400)
        
        reason = data.get('reason')
        
        # Batch reject
        batch_processor = get_batch_processor()
        result = batch_processor.batch_reject(item_ids, user_id, reason)
        
        return cors_response({
            'success': True,
            'data': result.to_dict()
        })
        
    except ValueError as e:
        logger.error(f"Validation error in batch_reject: {str(e)}")
        return cors_response({
            'success': False,
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': str(e)
            }
        }, 400)
    except Exception as e:
        logger.error(f"Error in batch reject: {str(e)}")
        return cors_response({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Failed to batch reject items'
            }
        }, 500)


def handle_get_user_stats(request: Request, user_id: str) -> flask.Response:
    """Handle GET /review/stats requests."""
    try:
        # Get user statistics
        queue_manager = get_queue_manager()
        stats = queue_manager.get_user_stats(user_id)
        
        return cors_response({
            'success': True,
            'data': stats.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Error getting user stats: {str(e)}")
        return cors_response({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Failed to get user statistics'
            }
        }, 500)


# Export for testing
__all__ = [
    'handle_request',
    'handle_health_check',
    'handle_get_pending_items',
    'handle_approve_item',
    'handle_reject_item',
    'handle_batch_approve_items',
    'handle_batch_reject_items',
    'handle_get_user_stats',
    'verify_auth_token'
]


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081, debug=True)