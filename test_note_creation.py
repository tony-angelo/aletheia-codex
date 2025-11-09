"""
Test script to create a note in Firestore and verify orchestration function triggers.
"""
from google.cloud import firestore
import time
import sys

def create_test_note():
    """Create a test note in Firestore."""
    print("=" * 80)
    print("CREATING TEST NOTE")
    print("=" * 80)
    
    try:
        # Initialize Firestore client
        db = firestore.Client(project='aletheia-codex-prod')
        print("✓ Firestore client initialized")
        
        # Create test note
        test_note = {
            'userId': 'test-user-123',
            'content': 'I met John Smith at Google headquarters in Mountain View. He is the CEO and we discussed the new AI project.',
            'status': 'processing',
            'createdAt': firestore.SERVER_TIMESTAMP,
            'updatedAt': firestore.SERVER_TIMESTAMP,
            'metadata': {
                'source': 'test',
                'userAgent': 'test-script'
            }
        }
        
        print("\nCreating note with content:")
        print(f"  Content: {test_note['content'][:100]}...")
        print(f"  User ID: {test_note['userId']}")
        print(f"  Status: {test_note['status']}")
        
        # Add to Firestore
        doc_ref = db.collection('notes').add(test_note)
        note_id = doc_ref[1].id
        
        print(f"\n✓ Test note created successfully!")
        print(f"  Note ID: {note_id}")
        print(f"  Collection: notes")
        
        print("\n" + "=" * 80)
        print("WAITING FOR PROCESSING")
        print("=" * 80)
        print("Waiting 10 seconds for orchestration function to process...")
        
        time.sleep(10)
        
        # Check note status
        print("\nChecking note status...")
        note_doc = db.collection('notes').document(note_id).get()
        
        if note_doc.exists:
            note_data = note_doc.to_dict()
            status = note_data.get('status', 'unknown')
            error = note_data.get('error')
            extraction_summary = note_data.get('extractionSummary')
            
            print(f"  Status: {status}")
            if error:
                print(f"  Error: {error}")
            if extraction_summary:
                print(f"  Entities extracted: {extraction_summary.get('entityCount', 0)}")
                print(f"  Relationships detected: {extraction_summary.get('relationshipCount', 0)}")
            
            # Check review queue
            print("\nChecking review queue...")
            review_items = db.collection('review_queue').where('note_id', '==', note_id).get()
            print(f"  Review items created: {len(review_items)}")
            
            if len(review_items) > 0:
                entities = [item.to_dict() for item in review_items if item.to_dict().get('type') == 'entity']
                relationships = [item.to_dict() for item in review_items if item.to_dict().get('type') == 'relationship']
                print(f"  - Entities: {len(entities)}")
                print(f"  - Relationships: {len(relationships)}")
            
            print("\n" + "=" * 80)
            if status == 'completed':
                print("✓ TEST PASSED - Note processed successfully!")
            elif status == 'processing':
                print("⚠ TEST INCOMPLETE - Note still processing (may need more time)")
            elif status == 'failed':
                print("✗ TEST FAILED - Note processing failed")
                if error:
                    print(f"  Error: {error}")
            print("=" * 80)
            
            return note_id, status
        else:
            print("✗ Note not found!")
            return note_id, 'not_found'
            
    except Exception as e:
        print(f"\n✗ Error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, 'error'

if __name__ == '__main__':
    note_id, status = create_test_note()
    
    if status == 'completed':
        sys.exit(0)
    else:
        sys.exit(1)
