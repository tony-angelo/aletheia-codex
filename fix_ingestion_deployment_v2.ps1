# Fix Ingestion Deployment - Corrected for Gen2 and proper entry point

Write-Host "=== Fixing Ingestion Function Deployment ===" -ForegroundColor Green

# Get current project
$PROJECT_ID = gcloud config get-value project
Write-Host "Project: $PROJECT_ID"

# Step 1: Delete existing Cloud Run service if it exists
Write-Host "`nStep 1: Checking for existing Cloud Run service..." -ForegroundColor Yellow
$service = gcloud run services describe ingestion --region=us-central1 --format="value(name)" 2>$null

if ($service) {
    Write-Host "Found existing Cloud Run service. Deleting..." -ForegroundColor Red
    gcloud run services delete ingestion --region=us-central1 --quiet
    Write-Host "Cloud Run service deleted." -ForegroundColor Green
    Start-Sleep -Seconds 5
} else {
    Write-Host "No existing Cloud Run service found." -ForegroundColor Green
}

# Step 2: Deploy as Gen1 function (more stable for HTTP functions)
Write-Host "`nStep 2: Deploying ingestion function as Gen1..." -ForegroundColor Yellow
gcloud functions deploy ingestion `
    --gen2 `
    --runtime=python311 `
    --trigger-http `
    --allow-unauthenticated `
    --entry-point=ingest_document `
    --source=functions/ingestion `
    --region=us-central1 `
    --timeout=540s `
    --memory=512MB `
    --set-env-vars="GCP_PROJECT=$PROJECT_ID"

if ($LASTEXITCODE -ne 0) {
    Write-Host "`n❌ Deployment failed. Trying alternative approach..." -ForegroundColor Red
    
    # Alternative: Deploy as Gen1 function
    Write-Host "`nTrying Gen1 deployment..." -ForegroundColor Yellow
    gcloud functions deploy ingestion `
        --no-gen2 `
        --runtime=python311 `
        --trigger-http `
        --allow-unauthenticated `
        --entry-point=ingest_document `
        --source=functions/ingestion `
        --region=us-central1 `
        --timeout=540s `
        --memory=512MB `
        --set-env-vars="GCP_PROJECT=$PROJECT_ID"
}

# Step 3: Verify deployment
Write-Host "`nStep 3: Verifying deployment..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

$function = gcloud functions describe ingestion --region=us-central1 --format="value(status)" 2>$null
if ($function -eq "ACTIVE") {
    Write-Host "`n✅ Ingestion function deployed successfully!" -ForegroundColor Green
    $url = gcloud functions describe ingestion --region=us-central1 --format='value(serviceConfig.uri)' 2>$null
    if (-not $url) {
        $url = gcloud functions describe ingestion --region=us-central1 --format='value(httpsTrigger.url)' 2>$null
    }
    Write-Host "Function URL: $url"
    Write-Host "`nTest with:"
    Write-Host "curl -X POST $url -H 'Content-Type: application/json' -d '{`"title`":`"Test`",`"content`":`"Test content`"}'"
} else {
    Write-Host "`n❌ Failed to deploy ingestion function" -ForegroundColor Red
    Write-Host "Check logs at: https://console.cloud.google.com/functions/list?project=$PROJECT_ID"
    exit 1
}

Write-Host "`n=== Deployment Complete ===" -ForegroundColor Green