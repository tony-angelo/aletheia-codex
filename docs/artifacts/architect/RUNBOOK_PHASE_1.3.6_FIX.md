# Runbook: Phase 1.3.6 Fix - Grant Firestore Permissions

**Phase**: 1.3.6 Fix  
**Objective**: Grant Firestore permissions to Cloud Run service account  
**Estimated Duration**: 5 minutes  
**Priority**: CRITICAL

---

## Issue Summary

The Cloud Run service cannot access Firestore because the service account lacks permissions. This causes all API endpoints to return 500 errors.

**Service Account**: `679360092359-compute@developer.gserviceaccount.com`  
**Missing Permission**: `roles/datastore.user`

---

## Quick Fix Steps

### Step 1: Authenticate
```bash
gcloud auth login
gcloud config set project aletheia-codex-prod
```

### Step 2: Grant Firestore Permission
```bash
gcloud projects add-iam-policy-binding aletheia-codex-prod \
  --member="serviceAccount:679360092359-compute@developer.gserviceaccount.com" \
  --role="roles/datastore.user"
```

**Expected Output**:
```
Updated IAM policy for project [aletheia-codex-prod].
bindings:
- members:
  - serviceAccount:679360092359-compute@developer.gserviceaccount.com
  role: roles/datastore.user
```

### Step 3: Verify Permission
```bash
gcloud projects get-iam-policy aletheia-codex-prod \
  --flatten="bindings[].members" \
  --filter="bindings.members:679360092359-compute@developer.gserviceaccount.com" \
  --format="table(bindings.role)"
```

**Expected Output**:
```
ROLE
roles/cloudbuild.builds.builder
roles/datastore.user
```

### Step 4: Wait for Propagation (30 seconds)
```bash
sleep 30
```

### Step 5: Test API Endpoint
```bash
curl -X GET "https://aletheiacodex.app/api/review/pending" \
  -H "Content-Type: application/json" \
  -w "\n\nHTTP Status: %{http_code}\n"
```

**Expected Output**: 
- HTTP Status: 401 (if not authenticated) - This is correct
- OR HTTP Status: 200 (if authenticated with valid token)

**NOT Expected**: 500 Internal Server Error

---

## Verification in Browser

1. Open `https://aletheiacodex.app`
2. Login with Firebase Auth
3. Navigate to Review page (`https://aletheiacodex.app/review`)
4. Expected: Page loads without errors, shows pending items or "No items"

---

## Success Criteria

- [ ] Service account has `roles/datastore.user` role
- [ ] API endpoints return 200 or 401 (not 500)
- [ ] Review page loads without errors
- [ ] No "Missing or insufficient permissions" in Cloud Run logs
- [ ] No 403 errors in browser console

---

## Rollback Plan

If issues occur, remove the permission:
```bash
gcloud projects remove-iam-policy-binding aletheia-codex-prod \
  --member="serviceAccount:679360092359-compute@developer.gserviceaccount.com" \
  --role="roles/datastore.user"
```

---

**Created By**: Architect (SuperNinja AI Agent)  
**Date**: 2024-01-13  
**Status**: Ready to Execute