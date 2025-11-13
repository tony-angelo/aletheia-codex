#!/bin/bash
# Disable IAP on all backend services
# This script removes IAP from the Load Balancer backend services
# to restore public access for the SaaS application

set -e

echo "=========================================="
echo "Disabling IAP on Backend Services"
echo "=========================================="
echo ""

# Set project
gcloud config set project aletheia-codex-prod

# List of backend services
SERVICES=(
  "backend-graphfunction"
  "backend-notesapifunction"
  "backend-orchestration"
  "backend-reviewapifunction"
  "backend-ingestion"
)

echo "Disabling IAP on all backend services..."
echo ""

for service in "${SERVICES[@]}"; do
  echo "Disabling IAP on $service..."
  gcloud compute backend-services update "$service" --global --no-iap
  echo "✓ IAP disabled on $service"
  echo ""
done

echo "=========================================="
echo "Verification"
echo "=========================================="
echo ""

for service in "${SERVICES[@]}"; do
  enabled=$(gcloud compute backend-services describe "$service" --global --format="value(iap.enabled)" 2>/dev/null || echo "")
  if [ -z "$enabled" ] || [ "$enabled" = "False" ]; then
    echo "✓ $service: IAP disabled"
  else
    echo "✗ $service: IAP still enabled (value: $enabled)"
  fi
done

echo ""
echo "=========================================="
echo "IAP Removal Complete"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Test application access at https://aletheiacodex.app"
echo "2. Verify Firebase Auth login works"
echo "3. Test self-service user registration"
echo "4. Confirm no 403 errors"
echo ""