"""
Neo4j client with enhanced connection management, retry logic, and monitoring.

ENHANCEMENTS:
- Exponential backoff retry logic
- Connection timeout handling
- AuraDB sleep mode detection
- Connection health monitoring
- Secret caching for performance
"""

from neo4j import GraphDatabase, Driver
from neo4j.exceptions import ServiceUnavailable, SessionExpired, TransientError
from google.cloud import secretmanager
from typing import Optional, Dict
import os
import logging
import time
from datetime import datetime, timedelta

# Configure logging
logger = logging.getLogger(__name__)

# Secret cache configuration
_secret_cache: Dict[str, tuple] = {}  # {secret_id: (value, expiry_time)}
SECRET_CACHE_TTL = 300  # 5 minutes

# Retry configuration
MAX_CONNECTION_RETRIES = 3
INITIAL_RETRY_DELAY = 2  # seconds
MAX_RETRY_DELAY = 10  # seconds
CONNECTION_TIMEOUT = 30  # seconds


def get_secret(project_id: str, secret_id: str, version: str = "latest", use_cache: bool = True) -> str:
    """
    Retrieve a secret from Secret Manager with optional caching.
    
    Args:
        project_id: GCP project ID
        secret_id: Secret name
        version: Secret version (default: latest)
        use_cache: Whether to use cached secrets (default: True)
        
    Returns:
        Secret value as string
    """
    cache_key = f"{project_id}:{secret_id}:{version}"
    
    # Check cache if enabled
    if use_cache and cache_key in _secret_cache:
        value, expiry = _secret_cache[cache_key]
        if datetime.now() < expiry:
            logger.debug(f"Using cached secret: {secret_id}")
            return value
        else:
            logger.debug(f"Cache expired for secret: {secret_id}")
            del _secret_cache[cache_key]
    
    try:
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{secret_id}/versions/{version}"
        logger.info(f"Retrieving secret: {secret_id}")
        
        response = client.access_secret_version(request={"name": name})
        # Decode and strip ALL whitespace including newlines, tabs, etc.
        secret_value = response.payload.data.decode("UTF-8").strip().replace('\n', '').replace('\r', '').replace('\t', '')
        
        # Cache the secret
        if use_cache:
            expiry = datetime.now() + timedelta(seconds=SECRET_CACHE_TTL)
            _secret_cache[cache_key] = (secret_value, expiry)
            logger.debug(f"Cached secret: {secret_id} (TTL: {SECRET_CACHE_TTL}s)")
        
        logger.info(f"Successfully retrieved secret: {secret_id} (length: {len(secret_value)})")
        return secret_value
        
    except Exception as e:
        logger.error(f"Failed to retrieve secret {secret_id}: {str(e)}")
        raise


def clear_secret_cache():
    """Clear the secret cache. Useful for testing or after secret rotation."""
    global _secret_cache
    _secret_cache.clear()
    logger.info("Secret cache cleared")


