"""
Tests for the approval workflow.
"""

import pytest
import os
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock, call

# Set environment variable before importing
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/workspace/aletheia-codex-prod-af9a64a7fcaa.json'

from shared.review.approval_workflow import ApprovalWorkflow, create_approval_workflow
from shared.review.batch_processor import (
    BatchProcessor, BatchOperation, BatchResult, BatchOperationType, create_batch_processor
)
from shared.models.review_item import ReviewItem, ReviewItemType, ReviewItemStatus


@pytest.fixture
def mock_approval_workflow():
    """Mock approval workflow with mocked dependencies."""
    with patch('shared.review.approval_workflow.create_queue_manager') as mock_qm, \
         patch('shared.review.approval_workflow.create_graph_populator') as mock_gp:
        
        queue_manager = MagicMock()
        graph_populator = MagicMock()
        mock_qm.return_value = queue_manager
        mock_gp.return_value = graph_populator
        
        workflow = ApprovalWorkflow(project_id="test-project")
        workflow.queue_manager = queue_manager
        workflow.graph_populator = graph_populator
        
        yield workflow, queue_manager, graph_populator


@pytest.fixture
def mock_batch_processor():
    """Mock batch processor with mocked dependencies."""
    with patch('shared.review.batch_processor.create_approval_workflow') as mock_aw, \
         patch('shared.review.batch_processor.create_queue_manager') as mock_qm:
        
        approval_workflow = MagicMock()
        queue_manager = MagicMock()
        mock_aw.return_value = approval_workflow
        mock_qm.return_value = queue_manager
        
        processor = BatchProcessor(project_id="test-project")
        processor.approval_workflow = approval_workflow
        processor.queue_manager = queue_manager
        
        yield processor, approval_workflow, queue_manager


@pytest.fixture
def sample_entity_item():
    """Create a sample entity review item."""
    return ReviewItem(
        id="entity-123",
        user_id="test-user",
        type=ReviewItemType.ENTITY,
        status=ReviewItemStatus.PENDING,
        confidence=0.85,
        source_document_id="doc-123",
        entity={
            'name': 'John Doe',
            'type': 'Person',
            'properties': {'age': 30}
        },
        extracted_text="John Doe is a software engineer."
    )


@pytest.fixture
def sample_relationship_item():
    """Create a sample relationship review item."""
    return ReviewItem(
        id="rel-123",
        user_id="test-user",
        type=ReviewItemType.RELATIONSHIP,
        status=ReviewItemStatus.PENDING,
        confidence=0.75,
        source_document_id="doc-123",
        relationship={
            'source_entity': 'John Doe',
            'target_entity': 'Acme Corp',
            'relationship_type': 'WORKS_AT',
            'properties': {}
        },
        extracted_text="John Doe works at Acme Corp."
    )


