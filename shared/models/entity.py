"""
Entity data models for AletheiaCodex.

Defines the structure for entities extracted from documents.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from datetime import datetime


@dataclass
class Entity:
    """
    Represents an entity extracted from a document.
    
    Attributes:
        type: Entity type (Person, Organization, Place, Concept, Moment, Thing)
        name: Entity name/identifier
        properties: Additional properties as key-value pairs
        confidence: Confidence score (0.0 to 1.0)
        source_document_id: ID of the source document
        user_id: ID of the user who owns this entity
        created_at: Timestamp when entity was created
        metadata: Additional metadata
    """
    type: str
    name: str
    properties: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    source_document_id: Optional[str] = None
    user_id: Optional[str] = None
    created_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate entity after initialization."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {self.confidence}")
        
        if not self.name or not self.name.strip():
            raise ValueError("Entity name cannot be empty")
        
        if not self.type or not self.type.strip():
            raise ValueError("Entity type cannot be empty")
        
        # Normalize entity type
        self.type = self.type.strip().title()
        self.name = self.name.strip()
        
        # Set created_at if not provided
        if self.created_at is None:
            self.created_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary representation."""
        return {
            'type': self.type,
            'name': self.name,
            'properties': self.properties,
            'confidence': self.confidence,
            'source_document_id': self.source_document_id,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Entity':
        """Create entity from dictionary representation."""
        # Handle datetime conversion
        created_at = data.get('created_at')
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        
        return cls(
            type=data['type'],
            name=data['name'],
            properties=data.get('properties', {}),
            confidence=data.get('confidence', 0.0),
            source_document_id=data.get('source_document_id'),
            user_id=data.get('user_id'),
            created_at=created_at,
            metadata=data.get('metadata', {})
        )
    
    def is_valid(self, min_confidence: float = 0.7) -> bool:
        """
        Check if entity meets validation criteria.
        
        Args:
            min_confidence: Minimum confidence threshold
            
        Returns:
            True if entity is valid, False otherwise
        """
        return (
            self.confidence >= min_confidence and
            bool(self.name and self.name.strip()) and
            bool(self.type and self.type.strip())
        )


# Entity type constants
ENTITY_TYPE_PERSON = "Person"
ENTITY_TYPE_ORGANIZATION = "Organization"
ENTITY_TYPE_PLACE = "Place"
ENTITY_TYPE_CONCEPT = "Concept"
ENTITY_TYPE_MOMENT = "Moment"
ENTITY_TYPE_THING = "Thing"

# Valid entity types
VALID_ENTITY_TYPES = {
    ENTITY_TYPE_PERSON,
    ENTITY_TYPE_ORGANIZATION,
    ENTITY_TYPE_PLACE,
    ENTITY_TYPE_CONCEPT,
    ENTITY_TYPE_MOMENT,
    ENTITY_TYPE_THING
}

# Entity type aliases for mapping
ENTITY_TYPE_ALIASES = {
    'Company': ENTITY_TYPE_ORGANIZATION,
    'Business': ENTITY_TYPE_ORGANIZATION,
    'Location': ENTITY_TYPE_PLACE,
    'Event': ENTITY_TYPE_MOMENT,
    'Idea': ENTITY_TYPE_CONCEPT,
    'Topic': ENTITY_TYPE_CONCEPT,
    'Object': ENTITY_TYPE_THING,
    'Item': ENTITY_TYPE_THING,
}


def normalize_entity_type(entity_type: str) -> str:
    """
    Normalize entity type to standard form.
    
    Args:
        entity_type: Raw entity type string
        
    Returns:
        Normalized entity type
    """
    entity_type = entity_type.strip().title()
    
    # Check if it's already a valid type
    if entity_type in VALID_ENTITY_TYPES:
        return entity_type
    
    # Check aliases
    if entity_type in ENTITY_TYPE_ALIASES:
        return ENTITY_TYPE_ALIASES[entity_type]
    
    # Default to Thing for unknown types
    return ENTITY_TYPE_THING