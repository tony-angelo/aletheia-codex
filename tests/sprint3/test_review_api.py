"""
Tests for the Review API Cloud Functions.
"""

import pytest
import os
import json
from unittest.mock import Mock, patch, MagicMock
from flask import Flask

# Set environment variable before importing
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/workspace/aletheia-codex-prod-af9a64a7fcaa.json'

# Import the API module
import sys
sys.path.append('/workspace/aletheia-codex/functions/review_api')

from main import (
    handle_request, handle_health_check, handle_get_pending_items,
    handle_approve_item, handle_reject_item,
    handle_batch_approve_items, handle_batch_reject_items,
    handle_get_user_stats, verify_auth_token, cors_response
)


@pytest.fixture
def app():
    """Create Flask app for testing."""
    app = Flask(__name__)
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def mock_queue_manager():
    """Mock queue manager."""
    with patch('main.get_queue_manager') as mock:
        manager = MagicMock()
        mock.return_value = manager
        yield manager


@pytest.fixture
def mock_approval_workflow():
    """Mock approval workflow."""
    with patch('main.get_approval_workflow') as mock:
        workflow = MagicMock()
        mock.return_value = workflow
        yield workflow


@pytest.fixture
def mock_batch_processor():
    """Mock batch processor."""
    with patch('main.get_batch_processor') as mock:
        processor = MagicMock()
        mock.return_value = processor
        yield processor


@pytest.fixture
def sample_review_items():
    """Sample review items for testing."""
    from shared.models.review_item import ReviewItem, ReviewItemType, ReviewItemStatus
    from datetime import datetime
    
    entity_item = ReviewItem(
        id="entity-123",
        user_id="test-user",
        type=ReviewItemType.ENTITY,
        status=ReviewItemStatus.PENDING,
        confidence=0.85,
        source_document_id="doc-123",
        entity={'name': 'John Doe', 'type': 'Person'},
        created_at=datetime.utcnow()
    )
    
    relationship_item = ReviewItem(
        id="rel-123",
        user_id="test-user",
        type=ReviewItemType.RELATIONSHIP,
        status=ReviewItemStatus.PENDING,
        confidence=0.75,
        source_document_id="doc-123",
        relationship={
            'source_entity': 'John Doe',
            'target_entity': 'Acme Corp',
            'relationship_type': 'WORKS_AT'
        },
        created_at=datetime.utcnow()
    )
    
    return [entity_item, relationship_item]


class TestVerifyAuthToken:
    """Test suite for token verification."""
    
    def test_verify_auth_token_bearer_missing(self, app):
        """Test missing Authorization header."""
        with app.test_request_context('/'):
            request = Mock()
            request.headers = {}
            
            result = verify_auth_token(request)
            assert result is None
    
    def test_verify_auth_token_invalid_format(self, app):
        """Test invalid Authorization header format."""
        with app.test_request_context('/'):
            request = Mock()
            request.headers = {'Authorization': 'InvalidFormat token123'}
            
            result = verify_auth_token(request)
            assert result is None
    
    def test_verify_auth_token_test_token(self, app):
        """Test test token verification."""
        with app.test_request_context('/'):
            request = Mock()
            request.headers = {'Authorization': 'Bearer test-token'}
            
            result = verify_auth_token(request)
            assert result == 'test-user'
    
    def test_verify_auth_token_base64_json(self, app):
        """Test base64 JSON token verification."""
        import base64
        
        token_data = {'user_id': 'user-123'}
        token_json = json.dumps(token_data)
        token_b64 = base64.b64encode(token_json.encode()).decode()
        
        with app.test_request_context('/'):
            request = Mock()
            request.headers = {'Authorization': f'Bearer {token_b64}'}
            
            result = verify_auth_token(request)
            assert result == 'user-123'


class TestCorsResponse:
    """Test suite for CORS response helper."""
    
    def test_cors_response_basic(self, app):
        """Test basic CORS response."""
        data = {'message': 'test'}
        
        with app.test_request_context('/'):
            response = cors_response(data, 200)
            
            assert response.status_code == 200
            assert 'Access-Control-Allow-Origin' in response.headers


class TestHealthCheck:
    """Test suite for health check endpoint."""
    
    def test_handle_health_check(self):
        """Test health check returns success."""
        response = handle_health_check()
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['status'] == 'healthy'