class TestApprovalWorkflow:
    """Test suite for ApprovalWorkflow."""
    
    def test_initialization(self, mock_approval_workflow):
        """Test approval workflow initialization."""
        workflow, _, _ = mock_approval_workflow
        assert workflow.project_id == "test-project"
    
    def test_approve_entity_success(self, mock_approval_workflow, sample_entity_item):
        """Test successfully approving an entity."""
        workflow, queue_manager, graph_populator = mock_approval_workflow
        
        # Mock get_item_by_id
        queue_manager.get_item_by_id.return_value = sample_entity_item
        
        # Mock update_item_status
        queue_manager.update_item_status.return_value = True
        
        # Mock create_entity
        graph_populator.create_entity.return_value = True
        
        # Approve entity
        result = workflow.approve_entity("entity-123", "test-user")
        
        # Verify
        assert result is True
        queue_manager.get_item_by_id.assert_called_with("entity-123")
        graph_populator.create_entity.assert_called_once()
        queue_manager.update_item_status.assert_called_once()
    
    def test_approve_entity_not_found(self, mock_approval_workflow):
        """Test approving entity that doesn't exist."""
        workflow, queue_manager, _ = mock_approval_workflow
        
        # Mock get_item_by_id
        queue_manager.get_item_by_id.return_value = None
        
        # Approve entity
        result = workflow.approve_entity("entity-123", "test-user")
        
        # Verify
        assert result is False
    
    def test_approve_entity_wrong_user(self, mock_approval_workflow, sample_entity_item):
        """Test approving entity with wrong user."""
        workflow, queue_manager, _ = mock_approval_workflow
        
        # Mock get_item_by_id with different user
        wrong_user_item = ReviewItem(
            id="entity-123",
            user_id="other-user",
            type=ReviewItemType.ENTITY,
            status=ReviewItemStatus.PENDING,
            confidence=0.85,
            source_document_id="doc-123",
            entity={'name': 'John Doe', 'type': 'Person'}
        )
        queue_manager.get_item_by_id.return_value = wrong_user_item
        
        # Approve entity should raise error
        with pytest.raises(ValueError, match="does not own item"):
            workflow.approve_entity("entity-123", "test-user")
    
    def test_approve_entity_not_entity_type(self, mock_approval_workflow, sample_relationship_item):
        """Test approving a relationship item as entity."""
        workflow, queue_manager, _ = mock_approval_workflow
        
        # Mock get_item_by_id with relationship item
        queue_manager.get_item_by_id.return_value = sample_relationship_item
        
        # Approve should raise error
        with pytest.raises(ValueError, match="is not an entity"):
            workflow.approve_entity("entity-123", "test-user")
    
    def test_reject_entity_success(self, mock_approval_workflow, sample_entity_item):
        """Test successfully rejecting an entity."""
        workflow, queue_manager, _ = mock_approval_workflow
        
        # Mock get_item_by_id
        queue_manager.get_item_by_id.return_value = sample_entity_item
        
        # Mock update_item_status
        queue_manager.update_item_status.return_value = True
        
        # Mock _log_rejection
        with patch.object(workflow, '_log_rejection'):
            # Reject entity
            result = workflow.reject_entity("entity-123", "test-user", "Low quality")
            
            # Verify
            assert result is True
            queue_manager.update_item_status.assert_called_once()
    
    def test_approve_relationship_success(self, mock_approval_workflow, sample_relationship_item):
        """Test successfully approving a relationship."""
        workflow, queue_manager, graph_populator = mock_approval_workflow
        
        # Mock get_item_by_id
        queue_manager.get_item_by_id.return_value = sample_relationship_item
        
        # Mock update_item_status
        queue_manager.update_item_status.return_value = True
        
        # Mock create_relationship
        graph_populator.create_relationship.return_value = True
        
        # Approve relationship
        result = workflow.approve_relationship("rel-123", "test-user")
        
        # Verify
        assert result is True
        queue_manager.get_item_by_id.assert_called_with("rel-123")
        graph_populator.create_relationship.assert_called_once()
        queue_manager.update_item_status.assert_called_once()
    
    def test_reject_relationship_success(self, mock_approval_workflow, sample_relationship_item):
        """Test successfully rejecting a relationship."""
        workflow, queue_manager, _ = mock_approval_workflow
        
        # Mock get_item_by_id
        queue_manager.get_item_by_id.return_value = sample_relationship_item
        
        # Mock update_item_status
        queue_manager.update_item_status.return_value = True
        
        # Mock _log_rejection
        with patch.object(workflow, '_log_rejection'):
            # Reject relationship
            result = workflow.reject_relationship("rel-123", "test-user", "Low confidence")
            
            # Verify
            assert result is True
            queue_manager.update_item_status.assert_called_once()
    
    def test_create_entity_from_review_item(self, mock_approval_workflow, sample_entity_item):
        """Test creating entity from review item."""
        workflow, _, _ = mock_approval_workflow
        
        entity = workflow._create_entity_from_review_item(sample_entity_item)
        
        assert entity.name == 'John Doe'
        assert entity.type == 'Person'
        assert entity.confidence == 0.85
        assert entity.user_id == 'test-user'
        assert entity.metadata['review_item_id'] == 'entity-123'
    
    def test_create_relationship_from_review_item(self, mock_approval_workflow, sample_relationship_item):
        """Test creating relationship from review item."""
        workflow, _, _ = mock_approval_workflow
        
        relationship = workflow._create_relationship_from_review_item(sample_relationship_item)
        
        assert relationship.source_entity == 'John Doe'
        assert relationship.target_entity == 'Acme Corp'
        assert relationship.relationship_type == 'WORKS_AT'
        assert relationship.confidence == 0.75
        assert relationship.user_id == 'test-user'
        assert relationship.metadata['review_item_id'] == 'rel-123'


