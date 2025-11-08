# Cleanup and Deploy Ingestion Function

Write-Host "=== Cleanup and Deploy Ingestion Function ===" -ForegroundColor Green

$PROJECT_ID = gcloud config get-value project
Write-Host "Project: $PROJECT_ID"

# Step 1: Delete ALL existing ingestion-related functions and services
Write-Host "`nStep 1: Cleaning up existing functions and services..." -ForegroundColor Yellow

# Delete Gen2 function if exists
Write-Host "Deleting Gen2 function 'ingestion'..." -ForegroundColor Yellow
gcloud functions delete ingestion --region=us-central1 --gen2 --quiet 2>$null
Start-Sleep -Seconds 3

# Delete Gen1 function if exists
Write-Host "Deleting Gen1 function 'ingestion'..." -ForegroundColor Yellow
gcloud functions delete ingestion --region=us-central1 --quiet 2>$null
Start-Sleep -Seconds 3

# Delete the old 'ingest-document' function if exists
Write-Host "Deleting old 'ingest-document' function..." -ForegroundColor Yellow
gcloud functions delete ingest-document --region=us-central1 --quiet 2>$null
Start-Sleep -Seconds 3

# Delete Cloud Run service if exists
Write-Host "Deleting Cloud Run service 'ingestion'..." -ForegroundColor Yellow
gcloud run services delete ingestion --region=us-central1 --quiet 2>$null
Start-Sleep -Seconds 5

Write-Host "Cleanup complete." -ForegroundColor Green

# Step 2: Prepare standalone files
Write-Host "`nStep 2: Preparing standalone files..." -ForegroundColor Yellow
Copy-Item functions/ingestion/main.py functions/ingestion/main_original.py -Force
Copy-Item functions/ingestion/requirements.txt functions/ingestion/requirements_original.txt -Force
Copy-Item functions/ingestion/main_standalone.py functions/ingestion/main.py -Force
Copy-Item functions/ingestion/requirements_standalone.txt functions/ingestion/requirements.txt -Force
Write-Host "Standalone files ready." -ForegroundColor Green

# Step 3: Deploy as Gen1 function (more stable, avoids org policy issues)
Write-Host "`nStep 3: Deploying as Gen1 function..." -ForegroundColor Yellow
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

$deployResult = $LASTEXITCODE

# Step 4: Restore original files
Write-Host "`nStep 4: Restoring original files..." -ForegroundColor Yellow
Copy-Item functions/ingestion/main_original.py functions/ingestion/main.py -Force
Copy-Item functions/ingestion/requirements_original.txt functions/ingestion/requirements.txt -Force
Write-Host "Original files restored." -ForegroundColor Green

# Step 5: Verify deployment
if ($deployResult -eq 0) {
    Write-Host "`nStep 5: Verifying deployment..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
    
    $function = gcloud functions describe ingestion --region=us-central1 --format="value(status)" 2>$null
    if ($function -eq "ACTIVE") {
        Write-Host "`n✅ Ingestion function deployed successfully!" -ForegroundColor Green
        
        $url = gcloud functions describe ingestion --region=us-central1 --format='value(httpsTrigger.url)' 2>$null
        Write-Host "Function URL: $url"
        Write-Host "`nTest with:"
        Write-Host "curl -X POST `"$url`" -H 'Content-Type: application/json' -d '{`"title`":`"Test`",`"content`":`"Test content`"}'"
        
        Write-Host "`n=== Deployment Complete ===" -ForegroundColor Green
    } else {
        Write-Host "`n❌ Deployment verification failed" -ForegroundColor Red
        Write-Host "Status: $function"
    }
} else {
    Write-Host "`n❌ Deployment failed" -ForegroundColor Red
    Write-Host "Check logs at: https://console.cloud.google.com/functions/list?project=$PROJECT_ID"
    exit 1
}