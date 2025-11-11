#!/bin/bash
# Deploy Cloud Functions with Firebase Authentication
# Sprint 6: Authentication Implementation

PROJECT_ID="aletheia-codex-prod"
REGION="us-central1"

echo "=========================================="
echo "Deploying Authenticated Cloud Functions"
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "=========================================="

# Authenticate and set project
echo "Setting up GCP authentication..."
gcloud config set project $PROJECT_ID

# Get the current directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "Working from directory: $SCRIPT_DIR"

# Function to copy shared directory
copy_shared() {
    local target_dir=$1
    echo "Copying shared directory to $target_dir..."
    
    # Remove existing shared directory if it exists
    if [ -d "$target_dir/shared" ]; then
        rm -rf "$target_dir/shared"
    fi
    
    # Copy the complete shared directory from root
    cp -r "$SCRIPT_DIR/shared" "$target_dir/"
    
    echo "Shared directory copied successfully"
}

# Function to grant invoker permissions (may fail due to org policy)
grant_invoker_permissions() {
    local function_name=$1
    echo "Attempting to grant invoker permissions to $function_name..."
    
    if gcloud functions add-invoker-policy-binding $function_name \
        --region=$REGION \
        --member=allUsers 2>&1; then
        echo "✓ Invoker permissions granted successfully"
    else
        echo "⚠ Could not grant invoker permissions (organization policy restriction)"
        echo "  This is expected and OK - the function will work with Firebase Authentication"
    fi
}

# Deploy Notes API
echo ""
echo "=========================================="
echo "Deploying Notes API Function..."
echo "=========================================="
cd "$SCRIPT_DIR/functions/notes_api"

# Copy shared directory
copy_shared "$SCRIPT_DIR/functions/notes_api"

if echo "N" | gcloud functions deploy notes-api-function \
  --gen2 \
  --runtime=python311 \
  --region=$REGION \
  --source=. \
  --entry-point=notes_api \
  --trigger-http \
  --service-account=aletheia-functions@${PROJECT_ID}.iam.gserviceaccount.com \
  --set-env-vars GCP_PROJECT=$PROJECT_ID \
  --memory=512MB \
  --timeout=60s; then
    echo "✓ Notes API deployed successfully"
    grant_invoker_permissions "notes-api-function"
else
    echo "✗ Notes API deployment failed"
    exit 1
fi

# Deploy Review API
echo ""
echo "=========================================="
echo "Deploying Review API Function..."
echo "=========================================="
cd "$SCRIPT_DIR/functions/review_api"

# Copy shared directory
copy_shared "$SCRIPT_DIR/functions/review_api"

if echo "N" | gcloud functions deploy review-api-function \
  --gen2 \
  --runtime=python311 \
  --region=$REGION \
  --source=. \
  --entry-point=handle_request \
  --trigger-http \
  --service-account=aletheia-functions@${PROJECT_ID}.iam.gserviceaccount.com \
  --set-env-vars GCP_PROJECT=$PROJECT_ID \
  --memory=512MB \
  --timeout=60s; then
    echo "✓ Review API deployed successfully"
    grant_invoker_permissions "review-api-function"
else
    echo "✗ Review API deployment failed"
    exit 1
fi

# Deploy Graph Function
echo ""
echo "=========================================="
echo "Deploying Graph Function..."
echo "=========================================="
cd "$SCRIPT_DIR/functions/graph"

# Copy shared directory
copy_shared "$SCRIPT_DIR/functions/graph"

if echo "N" | gcloud functions deploy graph-function \
  --gen2 \
  --runtime=python311 \
  --region=$REGION \
  --source=. \
  --entry-point=graph_function \
  --trigger-http \
  --service-account=aletheia-functions@${PROJECT_ID}.iam.gserviceaccount.com \
  --set-env-vars GCP_PROJECT=$PROJECT_ID \
  --memory=512MB \
  --timeout=60s; then
    echo "✓ Graph API deployed successfully"
    grant_invoker_permissions "graph-function"
else
    echo "✗ Graph API deployment failed"
    exit 1
fi

cd "$SCRIPT_DIR"

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
echo "Note: Invoker permissions may not be granted due to organization policy."
echo "This is expected and correct - functions verify Firebase tokens internally."
echo ""