class TestBatchProcessor:
    """Test suite for BatchProcessor."""
    
    def test_initialization(self, mock_batch_processor):
        """Test batch processor initialization."""
        processor, _, _ = mock_batch_processor
        assert processor.project_id == "test-project"
        assert processor.max_batch_size == 50
    
    def test_batch_approve_success(self, mock_batch_processor, sample_entity_item, sample_relationship_item):
        """Test successful batch approval."""
        processor, approval_workflow, queue_manager = mock_batch_processor
        
        # Mock get_item_by_id
        queue_manager.get_item_by_id.side_effect = [sample_entity_item, sample_relationship_item]
        
        # Mock approval methods
        approval_workflow.approve_entity.return_value = True
        approval_workflow.approve_relationship.return_value = True
        
        # Mock _is_entity_item
        with patch.object(processor, '_is_entity_item', side_effect=[True, False]):
            # Batch approve
            result = processor.batch_approve(["entity-123", "rel-123"], "test-user")
            
            # Verify
            assert isinstance(result, BatchResult)
            assert result.total_items == 2
            assert len(result.successful) == 2
            assert len(result.failed) == 0
            assert result.operation_type == BatchOperationType.APPROVE
    
    def test_batch_approve_partial_failure(self, mock_batch_processor, sample_entity_item):
        """Test batch approval with partial failures."""
        processor, approval_workflow, queue_manager = mock_batch_processor
        
        # Mock get_item_by_id
        queue_manager.get_item_by_id.return_value = sample_entity_item
        
        # Mock approval methods
        approval_workflow.approve_entity.side_effect = [True, Exception("Failed")]
        
        # Mock _is_entity_item
        with patch.object(processor, '_is_entity_item', return_value=True):
            # Batch approve
            result = processor.batch_approve(["entity-123", "entity-456"], "test-user")
            
            # Verify
            assert result.total_items == 2
            assert len(result.successful) == 1
            assert len(result.failed) == 1
            assert result.get_success_rate() == 50.0
    
    def test_batch_reject_success(self, mock_batch_processor, sample_entity_item):
        """Test successful batch rejection."""
        processor, approval_workflow, queue_manager = mock_batch_processor
        
        # Mock get_item_by_id
        queue_manager.get_item_by_id.return_value = sample_entity_item
        
        # Mock approval methods
        approval_workflow.reject_entity.return_value = True
        
        # Mock _is_entity_item
        with patch.object(processor, '_is_entity_item', return_value=True):
            # Batch reject
            result = processor.batch_reject(["entity-123"], "test-user", "Low quality")
            
            # Verify
            assert result.total_items == 1
            assert len(result.successful) == 1
            assert len(result.failed) == 0
            assert result.operation_type == BatchOperationType.REJECT
    
    def test_batch_process_mixed(self, mock_batch_processor, sample_entity_item, sample_relationship_item):
        """Test mixed batch processing."""
        processor, approval_workflow, queue_manager = mock_batch_processor
        
        # Mock get_item_by_id
        queue_manager.get_item_by_id.side_effect = [sample_entity_item, sample_relationship_item]
        
        # Mock approval methods
        approval_workflow.approve_entity.return_value = True
        approval_workflow.reject_relationship.return_value = True
        
        # Mock _is_entity_item and batch methods
        with patch.object(processor, '_is_entity_item', side_effect=[True, False]), \
             patch.object(processor, 'batch_approve') as mock_approve, \
             patch.object(processor, 'batch_reject') as mock_reject:
            
            mock_approve.return_value = BatchResult(
                total_items=1,
                successful=["entity-123"],
                failed=[],
                operation_type=BatchOperationType.APPROVE,
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
                duration_seconds=0.1
            )
            
            mock_reject.return_value = BatchResult(
                total_items=1,
                successful=["rel-123"],
                failed=[],
                operation_type=BatchOperationType.REJECT,
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
                duration_seconds=0.1
            )
            
            # Create operations
            operations = [
                BatchOperation("entity-123", BatchOperationType.APPROVE),
                BatchOperation("rel-123", BatchOperationType.REJECT, reason="Low confidence")
            ]
            
            # Process mixed batch
            result = processor.batch_process(operations, "test-user")
            
            # Verify
            assert result.total_items == 2
            assert len(result.successful) == 2
            assert len(result.failed) == 0
    
    def test_get_batch_estimate(self, mock_batch_processor):
        """Test batch operation estimates."""
        processor, _, _ = mock_batch_processor
        
        # Get estimate
        estimate = processor.get_batch_estimate(["item1", "item2", "item3"])
        
        # Verify
        assert estimate['total_items'] == 3
        assert estimate['estimated_duration_seconds'] == 0.3  # 3 items * 0.1s each
        assert estimate['max_batch_size'] == 50
        assert len(estimate['recommendations']) == 0
    
    def test_get_batch_estimate_large_batch(self, mock_batch_processor):
        """Test batch estimate for large batch."""
        processor, _, _ = mock_batch_processor
        
        # Get estimate for large batch
        item_ids = [f"item{i}" for i in range(100)]
        estimate = processor.get_batch_estimate(item_ids)
        
        # Verify
        assert estimate['total_items'] == 100
        assert len(estimate['recommendations']) > 0
        assert any("splitting" in rec for rec in estimate['recommendations'])
    
    def test_validate_batch_permissions_success(self, mock_batch_processor, sample_entity_item):
        """Test successful batch permission validation."""
        processor, _, queue_manager = mock_batch_processor
        
        # Mock get_item_by_id
        queue_manager.get_item_by_id.return_value = sample_entity_item
        
        # Validate permissions
        all_valid, unauthorized = processor.validate_batch_permissions(
            ["entity-123"], "test-user"
        )
        
        # Verify
        assert all_valid is True
        assert len(unauthorized) == 0
    
    def test_validate_batch_permissions_failure(self, mock_batch_processor):
        """Test batch permission validation with unauthorized items."""
        processor, _, queue_manager = mock_batch_processor
        
        # Create item with different user
        wrong_user_item = ReviewItem(
            id="entity-456",
            user_id="other-user",
            type=ReviewItemType.ENTITY,
            status=ReviewItemStatus.PENDING,
            confidence=0.85,
            source_document_id="doc-123",
            entity={'name': 'Jane Doe', 'type': 'Person'}
        )
        
        # Mock get_item_by_id
        queue_manager.get_item_by_id.return_value = wrong_user_item
        
        # Validate permissions
        all_valid, unauthorized = processor.validate_batch_permissions(
            ["entity-456"], "test-user"
        )
        
        # Verify
        assert all_valid is False
        assert len(unauthorized) == 1
        assert "entity-456" in unauthorized


