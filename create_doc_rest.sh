#!/bin/bash

source /root/google-cloud-sdk/path.bash.inc

# Generate document ID
DOC_ID="test-ai-sprint2-$(date +%s)"

# Get access token
TOKEN=$(gcloud auth print-access-token)

# Create document using REST API
curl -X PATCH \
  "https://firestore.googleapis.com/v1/projects/aletheia-codex-prod/databases/(default)/documents/documents/$DOC_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
  "fields": {
    "title": {
      "stringValue": "Sprint 2 AI Test Document"
    },
    "content": {
      "stringValue": "Albert Einstein was a theoretical physicist who developed the theory of relativity. He was born in Ulm, Germany in 1879. Einstein worked at the Institute for Advanced Study in Princeton, New Jersey. His famous equation E=mc² revolutionized physics. He received the Nobel Prize in Physics in 1921 for his explanation of the photoelectric effect.\n\nMarie Curie was a Polish-French physicist and chemist who conducted pioneering research on radioactivity. She was the first woman to win a Nobel Prize and the only person to win Nobel Prizes in two different scientific fields - Physics and Chemistry. Curie worked closely with her husband Pierre Curie at the University of Paris.\n\nThe Manhattan Project was a research and development undertaking during World War II that produced the first nuclear weapons. It was led by the United States with support from the United Kingdom and Canada. J. Robert Oppenheimer served as the scientific director of the project at Los Alamos Laboratory in New Mexico."
    },
    "user_id": {
      "stringValue": "test-user-sprint2"
    },
    "status": {
      "stringValue": "pending"
    },
    "file_path": {
      "stringValue": "raw/test-ai-sprint2.txt"
    },
    "created_at": {
      "timestampValue": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"
    },
    "updated_at": {
      "timestampValue": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"
    },
    "metadata": {
      "mapValue": {
        "fields": {
          "source": {
            "stringValue": "sprint2_test"
          },
          "test_type": {
            "stringValue": "ai_integration"
          }
        }
      }
    }
  }
}'

echo ""
echo ""
echo "✅ Document created successfully!"
echo "   Document ID: $DOC_ID"
echo "   User ID: test-user-sprint2"
echo ""
echo "Now testing the function..."
echo ""

# Test the function
echo "🧪 Testing orchestration function..."
IDENTITY_TOKEN=$(gcloud auth print-identity-token)

RESPONSE=$(curl -s -X POST \
  "https://us-central1-aletheia-codex-prod.cloudfunctions.net/orchestrate" \
  -H "Authorization: Bearer $IDENTITY_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{&quot;document_id&quot;: &quot;$DOC_ID&quot;, &quot;user_id&quot;: &quot;test-user-sprint2&quot;}" \
  -w "\nHTTP_STATUS:%{http_code}")

HTTP_STATUS=$(echo "$RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | grep -v "HTTP_STATUS")

echo "Response:"
echo "$BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"
echo ""
echo "HTTP Status: $HTTP_STATUS"
echo ""

if [ "$HTTP_STATUS" = "200" ]; then
    echo "✅ Function executed successfully!"
    echo ""
    echo "📊 Next steps:"
    echo "   1. Check Firestore review_queue collection"
    echo "   2. Check Neo4j graph for entities and relationships"
    echo "   3. Check usage_logs for cost tracking"
    echo ""
    echo "   Document ID: $DOC_ID"
else
    echo "⚠️  Function returned status $HTTP_STATUS"
    echo "   Check logs: gcloud functions logs read orchestrate --region=us-central1 --limit=20"
fi