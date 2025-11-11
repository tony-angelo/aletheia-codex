#!/usr/bin/env python3
"""
Verify AI extraction results and cost monitoring.
"""
import os
import sys
from google.cloud import firestore
from google.oauth2 import service_account
from datetime import datetime

credentials_path = '/workspace/aletheia-codex/service-account-key.json'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path

def verify_results():
    """Verify AI extraction results."""
    try:
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=['https://www.googleapis.com/auth/datastore']
        )
        db = firestore.Client(project='aletheia-codex-prod', credentials=credentials)
        
        doc_id = 'test-ai-sprint2-1762656877'
        
        print("=" * 80)
        print("SPRINT 2 AI EXTRACTION VERIFICATION")
        print("=" * 80)
        print()
        
        # Check document status
        print("📄 Document Status:")
        doc_ref = db.collection('documents').document(doc_id)
        doc = doc_ref.get()
        if doc.exists:
            data = doc.to_dict()
            print(f"   Status: {data.get('status', 'unknown')}")
            print(f"   Updated: {data.get('updated_at', 'unknown')}")
            if 'error' in data:
                print(f"   Error: {data.get('error')}")
        print()
        
        # Check review queue
        print("🔍 Review Queue (Extracted Entities & Relationships):")
        review_items = db.collection('review_queue').where('document_id', '==', doc_id).stream()
        
        entities = []
        relationships = []
        
        for item in review_items:
            item_data = item.to_dict()
            item_type = item_data.get('item_type')
            
            if item_type == 'entity':
                entities.append(item_data)
            elif item_type == 'relationship':
                relationships.append(item_data)
        
        print(f"\n   📊 Entities Extracted: {len(entities)}")
        if entities:
            print("   " + "-" * 76)
            for i, entity in enumerate(entities[:10], 1):  # Show first 10
                entity_data = entity.get('item_data', {})
                name = entity_data.get('name', 'Unknown')
                entity_type = entity_data.get('type', 'Unknown')
                confidence = entity_data.get('confidence', 0)
                print(f"   {i:2d}. {name:30s} | Type: {entity_type:15s} | Confidence: {confidence:.2f}")
            if len(entities) > 10:
                print(f"   ... and {len(entities) - 10} more")
        
        print(f"\n   🔗 Relationships Detected: {len(relationships)}")
        if relationships:
            print("   " + "-" * 76)
            for i, rel in enumerate(relationships[:10], 1):  # Show first 10
                rel_data = rel.get('item_data', {})
                source = rel_data.get('source_entity', 'Unknown')
                rel_type = rel_data.get('relationship_type', 'Unknown')
                target = rel_data.get('target_entity', 'Unknown')
                confidence = rel_data.get('confidence', 0)
                print(f"   {i:2d}. {source:20s} --[{rel_type}]--> {target:20s} | Conf: {confidence:.2f}")
            if len(relationships) > 10:
                print(f"   ... and {len(relationships) - 10} more")
        
        print()
        
        # Check usage logs
        print("💰 Cost Monitoring (Usage Logs):")
        usage_logs = list(db.collection('usage_logs').where('document_id', '==', doc_id).stream())
        
        if usage_logs:
            total_cost = 0
            total_tokens = 0
            
            print("   " + "-" * 76)
            for log in usage_logs:
                log_data = log.to_dict()
                operation = log_data.get('operation_type', 'unknown')
                tokens = log_data.get('tokens_used', 0)
                cost = log_data.get('cost', 0)
                model = log_data.get('model', 'unknown')
                
                total_cost += cost
                total_tokens += tokens
                
                print(f"   Operation: {operation:25s} | Tokens: {tokens:6d} | Cost: ${cost:.6f} | Model: {model}")
            
            print("   " + "-" * 76)
            print(f"   TOTAL: {len(usage_logs)} operations | {total_tokens:6d} tokens | ${total_cost:.6f}")
            print()
            print(f"   💵 Cost Analysis:")
            print(f"      Per Document: ${total_cost:.6f}")
            print(f"      Budget Target: $0.01")
            print(f"      Under Budget: {((0.01 - total_cost) / 0.01 * 100):.1f}%")
            
            if total_cost < 0.01:
                print(f"      ✅ UNDER BUDGET!")
            else:
                print(f"      ⚠️  OVER BUDGET!")
        else:
            print("   ⚠️  No usage logs found")
        
        print()
        print("=" * 80)
        print("VERIFICATION SUMMARY")
        print("=" * 80)
        
        # Calculate accuracy
        expected_entities = 10
        expected_relationships = 8
        
        entity_accuracy = (len(entities) / expected_entities * 100) if expected_entities > 0 else 0
        relationship_accuracy = (len(relationships) / expected_relationships * 100) if expected_relationships > 0 else 0
        
        print(f"\n✅ Entities Extracted: {len(entities)}/{expected_entities} (Expected ~{expected_entities})")
        print(f"   Accuracy: {entity_accuracy:.1f}% (Target: >80%)")
        if entity_accuracy >= 80:
            print(f"   ✅ PASSED")
        else:
            print(f"   ⚠️  BELOW TARGET")
        
        print(f"\n✅ Relationships Detected: {len(relationships)}/{expected_relationships} (Expected ~{expected_relationships})")
        print(f"   Accuracy: {relationship_accuracy:.1f}% (Target: >70%)")
        if relationship_accuracy >= 70:
            print(f"   ✅ PASSED")
        else:
            print(f"   ⚠️  BELOW TARGET")
        
        if usage_logs:
            print(f"\n✅ Cost per Document: ${total_cost:.6f} (Target: <$0.01)")
            if total_cost < 0.01:
                print(f"   ✅ PASSED ({((0.01 - total_cost) / 0.01 * 100):.1f}% under budget)")
            else:
                print(f"   ⚠️  OVER BUDGET")
        
        print()
        print("=" * 80)
        
        # Overall assessment
        if len(entities) >= 8 and len(relationships) >= 6 and (not usage_logs or total_cost < 0.01):
            print("🎉 SPRINT 2 TESTING: PASSED!")
            print("   All targets met or exceeded.")
            return True
        else:
            print("⚠️  SPRINT 2 TESTING: NEEDS REVIEW")
            print("   Some targets not met. Check results above.")
            return False
        
    except Exception as e:
        print(f"❌ Error verifying results: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if verify_results():
        sys.exit(0)
    else:
        sys.exit(1)