class TestBatchOperation:
    """Test suite for BatchOperation."""
    
    def test_creation(self):
        """Test creating batch operation."""
        op = BatchOperation("item-123", BatchOperationType.APPROVE)
        
        assert op.item_id == "item-123"
        assert op.operation_type == BatchOperationType.APPROVE
        assert op.reason is None
    
    def test_creation_with_reason(self):
        """Test creating batch operation with reason."""
        op = BatchOperation("item-123", BatchOperationType.REJECT, "Low quality")
        
        assert op.item_id == "item-123"
        assert op.operation_type == BatchOperationType.REJECT
        assert op.reason == "Low quality"


class TestBatchResult:
    """Test suite for BatchResult."""
    
    def test_creation(self):
        """Test creating batch result."""
        started_at = datetime.utcnow()
        completed_at = datetime.utcnow()
        
        result = BatchResult(
            total_items=10,
            successful=["item1", "item2"],
            failed=[{"item_id": "item3", "error": "Failed"}],
            operation_type=BatchOperationType.APPROVE,
            started_at=started_at,
            completed_at=completed_at,
            duration_seconds=1.5
        )
        
        assert result.total_items == 10
        assert len(result.successful) == 2
        assert len(result.failed) == 1
        assert result.get_success_rate() == 20.0
    
    def test_get_success_rate(self):
        """Test success rate calculation."""
        result = BatchResult(
            total_items=0,
            successful=[],
            failed=[],
            operation_type=BatchOperationType.APPROVE,
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            duration_seconds=0.0
        )
        
        assert result.get_success_rate() == 0.0
    
    def test_to_dict(self):
        """Test converting to dictionary."""
        result = BatchResult(
            total_items=2,
            successful=["item1"],
            failed=[{"item_id": "item2", "error": "Failed"}],
            operation_type=BatchOperationType.APPROVE,
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            duration_seconds=0.5
        )
        
        data = result.to_dict()
        
        assert data['total_items'] == 2
        assert data['successful_count'] == 1
        assert data['failed_count'] == 1
        assert data['success_rate'] == 50.0
        assert isinstance(data['started_at'], str)


def test_create_approval_workflow():
    """Test factory function."""
    with patch('shared.review.approval_workflow.create_queue_manager'), \
         patch('shared.review.approval_workflow.create_graph_populator'):
        workflow = create_approval_workflow("test-project")
        assert isinstance(workflow, ApprovalWorkflow)
        assert workflow.project_id == "test-project"


def test_create_batch_processor():
    """Test factory function."""
    with patch('shared.review.batch_processor.create_approval_workflow'), \
         patch('shared.review.batch_processor.create_queue_manager'):
        processor = create_batch_processor("test-project")
        assert isinstance(processor, BatchProcessor)
        assert processor.project_id == "test-project"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])