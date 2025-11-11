#!/bin/bash

# API Gateway Deployment Script for Aletheia Codex
# This script deploys the API Gateway configuration to GCP

set -e

PROJECT_ID="aletheia-codex-prod"
REGION="us-central1"
API_ID="aletheia-codex-api"
CONFIG_ID="aletheia-codex-config-v1"
GATEWAY_ID="aletheia-codex-gateway"

echo "=========================================="
echo "Aletheia Codex API Gateway Deployment"
echo "=========================================="
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI not found. Please install Google Cloud SDK."
    exit 1
fi

echo "✅ gcloud CLI found"
echo ""

# Set project
echo "Setting project to $PROJECT_ID..."
gcloud config set project $PROJECT_ID
echo ""

# Step 1: Create API
echo "=========================================="
echo "Step 1: Creating API"
echo "=========================================="
echo ""

if gcloud api-gateway apis describe $API_ID --project=$PROJECT_ID &> /dev/null; then
    echo "✅ API '$API_ID' already exists"
else
    echo "Creating API '$API_ID'..."
    gcloud api-gateway apis create $API_ID \
        --project=$PROJECT_ID \
        --display-name="Aletheia Codex API"
    echo "✅ API created"
fi
echo ""

# Step 2: Create API Config
echo "=========================================="
echo "Step 2: Creating API Config"
echo "=========================================="
echo ""

echo "Creating API config from OpenAPI spec..."
gcloud api-gateway api-configs create $CONFIG_ID \
    --api=$API_ID \
    --openapi-spec=api-gateway-config.yaml \
    --project=$PROJECT_ID \
    --backend-auth-service-account=$PROJECT_ID@appspot.gserviceaccount.com

echo "✅ API config created"
echo ""

# Step 3: Create Gateway
echo "=========================================="
echo "Step 3: Creating API Gateway"
echo "=========================================="
echo ""

if gcloud api-gateway gateways describe $GATEWAY_ID --location=$REGION --project=$PROJECT_ID &> /dev/null; then
    echo "Gateway '$GATEWAY_ID' already exists. Updating..."
    gcloud api-gateway gateways update $GATEWAY_ID \
        --api=$API_ID \
        --api-config=$CONFIG_ID \
        --location=$REGION \
        --project=$PROJECT_ID
    echo "✅ Gateway updated"
else
    echo "Creating gateway '$GATEWAY_ID'..."
    gcloud api-gateway gateways create $GATEWAY_ID \
        --api=$API_ID \
        --api-config=$CONFIG_ID \
        --location=$REGION \
        --project=$PROJECT_ID
    echo "✅ Gateway created"
fi
echo ""

# Step 4: Get Gateway URL
echo "=========================================="
echo "Step 4: Getting Gateway URL"
echo "=========================================="
echo ""

echo "Retrieving gateway URL..."
GATEWAY_URL=$(gcloud api-gateway gateways describe $GATEWAY_ID \
    --location=$REGION \
    --project=$PROJECT_ID \
    --format="value(defaultHostname)")

echo ""
echo "=========================================="
echo "✅ Deployment Complete!"
echo "=========================================="
echo ""
echo "Gateway URL: https://$GATEWAY_URL"
echo ""
echo "Next steps:"
echo "1. Update frontend environment variables:"
echo "   REACT_APP_API_URL=https://$GATEWAY_URL"
echo ""
echo "2. Test the endpoints:"
echo "   curl -H &quot;Authorization: Bearer YOUR_FIREBASE_TOKEN&quot; https://$GATEWAY_URL/api/review/pending"
echo "   curl -H &quot;Authorization: Bearer YOUR_FIREBASE_TOKEN&quot; https://$GATEWAY_URL/api/graph?limit=10"
echo ""
echo "3. Deploy frontend with new API URL"
echo ""