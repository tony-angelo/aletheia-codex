#!/bin/bash

# Test the orchestration function
source /root/google-cloud-sdk/path.bash.inc

DOC_ID="test-ai-sprint2-1762656877"
TOKEN=$(gcloud auth print-identity-token)

echo "🧪 Testing orchestration function..."
echo "Document ID: $DOC_ID"
echo "This will take 15-20 seconds for AI processing..."
echo ""

START_TIME=$(date +%s)

RESPONSE=$(curl -s -X POST \
  "https://us-central1-aletheia-codex-prod.cloudfunctions.net/orchestrate" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{&quot;document_id&quot;: &quot;$DOC_ID&quot;, &quot;user_id&quot;: &quot;test-user-sprint2&quot;}" \
  -w "\nHTTP_STATUS:%{http_code}")

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo "Response:"
echo "$RESPONSE" | grep -v "HTTP_STATUS" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE" | grep -v "HTTP_STATUS"
echo ""

HTTP_STATUS=$(echo "$RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)
echo "HTTP Status: $HTTP_STATUS"
echo "Duration: ${DURATION}s"
echo ""

if [ "$HTTP_STATUS" = "200" ]; then
    echo "✅ Function executed successfully!"
    echo ""
    echo "📊 Next steps:"
    echo "   1. Run: python3 verify_results.py"
    echo "   2. Check AI extraction results"
    echo "   3. Validate cost monitoring"
else
    echo "⚠️  Function returned status $HTTP_STATUS"
    echo ""
    echo "Check logs:"
    echo "   gcloud functions logs read orchestrate --region=us-central1 --limit=20"
fi