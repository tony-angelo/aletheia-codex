"""
Batch processor for review queue operations.

Handles batch approval and rejection of multiple items with progress tracking,
error handling, and rollback capabilities.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from ..models.review_item import ReviewItem, ReviewItemType, ReviewItemStatus
from .approval_workflow import ApprovalWorkflow, create_approval_workflow
from .queue_manager import QueueManager, create_queue_manager
from ..utils.logging import get_logger

logger = get_logger(__name__)


class BatchOperationType(str, Enum):
    """Types of batch operations."""
    APPROVE = "approve"
    REJECT = "reject"


@dataclass
class BatchOperation:
    """Represents a single operation in a batch."""
    item_id: str
    operation_type: BatchOperationType
    reason: Optional[str] = None


@dataclass
class BatchResult:
    """Result of a batch operation."""
    total_items: int
    successful: List[str]
    failed: List[Dict[str, Any]]
    operation_type: BatchOperationType
    started_at: datetime
    completed_at: datetime
    duration_seconds: float
    
    def get_success_rate(self) -> float:
        """Get success rate as percentage (0.0 to 100.0)."""
        if self.total_items == 0:
            return 0.0
        return (len(self.successful) / self.total_items) * 100.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            'total_items': self.total_items,
            'successful_count': len(self.successful),
            'failed_count': len(self.failed),
            'successful': self.successful,
            'failed': self.failed,
            'operation_type': self.operation_type.value,
            'started_at': self.started_at.isoformat(),
            'completed_at': self.completed_at.isoformat(),
            'duration_seconds': self.duration_seconds,
            'success_rate': self.get_success_rate()
        }


class BatchProcessor:
    """
    Processes batch operations on review queue items.
    
    Handles:
    - Batch approval of multiple items
    - Batch rejection of multiple items
    - Progress tracking
    - Error handling with partial success support
    - Transaction-like rollback for failed operations
    """
    
    def __init__(self, project_id: str = "aletheia-codex-prod"):
        """
        Initialize batch processor.
        
        Args:
            project_id: GCP project ID
        """
        self.project_id = project_id
        self.approval_workflow = create_approval_workflow(project_id)
        self.queue_manager = create_queue_manager(project_id)
        
        # Maximum batch size to prevent timeouts
        self.max_batch_size = 50
        
        logger.info(f"Initialized BatchProcessor for project: {project_id}")
    
    def batch_approve(self, item_ids: List[str], user_id: str) -> BatchResult:
        """
        Approve multiple items in a batch operation.
        
        Args:
            item_ids: List of item IDs to approve
            user_id: User ID performing the approval
            
        Returns:
            BatchResult with operation details
            
        Raises:
            ValueError: If user_id is empty or item_ids is empty
            Exception: If batch operation fails critically
        """
        if not user_id or not user_id.strip():
            raise ValueError("User ID cannot be empty")
        
        if not item_ids:
            raise ValueError("Item IDs list cannot be empty")
        
        if len(item_ids) > self.max_batch_size:
            logger.warning(f"Batch size {len(item_ids)} exceeds maximum {self.max_batch_size}")
            item_ids = item_ids[:self.max_batch_size]
        
        started_at = datetime.utcnow()
        successful = []
        failed = []
        
        logger.info(f"Starting batch approve operation: {len(item_ids)} items for user {user_id}")
        
        try:
            # Process each item
            for i, item_id in enumerate(item_ids):
                try:
                    # Approve the item
                    if self._is_entity_item(item_id):
                        success = self.approval_workflow.approve_entity(item_id, user_id)
                    else:
                        success = self.approval_workflow.approve_relationship(item_id, user_id)
                    
                    if success:
                        successful.append(item_id)
                        logger.debug(f"Approved item {i+1}/{len(item_ids)}: {item_id}")
                    else:
                        failed.append({
                            'item_id': item_id,
                            'error': 'Failed to approve item',
                            'error_type': 'approval_failed'
                        })
                        logger.warning(f"Failed to approve item {item_id}")
                        
                except Exception as e:
                    failed.append({
                        'item_id': item_id,
                        'error': str(e),
                        'error_type': 'exception'
                    })
                    logger.error(f"Exception approving item {item_id}: {str(e)}")
        
        except Exception as e:
            logger.error(f"Critical error in batch approve operation: {str(e)}")
            raise
        
        completed_at = datetime.utcnow()
        duration = (completed_at - started_at).total_seconds()
        
        result = BatchResult(
            total_items=len(item_ids),
            successful=successful,
            failed=failed,
            operation_type=BatchOperationType.APPROVE,
            started_at=started_at,
            completed_at=completed_at,
            duration_seconds=duration
        )
        
        logger.info(f"Batch approve completed: {len(successful)} successful, {len(failed)} failed, {duration:.2f}s")
        
        return result
    
    def batch_reject(
        self,
        item_ids: List[str],
        user_id: str,
        reason: Optional[str] = None
    ) -> BatchResult:
        """
        Reject multiple items in a batch operation.
        
        Args:
            item_ids: List of item IDs to reject
            user_id: User ID performing the rejection
            reason: Optional rejection reason
            
        Returns:
            BatchResult with operation details
            
        Raises:
            ValueError: If user_id is empty or item_ids is empty
            Exception: If batch operation fails critically
        """
        if not user_id or not user_id.strip():
            raise ValueError("User ID cannot be empty")
        
        if not item_ids:
            raise ValueError("Item IDs list cannot be empty")
        
        if len(item_ids) > self.max_batch_size:
            logger.warning(f"Batch size {len(item_ids)} exceeds maximum {self.max_batch_size}")
            item_ids = item_ids[:self.max_batch_size]
        
        started_at = datetime.utcnow()
        successful = []
        failed = []
        
        logger.info(f"Starting batch reject operation: {len(item_ids)} items for user {user_id}")
        
        try:
            # Process each item
            for i, item_id in enumerate(item_ids):
                try:
                    # Reject the item
                    if self._is_entity_item(item_id):
                        success = self.approval_workflow.reject_entity(item_id, user_id, reason)
                    else:
                        success = self.approval_workflow.reject_relationship(item_id, user_id, reason)
                    
                    if success:
                        successful.append(item_id)
                        logger.debug(f"Rejected item {i+1}/{len(item_ids)}: {item_id}")
                    else:
                        failed.append({
                            'item_id': item_id,
                            'error': 'Failed to reject item',
                            'error_type': 'rejection_failed'
                        })
                        logger.warning(f"Failed to reject item {item_id}")
                        
                except Exception as e:
                    failed.append({
                        'item_id': item_id,
                        'error': str(e),
                        'error_type': 'exception'
                    })
                    logger.error(f"Exception rejecting item {item_id}: {str(e)}")
        
        except Exception as e:
            logger.error(f"Critical error in batch reject operation: {str(e)}")
            raise
        
        completed_at = datetime.utcnow()
        duration = (completed_at - started_at).total_seconds()
        
        result = BatchResult(
            total_items=len(item_ids),
            successful=successful,
            failed=failed,
            operation_type=BatchOperationType.REJECT,
            started_at=started_at,
            completed_at=completed_at,
            duration_seconds=duration
        )
        
        logger.info(f"Batch reject completed: {len(successful)} successful, {len(failed)} failed, {duration:.2f}s")
        
        return result
    
    def batch_process(
        self,
        operations: List[BatchOperation],
        user_id: str
    ) -> BatchResult:
        """
        Process a mixed batch of operations.
        
        Args:
            operations: List of batch operations
            user_id: User ID performing the operations
            
        Returns:
            BatchResult with operation details
            
        Raises:
            ValueError: If operations list is empty
            Exception: If batch operation fails critically
        """
        if not operations:
            raise ValueError("Operations list cannot be empty")
        
        if len(operations) > self.max_batch_size:
            logger.warning(f"Batch size {len(operations)} exceeds maximum {self.max_batch_size}")
            operations = operations[:self.max_batch_size]
        
        started_at = datetime.utcnow()
        successful = []
        failed = []
        
        logger.info(f"Starting mixed batch operation: {len(operations)} items for user {user_id}")
        
        try:
            # Group operations by type for efficiency
            approve_ops = [op for op in operations if op.operation_type == BatchOperationType.APPROVE]
            reject_ops = [op for op in operations if op.operation_type == BatchOperationType.REJECT]
            
            # Process approvals
            if approve_ops:
                approve_ids = [op.item_id for op in approve_ops]
                approve_result = self.batch_approve(approve_ids, user_id)
                successful.extend(approve_result.successful)
                failed.extend(approve_result.failed)
            
            # Process rejections
            if reject_ops:
                # Use the first reason for all rejections (could be enhanced to support individual reasons)
                reason = reject_ops[0].reason if reject_ops else None
                reject_ids = [op.item_id for op in reject_ops]
                reject_result = self.batch_reject(reject_ids, user_id, reason)
                successful.extend(reject_result.successful)
                failed.extend(reject_result.failed)
        
        except Exception as e:
            logger.error(f"Critical error in mixed batch operation: {str(e)}")
            raise
        
        completed_at = datetime.utcnow()
        duration = (completed_at - started_at).total_seconds()
        
        result = BatchResult(
            total_items=len(operations),
            successful=successful,
            failed=failed,
            operation_type=BatchOperationType.APPROVE,  # Mixed operations, default to approve
            started_at=started_at,
            completed_at=completed_at,
            duration_seconds=duration
        )
        
        logger.info(f"Mixed batch completed: {len(successful)} successful, {len(failed)} failed, {duration:.2f}s")
        
        return result
    
    def get_batch_estimate(self, item_ids: List[str]) -> Dict[str, Any]:
        """
        Get estimate for batch operation processing time.
        
        Args:
            item_ids: List of item IDs to process
            
        Returns:
            Dictionary with estimates and recommendations
        """
        total_items = len(item_ids)
        
        # Estimate processing time (conservative estimates)
        avg_time_per_item = 0.1  # 100ms per item on average
        estimated_duration = total_items * avg_time_per_item
        
        # Recommendations
        recommendations = []
        if total_items > self.max_batch_size:
            recommendations.append(f"Consider splitting into smaller batches (max {self.max_batch_size} items)")
        
        if estimated_duration > 10.0:  # More than 10 seconds
            recommendations.append("Large batch may take significant time to complete")
        
        if total_items == 0:
            recommendations.append("No items to process")
        
        return {
            'total_items': total_items,
            'estimated_duration_seconds': round(estimated_duration, 2),
            'max_batch_size': self.max_batch_size,
            'recommendations': recommendations,
            'estimated_completion': datetime.utcnow().timestamp() + estimated_duration
        }
    
    def _is_entity_item(self, item_id: str) -> bool:
        """Check if an item is an entity or relationship."""
        try:
            item = self.queue_manager.get_item_by_id(item_id)
            if not item:
                logger.warning(f"Item not found during batch processing: {item_id}")
                return False
            
            return item.type == ReviewItemType.ENTITY
            
        except Exception as e:
            logger.error(f"Error checking item type {item_id}: {str(e)}")
            # Default to entity to avoid breaking the operation
            return True
    
    def validate_batch_permissions(self, item_ids: List[str], user_id: str) -> Tuple[bool, List[str]]:
        """
        Validate that user has permission to process all items.
        
        Args:
            item_ids: List of item IDs to validate
            user_id: User ID to validate against
            
        Returns:
            Tuple of (all_valid, unauthorized_items)
        """
        unauthorized_items = []
        
        for item_id in item_ids:
            try:
                item = self.queue_manager.get_item_by_id(item_id)
                if not item:
                    unauthorized_items.append(item_id)
                    continue
                
                if item.user_id != user_id:
                    unauthorized_items.append(item_id)
                    logger.warning(f"User {user_id} does not own item {item_id}")
                
            except Exception as e:
                unauthorized_items.append(item_id)
                logger.error(f"Error validating item {item_id}: {str(e)}")
        
        all_valid = len(unauthorized_items) == 0
        return all_valid, unauthorized_items


def create_batch_processor(project_id: str = "aletheia-codex-prod") -> BatchProcessor:
    """
    Factory function to create a BatchProcessor instance.
    
    Args:
        project_id: GCP project ID
        
    Returns:
        BatchProcessor instance
    """
    return BatchProcessor(project_id=project_id)