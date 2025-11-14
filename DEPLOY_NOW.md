# Deploy Review API - Fixed Build Error

## What Was Fixed

**Problem**: Build failed with pydantic-core dependency error  
**Solution**: Downgraded pydantic from v2.5.0 to v1.10.13

The pydantic v2 requires a Rust compiler to build pydantic-core, which isn't available in Cloud Run's build environment. Using v1 avoids this issue.

---

## Deploy Now (Cloud Shell)

```bash
# 1. Pull latest fix
cd ~/aletheia-codex
git checkout sprint-1
git pull origin sprint-1

# 2. Deploy
cd functions
gcloud run deploy review-api \
  --source=review_api \
  --region=us-central1 \
  --platform=managed \
  --allow-unauthenticated \
  --set-env-vars="GCP_PROJECT=aletheia-codex-prod" \
  --memory=512Mi \
  --cpu=1 \
  --project=aletheia-codex-prod

# 3. Test
curl https://review-api-679360092359.us-central1.run.app
curl https://aletheiacodex.app/api/review/pending
```

---

## Expected Output

### Build Success
```
Building using Buildpacks...
✓ Creating Container Repository
✓ Uploading sources
✓ Building Container
✓ Pushing Container
✓ Deploying Revision
✓ Routing traffic

Service [review-api] revision [review-api-00002-xxx] has been deployed
Service URL: https://review-api-679360092359.us-central1.run.app
```

### Test Success
```json
{
  "success": true,
  "data": [...],
  ...
}
```

---

## Changes Made

### requirements.txt
```diff
- pydantic==2.5.0
+ pydantic==1.10.13

- functions-framework==3.4.0
+ functions-framework==3.8.1

- flask==2.3.3
+ flask==3.0.0

- Removed unused dependencies
```

---

## Time Estimate

- Pull code: 10 seconds
- Build: 3-4 minutes
- Deploy: 1 minute
- Test: 10 seconds

**Total**: ~5 minutes

---

**Ready to deploy!** Run the commands above in Cloud Shell.