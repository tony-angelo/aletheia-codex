"""
Test script for AI service functionality.

Tests entity extraction and relationship detection using the Gemini provider.
"""

import asyncio
import os
import sys
import json
import logging

# Add shared directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'shared'))

from shared.ai.ai_service import create_ai_service
from shared.models.entity import Entity
from shared.models.relationship import Relationship

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Test documents
TEST_DOCUMENTS = [
    {
        "title": "Simple Test",
        "text": "Steve Jobs founded Apple in 1976 in Cupertino, California. He revolutionized personal computing with the Macintosh."
    },
    {
        "title": "Conference Note",
        "text": "I attended the AI conference in London last week. The keynote on deep learning was fascinating. I met Sarah who works at Google as a software engineer."
    },
    {
        "title": "Project Note",
        "text": "Working on the AletheiaCodex project with Neo4j and Gemini AI. The knowledge graph is stored in Neo4j Aura. Using Python and Google Cloud Functions for the backend."
    }
]


async def test_entity_extraction(ai_service, test_doc):
    """Test entity extraction on a document."""
    logger.info(f"\n{'='*80}")
    logger.info(f"Testing Entity Extraction: {test_doc['title']}")
    logger.info(f"{'='*80}")
    logger.info(f"Text: {test_doc['text']}")
    
    try:
        # Extract entities
        entities = await ai_service.extract_entities(
            text=test_doc['text'],
            user_id="test_user",
            document_id="test_doc_1",
            min_confidence=0.7
        )
        
        logger.info(f"\n✓ Extracted {len(entities)} entities:")
        for i, entity in enumerate(entities, 1):
            logger.info(f"\n  {i}. {entity.name} ({entity.type})")
            logger.info(f"     Confidence: {entity.confidence:.2f}")
            if entity.properties:
                logger.info(f"     Properties: {json.dumps(entity.properties, indent=8)}")
        
        return entities
        
    except Exception as e:
        logger.error(f"✗ Entity extraction failed: {e}")
        raise


async def test_relationship_detection(ai_service, test_doc, entities):
    """Test relationship detection on entities."""
    logger.info(f"\n{'='*80}")
    logger.info(f"Testing Relationship Detection: {test_doc['title']}")
    logger.info(f"{'='*80}")
    
    try:
        # Detect relationships
        relationships = await ai_service.detect_relationships(
            text=test_doc['text'],
            entities=entities,
            user_id="test_user",
            document_id="test_doc_1",
            min_confidence=0.6
        )
        
        logger.info(f"\n✓ Detected {len(relationships)} relationships:")
        for i, rel in enumerate(relationships, 1):
            logger.info(f"\n  {i}. {rel.source_entity} --[{rel.relationship_type}]--> {rel.target_entity}")
            logger.info(f"     Confidence: {rel.confidence:.2f}")
            if rel.properties:
                logger.info(f"     Properties: {json.dumps(rel.properties, indent=8)}")
        
        return relationships
        
    except Exception as e:
        logger.error(f"✗ Relationship detection failed: {e}")
        raise


async def test_cost_estimation(ai_service, test_doc):
    """Test cost estimation."""
    logger.info(f"\n{'='*80}")
    logger.info(f"Testing Cost Estimation: {test_doc['title']}")
    logger.info(f"{'='*80}")
    
    try:
        costs = ai_service.estimate_cost(test_doc['text'], include_relationships=True)
        
        logger.info(f"\n✓ Cost Estimation:")
        logger.info(f"  Entity Extraction: ${costs['entity_extraction']:.6f}")
        logger.info(f"  Relationship Detection: ${costs['relationship_detection']:.6f}")
        logger.info(f"  Total: ${costs['total']:.6f}")
        
        return costs
        
    except Exception as e:
        logger.error(f"✗ Cost estimation failed: {e}")
        raise


async def main():
    """Main test function."""
    logger.info("="*80)
    logger.info("AI Service Test Suite")
    logger.info("="*80)
    
    try:
        # Create AI service
        logger.info("\n1. Initializing AI Service...")
        ai_service = create_ai_service(provider="gemini")
        
        provider_info = ai_service.get_provider_info()
        logger.info(f"✓ AI Service initialized")
        logger.info(f"  Provider: {provider_info['provider']}")
        logger.info(f"  Model: {provider_info['model']}")
        
        # Test each document
        all_results = []
        for test_doc in TEST_DOCUMENTS:
            try:
                # Test entity extraction
                entities = await test_entity_extraction(ai_service, test_doc)
                
                # Test relationship detection
                relationships = await test_relationship_detection(ai_service, test_doc, entities)
                
                # Test cost estimation
                costs = await test_cost_estimation(ai_service, test_doc)
                
                all_results.append({
                    'title': test_doc['title'],
                    'entities': len(entities),
                    'relationships': len(relationships),
                    'cost': costs['total']
                })
                
            except Exception as e:
                logger.error(f"Test failed for '{test_doc['title']}': {e}")
                continue
        
        # Summary
        logger.info(f"\n{'='*80}")
        logger.info("Test Summary")
        logger.info(f"{'='*80}")
        
        total_entities = sum(r['entities'] for r in all_results)
        total_relationships = sum(r['relationships'] for r in all_results)
        total_cost = sum(r['cost'] for r in all_results)
        
        logger.info(f"\nTests Completed: {len(all_results)}/{len(TEST_DOCUMENTS)}")
        logger.info(f"Total Entities Extracted: {total_entities}")
        logger.info(f"Total Relationships Detected: {total_relationships}")
        logger.info(f"Total Estimated Cost: ${total_cost:.6f}")
        
        logger.info("\n✓ All tests completed successfully!")
        
    except Exception as e:
        logger.error(f"\n✗ Test suite failed: {e}")
        raise


if __name__ == "__main__":
    # Set environment variable for service account
    if not os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'):
        service_account_path = os.path.join(
            os.path.dirname(__file__),
            'service-account-key.json'
        )
        if os.path.exists(service_account_path):
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = service_account_path
            logger.info(f"Using service account: {service_account_path}")
    
    # Run tests
    asyncio.run(main())