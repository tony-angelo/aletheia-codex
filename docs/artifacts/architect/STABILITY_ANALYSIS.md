# Application Stability Analysis

**Date**: 2024-01-XX  
**Analyst**: Architect Node  
**Status**: CRITICAL ISSUES IDENTIFIED

---

## Executive Summary

The application has **3 critical issues** preventing full functionality:

1. ✅ **WORKING**: Notes API - Fully functional
2. ❌ **BROKEN**: Dashboard - Firestore permission errors
3. ❌ **BROKEN**: Review Page - API returns empty stats
4. ❌ **BROKEN**: Knowledge Graph - Returns HTML instead of JSON

**Root Causes Identified**:
- Firestore security rules blocking direct client access
- Review API not returning data (empty database or API issue)
- Graph API returning HTML (likely 404 or routing issue)

---

## Detailed Analysis

### 1. Dashboard Page - FIRESTORE PERMISSION ERROR ❌

**Error**: `FirebaseError: Missing or insufficient permissions`

**Root Cause**: Dashboard directly queries Firestore from the client:
```typescript
// DashboardPage.tsx line 32-77
const notesQuery = query(
  collection(db, 'notes'),
  where('userId', '==', user.uid)
);
const notesSnapshot = await getDocs(notesQuery);
```

**Problem**: Firestore security rules require authentication, but the client-side query is being blocked.

**Firestore Rules** (firestore.rules):
```
match /notes/{noteId} {
  allow read: if isAuthenticated() && resource.data.userId == request.auth.uid;
}
```

