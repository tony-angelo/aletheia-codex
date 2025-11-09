"""
Tests for the review queue manager.
"""

import pytest
import os
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

# Set environment variable before importing
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/workspace/aletheia-codex-prod-af9a64a7fcaa.json'

from shared.review.queue_manager import QueueManager, create_queue_manager
from shared.models.review_item import ReviewItem, ReviewItemType, ReviewItemStatus, UserStats


@pytest.fixture
def mock_firestore():
    """Mock Firestore client."""
    with patch('shared.review.queue_manager.get_firestore_client') as mock:
        db = MagicMock()
        mock.return_value = db
        yield db


@pytest.fixture
def queue_manager(mock_firestore):
    """Create queue manager with mocked Firestore."""
    return QueueManager(project_id="test-project")


@pytest.fixture
def sample_entity_item():
    """Create a sample entity review item."""
    return ReviewItem(
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


class TestQueueManager:
    """Test suite for QueueManager."""
    
    def test_initialization(self, queue_manager):
        """Test queue manager initialization."""
        assert queue_manager.project_id == "test-project"
        assert queue_manager.review_queue_collection == "review_queue"
        assert queue_manager.user_stats_collection == "user_stats"
    
    def test_add_to_queue_success(self, queue_manager, mock_firestore, sample_entity_item):
        """Test successfully adding items to queue."""
        # Mock batch operations
        mock_batch = MagicMock()
        mock_firestore.batch.return_value = mock_batch
        
        # Mock document reference
        mock_doc_ref = MagicMock()
        mock_doc_ref.id = "item-123"
        mock_firestore.collection.return_value.document.return_value = mock_doc_ref
        
        # Add items
        items = [sample_entity_item]
        result = queue_manager.add_to_queue("test-user", items, "doc-123")
        
        # Verify
        assert len(result) == 1
        assert result[0] == "item-123"
        mock_batch.commit.assert_called_once()
    
    def test_add_to_queue_empty_list(self, queue_manager):
        """Test adding empty list raises error."""
        with pytest.raises(ValueError, match="Items list cannot be empty"):
            queue_manager.add_to_queue("test-user", [], "doc-123")
    
    def test_add_to_queue_empty_user_id(self, queue_manager, sample_entity_item):
        """Test adding with empty user_id raises error."""
        with pytest.raises(ValueError, match="User ID cannot be empty"):
            queue_manager.add_to_queue("", [sample_entity_item], "doc-123")
    
    def test_get_pending_items_success(self, queue_manager, mock_firestore):
        """Test successfully retrieving pending items."""
        # Mock query chain
        mock_query = MagicMock()
        mock_firestore.collection.return_value = mock_query
        mock_query.where.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        
        # Mock document
        mock_doc = MagicMock()
        mock_doc.id = "item-123"
        mock_doc.to_dict.return_value = {
            'user_id': 'test-user',
            'type': 'entity',
            'status': 'pending',
            'confidence': 0.85,
            'source_document_id': 'doc-123',
            'entity': {'name': 'John Doe', 'type': 'Person'},
            'created_at': datetime.utcnow().isoformat()
        }
        mock_query.stream.return_value = [mock_doc]
        
        # Get items
        items = queue_manager.get_pending_items("test-user")
        
        # Verify
        assert len(items) == 1
        assert items[0].id == "item-123"
        assert items[0].user_id == "test-user"
    
    def test_get_pending_items_empty_user_id(self, queue_manager):
        """Test getting items with empty user_id raises error."""
        with pytest.raises(ValueError, match="User ID cannot be empty"):
            queue_manager.get_pending_items("")
    
    def test_get_item_by_id_found(self, queue_manager, mock_firestore):
        """Test getting item by ID when it exists."""
        # Mock document
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_doc.id = "item-123"
        mock_doc.to_dict.return_value = {
            'user_id': 'test-user',
            'type': 'entity',
            'status': 'pending',
            'confidence': 0.85,
            'source_document_id': 'doc-123',
            'entity': {'name': 'John Doe', 'type': 'Person'},
            'created_at': datetime.utcnow().isoformat()
        }
        
        mock_firestore.collection.return_value.document.return_value.get.return_value = mock_doc
        
        # Get item
        item = queue_manager.get_item_by_id("item-123")
        
        # Verify
        assert item is not None
        assert item.id == "item-123"
        assert item.user_id == "test-user"
    
    def test_get_item_by_id_not_found(self, queue_manager, mock_firestore):
        """Test getting item by ID when it doesn't exist."""
        # Mock document
        mock_doc = MagicMock()
        mock_doc.exists = False
        
        mock_firestore.collection.return_value.document.return_value.get.return_value = mock_doc
        
        # Get item
        item = queue_manager.get_item_by_id("item-123")
        
        # Verify
        assert item is None
    
    def test_update_item_status_success(self, queue_manager, mock_firestore):
        """Test successfully updating item status."""
        # Mock get_item_by_id
        mock_item = MagicMock()
        mock_item.user_id = "test-user"
        mock_item.confidence = 0.85
        
        with patch.object(queue_manager, 'get_item_by_id', return_value=mock_item):
            # Mock document update
            mock_doc_ref = MagicMock()
            mock_firestore.collection.return_value.document.return_value = mock_doc_ref
            
            # Update status
            result = queue_manager.update_item_status(
                "item-123",
                ReviewItemStatus.APPROVED,
                "test-user"
            )
            
            # Verify
            assert result is True
            mock_doc_ref.update.assert_called_once()
    
    def test_update_item_status_wrong_user(self, queue_manager):
        """Test updating item status with wrong user raises error."""
        # Mock get_item_by_id
        mock_item = MagicMock()
        mock_item.user_id = "other-user"
        
        with patch.object(queue_manager, 'get_item_by_id', return_value=mock_item):
            with pytest.raises(ValueError, match="does not own item"):
                queue_manager.update_item_status(
                    "item-123",
                    ReviewItemStatus.APPROVED,
                    "test-user"
                )
    
    def test_delete_item_success(self, queue_manager, mock_firestore):
        """Test successfully deleting an item."""
        # Mock get_item_by_id
        mock_item = MagicMock()
        mock_item.user_id = "test-user"
        mock_item.is_pending.return_value = True
        
        with patch.object(queue_manager, 'get_item_by_id', return_value=mock_item):
            # Mock document delete
            mock_doc_ref = MagicMock()
            mock_firestore.collection.return_value.document.return_value = mock_doc_ref
            
            # Delete item
            result = queue_manager.delete_item("item-123", "test-user")
            
            # Verify
            assert result is True
            mock_doc_ref.delete.assert_called_once()
    
    def test_delete_item_wrong_user(self, queue_manager):
        """Test deleting item with wrong user raises error."""
        # Mock get_item_by_id
        mock_item = MagicMock()
        mock_item.user_id = "other-user"
        
        with patch.object(queue_manager, 'get_item_by_id', return_value=mock_item):
            with pytest.raises(ValueError, match="does not own item"):
                queue_manager.delete_item("item-123", "test-user")
    
    def test_get_user_stats_existing(self, queue_manager, mock_firestore):
        """Test getting existing user stats."""
        # Mock document
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {
            'user_id': 'test-user',
            'total_pending': 5,
            'total_approved': 10,
            'total_rejected': 2,
            'average_confidence': 0.82
        }
        
        mock_firestore.collection.return_value.document.return_value.get.return_value = mock_doc
        
        # Get stats
        stats = queue_manager.get_user_stats("test-user")
        
        # Verify
        assert stats.user_id == "test-user"
        assert stats.total_pending == 5
        assert stats.total_approved == 10
        assert stats.total_rejected == 2
    
    def test_get_user_stats_new_user(self, queue_manager, mock_firestore):
        """Test getting stats for new user creates default stats."""
        # Mock document
        mock_doc = MagicMock()
        mock_doc.exists = False
        
        mock_doc_ref = MagicMock()
        mock_firestore.collection.return_value.document.return_value = mock_doc_ref
        mock_doc_ref.get.return_value = mock_doc
        
        # Get stats
        stats = queue_manager.get_user_stats("test-user")
        
        # Verify
        assert stats.user_id == "test-user"
        assert stats.total_pending == 0
        assert stats.total_approved == 0
        assert stats.total_rejected == 0
        mock_doc_ref.set.assert_called_once()


class TestReviewItem:
    """Test suite for ReviewItem model."""
    
    def test_entity_item_creation(self, sample_entity_item):
        """Test creating an entity review item."""
        assert sample_entity_item.type == ReviewItemType.ENTITY
        assert sample_entity_item.status == ReviewItemStatus.PENDING
        assert sample_entity_item.confidence == 0.85
        assert sample_entity_item.entity['name'] == 'John Doe'
    
    def test_relationship_item_creation(self, sample_relationship_item):
        """Test creating a relationship review item."""
        assert sample_relationship_item.type == ReviewItemType.RELATIONSHIP
        assert sample_relationship_item.status == ReviewItemStatus.PENDING
        assert sample_relationship_item.confidence == 0.75
        assert sample_relationship_item.relationship['source_entity'] == 'John Doe'
    
    def test_invalid_confidence(self):
        """Test creating item with invalid confidence raises error."""
        with pytest.raises(ValueError, match="Confidence must be between"):
            ReviewItem(
                user_id="test-user",
                type=ReviewItemType.ENTITY,
                status=ReviewItemStatus.PENDING,
                confidence=1.5,
                source_document_id="doc-123",
                entity={'name': 'Test', 'type': 'Person'}
            )
    
    def test_empty_user_id(self):
        """Test creating item with empty user_id raises error."""
        with pytest.raises(ValueError, match="User ID cannot be empty"):
            ReviewItem(
                user_id="",
                type=ReviewItemType.ENTITY,
                status=ReviewItemStatus.PENDING,
                confidence=0.8,
                source_document_id="doc-123",
                entity={'name': 'Test', 'type': 'Person'}
            )
    
    def test_entity_without_data(self):
        """Test creating entity item without entity data raises error."""
        with pytest.raises(ValueError, match="Entity data is required"):
            ReviewItem(
                user_id="test-user",
                type=ReviewItemType.ENTITY,
                status=ReviewItemStatus.PENDING,
                confidence=0.8,
                source_document_id="doc-123"
            )
    
    def test_relationship_without_data(self):
        """Test creating relationship item without relationship data raises error."""
        with pytest.raises(ValueError, match="Relationship data is required"):
            ReviewItem(
                user_id="test-user",
                type=ReviewItemType.RELATIONSHIP,
                status=ReviewItemStatus.PENDING,
                confidence=0.8,
                source_document_id="doc-123"
            )
    
    def test_to_dict(self, sample_entity_item):
        """Test converting item to dictionary."""
        data = sample_entity_item.to_dict()
        
        assert data['user_id'] == 'test-user'
        assert data['type'] == 'entity'
        assert data['status'] == 'pending'
        assert data['confidence'] == 0.85
        assert data['entity']['name'] == 'John Doe'
    
    def test_from_dict(self):
        """Test creating item from dictionary."""
        data = {
            'id': 'item-123',
            'user_id': 'test-user',
            'type': 'entity',
            'status': 'pending',
            'confidence': 0.85,
            'source_document_id': 'doc-123',
            'entity': {'name': 'John Doe', 'type': 'Person'},
            'created_at': datetime.utcnow().isoformat()
        }
        
        item = ReviewItem.from_dict(data)
        
        assert item.id == 'item-123'
        assert item.user_id == 'test-user'
        assert item.type == ReviewItemType.ENTITY
        assert item.entity['name'] == 'John Doe'
    
    def test_get_display_name_entity(self, sample_entity_item):
        """Test getting display name for entity."""
        assert sample_entity_item.get_display_name() == 'John Doe'
    
    def test_get_display_name_relationship(self, sample_relationship_item):
        """Test getting display name for relationship."""
        expected = 'John Doe → WORKS_AT → Acme Corp'
        assert sample_relationship_item.get_display_name() == expected
    
    def test_get_confidence_level(self, sample_entity_item):
        """Test getting confidence level."""
        assert sample_entity_item.get_confidence_level() == 'high'
        
        sample_entity_item.confidence = 0.6
        assert sample_entity_item.get_confidence_level() == 'medium'
        
        sample_entity_item.confidence = 0.4
        assert sample_entity_item.get_confidence_level() == 'low'


class TestUserStats:
    """Test suite for UserStats model."""
    
    def test_creation(self):
        """Test creating user stats."""
        stats = UserStats(user_id="test-user")
        
        assert stats.user_id == "test-user"
        assert stats.total_pending == 0
        assert stats.total_approved == 0
        assert stats.total_rejected == 0
    
    def test_get_total_reviewed(self):
        """Test getting total reviewed count."""
        stats = UserStats(
            user_id="test-user",
            total_approved=10,
            total_rejected=2
        )
        
        assert stats.get_total_reviewed() == 12
    
    def test_get_approval_rate(self):
        """Test getting approval rate."""
        stats = UserStats(
            user_id="test-user",
            total_approved=8,
            total_rejected=2
        )
        
        assert stats.get_approval_rate() == 0.8
    
    def test_get_approval_rate_no_reviews(self):
        """Test getting approval rate with no reviews."""
        stats = UserStats(user_id="test-user")
        
        assert stats.get_approval_rate() == 0.0
    
    def test_to_dict(self):
        """Test converting stats to dictionary."""
        stats = UserStats(
            user_id="test-user",
            total_pending=5,
            total_approved=10
        )
        
        data = stats.to_dict()
        
        assert data['user_id'] == 'test-user'
        assert data['total_pending'] == 5
        assert data['total_approved'] == 10
    
    def test_from_dict(self):
        """Test creating stats from dictionary."""
        data = {
            'user_id': 'test-user',
            'total_pending': 5,
            'total_approved': 10,
            'total_rejected': 2,
            'average_confidence': 0.82
        }
        
        stats = UserStats.from_dict(data)
        
        assert stats.user_id == 'test-user'
        assert stats.total_pending == 5
        assert stats.total_approved == 10


def test_create_queue_manager():
    """Test factory function."""
    with patch('shared.review.queue_manager.get_firestore_client'):
        manager = create_queue_manager("test-project")
        assert isinstance(manager, QueueManager)
        assert manager.project_id == "test-project"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])