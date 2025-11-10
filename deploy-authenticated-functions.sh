#!/bin/bash
# Deploy Cloud Functions with Firebase Authentication
# Sprint 6: Authentication Implementation

set -e

PROJECT_ID="aletheia-codex-prod"
REGION="us-central1"

echo "=========================================="
echo "Deploying Authenticated Cloud Functions"
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "=========================================="

# Set PATH to include gcloud
export PATH=$PATH:/root/google-cloud-sdk/bin

# Authenticate and set project
echo "Setting up GCP authentication..."
gcloud config set project $PROJECT_ID

cd aletheia-codex

# Deploy Notes API
echo ""
echo "=========================================="
echo "Deploying Notes API Function..."
echo "=========================================="
cd functions/notes_api

# Copy shared directory if it's a symlink
if [ -L "shared" ]; then
  echo "Copying shared directory..."
  rm shared
  cp -r ../orchestration/shared .
fi
gcloud functions deploy notes-api-function \
  --runtime=python311 \
  --region=$REGION \
  --source=. \
  --entry-point=notes_api \
  --trigger-http \
  --service-account=aletheia-functions@${PROJECT_ID}.iam.gserviceaccount.com \
  --set-env-vars GCP_PROJECT=$PROJECT_ID \
  --memory=512MB \
  --timeout=60s

echo "Granting invoker permissions to Notes API..."
gcloud functions add-invoker-policy-binding notes-api-function \
  --region=$REGION \
  --member=allUsers

cd ../..

# Deploy Review API
echo ""
echo "=========================================="
echo "Deploying Review API Function..."
echo "=========================================="
cd functions/review_api

# Copy shared directory if it's a symlink
if [ -L "shared" ]; then
  echo "Copying shared directory..."
  rm shared
  cp -r ../orchestration/shared .
fi
gcloud functions deploy review-api-function \
  --runtime=python311 \
  --region=$REGION \
  --source=. \
  --entry-point=handle_request \
  --trigger-http \
  --service-account=aletheia-functions@${PROJECT_ID}.iam.gserviceaccount.com \
  --set-env-vars GCP_PROJECT=$PROJECT_ID \
  --memory=512MB \
  --timeout=60s

echo "Granting invoker permissions to Review API..."
gcloud functions add-invoker-policy-binding review-api-function \
  --region=$REGION \
  --member=allUsers

cd ../..

# Deploy Graph Function
echo ""
echo "=========================================="
echo "Deploying Graph Function..."
echo "=========================================="
cd functions/graph

# Copy shared directory if it's a symlink
if [ -L "shared" ]; then
  echo "Copying shared directory..."
  rm shared
  cp -r ../orchestration/shared .
fi
gcloud functions deploy graph-function \
  --runtime=python311 \
  --region=$REGION \
  --source=. \
  --entry-point=graph_function \
  --trigger-http \
  --service-account=aletheia-functions@${PROJECT_ID}.iam.gserviceaccount.com \
  --set-env-vars GCP_PROJECT=$PROJECT_ID \
  --memory=512MB \
  --timeout=60s

echo "Granting invoker permissions to Graph Function..."
gcloud functions add-invoker-policy-binding graph-function \
  --region=$REGION \
  --member=allUsers

cd ../..

echo ""
echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="
echo ""
echo "Function URLs:"
echo "- Notes API: https://${REGION}-${PROJECT_ID}.cloudfunctions.net/notes-api-function"
echo "- Review API: https://${REGION}-${PROJECT_ID}.cloudfunctions.net/review-api-function"
echo "- Graph API: https://${REGION}-${PROJECT_ID}.cloudfunctions.net/graph-function"
echo ""
echo "All functions require Firebase Authentication."
echo "Requests must include: Authorization: Bearer <firebase-token>"
echo ""