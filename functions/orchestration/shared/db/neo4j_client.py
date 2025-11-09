"""
Neo4j HTTP API client for AletheiaCodex.

This implementation uses Neo4j's HTTP API instead of the Bolt protocol
to avoid Cloud Run's gRPC proxy incompatibility issues.

RATIONALE:
- Cloud Run's gRPC proxy is incompatible with Neo4j's Bolt protocol
- HTTP API bypasses gRPC entirely while maintaining security (HTTPS/TLS)
- Officially supported by Neo4j as a standard workaround
- Trade-off: Slightly slower (~50-100ms overhead) but reliable

FEATURES:
- Exponential backoff retry logic
- Connection timeout handling
- Comprehensive error handling
- Secret caching for performance
- Detailed logging
"""

import requests
from google.cloud import secretmanager
from typing import Optional, Dict, Any, List
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
REQUEST_TIMEOUT = 30  # seconds


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


def convert_uri_to_http(uri: str) -> str:
    """
    Convert Neo4j Bolt URI to HTTP endpoint.
    
    Args:
        uri: Neo4j URI (e.g., neo4j+s://xxx.databases.neo4j.io:7687)
        
    Returns:
        HTTP endpoint URL (e.g., https://xxx.databases.neo4j.io)
    """
    # Convert neo4j+s:// to https://
    if uri.startswith('neo4j+s://'):
        http_uri = uri.replace('neo4j+s://', 'https://')
    elif uri.startswith('neo4j://'):
        http_uri = uri.replace('neo4j://', 'http://')
    else:
        http_uri = uri
    
    # Remove port if present (HTTP API uses standard HTTPS port)
    if ':7687' in http_uri:
        http_uri = http_uri.replace(':7687', '')
    
    return http_uri


