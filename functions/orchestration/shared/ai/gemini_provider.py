"""
Gemini AI provider implementation for AletheiaCodex.

Implements the BaseAIProvider interface using Google's Gemini API.
"""

import json
import logging
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

from .base_provider import (
    BaseAIProvider,
    AIProviderError,
    AIProviderAuthError,
    AIProviderRateLimitError,
    AIProviderResponseError
)
from ..models.entity import Entity, normalize_entity_type
from ..models.relationship import Relationship, normalize_relationship_type
from .prompts.entity_extraction import build_entity_extraction_prompt
from .prompts.relationship_detection import build_relationship_detection_prompt

logger = logging.getLogger(__name__)


class GeminiProvider(BaseAIProvider):
    """
    Gemini AI provider implementation.
    
    Uses Google's Gemini 2.0 Flash model for entity extraction
    and relationship detection.
    """
    
    # Pricing for Gemini 2.0 Flash (per 1M tokens)
    PRICE_INPUT_PER_1M = 0.075  # $0.075 per 1M input tokens
    PRICE_OUTPUT_PER_1M = 0.30  # $0.30 per 1M output tokens
    
    def __init__(
        self,
        api_key: str,
        model_name: str = "gemini-2.0-flash-exp",
        temperature: float = 0.2,
        **kwargs
    ):
        """
        Initialize Gemini provider.
        
        Args:
            api_key: Gemini API key
            model_name: Model to use (default: gemini-2.0-flash-exp)
            temperature: Temperature for generation (0.0-1.0, default: 0.2)
            **kwargs: Additional configuration
        """
        self.api_key = api_key
        self.model_name = model_name
        self.temperature = temperature
        
        # Configure Gemini
        try:
            genai.configure(api_key=api_key)
            logger.info(f"Configured Gemini API with model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to configure Gemini API: {e}")
            raise AIProviderAuthError(f"Gemini authentication failed: {e}")
        
        # Initialize model with safety settings
        self.model = genai.GenerativeModel(
            model_name=model_name,
            generation_config={
                "temperature": temperature,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 8192,
            },
            safety_settings={
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
        )
        
        logger.info(f"Initialized Gemini provider with model: {model_name}")
    
    async def extract_entities(
        self,
        text: str,
        user_id: str,
        document_id: Optional[str] = None,
        **kwargs
    ) -> List[Entity]:
        """
        Extract entities from text using Gemini.
        
        Args:
            text: Input text to extract entities from
            user_id: ID of the user who owns the document
            document_id: Optional document ID for tracking
            **kwargs: Additional parameters
            
        Returns:
            List of extracted entities
        """
        try:
            logger.info(f"Extracting entities from text (length: {len(text)})")
            
            # Build prompt
            prompt = build_entity_extraction_prompt(text)
            
            # Generate response
            response = await self._generate_content_async(prompt)
            
            # Parse response
            entities_data = self._parse_json_response(response)
            
            # Convert to Entity objects
            entities = []
            for entity_dict in entities_data:
                try:
                    # Normalize entity type
                    entity_type = normalize_entity_type(entity_dict.get('type', 'Thing'))
                    
                    entity = Entity(
                        type=entity_type,
                        name=entity_dict['name'],
                        properties=entity_dict.get('properties', {}),
                        confidence=entity_dict.get('confidence', 0.0),
                        source_document_id=document_id,
                        user_id=user_id
                    )
                    entities.append(entity)
                except Exception as e:
                    logger.warning(f"Failed to create entity from {entity_dict}: {e}")
                    continue
            
            logger.info(f"Extracted {len(entities)} entities")
            return entities
            
        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            raise AIProviderError(f"Entity extraction failed: {e}")
    
    async def detect_relationships(
        self,
        text: str,
        entities: List[Entity],
        user_id: str,
        document_id: Optional[str] = None,
        **kwargs
    ) -> List[Relationship]:
        """
        Detect relationships between entities using Gemini.
        
        Args:
            text: Original text containing the entities
            entities: List of entities to find relationships between
            user_id: ID of the user who owns the document
            document_id: Optional document ID for tracking
            **kwargs: Additional parameters
            
        Returns:
            List of detected relationships
        """
        try:
            logger.info(f"Detecting relationships for {len(entities)} entities")
            
            # Convert entities to dict format for prompt
            entities_dict = [e.to_dict() for e in entities]
            
            # Build prompt
            prompt = build_relationship_detection_prompt(text, entities_dict)
            
            # Generate response
            response = await self._generate_content_async(prompt)
            
            # Parse response
            relationships_data = self._parse_json_response(response)
            
            # Convert to Relationship objects
            relationships = []
            for rel_dict in relationships_data:
                try:
                    # Normalize relationship type
                    rel_type = normalize_relationship_type(
                        rel_dict.get('relationship_type', 'RELATED_TO')
                    )
                    
                    relationship = Relationship(
                        source_entity=rel_dict['source_entity'],
                        target_entity=rel_dict['target_entity'],
                        relationship_type=rel_type,
                        properties=rel_dict.get('properties', {}),
                        confidence=rel_dict.get('confidence', 0.0),
                        source_document_id=document_id,
                        user_id=user_id
                    )
                    relationships.append(relationship)
                except Exception as e:
                    logger.warning(f"Failed to create relationship from {rel_dict}: {e}")
                    continue
            
            logger.info(f"Detected {len(relationships)} relationships")
            return relationships
            
        except Exception as e:
            logger.error(f"Relationship detection failed: {e}")
            raise AIProviderError(f"Relationship detection failed: {e}")
    
    def estimate_cost(
        self,
        text: str,
        operation: str = 'extract_entities'
    ) -> float:
        """
        Estimate the cost of processing text.
        
        Args:
            text: Input text to estimate cost for
            operation: Type of operation
            
        Returns:
            Estimated cost in USD
        """
        # Estimate input tokens
        input_tokens = self.get_token_count(text)
        
        # Estimate output tokens based on operation
        if operation == 'extract_entities':
            # Assume ~50 tokens per entity, ~10 entities average
            output_tokens = 500
        elif operation == 'detect_relationships':
            # Assume ~30 tokens per relationship, ~5 relationships average
            output_tokens = 150
        else:
            output_tokens = 200
        
        # Calculate cost
        input_cost = (input_tokens / 1_000_000) * self.PRICE_INPUT_PER_1M
        output_cost = (output_tokens / 1_000_000) * self.PRICE_OUTPUT_PER_1M
        
        total_cost = input_cost + output_cost
        
        logger.debug(f"Estimated cost: ${total_cost:.6f} "
                    f"(input: {input_tokens} tokens, output: {output_tokens} tokens)")
        
        return total_cost
    
    def get_provider_name(self) -> str:
        """Get the provider name."""
        return "gemini"
    
    def get_model_name(self) -> str:
        """Get the model name."""
        return self.model_name
    
    async def _generate_content_async(self, prompt: str) -> str:
        """
        Generate content asynchronously using Gemini.
        
        Args:
            prompt: Input prompt
            
        Returns:
            Generated text response
        """
        try:
            response = await self.model.generate_content_async(prompt)
            
            # Check for blocked content
            if not response.text:
                if response.prompt_feedback:
                    logger.error(f"Content blocked: {response.prompt_feedback}")
                    raise AIProviderResponseError("Content was blocked by safety filters")
                raise AIProviderResponseError("Empty response from Gemini")
            
            return response.text
            
        except Exception as e:
            if "quota" in str(e).lower() or "rate" in str(e).lower():
                raise AIProviderRateLimitError(f"Rate limit exceeded: {e}")
            elif "auth" in str(e).lower() or "api key" in str(e).lower():
                raise AIProviderAuthError(f"Authentication failed: {e}")
            else:
                raise AIProviderError(f"Content generation failed: {e}")
    
    def _parse_json_response(self, response: str) -> List[Dict[str, Any]]:
        """
        Parse JSON response from Gemini.
        
        Args:
            response: Raw response text
            
        Returns:
            Parsed JSON data as list
        """
        try:
            # Remove markdown code blocks if present
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            # Parse JSON
            data = json.loads(response)
            
            # Ensure it's a list
            if not isinstance(data, list):
                logger.warning(f"Response is not a list, wrapping: {type(data)}")
                data = [data]
            
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Response text: {response[:500]}")
            raise AIProviderResponseError(f"Invalid JSON response: {e}")
    
    def get_token_count(self, text: str) -> int:
        """
        Estimate token count for text.
        
        Uses Gemini's token counting if available, otherwise falls back to heuristic.
        
        Args:
            text: Input text
            
        Returns:
            Estimated token count
        """
        try:
            # Try to use Gemini's token counting
            result = self.model.count_tokens(text)
            return result.total_tokens
        except Exception as e:
            logger.debug(f"Token counting failed, using heuristic: {e}")
            # Fallback to heuristic (4 chars per token)
            return len(text) // 4