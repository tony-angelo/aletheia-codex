from neo4j import GraphDatabase

# URI examples: "neo4j://localhost", "neo4j+s://xxx.databases.neo4j.io"
URI = "neo4j+s://ac286c9e.databases.neo4j.io"
AUTH = ("neo4j", "LrVUYKHm7Uu8KWTYlDNnDnWYALD8v9KzdTzPl11WB6E")

with GraphDatabase.driver(URI, auth=AUTH) as driver:
    driver.verify_connectivity()
    print("Connection established.")