#!/bin/bash

# Create a test document in Firestore using gcloud
# This creates a document with test content for AI extraction

source /root/google-cloud-sdk/path.bash.inc

# Document data
DOC_ID="test-ai-sprint2-$(date +%s)"
USER_ID="test-user-sprint2"
CONTENT="Albert Einstein was a theoretical physicist who developed the theory of relativity. He was born in Ulm, Germany in 1879. Einstein worked at the Institute for Advanced Study in Princeton, New Jersey. His famous equation E=mc² revolutionized physics. He received the Nobel Prize in Physics in 1921 for his explanation of the photoelectric effect.

Marie Curie was a Polish-French physicist and chemist who conducted pioneering research on radioactivity. She was the first woman to win a Nobel Prize and the only person to win Nobel Prizes in two different scientific fields - Physics and Chemistry. Curie worked closely with her husband Pierre Curie at the University of Paris.

The Manhattan Project was a research and development undertaking during World War II that produced the first nuclear weapons. It was led by the United States with support from the United Kingdom and Canada. J. Robert Oppenheimer served as the scientific director of the project at Los Alamos Laboratory in New Mexico."

# Create the document using Firestore REST API
TOKEN=$(gcloud auth print-access-token)

curl -X POST \
  "https://firestore.googleapis.com/v1/projects/aletheia-codex-prod/databases/(default)/documents/documents?documentId=$DOC_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    &quot;fields&quot;: {
      &quot;title&quot;: {&quot;stringValue&quot;: &quot;Sprint 2 AI Test Document&quot;},
      &quot;content&quot;: {&quot;stringValue&quot;: &quot;$CONTENT&quot;},
      &quot;user_id&quot;: {&quot;stringValue&quot;: &quot;$USER_ID&quot;},
      &quot;status&quot;: {&quot;stringValue&quot;: &quot;pending&quot;},
      &quot;file_path&quot;: {&quot;stringValue&quot;: &quot;raw/test-ai-sprint2.txt&quot;},
      &quot;created_at&quot;: {&quot;timestampValue&quot;: &quot;$(date -u +%Y-%m-%dT%H:%M:%SZ)&quot;},
      &quot;updated_at&quot;: {&quot;timestampValue&quot;: &quot;$(date -u +%Y-%m-%dT%H:%M:%SZ)&quot;},
      &quot;metadata&quot;: {
        &quot;mapValue&quot;: {
          &quot;fields&quot;: {
            &quot;source&quot;: {&quot;stringValue&quot;: &quot;sprint2_test&quot;},
            &quot;test_type&quot;: {&quot;stringValue&quot;: &quot;ai_integration&quot;}
          }
        }
      }
    }
  }"

echo ""
echo "Document ID: $DOC_ID"
echo "User ID: $USER_ID"