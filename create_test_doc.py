#!/usr/bin/env python3
"""
Create a test document in Firestore for Sprint 2 AI testing.
"""
import os
import sys
import json
import time
from datetime import datetime
from google.cloud import firestore
from google.oauth2 import service_account

# Set up credentials
credentials_path = '/workspace/aletheia-codex/service-account-key.json'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path

try:
    # Initialize Firestore with explicit credentials
    credentials = service_account.Credentials.from_service_account_file(
        credentials_path,
        scopes=['https://www.googleapis.com/auth/datastore']
    )
    db = firestore.Client(project='aletheia-codex-prod', credentials=credentials)
    
    # Create test document
    doc_id = f'test-ai-sprint2-{int(time.time())}'
    doc_ref = db.collection('documents').document(doc_id)
    
    content = """Albert Einstein was a theoretical physicist who developed the theory of relativity. He was born in Ulm, Germany in 1879. Einstein worked at the Institute for Advanced Study in Princeton, New Jersey. His famous equation E=mc² revolutionized physics. He received the Nobel Prize in Physics in 1921 for his explanation of the photoelectric effect.

Marie Curie was a Polish-French physicist and chemist who conducted pioneering research on radioactivity. She was the first woman to win a Nobel Prize and the only person to win Nobel Prizes in two different scientific fields - Physics and Chemistry. Curie worked closely with her husband Pierre Curie at the University of Paris.

The Manhattan Project was a research and development undertaking during World War II that produced the first nuclear weapons. It was led by the United States with support from the United Kingdom and Canada. J. Robert Oppenheimer served as the scientific director of the project at Los Alamos Laboratory in New Mexico."""
    
    doc_data = {
        'title': 'Sprint 2 AI Test Document',
        'content': content,
        'user_id': 'test-user-sprint2',
        'status': 'pending',
        'created_at': firestore.SERVER_TIMESTAMP,
        'updated_at': firestore.SERVER_TIMESTAMP,
        'file_path': 'raw/test-ai-sprint2.txt',
        'metadata': {
            'source': 'sprint2_test',
            'test_type': 'ai_integration'
        }
    }
    
    # Create the document
    doc_ref.set(doc_data)
    print(f"✅ Successfully created test document!")
    print(f"   Document ID: {doc_id}")
    print(f"   User ID: {doc_data['user_id']}")
    print(f"   Status: {doc_data['status']}")
    print(f"   Content length: {len(content)} characters")
    print(f"\n📝 Document contains entities:")
    print(f"   - Albert Einstein (Person)")
    print(f"   - Marie Curie (Person)")
    print(f"   - Pierre Curie (Person)")
    print(f"   - J. Robert Oppenheimer (Person)")
    print(f"   - Institute for Advanced Study (Organization)")
    print(f"   - University of Paris (Organization)")
    print(f"   - Manhattan Project (Concept)")
    print(f"   - Ulm, Germany (Place)")
    print(f"   - Princeton, New Jersey (Place)")
    print(f"   - Los Alamos Laboratory (Place)")
    
    # Return the document ID for testing
    sys.exit(0)
    
except Exception as e:
    print(f"❌ Error creating document: {e}")
    sys.exit(1)