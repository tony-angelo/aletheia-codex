# Immediate Fixes Required

**Priority**: CRITICAL  
**Estimated Time**: 20-30 minutes  
**Status**: Ready to Execute

---

## Fix #1: Firestore Rules Field Name Mismatch (5 minutes)

### Problem
Dashboard shows: `FirebaseError: Missing or insufficient permissions`

### Root Cause
Firestore rules use inconsistent field names:
- `notes` collection rules check: `resource.data.userId`
- Actual notes in database use: `user_id`
- `review_queue` rules correctly use: `user_id`

### Solution
Update firestore.rules to use consistent `user_id` field name.

### Steps

1. **Update firestore.rules**:

```bash
cd /workspace/aletheia-codex
```

Replace the notes section in `firestore.rules`:

**BEFORE**:
```
match /notes/{noteId} {
  allow read: if isAuthenticated() && resource.data.userId == request.auth.uid;
  allow create: if isAuthenticated() && request.resource.data.userId == request.auth.uid;
  allow update: if isAuthenticated() && resource.data.userId == request.auth.uid;
  allow delete: if isAuthenticated() && resource.data.userId == request.auth.uid;
}
```

**AFTER**:
```
match /notes/{noteId} {
  allow read: if isAuthenticated() && resource.data.user_id == request.auth.uid;
  allow create: if isAuthenticated() && request.resource.data.user_id == request.auth.uid;
  allow update: if isAuthenticated() && resource.data.user_id == request.auth.uid;
  allow delete: if isAuthenticated() && resource.data.user_id == request.auth.uid;
}
```

2. **Deploy updated rules**:

```bash
firebase deploy --only firestore:rules --project aletheia-codex-prod
```

3. **Verify deployment**:
```bash
# Should show: ✔  firestore: released rules
```

4. **Test in browser**:
- Refresh Dashboard page
- Should now show: Total Notes: 8, Entities: X, Relationships: Y

---

## Fix #2: Verify Graph API Deployment (10 minutes)

### Problem
Knowledge Graph shows: `Unexpected token '<', "<!doctype "... is not valid JSON`

### Root Cause
Graph API either not deployed or returning HTML error page instead of JSON.

### Solution
Verify graph-api deployment status and redeploy if needed.

### Steps

1. **Check if graph-api is deployed**:

```bash
gcloud run services describe graph-api \
  --region=us-central1 \
  --project=aletheia-codex-prod
```

**Expected Output**: Service details (URL, status, etc.)  
**If Error**: "Service not found" - proceed to step 2

2. **If not deployed, deploy graph-api**:

```bash
cd /workspace/aletheia-codex/functions

gcloud run deploy graph-api \
  --source=graph_api \
  --region=us-central1 \
  --platform=managed \
  --allow-unauthenticated \
  --no-invoker-iam-check \
  --set-env-vars="GCP_PROJECT=aletheia-codex-prod" \
  --memory=512Mi \
  --cpu=1 \
  --project=aletheia-codex-prod
```

3. **Grant Firestore permissions to service account**:

```bash
gcloud projects add-iam-policy-binding aletheia-codex-prod \
  --member="serviceAccount:679360092359-compute@developer.gserviceaccount.com" \
  --role="roles/datastore.user"
```

4. **Test direct API access**:

```bash
# Get auth token
TOKEN=$(gcloud auth print-identity-token)

# Test graph API
curl -H "Authorization: Bearer $TOKEN" \
  https://graph-api-679360092359.us-central1.run.app
```

**Expected Response**: JSON with success/error message (not HTML)

5. **Test via Firebase Hosting**:
- Open browser to: https://aletheiacodex.app/graph
- Should load without JSON parse error
- May show "No nodes found" (expected if database empty)

---

## Fix #3: Verify Review Stats (5 minutes)

### Problem
Review page shows blank stats values.

### Root Cause
Either empty database (expected for new user) or API not returning correct format.

### Solution
Test stats endpoint and verify response structure.

### Steps

1. **Test stats endpoint directly**:

```bash
# Get auth token
TOKEN=$(gcloud auth print-identity-token)

# Test stats API
curl -H "Authorization: Bearer $TOKEN" \
  https://review-api-679360092359.us-central1.run.app/stats
```

**Expected Response**:
```json
{
  "success": true,
  "data": {
    "total": 0,
    "pending": 0,
    "approved": 0,
    "rejected": 0
  }
}
```

2. **If response is correct but stats still blank**:
- This is EXPECTED behavior for a new user with no review items
- Stats will populate once notes are processed and entities/relationships extracted

3. **If response is incorrect or error**:
- Check Cloud Run logs:
```bash
gcloud run services logs read review-api \
  --region=us-central1 \
  --project=aletheia-codex-prod \
  --limit=50
```

---

## Verification Checklist

After applying all fixes, verify:

### Dashboard Page
- [ ] No Firestore permission errors in console
- [ ] Total Notes shows: 8
- [ ] Entities count displays (may be 0)
- [ ] Relationships count displays (may be 0)
- [ ] Recent notes list shows items

### Review Page
- [ ] No console errors
- [ ] Stats display (even if 0)
- [ ] Page loads without errors

### Knowledge Graph Page
- [ ] No JSON parse errors
- [ ] Page loads successfully
- [ ] Shows "No nodes found" or displays nodes
- [ ] Search and filter controls work

---

## Expected Results

### After Fix #1 (Firestore Rules)
✅ Dashboard fully functional  
✅ Stats display correctly  
✅ Recent notes list populated

### After Fix #2 (Graph API)
✅ Knowledge Graph page loads  
✅ No JSON parse errors  
✅ Can search/filter (even if no results)

### After Fix #3 (Review Stats)
✅ Review stats display (may be 0)  
✅ No API errors  
✅ Page fully functional

---

## Rollback Plan

If any fix causes issues:

### Rollback Firestore Rules
```bash
cd /workspace/aletheia-codex
git checkout HEAD~1 firestore.rules
firebase deploy --only firestore:rules --project aletheia-codex-prod
```

### Rollback Graph API
```bash
# Delete service
gcloud run services delete graph-api \
  --region=us-central1 \
  --project=aletheia-codex-prod
```

---

## Post-Fix Testing

1. **Clear browser cache** (Ctrl+Shift+Delete)
2. **Open incognito window**
3. **Login to application**
4. **Test each page**:
   - Dashboard
   - Notes
   - Review
   - Knowledge Graph
5. **Check browser console** for errors
6. **Verify all features** work as expected

---

## Timeline

| Fix | Time | Status |
|-----|------|--------|
| Fix #1: Firestore Rules | 5 min | ⏳ Pending |
| Fix #2: Graph API | 10 min | ⏳ Pending |
| Fix #3: Review Stats | 5 min | ⏳ Pending |
| Testing | 10 min | ⏳ Pending |
| **Total** | **30 min** | |

---

## Success Criteria

Application is considered STABLE when:
- ✅ All pages load without errors
- ✅ Dashboard displays stats correctly
- ✅ Review page displays stats (even if 0)
- ✅ Knowledge Graph loads without JSON errors
- ✅ No console errors in browser
- ✅ All API calls return JSON (not HTML)