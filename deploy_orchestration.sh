#!/bin/bash
# Deploy orchestration function with AI integration

set -e

echo "Deploying orchestration function with AI integration..."

cd functions/orchestration

gcloud functions deploy orchestrate \
    --gen2 \
    --runtime=python311 \
    --region=us-central1 \
    --source=. \
    --entry-point=orchestrate \
    --trigger-http \
    --service-account=aletheia-functions@aletheia-codex-prod.iam.gserviceaccount.com \
    --timeout=540s \
    --memory=512MB \
    --set-env-vars GCP_PROJECT=aletheia-codex-prod \
    --allow-unauthenticated

echo "Deployment complete!"
echo ""
echo "Verifying deployment..."
gcloud functions describe orchestrate --region=us-central1 --gen2

echo ""
echo "Function URL:"
gcloud functions describe orchestrate --region=us-central1 --gen2 --format='value(serviceConfig.uri)'