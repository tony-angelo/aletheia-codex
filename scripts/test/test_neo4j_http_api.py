#!/usr/bin/env python3
"""
Test Neo4j HTTP API connection and queries.

This test suite verifies that the HTTP API implementation works correctly
and can connect to Neo4j Aura without gRPC issues.
"""

import sys
import os

# Add shared directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'shared'))

from db.neo4j_client import (
    create_neo4j_http_client,
    execute_neo4j_query_http,
    execute_query,
    test_connection,
    convert_uri_to_http
)

def print_header(title):
    """Print a formatted test header."""
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)

def test_uri_conversion():
    """Test URI conversion from Bolt to HTTP."""
    print_header("Test 1: URI Conversion")
    
    test_cases = [
        ("neo4j+s://abc123.databases.neo4j.io:7687", "https://abc123.databases.neo4j.io"),
        ("neo4j://localhost:7687", "http://localhost"),
        ("https://example.com", "https://example.com"),
    ]
    
    all_passed = True
    for bolt_uri, expected_http in test_cases:
        result = convert_uri_to_http(bolt_uri)
        if result == expected_http:
            print(f"✓ {bolt_uri} → {result}")
        else:
            print(f"✗ {bolt_uri} → {result} (expected: {expected_http})")
            all_passed = False
    
    return all_passed

def test_client_creation():
    """Test Neo4j HTTP client creation."""
    print_header("Test 2: Client Creation")
    
    try:
        client = create_neo4j_http_client()
        print(f"✓ Client created successfully")
        print(f"   URI: {client['uri']}")
        print(f"   User: {client['user']}")
        print(f"   Password length: {len(client['password'])}")
        print(f"   HTTP endpoint: {convert_uri_to_http(client['uri'])}")
        return True
    except Exception as e:
        print(f"✗ Client creation failed: {e}")
        return False

def test_simple_query():
    """Test simple query execution."""
    print_header("Test 3: Simple Query (RETURN 1)")
    
    try:
        client = create_neo4j_http_client()
        result = execute_neo4j_query_http(
            client['uri'],
            client['user'],
            client['password'],
            "RETURN 1 as num"
        )
        
        print(f"✓ Query executed successfully")
        print(f"   Response structure: {list(result.keys())}")
        
        # Verify result structure
        if 'results' in result and result['results']:
            data = result['results'][0]['data']
            if data and data[0]['row'][0] == 1:
                print(f"✓ Result validation passed")
                print(f"   Value: {data[0]['row'][0]}")
                return True
        
        print(f"✗ Result validation failed")
        print(f"   Result: {result}")
        return False
        
    except Exception as e:
        print(f"✗ Query failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_parameterized_query():
    """Test parameterized query."""
    print_header("Test 4: Parameterized Query")
    
    try:
        client = create_neo4j_http_client()
        result = execute_neo4j_query_http(
            client['uri'],
            client['user'],
            client['password'],
            "RETURN $value as result",
            {"value": "test-value-123"}
        )
        
        print(f"✓ Parameterized query executed successfully")
        
        # Verify result
        if 'results' in result and result['results']:
            data = result['results'][0]['data']
            if data and data[0]['row'][0] == "test-value-123":
                print(f"✓ Parameter substitution verified")
                print(f"   Value: {data[0]['row'][0]}")
                return True
        
        print(f"✗ Parameter verification failed")
        return False
        
    except Exception as e:
        print(f"✗ Parameterized query failed: {e}")
        return False

def test_convenience_function():
    """Test convenience execute_query function."""
    print_header("Test 5: Convenience Function")
    
    try:
        records = execute_query("RETURN 42 as answer, 'hello' as greeting")
        print(f"✓ Convenience function executed successfully")
        print(f"   Records: {records}")
        
        if records and len(records) > 0:
            print(f"✓ Records extracted correctly")
            return True
        else:
            print(f"✗ No records returned")
            return False
        
    except Exception as e:
        print(f"✗ Convenience function failed: {e}")
        return False

def test_connection_diagnostics():
    """Test connection diagnostics function."""
    print_header("Test 6: Connection Diagnostics")
    
    try:
        result = test_connection()
        print(f"Connection test result:")
        print(f"   Success: {result['success']}")
        print(f"   Message: {result['message']}")
        print(f"   Details: {result['details']}")
        
        return result['success']
        
    except Exception as e:
        print(f"✗ Connection diagnostics failed: {e}")
        return False

def test_multi_row_query():
    """Test query returning multiple rows."""
    print_header("Test 7: Multi-Row Query")
    
    try:
        client = create_neo4j_http_client()
        result = execute_neo4j_query_http(
            client['uri'],
            client['user'],
            client['password'],
            "UNWIND range(1, 5) as num RETURN num"
        )
        
        print(f"✓ Multi-row query executed successfully")
        
        # Verify result
        if 'results' in result and result['results']:
            data = result['results'][0]['data']
            if len(data) == 5:
                print(f"✓ Correct number of rows returned: {len(data)}")
                print(f"   Values: {[row['row'][0] for row in data]}")
                return True
            else:
                print(f"✗ Expected 5 rows, got {len(data)}")
                return False
        
        print(f"✗ Invalid result structure")
        return False
        
    except Exception as e:
        print(f"✗ Multi-row query failed: {e}")
        return False

def test_error_handling():
    """Test error handling with invalid query."""
    print_header("Test 8: Error Handling")
    
    try:
        client = create_neo4j_http_client()
        result = execute_neo4j_query_http(
            client['uri'],
            client['user'],
            client['password'],
            "INVALID CYPHER QUERY"
        )
        
        print(f"✗ Expected error but query succeeded")
        return False
        
    except Exception as e:
        print(f"✓ Error handling works correctly")
        print(f"   Error: {str(e)[:100]}...")
        return True

def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("Neo4j HTTP API Test Suite")
    print("=" * 60)
    print("\nThis test suite verifies the HTTP API implementation")
    print("and ensures Cloud Run compatibility (no gRPC issues).\n")
    
    tests = [
        ("URI Conversion", test_uri_conversion),
        ("Client Creation", test_client_creation),
        ("Simple Query", test_simple_query),
        ("Parameterized Query", test_parameterized_query),
        ("Convenience Function", test_convenience_function),
        ("Connection Diagnostics", test_connection_diagnostics),
        ("Multi-Row Query", test_multi_row_query),
        ("Error Handling", test_error_handling),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            results.append((name, test_func()))
        except Exception as e:
            print(f"\n✗ Test '{name}' crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # Print summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {name}")
    
    print("\n" + "-" * 60)
    total = len(results)
    passed = sum(1 for _, p in results if p)
    failed = total - passed
    
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if all(p for _, p in results):
        print("\n✓ All tests passed! HTTP API is working correctly.")
        print("  Ready for Cloud Run deployment.")
        return 0
    else:
        print("\n✗ Some tests failed. Please review the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())