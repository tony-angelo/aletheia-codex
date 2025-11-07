from google.cloud import secretmanager
from neo4j import GraphDatabase

project_id = "aletheia-codex-prod"

def get_secret(secret_id):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

print("Fetching credentials from Secret Manager...")
uri = get_secret("NEO4J_URI")
user = get_secret("NEO4J_USER")
password = get_secret("NEO4J_PASSWORD")

print(f"URI: {uri}")
print(f"User: {user}")
print(f"Password: {password[:5]}...{password[-5:]}")

print("\nTesting Neo4j connection...")
try:
    driver = GraphDatabase.driver(uri, auth=(user, password))
    print(" Driver created")
    
    # Verify connection
    driver.verify_connectivity()
    print(" Connectivity verified")
    
    with driver.session() as session:
        result = session.run("RETURN 1 as num")
        record = result.single()
        print(f" Query successful: {record['num']}")
    
    driver.close()
    print("\n All tests passed! Credentials are correct.")
    
except Exception as e:
    print(f"\n Failed: {e}")
    import traceback
    traceback.print_exc()
