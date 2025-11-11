# Deploy orchestration function with AI integration
# PowerShell script for Windows users

Write-Host "Deploying orchestration function with AI integration..." -ForegroundColor Green

Set-Location functions/orchestration

gcloud functions deploy orchestrate `
    --gen2 `
    --runtime=python311 `
    --region=us-central1 `
    --source=. `
    --entry-point=orchestrate `
    --trigger-http `
    --service-account=aletheia-functions@aletheia-codex-prod.iam.gserviceaccount.com `
    --timeout=540s `
    --memory=512MB `
    --set-env-vars GCP_PROJECT=aletheia-codex-prod `
    --allow-unauthenticated

if ($LASTEXITCODE -eq 0) {
    Write-Host "Deployment complete!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Verifying deployment..." -ForegroundColor Yellow
    gcloud functions describe orchestrate --region=us-central1 --gen2
    
    Write-Host ""
    Write-Host "Function URL:" -ForegroundColor Yellow
    gcloud functions describe orchestrate --region=us-central1 --gen2 --format='value(serviceConfig.uri)'
} else {
    Write-Host "Deployment failed!" -ForegroundColor Red
    exit 1
}