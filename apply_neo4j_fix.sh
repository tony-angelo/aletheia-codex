#!/bin/bash

# Script to apply Neo4j authentication fix
# This script replaces the cached driver implementation with a fresh-driver approach

set -e  # Exit on error

echo "================================================"
echo "Neo4j Authentication Fix - Deployment Script"
echo "================================================"
echo ""

# Check if we're in the right directory
if [ ! -f "shared/db/neo4j_client.py" ]; then
    echo "Error: Must run this script from the aletheia-codex directory"
    exit 1
fi

# Backup original file
echo "[1/5] Backing up original neo4j_client.py..."
cp shared/db/neo4j_client.py shared/db/neo4j_client.py.backup
echo "✓ Backup created: shared/db/neo4j_client.py.backup"
echo ""

# Apply the fix
echo "[2/5] Applying fix (replacing with neo4j_client_fixed.py)..."
cp shared/db/neo4j_client_fixed.py shared/db/neo4j_client.py
echo "✓ Fix applied"
echo ""

# Commit changes
echo "[3/5] Committing changes to git..."
git add shared/db/neo4j_client.py
git commit -m "Fix: Remove Neo4j driver caching to resolve Cloud Function auth issues

- Removed module-level driver singleton
- Create fresh driver on each invocation
- Added immediate connectivity verification
- Added comprehensive logging
- Proper resource management with context managers

This fixes the authentication issue where Cloud Functions reuse
instances with stale/failed driver connections."
echo "✓ Changes committed"
echo ""

# Push to GitHub
echo "[4/5] Pushing to GitHub..."
git push origin main
echo "✓ Pushed to GitHub"
echo ""

# Deploy to Cloud Functions
echo "[5/5] Deploying to Cloud Functions..."
echo "Running deployment script..."

cd functions/orchestration

# Check if deploy script exists
if [ -f "../../infrastructure/deploy-function.ps1" ]; then
    echo "Note: Found PowerShell deployment script."
    echo "Please run the following command in PowerShell:"
    echo ""
    echo "  cd functions/orchestration"
    echo "  ../../infrastructure/deploy-function.ps1"
    echo ""
else
    # Deploy using gcloud directly
    echo "Deploying with gcloud..."
    gcloud functions deploy orchestrate \
        --gen2 \
        --runtime=python311 \
        --region=us-central1 \
        --source=. \
        --entry-point=orchestrate \
        --trigger-http \
        --service-account=aletheia-functions@aletheia-codex-prod.iam.gserviceaccount.com \
        --timeout=540s \
        --memory=512MB
    
    echo "✓ Deployed to Cloud Functions"
fi

cd ../..

echo ""
echo "================================================"
echo "✓ Fix Applied Successfully!"
echo "================================================"
echo ""
echo "Next steps:"
echo "1. Test the function with a sample document"
echo "2. Check logs: gcloud functions logs read orchestrate --region=us-central1 --limit=50"
echo "3. Look for: '✓ Neo4j connection verified successfully'"
echo ""
echo "If issues persist, see TROUBLESHOOTING_GUIDE.md for additional solutions."