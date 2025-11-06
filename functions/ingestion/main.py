"""
AletheiaCodex - Ingestion Function
Accepts document uploads and queues them for processing.
"""

import functions_framework
from flask import Request, jsonify
from google.cloud import firestore, tasks_v2, storage
from datetime import datetime
import json
import sys
import os

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from shared.db.firestore_client import get_firestore_client
from shared.utils.logging import get_logger

logger = get_logger("ingestion")

PROJECT_ID = os.environ.get("GCP_PROJECT", "aletheia-codex-prod")
QUEUE_LOCATION = "us-central1"
QUEUE_NAME = "aletheia-tasks"
BUCKET_NAME = f"{PROJECT_ID}-documents"


@functions_framework.http
def ingest_document(request: Request):
    """
    HTTP endpoint to ingest a new document.
    
    Expected JSON payload:
    {
        "title": "Document Title",
        "content": "Document text content...",
        "source": "upload|url|api",
        "metadata": {
            "author": "optional",
            "tags": ["optional"]
        }
    }
    
    Returns:
        JSON response with document ID and status
    """
    try:
        # Parse request
        if request.method != "POST":
            return jsonify({"error": "Method not allowed. Use POST."}), 405
        
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"error": "Invalid JSON payload"}), 400
        
        # Validate required fields
        title = data.get("title")
        content = data.get("content")
        source = data.get("source", "api")
        
        if not title or not content:
            return jsonify({"error": "Missing required fields: title, content"}), 400
        
        logger.info(f"Ingesting document: {title} (source: {source})")
        
        # Store document metadata in Firestore
        db = get_firestore_client(PROJECT_ID)
        doc_ref = db.collection("documents").document()
        document_id = doc_ref.id
        
        doc_data = {
            "title": title,
            "source": source,
            "status": "pending",
            "created_at": firestore.SERVER_TIMESTAMP,
            "metadata": data.get("metadata", {}),
            "content_length": len(content)
        }
        
        doc_ref.set(doc_data)
        logger.info(f"Created document record: {document_id}")
        
        # Upload content to Cloud Storage
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(f"raw/{document_id}.txt")
        blob.upload_from_string(content, content_type="text/plain")
        logger.info(f"Uploaded content to gs://{BUCKET_NAME}/raw/{document_id}.txt")
        
        # Queue processing task
        queue_processing_task(document_id)
        
        return jsonify({
            "status": "success",
            "document_id": document_id,
            "message": "Document ingested and queued for processing"
        }), 201
        
    except Exception as e:
        logger.error(f"Error ingesting document: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


def queue_processing_task(document_id: str):
    """
    Queue a Cloud Task to process the document.
    
    Args:
        document_id: Firestore document ID
    """
    try:
        client = tasks_v2.CloudTasksClient()
        parent = client.queue_path(PROJECT_ID, QUEUE_LOCATION, QUEUE_NAME)
        
        # Task payload
        task_payload = {
            "document_id": document_id,
            "action": "process_document"
        }
        
        # Create the task (will call orchestration function)
        task = {
            "http_request": {
                "http_method": tasks_v2.HttpMethod.POST,
                "url": f"https://{QUEUE_LOCATION}-{PROJECT_ID}.cloudfunctions.net/orchestrate",
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(task_payload).encode()
            }
        }
        
        response = client.create_task(request={"parent": parent, "task": task})
        logger.info(f"Queued processing task: {response.name}")
        
    except Exception as e:
        logger.error(f"Error queuing task: {str(e)}")
        raise
