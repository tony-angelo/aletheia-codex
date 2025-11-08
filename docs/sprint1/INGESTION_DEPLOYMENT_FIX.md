# Ingestion Function Deployment Fix

## Problem Identified

The ingestion function was failing to deploy with this error:
```
Container Healthcheck failed. The user-provided container failed to start and listen on the port defined by PORT=8080
```

### Root Cause

The ingestion function (`functions/ingestion/main.py`) imports from the shared module:
```python
from shared.db.firestore_client import get_firestore_client
from shared.utils.logging import get_logger
```

**Issue:** When Cloud Functions deploys, it only packages the `functions/ingestion` directory. The `shared` module in the parent directory is NOT included, causing import failures and container startup failures.

## Solution

Created a **standalone version** of the ingestion function that includes all necessary code inline without external dependencies.

### Files Created

1. **`functions/ingestion/main_standalone.py`**
   - Self-contained version with no shared module dependencies
   - Includes inline Firestore client and logging setup
   - Uses Cloud Logging directly

2. **`functions/ingestion/requirements_standalone.txt`**
   - Complete dependency list including `google-cloud-logging`
   - No references to shared modules

3. **`deploy_ingestion_standalone.ps1`**
   - Automated deployment script that:
     * Backs up original files
     * Switches to standalone versions
     * Deploys the function
     * Restores original files (for version control)

## Deployment Instructions

### Option 1: Use the Automated Script (Recommended)

```powershell
cd C:\dev\aletheia-codex
git pull origin main
.\deploy_ingestion_standalone.ps1
```

This script will:
1. ✅ Backup your original files
2. ✅ Deploy the standalone version
3. ✅ Restore original files after deployment
4. ✅ Provide the function URL for testing

### Option 2: Manual Deployment

```powershell
# 1. Pull latest changes
git pull origin main

# 2. Backup original files
Copy-Item functions/ingestion/main.py functions/ingestion/main_backup.py
Copy-Item functions/ingestion/requirements.txt functions/ingestion/requirements_backup.txt

# 3. Use standalone versions
Copy-Item functions/ingestion/main_standalone.py functions/ingestion/main.py -Force
Copy-Item functions/ingestion/requirements_standalone.txt functions/ingestion/requirements.txt -Force

# 4. Deploy
gcloud functions deploy ingestion `
    --gen2 `
    --runtime=python311 `
    --trigger-http `
    --allow-unauthenticated `
    --entry-point=ingest_document `
    --source=functions/ingestion `
    --region=us-central1 `
    --timeout=540s `
    --memory=512MB

# 5. Restore original files
Copy-Item functions/ingestion/main_backup.py functions/ingestion/main.py -Force
Copy-Item functions/ingestion/requirements_backup.txt functions/ingestion/requirements.txt -Force
```

## Testing the Deployed Function

After successful deployment, test with:

```powershell
# Get the function URL
$url = gcloud functions describe ingestion --region=us-central1 --format='value(serviceConfig.uri)'

# Test the endpoint
curl -X POST "$url" `
  -H "Content-Type: application/json" `
  -d '{"title":"Test Document","content":"This is test content"}'
```

Expected response:
```json
{
  "status": "success",
  "document_id": "abc123...",
  "message": "Document ingested successfully"
}
```

## Why This Approach?

### Advantages
1. ✅ **No Import Errors** - All code is self-contained
2. ✅ **Faster Deployment** - Smaller package size
3. ✅ **Version Control** - Original files remain unchanged in repo
4. ✅ **Automated** - Script handles everything

### Trade-offs
- Slight code duplication (Firestore client, logging setup)
- Need to maintain two versions temporarily

## Long-term Solution

For future iterations, consider:
1. **Monorepo Structure** - Use a proper Python package structure
2. **Shared Package** - Create a pip-installable shared package
3. **Cloud Build** - Use Cloud Build to package shared dependencies
4. **Container Deployment** - Deploy as containers with full control

## Verification Checklist

After deployment, verify:
- [ ] Function shows as ACTIVE: `gcloud functions describe ingestion --region=us-central1`
- [ ] Function URL is accessible
- [ ] Test POST request succeeds
- [ ] Document appears in Firestore
- [ ] Content uploaded to Cloud Storage
- [ ] Logs show successful ingestion

## Troubleshooting

### If deployment still fails:

1. **Check Cloud Build logs:**
   ```powershell
   gcloud builds list --limit=5
   ```

2. **Check function logs:**
   ```powershell
   gcloud functions logs read ingestion --region=us-central1 --limit=50
   ```

3. **Try Gen1 deployment:**
   ```powershell
   gcloud functions deploy ingestion --no-gen2 ...
   ```

4. **Verify bucket exists:**
   ```powershell
   gsutil ls gs://aletheia-codex-prod-documents
   ```

## Next Steps

Once ingestion is deployed successfully:
1. Test orchestration function end-to-end
2. Verify Neo4j connectivity with new password
3. Complete Sprint 1 handoff
4. Plan Sprint 2 improvements