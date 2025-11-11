# 🎯 Final Deployment Instructions - Sprint 1

## Current Situation

You have conflicting functions in GCP:
- `ingest-document` (old version, 1 day ago)
- `ingestion` (new version, but failed to start due to Gen2 org policy)
- `orchestrate` (working fine)

## The Issue

Two problems were identified:
1. **Shared module imports** - Function tried to import from parent directory
2. **Gen2 org policy** - Organization policy blocking Gen2 deployment

## The Solution

✅ **Standalone function** - No shared dependencies
✅ **Gen1 deployment** - Avoids org policy issues
✅ **Automated cleanup** - Removes all conflicting resources

## 🚀 Quick Start (Recommended)

Run this ONE command to fix everything:

```powershell
cd C:\dev\aletheia-codex
git pull origin main
.\cleanup_and_deploy_ingestion.ps1
```

This automated script will:
1. ✅ Delete all existing ingestion functions (Gen1, Gen2, old names)
2. ✅ Delete any Cloud Run services
3. ✅ Deploy fresh Gen1 function with standalone code
4. ✅ Verify deployment success
5. ✅ Provide function URL for testing

## What Happens During Cleanup

The script will delete:
- Gen2 function `ingestion` (if exists)
- Gen1 function `ingestion` (if exists)
- Old function `ingest-document` (if exists)
- Cloud Run service `ingestion` (if exists)

Then deploy fresh as Gen1 function.

## Alternative: Manual Cleanup

If you prefer manual control, see `MANUAL_CLEANUP_GUIDE.md` for:
- Console-based cleanup steps
- Command-line cleanup commands
- Manual deployment instructions

## After Successful Deployment

### 1. Verify Function
```powershell
gcloud functions describe ingestion --region=us-central1
```

### 2. Get Function URL
```powershell
$url = gcloud functions describe ingestion --region=us-central1 --format='value(httpsTrigger.url)'
Write-Host "Function URL: $url"
```

### 3. Test the Function
```powershell
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

## Sprint 1 Completion Checklist

Once ingestion deploys successfully:

- [ ] Ingestion function deployed and responding
- [ ] Test orchestration function end-to-end
- [ ] Verify Neo4j connectivity with new password
- [ ] Confirm all functions are working together
- [ ] Review Sprint 1 improvements summary

## Why Gen1 Instead of Gen2?

**Gen2 Issue:**
```
One or more users named in the policy do not belong to a permitted customer,
perhaps due to an organization policy.
```

**Gen1 Benefits:**
- ✅ No organization policy restrictions
- ✅ More stable for HTTP triggers
- ✅ Simpler deployment model
- ✅ Perfect for our use case
- ✅ Same functionality, fewer restrictions

## Troubleshooting

### If cleanup script fails:

1. **Manually delete via console:**
   - Go to Cloud Functions console
   - Delete `ingestion` and `ingest-document`
   - Wait 60 seconds
   - Run script again

2. **Check for Cloud Run services:**
   ```powershell
   gcloud run services list --region=us-central1
   ```
   Delete any `ingestion` service found

3. **Verify bucket exists:**
   ```powershell
   gsutil ls gs://aletheia-codex-prod-documents
   ```
   Create if missing:
   ```powershell
   gsutil mb -p aletheia-codex-prod gs://aletheia-codex-prod-documents
   ```

## Documentation Reference

- `INGESTION_DEPLOYMENT_FIX.md` - Detailed problem analysis
- `MANUAL_CLEANUP_GUIDE.md` - Manual cleanup options
- `DEPLOYMENT_READY.md` - Overview and context
- `cleanup_and_deploy_ingestion.ps1` - Automated script

## Ready to Complete Sprint 1?

Just run:
```powershell
.\cleanup_and_deploy_ingestion.ps1
```

This is the final step! Once this succeeds, Sprint 1 is complete with all optimizations in place! 🎉

---

**Need help?** Check the troubleshooting section above or review the detailed guides.