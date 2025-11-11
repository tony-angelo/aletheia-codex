"""
Graph API Cloud Function for AletheiaCodex (with Firebase Authentication).
Provides HTTP endpoints for browsing the knowledge graph.

SPRINT 6: Knowledge Graph API with proper authentication and CORS
"""

import functions_framework
from flask import Request, jsonify
import os
import sys

# Add shared directory to path
sys.path.append('/workspace')

from shared.auth.firebase_auth import require_auth
from shared.db.neo4j_client import execute_query
from shared.utils.logging import get_logger

logger = get_logger(__name__)

PROJECT_ID = os.environ.get('GCP_PROJECT', 'aletheia-codex-prod')

# CORS configuration
ALLOWED_ORIGINS = [
    'https://aletheia-codex-prod.web.app',
    'https://aletheiacodex.app',
    'http://localhost:3000'
]


def add_cors_headers(response, origin):
    """Add CORS headers to response."""
    if origin in ALLOWED_ORIGINS:
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        response.headers['Access-Control-Max-Age'] = '3600'
    return response


@functions_framework.http
@require_auth  # Require Firebase authentication
def graph_function(request: Request):
    """
    Main entry point for Graph API (authenticated).
    
    Endpoints:
    - GET / - List all nodes for user
    - GET /?nodeId={id} - Get node details
    - GET /?search=true&query={text} - Search nodes
    """
    origin = request.headers.get('Origin')
    
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        return add_cors_headers(response, origin)
    
    try:
        # Get authenticated user ID (set by @require_auth decorator)
        user_id = request.user_id
        logger.info(f"Processing graph request for user: {user_id}")
        
        # Route based on query parameters
        if request.args.get('search') == 'true':
            response = search_nodes(user_id, request)
        elif request.args.get('nodeId'):
            node_id = request.args.get('nodeId')
            response = get_node_details(user_id, node_id)
        else:
            response = get_nodes(user_id, request)
        
        return add_cors_headers(response, origin)
        
    except Exception as e:
        logger.error(f"Error in graph function: {str(e)}", exc_info=True)
        response = jsonify({'error': 'Internal server error'}), 500
        return add_cors_headers(response, origin)


def get_nodes(user_id: str, request: Request):
    """Get all nodes for user with pagination."""
    limit = int(request.args.get('limit', 50))
    offset = int(request.args.get('offset', 0))
    node_type = request.args.get('type', None)
    
    # Build query - only return nodes owned by user
    query = """
    MATCH (u:User {userId: $userId})-[:OWNS]->(n)
    """
    
    if node_type:
        query += f"WHERE '{node_type}' IN labels(n) "
    
    query += """
    RETURN n, labels(n) as types, elementId(n) as id
    ORDER BY n.createdAt DESC
    SKIP $offset
    LIMIT $limit
    """
    
    result = execute_query(
        cypher=query,
        parameters={
            'userId': user_id,
            'offset': offset,
            'limit': limit
        }
    )
    
    nodes = []
    for record in result:
        node_data = dict(record['n'])
        node_data['types'] = record['types']
        node_data['id'] = record['id']
        nodes.append(node_data)
    
    return jsonify({
        'nodes': nodes,
        'total': len(nodes),
        'offset': offset,
        'limit': limit
    })


def get_node_details(user_id: str, node_id: str):
    """Get detailed information about a specific node."""
    
    # Get node with relationships - verify user owns it
    query = """
    MATCH (u:User {userId: $userId})-[:OWNS]->(n)
    WHERE elementId(n) = $nodeId
    OPTIONAL MATCH (n)-[r]-(related)
    RETURN n, labels(n) as types, elementId(n) as id,
           collect({
               relationship: type(r),
               direction: CASE 
                   WHEN startNode(r) = n THEN 'outgoing'
                   ELSE 'incoming'
               END,
               node: related,
               nodeTypes: labels(related),
               nodeId: elementId(related)
           }) as relationships
    """
    
    result = execute_query(
        cypher=query,
        parameters={
            'userId': user_id,
            'nodeId': node_id
        }
    )
    
    if not result:
        return jsonify({'error': 'Node not found'}), 404
    
    record = result[0]
    node_data = dict(record['n'])
    node_data['types'] = record['types']
    node_data['id'] = record['id']
    node_data['relationships'] = record['relationships']
    
    return jsonify(node_data)


def search_nodes(user_id: str, request: Request):
    """Search nodes by name or properties."""
    query_text = request.args.get('query', '')
    if not query_text:
        return jsonify({'error': 'query parameter required'}), 400
    
    # Search by name (case-insensitive) - only user's nodes
    query = """
    MATCH (u:User {userId: $userId})-[:OWNS]->(n)
    WHERE toLower(n.name) CONTAINS toLower($query)
    RETURN n, labels(n) as types, elementId(n) as id
    ORDER BY n.name
    LIMIT 50
    """
    
    result = execute_query(
        cypher=query,
        parameters={
            'userId': user_id,
            'query': query_text
        }
    )
    
    nodes = []
    for record in result:
        node_data = dict(record['n'])
        node_data['types'] = record['types']
        node_data['id'] = record['id']
        nodes.append(node_data)
    
    return jsonify({
        'nodes': nodes,
        'total': len(nodes)
    })