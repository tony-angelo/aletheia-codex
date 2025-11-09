"""
Review queue manager for AletheiaCodex.

Manages the review queue in Firestore, including adding items, retrieving pending items,
updating status, and managing user statistics.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from google.cloud import firestore
from google.cloud.firestore_v1 import FieldFilter

from ..models.review_item import ReviewItem, ReviewItemType, ReviewItemStatus, UserStats
from ..db.firestore_client import get_firestore_client

logger = logging.getLogger(__name__)


class QueueManager:
    """
    Manages the review queue in Firestore.
    
    Handles all operations related to the review queue including:
    - Adding items to the queue
    - Retrieving pending items
    - Updating item status
    - Managing user statistics
    """
    
    def __init__(self, project_id: str = "aletheia-codex-prod"):
        """
        Initialize queue manager.
        
        Args:
            project_id: GCP project ID
        """
        self.project_id = project_id
        self.db = get_firestore_client(project_id)
        self.review_queue_collection = "review_queue"
        self.user_stats_collection = "user_stats"
        
        logger.info(f"Initialized QueueManager for project: {project_id}")
    
    def add_to_queue(
        self,
        user_id: str,
        items: List[ReviewItem],
        source_doc_id: str
    ) -> List[str]:
        """
        Add items to the review queue.
        
        Args:
            user_id: User ID
            items: List of review items to add
            source_doc_id: Source document ID
            
        Returns:
            List of created item IDs
            
        Raises:
            ValueError: If items list is empty or invalid
            Exception: If Firestore operation fails
        """
        if not items:
            raise ValueError("Items list cannot be empty")
        
        if not user_id or not user_id.strip():
            raise ValueError("User ID cannot be empty")
        
        try:
            created_ids = []
            batch = self.db.batch()
            
            for item in items:
                # Validate item
                if item.user_id != user_id:
                    logger.warning(f"Item user_id {item.user_id} doesn't match provided user_id {user_id}")
                    item.user_id = user_id
                
                if item.source_document_id != source_doc_id:
                    logger.warning(f"Item source_document_id doesn't match provided source_doc_id")
                    item.source_document_id = source_doc_id
                
                # Create document reference
                doc_ref = self.db.collection(self.review_queue_collection).document()
                item.id = doc_ref.id
                
                # Add to batch
                batch.set(doc_ref, item.to_dict())
                created_ids.append(doc_ref.id)
            
            # Commit batch
            batch.commit()
            
            # Update user stats
            self._update_user_stats_pending(user_id, len(items))
            
            logger.info(f"Added {len(items)} items to review queue for user {user_id}")
            return created_ids
            
        except Exception as e:
            logger.error(f"Failed to add items to queue: {str(e)}")
            raise
    
    def get_pending_items(
        self,
        user_id: str,
        limit: int = 50,
        min_confidence: float = 0.0,
        item_type: Optional[ReviewItemType] = None,
        order_by: str = "confidence",
        descending: bool = True
    ) -> List[ReviewItem]:
        """
        Get pending review items for a user.
        
        Args:
            user_id: User ID
            limit: Maximum number of items to return (default: 50)
            min_confidence: Minimum confidence threshold (default: 0.0)
            item_type: Filter by item type (optional)
            order_by: Field to order by (default: "confidence")
            descending: Order descending (default: True)
            
        Returns:
            List of pending review items
            
        Raises:
            ValueError: If user_id is empty
            Exception: If Firestore query fails
        """
        if not user_id or not user_id.strip():
            raise ValueError("User ID cannot be empty")
        
        try:
            # Build query
            query = self.db.collection(self.review_queue_collection)
            query = query.where(filter=FieldFilter("user_id", "==", user_id))
            query = query.where(filter=FieldFilter("status", "==", ReviewItemStatus.PENDING.value))
            
            if min_confidence > 0.0:
                query = query.where(filter=FieldFilter("confidence", ">=", min_confidence))
            
            if item_type:
                type_value = item_type.value if isinstance(item_type, ReviewItemType) else item_type
                query = query.where(filter=FieldFilter("type", "==", type_value))
            
            # Order and limit
            direction = firestore.Query.DESCENDING if descending else firestore.Query.ASCENDING
            query = query.order_by(order_by, direction=direction)
            query = query.limit(limit)
            
            # Execute query
            docs = query.stream()
            
            # Convert to ReviewItem objects
            items = []
            for doc in docs:
                try:
                    data = doc.to_dict()
                    data['id'] = doc.id
                    item = ReviewItem.from_dict(data)
                    items.append(item)
                except Exception as e:
                    logger.error(f"Failed to parse review item {doc.id}: {str(e)}")
                    continue
            
            logger.info(f"Retrieved {len(items)} pending items for user {user_id}")
            return items
            
        except Exception as e:
            logger.error(f"Failed to get pending items: {str(e)}")
            raise
    
    def get_item_by_id(self, item_id: str) -> Optional[ReviewItem]:
        """
        Get a review item by ID.
        
        Args:
            item_id: Review item ID
            
        Returns:
            ReviewItem if found, None otherwise
            
        Raises:
            Exception: If Firestore operation fails
        """
        try:
            doc_ref = self.db.collection(self.review_queue_collection).document(item_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                logger.warning(f"Review item not found: {item_id}")
                return None
            
            data = doc.to_dict()
            data['id'] = doc.id
            item = ReviewItem.from_dict(data)
            
            logger.info(f"Retrieved review item: {item_id}")
            return item
            
        except Exception as e:
            logger.error(f"Failed to get review item {item_id}: {str(e)}")
            raise
    
    def update_item_status(
        self,
        item_id: str,
        status: ReviewItemStatus,
        user_id: str,
        rejection_reason: Optional[str] = None
    ) -> bool:
        """
        Update the status of a review item.
        
        Args:
            item_id: Review item ID
            status: New status
            user_id: User ID (for verification)
            rejection_reason: Reason for rejection (if status is rejected)
            
        Returns:
            True if update successful, False otherwise
            
        Raises:
            ValueError: If user doesn't own the item
            Exception: If Firestore operation fails
        """
        try:
            # Get item to verify ownership
            item = self.get_item_by_id(item_id)
            if not item:
                logger.error(f"Item not found: {item_id}")
                return False
            
            if item.user_id != user_id:
                raise ValueError(f"User {user_id} does not own item {item_id}")
            
            # Prepare update data
            update_data = {
                'status': status.value if isinstance(status, ReviewItemStatus) else status,
                'reviewed_at': datetime.utcnow().isoformat()
            }
            
            if rejection_reason:
                update_data['rejection_reason'] = rejection_reason
            
            # Update item
            doc_ref = self.db.collection(self.review_queue_collection).document(item_id)
            doc_ref.update(update_data)
            
            # Update user stats
            self._update_user_stats_on_review(user_id, status, item.confidence)
            
            logger.info(f"Updated item {item_id} status to {status}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update item status: {str(e)}")
            raise
    
    def delete_item(self, item_id: str, user_id: str) -> bool:
        """
        Delete a review item.
        
        Args:
            item_id: Review item ID
            user_id: User ID (for verification)
            
        Returns:
            True if deletion successful, False otherwise
            
        Raises:
            ValueError: If user doesn't own the item
            Exception: If Firestore operation fails
        """
        try:
            # Get item to verify ownership
            item = self.get_item_by_id(item_id)
            if not item:
                logger.error(f"Item not found: {item_id}")
                return False
            
            if item.user_id != user_id:
                raise ValueError(f"User {user_id} does not own item {item_id}")
            
            # Delete item
            doc_ref = self.db.collection(self.review_queue_collection).document(item_id)
            doc_ref.delete()
            
            # Update user stats if item was pending
            if item.is_pending():
                self._update_user_stats_pending(user_id, -1)
            
            logger.info(f"Deleted review item: {item_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete item: {str(e)}")
            raise
    
    def get_user_stats(self, user_id: str) -> UserStats:
        """
        Get user review statistics.
        
        Args:
            user_id: User ID
            
        Returns:
            UserStats object
            
        Raises:
            Exception: If Firestore operation fails
        """
        try:
            doc_ref = self.db.collection(self.user_stats_collection).document(user_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                # Create default stats
                stats = UserStats(user_id=user_id)
                doc_ref.set(stats.to_dict())
                logger.info(f"Created default stats for user {user_id}")
                return stats
            
            data = doc.to_dict()
            stats = UserStats.from_dict(data)
            
            logger.info(f"Retrieved stats for user {user_id}")
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get user stats: {str(e)}")
            raise
    
    def _update_user_stats_pending(self, user_id: str, delta: int):
        """
        Update pending count in user stats.
        
        Args:
            user_id: User ID
            delta: Change in pending count (positive or negative)
        """
        try:
            doc_ref = self.db.collection(self.user_stats_collection).document(user_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                # Create new stats
                stats = UserStats(user_id=user_id, total_pending=max(0, delta))
                doc_ref.set(stats.to_dict())
            else:
                # Update existing stats
                doc_ref.update({
                    'total_pending': firestore.Increment(delta)
                })
            
            logger.debug(f"Updated pending count for user {user_id}: {delta:+d}")
            
        except Exception as e:
            logger.error(f"Failed to update user stats pending: {str(e)}")
            # Don't raise - stats update failure shouldn't break main flow
    
    def _update_user_stats_on_review(
        self,
        user_id: str,
        status: ReviewItemStatus,
        confidence: float
    ):
        """
        Update user stats when an item is reviewed.
        
        Args:
            user_id: User ID
            status: Review status
            confidence: Item confidence score
        """
        try:
            doc_ref = self.db.collection(self.user_stats_collection).document(user_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                # Create new stats
                stats = UserStats(
                    user_id=user_id,
                    total_pending=0,
                    total_approved=1 if status == ReviewItemStatus.APPROVED else 0,
                    total_rejected=1 if status == ReviewItemStatus.REJECTED else 0,
                    last_review_at=datetime.utcnow(),
                    average_confidence=confidence
                )
                doc_ref.set(stats.to_dict())
            else:
                # Update existing stats
                data = doc.to_dict()
                stats = UserStats.from_dict(data)
                
                # Update counts
                stats.total_pending = max(0, stats.total_pending - 1)
                if status == ReviewItemStatus.APPROVED:
                    stats.total_approved += 1
                elif status == ReviewItemStatus.REJECTED:
                    stats.total_rejected += 1
                
                # Update average confidence
                total_reviewed = stats.get_total_reviewed()
                if total_reviewed > 0:
                    # Recalculate average
                    old_sum = stats.average_confidence * (total_reviewed - 1)
                    stats.average_confidence = (old_sum + confidence) / total_reviewed
                else:
                    stats.average_confidence = confidence
                
                stats.last_review_at = datetime.utcnow()
                
                doc_ref.set(stats.to_dict())
            
            logger.debug(f"Updated review stats for user {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to update user stats on review: {str(e)}")
            # Don't raise - stats update failure shouldn't break main flow


def create_queue_manager(project_id: str = "aletheia-codex-prod") -> QueueManager:
    """
    Factory function to create a QueueManager instance.
    
    Args:
        project_id: GCP project ID
        
    Returns:
        QueueManager instance
    """
    return QueueManager(project_id=project_id)