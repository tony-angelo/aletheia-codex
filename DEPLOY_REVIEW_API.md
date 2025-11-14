# Deploy Review API to Cloud Run

## Quick Deployment Commands

Run these commands in **Cloud Shell**:

```bash
# 1. Navigate to the repository
cd ~/aletheia-codex

# 2. Pull latest changes
git checkout sprint-1
git pull origin sprint-1

# 3. Navigate to functions directory
cd functions

# 4. Deploy review-api to Cloud Run
gcloud run deploy review-api \
  --source=review_api \
  --region=us-central1 \
  --platform=managed \
  --allow-unauthenticated \
  --set-env-vars="GCP_PROJECT=aletheia-codex-prod" \
  --memory=512Mi \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=10 \
  --timeout=60s \
  --project=aletheia-codex-prod

# 5. Test the deployment
echo "=== Testing Cloud Run service directly ==="
curl https://review-api-679360092359.us-central1.run.app

echo "=== Testing through Firebase Hosting ==="
curl https://aletheiacodex.app/api/review/pending
```

## What This Does

1. **Pulls latest code** with the fixed import path
2. **Deploys to Cloud Run** using source-based deployment
3. **Tests the service** to verify it's working

## Expected Output

After deployment, you should see:
```
Service [review-api] revision [review-api-00002-xxx] has been deployed and is serving 100 percent of traffic.
Service URL: https://review-api-679360092359.us-central1.run.app
```

When testing, you should get **JSON responses** (not error messages):
```json
{
  "success": true,
  "data": [...],
  ...
}
```

## If You Get Errors

### Error: "No module named 'shared.auth.firebase_auth'"

This means the deployment didn't pick up the fix. Try:
```bash
# Force rebuild
gcloud run deploy review-api \
  --source=review_api \
  --region=us-central1 \
  --platform=managed \
  --allow-unauthenticated \
  --set-env-vars="GCP_PROJECT=aletheia-codex-prod" \
  --memory=512Mi \
  --cpu=1 \
  --project=aletheia-codex-prod \
  --no-cache
```

### Error: "Permission denied"

Make sure you're authenticated:
```bash
gcloud auth list
gcloud config set project aletheia-codex-prod
```

## After Successful Deployment

1. **Test in browser**: Visit https://aletheiacodex.app
2. **Log in**: Use sprint1@domain.com / Password1234!
3. **Navigate to Review page**: Should load without errors
4. **Check console**: No 403 or module errors

## Deployment Time

- **Build time**: 2-3 minutes
- **Deploy time**: 1-2 minutes
- **Total**: ~5 minutes

---

**Status**: Ready to deploy  
**Branch**: sprint-1  
**Commit**: a95e839