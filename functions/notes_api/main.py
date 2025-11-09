"""
AletheiaCodex - Notes API Function
Handles note operations: create, list, delete, and process notes.

SPRINT 4: Note Input & AI Processing
Provides REST API for note management and processing.
"""

import functions_framework
from flask import Request, jsonify
from google.cloud import firestore
from firebase_admin import auth, initialize_app
import os
from typing import Optional, Dict, Any
from datetime import datetime

import logging

logger = logging.getLogger("notes_api")
logger.setLevel(logging.INFO)

# Initialize Firebase Admin
try:
    initialize_app()
except ValueError:
    # Already initialized
    pass

PROJECT_ID = os.environ.get("GCP_PROJECT", "aletheia-codex-prod")


def get_firestore_client():
    """Get Firestore client."""
    return firestore.Client(project=PROJECT_ID)


def verify_user_auth(request: Request) -> Optional[str]:
    """
    Verify user authentication from Firebase Auth token.
    
    Args:
        request: Flask request object
        
    Returns:
        User ID if authenticated, None otherwise
    """
    auth_header = request.headers.get("Authorization", "")
    
    if not auth_header.startswith("Bearer "):
        return None
    
    token = auth_header.replace("Bearer ", "")
    
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token['uid']
    except Exception as e:
        logger.error(f"Token verification failed: {str(e)}")
        return None


@functions_framework.http
def notes_api(request: Request):
    """
    Notes API endpoint.
    
    Endpoints:
    - POST /notes/process - Process a note through AI
    - GET /notes - List user's notes
    - DELETE /notes/{note_id} - Delete a note
    """
    
    # Enable CORS
    if request.method == "OPTIONS":
        headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
            "Access-Control-Max-Age": "3600"
        }
        return ("", 204, headers)
    
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Content-Type": "application/json"
    }
    
    try:
        # Verify authentication
        user_id = verify_user_auth(request)
        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401, headers
        
        # Route based on method and path
        path = request.path
        method = request.method
        
        if method == "POST" and path.endswith("/process"):
            return process_note(request, user_id, headers)
        elif method == "GET":
            return list_notes(request, user_id, headers)
        elif method == "DELETE":
            return delete_note(request, user_id, headers)
        else:
            return jsonify({"error": "Not found"}), 404, headers
            
    except Exception as e:
        logger.error(f"Unexpected error: {type(e).__name__}: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500, headers


def process_note(request: Request, user_id: str, headers: Dict[str, str]):
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
            return jsonify({"error": "Invalid JSON payload"}), 400, headers
        
        note_id = data.get("note_id")
        content = data.get("content")
        
        if not note_id or not content:
            return jsonify({
                "error": "Invalid payload. Expected note_id and content"
            }), 400, headers
        
        logger.info(f"Processing note: {note_id} for user: {user_id}")
        
        # Update note status to processing
        db = get_firestore_client()
        note_ref = db.collection("notes").document(note_id)
        
        # Verify note belongs to user
        note_doc = note_ref.get()
        if not note_doc.exists:
            return jsonify({"error": "Note not found"}), 404, headers
        
        note_data = note_doc.to_dict()
        if note_data.get("userId") != user_id:
            return jsonify({"error": "Forbidden"}), 403, headers
        
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
        }), 200, headers
        
    except Exception as e:
        logger.error(f"Error processing note: {str(e)}")
        return jsonify({"error": f"Failed to process note: {str(e)}"}), 500, headers


def list_notes(request: Request, user_id: str, headers: Dict[str, str]):
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
        }), 200, headers
        
    except Exception as e:
        logger.error(f"Error listing notes: {str(e)}")
        return jsonify({"error": f"Failed to list notes: {str(e)}"}), 500, headers


def delete_note(request: Request, user_id: str, headers: Dict[str, str]):
    """
    Delete a note.
    
    Path: /notes/{note_id}
    """
    try:
        # Extract note_id from path
        path_parts = request.path.split("/")
        if len(path_parts) < 2:
            return jsonify({"error": "Invalid path"}), 400, headers
        
        note_id = path_parts[-1]
        
        if not note_id:
            return jsonify({"error": "Note ID required"}), 400, headers
        
        logger.info(f"Deleting note: {note_id} for user: {user_id}")
        
        # Verify note belongs to user
        db = get_firestore_client()
        note_ref = db.collection("notes").document(note_id)
        note_doc = note_ref.get()
        
        if not note_doc.exists:
            return jsonify({"error": "Note not found"}), 404, headers
        
        note_data = note_doc.to_dict()
        if note_data.get("userId") != user_id:
            return jsonify({"error": "Forbidden"}), 403, headers
        
        # Delete note
        note_ref.delete()
        
        logger.info(f"Deleted note: {note_id}")
        
        return jsonify({
            "success": True,
            "note_id": note_id,
            "message": "Note deleted successfully"
        }), 200, headers
        
    except Exception as e:
        logger.error(f"Error deleting note: {str(e)}")
        return jsonify({"error": f"Failed to delete note: {str(e)}"}), 500, headers