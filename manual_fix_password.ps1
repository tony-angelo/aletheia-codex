# Manual Neo4j Password Fix
# Use this if the automatic script doesn't work

$PROJECT_ID = "aletheia-codex-prod"

Write-Host "=== Manual Neo4j Password Fix ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "This script will prompt you for the correct Neo4j password" -ForegroundColor Yellow
Write-Host "and update it in Secret Manager." -ForegroundColor Yellow
Write-Host ""
Write-Host "To get your password:" -ForegroundColor Cyan
Write-Host "1. Go to https://console.neo4j.io/" -ForegroundColor Gray
Write-Host "2. Select your database" -ForegroundColor Gray
Write-Host "3. Copy the password (it should be around 30-40 characters)" -ForegroundColor Gray
Write-Host ""

# Prompt for password
$password = Read-Host "Enter Neo4j password"

# Clean it
$cleanPassword = $password.Trim().Replace("`n", "").Replace("`r", "").Replace("`t", "").Replace(" ", "")

Write-Host ""
Write-Host "Password length: $($cleanPassword.Length)" -ForegroundColor Gray

if ($cleanPassword.Length -lt 10) {
    Write-Host "✗ Password seems too short! Please check and try again." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Updating secret in Secret Manager..." -ForegroundColor Yellow

try {
    # Create new version
    $cleanPassword | gcloud secrets versions add NEO4J_PASSWORD --data-file=- --project=$PROJECT_ID
    
    Write-Host "✓ Password updated successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Redeploy orchestrate function" -ForegroundColor Gray
    Write-Host "2. Test with a document" -ForegroundColor Gray
    
} catch {
    Write-Host "✗ Failed to update secret: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Alternative: Update manually in Cloud Console" -ForegroundColor Yellow
    Write-Host "https://console.cloud.google.com/security/secret-manager/secret/NEO4J_PASSWORD?project=$PROJECT_ID" -ForegroundColor Cyan
}