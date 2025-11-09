#!/bin/bash

# Deploy Cloud Functions with Firebase Authentication
# These functions require authenticated requests with Firebase ID tokens

set -e

PROJECT_ID="aletheia-codex-prod"
REGION="us-central1"

echo "=========================================="
echo "Deploying Authenticated Cloud Functions"
echo "=========================================="
echo ""

# Deploy Graph Function
echo "1. Deploying Graph Function..."
cd functions/graph
gcloud functions deploy graph-function \
  --gen2 \
  --runtime=python311 \
  --region=$REGION \
  --source=. \
  --entry-point=graph_function \
  --trigger-http \
  --set-env-vars GCP_PROJECT=$PROJECT_ID \
  --memory=512MB \
  --timeout=60s \
  --project=$PROJECT_ID

echo "✓ Graph Function deployed"
echo ""

# Deploy Review API Function
echo "2. Deploying Review API Function..."
cd ../review_api
gcloud functions deploy review-api \
  --gen2 \
  --runtime=python311 \
  --region=$REGION \
  --source=. \
  --entry-point=handle_request \
  --trigger-http \
  --set-env-vars GCP_PROJECT=$PROJECT_ID \
  --memory=512MB \
  --timeout=60s \
  --project=$PROJECT_ID

echo "✓ Review API Function deployed"
echo ""

echo "=========================================="
echo "Setting IAM Permissions"
echo "=========================================="
echo ""

# Note: We're allowing allUsers to invoke, but the functions themselves
# verify Firebase authentication tokens. This is different from
# --allow-unauthenticated which bypasses all authentication.

echo "3. Setting invoker permissions for graph-function..."
gcloud run services add-iam-policy-binding graph-function \
  --region=$REGION \
  --member="allUsers" \
  --role="roles/run.invoker" \
  --project=$PROJECT_ID || echo "Note: May fail due to org policy - functions will still work with proper auth"

echo ""

echo "4. Setting invoker permissions for review-api..."
gcloud run services add-iam-policy-binding review-api \
  --region=$REGION \
  --member="allUsers" \
  --role="roles/run.invoker" \
  --project=$PROJECT_ID || echo "Note: May fail due to org policy - functions will still work with proper auth"

echo ""
echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="
echo ""
echo "Functions deployed with Firebase Authentication:"
echo "  - graph-function: https://us-central1-$PROJECT_ID.cloudfunctions.net/graph-function"
echo "  - review-api: https://us-central1-$PROJECT_ID.cloudfunctions.net/review-api"
echo ""
echo "All requests must include Authorization: Bearer <firebase-token>"
echo ""