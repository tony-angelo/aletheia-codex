"""
AletheiaCodex - Ingestion Function
Accepts document uploads and queues them for processing.
"""

import functions_framework
from flask import Request, jsonify
from google.cloud import firestore, storage
import sys
import os

# Import shared modules
from shared.db.firestore_client import get_firestore_client
from shared.utils.logging import get_logger

logger = get_logger("ingestion")

PROJECT_ID = os.environ.get("GCP_PROJECT", "aletheia-codex-prod")
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
        
        # Note: Cloud Tasks integration will be added in next iteration
        
        return jsonify({
            "status": "success",
            "document_id": document_id,
            "message": "Document ingested successfully"
        }), 201
        
    except Exception as e:
        logger.error(f"Error ingesting document: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500
