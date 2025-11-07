# 🚀 PowerShell Deployment Guide - Sprint 1

**Optimized for Windows PowerShell**  
**Status**: Ready for Production Deployment  
**Prerequisites**: Windows 10/11 with PowerShell 5.1+

---

## 📋 PowerShell Prerequisites

### Required Software
- **PowerShell 5.1+** (included with Windows 10/11)
- **gcloud CLI** for Windows
- **Git for Windows**
- **Python 3.11+** for local testing

### gcloud CLI Installation
```powershell
# Download and install gcloud CLI
# Visit: https://cloud.google.com/sdk/docs/install-windows

# After installation, verify
gcloud version
```

### PowerShell Execution Policy
```powershell
# Check current execution policy
Get-ExecutionPolicy

# If restricted, allow script execution
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 🚀 PowerShell Deployment Steps

### Step 1: Setup Environment

```powershell
# Navigate to project directory
cd C:\dev\aletheia-codex

# Pull latest changes
git pull origin main

# Verify gcloud authentication
gcloud auth list

# Verify correct project
gcloud config get-value project

# Set project if needed
gcloud config set project aletheia-codex-prod
```

### Step 2: Deploy Orchestration Function

**Option A: Use PowerShell Script (Recommended)**
```powershell
# Use existing deployment script
.\infrastructure\deploy-function.ps1 `
    -FunctionName orchestrate `
    -FunctionDir functions\orchestration `
    -EntryPoint orchestrate `
    -Region us-central1 `
    -Project aletheia-codex-prod
```

**Option B: Manual PowerShell Commands**
```powershell
# Create deployment directory
Write-Host "Creating deployment directory..." -ForegroundColor Green
New-Item -ItemType Directory -Path deploy-temp -Force

# Copy function and shared code
Write-Host "Copying function code..." -ForegroundColor Green
Copy-Item -Path "functions\orchestration\*" -Destination "deploy-temp" -Recurse
Copy-Item -Path "shared" -Destination "deploy-temp" -Recurse

# Deploy to Cloud Functions
Write-Host "Deploying function..." -ForegroundColor Green
Set-Location deploy-temp

gcloud functions deploy orchestrate `
  --gen2 `
  --runtime=python311 `
  --region=us-central1 `
  --source=. `
  --entry-point=orchestrate `
  --trigger=http `
  --service-account=aletheia-functions@aletheia-codex-prod.iam.gserviceaccount.com `
  --timeout=540s `
  --memory=512MB `
  --set-env-vars=GCP_PROJECT=aletheia-codex-prod

# Clean up
Set-Location ..
Remove-Item -Recurse -Force deploy-temp

Write-Host "Deployment completed!" -ForegroundColor Green
```

### Step 3: Verify Deployment

```powershell
# Check function status
Write-Host "Checking function status..." -ForegroundColor Green
gcloud functions describe orchestrate --region=us-central1 --format="table(name,state,updateTime)"

# Test the function
Write-Host "Testing function..." -ForegroundColor Green
$TOKEN = gcloud auth print-identity-token

$headers = @{
    "Authorization" = "Bearer $TOKEN"
    "Content-Type" = "application/json"
}

$body = @{
    "document_id" = "test-doc-powershell"
    "action" = "process_document"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "https://us-central1-aletheia-codex-prod.cloudfunctions.net/orchestrate" `
        -Method POST `
        -Headers $headers `
        -Body $body `
        -ErrorAction Stop
    
    Write-Host "✓ Function test successful!" -ForegroundColor Green
    Write-Host "Response: $($response | ConvertTo-Json -Depth 10)"
} catch {
    Write-Host "✗ Function test failed: $($_.Exception.Message)" -ForegroundColor Red
}
```

---

## 📊 PowerShell Monitoring Scripts

### Real-time Log Monitoring
```powershell
# Save as monitor-logs.ps1
function Watch-FunctionLogs {
    param(
        [string]$FunctionName = "orchestrate",
        [string]$Region = "us-central1",
        [int]$RefreshInterval = 30
    )
    
    try {
        while ($true) {
            Clear-Host
            Write-Host "=== $FunctionName Logs ===" -ForegroundColor Cyan
            Write-Host "Last updated: $(Get-Date)" -ForegroundColor Gray
            Write-Host "Refresh interval: $RefreshInterval seconds" -ForegroundColor Gray
            Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
            Write-Host ""
            
            $logs = gcloud functions logs read $FunctionName --region=$Region --limit=20 --format="table(time,textPayload)"
            Write-Host $logs
            
            Write-Host ""
            Write-Host "Next refresh in $RefreshInterval seconds..." -ForegroundColor Gray
            Start-Sleep -Seconds $RefreshInterval
        }
    }
    catch {
        Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Usage: Watch-FunctionLogs
Watch-FunctionLogs
```

