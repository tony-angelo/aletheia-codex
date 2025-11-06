"""Neo4j client with automatic secret retrieval and connection management."""

from neo4j import GraphDatabase, Driver
from google.cloud import secretmanager
from typing import Optional
import os

_driver: Optional[Driver] = None


def get_secret(project_id: str, secret_id: str, version: str = "latest") -> str:
    """
    Retrieve a secret from Secret Manager.
    
    Args:
        project_id: GCP project ID
        secret_id: Secret name
        version: Secret version (default: latest)
        
    Returns:
        Secret value as string
    """
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version}"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")


def get_neo4j_driver(project_id: str = "aletheia-codex-prod") -> Driver:
    """
    Get or create a Neo4j driver (singleton pattern).
    
    Retrieves credentials from Secret Manager automatically.
    
    Args:
        project_id: GCP project ID
        
    Returns:
        Initialized Neo4j driver
    """
    global _driver
    if _driver is None:
        uri = get_secret(project_id, "NEO4J_URI")
        user = get_secret(project_id, "NEO4J_USER")
        password = get_secret(project_id, "NEO4J_PASSWORD")
        _driver = GraphDatabase.driver(uri, auth=(user, password))
    return _driver


def close_neo4j_driver():
    """Close the Neo4j driver connection."""
    global _driver
    if _driver is not None:
        _driver.close()
        _driver = None


def execute_query(cypher: str, parameters: dict = None) -> list:
    """
    Execute a Cypher query and return results.
    
    Args:
        cypher: Cypher query string
        parameters: Query parameters (optional)
        
    Returns:
        List of result records
    """
    driver = get_neo4j_driver()
    with driver.session() as session:
        result = session.run(cypher, parameters or {})
        return [record.data() for record in result]
