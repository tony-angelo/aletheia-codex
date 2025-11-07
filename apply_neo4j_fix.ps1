# Script to apply Neo4j authentication fix
# This script replaces the cached driver implementation with a fresh-driver approach

$ErrorActionPreference = "Stop"

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Neo4j Authentication Fix - Deployment Script" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "shared/db/neo4j_client.py")) {
    Write-Host "Error: Must run this script from the aletheia-codex directory" -ForegroundColor Red
    exit 1
}

# Backup original file
Write-Host "[1/5] Backing up original neo4j_client.py..." -ForegroundColor Yellow
Copy-Item "shared/db/neo4j_client.py" "shared/db/neo4j_client.py.backup"
Write-Host "Backup created: shared/db/neo4j_client.py.backup" -ForegroundColor Green
Write-Host ""

# Apply the fix
Write-Host "[2/5] Applying fix (replacing with neo4j_client_fixed.py)..." -ForegroundColor Yellow
Copy-Item "shared/db/neo4j_client_fixed.py" "shared/db/neo4j_client.py"
Write-Host "Fix applied" -ForegroundColor Green
Write-Host ""

# Commit changes
Write-Host "[3/5] Committing changes to git..." -ForegroundColor Yellow
git add shared/db/neo4j_client.py
git commit -m "Fix: Remove Neo4j driver caching to resolve Cloud Function auth issues

- Removed module-level driver singleton
- Create fresh driver on each invocation
- Added immediate connectivity verification
- Added comprehensive logging
- Proper resource management with context managers

This fixes the authentication issue where Cloud Functions reuse
instances with stale/failed driver connections."
Write-Host "Changes committed" -ForegroundColor Green
Write-Host ""

# Push to GitHub
Write-Host "[4/5] Pushing to GitHub..." -ForegroundColor Yellow
git push origin main
Write-Host "Pushed to GitHub" -ForegroundColor Green
Write-Host ""

# Deploy to Cloud Functions
Write-Host "[5/5] Deploying to Cloud Functions..." -ForegroundColor Yellow
Write-Host "Running deployment script..." -ForegroundColor Yellow

if (Test-Path "infrastructure/deploy-function.ps1") {
    & "infrastructure/deploy-function.ps1"
    Write-Host "Deployed to Cloud Functions" -ForegroundColor Green
} else {
    Write-Host "Deployment script not found. Please deploy manually:" -ForegroundColor Yellow
    Write-Host "  cd functions/orchestration" -ForegroundColor White
    Write-Host "  gcloud functions deploy orchestrate --gen2 --runtime=python311 --region=us-central1 --source=. --entry-point=orchestrate --trigger-http --service-account=aletheia-functions@aletheia-codex-prod.iam.gserviceaccount.com" -ForegroundColor White
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Fix Applied Successfully!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Test the function with a sample document"
Write-Host "2. Check logs: gcloud functions logs read orchestrate --region=us-central1 --limit=50"
Write-Host "3. Look for: 'Neo4j connection verified successfully'"
Write-Host ""
Write-Host "If issues persist, see TROUBLESHOOTING_GUIDE.md for additional solutions." -ForegroundColor Cyan