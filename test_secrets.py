from google.cloud import secretmanager

project_id = "aletheia-codex-prod"

def get_secret(secret_id):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

print("Testing secret retrieval...")
try:
    uri = get_secret("NEO4J_URI")
    user = get_secret("NEO4J_USER")
    password = get_secret("NEO4J_PASSWORD")
    
    print(f" NEO4J_URI: {uri}")
    print(f" NEO4J_USER: {user}")
    print(f" NEO4J_PASSWORD: {password[:5]}...{password[-5:]}")
    
    # Now test Neo4j connection
    from neo4j import GraphDatabase
    driver = GraphDatabase.driver(uri, auth=(user, password))
    with driver.session() as session:
        result = session.run("RETURN 1 as num")
        print(f" Neo4j connection successful!")
    driver.close()
    
except Exception as e:
    print(f" Error: {e}")
    import traceback
    traceback.print_exc()
