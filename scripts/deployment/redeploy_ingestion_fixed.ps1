# Redeploy Ingestion Function - Permanently use standalone version

Write-Host "=== Redeploying Ingestion Function (Standalone) ===" -ForegroundColor Green

$PROJECT_ID = gcloud config get-value project
Write-Host "Project: $PROJECT_ID"

# Step 1: Switch to standalone version PERMANENTLY
Write-Host "`nStep 1: Switching to standalone version..." -ForegroundColor Yellow

# Backup current version
Copy-Item functions/ingestion/main.py functions/ingestion/main_with_shared.py -Force
Copy-Item functions/ingestion/requirements.txt functions/ingestion/requirements_with_shared.txt -Force

# Use standalone version
Copy-Item functions/ingestion/main_standalone.py functions/ingestion/main.py -Force
Copy-Item functions/ingestion/requirements_standalone.txt functions/ingestion/requirements.txt -Force

Write-Host "Standalone version activated." -ForegroundColor Green

# Step 2: Delete existing function
Write-Host "`nStep 2: Deleting existing function..." -ForegroundColor Yellow
gcloud functions delete ingestion --region=us-central1 --quiet 2>$null
Start-Sleep -Seconds 5
Write-Host "Function deleted." -ForegroundColor Green

# Step 3: Deploy standalone version
Write-Host "`nStep 3: Deploying standalone function..." -ForegroundColor Yellow
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

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ Deployment successful!" -ForegroundColor Green
    
    # Step 4: Verify deployment
    Write-Host "`nStep 4: Verifying deployment..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
    
    $function = gcloud functions describe ingestion --region=us-central1 --format="value(status)" 2>$null
    if ($function -eq "ACTIVE") {
        Write-Host "✅ Function is ACTIVE" -ForegroundColor Green
        
        $url = gcloud functions describe ingestion --region=us-central1 --format='value(httpsTrigger.url)' 2>$null
        Write-Host "`nFunction URL: $url"
        
        # Step 5: Test the function
        Write-Host "`nStep 5: Testing function..." -ForegroundColor Yellow
        
        $testPayload = @{
            title = "Deployment Test"
            content = "Testing standalone ingestion function after redeployment"
        } | ConvertTo-Json
        
        try {
            $response = Invoke-RestMethod -Uri $url -Method Post -Body $testPayload -ContentType "application/json"
            Write-Host "✅ Test successful!" -ForegroundColor Green
            Write-Host "Response: $($response | ConvertTo-Json)"
        } catch {
            Write-Host "⚠️  Test failed: $($_.Exception.Message)" -ForegroundColor Yellow
        }
        
        Write-Host "`n=== Deployment Complete ===" -ForegroundColor Green
        Write-Host "`nNote: The function is now using standalone code."
        Write-Host "Original files with shared imports are backed up as:"
        Write-Host "  - main_with_shared.py"
        Write-Host "  - requirements_with_shared.txt"
        
    } else {
        Write-Host "❌ Function status: $function" -ForegroundColor Red
    }
} else {
    Write-Host "`n❌ Deployment failed" -ForegroundColor Red
    
    # Restore original files on failure
    Write-Host "Restoring original files..." -ForegroundColor Yellow
    Copy-Item functions/ingestion/main_with_shared.py functions/ingestion/main.py -Force
    Copy-Item functions/ingestion/requirements_with_shared.txt functions/ingestion/requirements.txt -Force
    
    exit 1
}