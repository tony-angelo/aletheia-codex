# Fix Service Account Permissions for Ingestion Function

Write-Host "=== Fixing Service Account Permissions ===" -ForegroundColor Green

$PROJECT_ID = gcloud config get-value project
$SERVICE_ACCOUNT = "$PROJECT_ID@appspot.gserviceaccount.com"

Write-Host "Project: $PROJECT_ID"
Write-Host "Service Account: $SERVICE_ACCOUNT"
Write-Host ""

# Add Firestore permissions
Write-Host "Adding Firestore Data User role..." -ForegroundColor Yellow
gcloud projects add-iam-policy-binding $PROJECT_ID `
    --member="serviceAccount:$SERVICE_ACCOUNT" `
    --role="roles/datastore.user"

Write-Host ""

# Add Cloud Storage permissions
Write-Host "Adding Storage Object Admin role..." -ForegroundColor Yellow
gcloud projects add-iam-policy-binding $PROJECT_ID `
    --member="serviceAccount:$SERVICE_ACCOUNT" `
    --role="roles/storage.objectAdmin"

Write-Host ""

# Add Cloud Logging permissions
Write-Host "Adding Logging Writer role..." -ForegroundColor Yellow
gcloud projects add-iam-policy-binding $PROJECT_ID `
    --member="serviceAccount:$SERVICE_ACCOUNT" `
    --role="roles/logging.logWriter"

Write-Host ""

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Permissions updated successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "The service account now has:"
    Write-Host "  ✅ Firestore Data User - Read/write Firestore documents"
    Write-Host "  ✅ Storage Object Admin - Upload files to Cloud Storage"
    Write-Host "  ✅ Logging Writer - Write to Cloud Logging"
    Write-Host ""
    Write-Host "Wait 30 seconds for permissions to propagate, then test again:"
    Write-Host ".\test_ingestion_authenticated.ps1" -ForegroundColor Cyan
} else {
    Write-Host "❌ Failed to update permissions" -ForegroundColor Red
}