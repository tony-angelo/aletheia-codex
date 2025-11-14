# Deploy Review API with Python 3.11 Fix

## Problem
Cloud Run was using Python 3.13, which is incompatible with `functions-framework`. The error was:
```
ImportError: cannot import name 'T' from 're'
```

## Solution
Added `runtime.txt` to pin Python to 3.11 and downgraded `functions-framework` to 3.5.0 for compatibility.

## Files Changed
- `functions/review_api/runtime.txt` (NEW) - Specifies Python 3.11
- `functions/review_api/requirements.txt` - Downgraded functions-framework to 3.5.0

## Deployment Commands

### Step 1: Push the changes (if not already done)
```bash
cd ~/aletheia-codex
git checkout sprint-1
git pull origin sprint-1
git push origin sprint-1  # If the push from workspace failed
```

### Step 2: Deploy to Cloud Run
```bash
cd ~/aletheia-codex/functions
gcloud run deploy review-api \
  --source=review_api \
  --region=us-central1 \
  --platform=managed \
  --allow-unauthenticated \
  --set-env-vars="GCP_PROJECT=aletheia-codex-prod" \
  --memory=512Mi \
  --cpu=1 \
  --project=aletheia-codex-prod
```

### Step 3: Verify Deployment
```bash
# Check the service URL
gcloud run services describe review-api --region=us-central1 --project=aletheia-codex-prod --format="value(status.url)"

# Test the endpoint
curl https://review-api-679360092359.us-central1.run.app/api/review/pending
```

### Step 4: Test in Browser
Visit: https://aletheiacodex.app

The review page should now load without "Service Unavailable" errors.

## Expected Results
- ✅ Cloud Run builds successfully with Python 3.11
- ✅ Service starts without import errors
- ✅ API endpoints return JSON (not 503 errors)
- ✅ Frontend loads review data successfully

## Troubleshooting
If you still see errors:
1. Check Cloud Run logs: `gcloud run services logs read review-api --region=us-central1 --project=aletheia-codex-prod --limit=50`
2. Verify Python version in logs (should show Python 3.11)
3. Verify functions-framework version (should be 3.5.0)

## Next Steps After Success
1. Deploy remaining services (graph-api, notes-api, orchestration-api) with same Python 3.11 fix
2. Update firebase.json with all Cloud Run service URLs
3. Complete end-to-end testing
4. Merge sprint-1 to main