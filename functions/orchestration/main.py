"""
AletheiaCodex - Orchestration Function with AI Integration
Processes documents: entity extraction, relationship detection, and knowledge graph storage.

SPRINT 2 UPDATE: Now includes AI-powered entity extraction and relationship detection
using Google Gemini API.

FEATURES:
- AI-powered entity extraction
- Relationship detection
- Review queue integration
- Cost monitoring
- Neo4j HTTP API for connectivity
- Retry logic for transient failures
- Enhanced error handling
- Comprehensive logging
"""

import functions_framework
from flask import Request, jsonify
from google.cloud import firestore, storage
import os
import json
import time
from typing import Optional, Tuple, List, Dict, Any
import asyncio

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
BUCKET_NAME = f"{PROJECT_ID}-documents"

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


def update_document_status(document_id: str, status: str, error: Optional[str] = None, **kwargs):
    """
    Update document status in Firestore with error handling.
    
    Args:
        document_id: Document ID
        status: New status
        error: Error message (optional)
        **kwargs: Additional fields to update
    """
    try:
        db = get_firestore_client(PROJECT_ID)
        update_data = {"status": status}
        
        if error:
            update_data["error"] = error
            
        update_data.update(kwargs)
        
        db.collection("documents").document(document_id).update(update_data)
        logger.info(f"Updated document {document_id} status to: {status}")
    except Exception as e:
        logger.error(f"Failed to update document status: {str(e)}")
        # Don't raise - status update failure shouldn't break the main flow


def fetch_document_content(document_id: str) -> Tuple[str, dict]:
    """
    Fetch document content and metadata.
    
    Args:
        document_id: Document ID
        
    Returns:
        Tuple of (content, metadata)
        
    Raises:
        Exception if fetch fails
    """
    try:
        # Fetch from Cloud Storage
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(f"raw/{document_id}.txt")
        
        if not blob.exists():
            raise ValueError(f"Document content not found: {document_id}")
        
        content = blob.download_as_text()
        logger.info(f"Fetched content: {len(content)} characters")
        
        # Fetch metadata from Firestore
        db = get_firestore_client(PROJECT_ID)
        doc_ref = db.collection("documents").document(document_id)
        doc_data = doc_ref.get().to_dict()
        
        if not doc_data:
            raise ValueError(f"Document metadata not found: {document_id}")
        
        return content, doc_data
        
    except Exception as e:
        logger.error(f"Failed to fetch document: {str(e)}")
        raise


async def process_with_ai(
    document_id: str,
    content: str,
    user_id: str
) -> Dict[str, Any]:
    """
    Process document with AI: extract entities and detect relationships.
    
    Args:
        document_id: Document ID
        content: Document content
        user_id: User ID
        
    Returns:
        Dictionary with entities, relationships, and costs
    """
    try:
        logger.info(f"Starting AI processing for document {document_id}")
        
        # Initialize services
        ai_service = create_ai_service(provider="gemini", project_id=PROJECT_ID)
        cost_monitor = create_cost_monitor(project_id=PROJECT_ID)
        
        # Extract entities
        logger.info("Extracting entities...")
        entities = await ai_service.extract_entities(
            text=content,
            user_id=user_id,
            document_id=document_id,
            min_confidence=0.7
        )
        logger.info(f"Extracted {len(entities)} entities")
        
        # Detect relationships
        logger.info("Detecting relationships...")
        relationships = await ai_service.detect_relationships(
            text=content,
            entities=entities,
            user_id=user_id,
            document_id=document_id,
            min_confidence=0.6
        )
        logger.info(f"Detected {len(relationships)} relationships")
        
        # Estimate costs
        costs = ai_service.estimate_cost(content, include_relationships=True)
        logger.info(f"Estimated cost: ${costs['total']:.6f}")
        
        # Log usage for cost monitoring
        await cost_monitor.log_usage(
            user_id=user_id,
            provider="gemini",
            model="gemini-2.0-flash-exp",
            operation="extract_entities",
            input_tokens=len(content) // 4,
            output_tokens=500,
            cost=costs['entity_extraction'],
            document_id=document_id
        )
        
        await cost_monitor.log_usage(
            user_id=user_id,
            provider="gemini",
            model="gemini-2.0-flash-exp",
            operation="detect_relationships",
            input_tokens=len(content) // 4,
            output_tokens=150,
            cost=costs['relationship_detection'],
            document_id=document_id
        )
        
        return {
            'entities': entities,
            'relationships': relationships,
            'costs': costs
        }
        
    except Exception as e:
        logger.error(f"AI processing failed: {str(e)}")
        raise


async def store_in_review_queue(
    document_id: str,
    entities: List,
    relationships: List,
    user_id: str
):
    """
    Store extracted entities and relationships in review queue.
    
    Args:
        document_id: Document ID
        entities: List of Entity objects
        relationships: List of Relationship objects
        user_id: User ID
    """
    try:
        db = get_firestore_client(PROJECT_ID)
        
        # Store entities in review queue
        for entity in entities:
            entity_data = entity.to_dict()
            entity_data['status'] = 'pending'
            entity_data['reviewed_at'] = None
            
            db.collection('review_queue').add(entity_data)
        
        logger.info(f"Stored {len(entities)} entities in review queue")
        
        # Store relationships in review queue
        for relationship in relationships:
            rel_data = relationship.to_dict()
            rel_data['status'] = 'pending'
            rel_data['reviewed_at'] = None
            
            db.collection('review_queue').add(rel_data)
        
        logger.info(f"Stored {len(relationships)} relationships in review queue")
        
    except Exception as e:
        logger.error(f"Failed to store in review queue: {str(e)}")
        raise


