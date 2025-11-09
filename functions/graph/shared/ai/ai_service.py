"""
AI service wrapper for AletheiaCodex.

Provides a unified interface for AI operations with provider management,
caching, and error handling.
"""

import logging
from typing import List, Optional, Dict, Any
from google.cloud import secretmanager

from .base_provider import BaseAIProvider, AIProviderError
from .gemini_provider import GeminiProvider
from ..models.entity import Entity
from ..models.relationship import Relationship

logger = logging.getLogger(__name__)


class AIService:
    """
    Unified AI service for entity extraction and relationship detection.
    
    Manages AI provider instances, handles authentication, and provides
    a consistent interface for AI operations.
    """
    
    def __init__(
        self,
        provider: str = "gemini",
        project_id: str = "aletheia-codex-prod",
        api_key: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize AI service.
        
        Args:
            provider: AI provider name (default: "gemini")
            project_id: GCP project ID for secret retrieval
            api_key: Optional API key (if not provided, retrieved from Secret Manager)
            **kwargs: Additional provider-specific configuration
        """
        self.provider_name = provider
        self.project_id = project_id
        self.provider: Optional[BaseAIProvider] = None
        
        # Get API key if not provided
        if api_key is None:
            api_key = self._get_api_key_from_secret_manager()
        
        # Initialize provider
        self.provider = self._create_provider(provider, api_key, **kwargs)
        
        logger.info(f"Initialized AI service with provider: {provider}")
    
    async def extract_entities(
        self,
        text: str,
        user_id: str,
        document_id: Optional[str] = None,
        min_confidence: float = 0.7,
        **kwargs
    ) -> List[Entity]:
        """
        Extract entities from text.
        
        Args:
            text: Input text to extract entities from
            user_id: ID of the user who owns the document
            document_id: Optional document ID for tracking
            min_confidence: Minimum confidence threshold (default: 0.7)
            **kwargs: Additional provider-specific parameters
            
        Returns:
            List of validated entities
        """
        try:
            logger.info(f"Extracting entities for user {user_id}")
            
            # Extract entities using provider
            entities = await self.provider.extract_entities(
                text=text,
                user_id=user_id,
                document_id=document_id,
                **kwargs
            )
            
            # Validate entities
            valid_entities = self.provider.validate_entities(entities, min_confidence)
            
            logger.info(f"Extracted {len(entities)} entities, "
                       f"{len(valid_entities)} passed validation")
            
            return valid_entities
            
        except AIProviderError as e:
            logger.error(f"Entity extraction failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during entity extraction: {e}")
            raise AIProviderError(f"Entity extraction failed: {e}")
    
    async def detect_relationships(
        self,
        text: str,
        entities: List[Entity],
        user_id: str,
        document_id: Optional[str] = None,
        min_confidence: float = 0.6,
        **kwargs
    ) -> List[Relationship]:
        """
        Detect relationships between entities.
        
        Args:
            text: Original text containing the entities
            entities: List of entities to find relationships between
            user_id: ID of the user who owns the document
            document_id: Optional document ID for tracking
            min_confidence: Minimum confidence threshold (default: 0.6)
            **kwargs: Additional provider-specific parameters
            
        Returns:
            List of validated relationships
        """
        try:
            logger.info(f"Detecting relationships for user {user_id}")
            
            # Detect relationships using provider
            relationships = await self.provider.detect_relationships(
                text=text,
                entities=entities,
                user_id=user_id,
                document_id=document_id,
                **kwargs
            )
            
            # Validate relationships
            valid_relationships = self.provider.validate_relationships(
                relationships, min_confidence
            )
            
            logger.info(f"Detected {len(relationships)} relationships, "
                       f"{len(valid_relationships)} passed validation")
            
            return valid_relationships
            
        except AIProviderError as e:
            logger.error(f"Relationship detection failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during relationship detection: {e}")
            raise AIProviderError(f"Relationship detection failed: {e}")
    
    def estimate_cost(
        self,
        text: str,
        include_relationships: bool = True
    ) -> Dict[str, float]:
        """
        Estimate the cost of processing text.
        
        Args:
            text: Input text to estimate cost for
            include_relationships: Whether to include relationship detection cost
            
        Returns:
            Dictionary with cost breakdown
        """
        entity_cost = self.provider.estimate_cost(text, 'extract_entities')
        
        costs = {
            'entity_extraction': entity_cost,
            'relationship_detection': 0.0,
            'total': entity_cost
        }
        
        if include_relationships:
            rel_cost = self.provider.estimate_cost(text, 'detect_relationships')
            costs['relationship_detection'] = rel_cost
            costs['total'] += rel_cost
        
        return costs
    
    def get_provider_info(self) -> Dict[str, str]:
        """
        Get information about the current provider.
        
        Returns:
            Dictionary with provider information
        """
        return {
            'provider': self.provider.get_provider_name(),
            'model': self.provider.get_model_name()
        }
    
    def _create_provider(
        self,
        provider: str,
        api_key: str,
        **kwargs
    ) -> BaseAIProvider:
        """
        Create AI provider instance.
        
        Args:
            provider: Provider name
            api_key: API key for authentication
            **kwargs: Additional configuration
            
        Returns:
            Initialized provider instance
        """
        if provider.lower() == "gemini":
            return GeminiProvider(api_key=api_key, **kwargs)
        else:
            raise ValueError(f"Unsupported AI provider: {provider}")
    
    def _get_api_key_from_secret_manager(self) -> str:
        """
        Retrieve API key from Secret Manager.
        
        Returns:
            API key string
        """
        try:
            client = secretmanager.SecretManagerServiceClient()
            
            # Determine secret name based on provider
            if self.provider_name.lower() == "gemini":
                secret_name = "GEMINI_API_KEY"
            else:
                raise ValueError(f"Unknown secret for provider: {self.provider_name}")
            
            # Build secret path
            name = f"projects/{self.project_id}/secrets/{secret_name}/versions/latest"
            
            # Access secret
            logger.info(f"Retrieving {secret_name} from Secret Manager")
            response = client.access_secret_version(request={"name": name})
            api_key = response.payload.data.decode("UTF-8").strip()
            
            logger.info(f"Successfully retrieved {secret_name}")
            return api_key
            
        except Exception as e:
            logger.error(f"Failed to retrieve API key from Secret Manager: {e}")
            raise AIProviderError(f"Failed to retrieve API key: {e}")


# Convenience function for creating AI service
def create_ai_service(
    provider: str = "gemini",
    project_id: str = "aletheia-codex-prod",
    **kwargs
) -> AIService:
    """
    Create and configure AI service.
    
    Args:
        provider: AI provider name (default: "gemini")
        project_id: GCP project ID
        **kwargs: Additional configuration
        
    Returns:
        Configured AIService instance
    """
    return AIService(provider=provider, project_id=project_id, **kwargs)