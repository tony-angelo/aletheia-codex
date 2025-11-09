#!/usr/bin/env python3
"""
Reset document status and retry testing.
"""
import os
import sys
from google.cloud import firestore
from google.oauth2 import service_account

credentials_path = '/workspace/aletheia-codex/service-account-key.json'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path

def reset_document_status():
    """Reset document status to pending for retry."""
    try:
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=['https://www.googleapis.com/auth/datastore']
        )
        db = firestore.Client(project='aletheia-codex-prod', credentials=credentials)
        
        doc_id = 'test-ai-sprint2-1762656877'
        doc_ref = db.collection('documents').document(doc_id)
        
        # Update status to pending
        doc_ref.update({
            'status': 'pending',
            'updated_at': firestore.SERVER_TIMESTAMP,
            'error': firestore.DELETE_FIELD  # Remove error field
        })
        
        print(f"✅ Reset document status to 'pending'")
        print(f"   Document ID: {doc_id}")
        print(f"\n📝 Document is ready for retry")
        print(f"\nNext steps:")
        print(f"1. Ensure Firestore index is built (check Firebase Console)")
        print(f"2. Run: ./test_function.sh")
        print(f"3. Verify results")
        
        return True
        
    except Exception as e:
        print(f"❌ Error resetting document: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if reset_document_status():
        sys.exit(0)
    else:
        sys.exit(1)