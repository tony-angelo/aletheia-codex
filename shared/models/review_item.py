"""
Review item data model for AletheiaCodex.

Defines the structure for items in the review queue that users can approve or reject.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Literal
from datetime import datetime
from enum import Enum


class ReviewItemType(str, Enum):
    """Types of items that can be reviewed."""
    ENTITY = "entity"
    RELATIONSHIP = "relationship"


class ReviewItemStatus(str, Enum):
    """Status of review items."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass
class ReviewItem:
    """
    Represents an item in the review queue.
    
    Attributes:
        id: Unique identifier for the review item
        user_id: ID of the user who owns this item
        type: Type of item (entity or relationship)
        status: Current status (pending, approved, rejected)
        confidence: Confidence score (0.0 to 1.0)
        source_document_id: ID of the source document
        created_at: Timestamp when item was created
        reviewed_at: Timestamp when item was reviewed (None if pending)
        entity: Entity data (if type is entity)
        relationship: Relationship data (if type is relationship)
        extracted_text: Context text from document
        rejection_reason: Reason for rejection (if rejected)
        metadata: Additional metadata
    """
    user_id: str
    type: ReviewItemType
    status: ReviewItemStatus
    confidence: float
    source_document_id: str
    id: Optional[str] = None
    created_at: Optional[datetime] = None
    reviewed_at: Optional[datetime] = None
    entity: Optional[Dict[str, Any]] = None
    relationship: Optional[Dict[str, Any]] = None
    extracted_text: Optional[str] = None
    rejection_reason: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate review item after initialization."""
        # Validate confidence
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {self.confidence}")
        
        # Validate user_id
        if not self.user_id or not self.user_id.strip():
            raise ValueError("User ID cannot be empty")
        
        # Validate source_document_id
        if not self.source_document_id or not self.source_document_id.strip():
            raise ValueError("Source document ID cannot be empty")
        
        # Validate type-specific data
        if self.type == ReviewItemType.ENTITY:
            if not self.entity:
                raise ValueError("Entity data is required for entity type")
            if not self.entity.get('name') or not self.entity.get('type'):
                raise ValueError("Entity must have name and type")
        elif self.type == ReviewItemType.RELATIONSHIP:
            if not self.relationship:
                raise ValueError("Relationship data is required for relationship type")
            required_fields = ['source_entity', 'target_entity', 'relationship_type']
            if not all(self.relationship.get(field) for field in required_fields):
                raise ValueError(f"Relationship must have {', '.join(required_fields)}")
        
        # Set created_at if not provided
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        
        # Normalize fields
        self.user_id = self.user_id.strip()
        self.source_document_id = self.source_document_id.strip()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert review item to dictionary representation."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type.value if isinstance(self.type, ReviewItemType) else self.type,
            'status': self.status.value if isinstance(self.status, ReviewItemStatus) else self.status,
            'confidence': self.confidence,
            'source_document_id': self.source_document_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
            'entity': self.entity,
            'relationship': self.relationship,
            'extracted_text': self.extracted_text,
            'rejection_reason': self.rejection_reason,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ReviewItem':
        """Create review item from dictionary representation."""
        # Handle datetime conversion
        created_at = data.get('created_at')
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        
        reviewed_at = data.get('reviewed_at')
        if isinstance(reviewed_at, str):
            reviewed_at = datetime.fromisoformat(reviewed_at)
        
        # Handle enum conversion
        item_type = data['type']
        if isinstance(item_type, str):
            item_type = ReviewItemType(item_type)
        
        status = data['status']
        if isinstance(status, str):
            status = ReviewItemStatus(status)
        
        return cls(
            id=data.get('id'),
            user_id=data['user_id'],
            type=item_type,
            status=status,
            confidence=data['confidence'],
            source_document_id=data['source_document_id'],
            created_at=created_at,
            reviewed_at=reviewed_at,
            entity=data.get('entity'),
            relationship=data.get('relationship'),
            extracted_text=data.get('extracted_text'),
            rejection_reason=data.get('rejection_reason'),
            metadata=data.get('metadata', {})
        )
    
    def is_pending(self) -> bool:
        """Check if item is pending review."""
        return self.status == ReviewItemStatus.PENDING
    
    def is_approved(self) -> bool:
        """Check if item is approved."""
        return self.status == ReviewItemStatus.APPROVED
    
    def is_rejected(self) -> bool:
        """Check if item is rejected."""
        return self.status == ReviewItemStatus.REJECTED
    
    def get_display_name(self) -> str:
        """Get display name for the item."""
        if self.type == ReviewItemType.ENTITY:
            return self.entity.get('name', 'Unknown Entity')
        elif self.type == ReviewItemType.RELATIONSHIP:
            source = self.relationship.get('source_entity', 'Unknown')
            target = self.relationship.get('target_entity', 'Unknown')
            rel_type = self.relationship.get('relationship_type', 'RELATED_TO')
            return f"{source} → {rel_type} → {target}"
        return "Unknown Item"
    
    def get_confidence_level(self) -> Literal['high', 'medium', 'low']:
        """Get confidence level category."""
        if self.confidence >= 0.8:
            return 'high'
        elif self.confidence >= 0.5:
            return 'medium'
        else:
            return 'low'


@dataclass
class UserStats:
    """
    User review statistics.
    
    Attributes:
        user_id: User ID
        total_pending: Number of pending items
        total_approved: Number of approved items
        total_rejected: Number of rejected items
        last_review_at: Timestamp of last review
        average_confidence: Average confidence of reviewed items
    """
    user_id: str
    total_pending: int = 0
    total_approved: int = 0
    total_rejected: int = 0
    last_review_at: Optional[datetime] = None
    average_confidence: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user stats to dictionary representation."""
        return {
            'user_id': self.user_id,
            'total_pending': self.total_pending,
            'total_approved': self.total_approved,
            'total_rejected': self.total_rejected,
            'last_review_at': self.last_review_at.isoformat() if self.last_review_at else None,
            'average_confidence': self.average_confidence
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserStats':
        """Create user stats from dictionary representation."""
        last_review_at = data.get('last_review_at')
        if isinstance(last_review_at, str):
            last_review_at = datetime.fromisoformat(last_review_at)
        
        return cls(
            user_id=data['user_id'],
            total_pending=data.get('total_pending', 0),
            total_approved=data.get('total_approved', 0),
            total_rejected=data.get('total_rejected', 0),
            last_review_at=last_review_at,
            average_confidence=data.get('average_confidence', 0.0)
        )
    
    def get_total_reviewed(self) -> int:
        """Get total number of reviewed items."""
        return self.total_approved + self.total_rejected
    
    def get_approval_rate(self) -> float:
        """Get approval rate (0.0 to 1.0)."""
        total_reviewed = self.get_total_reviewed()
        if total_reviewed == 0:
            return 0.0
        return self.total_approved / total_reviewed