**Why It's Failing**:
- User IS authenticated (we can see they're logged in)
- The rule checks `resource.data.userId == request.auth.uid`
- This suggests either:
  1. Notes don't have `userId` field (should be `user_id`?)
  2. Field name mismatch between code and rules
  3. User has no notes yet (but error says "permission denied" not "no results")

**Evidence from Notes Page**:
- Notes page shows: Total: 8, Processing: 2, Completed: 5, Failed: 1
- This proves notes EXIST and ARE accessible via API
- Dashboard tries to access Firestore directly (fails)
- Notes page uses API (works)

**Conclusion**: Field name mismatch - Firestore rules use `userId` but notes likely use `user_id`

---

### 2. Review Page - EMPTY STATS ❌

**Observation**: Stats show blank values:
```
Total: {{blank}}
Pending: {{blank}}
Approved: {{blank}}
Rejected: {{blank}}
```

**No Console Errors**: API call succeeds but returns empty data

**Root Cause Analysis**:

**Option A: Empty Database** (Most Likely)
- User has no review queue items yet
- Stats API returns success but with zero counts
- This is EXPECTED behavior for a new user

**Option B: API Not Returning Data**
- API call succeeds (no 401/403 errors)
- Response structure might be incorrect
- Frontend expecting different format

**Code Review** (useReviewQueue.ts):
```typescript
const fetchStats = useCallback(async () => {
  try {
    const response = await reviewApi.getUserStats();
    if (response.success && response.data) {
      setStats(response.data);
    }
  } catch (err) {
    console.error('Failed to fetch stats:', err);
  }
}, []);
```

**Verification Needed**:
1. Check if review-api `/stats` endpoint returns data
2. Verify response structure matches frontend expectations
3. Confirm user has review queue items in Firestore

---

### 3. Knowledge Graph - JSON PARSE ERROR ❌

**Error**: `Unexpected token '<', "<!doctype "... is not valid JSON`

**Root Cause**: API returning HTML instead of JSON

**Why This Happens**:
1. **404 Error**: Endpoint doesn't exist, returns HTML error page
2. **Routing Issue**: Firebase Hosting not proxying correctly
3. **CORS Issue**: Browser receiving error page instead of JSON

**Firebase Hosting Configuration** (firebase.json):
```json
{
  "source": "/api/graph/**",
  "run": {
    "serviceId": "graph-api",
    "region": "us-central1",
    "invoker": "firebase-invoker@aletheia-codex-prod.iam.gserviceaccount.com"
  }
}
```

**Frontend Code** (graphService.ts):
```typescript
const GRAPH_API_URL = process.env.REACT_APP_GRAPH_API_URL || '/api/graph';

async getNodes(options = {}): Promise<NodesResponse> {
  const params = new URLSearchParams({
    limit: String(options.limit || 50),
    offset: String(options.offset || 0),
  });
  
  const response = await fetch(`${GRAPH_API_URL}?${params}`, {
    headers,
  });
  
  return response.json(); // FAILS HERE - response is HTML
}
```

**Problem**: 
- Frontend calls `/api/graph?limit=50&offset=0`
- Firebase Hosting should proxy to `graph-api` Cloud Run service
- Instead, returns HTML (likely 404 or error page)

**Possible Causes**:
1. `graph-api` service not deployed or not responding
2. Firebase Hosting rewrite not working
3. Service returning error page instead of JSON error

---

## Critical Issues Summary

### Issue #1: Dashboard Firestore Permission Error
**Severity**: HIGH  
**Impact**: Dashboard completely non-functional  
**Root Cause**: Field name mismatch in Firestore rules  
**Fix Required**: Update firestore.rules to use `user_id` instead of `userId`

### Issue #2: Review Page Empty Stats
**Severity**: LOW (if empty database) / MEDIUM (if API issue)  
**Impact**: Stats not displayed, but page functional  
**Root Cause**: Likely empty database (new user)  
**Fix Required**: Verify API response structure, add sample data for testing

### Issue #3: Knowledge Graph JSON Parse Error
**Severity**: HIGH  
**Impact**: Knowledge Graph completely non-functional  
**Root Cause**: API returning HTML instead of JSON  
**Fix Required**: Verify graph-api deployment and Firebase Hosting proxy

---

## Recommended Fixes

### Priority 1: Fix Firestore Rules (Dashboard)

**Current Rules**:
```
match /notes/{noteId} {
  allow read: if isAuthenticated() && resource.data.userId == request.auth.uid;
}

match /review_queue/{itemId} {
  allow read: if isAuthenticated() && resource.data.user_id == request.auth.uid;
}
```

**Notice**: `notes` uses `userId`, `review_queue` uses `user_id` - INCONSISTENT!

**Fix**: Update firestore.rules to use consistent field names:
```
match /notes/{noteId} {
  allow read: if isAuthenticated() && resource.data.user_id == request.auth.uid;
  allow create: if isAuthenticated() && request.resource.data.user_id == request.auth.uid;
  allow update: if isAuthenticated() && resource.data.user_id == request.auth.uid;
  allow delete: if isAuthenticated() && resource.data.user_id == request.auth.uid;
}
```

**Deployment**:
```bash
cd /workspace/aletheia-codex
firebase deploy --only firestore:rules --project aletheia-codex-prod
```

---

### Priority 2: Verify Graph API Deployment

**Check if graph-api is deployed**:
```bash
gcloud run services describe graph-api \
  --region=us-central1 \
  --project=aletheia-codex-prod
```

**If not deployed, deploy it**:
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

**Test direct API access**:
```bash
curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
  https://graph-api-679360092359.us-central1.run.app
```

---

### Priority 3: Verify Review API Stats Endpoint

**Test stats endpoint directly**:
```bash
curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
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

**If empty, create test data** (optional for testing):
```python
# Add sample review queue item to Firestore
```

---

## Architecture Review

### Current Architecture (Correct)
```
User Browser
  ↓
https://aletheiacodex.app
  ↓
Firebase Hosting (serves React app)
  ↓
API calls to /api/* proxied to Cloud Run
  ↓
Cloud Run Services:
  - review-api ✅ (deployed, working)
  - graph-api ❓ (status unknown)
  - notes-api ✅ (deployed, working)
  ↓
Firestore Database
```

### Security Model (Correct)
- **Layer 1 (GCP IAM)**: Bypassed via `--no-invoker-iam-check`
- **Layer 2 (Application Auth)**: Firebase ID token required
- **Layer 3 (Firestore Rules)**: User-level data isolation

---

## Testing Checklist

### ✅ Working Features
- [x] User authentication (Firebase Auth)
- [x] Notes page (displays 8 notes)
- [x] Notes API (returns data correctly)
- [x] Navigation between pages
- [x] Review page loads (no errors)

### ❌ Broken Features
- [ ] Dashboard stats (Firestore permission error)
- [ ] Review stats (empty/blank values)
- [ ] Knowledge Graph (JSON parse error)

### ⏳ Untested Features
- [ ] Creating new notes
- [ ] Approving/rejecting review items
- [ ] Searching knowledge graph
- [ ] Node details view

---

## Conclusion

**Application Status**: PARTIALLY FUNCTIONAL

**Critical Path to Stability**:
1. Fix Firestore rules (5 minutes) - Restores Dashboard
2. Verify graph-api deployment (10 minutes) - Restores Knowledge Graph
3. Test review stats endpoint (5 minutes) - Verify Review page

**Estimated Time to Full Functionality**: 20-30 minutes

**Recommendation**: Address Priority 1 and Priority 2 fixes immediately. Priority 3 (Review stats) is likely just empty database and can be addressed later.

---

## Next Steps

1. **User Action Required**: Deploy Firestore rules fix
2. **User Action Required**: Verify graph-api deployment status
3. **Architect**: Create detailed fix guides for each issue
4. **Testing**: Re-test all features after fixes applied