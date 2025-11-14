# Final Deployment Steps - Run in Cloud Shell

## Current Status

✅ **Organization policy deleted** - Public access now allowed  
✅ **IAM permissions granted** - `allUsers` can invoke review-api  
✅ **Import path fixed** - Code updated to use local shared directory  
✅ **Code committed and pushed** - Changes are in GitHub (sprint-1 branch)  

❌ **Service needs redeployment** - Must deploy with fixed code

---

## Quick Deployment (5 minutes)

### Step 1: Open Cloud Shell

Go to: https://console.cloud.google.com/  
Click the **Cloud Shell** icon (>_) in the top right

### Step 2: Clone/Update Repository

```bash
# If you don't have the repo yet
cd ~
git clone https://github.com/tony-angelo/aletheia-codex.git
cd aletheia-codex

# If you already have it
cd ~/aletheia-codex
git fetch origin
git checkout sprint-1
git pull origin sprint-1
```

### Step 3: Deploy to Cloud Run

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
  --min-instances=0 \
  --max-instances=10 \
  --timeout=60s \
  --project=aletheia-codex-prod
```

**Wait for deployment** (~3-5 minutes)

### Step 4: Test the Service

```bash
# Test Cloud Run directly
curl https://review-api-679360092359.us-central1.run.app

# Test through Firebase Hosting
curl https://aletheiacodex.app/api/review/pending
```

**Expected**: JSON response (not error message)

### Step 5: Test in Browser

1. Visit: https://aletheiacodex.app
2. Log in: `sprint1@domain.com` / `Password1234!`
3. Navigate to Review page
4. **Should work!** 🎉

---

## Expected Deployment Output

```
Building using Buildpacks and deploying container to Cloud Run service [review-api]
✓ Creating Container Repository
✓ Uploading sources
✓ Building Container
✓ Pushing Container
✓ Deploying Revision
✓ Routing traffic

Service [review-api] revision [review-api-00002-xxx] has been deployed and is serving 100 percent of traffic.
Service URL: https://review-api-679360092359.us-central1.run.app
```

---

## What Was Fixed

### The Problem
```python
# Old code (WRONG)
sys.path.append('/workspace')
from shared.auth.unified_auth import require_auth
```

This tried to import from `/workspace/shared/` which doesn't exist in Cloud Run.

### The Fix
```python
# New code (CORRECT)
sys.path.insert(0, os.path.dirname(__file__))
from shared.auth.firebase_auth import require_auth
```

This imports from `functions/review_api/shared/` which is included in the deployment.

---

## Troubleshooting

### Error: "No module named 'shared'"

The deployment didn't pick up the fix. Try:
```bash
# Force rebuild without cache
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

Make sure you're in the right project:
```bash
gcloud config set project aletheia-codex-prod
gcloud auth list
```

### Still Getting 403 Errors

Check IAM permissions:
```bash
gcloud run services get-iam-policy review-api \
  --region=us-central1 \
  --project=aletheia-codex-prod
```

Should show:
```yaml
bindings:
- members:
  - allUsers
  role: roles/run.invoker
```

If not, grant access:
```bash
gcloud run services add-iam-policy-binding review-api \
  --region=us-central1 \
  --member="allUsers" \
  --role="roles/run.invoker" \
  --project=aletheia-codex-prod
```

---

## After Successful Deployment

### Update firebase.json (Optional Cleanup)

Since the service is now public, you can remove the invoker parameter:

```bash
cd ~/aletheia-codex
git checkout sprint-1
```

Edit `firebase.json` and change:
```json
{
  "source": "/api/review/**",
  "run": {
    "serviceId": "review-api",
    "region": "us-central1",
    "invoker": "firebase-invoker@aletheia-codex-prod.iam.gserviceaccount.com"
  }
}
```

To:
```json
{
  "source": "/api/review/**",
  "run": {
    "serviceId": "review-api",
    "region": "us-central1"
  }
}
```

Then deploy:
```bash
firebase deploy --only hosting --project aletheia-codex-prod
```

---

## Summary of Changes

### What Was Done
1. ✅ Deleted organization policy
2. ✅ Granted public access to review-api
3. ✅ Fixed import path in main.py
4. ✅ Committed and pushed to GitHub
5. ⏳ **Need to deploy** (you're doing this now)

### Time Investment
- Sprint 1: 6+ hours
- Sprint 1.1: 4 hours
- Sprint 1.2: 2 hours
- Sprint 1.3: 6 hours
- Policy troubleshooting: 2 hours
- **Total**: 20+ hours

### Resolution
- **Delete organization policy**: 5 minutes
- **Fix import path**: 5 minutes
- **Deploy service**: 5 minutes
- **Total to working app**: 15 minutes

---

## Next Steps After This Works

1. **Deploy other services** (graph-api, notes-api, orchestration-api)
2. **Update firebase.json** with all services
3. **Test all features**
4. **Merge sprint-1 to main**
5. **Implement monitoring and safeguards**

---

## Files Changed

- `functions/review_api/main.py` - Fixed import path
- Commit: `a95e839` on sprint-1 branch
- Pushed to GitHub: ✅

---

**Ready to deploy!** Run the commands above in Cloud Shell.

**Estimated time**: 5 minutes to fully functional application 🚀