class TestGetPendingItems:
    """Test suite for getting pending items."""
    
    def test_get_pending_items_success(self, mock_queue_manager, sample_review_items, app):
        """Test successfully getting pending items."""
        mock_queue_manager.get_pending_items.return_value = sample_review_items
        
        with app.test_request_context('/review/pending?limit=10&min_confidence=0.5&type=entity'):
            request = Mock()
            request.args = {
                'limit': '10',
                'min_confidence': '0.5',
                'type': 'entity',
                'order_by': 'confidence',
                'descending': 'true'
            }
            
            response = handle_get_pending_items(request, 'test-user')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert len(data['data']['items']) == 2
            assert data['data']['count'] == 2
    
    def test_get_pending_items_invalid_type(self, mock_queue_manager, app):
        """Test invalid item type parameter."""
        with app.test_request_context('/review/pending?type=invalid'):
            request = Mock()
            request.args = {'type': 'invalid'}
            
            response = handle_get_pending_items(request, 'test-user')
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['success'] is False
            assert data['error']['code'] == 'INVALID_PARAMETER'
    
    def test_get_pending_items_invalid_limit(self, mock_queue_manager, app):
        """Test invalid limit parameter."""
        with app.test_request_context('/review/pending?limit=invalid'):
            request = Mock()
            request.args = {'limit': 'invalid'}
            
            response = handle_get_pending_items(request, 'test-user')
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['success'] is False


class TestApproveItem:
    """Test suite for approving items."""
    
    def test_approve_item_success(self, mock_approval_workflow, sample_review_items, app):
        """Test successfully approving an entity."""
        mock_approval_workflow.approve_entity.return_value = True
        mock_approval_workflow.approve_relationship.return_value = True
        
        # Mock get_item_by_id
        with patch('main.get_queue_manager') as mock_qm:
            queue_manager = MagicMock()
            queue_manager.get_item_by_id.return_value = sample_review_items[0]
            mock_qm.return_value = queue_manager
            
            with app.test_request_context('/review/approve', method='POST'):
                request = Mock()
                request.get_json.return_value = {'item_id': 'entity-123'}
                
                response = handle_approve_item(request, 'test-user')
                
                assert response.status_code == 200
                data = json.loads(response.data)
                assert data['success'] is True
                assert data['data']['item_id'] == 'entity-123'
    
    def test_approve_item_missing_item_id(self, app):
        """Test approving item with missing item_id."""
        with app.test_request_context('/review/approve', method='POST'):
            request = Mock()
            request.get_json.return_value = {}
            
            response = handle_approve_item(request, 'test-user')
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['error']['code'] == 'INVALID_REQUEST'
    
    def test_approve_item_empty_item_id(self, app):
        """Test approving item with empty item_id."""
        with app.test_request_context('/review/approve', method='POST'):
            request = Mock()
            request.get_json.return_value = {'item_id': ''}
            
            response = handle_approve_item(request, 'test-user')
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['error']['code'] == 'INVALID_REQUEST'
    
    def test_approve_item_not_found(self, app):
        """Test approving item that doesn't exist."""
        with patch('main.get_queue_manager') as mock_qm:
            queue_manager = MagicMock()
            queue_manager.get_item_by_id.return_value = None
            mock_qm.return_value = queue_manager
            
            with app.test_request_context('/review/approve', method='POST'):
                request = Mock()
                request.get_json.return_value = {'item_id': 'nonexistent'}
                
                response = handle_approve_item(request, 'test-user')
                
                assert response.status_code == 404
                data = json.loads(response.data)
                assert data['error']['code'] == 'NOT_FOUND'


class TestRejectItem:
    """Test suite for rejecting items."""
    
    def test_reject_item_success(self, mock_approval_workflow, sample_review_items, app):
        """Test successfully rejecting an entity."""
        mock_approval_workflow.reject_entity.return_value = True
        mock_approval_workflow.reject_relationship.return_value = True
        
        # Mock get_item_by_id
        with patch('main.get_queue_manager') as mock_qm:
            queue_manager = MagicMock()
            queue_manager.get_item_by_id.return_value = sample_review_items[0]
            mock_qm.return_value = queue_manager
            
            with app.test_request_context('/review/reject', method='POST'):
                request = Mock()
                request.get_json.return_value = {'item_id': 'entity-123', 'reason': 'Low quality'}
                
                response = handle_reject_item(request, 'test-user')
                
                assert response.status_code == 200
                data = json.loads(response.data)
                assert data['success'] is True
                assert data['data']['item_id'] == 'entity-123'
                assert data['data']['reason'] == 'Low quality'
    
    def test_reject_item_missing_item_id(self, app):
        """Test rejecting item with missing item_id."""
        with app.test_request_context('/review/reject', method='POST'):
            request = Mock()
            request.get_json.return_value = {}
            
            response = handle_reject_item(request, 'test-user')
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['error']['code'] == 'INVALID_REQUEST'


