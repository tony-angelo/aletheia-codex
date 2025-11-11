# 🔧 Neo4j Authentication Troubleshooting Guide

**Issue**: Neo4j authentication failures in Cloud Functions  
**Error**: `Neo.ClientError.Security.Unauthorized` or `Illegal metadata value`

---

## 🔍 Problem Diagnosis

You're seeing these errors in the logs:
```
Error processing document: {code: Neo.ClientError.Security.Unauthorized} 
{message: The client is unauthorized due to authentication failure.}

E0000 plugin_credentials.cc:82] Plugin added invalid metadata value.
E0000 plugin_credentials.cc:79] validate_metadata_from_plugin: INTERNAL:Illegal header value
```

### Root Cause

The Neo4j password stored in Secret Manager likely contains:
- Trailing newlines (`\n`)
- Carriage returns (`\r`)
- Tabs (`\t`)
- Extra spaces

These invisible characters cause authentication to fail because they're included in the password when retrieved from Secret Manager.

---

## ✅ Solution Steps

### Step 1: Fix the Secrets

Run the secret fixer script:

```powershell
cd C:\dev\aletheia-codex
.\fix_neo4j_secrets.ps1
```

This script will:
1. Retrieve each Neo4j secret
2. Remove all whitespace characters
3. Create new versions with cleaned values

**Expected Output:**
```
=== Neo4j Secret Fixer ===

Checking NEO4J_PASSWORD...
Original length: 33
Cleaned length: 32
Password contains whitespace! Fixing...
✓ Password cleaned and updated!

Checking NEO4J_URI...
URI: neo4j+s://xxxxx.databases.neo4j.io
✓ URI is clean

Checking NEO4J_USER...
User: neo4j
✓ User is clean

=== Secret Check Complete ===
```

### Step 2: Redeploy Functions

The code fix has already been applied. Now redeploy to pick it up:

```powershell
# Deploy all functions
.\deploy_all_functions.ps1
```

Or deploy individually:

```powershell
# Just orchestration
.\infrastructure\deploy-function.ps1 `
    -FunctionName orchestrate `
    -FunctionDir functions\orchestration `
    -EntryPoint orchestrate

# Ingestion (was missing)
.\infrastructure\deploy-function.ps1 `
    -FunctionName ingest_document `
    -FunctionDir functions\ingestion `
    -EntryPoint ingest_document
```

### Step 3: Test Again

```powershell
# Get token
$TOKEN = gcloud auth print-identity-token

# Upload document
$headers = @{
    "Authorization" = "Bearer $TOKEN"
    "Content-Type" = "application/json"
}
$body = @{
    "title" = "Test Document"
    "content" = "This is a test document with some content to process."
    "source" = "api"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "https://us-central1-aletheia-codex-prod.cloudfunctions.net/ingest_document" `
    -Method POST `
    -Headers $headers `
    -Body $body

Write-Host "Document ID: $($response.document_id)"

# Process document
$documentId = $response.document_id
$body = @{
    "document_id" = $documentId
    "action" = "process_document"
} | ConvertTo-Json

Invoke-RestMethod -Uri "https://us-central1-aletheia-codex-prod.cloudfunctions.net/orchestrate" `
    -Method POST `
    -Headers $headers `
    -Body $body

# Check logs
gcloud functions logs read orchestrate --region=us-central1 --limit=50
```

### Step 4: Verify Success

Look for these in the logs:
```
✓ Creating Neo4j driver...
✓ Successfully retrieved secret: NEO4J_PASSWORD (length: 32)
✓ Connecting to Neo4j:
✓ Verifying Neo4j connectivity...
✓ Neo4j connection verified successfully
✓ Generated embedding for chunk 1/1
✓ Stored 1 chunks in Neo4j
✓ Neo4j driver closed successfully
```

**No more authentication errors!**

---

## 🔍 Manual Secret Verification

If the script doesn't work, manually check and fix secrets:

### Check Current Secret Values

