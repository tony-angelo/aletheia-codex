"""
AletheiaCodex - Orchestration Function with Firestore Trigger
Automatically processes notes when they are created in Firestore.

SPRINT 5 FIX: Changed from HTTP trigger to Firestore trigger
- Automatically triggered when a note is created in the 'notes' collection
- No authentication needed (runs with service account)
- Processes notes in real-time
"""

import functions_framework
from google.cloud import firestore
from firebase_admin import initialize_app
import os
import json
import time
from typing import Optional, List, Dict, Any
import asyncio
from cloudevents.http import CloudEvent

# Initialize Firebase Admin
try:
    initialize_app()
except ValueError:
    # Already initialized
    pass

from shared.db.firestore_client import get_firestore_client
from shared.db.neo4j_client import (
    create_neo4j_http_client,
    execute_neo4j_query_http
)
from shared.ai.ai_service import create_ai_service
from shared.db.graph_populator import create_graph_populator
from shared.utils.cost_monitor import create_cost_monitor
from shared.utils.logging import get_logger
from shared.utils.text_chunker import chunk_text

logger = get_logger("orchestration")

PROJECT_ID = os.environ.get("GCP_PROJECT", "aletheia-codex-prod")

# Retry configuration
MAX_RETRIES = 3
INITIAL_RETRY_DELAY = 1  # seconds
MAX_RETRY_DELAY = 10  # seconds


def retry_with_backoff(func, max_retries=MAX_RETRIES, initial_delay=INITIAL_RETRY_DELAY):
    """
    Retry a function with exponential backoff.
    
    Args:
        func: Function to retry
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        
    Returns:
        Function result
        
    Raises:
        Last exception if all retries fail
    """
    delay = initial_delay
    last_exception = None
    
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            last_exception = e
            if attempt < max_retries - 1:
                logger.warning(
                    f"Transient error on attempt {attempt + 1}/{max_retries}: {type(e).__name__}: {str(e)}. "
                    f"Retrying in {delay}s..."
                )
                time.sleep(delay)
                delay = min(delay * 2, MAX_RETRY_DELAY)  # Exponential backoff with cap
            else:
                logger.error(f"All {max_retries} retry attempts failed")
                raise
    
    # Should never reach here, but just in case
    if last_exception:
        raise last_exception


def update_note_status(note_id: str, status: str, error: Optional[str] = None, **kwargs):
    """
    Update note status in Firestore with error handling.
    
    Args:
        note_id: Note document ID
        status: New status ('processing', 'completed', 'failed')
        error: Error message if status is 'failed'
        **kwargs: Additional fields to update
    """
    logger.info(f"=" * 80)
    logger.info(f"UPDATING NOTE STATUS: {note_id}")
    logger.info(f"Status: {status}")
    if error:
        logger.info(f"Error: {error}")
    logger.info(f"Additional fields: {kwargs}")
    logger.info(f"=" * 80)
    
    try:
        db = get_firestore_client()
        note_ref = db.collection('notes').document(note_id)
        
        update_data = {
            'status': status,
            'updatedAt': firestore.SERVER_TIMESTAMP
        }
        
        if error:
            update_data['error'] = error
        
        # Add any additional fields
        update_data.update(kwargs)
        
        note_ref.update(update_data)
        logger.info(f"Successfully updated note {note_id} status to {status}")
        
    except Exception as e:
        logger.error(f"Failed to update note status: {type(e).__name__}: {str(e)}")
        # Don't raise - we don't want status update failures to break processing