### Health Check Script
```powershell
# Save as health-check.ps1
function Test-FunctionHealth {
    param(
        [string]$FunctionName = "orchestrate",
        [string]$Region = "us-central1"
    )
    
    Write-Host "=== Function Health Check ===" -ForegroundColor Green
    
    # Check function status
    $status = gcloud functions describe $FunctionName --region=$Region --format="value(state)"
    Write-Host "Function State: $status" -ForegroundColor $(if($status -eq "ACTIVE") {"Green"} else {"Red"})
    
    # Test connectivity
    try {
        $TOKEN = gcloud auth print-identity-token
        $headers = @{
            "Authorization" = "Bearer $TOKEN"
            "Content-Type" = "application/json"
        }
        
        $testBody = @{
            "document_id" = "health-check-$((Get-Date).ToString('yyyyMMdd-HHmmss'))"
            "action" = "process_document"
        } | ConvertTo-Json
        
        $response = Invoke-RestMethod -Uri "https://$Region-aletheia-codex-prod.cloudfunctions.net/$FunctionName" `
            -Method POST `
            -Headers $headers `
            -Body $testBody `
            -TimeoutSec 30
        
        Write-Host "✓ Function responding" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "✗ Function not responding: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Usage: Test-FunctionHealth
Test-FunctionHealth
```

---

## 🔄 PowerShell Rollback Script

```powershell
# Save as rollback.ps1
function Invoke-DeploymentRollback {
    param(
        [string]$ProjectDir = "C:\dev\aletheia-codex"
    )
    
    Write-Host "=== Deployment Rollback ===" -ForegroundColor Yellow
    Write-Host "This will restore the original implementations." -ForegroundColor Yellow
    $confirm = Read-Host "Continue? (y/N)"
    
    if ($confirm -ne "y") {
        Write-Host "Rollback cancelled." -ForegroundColor Yellow
        return
    }
    
    try {
        Set-Location $ProjectDir
        
        # Restore original files
        Write-Host "Restoring original files..." -ForegroundColor Green
        Copy-Item "functions\orchestration\main_backup.py" "functions\orchestration\main.py" -Force
        Copy-Item "shared\db\neo4j_client_backup.py" "shared\db\neo4j_client.py" -Force
        Copy-Item "shared\utils\logging_backup.py" "shared\utils\logging.py" -Force
        
        # Commit changes
        Write-Host "Committing rollback..." -ForegroundColor Green
        git add -A
        git commit -m "Rollback: Restore original implementations"
        git push origin main
        
        # Redeploy
        Write-Host "Redeploying original version..." -ForegroundColor Green
        New-Item -ItemType Directory -Path deploy-temp -Force
        Copy-Item -Path "functions\orchestration\*" -Destination "deploy-temp" -Recurse
        Copy-Item -Path "shared" -Destination "deploy-temp" -Recurse
        Set-Location deploy-temp
        
        gcloud functions deploy orchestrate `
          --gen2 `
          --runtime=python311 `
          --region=us-central1 `
          --source=. `
          --entry-point=orchestrate `
          --trigger=http `
          --service-account=aletheia-functions@aletheia-codex-prod.iam.gserviceaccount.com
        
        Set-Location ..
        Remove-Item -Recurse -Force deploy-temp
        
        Write-Host "✓ Rollback completed successfully!" -ForegroundColor Green
        Write-Host "Function has been restored to original state." -ForegroundColor Green
    }
    catch {
        Write-Host "✗ Rollback failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Usage: Invoke-DeploymentRollback
Invoke-DeploymentRollback
```

---

## 🧪 PowerShell Testing

### Local Test Execution
```powershell
# Run local tests
Write-Host "Running test suite..." -ForegroundColor Green
python test_improvements.py

# Check exit code
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ All tests passed!" -ForegroundColor Green
} else {
    Write-Host "✗ Some tests failed!" -ForegroundColor Red
}
```

### Pre-deployment Validation
```powershell
# Save as pre-deployment-check.ps1
function Invoke-PreDeploymentCheck {
    Write-Host "=== Pre-deployment Validation ===" -ForegroundColor Cyan
    
    # Check prerequisites
    Write-Host "Checking prerequisites..." -ForegroundColor Yellow
    
    # Check gcloud authentication
    try {
        $auth = gcloud auth list --format="value(account)" --filter="status:ACTIVE"
        if ($auth) {
            Write-Host "✓ gcloud authenticated as: $auth" -ForegroundColor Green
        } else {
            Write-Host "✗ gcloud not authenticated" -ForegroundColor Red
            return $false
        }
    }
    catch {
        Write-Host "✗ gcloud check failed" -ForegroundColor Red
        return $false
    }
    
    # Check project
    try {
        $project = gcloud config get-value project
        if ($project -eq "aletheia-codex-prod") {
            Write-Host "✓ Correct project set: $project" -ForegroundColor Green
        } else {
            Write-Host "✗ Wrong project: $project" -ForegroundColor Red
            return $false
        }
    }
    catch {
        Write-Host "✗ Project check failed" -ForegroundColor Red
        return $false
    }
    
    # Check files exist
    $files = @(
        "functions\orchestration\main.py",
        "shared\db\neo4j_client.py",
        "shared\utils\logging.py"
    )
    
    foreach ($file in $files) {
        if (Test-Path $file) {
            Write-Host "✓ $file exists" -ForegroundColor Green
        } else {
            Write-Host "✗ $file missing" -ForegroundColor Red
            return $false
        }
    }
    
    # Run local tests
    Write-Host "Running local tests..." -ForegroundColor Yellow
    python test_improvements.py
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Local tests passed" -ForegroundColor Green
    } else {
        Write-Host "✗ Local tests failed" -ForegroundColor Red
        return $false
    }
    
    Write-Host "✓ All checks passed. Ready for deployment!" -ForegroundColor Green
    return $true
}

