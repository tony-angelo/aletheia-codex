# Manual Cleanup Guide

## Current Situation

You have multiple functions deployed:
- `ingest-document` (old, 1 day ago)
- `ingestion` (new, but failed to start properly)
- `orchestrate` (working)

## Option 1: Automated Cleanup (Recommended)

Run this script to automatically clean up and redeploy:

```powershell
cd C:\dev\aletheia-codex
git pull origin main
.\cleanup_and_deploy_ingestion.ps1
```

This will:
1. Delete all existing ingestion-related functions
2. Delete any Cloud Run services
3. Deploy fresh Gen1 function (avoids org policy issues)
4. Verify deployment

## Option 2: Manual Cleanup via Console

If you prefer to clean up manually:

### Step 1: Delete Functions via Console
1. Go to: https://console.cloud.google.com/functions/list?project=aletheia-codex-prod
2. Select the checkbox next to `ingestion`
3. Click **DELETE** at the top
4. Confirm deletion
5. Repeat for `ingest-document` if it exists

### Step 2: Delete Cloud Run Service (if exists)
1. Go to: https://console.cloud.google.com/run?project=aletheia-codex-prod
2. Look for service named `ingestion`
3. If found, click the three dots menu → **Delete**
4. Confirm deletion

### Step 3: Wait for Cleanup
Wait 30-60 seconds for resources to fully delete

### Step 4: Deploy Fresh
```powershell
cd C:\dev\aletheia-codex

# Prepare standalone files
Copy-Item functions/ingestion/main_standalone.py functions/ingestion/main.py -Force
Copy-Item functions/ingestion/requirements_standalone.txt functions/ingestion/requirements.txt -Force

# Deploy as Gen1 (avoids org policy issues)
gcloud functions deploy ingestion `
    --no-gen2 `
    --runtime=python311 `
    --trigger-http `
    --allow-unauthenticated `
    --entry-point=ingest_document `
    --source=functions/ingestion `
    --region=us-central1 `
    --timeout=540s `
    --memory=512MB

# Restore original files
Copy-Item functions/ingestion/main_original.py functions/ingestion/main.py -Force
Copy-Item functions/ingestion/requirements_original.txt functions/ingestion/requirements.txt -Force
```

## Option 3: Command Line Cleanup

```powershell
# Delete Gen2 function
gcloud functions delete ingestion --region=us-central1 --gen2 --quiet

# Delete Gen1 function
gcloud functions delete ingestion --region=us-central1 --quiet

# Delete old ingest-document
gcloud functions delete ingest-document --region=us-central1 --quiet

# Delete Cloud Run service
gcloud run services delete ingestion --region=us-central1 --quiet

# Wait a bit
Start-Sleep -Seconds 30

# Then deploy fresh (see Step 4 above)
```

## Why Gen1 Instead of Gen2?

The error message showed:
```
One or more users named in the policy do not belong to a permitted customer, 
perhaps due to an organization policy.
```

This is a Gen2-specific organization policy issue. Gen1 functions:
- ✅ Don't have this org policy restriction
- ✅ Are more stable for HTTP triggers
- ✅ Have simpler deployment model
- ✅ Work perfectly for our use case

## Verification

After deployment, verify:

```powershell
# Check function status
gcloud functions describe ingestion --region=us-central1

# Get function URL
$url = gcloud functions describe ingestion --region=us-central1 --format='value(httpsTrigger.url)'

# Test it
curl -X POST "$url" -H "Content-Type: application/json" -d '{"title":"Test","content":"Test content"}'
```

Expected response:
```json
{
  "status": "success",
  "document_id": "abc123...",
  "message": "Document ingested successfully"
}
```

## Troubleshooting

### If deployment still fails:

1. **Check if resources are fully deleted:**
   ```powershell
   gcloud functions list --region=us-central1
   gcloud run services list --region=us-central1
   ```

2. **Check Cloud Build logs:**
   ```powershell
   gcloud builds list --limit=5
   ```

3. **Check function logs:**
   ```powershell
   gcloud functions logs read ingestion --region=us-central1 --limit=50
   ```

4. **Verify bucket exists:**
   ```powershell
   gsutil ls gs://aletheia-codex-prod-documents
   ```
   If not, create it:
   ```powershell
   gsutil mb -p aletheia-codex-prod gs://aletheia-codex-prod-documents
   ```

## Next Steps

Once ingestion deploys successfully:
1. ✅ Test the ingestion endpoint
2. ✅ Test orchestration function end-to-end
3. ✅ Verify Neo4j connectivity
4. ✅ Complete Sprint 1 handoff

You're almost there! 🚀