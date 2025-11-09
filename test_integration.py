"""
End-to-end integration test for Sprint 2.

Tests the complete workflow: Document → AI → Graph
"""

import asyncio
import os
import sys
import json
import logging

# Add shared directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'shared'))

from shared.ai.ai_service import create_ai_service
from shared.db.graph_populator import create_graph_populator
from shared.utils.cost_monitor import create_cost_monitor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Test document
TEST_DOCUMENT = {
    "id": "test_doc_integration_001",
    "user_id": "test_user_sprint2",
    "title": "Sprint 2 Integration Test",
    "content": """
    I'm working on the AletheiaCodex project with my colleague Sarah Johnson. 
    She's a software engineer at Google and has been helping me design the knowledge graph architecture.
    
    We're using Neo4j Aura for the graph database and Google Gemini AI for entity extraction.
    The project is based in San Francisco, California, and we started development in January 2025.
    
    The core concept is to build a personal knowledge graph that learns from conversations.
    We're implementing this using Python and Google Cloud Functions for the backend infrastructure.
    """
}


async def test_end_to_end_workflow():
    """Test complete workflow from document to graph."""
    logger.info("="*80)
    logger.info("Sprint 2 End-to-End Integration Test")
    logger.info("="*80)
    
    try:
        # Initialize services
        logger.info("\n1. Initializing services...")
        ai_service = create_ai_service(provider="gemini")
        graph_populator = create_graph_populator()
        cost_monitor = create_cost_monitor()
        
        logger.info("✓ All services initialized")
        
        # Extract entities
        logger.info(f"\n2. Extracting entities from document...")
        logger.info(f"   Document: {TEST_DOCUMENT['title']}")
        logger.info(f"   Content length: {len(TEST_DOCUMENT['content'])} characters")
        
        entities = await ai_service.extract_entities(
            text=TEST_DOCUMENT['content'],
            user_id=TEST_DOCUMENT['user_id'],
            document_id=TEST_DOCUMENT['id'],
            min_confidence=0.7
        )
        
        logger.info(f"\n✓ Extracted {len(entities)} entities:")
        for i, entity in enumerate(entities, 1):
            logger.info(f"   {i}. {entity.name} ({entity.type}) - confidence: {entity.confidence:.2f}")
        
        # Detect relationships
        logger.info(f"\n3. Detecting relationships...")
        
        relationships = await ai_service.detect_relationships(
            text=TEST_DOCUMENT['content'],
            entities=entities,
            user_id=TEST_DOCUMENT['user_id'],
            document_id=TEST_DOCUMENT['id'],
            min_confidence=0.6
        )
        
        logger.info(f"\n✓ Detected {len(relationships)} relationships:")
        for i, rel in enumerate(relationships, 1):
            logger.info(f"   {i}. {rel.source_entity} --[{rel.relationship_type}]--> {rel.target_entity}")
            logger.info(f"      Confidence: {rel.confidence:.2f}")
        
        # Populate graph
        logger.info(f"\n4. Populating Neo4j graph...")
        
        summary = await graph_populator.populate_from_document(
            entities=entities,
            relationships=relationships,
            user_id=TEST_DOCUMENT['user_id']
        )
        
        logger.info(f"\n✓ Graph populated:")
        logger.info(f"   Entities created: {summary['entities_created']}")
        logger.info(f"   Relationships created: {summary['relationships_created']}")
        
        # Get graph statistics
        logger.info(f"\n5. Getting graph statistics...")
        
        stats = await graph_populator.get_user_stats(TEST_DOCUMENT['user_id'])
        
        logger.info(f"\n✓ Graph statistics:")
        logger.info(f"   Total entities: {stats.get('entity_count', 0)}")
        logger.info(f"   Total relationships: {stats.get('relationship_count', 0)}")
        logger.info(f"   Entity types: {stats.get('entity_type_count', 0)}")
        
        # Track costs
        logger.info(f"\n6. Tracking costs...")
        
        # Estimate costs
        cost_estimate = await cost_monitor.get_cost_estimate(
            text=TEST_DOCUMENT['content'],
            operations=['extract_entities', 'detect_relationships']
        )
        
        logger.info(f"\n✓ Cost estimate:")
        logger.info(f"   Entity extraction: ${cost_estimate['extract_entities']:.6f}")
        logger.info(f"   Relationship detection: ${cost_estimate['detect_relationships']:.6f}")
        logger.info(f"   Total: ${cost_estimate['total']:.6f}")
        
        # Log actual usage (simulated with estimates)
        await cost_monitor.log_usage(
            user_id=TEST_DOCUMENT['user_id'],
            provider='gemini',
            model='gemini-2.0-flash-exp',
            operation='extract_entities',
            input_tokens=len(TEST_DOCUMENT['content']) // 4,
            output_tokens=500,
            cost=cost_estimate['extract_entities'],
            document_id=TEST_DOCUMENT['id']
        )
        
        await cost_monitor.log_usage(
            user_id=TEST_DOCUMENT['user_id'],
            provider='gemini',
            model='gemini-2.0-flash-exp',
            operation='detect_relationships',
            input_tokens=len(TEST_DOCUMENT['content']) // 4,
            output_tokens=150,
            cost=cost_estimate['detect_relationships'],
            document_id=TEST_DOCUMENT['id']
        )
        
        logger.info(f"✓ Usage logged to Firestore")
        
        # Get usage summary
        usage_summary = await cost_monitor.get_usage_summary(
            user_id=TEST_DOCUMENT['user_id'],
            timeframe='daily'
        )
        
        logger.info(f"\n✓ Usage summary (daily):")
        logger.info(f"   Total cost: ${usage_summary['total_cost']:.6f}")
        logger.info(f"   Total tokens: {usage_summary['total_tokens']}")
        logger.info(f"   Operations: {usage_summary['operation_counts']}")
        
        # Check cost alerts
        alert_status = await cost_monitor.check_cost_alerts(TEST_DOCUMENT['user_id'])
        
        logger.info(f"\n✓ Cost alert status:")
        for timeframe, level in alert_status['alerts'].items():
            logger.info(f"   {timeframe}: {level}")
        
        # Final summary
        logger.info(f"\n{'='*80}")
        logger.info("Integration Test Summary")
        logger.info(f"{'='*80}")
        logger.info(f"\n✓ Complete workflow executed successfully!")
        logger.info(f"\nResults:")
        logger.info(f"  - Entities extracted: {len(entities)}")
        logger.info(f"  - Relationships detected: {len(relationships)}")
        logger.info(f"  - Entities in graph: {summary['entities_created']}")
        logger.info(f"  - Relationships in graph: {summary['relationships_created']}")
        logger.info(f"  - Total cost: ${cost_estimate['total']:.6f}")
        logger.info(f"  - Cost per note: ${cost_estimate['total']:.6f} (target: <$0.01)")
        
        if cost_estimate['total'] < 0.01:
            logger.info(f"\n✓ Cost target achieved! (${cost_estimate['total']:.6f} < $0.01)")
        else:
            logger.warning(f"\n⚠ Cost target not met (${cost_estimate['total']:.6f} > $0.01)")
        
        return True
        
    except Exception as e:
        logger.error(f"\n✗ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


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
    
    # Run integration test
    success = asyncio.run(test_end_to_end_workflow())
    
    if success:
        logger.info("\n" + "="*80)
        logger.info("✓ ALL TESTS PASSED")
        logger.info("="*80)
        exit(0)
    else:
        logger.error("\n" + "="*80)
        logger.error("✗ TESTS FAILED")
        logger.error("="*80)
        exit(1)