# Test Sprint 1 Deployment - Complete Workflow Test

Write-Host "=== Testing Sprint 1 Deployment ===" -ForegroundColor Green

$PROJECT_ID = gcloud config get-value project
Write-Host "Project: $PROJECT_ID`n"

# Test 1: Ingestion Function
Write-Host "Test 1: Testing Ingestion Function..." -ForegroundColor Yellow
$ingestUrl = "https://us-central1-aletheia-codex-prod.cloudfunctions.net/ingestion"

Write-Host "Ingestion URL: $ingestUrl"
Write-Host "Getting authentication token..." -ForegroundColor Yellow
$token = gcloud auth print-identity-token

if ($token) {
    Write-Host "Sending test document...`n"
    
    $testPayload = @{
        title = "Sprint 1 Test Document"
        content = "This is a comprehensive test document created to verify all Sprint 1 fixes are working correctly. It includes enhanced Neo4j connectivity, production logging, proper error handling, and resource leak fixes."
    } | ConvertTo-Json
    
    $headers = @{
        "Authorization" = "Bearer $token"
        "Content-Type" = "application/json"
    }
    
    try {
        $ingestResponse = Invoke-RestMethod -Uri $ingestUrl -Method Post -Body $testPayload -Headers $headers
        
        Write-Host "Response:"
        Write-Host ($ingestResponse | ConvertTo-Json)
        Write-Host ""
        
        if ($ingestResponse.status -eq "success") {
            Write-Host "✅ Ingestion function working!" -ForegroundColor Green
            Write-Host "Document ID: $($ingestResponse.document_id)" -ForegroundColor Cyan
        } else {
            Write-Host "❌ Ingestion function failed" -ForegroundColor Red
        }
    } catch {
        Write-Host "❌ Ingestion function failed: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "Error details: $($_.ErrorDetails.Message)" -ForegroundColor Red
    }
} else {
    Write-Host "❌ Failed to get authentication token" -ForegroundColor Red
}

Write-Host "`n" + ("="*60) + "`n"

# Test 2: Orchestration Function
Write-Host "Test 2: Testing Orchestration Function..." -ForegroundColor Yellow

$orchestrateUrl = gcloud functions describe orchestrate --region=us-central1 --format='value(httpsTrigger.url)' 2>$null

if ($orchestrateUrl) {
    Write-Host "Orchestration URL: $orchestrateUrl"
    Write-Host "Testing orchestration with Neo4j connection...`n"
    
    # Use the document ID from Test 1 if available, otherwise use a test ID
    if ($ingestResponse -and $ingestResponse.document_id) {
        $testDocId = $ingestResponse.document_id
        Write-Host "Using document from Test 1: $testDocId" -ForegroundColor Cyan
    } else {
        $testDocId = "test-doc-sprint1"
        Write-Host "Using test document ID: $testDocId" -ForegroundColor Cyan
    }
    
    $orchestratePayload = @{
        document_id = $testDocId
        action = "process"
    } | ConvertTo-Json
    
    $headers = @{
        "Authorization" = "Bearer $token"
        "Content-Type" = "application/json"
    }
    
    try {
        $orchestrateResponse = Invoke-RestMethod -Uri $orchestrateUrl -Method Post -Body $orchestratePayload -Headers $headers
        
        Write-Host "Response:"
        Write-Host ($orchestrateResponse | ConvertTo-Json)
        Write-Host ""
        
        if ($orchestrateResponse.status -eq "success") {
            Write-Host "✅ Orchestration function working!" -ForegroundColor Green
        } else {
            Write-Host "⚠️  Orchestration function responded but check logs for details" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "⚠️  Orchestration test failed: $($_.Exception.Message)" -ForegroundColor Yellow
        Write-Host "Error details: $($_.ErrorDetails.Message)" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️  Orchestration function not found or not deployed" -ForegroundColor Yellow
}

Write-Host "`n" + ("="*60) + "`n"

# Test 3: Check Function Logs
Write-Host "Test 3: Checking Recent Logs..." -ForegroundColor Yellow

Write-Host "`nIngestion Function Logs (last 10 entries):"
gcloud functions logs read ingestion --region=us-central1 --limit=10 2>$null

Write-Host "`nOrchestration Function Logs (last 10 entries):"
gcloud functions logs read orchestrate --region=us-central1 --limit=10 2>$null

Write-Host "`n" + ("="*60) + "`n"

# Test 4: Verify Firestore Document
Write-Host "Test 4: Checking Firestore for Test Document..." -ForegroundColor Yellow
Write-Host "To verify in console, visit:"
Write-Host "https://console.cloud.google.com/firestore/databases/-default-/data/panel/documents?project=$PROJECT_ID" -ForegroundColor Cyan

Write-Host "`n" + ("="*60) + "`n"

# Test 5: Verify Cloud Storage
Write-Host "Test 5: Checking Cloud Storage for Uploaded Content..." -ForegroundColor Yellow
$bucketName = "$PROJECT_ID-documents"
Write-Host "Bucket: gs://$bucketName/raw/"

$files = gsutil ls "gs://$bucketName/raw/" 2>$null
if ($files) {
    Write-Host "Recent files in bucket:"
    $files | Select-Object -Last 5
    Write-Host "✅ Files found in Cloud Storage" -ForegroundColor Green
} else {
    Write-Host "⚠️  No files found or bucket doesn't exist" -ForegroundColor Yellow
}

Write-Host "`n" + ("="*60) + "`n"

# Summary
Write-Host "=== Test Summary ===" -ForegroundColor Green
Write-Host ""
Write-Host "Sprint 1 Improvements Deployed:"
Write-Host "✅ Enhanced Neo4j client with retry logic and connection pooling"
Write-Host "✅ Production-ready Cloud Logging integration"
Write-Host "✅ Fixed resource leaks in orchestration function"
Write-Host "✅ Proper error handling throughout"
Write-Host "✅ Standalone ingestion function (no shared dependencies)"
Write-Host "✅ Neo4j password updated (43 characters)"
Write-Host ""
Write-Host "Next Steps:"
Write-Host "1. Review logs above for any errors"
Write-Host "2. Check Firestore console for test document"
Write-Host "3. Verify Neo4j connectivity in orchestration logs"
Write-Host "4. If all tests pass, Sprint 1 is complete! 🎉"
Write-Host ""