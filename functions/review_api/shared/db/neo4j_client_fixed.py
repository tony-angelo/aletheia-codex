"""Neo4j client with improved connection management and debugging.

This version addresses potential caching issues and adds comprehensive logging.
"""

from neo4j import GraphDatabase, Driver
from google.cloud import secretmanager
from typing import Optional
import os
import logging

# Configure logging
logger = logging.getLogger(__name__)


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
    try:
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{secret_id}/versions/{version}"
        logger.info(f"Retrieving secret: {secret_id}")
        response = client.access_secret_version(request={"name": name})
        secret_value = response.payload.data.decode("UTF-8").strip()
        logger.info(f"Successfully retrieved secret: {secret_id} (length: {len(secret_value)})")
        return secret_value
    except Exception as e:
        logger.error(f"Failed to retrieve secret {secret_id}: {str(e)}")
        raise


def create_neo4j_driver(project_id: str = "aletheia-codex-prod") -> Driver:
    """
    Create a new Neo4j driver instance.
    
    This function ALWAYS creates a fresh driver to avoid caching issues.
    
    Args:
        project_id: GCP project ID
        
    Returns:
        Initialized Neo4j driver
    """
    try:
        print("=== FIXED CODE IS RUNNING ==="); print("=== CREATING NEW NEO4J DRIVER ===")
        
        # Retrieve credentials
        uri = get_secret(project_id, "NEO4J_URI")
        user = get_secret(project_id, "NEO4J_USER")
        password = get_secret(project_id, "NEO4J_PASSWORD")
        
        # Log connection details (without sensitive data)
        logger.info(f"Connecting to Neo4j:")
        logger.info(f"  URI: {uri}")
        logger.info(f"  User: {user}")
        logger.info(f"  Password length: {len(password)}")
        
        # Create driver
        driver = GraphDatabase.driver(uri, auth=(user, password))
        
        # Verify connectivity immediately
        logger.info("Verifying Neo4j connectivity...")
        driver.verify_connectivity()
        logger.info("✓ Neo4j connection verified successfully")
        
        return driver
        
    except Exception as e:
        logger.error(f"Failed to create Neo4j driver: {type(e).__name__}: {str(e)}")
        raise


def get_neo4j_driver(project_id: str = "aletheia-codex-prod") -> Driver:
    """
    Get a Neo4j driver instance.
    
    NOTE: This creates a NEW driver on each call to avoid caching issues.
    Caller is responsible for closing the driver when done.
    
    Args:
        project_id: GCP project ID
        
    Returns:
        Initialized Neo4j driver
    """
    return create_neo4j_driver(project_id)


def execute_query(cypher: str, parameters: dict = None, project_id: str = "aletheia-codex-prod") -> list:
    """
    Execute a Cypher query and return results.
    
    This function manages the driver lifecycle automatically.
    
    Args:
        cypher: Cypher query string
        parameters: Query parameters (optional)
        project_id: GCP project ID
        
    Returns:
        List of result records
    """
    driver = None
    try:
        driver = get_neo4j_driver(project_id)
        with driver.session() as session:
            result = session.run(cypher, parameters or {})
            return [record.data() for record in result]
    finally:
        if driver:
            driver.close()


# Context manager for better resource management
class Neo4jConnection:
    """Context manager for Neo4j connections."""
    
    def __init__(self, project_id: str = "aletheia-codex-prod"):
        self.project_id = project_id
        self.driver = None
    
    def __enter__(self) -> Driver:
        self.driver = get_neo4j_driver(self.project_id)
        return self.driver
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.driver:
            self.driver.close()
        return False


# Usage example:
# with Neo4jConnection() as driver:
#     with driver.session() as session:
#         result = session.run("RETURN 1")
