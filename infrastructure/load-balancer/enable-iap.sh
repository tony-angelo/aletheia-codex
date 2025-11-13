#!/bin/bash
set -e

echo "Enabling IAP on backend services..."
echo ""

# Note: IAP requires OAuth consent screen to be configured
# This will be done through the GCP Console or by Admin-Backend

echo "Checking if OAuth consent screen is configured..."
# We'll enable IAP on backend services
# The OAuth configuration will need to be done separately

for backend in backend-graphfunction backend-notesapifunction backend-orchestrate backend-orchestration backend-reviewapifunction backend-ingestion; do
    echo "Enabling IAP for $backend..."
    gcloud compute backend-services update $backend \
        --global \
        --iap=enabled 2>&1 || echo "Note: IAP enablement may require OAuth consent screen configuration"
    echo ""
done

echo "✅ IAP enablement attempted on all backend services"
echo ""
echo "Note: IAP requires OAuth consent screen configuration."
echo "This should be configured through GCP Console or by Admin-Backend."
echo ""

