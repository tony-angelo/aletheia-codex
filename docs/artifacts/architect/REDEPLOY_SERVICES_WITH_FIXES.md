# Redeploy Services with Import Path Fixes

**Date**: 2024-01-13  
**Issue**: Services deployed with old code (before import path fixes)  
**Solution**: Pull latest changes and redeploy

---

## Problem

The services were deployed before the import path fixes were pushed to GitHub. The deployed code still has:
- `sys.path.append('/workspace')` (wrong)
- `from shared.auth.unified_auth` (wrong)

This causes the error:
```
ModuleNotFoundError: No module named 'shared.auth.unified_auth'
```

---

## Solution: Pull Latest Code and Redeploy

### Step 1: Pull Latest Changes in Cloud Shell

```bash
cd ~/aletheia-codex
git checkout sprint-1
git pull origin sprint-1
```

**Verify the fix is present**:
```bash
grep -A 2 "sys.path" functions/graph/main.py
```

**Expected Output**:
```python
sys.path.insert(0, os.path.dirname(__file__))

from shared.auth.firebase_auth import require_auth
```

---

### Step 2: Redeploy All Three Services

```bash
cd ~/aletheia-codex/functions

# Redeploy graph-api
gcloud run deploy graph-api \
  --source=graph \
  --region=us-central1 \
  --platform=managed \
  --no-invoker-iam-check \
  --set-env-vars="GCP_PROJECT=aletheia-codex-prod" \
  --memory=512Mi \
  --cpu=1 \
  --project=aletheia-codex-prod

# Redeploy notes-api
gcloud run deploy notes-api \
  --source=notes_api \
  --region=us-central1 \
  --platform=managed \
  --no-invoker-iam-check \
  --set-env-vars="GCP_PROJECT=aletheia-codex-prod" \
  --memory=512Mi \
  --cpu=1 \
  --project=aletheia-codex-prod

# Redeploy orchestration-api
gcloud run deploy orchestration-api \
  --source=orchestration \
  --region=us-central1 \
  --platform=managed \
  --no-invoker-iam-check \
  --set-env-vars="GCP_PROJECT=aletheia-codex-prod" \
  --memory=512Mi \
  --cpu=1 \
  --project=aletheia-codex-prod
```

---

### Step 3: Test Services

After redeployment, test each service:

```bash
# Test graph-api
curl -X GET "https://aletheiacodex.app/api/graph/nodes" \
  -H "Content-Type: application/json"

# Test notes-api
curl -X GET "https://aletheiacodex.app/api/notes" \
  -H "Content-Type: application/json"

# Test orchestration-api
curl -X GET "https://aletheiacodex.app/api/orchestration/status" \
  -H "Content-Type: application/json"
```

**Expected Output for ALL**:
```json
{"error":"Missing Authorization header"}
```

**NOT Expected**: 
- HTML response (means rewrite not working)
- No response (means service crashed)
- 503 Service Unavailable (means service failed to start)

---

## Verification

### Check Service Logs

If any service still fails, check logs:

```bash
# Check graph-api logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=graph-api AND severity>=ERROR" \
  --limit=5 \
  --project=aletheia-codex-prod

# Check notes-api logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=notes-api AND severity>=ERROR" \
  --limit=5 \
  --project=aletheia-codex-prod

# Check orchestration-api logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=orchestration-api AND severity>=ERROR" \
  --limit=5 \
  --project=aletheia-codex-prod
```

**Expected**: No "ModuleNotFoundError" errors

---

## Success Criteria

- [ ] Latest code pulled from GitHub (commit 4d6142f)
- [ ] All three services redeployed successfully
- [ ] All curl tests return `{"error":"Missing Authorization header"}`
- [ ] No 503 errors
- [ ] No import errors in logs
- [ ] Graph page works in browser
- [ ] Notes page works in browser

---

**Created By**: Architect (SuperNinja AI Agent)  
**Date**: 2024-01-13  
**Status**: Ready to Execute