async def process_with_ai(note_id: str, content: str, user_id: str) -> Dict[str, Any]:
    """
    Process content with AI to extract entities and relationships.
    
    Args:
        note_id: Note ID for tracking
        content: Text content to process
        user_id: User ID for cost tracking
        
    Returns:
        Dictionary with entities, relationships, and costs
    """
    logger.info(f"=" * 80)
    logger.info(f"AI PROCESSING STARTED")
    logger.info(f"=" * 80)
    logger.info(f"Note ID: {note_id}")
    logger.info(f"User ID: {user_id}")
    logger.info(f"Content length: {len(content)} characters")
    logger.info(f"Content preview: {content[:200]}...")
    
    try:
        # Initialize AI service
        ai_service = create_ai_service()
        cost_monitor = create_cost_monitor()
        
        # Chunk text if needed
        chunks = chunk_text(content, max_chunk_size=8000)
        logger.info(f"Content split into {len(chunks)} chunks")
        
        all_entities = []
        all_relationships = []
        total_cost = 0.0
        
        # Process each chunk
        for i, chunk in enumerate(chunks):
            logger.info(f"Processing chunk {i+1}/{len(chunks)} ({len(chunk)} chars)")
            
            try:
                result = await ai_service.extract_entities_and_relationships(
                    text=chunk,
                    user_id=user_id
                )
                
                entities = result.get('entities', [])
                relationships = result.get('relationships', [])
                cost = result.get('cost', 0.0)
                
                logger.info(f"Chunk {i+1} results: {len(entities)} entities, {len(relationships)} relationships")
                logger.info(f"Chunk {i+1} cost: ${cost:.4f}")
                
                all_entities.extend(entities)
                all_relationships.extend(relationships)
                total_cost += cost
                
            except Exception as e:
                logger.error(f"Failed to process chunk {i+1}: {type(e).__name__}: {str(e)}")
                # Continue with other chunks
        
        # Record cost
        cost_monitor.record_cost(
            user_id=user_id,
            operation='ai_extraction',
            cost=total_cost,
            metadata={
                'note_id': note_id,
                'chunks_processed': len(chunks),
                'entities_extracted': len(all_entities),
                'relationships_detected': len(all_relationships)
            }
        )
        
        logger.info(f"=" * 80)
        logger.info(f"AI PROCESSING COMPLETE")
        logger.info(f"Total entities: {len(all_entities)}")
        logger.info(f"Total relationships: {len(all_relationships)}")
        logger.info(f"Total cost: ${total_cost:.4f}")
        logger.info(f"=" * 80)
        
        return {
            'entities': all_entities,
            'relationships': all_relationships,
            'costs': {
                'ai_extraction': total_cost,
                'total': total_cost
            }
        }
        
    except Exception as e:
        logger.error(f"=" * 80)
        logger.error(f"AI PROCESSING FAILED")
        logger.error(f"Error: {type(e).__name__}: {str(e)}")
        logger.error(f"=" * 80)
        logger.exception("Full traceback:")
        raise


async def store_in_review_queue(note_id: str, entities: List[Dict], relationships: List[Dict], user_id: str):
    """
    Store extracted entities and relationships in review queue.
    
    Args:
        note_id: Note ID
        entities: List of extracted entities
        relationships: List of detected relationships
        user_id: User ID
    """
    logger.info(f"=" * 80)
    logger.info(f"STORING IN REVIEW QUEUE")
    logger.info(f"=" * 80)
    logger.info(f"Note ID: {note_id}")
    logger.info(f"User ID: {user_id}")
    logger.info(f"Entities: {len(entities)}")
    logger.info(f"Relationships: {len(relationships)}")
    
    try:
        db = get_firestore_client()
        batch = db.batch()
        items_created = 0
        
        # Create review items for entities
        for i, entity in enumerate(entities):
            logger.info(f"Creating entity review item {i+1}/{len(entities)}: {entity.get('name', 'unknown')}")
            
            doc_ref = db.collection('review_queue').document()
            batch.set(doc_ref, {
                'user_id': user_id,
                'note_id': note_id,
                'type': 'entity',
                'data': entity,
                'status': 'pending',
                'confidence': entity.get('confidence', 0.0),
                'created_at': firestore.SERVER_TIMESTAMP
            })
            items_created += 1
        
        # Create review items for relationships
        for i, relationship in enumerate(relationships):
            logger.info(f"Creating relationship review item {i+1}/{len(relationships)}")
            
            doc_ref = db.collection('review_queue').document()
            batch.set(doc_ref, {
                'user_id': user_id,
                'note_id': note_id,
                'type': 'relationship',
                'data': relationship,
                'status': 'pending',
                'confidence': relationship.get('confidence', 0.0),
                'created_at': firestore.SERVER_TIMESTAMP
            })
            items_created += 1
        
        # Commit batch
        logger.info(f"Committing batch with {items_created} items...")
        batch.commit()
        
        logger.info(f"=" * 80)
        logger.info(f"REVIEW QUEUE STORAGE COMPLETE")
        logger.info(f"Items created: {items_created}")
        logger.info(f"=" * 80)
        
    except Exception as e:
        logger.error(f"=" * 80)
        logger.error(f"REVIEW QUEUE STORAGE FAILED")
        logger.error(f"Error: {type(e).__name__}: {str(e)}")
        logger.error(f"=" * 80)
        logger.exception("Full traceback:")
        raise