```powershell
# Check password (will show length)
$password = gcloud secrets versions access latest --secret="NEO4J_PASSWORD"
Write-Host "Password length: $($password.Length)"
Write-Host "Password (first 5 chars): $($password.Substring(0,5))..."

# Check for whitespace
if ($password -match '\s') {
    Write-Host "WARNING: Password contains whitespace!" -ForegroundColor Red
} else {
    Write-Host "Password is clean" -ForegroundColor Green
}
```

### Manually Update Secret

If you need to manually update:

```powershell
# Get your Neo4j password from AuraDB console
# Make sure to copy it WITHOUT any extra spaces or newlines

# Update the secret
$cleanPassword = "your-password-here"  # NO trailing newline!
$cleanPassword | gcloud secrets versions add NEO4J_PASSWORD --data-file=-

# Verify
$newPassword = gcloud secrets versions access latest --secret="NEO4J_PASSWORD"
Write-Host "New password length: $($newPassword.Length)"
```

---

## 🎯 Alternative: Use Secret Manager UI

1. Go to: https://console.cloud.google.com/security/secret-manager
2. Select project: `aletheia-codex-prod`
3. Click on `NEO4J_PASSWORD`
4. Click "New Version"
5. Paste password (ensure no trailing spaces/newlines)
6. Click "Add New Version"

---

## 📊 Common Issues

### Issue: Still Getting Authentication Errors

**Check:**
1. Password is correct in Neo4j AuraDB
2. Secret Manager has the correct password
3. Service account has `secretAccessor` role
4. Function has been redeployed after fixing secrets

**Solution:**
```powershell
# Verify secret access
gcloud secrets get-iam-policy NEO4J_PASSWORD

# Should show:
# - serviceAccount:aletheia-functions@aletheia-codex-prod.iam.gserviceaccount.com
# - roles/secretmanager.secretAccessor
```

### Issue: "Illegal metadata value" Errors

This is caused by whitespace in the password. The fix:
1. Run `fix_neo4j_secrets.ps1`
2. Redeploy functions
3. Test again

### Issue: Connection Timeout

If you see timeout instead of auth errors:
- Neo4j instance might be in sleep mode (free tier)
- Wait 30 seconds and retry
- Retry logic will handle this automatically

---

## 🔐 Security Best Practices

### When Creating Secrets

```powershell
# CORRECT: No trailing newline
$password = "your-password-here"
$password | gcloud secrets create NEO4J_PASSWORD --data-file=-

# WRONG: Has trailing newline
echo "your-password-here" | gcloud secrets create NEO4J_PASSWORD --data-file=-
```

### When Copying Passwords

1. Copy from Neo4j AuraDB console
2. Paste into a text editor
3. Remove any trailing spaces/newlines
4. Copy the clean password
5. Use in Secret Manager

---

## ✅ Success Indicators

After fixing, you should see:

### In Logs:
```
✓ Successfully retrieved secret: NEO4J_PASSWORD (length: 32)
✓ Neo4j connection verified successfully
✓ Stored X chunks in Neo4j
```

### No More Errors:
- ❌ No "Unauthorized" errors
- ❌ No "Illegal metadata value" errors
- ❌ No "Plugin added invalid metadata" errors

### Successful Response:
```json
{
  "status": "success",
  "document_id": "abc123",
  "chunks_processed": 1
}
```

---

## 📞 Still Having Issues?

1. **Check Neo4j Console**: Verify instance is running
2. **Check Secrets**: Run `fix_neo4j_secrets.ps1` again
3. **Check Logs**: Look for specific error messages
4. **Verify Deployment**: Ensure latest code is deployed

### Get Detailed Logs

```powershell
# Get last 100 logs with full details
gcloud functions logs read orchestrate --region=us-central1 --limit=100 --format=json | Out-File logs.json

# Search for errors
Get-Content logs.json | Select-String "error" -Context 2
```

---

**This issue is fixable!** The secret fixer script and code changes will resolve the authentication problems.