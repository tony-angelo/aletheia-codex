"""
Test Neo4j connection to identify authentication issues.
This script tests various scenarios to help diagnose the problem.
"""

from neo4j import GraphDatabase
import sys

def test_connection(uri, user, password):
    """Test Neo4j connection with provided credentials."""
    print(f"\n{'='*60}")
    print(f"Testing Neo4j Connection")
    print(f"{'='*60}")
    print(f"URI: {uri}")
    print(f"User: {user}")
    print(f"Password: {'*' * len(password)}")
    
    try:
        # Test 1: Create driver
        print("\n[1] Creating driver...")
        driver = GraphDatabase.driver(uri, auth=(user, password))
        print("✓ Driver created successfully")
        
        # Test 2: Verify connectivity
        print("\n[2] Verifying connectivity...")
        driver.verify_connectivity()
        print("✓ Connectivity verified")
        
        # Test 3: Execute simple query
        print("\n[3] Executing test query...")
        with driver.session() as session:
            result = session.run("RETURN 1 as num")
            record = result.single()
            print(f"✓ Query executed successfully: {record['num']}")
        
        # Test 4: Check database info
        print("\n[4] Checking database info...")
        with driver.session() as session:
            result = session.run("CALL dbms.components() YIELD name, versions, edition")
            for record in result:
                print(f"✓ Database: {record['name']}")
                print(f"  Version: {record['versions']}")
                print(f"  Edition: {record['edition']}")
        
        driver.close()
        print("\n" + "="*60)
        print("✓ ALL TESTS PASSED")
        print("="*60)
        return True
        
    except Exception as e:
        print(f"\n✗ ERROR: {type(e).__name__}")
        print(f"  Message: {str(e)}")
        print("\n" + "="*60)
        print("✗ CONNECTION FAILED")
        print("="*60)
        return False


def test_driver_versions():
    """Check Neo4j driver version."""
    import neo4j
    print(f"\nNeo4j Driver Version: {neo4j.__version__}")


if __name__ == "__main__":
    test_driver_versions()
    
    if len(sys.argv) != 4:
        print("\nUsage: python test_neo4j_connection.py <uri> <user> <password>")
        print("\nExample:")
        print("  python test_neo4j_connection.py neo4j+s://xxxxx.databases.neo4j.io neo4j mypassword")
        sys.exit(1)
    
    uri = sys.argv[1]
    user = sys.argv[2]
    password = sys.argv[3]
    
    success = test_connection(uri, user, password)
    sys.exit(0 if success else 1)