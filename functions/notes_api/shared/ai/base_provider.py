"""
Base AI provider interface for AletheiaCodex.

Defines the abstract interface that all AI providers must implement.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from ..models.entity import Entity
from ..models.relationship import Relationship


class BaseAIProvider(ABC):
    """
    Abstract base class for AI providers.
    
    All AI providers (Gemini, OpenAI, etc.) must implement this interface
    to ensure consistent behavior across the application.
    """
    
    @abstractmethod
    def __init__(self, api_key: str, **kwargs):
        """
        Initialize the AI provider.
        
        Args:
            api_key: API key for authentication
            **kwargs: Additional provider-specific configuration
        """
        pass
    
    @abstractmethod
    async def extract_entities(
        self,
        text: str,
        user_id: str,
        document_id: Optional[str] = None,
        **kwargs
    ) -> List[Entity]:
        """
        Extract entities from text.
        
        Args:
            text: Input text to extract entities from
            user_id: ID of the user who owns the document
            document_id: Optional document ID for tracking
            **kwargs: Additional provider-specific parameters
            
        Returns:
            List of extracted entities
        """
        pass
    
    @abstractmethod
    async def detect_relationships(
        self,
        text: str,
        entities: List[Entity],
        user_id: str,
        document_id: Optional[str] = None,
        **kwargs
    ) -> List[Relationship]:
        """
        Detect relationships between entities.
        
        Args:
            text: Original text containing the entities
            entities: List of entities to find relationships between
            user_id: ID of the user who owns the document
            document_id: Optional document ID for tracking
            **kwargs: Additional provider-specific parameters
            
        Returns:
            List of detected relationships
        """
        pass
    
    @abstractmethod
    def estimate_cost(
        self,
        text: str,
        operation: str = 'extract_entities'
    ) -> float:
        """
        Estimate the cost of processing text.
        
        Args:
            text: Input text to estimate cost for
            operation: Type of operation (extract_entities, detect_relationships)
            
        Returns:
            Estimated cost in USD
        """
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """
        Get the name of the AI provider.
        
        Returns:
            Provider name (e.g., 'gemini', 'openai')
        """
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        """
        Get the name of the model being used.
        
        Returns:
            Model name (e.g., 'gemini-2.0-flash-exp')
        """
        pass
    
    def get_token_count(self, text: str) -> int:
        """
        Estimate token count for text.
        
        Default implementation uses a simple heuristic.
        Providers can override with more accurate counting.
        
        Args:
            text: Input text
            
        Returns:
            Estimated token count
        """
        # Simple heuristic: ~4 characters per token
        return len(text) // 4
    
    def validate_entities(
        self,
        entities: List[Entity],
        min_confidence: float = 0.7
    ) -> List[Entity]:
        """
        Validate and filter entities based on confidence threshold.
        
        Args:
            entities: List of entities to validate
            min_confidence: Minimum confidence threshold
            
        Returns:
            List of valid entities
        """
        return [e for e in entities if e.is_valid(min_confidence)]
    
    def validate_relationships(
        self,
        relationships: List[Relationship],
        min_confidence: float = 0.6
    ) -> List[Relationship]:
        """
        Validate and filter relationships based on confidence threshold.
        
        Args:
            relationships: List of relationships to validate
            min_confidence: Minimum confidence threshold
            
        Returns:
            List of valid relationships
        """
        return [r for r in relationships if r.is_valid(min_confidence)]


class AIProviderError(Exception):
    """Base exception for AI provider errors."""
    pass


class AIProviderAuthError(AIProviderError):
    """Exception raised for authentication errors."""
    pass


class AIProviderRateLimitError(AIProviderError):
    """Exception raised when rate limit is exceeded."""
    pass


class AIProviderResponseError(AIProviderError):
    """Exception raised when response parsing fails."""
    pass