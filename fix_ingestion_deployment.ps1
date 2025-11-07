# Fix Ingestion Function Deployment
# Deletes the conflicting Cloud Run service and redeploys

$PROJECT_ID = "aletheia-codex-prod"
$REGION = "us-central1"

Write-Host "=== Fixing Ingestion Function Deployment ===" -ForegroundColor Cyan
Write-Host ""

# Check if the old Cloud Run service exists
Write-Host "Checking for conflicting Cloud Run service..." -ForegroundColor Yellow
$service = gcloud run services list --platform=managed --region=$REGION --project=$PROJECT_ID --filter="metadata.name:ingest-document" --format="value(metadata.name)" 2>$null

if ($service) {
    Write-Host "Found conflicting service: $service" -ForegroundColor Yellow
    Write-Host "Deleting old service..." -ForegroundColor Yellow
    
    try {
        gcloud run services delete $service --platform=managed --region=$REGION --project=$PROJECT_ID --quiet
        Write-Host "✓ Old service deleted" -ForegroundColor Green
    } catch {
        Write-Host "✗ Failed to delete service: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "You may need to delete it manually in Cloud Console" -ForegroundColor Yellow
        exit 1
    }
} else {
    Write-Host "No conflicting service found" -ForegroundColor Green
}

Write-Host ""
Write-Host "Deploying ingestion function..." -ForegroundColor Yellow

# Create deployment directory
$deployDir = "deploy-temp-ingestion"
New-Item -ItemType Directory -Path $deployDir -Force | Out-Null

# Copy function code
Copy-Item -Path "functions\ingestion\*" -Destination $deployDir -Recurse -Force

# Copy shared modules
Copy-Item -Path "shared" -Destination $deployDir -Recurse -Force

# Deploy
Set-Location $deployDir

try {
    gcloud functions deploy ingest_document `
        --gen2 `
        --runtime=python311 `
        --region=$REGION `
        --source=. `
        --entry-point=ingest_document `
        --trigger-http `
        --allow-unauthenticated `
        --service-account=aletheia-functions@$PROJECT_ID.iam.gserviceaccount.com `
        --timeout=540s `
        --memory=512MB `
        --set-env-vars=GCP_PROJECT=$PROJECT_ID `
        --project=$PROJECT_ID
    
    Set-Location ..
    Remove-Item -Recurse -Force $deployDir
    
    Write-Host ""
    Write-Host "✓ Ingestion function deployed successfully!" -ForegroundColor Green
    Write-Host "URL: https://$REGION-$PROJECT_ID.cloudfunctions.net/ingest_document" -ForegroundColor Cyan
    
} catch {
    Set-Location ..
    Remove-Item -Recurse -Force $deployDir
    Write-Host "✗ Deployment failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}