def create_neo4j_driver(project_id: str = "aletheia-codex-prod", max_retries: int = MAX_CONNECTION_RETRIES) -> Driver:
    """
    Create a new Neo4j driver instance with retry logic.
    
    This function ALWAYS creates a fresh driver to avoid caching issues.
    Implements exponential backoff for transient connection failures.
    
    Args:
        project_id: GCP project ID
        max_retries: Maximum number of connection attempts
        
    Returns:
        Initialized Neo4j driver
        
    Raises:
        Exception if connection fails after all retries
    """
    delay = INITIAL_RETRY_DELAY
    last_exception = None
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Creating Neo4j driver (attempt {attempt + 1}/{max_retries})...")
            
            # Retrieve credentials (with caching)
            uri = get_secret(project_id, "NEO4J_URI")
            user = get_secret(project_id, "NEO4J_USER")
            password = get_secret(project_id, "NEO4J_PASSWORD")
            
            # Log connection details (without sensitive data)
            logger.info(f"Connecting to Neo4j:")
            logger.info(f"  URI: {uri}")
            logger.info(f"  User: {user}")
            logger.info(f"  Password length: {len(password)}")
            
            # Ensure credentials are clean strings (no hidden characters)
            uri_clean = str(uri).strip()
            user_clean = str(user).strip()
            password_clean = str(password).strip()
            
            logger.info(f"After cleaning - URI: {len(uri_clean)}, User: {len(user_clean)}, Password: {len(password_clean)}")
            
            # Create driver with timeout configuration
            driver = GraphDatabase.driver(
                uri_clean, 
                auth=(user_clean, password_clean),
                connection_timeout=CONNECTION_TIMEOUT,
                max_connection_lifetime=3600,  # 1 hour
                max_connection_pool_size=50,
                connection_acquisition_timeout=60
            )
            
            # Verify connectivity immediately
            logger.info("Verifying Neo4j connectivity...")
            driver.verify_connectivity()
            logger.info("✓ Neo4j connection verified successfully")
            
            return driver
            
        except (ServiceUnavailable, SessionExpired, TransientError) as e:
            last_exception = e
            if attempt < max_retries - 1:
                logger.warning(
                    f"Transient connection error (attempt {attempt + 1}/{max_retries}): "
                    f"{type(e).__name__}: {str(e)}. Retrying in {delay}s..."
                )
                
                # Check if this might be AuraDB sleep mode
                if "ServiceUnavailable" in str(type(e).__name__):
                    logger.warning(
                        "This might be AuraDB free tier sleep mode. "
                        "The database may need time to wake up."
                    )
                
                time.sleep(delay)
                delay = min(delay * 2, MAX_RETRY_DELAY)  # Exponential backoff with cap
            else:
                logger.error(f"All {max_retries} connection attempts failed")
                raise
                
        except Exception as e:
            logger.error(f"Failed to create Neo4j driver: {type(e).__name__}: {str(e)}")
            raise
    
    # Should never reach here, but just in case
    if last_exception:
        raise last_exception


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


def test_connection(project_id: str = "aletheia-codex-prod") -> dict:
    """
    Test Neo4j connection and return diagnostics.
    
    Args:
        project_id: GCP project ID
        
    Returns:
        Dictionary with connection test results
    """
    result = {
        "success": False,
        "message": "",
        "details": {}
    }
    
    driver = None
    start_time = time.time()
    
    try:
        logger.info("Testing Neo4j connection...")
        driver = get_neo4j_driver(project_id)
        
        # Run a simple query
        with driver.session() as session:
            test_result = session.run("RETURN 1 as test").single()
            if test_result["test"] == 1:
                elapsed = time.time() - start_time
                result["success"] = True
                result["message"] = "Connection successful"
                result["details"] = {
                    "connection_time": f"{elapsed:.2f}s",
                    "driver_verified": True,
                    "query_executed": True
                }
                logger.info(f"✓ Connection test passed ({elapsed:.2f}s)")
            else:
                result["message"] = "Query returned unexpected result"
                
    except Exception as e:
        elapsed = time.time() - start_time
        result["message"] = f"Connection failed: {str(e)}"
        result["details"] = {
            "error_type": type(e).__name__,
            "error_message": str(e),
            "elapsed_time": f"{elapsed:.2f}s"
        }
        logger.error(f"✗ Connection test failed: {str(e)}")
        
    finally:
        if driver:
            try:
                driver.close()
            except:
                pass
    
    return result


# Context manager for better resource management
class Neo4jConnection:
    """Context manager for Neo4j connections with automatic cleanup."""
    
    def __init__(self, project_id: str = "aletheia-codex-prod"):
        self.project_id = project_id
        self.driver = None
    
    def __enter__(self) -> Driver:
        self.driver = get_neo4j_driver(self.project_id)
        return self.driver
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.driver:
            try:
                self.driver.close()
                logger.debug("Neo4j driver closed via context manager")
            except Exception as e:
                logger.error(f"Error closing driver in context manager: {str(e)}")
        return False


# Usage examples:
# 
# Example 1: Using context manager (recommended)
# with Neo4jConnection() as driver:
#     with driver.session() as session:
#         result = session.run("RETURN 1")
#
# Example 2: Manual management
# driver = get_neo4j_driver()
# try:
#     with driver.session() as session:
#         result = session.run("RETURN 1")
# finally:
#     driver.close()
#
# Example 3: Test connection
# result = test_connection()
# print(result)