# ⚠️ Ingestion Function Needs Redeployment

## What Happened?

The ingestion function was deployed, but it's still using the **old code with shared module imports** instead of the standalone version. This is why you're seeing this error in the logs:

```
ModuleNotFoundError: No module named 'shared'
```

### Why This Happened

The deployment script (`cleanup_and_deploy_ingestion.ps1`) correctly:
1. ✅ Switched to standalone files
2. ✅ Deployed the function
3. ✅ Restored original files (for version control)

**BUT** the function that was deployed is still trying to import from the `shared` module because the deployment happened before the standalone code was fully in place.

## Solution: Redeploy with Standalone Version

I've created a new script that will:
1. Permanently switch to the standalone version
2. Delete the existing (broken) function
3. Deploy the working standalone version
4. Test the deployment
5. Keep the standalone version active

## 🚀 Run This Command

```powershell
cd C:\dev\aletheia-codex
git pull origin main
.\redeploy_ingestion_fixed.ps1
```

This will:
- ✅ Delete the current broken function
- ✅ Deploy the standalone version (no shared dependencies)
- ✅ Test the deployment automatically
- ✅ Provide the function URL

## What's Different This Time?

The new script (`redeploy_ingestion_fixed.ps1`):
- **Permanently** uses the standalone version
- Backs up the original files as `main_with_shared.py` (not `main.py`)
- Tests the function immediately after deployment
- Uses proper PowerShell commands (Invoke-RestMethod instead of curl)

## After Successful Deployment

Once the function is redeployed, run the test script:

```powershell
.\test_sprint1_deployment.ps1
```

This will verify:
- ✅ Ingestion function accepts documents
- ✅ Documents are stored in Firestore
- ✅ Content is uploaded to Cloud Storage
- ✅ Orchestration function connects to Neo4j
- ✅ All logging is working

## Expected Results

After redeployment, you should see:
- Function status: **ACTIVE**
- No "ModuleNotFoundError" in logs
- Successful test response with document ID
- Documents appearing in Firestore
- Content files in Cloud Storage bucket

## Troubleshooting

If redeployment fails:
1. Check that `main_standalone.py` exists in `functions/ingestion/`
2. Verify the standalone file doesn't have shared imports
3. Check Cloud Build logs for deployment errors
4. Ensure bucket `aletheia-codex-prod-documents` exists

## Why Standalone Version?

The standalone version:
- ✅ **No external dependencies** - All code is self-contained
- ✅ **Faster deployment** - Smaller package size
- ✅ **More reliable** - No import path issues
- ✅ **Easier to maintain** - Single file with all logic

## Next Steps

1. Run `.\redeploy_ingestion_fixed.ps1`
2. Verify function is ACTIVE
3. Run `.\test_sprint1_deployment.ps1`
4. Check test results
5. If all tests pass, Sprint 1 is complete! 🎉

---

**Ready to fix this?** Just run the redeploy script! 🚀