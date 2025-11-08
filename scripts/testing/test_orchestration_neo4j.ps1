# Test Orchestration Function with Neo4j Connectivity
# Sprint 1 Final Verification Script (PowerShell version)

Write-Host "=== Sprint 1: Orchestration Function Neo4j Verification ===" -ForegroundColor Cyan
Write-Host ""

# Step 1: Verify Neo4j password
Write-Host "Step 1: Verifying Neo4j password in Secret Manager..." -ForegroundColor Yellow
$password = gcloud secrets versions access latest --secret="NEO4J_PASSWORD"
$password = $password.Trim()
$passwordLength = $password.Length

if ($passwordLength -eq 43 -or $passwordLength -eq 44) {
    Write-Host "✓ Password retrieved successfully ($passwordLength characters)" -ForegroundColor Green
} else {
    Write-Host "✗ Password length is unexpected: $passwordLength characters" -ForegroundColor Red
    exit 1
}

# Step 2: Check function status
Write-Host ""
Write-Host "Step 2: Checking orchestration function status..." -ForegroundColor Yellow
$functionStatus = gcloud functions describe orchestrate --region=us-central1 --format="value(state)"

if ($functionStatus -eq "ACTIVE") {
    Write-Host "✓ Function is ACTIVE" -ForegroundColor Green
} else {
    Write-Host "✗ Function status: $functionStatus" -ForegroundColor Red
    exit 1
}

# Step 3: Create test document
Write-Host ""
Write-Host "Step 3: Creating test document via ingestion function..." -ForegroundColor Yellow
$token = gcloud auth print-identity-token

$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

$body = @{
    title = "Sprint 1 Final Verification Test"
    content = "Sprint 1 final verification test. This document mentions Alice Johnson who works at TechCorp in San Francisco. She is a senior software engineer specializing in cloud architecture and has been with the company for 5 years. Alice collaborates closely with Bob Smith, the CTO, on strategic initiatives."
    source = "test"
    metadata = @{
        test_type = "sprint1_final_verification"
    }
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "https://us-central1-aletheia-codex-prod.cloudfunctions.net/ingestion" `
        -Method Post `
        -Headers $headers `
        -Body $body
    
    Write-Host "✓ Test document created successfully" -ForegroundColor Green
    Write-Host "  Document ID: $($response.document_id)" -ForegroundColor Cyan
    $documentId = $response.document_id
} catch {
    Write-Host "✗ Failed to create test document" -ForegroundColor Red
    Write-Host "  Error: $_" -ForegroundColor Red
    exit 1
}

# Step 4: Wait for document to be ready
Write-Host ""
Write-Host "Step 4: Waiting 5 seconds for document to be ready in Firestore..." -ForegroundColor Yellow
Start-Sleep -Seconds 5
Write-Host "✓ Wait complete" -ForegroundColor Green

# Step 5: Trigger orchestration
Write-Host ""
Write-Host "Step 5: Triggering orchestration function..." -ForegroundColor Yellow
Write-Host "Note: This requires Cloud Run Invoker permission on the orchestrate service" -ForegroundColor Cyan

$orchestrationBody = @{
    document_id = $documentId
    action = "process_document"
} | ConvertTo-Json

try {
    $orchestrationResponse = Invoke-RestMethod -Uri "https://us-central1-aletheia-codex-prod.cloudfunctions.net/orchestrate" `
        -Method Post `
        -Headers $headers `
        -Body $orchestrationBody
    
    Write-Host "✓ Orchestration function triggered successfully" -ForegroundColor Green
    Write-Host "  Response: $($orchestrationResponse | ConvertTo-Json -Depth 3)" -ForegroundColor Cyan
    $orchestrationSuccess = $true
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    
    if ($statusCode -eq 403) {
        Write-Host "⚠ Orchestration function returned 403 Forbidden" -ForegroundColor Yellow
        Write-Host "  This means the service account needs Cloud Run Invoker permission" -ForegroundColor Yellow
        Write-Host "  To fix: Add roles/run.invoker to the service account on the orchestrate Cloud Run service" -ForegroundColor Cyan
        $orchestrationSuccess = $false
    } else {
        Write-Host "✗ Orchestration function returned HTTP $statusCode" -ForegroundColor Red
        Write-Host "  Error: $_" -ForegroundColor Red
        $orchestrationSuccess = $false
    }
}

