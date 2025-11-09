#!/bin/bash
# Test orchestration function with AI integration

set -e

FUNCTION_URL="https://us-central1-aletheia-codex-prod.cloudfunctions.net/orchestrate"

echo "Testing orchestration function with AI integration..."
echo ""

# Create test document in Firestore first
echo "Step 1: Create test document in Firestore"
echo "Please create a test document with:"
echo "  - Collection: documents"
echo "  - Document ID: test-ai-doc-1"
echo "  - Fields:"
echo "    - title: 'Sprint 2 AI Test'"
echo "    - user_id: 'test-user-ai'"
echo "    - status: 'uploaded'"
echo "    - created_at: (current timestamp)"
echo ""
echo "And upload content to Cloud Storage:"
echo "  - Bucket: aletheia-codex-prod-documents"
echo "  - Path: raw/test-ai-doc-1.txt"
echo "  - Content: 'I met Sarah Johnson at Google. She works as a software engineer in Mountain View, California.'"
echo ""
read -p "Press Enter when ready to test..."

echo ""
echo "Step 2: Testing orchestration function..."
curl -X POST \
  "$FUNCTION_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "test-ai-doc-1",
    "user_id": "test-user-ai"
  }' | jq .

echo ""
echo "Step 3: Verify results in Firestore"
echo "Check the following collections:"
echo "  - documents/test-ai-doc-1 (should have status: completed)"
echo "  - review_queue (should have extracted entities and relationships)"
echo "  - usage_logs (should have cost tracking entries)"
echo ""
echo "Step 4: Verify Neo4j graph"
echo "Check Neo4j for:"
echo "  - User node: test-user-ai"
echo "  - Entity nodes (Sarah Johnson, Google, Mountain View, California)"
echo "  - Relationships (WORKS_AT, LOCATED_IN)"