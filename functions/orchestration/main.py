"""
AletheiaCodex - Orchestration Function
Processes documents: chunking, embedding, and knowledge graph storage.
"""

import functions_framework
from flask import Request, jsonify
from google.cloud import firestore, storage
import os
import json

from shared.db.firestore_client import get_firestore_client
from shared.db.neo4j_client import get_neo4j_driver, execute_query
from shared.ai.gemini_client import generate_embeddings
from shared.utils.logging import get_logger
from shared.utils.text_chunker import chunk_text

logger = get_logger("orchestration")

PROJECT_ID = os.environ.get("GCP_PROJECT", "aletheia-codex-prod")
BUCKET_NAME = f"{PROJECT_ID}-documents"


@functions_framework.http
def orchestrate(request: Request):
    """
    Process a document: fetch, chunk, embed, and store in Neo4j.
    
    Expected JSON payload from Cloud Tasks:
    {
        "document_id": "firestore-doc-id",
        "action": "process_document"
    }
    """
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"error": "Invalid JSON payload"}), 400
        
        document_id = data.get("document_id")
        action = data.get("action")
        
        if not document_id or action != "process_document":
            return jsonify({"error": "Invalid payload. Expected document_id and action=process_document"}), 400
        
        logger.info(f"Processing document: {document_id}")
        
        # Update status to processing
        db = get_firestore_client(PROJECT_ID)
        doc_ref = db.collection("documents").document(document_id)
        doc_ref.update({"status": "processing"})
        
        # Fetch document content from Cloud Storage
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(f"raw/{document_id}.txt")
        content = blob.download_as_text()
        
        logger.info(f"Fetched content: {len(content)} characters")
        
        # Fetch document metadata
        doc_data = doc_ref.get().to_dict()
        title = doc_data.get("title", "Untitled")
        
        # Chunk the text
        chunks = chunk_text(content, chunk_size=500, overlap=50)
        logger.info(f"Created {len(chunks)} chunks")
        
        # Process each chunk
        driver = get_neo4j_driver(PROJECT_ID)
        
        with driver.session() as session:
            # Create document node
            session.run(
                """
                MERGE (d:Document {id: \})
                SET d.title = \,
                    d.created_at = datetime(),
                    d.chunk_count = \
                """,
                doc_id=document_id,
                title=title,
                chunk_count=len(chunks)
            )
            
            # Process each chunk
            for idx, chunk in enumerate(chunks):
                chunk_text = chunk['text']
                
                # Generate embedding
                embedding = generate_embeddings(chunk_text)
                logger.info(f"Generated embedding for chunk {idx + 1}/{len(chunks)}")
                
                # Store chunk and embedding in Neo4j
                session.run(
                    """
                    MATCH (d:Document {id: \})
                    CREATE (c:Chunk {
                        id: \,
                        text: \,
                        position: \,
                        length: \,
                        embedding: \
                    })
                    CREATE (d)-[:HAS_CHUNK {position: \}]->(c)
                    """,
                    doc_id=document_id,
                    chunk_id=f"{document_id}_chunk_{idx}",
                    text=chunk_text,
                    position=idx,
                    length=chunk['length'],
                    embedding=embedding
                )
        
        logger.info(f"Stored {len(chunks)} chunks in Neo4j")
        
        # Update status to completed
        doc_ref.update({
            "status": "completed",
            "processed_at": firestore.SERVER_TIMESTAMP,
            "chunk_count": len(chunks)
        })
        
        return jsonify({
            "status": "success",
            "document_id": document_id,
            "chunks_processed": len(chunks)
        }), 200
        
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        
        # Update status to failed
        if 'document_id' in locals():
            try:
                db = get_firestore_client(PROJECT_ID)
                db.collection("documents").document(document_id).update({
                    "status": "failed",
                    "error": str(e)
                })
            except:
                pass
        
        return jsonify({"error": f"Processing failed: {str(e)}"}), 500