# Usage: Invoke-PreDeploymentCheck
Invoke-PreDeploymentCheck
```

---

## 📁 PowerShell Profile Scripts

### Add to PowerShell Profile
```powershell
# Add these functions to your PowerShell profile
# Profile location: C:\Users\YourUsername\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1

function cd-aletheia {
    Set-Location "C:\dev\aletheia-codex"
}

function logs-orchestrate {
    param([int]$Limit = 50)
    gcloud functions logs read orchestrate --region=us-central1 --limit=$Limit
}

function test-orchestrate {
    $TOKEN = gcloud auth print-identity-token
    $headers = @{
        "Authorization" = "Bearer $TOKEN"
        "Content-Type" = "application/json"
    }
    $body = @{
        "document_id" = "test-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
        "action" = "process_document"
    } | ConvertTo-Json
    
    Invoke-RestMethod -Uri "https://us-central1-aletheia-codex-prod.cloudfunctions.net/orchestrate" `
        -Method POST `
        -Headers $headers `
        -Body $body
}

function deploy-orchestrate {
    .\infrastructure\deploy-function.ps1 `
        -FunctionName orchestrate `
        -FunctionDir functions\orchestration `
        -EntryPoint orchestrate
}

Write-Host "AletheiaCodex functions loaded!" -ForegroundColor Green
Write-Host "Available commands:" -ForegroundColor Yellow
Write-Host "  cd-aletheia    - Navigate to project directory"
Write-Host "  logs-orchestrate [Limit] - View orchestration logs"
Write-Host "  test-orchestrate       - Test orchestration function"
Write-Host "  deploy-orchestrate     - Deploy orchestration function"
```

---

## 🎯 Quick PowerShell Commands

### Common Tasks
```powershell
# Navigate to project
cd C:\dev\aletheia-codex

# Pull latest changes
git pull origin main

# Deploy function
.\infrastructure\deploy-function.ps1 -FunctionName orchestrate -FunctionDir functions\orchestration -EntryPoint orchestrate

# Check function status
gcloud functions describe orchestrate --region=us-central1

# View latest logs
gcloud functions logs read orchestrate --region=us-central1 --limit=20

# Test function
$TOKEN = gcloud auth print-identity-token
$headers = @{"Authorization" = "Bearer $TOKEN"; "Content-Type" = "application/json"}
$body = @{"document_id" = "test"; "action" = "process_document"} | ConvertTo-Json
Invoke-RestMethod -Uri "https://us-central1-aletheia-codex-prod.cloudfunctions.net/orchestrate" -Method POST -Headers $headers -Body $body

# Monitor logs (Ctrl+C to stop)
while ($true) { Clear-Host; gcloud functions logs read orchestrate --region=us-central1 --limit=10; Start-Sleep 30 }
```

---

## 🐛 PowerShell Troubleshooting

### Common PowerShell Issues

#### Execution Policy Error
```powershell
# Fix execution policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### gcloud Command Not Found
```powershell
# Add gcloud to PATH
$gcloudPath = "C:\Program Files\Google\Cloud SDK\google-cloud-sdk\bin"
$env:Path += ";$gcloudPath"

# Or install gcloud PowerShell module
Install-Module GoogleCloud
```

#### Network/Proxy Issues
```powershell
# Set proxy for gcloud (if needed)
$env:HTTPS_PROXY = "http://proxy.company.com:8080"
$env:HTTP_PROXY = "http://proxy.company.com:8080"
```

#### Certificate Issues
```powershell
# Bypass SSL validation for testing (NOT recommended for production)
[System.Net.ServicePointManager]::ServerCertificateValidationCallback = {$true}
```

---

## 📞 PowerShell Support

### Getting Help
1. **Check PowerShell version**: `$PSVersionTable`
2. **Verify gcloud installation**: `gcloud version`
3. **Check execution policy**: `Get-ExecutionPolicy`
4. **Test network connectivity**: `Test-NetConnection google.com -Port 443`

### Common PowerShell Commands
```powershell
# Get help on any command
Get-Help gcloud

# List all gcloud functions
gcloud functions list

# Get function details
gcloud functions describe orchestrate --region=us-central1

# List available regions
gcloud functions regions list

# Check service account permissions
gcloud iam service-accounts describe aletheia-functions@aletheia-codex-prod.iam.gserviceaccount.com
```

---

**PowerShell Deployment Status**: ✅ READY  
**Windows Support**: ✅ FULLY SUPPORTED  
**Recommended Action**: **USE POWERSHELL FOR DEPLOYMENT**  
**Next Step**: **DEPLOY TO PRODUCTION**