async def populate_knowledge_graph(entities: List[Dict], relationships: List[Dict], user_id: str) -> Dict[str, int]:
    """
    Populate knowledge graph with high-confidence entities and relationships.
    
    Args:
        entities: List of entities to add
        relationships: List of relationships to add
        user_id: User ID
        
    Returns:
        Dictionary with counts of entities and relationships created
    """
    logger.info(f"=" * 80)
    logger.info(f"POPULATING KNOWLEDGE GRAPH")
    logger.info(f"=" * 80)
    logger.info(f"User ID: {user_id}")
    logger.info(f"Entities: {len(entities)}")
    logger.info(f"Relationships: {len(relationships)}")
    
    try:
        graph_populator = create_graph_populator()
        
        result = await graph_populator.populate_graph(
            entities=entities,
            relationships=relationships,
            user_id=user_id
        )
        
        logger.info(f"=" * 80)
        logger.info(f"KNOWLEDGE GRAPH POPULATION COMPLETE")
        logger.info(f"Entities created: {result.get('entities_created', 0)}")
        logger.info(f"Relationships created: {result.get('relationships_created', 0)}")
        logger.info(f"=" * 80)
        
        return result
        
    except Exception as e:
        logger.error(f"=" * 80)
        logger.error(f"KNOWLEDGE GRAPH POPULATION FAILED")
        logger.error(f"Error: {type(e).__name__}: {str(e)}")
        logger.error(f"=" * 80)
        logger.exception("Full traceback:")
        raise


