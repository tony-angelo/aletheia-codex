import functions_framework
from flask import jsonify, request
from shared.db.neo4j_client import execute_query
import logging

logger = logging.getLogger(__name__)

@functions_framework.http
def graph_function(request):
    """HTTP Cloud Function for graph operations."""
    
    # CORS headers
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        }
        return ('', 204, headers)
    
    headers = {'Access-Control-Allow-Origin': '*'}
    
    try:
        # Get user ID from request
        user_id = request.args.get('userId')
        if not user_id:
            return (jsonify({'error': 'userId required'}), 400, headers)
        
        # Route based on query parameters
        if request.args.get('search') == 'true':
            return search_nodes(user_id, request, headers)
        elif request.args.get('nodeId'):
            node_id = request.args.get('nodeId')
            return get_node_details(user_id, node_id, headers)
        else:
            return get_nodes(user_id, request, headers)
            
    except Exception as e:
        logger.error(f"Graph function error: {str(e)}", exc_info=True)
        return (jsonify({'error': str(e)}), 500, headers)

def get_nodes(user_id: str, request, headers):
    """Get list of nodes for user."""
    limit = int(request.args.get('limit', 50))
    offset = int(request.args.get('offset', 0))
    node_type = request.args.get('type')  # Optional filter by type
    
    # Build query
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
        query=query,
        parameters={
            'userId': user_id,
            'offset': offset,
            'limit': limit
        }
    )
    
    nodes = []
    for record in result.get('data', []):
        node_data = dict(record['n'])
        node_data['types'] = record['types']
        node_data['id'] = record['id']
        nodes.append(node_data)
    
    return (jsonify({'nodes': nodes, 'total': len(nodes)}), 200, headers)

def get_node_details(user_id: str, node_id: str, headers):
    """Get detailed information about a node."""
    
    # Get node with relationships
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
        query=query,
        parameters={
            'userId': user_id,
            'nodeId': node_id
        }
    )
    
    if not result.get('data'):
        return (jsonify({'error': 'Node not found'}), 404, headers)
    
    record = result['data'][0]
    node_data = dict(record['n'])
    node_data['types'] = record['types']
    node_data['id'] = record['id']
    
    # Filter out null relationships
    relationships = [r for r in record['relationships'] if r['node'] is not None]
    for rel in relationships:
        if rel['node']:
            rel['node'] = dict(rel['node'])
    
    node_data['relationships'] = relationships
    
    return (jsonify(node_data), 200, headers)

def search_nodes(user_id: str, request, headers):
    """Search nodes by name or properties."""
    query_text = request.args.get('query', '')
    if not query_text:
        return (jsonify({'error': 'query parameter required'}), 400, headers)
    
    # Search by name (case-insensitive)
    query = """
    MATCH (u:User {userId: $userId})-[:OWNS]->(n)
    WHERE toLower(n.name) CONTAINS toLower($query)
    RETURN n, labels(n) as types, elementId(n) as id
    ORDER BY n.name
    LIMIT 50
    """
    
    result = execute_query(
        query=query,
        parameters={
            'userId': user_id,
            'query': query_text
        }
    )
    
    nodes = []
    for record in result.get('data', []):
        node_data = dict(record['n'])
        node_data['types'] = record['types']
        node_data['id'] = record['id']
        nodes.append(node_data)
    
    return (jsonify({'nodes': nodes, 'total': len(nodes)}), 200, headers)