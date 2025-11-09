"""
AletheiaCodex - Orchestration Function (HTTP API)
Processes documents: chunking, embedding, and knowledge graph storage.

UPDATED: Now uses Neo4j HTTP API instead of Bolt protocol to avoid
Cloud Run's gRPC proxy incompatibility.

FEATURES:
- HTTP API for Neo4j connectivity
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

from shared.db.firestore_client import get_firestore_client
from shared.db.neo4j_client import (
    create_neo4j_http_client,
    execute_neo4j_query_http
)
from shared.ai.gemini_client import generate_embeddings
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


def process_chunks_to_neo4j(
    document_id: str, 
    title: str, 
    chunks: List[Dict[str, Any]], 
    client: Dict[str, str]
):
    """
    Process and store chunks in Neo4j using HTTP API.
    
    Args:
        document_id: Document ID
        title: Document title
        chunks: List of text chunks
        client: Neo4j HTTP client configuration
    """
    def create_document_node():
        """Create document node in Neo4j."""
        execute_neo4j_query_http(
            client['uri'],
            client['user'],
            client['password'],
            """
            MERGE (d:Document {id: $doc_id})
            SET d.title = $title,
                d.created_at = datetime(),
                d.chunk_count = $chunk_count
            """,
            {
                "doc_id": document_id,
                "title": title,
                "chunk_count": len(chunks)
            }
        )
        logger.info(f"Created document node: {document_id}")
    
    # Create document node with retry
    retry_with_backoff(create_document_node)
    
    # Process each chunk
    for idx, chunk in enumerate(chunks):
        text = chunk['text']
        
        # Generate embedding
        logger.info(f"Generating embedding for chunk {idx + 1}/{len(chunks)}")
        embedding = generate_embeddings(text)
        
        # Store chunk with retry
        def store_chunk():
            execute_neo4j_query_http(
                client['uri'],
                client['user'],
                client['password'],
                """
                MATCH (d:Document {id: $doc_id})
                CREATE (c:Chunk {
                    id: $chunk_id,
                    text: $text,
                    position: $position,
                    length: $length,
                    embedding: $embedding
                })
                CREATE (d)-[:HAS_CHUNK {position: $position}]->(c)
                """,
                {
                    "doc_id": document_id,
                    "chunk_id": f"{document_id}_chunk_{idx}",
                    "text": text,
                    "position": idx,
                    "length": chunk['length'],
                    "embedding": embedding
                }
            )
        
        retry_with_backoff(store_chunk)
        logger.info(f"Stored chunk {idx + 1}/{len(chunks)}")


@functions_framework.http
def orchestrate(request: Request):
    """
    Process a document: fetch, chunk, embed, and store in Neo4j.
    
    Expected JSON payload:
    {
        "document_id": "firestore-doc-id",
        "action": "process_document"
    }
    """
    document_id = None
    
    try:
        # Parse and validate request
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"error": "Invalid JSON payload"}), 400
        
        document_id = data.get("document_id")
        action = data.get("action")
        
        if not document_id or action != "process_document":
            return jsonify({
                "error": "Invalid payload. Expected document_id and action=process_document"
            }), 400
        
        logger.info(f"Processing document: {document_id}")
        
        # Update status to processing
        update_document_status(document_id, "processing")
        
        # Fetch document content and metadata
        try:
            content, doc_data = fetch_document_content(document_id)
            title = doc_data.get("title", "Untitled")
        except Exception as e:
            update_document_status(document_id, "failed", error=f"Failed to fetch document: {str(e)}")
            return jsonify({"error": f"Failed to fetch document: {str(e)}"}), 500
        
        # Chunk the text
        try:
            chunks = chunk_text(content, chunk_size=500, overlap=50)
            logger.info(f"Created {len(chunks)} chunks")
        except Exception as e:
            update_document_status(document_id, "failed", error=f"Failed to chunk text: {str(e)}")
            return jsonify({"error": f"Failed to chunk text: {str(e)}"}), 500
        
        # Process with Neo4j HTTP API
        try:
            logger.info("Creating Neo4j HTTP client...")
            client = create_neo4j_http_client(PROJECT_ID)
            
            # Process chunks to Neo4j
            process_chunks_to_neo4j(document_id, title, chunks, client)
            
            logger.info(f"Successfully stored {len(chunks)} chunks in Neo4j")
            
        except Exception as e:
            logger.error(f"Neo4j processing failed: {type(e).__name__}: {str(e)}")
            update_document_status(document_id, "failed", error=f"Neo4j error: {str(e)}")
            return jsonify({"error": f"Neo4j processing failed: {str(e)}"}), 500
        
        # Update status to completed
        update_document_status(
            document_id,
            "completed",
            processed_at=firestore.SERVER_TIMESTAMP,
            chunk_count=len(chunks)
        )
        
        return jsonify({
            "status": "success",
            "document_id": document_id,
            "chunks_processed": len(chunks),
            "api_type": "HTTP"
        }), 200
        
    except Exception as e:
        logger.error(f"Unexpected error processing document: {type(e).__name__}: {str(e)}")
        
        # Update status to failed
        if document_id:
            update_document_status(document_id, "failed", error=str(e))
        
        return jsonify({"error": f"Processing failed: {str(e)}"}), 500