@functions_framework.cloud_event
def orchestration_function(cloud_event: CloudEvent):
    """
    Firestore trigger function that processes notes when they are created.
    
    Triggered by: Firestore document creation in 'notes' collection
    
    Event structure:
    {
        "data": {
            "value": {
                "fields": {
                    "userId": {"stringValue": "user-id"},
                    "content": {"stringValue": "note content"},
                    "status": {"stringValue": "processing"},
                    ...
                }
            }
        }
    }
    """
    logger.info("=" * 80)
    logger.info("ORCHESTRATION FUNCTION TRIGGERED")
    logger.info("=" * 80)
    
    note_id = None
    
    try:
        # Log event details
        logger.info(f"Event ID: {cloud_event.get('id', 'unknown')}")
        logger.info(f"Event type: {cloud_event.get('type', 'unknown')}")
        logger.info(f"Event source: {cloud_event.get('source', 'unknown')}")
        logger.info(f"Event time: {cloud_event.get('time', 'unknown')}")
        
        # Parse event data
        data = cloud_event.data
        logger.info(f"Event data keys: {list(data.keys())}")
        
        # Extract document data from Firestore event
        value = data.get('value', {})
        fields = value.get('fields', {})
        logger.info(f"Document fields: {list(fields.keys())}")
        
        # Extract note details
        note_id = cloud_event.get('subject', '').split('/')[-1]
        user_id = fields.get('userId', {}).get('stringValue', '')
        content = fields.get('content', {}).get('stringValue', '')
        status = fields.get('status', {}).get('stringValue', '')
        
        logger.info(f"Note ID: {note_id}")
        logger.info(f"User ID: {user_id}")
        logger.info(f"Content length: {len(content)} characters")
        logger.info(f"Status: {status}")
        
        # Validate required fields
        if not note_id:
            logger.error("No note ID found in event")
            return
        
        if not user_id:
            logger.error(f"No user ID found for note {note_id}")
            update_note_status(note_id, 'failed', error='Missing user ID')
            return
        
        if not content:
            logger.error(f"No content found for note {note_id}")
            update_note_status(note_id, 'failed', error='Missing content')
            return
        
        # Only process notes with 'processing' status
        if status != 'processing':
            logger.info(f"Skipping note with status: {status}")
            return
        
        # Update status to processing (with timestamp)
        update_note_status(
            note_id,
            'processing',
            processingStartedAt=firestore.SERVER_TIMESTAMP
        )
        
        # Process with AI
        logger.info("Starting AI processing...")
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            ai_results = loop.run_until_complete(
                process_with_ai(note_id, content, user_id)
            )
            
            entities = ai_results['entities']
            relationships = ai_results['relationships']
            costs = ai_results['costs']
            
            logger.info(f"AI processing complete: {len(entities)} entities, {len(relationships)} relationships")
            
        except Exception as e:
            logger.error(f"AI processing failed: {type(e).__name__}: {str(e)}")
            update_note_status(note_id, 'failed', error=f"AI processing error: {str(e)}")
            return
        
        # Store in review queue
        logger.info("Storing in review queue...")
        try:
            loop.run_until_complete(
                store_in_review_queue(note_id, entities, relationships, user_id)
            )
            logger.info("Review queue storage complete")
            
        except Exception as e:
            logger.error(f"Review queue storage failed: {type(e).__name__}: {str(e)}")
            update_note_status(note_id, 'failed', error=f"Review queue error: {str(e)}")
            return
        
        # Populate knowledge graph (auto-approve high confidence items)
        logger.info("Populating knowledge graph...")
        try:
            high_confidence_entities = [e for e in entities if e.get('confidence', 0) >= 0.85]
            high_confidence_relationships = [r for r in relationships if r.get('confidence', 0) >= 0.80]
            
            logger.info(f"High confidence items: {len(high_confidence_entities)} entities, {len(high_confidence_relationships)} relationships")
            
            if high_confidence_entities or high_confidence_relationships:
                graph_summary = loop.run_until_complete(
                    populate_knowledge_graph(
                        high_confidence_entities,
                        high_confidence_relationships,
                        user_id
                    )
                )
            else:
                graph_summary = {'entities_created': 0, 'relationships_created': 0}
            
            logger.info(f"Knowledge graph population complete: {graph_summary}")
            
            loop.close()
            
        except Exception as e:
            logger.error(f"Knowledge graph population failed: {type(e).__name__}: {str(e)}")
            # Don't fail the whole request - items are still in review queue
            graph_summary = {'entities_created': 0, 'relationships_created': 0}
        
        # Update status to completed
        logger.info("Updating note status to completed...")
        update_note_status(
            note_id,
            'completed',
            processingCompletedAt=firestore.SERVER_TIMESTAMP,
            extractionSummary={
                'entityCount': len(entities),
                'relationshipCount': len(relationships)
            }
        )
        
        logger.info("=" * 80)
        logger.info("ORCHESTRATION COMPLETE")
        logger.info(f"Note ID: {note_id}")
        logger.info(f"Entities extracted: {len(entities)}")
        logger.info(f"Relationships detected: {len(relationships)}")
        logger.info(f"Entities in graph: {graph_summary['entities_created']}")
        logger.info(f"Relationships in graph: {graph_summary['relationships_created']}")
        logger.info(f"Processing cost: ${costs['total']:.4f}")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error("=" * 80)
        logger.error("ORCHESTRATION FAILED")
        logger.error(f"Error: {type(e).__name__}: {str(e)}")
        logger.error("=" * 80)
        logger.exception("Full traceback:")
        
        # Update status to failed
        if note_id:
            update_note_status(note_id, 'failed', error=str(e))