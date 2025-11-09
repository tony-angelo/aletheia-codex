"""
Graph population logic for AletheiaCodex.

Handles creating and updating entities and relationships in Neo4j.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from .neo4j_client import execute_query, create_neo4j_http_client, execute_neo4j_query_http
from .graph_queries import (
    CREATE_USER_NODE,
    build_create_entity_query,
    build_create_relationship_query,
    GET_USER_STATS
)
from ..models.entity import Entity
from ..models.relationship import Relationship

logger = logging.getLogger(__name__)


class GraphPopulator:
    """
    Handles population of Neo4j knowledge graph with entities and relationships.
    """
    
    def __init__(self, project_id: str = "aletheia-codex-prod"):
        """
        Initialize graph populator.
        
        Args:
            project_id: GCP project ID for Neo4j credentials
        """
        self.project_id = project_id
        logger.info("Initialized GraphPopulator")
    
    async def ensure_user_exists(self, user_id: str) -> Dict[str, Any]:
        """
        Ensure user node exists in graph.
        
        Args:
            user_id: User ID
            
        Returns:
            User node data
        """
        try:
            logger.info(f"Ensuring user node exists: {user_id}")
            
            result = execute_query(
                CREATE_USER_NODE,
                {'user_id': user_id},
                self.project_id
            )
            
            logger.info(f"User node ensured: {user_id}")
            return result[0] if result else {}
            
        except Exception as e:
            logger.error(f"Failed to ensure user node: {e}")
            raise
    
    async def create_entity(self, entity: Entity) -> Dict[str, Any]:
        """
        Create or update entity node in graph.
        
        Args:
            entity: Entity to create
            
        Returns:
            Created/updated entity node data
        """
        try:
            logger.info(f"Creating entity: {entity.name} ({entity.type})")
            
            # Ensure user exists
            await self.ensure_user_exists(entity.user_id)
            
            # Build query for specific entity type
            query = build_create_entity_query(entity.type)
            
            # Prepare parameters
            params = {
                'user_id': entity.user_id,
                'name': entity.name,
                'confidence': entity.confidence,
                'source_document_id': entity.source_document_id,
                'properties': entity.properties
            }
            
            # Execute query
            result = execute_query(query, params, self.project_id)
            
            logger.info(f"Entity created: {entity.name}")
            return result[0] if result else {}
            
        except Exception as e:
            logger.error(f"Failed to create entity {entity.name}: {e}")
            raise
    
    async def create_entities_batch(self, entities: List[Entity]) -> List[Dict[str, Any]]:
        """
        Create multiple entities in batch.
        
        Args:
            entities: List of entities to create
            
        Returns:
            List of created entity node data
        """
        logger.info(f"Creating {len(entities)} entities in batch")
        
        results = []
        for entity in entities:
            try:
                result = await self.create_entity(entity)
                results.append(result)
            except Exception as e:
                logger.warning(f"Failed to create entity {entity.name}: {e}")
                continue
        
        logger.info(f"Created {len(results)}/{len(entities)} entities")
        return results
    
    async def create_relationship(self, relationship: Relationship) -> Dict[str, Any]:
        """
        Create or update relationship in graph.
        
        Args:
            relationship: Relationship to create
            
        Returns:
            Created/updated relationship data
        """
        try:
            logger.info(f"Creating relationship: {relationship.source_entity} "
                       f"--[{relationship.relationship_type}]--> {relationship.target_entity}")
            
            # Ensure user exists
            await self.ensure_user_exists(relationship.user_id)
            
            # Build query for specific relationship type
            query = build_create_relationship_query(relationship.relationship_type)
            
            # Prepare parameters
            params = {
                'user_id': relationship.user_id,
                'source_name': relationship.source_entity,
                'target_name': relationship.target_entity,
                'confidence': relationship.confidence,
                'source_document_id': relationship.source_document_id,
                'properties': relationship.properties
            }
            
            # Execute query
            result = execute_query(query, params, self.project_id)
            
            logger.info(f"Relationship created: {relationship.relationship_type}")
            return result[0] if result else {}
            
        except Exception as e:
            logger.error(f"Failed to create relationship "
                        f"{relationship.source_entity} -> {relationship.target_entity}: {e}")
            raise
    
    async def create_relationships_batch(
        self,
        relationships: List[Relationship]
    ) -> List[Dict[str, Any]]:
        """
        Create multiple relationships in batch.
        
        Args:
            relationships: List of relationships to create
            
        Returns:
            List of created relationship data
        """
        logger.info(f"Creating {len(relationships)} relationships in batch")
        
        results = []
        for relationship in relationships:
            try:
                result = await self.create_relationship(relationship)
                results.append(result)
            except Exception as e:
                logger.warning(f"Failed to create relationship "
                             f"{relationship.source_entity} -> {relationship.target_entity}: {e}")
                continue
        
        logger.info(f"Created {len(results)}/{len(relationships)} relationships")
        return results
    
    async def populate_from_document(
        self,
        entities: List[Entity],
        relationships: List[Relationship],
        user_id: str
    ) -> Dict[str, Any]:
        """
        Populate graph with entities and relationships from a document.
        
        Args:
            entities: List of entities to create
            relationships: List of relationships to create
            user_id: User ID
            
        Returns:
            Summary of created nodes and relationships
        """
        try:
            logger.info(f"Populating graph for user {user_id}: "
                       f"{len(entities)} entities, {len(relationships)} relationships")
            
            # Ensure user exists
            await self.ensure_user_exists(user_id)
            
            # Create entities
            entity_results = await self.create_entities_batch(entities)
            
            # Create relationships
            relationship_results = await self.create_relationships_batch(relationships)
            
            summary = {
                'user_id': user_id,
                'entities_created': len(entity_results),
                'relationships_created': len(relationship_results),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            logger.info(f"Graph population complete: {summary}")
            return summary
            
        except Exception as e:
            logger.error(f"Failed to populate graph: {e}")
            raise
    
    async def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """
        Get statistics for user's graph.
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with graph statistics
        """
        try:
            logger.info(f"Getting stats for user: {user_id}")
            
            result = execute_query(
                GET_USER_STATS,
                {'user_id': user_id},
                self.project_id
            )
            
            if result and len(result) > 0:
                # Result is a list of values, not a dict
                stats_list = result[0] if isinstance(result[0], list) else result
                
                stats = {
                    'entity_count': stats_list[0] if len(stats_list) > 0 else 0,
                    'relationship_count': stats_list[1] if len(stats_list) > 1 else 0,
                    'entity_type_count': stats_list[2] if len(stats_list) > 2 else 0
                }
                
                logger.info(f"User stats: {stats}")
                return stats
            
            return {
                'entity_count': 0,
                'relationship_count': 0,
                'entity_type_count': 0
            }
            
        except Exception as e:
            logger.error(f"Failed to get user stats: {e}")
            raise


# Convenience function
def create_graph_populator(project_id: str = "aletheia-codex-prod") -> GraphPopulator:
    """
    Create a GraphPopulator instance.
    
    Args:
        project_id: GCP project ID
        
    Returns:
        GraphPopulator instance
    """
    return GraphPopulator(project_id)