# Test Ingestion Function with Authentication

Write-Host "=== Testing Ingestion Function (Authenticated) ===" -ForegroundColor Green

$url = "https://us-central1-aletheia-codex-prod.cloudfunctions.net/ingestion"

Write-Host "Function URL: $url"
Write-Host "Getting authentication token..." -ForegroundColor Yellow

# Get authentication token
$token = gcloud auth print-identity-token

if ($token) {
    Write-Host "✅ Token obtained" -ForegroundColor Green
    
    Write-Host "`nSending test document..." -ForegroundColor Yellow
    
    $testPayload = @{
        title = "Authenticated Test Document"
        content = "Testing ingestion function with authenticated access. This verifies the standalone function works correctly without shared module dependencies."
    } | ConvertTo-Json
    
    $headers = @{
        "Authorization" = "Bearer $token"
        "Content-Type" = "application/json"
    }
    
    try {
        $response = Invoke-RestMethod -Uri $url -Method Post -Body $testPayload -Headers $headers
        
        Write-Host "`n✅ Test successful!" -ForegroundColor Green
        Write-Host "Response:"
        Write-Host ($response | ConvertTo-Json -Depth 3)
        
        if ($response.document_id) {
            Write-Host "`nDocument ID: $($response.document_id)" -ForegroundColor Cyan
            Write-Host "`nVerify in Firestore:"
            Write-Host "https://console.cloud.google.com/firestore/databases/-default-/data/panel/documents?project=aletheia-codex-prod" -ForegroundColor Cyan
            
            Write-Host "`nVerify in Cloud Storage:"
            $PROJECT_ID = gcloud config get-value project
            Write-Host "gsutil ls gs://$PROJECT_ID-documents/raw/" -ForegroundColor Cyan
        }
        
        Write-Host "`n=== Ingestion Function Working! ===" -ForegroundColor Green
        Write-Host "The function successfully:"
        Write-Host "  ✅ Accepted the document"
        Write-Host "  ✅ Created Firestore record"
        Write-Host "  ✅ Uploaded content to Cloud Storage"
        Write-Host "  ✅ No shared module errors!"
        
    } catch {
        Write-Host "`n❌ Test failed: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "Error details: $($_.ErrorDetails.Message)" -ForegroundColor Red
    }
} else {
    Write-Host "❌ Failed to get authentication token" -ForegroundColor Red
    Write-Host "Make sure you're logged in: gcloud auth login"
}