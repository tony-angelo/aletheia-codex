# Deploy a Cloud Function with shared dependencies
param(
    [Parameter(Mandatory=$true)]
    [string]$FunctionName,
    
    [Parameter(Mandatory=$true)]
    [string]$FunctionDir,
    
    [Parameter(Mandatory=$true)]
    [string]$EntryPoint,
    
    [string]$Region = "us-central1",
    [string]$Project = "aletheia-codex-prod"
)

$ErrorActionPreference = "Stop"

Write-Host "Preparing deployment for $FunctionName..." -ForegroundColor Cyan

# Create a temporary deployment directory
$deployDir = ".\deploy-temp"
if (Test-Path $deployDir) {
    Remove-Item -Recurse -Force $deployDir
}
New-Item -ItemType Directory -Path $deployDir | Out-Null

# Copy function code
Copy-Item -Path "$FunctionDir\*" -Destination $deployDir -Recurse

# Copy shared modules
Copy-Item -Path ".\shared" -Destination $deployDir -Recurse

Write-Host "Deploying function..." -ForegroundColor Cyan

# Deploy (without --allow-unauthenticated to avoid org policy issues)
gcloud functions deploy $FunctionName `
  --gen2 `
  --runtime=python313 `
  --region=$Region `
  --source=$deployDir `
  --entry-point=$EntryPoint `
  --trigger-http `
  --service-account=aletheia-functions@$Project.iam.gserviceaccount.com `
  --set-env-vars=GCP_PROJECT=$Project `
  --timeout=60s `
  --project=$Project

# Clean up
Remove-Item -Recurse -Force $deployDir

Write-Host "Deployment complete!" -ForegroundColor Green
