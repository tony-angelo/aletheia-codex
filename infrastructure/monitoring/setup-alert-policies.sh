#!/bin/bash

# Setup Alert Policies for AletheiaCodex Load Balancer
# This script creates monitoring alert policies for the infrastructure

set -e

PROJECT_ID="aletheia-codex-prod"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Creating alert policies for project: $PROJECT_ID"
echo "================================================"

# 1. High 5xx Error Rate Alert
echo "Creating alert policy: High 5xx Error Rate..."
gcloud alpha monitoring policies create \
  --policy-from-file="${SCRIPT_DIR}/alert-policy-5xx-errors.yaml" \
  --project="${PROJECT_ID}"
echo "✓ High 5xx Error Rate alert created"

# 2. High Latency Alert
echo "Creating alert policy: High Latency..."
gcloud alpha monitoring policies create \
  --policy-from-file="${SCRIPT_DIR}/alert-policy-high-latency.yaml" \
  --project="${PROJECT_ID}"
echo "✓ High Latency alert created"

# 3. IAP Authentication Failures Alert
echo "Creating alert policy: IAP Authentication Failures..."
gcloud alpha monitoring policies create \
  --policy-from-file="${SCRIPT_DIR}/alert-policy-iap-failures.yaml" \
  --project="${PROJECT_ID}"
echo "✓ IAP Authentication Failures alert created"

# 4. Backend Service Health Alert
echo "Creating alert policy: Backend Service Health..."
gcloud alpha monitoring policies create \
  --policy-from-file="${SCRIPT_DIR}/alert-policy-backend-health.yaml" \
  --project="${PROJECT_ID}"
echo "✓ Backend Service Health alert created"

# 5. SSL Certificate Expiration Alert
echo "Creating alert policy: SSL Certificate Expiration..."
gcloud alpha monitoring policies create \
  --policy-from-file="${SCRIPT_DIR}/alert-policy-ssl-expiration.yaml" \
  --project="${PROJECT_ID}"
echo "✓ SSL Certificate Expiration alert created"

echo ""
echo "================================================"
echo "All alert policies created successfully!"
echo ""
echo "IMPORTANT: Notification channels need to be added manually"
echo "To add notification channels:"
echo "1. Go to Cloud Console > Monitoring > Alerting"
echo "2. Edit each alert policy"
echo "3. Add appropriate notification channels (email, Slack, PagerDuty, etc.)"
echo ""
echo "List all policies:"
echo "  gcloud alpha monitoring policies list --project=${PROJECT_ID}"