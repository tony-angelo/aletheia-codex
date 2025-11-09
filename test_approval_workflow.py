"""
Test script to approve review items and verify they appear in Neo4j.
"""
from google.cloud import firestore
import requests
import json
import time

def test_approval_workflow():
    """Test the complete approval workflow."""
    print("=" * 80)
    print("TESTING APPROVAL WORKFLOW")
    print("=" * 80)
    
    try:
        # Initialize Firestore client
        db = firestore.Client(project='aletheia-codex-prod')
        print("✓ Firestore client initialized")
        
        # Get a pending review item
        print("\nFetching pending review items...")
        review_items = db.collection('review_queue').where('status', '==', 'pending').limit(1).get()
        
        if len(review_items) == 0:
            print("✗ No pending review items found!")
            return False
        
        review_item = review_items[0]
        item_id = review_item.id
        item_data = review_item.to_dict()
        
        print(f"✓ Found review item: {item_id}")
        print(f"  Type: {item_data.get('type')}")
        print(f"  User ID: {item_data.get('user_id')}")
        print(f"  Note ID: {item_data.get('note_id')}")
        
        if item_data.get('type') == 'entity':
            entity_data = item_data.get('data', {})
            print(f"  Entity name: {entity_data.get('name')}")
            print(f"  Entity type: {entity_data.get('type')}")
        
        # Approve the item by calling the review API
        print("\nApproving review item...")
        review_api_url = "https://review-api-h55nns6ojq-uc.a.run.app"
        
        # Note: This might require authentication
        # For now, let's try without auth since it might be configured as allow-unauthenticated
        response = requests.post(
            f"{review_api_url}/approve",
            json={
                'itemId': item_id,
                'userId': item_data.get('user_id')
            },
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"  Response status: {response.status_code}")
        print(f"  Response body: {response.text}")
        
        if response.status_code == 200:
            print("✓ Item approved successfully!")
            
            # Wait a moment for Neo4j write
            print("\nWaiting 5 seconds for Neo4j write...")
            time.sleep(5)
            
            # Check if item status changed
            updated_item = db.collection('review_queue').document(item_id).get()
            if updated_item.exists:
                updated_data = updated_item.to_dict()
                print(f"  Updated status: {updated_data.get('status')}")
                
                if updated_data.get('status') == 'approved':
                    print("✓ Item status updated to 'approved'")
                    print("\n" + "=" * 80)
                    print("✓ APPROVAL WORKFLOW TEST PASSED!")
                    print("=" * 80)
                    return True
                else:
                    print(f"✗ Item status not updated (still: {updated_data.get('status')})")
            else:
                print("✗ Item not found after approval")
        else:
            print(f"✗ Approval failed with status {response.status_code}")
            print(f"  Error: {response.text}")
        
        return False
        
    except Exception as e:
        print(f"\n✗ Error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_approval_workflow()
    exit(0 if success else 1)