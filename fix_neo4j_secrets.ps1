# Fix Neo4j Secrets - Remove whitespace and special characters
# This script retrieves, cleans, and updates Neo4j secrets in Secret Manager

Write-Host "=== Neo4j Secret Fixer ===" -ForegroundColor Cyan
Write-Host ""

$PROJECT_ID = "aletheia-codex-prod"

# Function to clean secret value
function Clean-SecretValue {
    param([string]$value)
    # Remove all whitespace, newlines, tabs, carriage returns
    return $value.Trim().Replace("`n", "").Replace("`r", "").Replace("`t", "").Replace(" ", "")
}

# Check and fix NEO4J_PASSWORD
Write-Host "Checking NEO4J_PASSWORD..." -ForegroundColor Yellow
try {
    $password = gcloud secrets versions access latest --secret="NEO4J_PASSWORD" --project=$PROJECT_ID
    $cleanPassword = Clean-SecretValue $password
    
    Write-Host "Original length: $($password.Length)" -ForegroundColor Gray
    Write-Host "Cleaned length: $($cleanPassword.Length)" -ForegroundColor Gray
    
    # If original is suspiciously short (< 10 chars) or different from cleaned, update it
    if ($password.Length -lt 10 -or $password -ne $cleanPassword) {
        Write-Host "Password needs fixing! (too short or contains whitespace)" -ForegroundColor Red
        
        # Get the actual password from Neo4j AuraDB
        Write-Host ""
        Write-Host "IMPORTANT: The current password in Secret Manager appears corrupted." -ForegroundColor Yellow
        Write-Host "Please enter the correct Neo4j password from your AuraDB console:" -ForegroundColor Yellow
        $correctPassword = Read-Host -AsSecureString "Neo4j Password"
        $BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($correctPassword)
        $plainPassword = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
        
        # Clean it
        $cleanedCorrectPassword = Clean-SecretValue $plainPassword
        
        Write-Host ""
        Write-Host "Creating new secret version with correct password..." -ForegroundColor Yellow
        Write-Host "New password length: $($cleanedCorrectPassword.Length)" -ForegroundColor Gray
        
        # Create new version
        echo $cleanedCorrectPassword | gcloud secrets versions add NEO4J_PASSWORD --data-file=- --project=$PROJECT_ID
        
        Write-Host "✓ Password updated successfully!" -ForegroundColor Green
        Write-Host "  Password length: $($cleanedCorrectPassword.Length)" -ForegroundColor Green
    } else {
        Write-Host "✓ Password appears correct (length: $($password.Length))" -ForegroundColor Green
    }
} catch {
    Write-Host "✗ Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "  Try manually updating the secret in Cloud Console" -ForegroundColor Yellow
}

Write-Host ""

# Check NEO4J_URI
Write-Host "Checking NEO4J_URI..." -ForegroundColor Yellow
try {
    $uri = gcloud secrets versions access latest --secret="NEO4J_URI" --project=$PROJECT_ID
    $cleanUri = Clean-SecretValue $uri
    
    Write-Host "URI: $cleanUri" -ForegroundColor Gray
    
    if ($uri -ne $cleanUri) {
        Write-Host "URI contains whitespace! Fixing..." -ForegroundColor Red
        $cleanUri | gcloud secrets versions add NEO4J_URI --data-file=- --project=$PROJECT_ID
        Write-Host "✓ URI cleaned and updated!" -ForegroundColor Green
    } else {
        Write-Host "✓ URI is clean" -ForegroundColor Green
    }
} catch {
    Write-Host "✗ Error checking URI: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Check NEO4J_USER
Write-Host "Checking NEO4J_USER..." -ForegroundColor Yellow
try {
    $user = gcloud secrets versions access latest --secret="NEO4J_USER" --project=$PROJECT_ID
    $cleanUser = Clean-SecretValue $user
    
    Write-Host "User: $cleanUser" -ForegroundColor Gray
    
    if ($user -ne $cleanUser) {
        Write-Host "User contains whitespace! Fixing..." -ForegroundColor Red
        $cleanUser | gcloud secrets versions add NEO4J_USER --data-file=- --project=$PROJECT_ID
        Write-Host "✓ User cleaned and updated!" -ForegroundColor Green
    } else {
        Write-Host "✓ User is clean" -ForegroundColor Green
    }
} catch {
    Write-Host "✗ Error checking user: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== Secret Check Complete ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Redeploy the orchestrate function to pick up the code fix"
Write-Host "2. Test again with a document"
Write-Host ""