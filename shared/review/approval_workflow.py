"""
Approval workflow for AletheiaCodex.

Handles the approval and rejection of review items, integrating with Neo4j
to add approved items to the knowledge graph.
"""

import logging
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from google.cloud import firestore

from ..models.review_item import ReviewItem, ReviewItemType, ReviewItemStatus
from ..models.entity import Entity
from ..models.relationship import Relationship
from ..db.firestore_client import get_firestore_client
from ..db.neo4j_client import create_neo4j_http_client, execute_neo4j_query_http
from ..db.graph_populator import create_graph_populator
from .queue_manager import QueueManager, create_queue_manager
from ..utils.logging import get_logger

logger = get_logger(__name__)


class ApprovalWorkflow:
    """
    Manages the approval and rejection workflow for review items.
    
    Handles:
    - Entity approval and Neo4j creation
    - Relationship approval and Neo4j creation
    - Rejection with audit logging
    - User ownership verification
    - Statistics tracking
    """
    
    def __init__(self, project_id: str = "aletheia-codex-prod"):
        """
        Initialize approval workflow.
        
        Args:
            project_id: GCP project ID
        """
        self.project_id = project_id
        self.db = get_firestore_client(project_id)
        self.queue_manager = create_queue_manager(project_id)
        self.graph_populator = create_graph_populator(project_id)
        
        logger.info(f"Initialized ApprovalWorkflow for project: {project_id}")
    
    def approve_entity(self, item_id: str, user_id: str) -> bool:
        """
        Approve an entity and add it to Neo4j.
        
        Args:
            item_id: Review item ID
            user_id: User ID approving the item
            
        Returns:
            True if approval successful, False otherwise
            
        Raises:
            ValueError: If user doesn't own the item or item is not an entity
            Exception: If approval fails
        """
        try:
            # Get the review item
            item = self.queue_manager.get_item_by_id(item_id)
            if not item:
                logger.error(f"Review item not found: {item_id}")
                return False
            
            # Verify ownership
            if item.user_id != user_id:
                raise ValueError(f"User {user_id} does not own item {item_id}")
            
            # Verify item type
            if item.type != ReviewItemType.ENTITY:
                raise ValueError(f"Item {item_id} is not an entity")
            
            # Verify item is pending
            if not item.is_pending():
                logger.warning(f"Item {item_id} is not pending: {item.status}")
                return False
            
            # Create Entity object from review item
            entity = self._create_entity_from_review_item(item)
            
            # Add to Neo4j
            success = self._add_entity_to_neo4j(entity, user_id)
            if not success:
                logger.error(f"Failed to add entity to Neo4j: {item_id}")
                return False
            
            # Update item status
            success = self.queue_manager.update_item_status(
                item_id,
                ReviewItemStatus.APPROVED,
                user_id
            )
            
            if success:
                logger.info(f"Approved entity: {entity.name} (ID: {item_id})")
                return True
            else:
                logger.error(f"Failed to update item status after approval: {item_id}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to approve entity {item_id}: {str(e)}")
            raise
    
    def reject_entity(
        self,
        item_id: str,
        user_id: str,
        reason: Optional[str] = None
    ) -> bool:
        """
        Reject an entity with optional reason.
        
        Args:
            item_id: Review item ID
            user_id: User ID rejecting the item
            reason: Optional rejection reason
            
        Returns:
            True if rejection successful, False otherwise
            
        Raises:
            ValueError: If user doesn't own the item or item is not an entity
            Exception: If rejection fails
        """
        try:
            # Get the review item
            item = self.queue_manager.get_item_by_id(item_id)
            if not item:
                logger.error(f"Review item not found: {item_id}")
                return False
            
            # Verify ownership
            if item.user_id != user_id:
                raise ValueError(f"User {user_id} does not own item {item_id}")
            
            # Verify item type
            if item.type != ReviewItemType.ENTITY:
                raise ValueError(f"Item {item_id} is not an entity")
            
            # Log rejection
            self._log_rejection(item, user_id, reason)
            
            # Update item status
            success = self.queue_manager.update_item_status(
                item_id,
                ReviewItemStatus.REJECTED,
                user_id,
                rejection_reason=reason
            )
            
            if success:
                entity_name = item.entity.get('name', 'Unknown') if item.entity else 'Unknown'
                logger.info(f"Rejected entity: {entity_name} (ID: {item_id}, Reason: {reason})")
                return True
            else:
                logger.error(f"Failed to update item status after rejection: {item_id}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to reject entity {item_id}: {str(e)}")
            raise
    
    def approve_relationship(self, item_id: str, user_id: str) -> bool:
        """
        Approve a relationship and add it to Neo4j.
        
        Args:
            item_id: Review item ID
            user_id: User ID approving the item
            
        Returns:
            True if approval successful, False otherwise
            
        Raises:
            ValueError: If user doesn't own the item or item is not a relationship
            Exception: If approval fails
        """
        try:
            # Get the review item
            item = self.queue_manager.get_item_by_id(item_id)
            if not item:
                logger.error(f"Review item not found: {item_id}")
                return False
            
            # Verify ownership
            if item.user_id != user_id:
                raise ValueError(f"User {user_id} does not own item {item_id}")
            
            # Verify item type
            if item.type != ReviewItemType.RELATIONSHIP:
                raise ValueError(f"Item {item_id} is not a relationship")
            
            # Verify item is pending
            if not item.is_pending():
                logger.warning(f"Item {item_id} is not pending: {item.status}")
                return False
            
            # Create Relationship object from review item
            relationship = self._create_relationship_from_review_item(item)
            
            # Add to Neo4j
            success = self._add_relationship_to_neo4j(relationship, user_id)
            if not success:
                logger.error(f"Failed to add relationship to Neo4j: {item_id}")
                return False
            
            # Update item status
            success = self.queue_manager.update_item_status(
                item_id,
                ReviewItemStatus.APPROVED,
                user_id
            )
            
            if success:
                logger.info(f"Approved relationship: {relationship.source_entity} -> {relationship.relationship_type} -> {relationship.target_entity} (ID: {item_id})")
                return True
            else:
                logger.error(f"Failed to update item status after approval: {item_id}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to approve relationship {item_id}: {str(e)}")
            raise
    
    def reject_relationship(
        self,
        item_id: str,
        user_id: str,
        reason: Optional[str] = None
    ) -> bool:
        """
        Reject a relationship with optional reason.
        
        Args:
            item_id: Review item ID
            user_id: User ID rejecting the item
            reason: Optional rejection reason
            
        Returns:
            True if rejection successful, False otherwise
            
        Raises:
            ValueError: If user doesn't own the item or item is not a relationship
            Exception: If rejection fails
        """
        try:
            # Get the review item
            item = self.queue_manager.get_item_by_id(item_id)
            if not item:
                logger.error(f"Review item not found: {item_id}")
                return False
            
            # Verify ownership
            if item.user_id != user_id:
                raise ValueError(f"User {user_id} does not own item {item_id}")
            
            # Verify item type
            if item.type != ReviewItemType.RELATIONSHIP:
                raise ValueError(f"Item {item_id} is not a relationship")
            
            # Log rejection
            self._log_rejection(item, user_id, reason)
            
            # Update item status
            success = self.queue_manager.update_item_status(
                item_id,
                ReviewItemStatus.REJECTED,
                user_id,
                rejection_reason=reason
            )
            
            if success:
                rel = item.relationship or {}
                rel_display = f"{rel.get('source_entity', 'Unknown')} -> {rel.get('relationship_type', 'RELATED')} -> {rel.get('target_entity', 'Unknown')}"
                logger.info(f"Rejected relationship: {rel_display} (ID: {item_id}, Reason: {reason})")
                return True
            else:
                logger.error(f"Failed to update item status after rejection: {item_id}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to reject relationship {item_id}: {str(e)}")
            raise
    
    def _create_entity_from_review_item(self, item: ReviewItem) -> Entity:
        """Create Entity object from review item."""
        if not item.entity:
            raise ValueError("Entity data is required")
        
        return Entity(
            name=item.entity['name'],
            type=item.entity['type'],
            properties=item.entity.get('properties', {}),
            confidence=item.confidence,
            source_document_id=item.source_document_id,
            user_id=item.user_id,
            created_at=item.created_at,
            metadata={
                'review_item_id': item.id,
                'approved_at': datetime.utcnow().isoformat(),
                'extracted_text': item.extracted_text
            }
        )
    
    def _create_relationship_from_review_item(self, item: ReviewItem) -> Relationship:
        """Create Relationship object from review item."""
        if not item.relationship:
            raise ValueError("Relationship data is required")
        
        return Relationship(
            source_entity=item.relationship['source_entity'],
            target_entity=item.relationship['target_entity'],
            relationship_type=item.relationship['relationship_type'],
            properties=item.relationship.get('properties', {}),
            confidence=item.confidence,
            source_document_id=item.source_document_id,
            user_id=item.user_id,
            created_at=item.created_at,
            metadata={
                'review_item_id': item.id,
                'approved_at': datetime.utcnow().isoformat(),
                'extracted_text': item.extracted_text
            }
        )
    
    def _add_entity_to_neo4j(self, entity: Entity, approved_by: str) -> bool:
        """Add entity to Neo4j knowledge graph."""
        try:
            # Check if entity already exists
            existing_id = self._find_existing_entity(entity.name, entity.type)
            if existing_id:
                logger.info(f"Entity already exists in Neo4j: {entity.name} (ID: {existing_id})")
                return True
            
            # Create entity in Neo4j
            success = self.graph_populator.create_entity(entity, approved_by=approved_by)
            if success:
                logger.info(f"Created entity in Neo4j: {entity.name}")
            return success
            
        except Exception as e:
            logger.error(f"Failed to add entity to Neo4j: {str(e)}")
            return False
    
    def _add_relationship_to_neo4j(self, relationship: Relationship, approved_by: str) -> bool:
        """Add relationship to Neo4j knowledge graph."""
        try:
            # Verify both entities exist in Neo4j
            source_exists = self._find_existing_entity(relationship.source_entity)
            target_exists = self._find_existing_entity(relationship.target_entity)
            
            if not source_exists:
                logger.warning(f"Source entity not found in Neo4j: {relationship.source_entity}")
                # Create source entity if it doesn't exist
                source_entity = Entity(
                    name=relationship.source_entity,
                    type="Person",  # Default type
                    user_id=relationship.user_id,
                    source_document_id=relationship.source_document_id,
                    confidence=1.0,  # High confidence for manually created entities
                    metadata={'auto_created': True, 'reason': 'relationship_approval'}
                )
                self.graph_populator.create_entity(source_entity, approved_by=approved_by)
            
            if not target_exists:
                logger.warning(f"Target entity not found in Neo4j: {relationship.target_entity}")
                # Create target entity if it doesn't exist
                target_entity = Entity(
                    name=relationship.target_entity,
                    type="Organization",  # Default type
                    user_id=relationship.user_id,
                    source_document_id=relationship.source_document_id,
                    confidence=1.0,
                    metadata={'auto_created': True, 'reason': 'relationship_approval'}
                )
                self.graph_populator.create_entity(target_entity, approved_by=approved_by)
            
            # Check if relationship already exists
            existing_id = self._find_existing_relationship(relationship)
            if existing_id:
                logger.info(f"Relationship already exists in Neo4j: {relationship.source_entity} -> {relationship.relationship_type} -> {relationship.target_entity}")
                return True
            
            # Create relationship in Neo4j
            success = self.graph_populator.create_relationship(relationship, approved_by=approved_by)
            if success:
                logger.info(f"Created relationship in Neo4j: {relationship.source_entity} -> {relationship.relationship_type} -> {relationship.target_entity}")
            return success
            
        except Exception as e:
            logger.error(f"Failed to add relationship to Neo4j: {str(e)}")
            return False
    
    def _find_existing_entity(self, name: str, entity_type: Optional[str] = None) -> Optional[str]:
        """Find existing entity in Neo4j by name and optionally type."""
        try:
            query = """
            MATCH (e:Entity)
            WHERE e.name = $name
            """
            params = {'name': name}
            
            if entity_type:
                query += " AND e.type = $type"
                params['type'] = entity_type
            
            query += " RETURN e.id AS id LIMIT 1"
            
            result = execute_neo4j_query_http(query, params)
            if result and 'data' in result and result['data']:
                return result['data'][0][0]  # First row, first column
            return None
            
        except Exception as e:
            logger.error(f"Failed to find existing entity: {str(e)}")
            return None
    
    def _find_existing_relationship(self, relationship: Relationship) -> Optional[str]:
        """Find existing relationship in Neo4j."""
        try:
            query = """
            MATCH (s:Entity {name: $source})-[r:RELATIONSHIP {type: $type}]->(t:Entity {name: $target})
            RETURN r.id AS id LIMIT 1
            """
            params = {
                'source': relationship.source_entity,
                'target': relationship.target_entity,
                'type': relationship.relationship_type
            }
            
            result = execute_neo4j_query_http(query, params)
            if result and 'data' in result and result['data']:
                return result['data'][0][0]
            return None
            
        except Exception as e:
            logger.error(f"Failed to find existing relationship: {str(e)}")
            return None
    
    def _log_rejection(self, item: ReviewItem, user_id: str, reason: Optional[str]):
        """Log rejection to audit trail."""
        try:
            # Create audit log entry
            audit_entry = {
                'item_id': item.id,
                'item_type': item.type.value,
                'user_id': user_id,
                'action': 'rejected',
                'reason': reason,
                'confidence': item.confidence,
                'source_document_id': item.source_document_id,
                'rejected_at': datetime.utcnow().isoformat()
            }
            
            # Add item-specific data
            if item.entity:
                audit_entry['entity'] = item.entity
            if item.relationship:
                audit_entry['relationship'] = item.relationship
            if item.extracted_text:
                audit_entry['extracted_text'] = item.extracted_text
            
            # Store in audit collection
            audit_collection = f"audit_{user_id}"
            self.db.collection(audit_collection).add(audit_entry)
            
            logger.info(f"Logged rejection to audit trail: {item.id}")
            
        except Exception as e:
            logger.error(f"Failed to log rejection to audit trail: {str(e)}")
            # Don't raise - audit logging failure shouldn't break main flow


def create_approval_workflow(project_id: str = "aletheia-codex-prod") -> ApprovalWorkflow:
    """
    Factory function to create an ApprovalWorkflow instance.
    
    Args:
        project_id: GCP project ID
        
    Returns:
        ApprovalWorkflow instance
    """
    return ApprovalWorkflow(project_id=project_id)