def execute_neo4j_query_http(
    uri: str,
    user: str,
    password: str,
    query: str,
    parameters: Dict[str, Any] = None,
    database: str = "neo4j",
    max_retries: int = MAX_CONNECTION_RETRIES
) -> Dict[str, Any]:
    """
    Execute Cypher query via Neo4j HTTP API.
    
    Args:
        uri: Neo4j URI (will be converted to HTTPS)
        user: Neo4j username
        password: Neo4j password
        query: Cypher query string
        parameters: Query parameters
        database: Database name (default: neo4j)
        max_retries: Maximum retry attempts
        
    Returns:
        Query results as dictionary
        
    Raises:
        Exception if query fails after all retries
    """
    # Convert URI to HTTP endpoint
    http_uri = convert_uri_to_http(uri)
    
    # Build endpoint URL - using Query API v2 (Aura compatible)
    endpoint = f"{http_uri}/db/{database}/query/v2"
    
    # Prepare request payload for Query API v2
    payload = {
        "statement": query,
        "parameters": parameters or {}
    }
    
    # Execute request with retry logic
    delay = INITIAL_RETRY_DELAY
    last_exception = None
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Executing Neo4j HTTP query (attempt {attempt + 1}/{max_retries})")
            logger.debug(f"Endpoint: {endpoint}")
            logger.debug(f"Query: {query[:100]}...")  # Log first 100 chars
            
            response = requests.post(
                endpoint,
                auth=(user, password),
                json=payload,
                timeout=REQUEST_TIMEOUT,
                headers={'Content-Type': 'application/json'}
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Check for Neo4j errors in response (Query API v2 format)
            if 'errors' in result and result['errors']:
                error_msg = result['errors'][0].get('message', 'Unknown error')
                error_code = result['errors'][0].get('code', 'Unknown code')
                raise Exception(f"Neo4j query error [{error_code}]: {error_msg}")
            
            logger.info("✓ Neo4j HTTP query executed successfully")
            
            # Transform Query API v2 response to match expected format
            # Query API v2 returns: {"data": {"fields": [...], "values": [[...]]}}
            # We need to transform to: {"results": [{"data": [{"row": [...]}]}]}
            if 'data' in result:
                transformed = {
                    "results": [{
                        "data": [
                            {"row": row} for row in result['data'].get('values', [])
                        ]
                    }]
                }
                return transformed
            
            return result
            
        except requests.exceptions.Timeout as e:
            last_exception = e
            logger.error(f"Request timeout (attempt {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                logger.warning(f"Retrying in {delay}s...")
                time.sleep(delay)
                delay = min(delay * 2, MAX_RETRY_DELAY)
            else:
                raise Exception(f"Query failed after {max_retries} attempts: Timeout")
                
        except requests.exceptions.HTTPError as e:
            last_exception = e
            status_code = e.response.status_code if e.response else 'unknown'
            logger.error(f"HTTP error {status_code} (attempt {attempt + 1}): {e}")
            
            # Don't retry on authentication errors (401) or bad requests (400)
            if status_code in [400, 401, 403]:
                raise Exception(f"HTTP {status_code}: {e}")
            
            if attempt < max_retries - 1:
                logger.warning(f"Retrying in {delay}s...")
                time.sleep(delay)
                delay = min(delay * 2, MAX_RETRY_DELAY)
            else:
                raise Exception(f"Query failed after {max_retries} attempts: HTTP {status_code}")
                
        except requests.exceptions.RequestException as e:
            last_exception = e
            logger.error(f"HTTP request failed (attempt {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                logger.warning(f"Retrying in {delay}s...")
                time.sleep(delay)
                delay = min(delay * 2, MAX_RETRY_DELAY)
            else:
                raise Exception(f"Query failed after {max_retries} attempts: {e}")
    
    # Should never reach here, but just in case
    if last_exception:
        raise last_exception
    raise Exception("Max retries exceeded")


def create_neo4j_http_client(project_id: str = "aletheia-codex-prod") -> Dict[str, str]:
    """
    Create Neo4j HTTP client configuration.
    
    Args:
        project_id: GCP project ID
        
    Returns:
        Dictionary with uri, user, password
    """
    try:
        uri = get_secret(project_id, "NEO4J_URI")
        user = get_secret(project_id, "NEO4J_USER")
        password = get_secret(project_id, "NEO4J_PASSWORD")
        
        logger.info(f"Created Neo4j HTTP client configuration")
        logger.info(f"  URI: {uri}")
        logger.info(f"  User: {user}")
        logger.info(f"  Password length: {len(password)}")
        
        return {
            'uri': uri,
            'user': user,
            'password': password
        }
    except Exception as e:
        logger.error(f"Failed to create Neo4j HTTP client: {e}")
        raise


def execute_query(
    cypher: str, 
    parameters: dict = None, 
    project_id: str = "aletheia-codex-prod"
) -> List[Dict[str, Any]]:
    """
    Execute a Cypher query and return results.
    
    This is a convenience function that manages client configuration automatically.
    
    Args:
        cypher: Cypher query string
        parameters: Query parameters (optional)
        project_id: GCP project ID
        
    Returns:
        List of result records
    """
    try:
        client = create_neo4j_http_client(project_id)
        result = execute_neo4j_query_http(
            client['uri'],
            client['user'],
            client['password'],
            cypher,
            parameters
        )
        
        # Extract records from HTTP response
        records = []
        if 'results' in result and result['results']:
            for row in result['results'][0].get('data', []):
                # Extract the row data
                if 'row' in row and row['row']:
                    records.append(row['row'][0] if len(row['row']) == 1 else row['row'])
        
        return records
        
    except Exception as e:
        logger.error(f"Query execution failed: {e}")
        raise


def test_connection(project_id: str = "aletheia-codex-prod") -> dict:
    """
    Test Neo4j HTTP API connection and return diagnostics.
    
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
    
    start_time = time.time()
    
    try:
        logger.info("Testing Neo4j HTTP API connection...")
        client = create_neo4j_http_client(project_id)
        
        # Run a simple query
        query_result = execute_neo4j_query_http(
            client['uri'],
            client['user'],
            client['password'],
            "RETURN 1 as test"
        )
        
        # Verify result structure
        if 'results' in query_result and query_result['results']:
            data = query_result['results'][0]['data']
            if data and data[0]['row'][0] == 1:
                elapsed = time.time() - start_time
                result["success"] = True
                result["message"] = "Connection successful"
                result["details"] = {
                    "connection_time": f"{elapsed:.2f}s",
                    "api_type": "HTTP",
                    "query_executed": True,
                    "endpoint": convert_uri_to_http(client['uri'])
                }
                logger.info(f"✓ Connection test passed ({elapsed:.2f}s)")
            else:
                result["message"] = "Query returned unexpected result"
        else:
            result["message"] = "Invalid response structure"
            
    except Exception as e:
        elapsed = time.time() - start_time
        result["message"] = f"Connection failed: {str(e)}"
        result["details"] = {
            "error_type": type(e).__name__,
            "error_message": str(e),
            "elapsed_time": f"{elapsed:.2f}s"
        }
        logger.error(f"✗ Connection test failed: {str(e)}")
    
    return result


# Context manager for better resource management
class Neo4jHTTPConnection:
    """Context manager for Neo4j HTTP connections."""
    
    def __init__(self, project_id: str = "aletheia-codex-prod"):
        self.project_id = project_id
        self.client = None
    
    def __enter__(self) -> Dict[str, str]:
        self.client = create_neo4j_http_client(self.project_id)
        return self.client
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # HTTP connections don't need explicit cleanup
        logger.debug("Neo4j HTTP connection context closed")
        return False


# Usage examples:
# 
# Example 1: Using context manager (recommended)
# with Neo4jHTTPConnection() as client:
#     result = execute_neo4j_query_http(
#         client['uri'],
#         client['user'],
#         client['password'],
#         "RETURN 1"
#     )
#
# Example 2: Direct execution
# client = create_neo4j_http_client()
# result = execute_neo4j_query_http(
#     client['uri'],
#     client['user'],
#     client['password'],
#     "MATCH (n:User) RETURN n LIMIT 1"
# )
#
# Example 3: Convenience function
# records = execute_query("MATCH (n:User) RETURN n LIMIT 1")
#
# Example 4: Test connection
# result = test_connection()
# print(result)