# Deploy All Functions Script
# Deploys ingestion, orchestration, and retrieval functions

param(
    [string]$Project = "aletheia-codex-prod",
    [string]$Region = "us-central1"
)

$ErrorActionPreference = "Stop"

Write-Host "=== Deploying All AletheiaCodex Functions ===" -ForegroundColor Cyan
Write-Host "Project: $Project" -ForegroundColor Gray
Write-Host "Region: $Region" -ForegroundColor Gray
Write-Host ""

# Function to deploy a Cloud Function
function Deploy-CloudFunction {
    param(
        [string]$Name,
        [string]$SourceDir,
        [string]$EntryPoint
    )
    
    Write-Host "[$Name] Deploying..." -ForegroundColor Yellow
    
    try {
        # Create deployment directory
        $deployDir = "deploy-temp-$Name"
        New-Item -ItemType Directory -Path $deployDir -Force | Out-Null
        
        # Copy function code
        Copy-Item -Path "$SourceDir\*" -Destination $deployDir -Recurse -Force
        
        # Copy shared modules
        Copy-Item -Path "shared" -Destination $deployDir -Recurse -Force
        
        # Deploy
        Set-Location $deployDir
        
        gcloud functions deploy $Name `
            --gen2 `
            --runtime=python311 `
            --region=$Region `
            --source=. `
            --entry-point=$EntryPoint `
            --trigger-http `
            --service-account=aletheia-functions@$Project.iam.gserviceaccount.com `
            --timeout=540s `
            --memory=512MB `
            --set-env-vars=GCP_PROJECT=$Project `
            --project=$Project
        
        Set-Location ..
        
        # Clean up
        Remove-Item -Recurse -Force $deployDir
        
        Write-Host "[$Name] Deployed successfully!" -ForegroundColor Green
        Write-Host ""
        
        return $true
    }
    catch {
        Write-Host "[$Name] Deployment failed: $($_.Exception.Message)" -ForegroundColor Red
        Set-Location ..
        if (Test-Path $deployDir) {
            Remove-Item -Recurse -Force $deployDir
        }
        return $false
    }
}

# Deploy functions
$results = @{}

Write-Host "=== Deploying Functions ===" -ForegroundColor Cyan
Write-Host ""

# 1. Ingestion Function
$results["ingestion"] = Deploy-CloudFunction -Name "ingest_document" -SourceDir "functions\ingestion" -EntryPoint "ingest_document"

# 2. Orchestration Function
$results["orchestration"] = Deploy-CloudFunction -Name "orchestrate" -SourceDir "functions\orchestration" -EntryPoint "orchestrate"

# 3. Retrieval Function (optional - currently a stub)
# $results["retrieval"] = Deploy-CloudFunction -Name "retrieve" -SourceDir "functions\retrieval" -EntryPoint "main"

# Summary
Write-Host "=== Deployment Summary ===" -ForegroundColor Cyan
Write-Host ""

foreach ($func in $results.Keys) {
    if ($results[$func]) {
        $status = "SUCCESS"
        $color = "Green"
    } else {
        $status = "FAILED"
        $color = "Red"
    }
    Write-Host "$func : $status" -ForegroundColor $color
}

Write-Host ""

if ($results.Values -contains $false) {
    Write-Host "Some deployments failed. Check the errors above." -ForegroundColor Red
    exit 1
} else {
    Write-Host "All deployments successful!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Function URLs:" -ForegroundColor Yellow
    Write-Host "  Ingestion: https://$Region-$Project.cloudfunctions.net/ingest_document"
    Write-Host "  Orchestration: https://$Region-$Project.cloudfunctions.net/orchestrate"
    Write-Host ""
    exit 0
}