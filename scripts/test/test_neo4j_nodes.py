#!/usr/bin/env python3
"""Test script to check Neo4j nodes for a user."""

import sys
sys.path.insert(0, 'shared')

from db.neo4j_client import execute_query

def check_user_nodes(user_id):
    """Check what nodes exist for a user."""
    
    # Query all nodes owned by user
    query = """
    MATCH (u:User {userId: $userId})-[:OWNS]->(n)
    RETURN n, labels(n) as types, elementId(n) as id
    LIMIT 20
    """
    
    result = execute_query(cypher=query, parameters={'userId': user_id})
    
    print(f"\n=== Nodes for user {user_id} ===")
    print(f"Found {len(result)} nodes\n")
    
    for record in result:
        node = record['n']
        types = record['types']
        node_id = record['id']
        print(f"Node ID: {node_id}")
        print(f"Types: {types}")
        print(f"Properties: {node}")
        print("-" * 50)

if __name__ == '__main__':
    user_id = '3ApRgeH5DUNGuiGG7h9Jw8Wb6dk1'  # Your user ID from the error
    check_user_nodes(user_id)