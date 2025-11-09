"""
Cypher query templates for Neo4j graph operations.

Provides reusable query templates for entity and relationship management.
"""

from typing import Dict, Any, List


# User node queries
CREATE_USER_NODE = """
MERGE (u:User {user_id: $user_id})
ON CREATE SET u.created_at = timestamp()
RETURN u
"""

GET_USER_NODE = """
MATCH (u:User {user_id: $user_id})
RETURN u
"""


# Entity node queries
CREATE_ENTITY_NODE = """
MATCH (u:User {user_id: $user_id})
MERGE (u)-[:OWNS]->(e:{entity_type} {name: $name})
ON CREATE SET 
    e.created_at = timestamp(),
    e.confidence = $confidence,
    e.source_document_id = $source_document_id
ON MATCH SET
    e.updated_at = timestamp(),
    e.confidence = CASE 
        WHEN $confidence > e.confidence THEN $confidence 
        ELSE e.confidence 
    END
SET e += $properties
RETURN e
"""

GET_ENTITY_NODE = """
MATCH (u:User {user_id: $user_id})-[:OWNS]->(e:{entity_type} {name: $name})
RETURN e
"""

GET_ALL_USER_ENTITIES = """
MATCH (u:User {user_id: $user_id})-[:OWNS]->(e)
RETURN e, labels(e) as types
ORDER BY e.created_at DESC
"""

DELETE_ENTITY_NODE = """
MATCH (u:User {user_id: $user_id})-[:OWNS]->(e:{entity_type} {name: $name})
DETACH DELETE e
"""


# Relationship queries
CREATE_RELATIONSHIP = """
MATCH (u:User {user_id: $user_id})
MATCH (u)-[:OWNS]->(source {name: $source_name})
MATCH (u)-[:OWNS]->(target {name: $target_name})
MERGE (source)-[r:{relationship_type}]->(target)
ON CREATE SET 
    r.created_at = timestamp(),
    r.confidence = $confidence,
    r.source_document_id = $source_document_id
ON MATCH SET
    r.updated_at = timestamp(),
    r.confidence = CASE 
        WHEN $confidence > r.confidence THEN $confidence 
        ELSE r.confidence 
    END
SET r += $properties
RETURN r, source, target
"""

GET_RELATIONSHIP = """
MATCH (u:User {user_id: $user_id})
MATCH (u)-[:OWNS]->(source {name: $source_name})
MATCH (u)-[:OWNS]->(target {name: $target_name})
MATCH (source)-[r:{relationship_type}]->(target)
RETURN r, source, target
"""

GET_ALL_USER_RELATIONSHIPS = """
MATCH (u:User {user_id: $user_id})
MATCH (u)-[:OWNS]->(source)
MATCH (u)-[:OWNS]->(target)
MATCH (source)-[r]->(target)
RETURN r, source, target, type(r) as relationship_type
ORDER BY r.created_at DESC
"""

DELETE_RELATIONSHIP = """
MATCH (u:User {user_id: $user_id})
MATCH (u)-[:OWNS]->(source {name: $source_name})
MATCH (u)-[:OWNS]->(target {name: $target_name})
MATCH (source)-[r:{relationship_type}]->(target)
DELETE r
"""


# Entity search queries
SEARCH_ENTITIES_BY_NAME = """
MATCH (u:User {user_id: $user_id})-[:OWNS]->(e)
WHERE toLower(e.name) CONTAINS toLower($search_term)
RETURN e, labels(e) as types
ORDER BY e.confidence DESC
LIMIT $limit
"""

SEARCH_ENTITIES_BY_TYPE = """
MATCH (u:User {user_id: $user_id})-[:OWNS]->(e:{entity_type})
RETURN e
ORDER BY e.confidence DESC
LIMIT $limit
"""


# Graph traversal queries
GET_ENTITY_NEIGHBORS = """
MATCH (u:User {user_id: $user_id})-[:OWNS]->(e {name: $entity_name})
MATCH (e)-[r]-(neighbor)
RETURN neighbor, r, type(r) as relationship_type
"""

GET_ENTITY_SUBGRAPH = """
MATCH (u:User {user_id: $user_id})-[:OWNS]->(e {name: $entity_name})
MATCH path = (e)-[*1..{max_depth}]-(connected)
WHERE (u)-[:OWNS]->(connected)
RETURN path
LIMIT $limit
"""


# Statistics queries
GET_USER_STATS = """
MATCH (u:User {user_id: $user_id})
OPTIONAL MATCH (u)-[:OWNS]->(e)
OPTIONAL MATCH (u)-[:OWNS]->(source)-[r]->(target)<-[:OWNS]-(u)
RETURN 
    count(DISTINCT e) as entity_count,
    count(DISTINCT r) as relationship_count,
    count(DISTINCT labels(e)) as entity_type_count
"""

GET_ENTITY_TYPE_COUNTS = """
MATCH (u:User {user_id: $user_id})-[:OWNS]->(e)
RETURN labels(e)[0] as entity_type, count(e) as count
ORDER BY count DESC
"""

GET_RELATIONSHIP_TYPE_COUNTS = """
MATCH (u:User {user_id: $user_id})
MATCH (u)-[:OWNS]->(source)-[r]->(target)<-[:OWNS]-(u)
RETURN type(r) as relationship_type, count(r) as count
ORDER BY count DESC
"""


# Deduplication queries
FIND_DUPLICATE_ENTITIES = """
MATCH (u:User {user_id: $user_id})-[:OWNS]->(e:{entity_type})
WITH e.name as name, collect(e) as entities
WHERE size(entities) > 1
RETURN name, entities
"""

MERGE_DUPLICATE_ENTITIES = """
MATCH (u:User {user_id: $user_id})-[:OWNS]->(e:{entity_type} {name: $name})
WITH collect(e) as entities
WHERE size(entities) > 1
WITH entities[0] as keep, entities[1..] as remove
UNWIND remove as r
MATCH (r)-[rel]-()
CREATE (keep)-[new_rel:type(rel)]->(endNode(rel))
SET new_rel = rel
DELETE rel, r
RETURN keep
"""


def build_create_entity_query(entity_type: str) -> str:
    """
    Build a CREATE query for a specific entity type.
    
    Args:
        entity_type: Type of entity (Person, Organization, etc.)
        
    Returns:
        Cypher query string
    """
    return CREATE_ENTITY_NODE.replace("{entity_type}", entity_type)


def build_create_relationship_query(relationship_type: str) -> str:
    """
    Build a CREATE query for a specific relationship type.
    
    Args:
        relationship_type: Type of relationship (WORKS_AT, KNOWS, etc.)
        
    Returns:
        Cypher query string
    """
    return CREATE_RELATIONSHIP.replace("{relationship_type}", relationship_type)


def build_get_entity_query(entity_type: str) -> str:
    """
    Build a GET query for a specific entity type.
    
    Args:
        entity_type: Type of entity
        
    Returns:
        Cypher query string
    """
    return GET_ENTITY_NODE.replace("{entity_type}", entity_type)


def build_get_relationship_query(relationship_type: str) -> str:
    """
    Build a GET query for a specific relationship type.
    
    Args:
        relationship_type: Type of relationship
        
    Returns:
        Cypher query string
    """
    return GET_RELATIONSHIP.replace("{relationship_type}", relationship_type)