class TestBatchApproveItems:
    """Test suite for batch approving items."""
    
    def test_batch_approve_success(self, mock_batch_processor, app):
        """Test successfully batch approving items."""
        # Mock batch result
        from shared.review.batch_processor import BatchResult, BatchOperationType
        from datetime import datetime
        
        mock_result = BatchResult(
            total_items=2,
            successful=['item1', 'item2'],
            failed=[],
            operation_type=BatchOperationType.APPROVE,
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            duration_seconds=1.0
        )
        mock_batch_processor.batch_approve.return_value = mock_result
        
        with app.test_request_context('/review/batch-approve', method='POST'):
            request = Mock()
            request.get_json.return_value = {'item_ids': ['item1', 'item2']}
            
            response = handle_batch_approve_items(request, 'test-user')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['data']['total_items'] == 2
            assert len(data['data']['successful']) == 2
    
    def test_batch_approve_missing_item_ids(self, app):
        """Test batch approving with missing item_ids."""
        with app.test_request_context('/review/batch-approve', method='POST'):
            request = Mock()
            request.get_json.return_value = {}
            
            response = handle_batch_approve_items(request, 'test-user')
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['error']['code'] == 'INVALID_REQUEST'
    
    def test_batch_approve_invalid_item_ids(self, app):
        """Test batch approving with invalid item_ids."""
        with app.test_request_context('/review/batch-approve', method='POST'):
            request = Mock()
            request.get_json.return_value = {'item_ids': []}
            
            response = handle_batch_approve_items(request, 'test-user')
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['error']['code'] == 'INVALID_REQUEST'


class TestBatchRejectItems:
    """Test suite for batch rejecting items."""
    
    def test_batch_reject_success(self, mock_batch_processor, app):
        """Test successfully batch rejecting items."""
        # Mock batch result
        from shared.review.batch_processor import BatchResult, BatchOperationType
        from datetime import datetime
        
        mock_result = BatchResult(
            total_items=2,
            successful=['item1', 'item2'],
            failed=[],
            operation_type=BatchOperationType.REJECT,
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            duration_seconds=1.0
        )
        mock_batch_processor.batch_reject.return_value = mock_result
        
        with app.test_request_context('/review/batch-reject', method='POST'):
            request = Mock()
            request.get_json.return_value = {'item_ids': ['item1', 'item2'], 'reason': 'Low confidence'}
            
            response = handle_batch_reject_items(request, 'test-user')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['data']['total_items'] == 2


class TestGetUserStats:
    """Test suite for getting user statistics."""
    
    def test_get_user_stats_success(self, mock_queue_manager, app):
        """Test successfully getting user stats."""
        # Mock user stats
        from shared.models.review_item import UserStats
        mock_stats = UserStats(
            user_id='test-user',
            total_pending=5,
            total_approved=10,
            total_rejected=2,
            average_confidence=0.82
        )
        mock_queue_manager.get_user_stats.return_value = mock_stats
        
        with app.test_request_context('/review/stats'):
            request = Mock()
            
            response = handle_get_user_stats(request, 'test-user')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['data']['user_id'] == 'test-user'
            assert data['data']['total_pending'] == 5


class TestMainRequestHandler:
    """Test suite for main request handler."""
    
    def test_handle_request_health_check(self, app):
        """Test health check route."""
        with app.test_request_context('/health', method='GET'):
            request = Mock()
            request.method = 'GET'
            request.path = '/health'
            request.headers = {}
            
            response = handle_request(request)
            
            assert response.status_code == 200
    
    def test_handle_request_unauthorized(self, app):
        """Test unauthorized request."""
        with app.test_request_context('/review/pending', method='GET'):
            request = Mock()
            request.method = 'GET'
            request.path = '/review/pending'
            request.headers = {}
            
            response = handle_request(request)
            
            assert response.status_code == 401
    
    def test_handle_request_not_found(self, app):
        """Test not found route."""
        with app.test_request_context('/nonexistent', method='GET'):
            request = Mock()
            request.method = 'GET'
            request.path = '/nonexistent'
            request.headers = {'Authorization': 'Bearer test-token'}
            
            response = handle_request(request)
            
            assert response.status_code == 404
    
    def test_handle_request_options_cors(self, app):
        """Test OPTIONS request for CORS."""
        with app.test_request_context('/review/pending', method='OPTIONS'):
            request = Mock()
            request.method = 'OPTIONS'
            request.path = '/review/pending'
            request.headers = {}
            
            response = handle_request(request)
            
            assert response.status_code == 200
            assert 'Access-Control-Allow-Methods' in response.headers


if __name__ == '__main__':
    pytest.main([__file__, '-v'])