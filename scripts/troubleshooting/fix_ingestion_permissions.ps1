# Fix Ingestion Function Permissions

Write-Host "=== Fixing Ingestion Function Permissions ===" -ForegroundColor Green

# Add IAM policy to allow unauthenticated access
Write-Host "Adding IAM policy for public access..." -ForegroundColor Yellow

gcloud functions add-iam-policy-binding ingestion `
    --region=us-central1 `
    --member=allUsers `
    --role=roles/cloudfunctions.invoker

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ Permissions updated successfully!" -ForegroundColor Green
    
    # Test the function
    Write-Host "`nTesting function..." -ForegroundColor Yellow
    $url = "https://us-central1-aletheia-codex-prod.cloudfunctions.net/ingestion"
    
    $testPayload = @{
        title = "Permission Test"
        content = "Testing ingestion function after fixing permissions"
    } | ConvertTo-Json
    
    try {
        $response = Invoke-RestMethod -Uri $url -Method Post -Body $testPayload -ContentType "application/json"
        Write-Host "`n✅ Test successful!" -ForegroundColor Green
        Write-Host "Response:"
        Write-Host ($response | ConvertTo-Json -Depth 3)
        
        if ($response.document_id) {
            Write-Host "`nDocument ID: $($response.document_id)" -ForegroundColor Cyan
            Write-Host "Check Firestore: https://console.cloud.google.com/firestore/databases/-default-/data/panel/documents?project=aletheia-codex-prod" -ForegroundColor Cyan
        }
    } catch {
        Write-Host "`n❌ Test failed: $($_.Exception.Message)" -ForegroundColor Red
    }
} else {
    Write-Host "`n❌ Failed to update permissions" -ForegroundColor Red
}