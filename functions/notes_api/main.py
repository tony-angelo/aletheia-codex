"""
AletheiaCodex - Notes API Function (with Unified Authentication)
Handles note operations: create, list, delete, and process notes.

SPRINT 1: Updated to use unified authentication (IAP + Firebase)
Provides REST API for note management and processing.
"""

import functions_framework
from flask import Request, jsonify
from google.cloud import firestore
import os
import sys
from typing import Dict, Any
from datetime import datetime

# Add shared directory to path
sys.path.append('/workspace')

from shared.auth.unified_auth import require_auth
from shared.utils.logging import get_logger

logger = get_logger(__name__)

PROJECT_ID = os.environ.get("GCP_PROJECT", "aletheia-codex-prod")

# CORS configuration
ALLOWED_ORIGINS = [
    'https://aletheia-codex-prod.web.app',
    'http://localhost:3000'
]


def get_firestore_client():
    """Get Firestore client."""
    return firestore.Client(project=PROJECT_ID)


def add_cors_headers(response, origin):
    """Add CORS headers to response."""
    if origin in ALLOWED_ORIGINS:
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        response.headers['Access-Control-Max-Age'] = '3600'
    return response


@functions_framework.http
@require_auth  # Require Firebase authentication
def notes_api(request: Request):
    """
    Notes API endpoint (authenticated).
    
    Endpoints:
    - POST /notes/process - Process a note through AI
    - GET /notes - List user's notes
    - DELETE /notes/{note_id} - Delete a note
    """
    origin = request.headers.get('Origin')
    
    # Handle CORS preflight
    if request.method == "OPTIONS":
        response = jsonify({'status': 'ok'})
        return add_cors_headers(response, origin)
    
    try:
        # Get authenticated user ID from request (set by @require_auth)
        user_id = request.user_id
        logger.info(f"Processing notes API request for user: {user_id}")
        
        # Route based on method and path
        path = request.path
        method = request.method
        
        if method == "POST" and path.endswith("/process"):
            response = process_note(request, user_id)
        elif method == "GET":
            response = list_notes(request, user_id)
        elif method == "DELETE":
            response = delete_note(request, user_id)
        else:
            response = jsonify({"error": "Not found"}), 404
        
        return add_cors_headers(response, origin)
            
    except Exception as e:
        logger.error(f"Unexpected error: {type(e).__name__}: {str(e)}", exc_info=True)
        response = jsonify({"error": f"Internal server error: {str(e)}"}), 500
        return add_cors_headers(response, origin)


def process_note(request: Request, user_id: str):
    """
    Process a note through AI extraction.
    
    Expected payload:
    {
        "note_id": "firestore-note-id",
        "content": "note content"
    }
    """
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"error": "Invalid JSON payload"}), 400
        
        note_id = data.get("note_id")
        content = data.get("content")
        
        if not note_id or not content:
            return jsonify({
                "error": "Invalid payload. Expected note_id and content"
            }), 400
        
        logger.info(f"Processing note: {note_id} for user: {user_id}")
        
        # Update note status to processing
        db = get_firestore_client()
        note_ref = db.collection("notes").document(note_id)
        
        # Verify note belongs to user
        note_doc = note_ref.get()
        if not note_doc.exists:
            return jsonify({"error": "Note not found"}), 404
        
        note_data = note_doc.to_dict()
        if note_data.get("userId") != user_id:
            logger.warning(f"User {user_id} attempted to process note owned by {note_data.get('userId')}")
            return jsonify({"error": "Forbidden"}), 403
        
        # Update status
        note_ref.update({
            "status": "processing",
            "processingStartedAt": firestore.SERVER_TIMESTAMP,
            "updatedAt": firestore.SERVER_TIMESTAMP
        })
        
        # In production, this would trigger the orchestration function
        # For now, return success
        return jsonify({
            "success": True,
            "note_id": note_id,
            "status": "processing",
            "message": "Note processing started"
        }), 200
        
    except Exception as e:
        logger.error(f"Error processing note: {str(e)}", exc_info=True)
        return jsonify({"error": f"Failed to process note: {str(e)}"}), 500


def list_notes(request: Request, user_id: str):
    """
    List user's notes.
    
    Query parameters:
    - limit: Maximum number of notes to return (default: 50)
    - status: Filter by status (processing, completed, failed)
    - order_by: Field to order by (default: createdAt)
    - order_direction: asc or desc (default: desc)
    """
    try:
        # Parse query parameters
        limit = int(request.args.get("limit", 50))
        status = request.args.get("status")
        order_by = request.args.get("order_by", "createdAt")
        order_direction = request.args.get("order_direction", "desc")
        
        # Build query
        db = get_firestore_client()
        query = db.collection("notes").where("userId", "==", user_id)
        
        if status:
            query = query.where("status", "==", status)
        
        # Order and limit
        direction = firestore.Query.DESCENDING if order_direction == "desc" else firestore.Query.ASCENDING
        query = query.order_by(order_by, direction=direction).limit(limit)
        
        # Execute query
        notes = []
        for doc in query.stream():
            note_data = doc.to_dict()
            note_data["id"] = doc.id
            notes.append(note_data)
        
        logger.info(f"Retrieved {len(notes)} notes for user: {user_id}")
        
        return jsonify({
            "success": True,
            "notes": notes,
            "count": len(notes)
        }), 200
        
    except Exception as e:
        logger.error(f"Error listing notes: {str(e)}", exc_info=True)
        return jsonify({"error": f"Failed to list notes: {str(e)}"}), 500


def delete_note(request: Request, user_id: str):
    """
    Delete a note.
    
    Path: /notes/{note_id}
    """
    try:
        # Extract note_id from path
        path_parts = request.path.split("/")
        if len(path_parts) < 2:
            return jsonify({"error": "Invalid path"}), 400
        
        note_id = path_parts[-1]
        
        if not note_id:
            return jsonify({"error": "Note ID required"}), 400
        
        logger.info(f"Deleting note: {note_id} for user: {user_id}")
        
        # Verify note belongs to user
        db = get_firestore_client()
        note_ref = db.collection("notes").document(note_id)
        note_doc = note_ref.get()
        
        if not note_doc.exists:
            return jsonify({"error": "Note not found"}), 404
        
        note_data = note_doc.to_dict()
        if note_data.get("userId") != user_id:
            logger.warning(f"User {user_id} attempted to delete note owned by {note_data.get('userId')}")
            return jsonify({"error": "Forbidden"}), 403
        
        # Delete note
        note_ref.delete()
        
        logger.info(f"Deleted note: {note_id}")
        
        return jsonify({
            "success": True,
            "note_id": note_id,
            "message": "Note deleted successfully"
        }), 200
        
    except Exception as e:
        logger.error(f"Error deleting note: {str(e)}", exc_info=True)
        return jsonify({"error": f"Failed to delete note: {str(e)}"}), 500