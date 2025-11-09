"""
Relationship data models for AletheiaCodex.

Defines the structure for relationships between entities.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from datetime import datetime


@dataclass
class Relationship:
    """
    Represents a relationship between two entities.
    
    Attributes:
        source_entity: Name of the source entity
        target_entity: Name of the target entity
        relationship_type: Type of relationship (e.g., WORKS_AT, KNOWS)
        properties: Additional properties as key-value pairs
        confidence: Confidence score (0.0 to 1.0)
        source_document_id: ID of the source document
        user_id: ID of the user who owns this relationship
        created_at: Timestamp when relationship was created
        metadata: Additional metadata
    """
    source_entity: str
    target_entity: str
    relationship_type: str
    properties: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    source_document_id: Optional[str] = None
    user_id: Optional[str] = None
    created_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate relationship after initialization."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {self.confidence}")
        
        if not self.source_entity or not self.source_entity.strip():
            raise ValueError("Source entity cannot be empty")
        
        if not self.target_entity or not self.target_entity.strip():
            raise ValueError("Target entity cannot be empty")
        
        if not self.relationship_type or not self.relationship_type.strip():
            raise ValueError("Relationship type cannot be empty")
        
        # Normalize fields
        self.source_entity = self.source_entity.strip()
        self.target_entity = self.target_entity.strip()
        self.relationship_type = self.relationship_type.strip().upper().replace(' ', '_')
        
        # Set created_at if not provided
        if self.created_at is None:
            self.created_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert relationship to dictionary representation."""
        return {
            'source_entity': self.source_entity,
            'target_entity': self.target_entity,
            'relationship_type': self.relationship_type,
            'properties': self.properties,
            'confidence': self.confidence,
            'source_document_id': self.source_document_id,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Relationship':
        """Create relationship from dictionary representation."""
        # Handle datetime conversion
        created_at = data.get('created_at')
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        
        return cls(
            source_entity=data['source_entity'],
            target_entity=data['target_entity'],
            relationship_type=data['relationship_type'],
            properties=data.get('properties', {}),
            confidence=data.get('confidence', 0.0),
            source_document_id=data.get('source_document_id'),
            user_id=data.get('user_id'),
            created_at=created_at,
            metadata=data.get('metadata', {})
        )
    
    def is_valid(self, min_confidence: float = 0.6) -> bool:
        """
        Check if relationship meets validation criteria.
        
        Args:
            min_confidence: Minimum confidence threshold
            
        Returns:
            True if relationship is valid, False otherwise
        """
        return (
            self.confidence >= min_confidence and
            bool(self.source_entity and self.source_entity.strip()) and
            bool(self.target_entity and self.target_entity.strip()) and
            bool(self.relationship_type and self.relationship_type.strip())
        )


# Standard relationship types
REL_TYPE_KNOWS = "KNOWS"
REL_TYPE_WORKS_AT = "WORKS_AT"
REL_TYPE_LOCATED_IN = "LOCATED_IN"
REL_TYPE_RELATED_TO = "RELATED_TO"
REL_TYPE_HAPPENED_AT = "HAPPENED_AT"
REL_TYPE_INVOLVES = "INVOLVES"
REL_TYPE_PART_OF = "PART_OF"
REL_TYPE_CREATED = "CREATED"
REL_TYPE_OWNS = "OWNS"
REL_TYPE_MEMBER_OF = "MEMBER_OF"
REL_TYPE_MANAGES = "MANAGES"
REL_TYPE_REPORTS_TO = "REPORTS_TO"
REL_TYPE_FOUNDED = "FOUNDED"
REL_TYPE_ATTENDED = "ATTENDED"
REL_TYPE_STUDIED_AT = "STUDIED_AT"

# Valid relationship types
VALID_RELATIONSHIP_TYPES = {
    REL_TYPE_KNOWS,
    REL_TYPE_WORKS_AT,
    REL_TYPE_LOCATED_IN,
    REL_TYPE_RELATED_TO,
    REL_TYPE_HAPPENED_AT,
    REL_TYPE_INVOLVES,
    REL_TYPE_PART_OF,
    REL_TYPE_CREATED,
    REL_TYPE_OWNS,
    REL_TYPE_MEMBER_OF,
    REL_TYPE_MANAGES,
    REL_TYPE_REPORTS_TO,
    REL_TYPE_FOUNDED,
    REL_TYPE_ATTENDED,
    REL_TYPE_STUDIED_AT,
}

# Relationship type aliases
RELATIONSHIP_TYPE_ALIASES = {
    'EMPLOYED_BY': REL_TYPE_WORKS_AT,
    'EMPLOYEE_OF': REL_TYPE_WORKS_AT,
    'IN': REL_TYPE_LOCATED_IN,
    'AT': REL_TYPE_LOCATED_IN,
    'CONNECTED_TO': REL_TYPE_RELATED_TO,
    'ASSOCIATED_WITH': REL_TYPE_RELATED_TO,
    'OCCURRED_AT': REL_TYPE_HAPPENED_AT,
    'INCLUDES': REL_TYPE_INVOLVES,
    'CONTAINS': REL_TYPE_INVOLVES,
    'COMPONENT_OF': REL_TYPE_PART_OF,
    'BELONGS_TO': REL_TYPE_PART_OF,
}


def normalize_relationship_type(rel_type: str) -> str:
    """
    Normalize relationship type to standard form.
    
    Args:
        rel_type: Raw relationship type string
        
    Returns:
        Normalized relationship type
    """
    rel_type = rel_type.strip().upper().replace(' ', '_')
    
    # Check if it's already a valid type
    if rel_type in VALID_RELATIONSHIP_TYPES:
        return rel_type
    
    # Check aliases
    if rel_type in RELATIONSHIP_TYPE_ALIASES:
        return RELATIONSHIP_TYPE_ALIASES[rel_type]
    
    # Return as-is for custom relationship types
    # (Neo4j allows dynamic relationship types)
    return rel_type