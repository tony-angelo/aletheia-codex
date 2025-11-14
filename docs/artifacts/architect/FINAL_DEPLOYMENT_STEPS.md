# Final Deployment Steps - Complete Guide

**Date**: 2024-01-13  
**Status**: Ready for Execution  
**Estimated Time**: 10 minutes

---

## Current Status

- ✅ **review-api**: Working perfectly
- ✅ **graph-api**: Working perfectly
- ❌ **notes-api**: Failed - needs to pull latest code and redeploy
- ⚠️ **orchestration-api**: This is a Firestore trigger, not HTTP endpoint (ignore 405 error)

---

## Critical Issue: notes-api

The notes-api deployment is using **old code** (before the symlink was replaced). You MUST pull the latest changes before redeploying.

---

## Step-by-Step Instructions

### Step 1: Pull Latest Code (CRITICAL)

```bash
cd ~/aletheia-codex
git checkout sprint-1
git pull origin sprint-1
```

**Verify the fix is present**:
```bash
# Check that shared is a real directory, not a symlink
ls -la functions/notes_api/shared
```

**Expected Output**: Should show `drwxr-xr-x` (directory), NOT `lrwxrwxrwx` (symlink)

---

### Step 2: Redeploy notes-api

```bash
cd ~/aletheia-codex/functions

gcloud run deploy notes-api \
  --source=notes_api \
  --region=us-central1 \
  --platform=managed \
  --no-invoker-iam-check \
  --set-env-vars="GCP_PROJECT=aletheia-codex-prod" \
  --memory=512Mi \
  --cpu=1 \
  --project=aletheia-codex-prod
```

**Expected**: Build should succeed and container should start

---

### Step 3: Deploy Firebase Hosting

```bash
cd ~/aletheia-codex
firebase deploy --only hosting --project aletheia-codex-prod
```

**This removes the orchestration-api route** (it's not an HTTP endpoint)

---

### Step 4: Test All Services

```bash
# Test review-api (already working)
curl -X GET "https://aletheiacodex.app/api/review/pending" \
  -H "Content-Type: application/json"

# Test graph-api (already working)
curl -X GET "https://aletheiacodex.app/api/graph/nodes" \
  -H "Content-Type: application/json"

# Test notes-api (should work after redeploy)
curl -X GET "https://aletheiacodex.app/api/notes" \
  -H "Content-Type: application/json"
```

**Expected for ALL THREE**:
```json
{"error":"Missing Authorization header"}
```

**NOT Expected**:
- HTML response
- 500 errors
- 503 errors
- ModuleNotFoundError in logs

---

## About orchestration-api

**DO NOT test orchestration-api with curl**. It's a **Firestore trigger** that:
- Automatically runs when documents are created in Firestore
- Uses CloudEvent signature, not HTTP
- Should NOT be exposed via Firebase Hosting
- The 405 error is expected and correct

**The orchestration-api is working correctly as a background service.**

---

## Verification Checklist

After completing all steps:

- [ ] Pulled latest code from sprint-1 branch
- [ ] Verified notes_api/shared is a directory (not symlink)
- [ ] notes-api deployed successfully
- [ ] Firebase Hosting deployed successfully
- [ ] review-api returns 401 (working)
- [ ] graph-api returns 401 (working)
- [ ] notes-api returns 401 (working)
- [ ] No ModuleNotFoundError in any logs

---

## If notes-api Still Fails

If you still get ModuleNotFoundError after pulling and redeploying:

1. **Verify you pulled the latest code**:
   ```bash
   cd ~/aletheia-codex
   git log --oneline -1
   ```
   **Expected**: Should show commit `7ba9495` or later

2. **Check the shared directory**:
   ```bash
   ls -la functions/notes_api/shared/auth/
   ```
   **Expected**: Should show `firebase_auth.py`

3. **Try cleaning the build cache**:
   ```bash
   gcloud builds list --limit=5 --project=aletheia-codex-prod
   # Then redeploy
   ```

---

## Success Criteria

✅ **Phase 1.3.7 Complete** when:
- All three HTTP services (review, graph, notes) return 401
- No import errors in logs
- Application works in browser
- Users can login and access all features

---

## Next Phase

After Phase 1.3.7 is complete:
- **Phase 1.3.8**: Final validation and testing
- **Phase 1.3.9**: Merge sprint-1 to main
- **Phase 1.4**: Production monitoring and optimization

---

**Created By**: Architect (SuperNinja AI Agent)  
**Date**: 2024-01-13  
**Status**: Ready for Execution