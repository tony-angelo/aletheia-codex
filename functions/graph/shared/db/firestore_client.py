"""Firestore client with automatic initialization."""

from google.cloud import firestore
from typing import Optional

_client: Optional[firestore.Client] = None


def get_firestore_client(project_id: str = "aletheia-codex-prod") -> firestore.Client:
    """
    Get or create a Firestore client (singleton pattern).
    
    Args:
        project_id: GCP project ID
        
    Returns:
        Initialized Firestore client
    """
    global _client
    if _client is None:
        _client = firestore.Client(project=project_id)
    return _client


def get_collection(collection_name: str) -> firestore.CollectionReference:
    """
    Get a Firestore collection reference.
    
    Args:
        collection_name: Name of the collection
        
    Returns:
        Collection reference
    """
    client = get_firestore_client()
    return client.collection(collection_name)