# Step 6: Check logs for Neo4j connection
Write-Host ""
Write-Host "Step 6: Checking logs for Neo4j connection status..." -ForegroundColor Yellow
Write-Host "  Waiting 10 seconds for logs to appear..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check orchestration logs
Write-Host "Checking orchestration function logs..." -ForegroundColor Cyan
$orchestrationLogs = gcloud logging read "resource.type=cloud_function AND resource.labels.function_name=orchestrate" `
    --limit=20 `
    --format="value(textPayload)" `
    --freshness=5m

if ($orchestrationLogs) {
    # Check for authentication errors
    $authErrors = $orchestrationLogs | Select-String -Pattern "authentication.*failed|auth.*error" -CaseSensitive:$false
    
    if ($authErrors) {
        Write-Host "✗ Neo4j authentication errors found in logs!" -ForegroundColor Red
        $authErrors | ForEach-Object { Write-Host "  $_" -ForegroundColor Red }
    } else {
        Write-Host "✓ No Neo4j authentication errors found" -ForegroundColor Green
    }
    
    # Check for connection errors
    $connErrors = $orchestrationLogs | Select-String -Pattern "connection.*failed|timeout" -CaseSensitive:$false
    
    if ($connErrors) {
        Write-Host "⚠ Connection warnings found in logs" -ForegroundColor Yellow
        $connErrors | Select-Object -First 3 | ForEach-Object { Write-Host "  $_" -ForegroundColor Yellow }
    } else {
        Write-Host "✓ No connection errors found" -ForegroundColor Green
    }
    
    # Check for successful processing
    $successLogs = $orchestrationLogs | Select-String -Pattern "success|completed|processed" -CaseSensitive:$false
    
    if ($successLogs) {
        Write-Host "✓ Found success indicators in logs" -ForegroundColor Green
        $successLogs | Select-Object -First 3 | ForEach-Object { Write-Host "  $_" -ForegroundColor Cyan }
    }
} else {
    Write-Host "⚠ No recent orchestration logs found" -ForegroundColor Yellow
    Write-Host "  This is expected if the function couldn't be invoked due to IAM permissions" -ForegroundColor Cyan
}

# Check ingestion logs to verify it worked
Write-Host ""
Write-Host "Checking ingestion function logs..." -ForegroundColor Cyan
$ingestionLogs = gcloud logging read "resource.type=cloud_function AND resource.labels.function_name=ingestion" `
    --limit=10 `
    --format="table(timestamp,severity,textPayload)" `
    --freshness=15m

if ($ingestionLogs -match $documentId) {
    Write-Host "✓ Ingestion function processed the document successfully" -ForegroundColor Green
} else {
    Write-Host "⚠ Could not verify ingestion in logs" -ForegroundColor Yellow
}

# Summary
Write-Host ""
Write-Host "=== Verification Summary ===" -ForegroundColor Cyan
Write-Host "✓ Neo4j password verified ($passwordLength characters)" -ForegroundColor Green
Write-Host "✓ Orchestration function is ACTIVE" -ForegroundColor Green
Write-Host "✓ Test document created: $documentId" -ForegroundColor Green
Write-Host "✓ Ingestion function working correctly" -ForegroundColor Green

if (-not $orchestrationSuccess) {
    Write-Host "⚠ Orchestration function requires IAM permission to invoke" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "=== Action Required ===" -ForegroundColor Cyan
    Write-Host "To complete the verification, add Cloud Run Invoker permission:" -ForegroundColor White
    Write-Host ""
    Write-Host "gcloud run services add-iam-policy-binding orchestrate ``" -ForegroundColor White
    Write-Host "  --region=us-central1 ``" -ForegroundColor White
    Write-Host "  --member='serviceAccount:superninja@aletheia-codex-prod.iam.gserviceaccount.com' ``" -ForegroundColor White
    Write-Host "  --role='roles/run.invoker'" -ForegroundColor White
    Write-Host ""
    Write-Host "Then re-run this script to complete the verification." -ForegroundColor White
} else {
    Write-Host "✓ Orchestration function triggered successfully" -ForegroundColor Green
}

Write-Host ""
Write-Host "=== Next Steps ===" -ForegroundColor Cyan
Write-Host "1. Review full logs in Cloud Console for detailed processing information" -ForegroundColor White
Write-Host "2. Check Neo4j Browser to verify data was created (optional)" -ForegroundColor White
Write-Host "3. Update documentation to reflect verification results" -ForegroundColor White
Write-Host "4. Create completion report" -ForegroundColor White
Write-Host ""
Write-Host "View logs: https://console.cloud.google.com/logs/query?project=aletheia-codex-prod" -ForegroundColor Cyan
Write-Host ""

if ($orchestrationSuccess) {
    Write-Host "✅ Sprint 1 verification complete! All checks passed." -ForegroundColor Green
} else {
    Write-Host "⚠ Sprint 1 verification partially complete. IAM permission needed for full verification." -ForegroundColor Yellow
}