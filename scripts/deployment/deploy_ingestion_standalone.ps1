# Deploy Ingestion Function - Standalone Version (No shared dependencies)

Write-Host "=== Deploying Ingestion Function (Standalone) ===" -ForegroundColor Green

# Get current project
$PROJECT_ID = gcloud config get-value project
Write-Host "Project: $PROJECT_ID"

# Step 1: Backup original files
Write-Host "`nStep 1: Backing up original files..." -ForegroundColor Yellow
Copy-Item functions/ingestion/main.py functions/ingestion/main_original.py -Force
Copy-Item functions/ingestion/requirements.txt functions/ingestion/requirements_original.txt -Force
Write-Host "Backup complete." -ForegroundColor Green

# Step 2: Use standalone versions
Write-Host "`nStep 2: Switching to standalone versions..." -ForegroundColor Yellow
Copy-Item functions/ingestion/main_standalone.py functions/ingestion/main.py -Force
Copy-Item functions/ingestion/requirements_standalone.txt functions/ingestion/requirements.txt -Force
Write-Host "Standalone versions activated." -ForegroundColor Green

# Step 3: Delete existing Cloud Run service if it exists
Write-Host "`nStep 3: Checking for existing Cloud Run service..." -ForegroundColor Yellow
$service = gcloud run services describe ingestion --region=us-central1 --format="value(name)" 2>$null

if ($service) {
    Write-Host "Found existing Cloud Run service. Deleting..." -ForegroundColor Red
    gcloud run services delete ingestion --region=us-central1 --quiet
    Write-Host "Cloud Run service deleted." -ForegroundColor Green
    Start-Sleep -Seconds 5
} else {
    Write-Host "No existing Cloud Run service found." -ForegroundColor Green
}

# Step 4: Deploy function
Write-Host "`nStep 4: Deploying ingestion function..." -ForegroundColor Yellow
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
    Write-Host "`n❌ Gen2 deployment failed. Trying Gen1..." -ForegroundColor Red
    
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

# Step 5: Verify deployment
Write-Host "`nStep 5: Verifying deployment..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

$function = gcloud functions describe ingestion --region=us-central1 --format="value(status)" 2>$null
if ($function -eq "ACTIVE") {
    Write-Host "`n✅ Ingestion function deployed successfully!" -ForegroundColor Green
    
    # Get function URL
    $url = gcloud functions describe ingestion --region=us-central1 --format='value(serviceConfig.uri)' 2>$null
    if (-not $url) {
        $url = gcloud functions describe ingestion --region=us-central1 --format='value(httpsTrigger.url)' 2>$null
    }
    
    Write-Host "Function URL: $url"
    Write-Host "`nTest with:"
    Write-Host "curl -X POST `"$url`" -H 'Content-Type: application/json' -d '{`"title`":`"Test Doc`",`"content`":`"Test content`"}'"
    
    # Step 6: Restore original files
    Write-Host "`nStep 6: Restoring original files for version control..." -ForegroundColor Yellow
    Copy-Item functions/ingestion/main_original.py functions/ingestion/main.py -Force
    Copy-Item functions/ingestion/requirements_original.txt functions/ingestion/requirements.txt -Force
    Write-Host "Original files restored." -ForegroundColor Green
    
} else {
    Write-Host "`n❌ Failed to deploy ingestion function" -ForegroundColor Red
    Write-Host "Status: $function"
    Write-Host "Check logs at: https://console.cloud.google.com/functions/list?project=$PROJECT_ID"
    
    # Restore original files even on failure
    Copy-Item functions/ingestion/main_original.py functions/ingestion/main.py -Force
    Copy-Item functions/ingestion/requirements_original.txt functions/ingestion/requirements.txt -Force
    
    exit 1
}

Write-Host "`n=== Deployment Complete ===" -ForegroundColor Green
Write-Host "`nNote: The deployed function uses standalone code without shared dependencies."
Write-Host "Original files have been restored in your local repository."