async def populate_knowledge_graph(
    entities: List,
    relationships: List,
    user_id: str
) -> Dict[str, int]:
    """
    Populate Neo4j knowledge graph with entities and relationships.
    
    Args:
        entities: List of Entity objects
        relationships: List of Relationship objects
        user_id: User ID
        
    Returns:
        Dictionary with counts of created entities and relationships
    """
    try:
        logger.info("Populating knowledge graph...")
        
        graph_populator = create_graph_populator(project_id=PROJECT_ID)
        
        summary = await graph_populator.populate_from_document(
            entities=entities,
            relationships=relationships,
            user_id=user_id
        )
        
        logger.info(f"Graph populated: {summary['entities_created']} entities, "
                   f"{summary['relationships_created']} relationships")
        
        return summary
        
    except Exception as e:
        logger.error(f"Failed to populate knowledge graph: {str(e)}")
        raise


@functions_framework.http
def orchestrate(request: Request):
    """
    Process a document or note: AI extraction, review queue, and knowledge graph storage.
    
    Expected JSON payload (Mode 1 - Document):
    {
        "document_id": "firestore-doc-id",
        "user_id": "user-id"
    }
    
    Expected JSON payload (Mode 2 - Note):
    {
        "noteId": "firestore-note-id",
        "content": "note text content",
        "userId": "user-id"
    }
    """
    document_id = None
    note_id = None
    
    try:
        # Parse and validate request
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"error": "Invalid JSON payload"}), 400
        
        # Check for note mode (Sprint 4)
        note_id = data.get("noteId")
        user_id = data.get("userId") or data.get("user_id")
        
        if note_id:
            # Note mode - content is provided directly
            content = data.get("content")
            if not content or not user_id:
                return jsonify({
                    "error": "Invalid payload. Expected noteId, content, and userId"
                }), 400
            
            logger.info(f"Processing note: {note_id} for user: {user_id}")
            document_id = note_id  # Use note_id as document_id for tracking
            title = "Note"
            
        else:
            # Document mode (existing functionality)
            document_id = data.get("document_id")
            if not document_id or not user_id:
                return jsonify({
                    "error": "Invalid payload. Expected document_id and user_id OR noteId, content, and userId"
                }), 400
            
            logger.info(f"Processing document: {document_id} for user: {user_id}")
            
            # Update status to processing
            update_document_status(document_id, "processing")
            
            # Fetch document content and metadata
            try:
                content, doc_data = fetch_document_content(document_id)
                title = doc_data.get("title", "Untitled")
            except Exception as e:
                update_document_status(document_id, "failed", error=f"Failed to fetch document: {str(e)}")
                return jsonify({"error": f"Failed to fetch document: {str(e)}"}), 500
        
        # Process with AI
        try:
            # Run async AI processing
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            ai_results = loop.run_until_complete(
                process_with_ai(document_id, content, user_id)
            )
            
            entities = ai_results['entities']
            relationships = ai_results['relationships']
            costs = ai_results['costs']
            
        except Exception as e:
            logger.error(f"AI processing failed: {type(e).__name__}: {str(e)}")
            update_document_status(document_id, "failed", error=f"AI processing error: {str(e)}")
            return jsonify({"error": f"AI processing failed: {str(e)}"}), 500
        
        # Store in review queue
        try:
            loop.run_until_complete(
                store_in_review_queue(document_id, entities, relationships, user_id)
            )
        except Exception as e:
            logger.error(f"Review queue storage failed: {str(e)}")
            update_document_status(document_id, "failed", error=f"Review queue error: {str(e)}")
            return jsonify({"error": f"Review queue storage failed: {str(e)}"}), 500
        
        # Populate knowledge graph (auto-approve high confidence items)
        try:
            high_confidence_entities = [e for e in entities if e.confidence >= 0.85]
            high_confidence_relationships = [r for r in relationships if r.confidence >= 0.80]
            
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
            
            loop.close()
            
        except Exception as e:
            logger.error(f"Knowledge graph population failed: {str(e)}")
            # Don't fail the whole request - items are still in review queue
            graph_summary = {'entities_created': 0, 'relationships_created': 0}
        
        # Update status to completed
        update_document_status(
            document_id,
            "completed",
            processed_at=firestore.SERVER_TIMESTAMP,
            entities_extracted=len(entities),
            relationships_detected=len(relationships),
            entities_in_graph=graph_summary['entities_created'],
            relationships_in_graph=graph_summary['relationships_created'],
            processing_cost=costs['total']
        )
        
        response_data = {
            "success": True,
            "status": "success",
            "document_id": document_id,
            "user_id": user_id,
            "entities_extracted": len(entities),
            "relationships_detected": len(relationships),
            "entities_in_review_queue": len(entities),
            "relationships_in_review_queue": len(relationships),
            "entities_in_graph": graph_summary['entities_created'],
            "relationships_in_graph": graph_summary['relationships_created'],
            "processing_cost": costs['total'],
            "cost_breakdown": costs
        }
        
        # Add noteId for note mode
        if note_id:
            response_data["noteId"] = note_id
            response_data["extractionSummary"] = {
                "entityCount": len(entities),
                "relationshipCount": len(relationships)
            }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"Unexpected error processing document: {type(e).__name__}: {str(e)}")
        
        # Update status to failed
        if document_id:
            update_document_status(document_id, "failed", error=str(e))
        
        return jsonify({"error": f"Processing failed: {str(e)}"}), 500