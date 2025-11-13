# Sprint 1.2.2 Guide: Fix Firebase Hosting Circular Rewrite

**Sprint**: 1.2.2  
**Domain**: Frontend  
**Admin Node**: Admin-Frontend  
**Priority**: CRITICAL  
**Estimated Duration**: 30 minutes  
**Branch**: `sprint-1` (continue on existing branch)

---

## Sprint Goal

Fix the Firebase Hosting circular rewrite configuration that is causing 404 errors and returning HTML instead of JSON from API endpoints.

---

## Problem Statement

### Current Issue
Despite fixing the API path duplication in Sprint 1.2, the application still shows:
- **404 Not Found** errors for `/api/review/pending` and `/api/review/stats`
- **"Unexpected token '<', '<!doctype'... is not valid JSON"** error
- API calls returning HTML instead of JSON

### Root Cause: Circular Rewrite in firebase.json

**Current Configuration**:
```json
{
  "source": "/api/**",
  "destination": "https://aletheiacodex.app/api/:splat"
}
```

**The Problem**:
1. User requests: `https://aletheiacodex.app/api/review/pending`
2. Firebase Hosting rewrites to: `https://aletheiacodex.app/api/review/pending` (SAME URL!)
3. This loops back to Firebase Hosting again
4. Eventually returns HTML (`index.html` fallback) instead of JSON
5. Frontend tries to parse HTML as JSON → **Error!**

**Why Sprint 1.2 Didn't Fix This**:
Sprint 1.2 only fixed the API path duplication in `web/src/services/api.ts`. The `firebase.json` configuration was not updated, so the circular rewrite still exists.

---

## Solution

### Change firebase.json to Point to Load Balancer IP

**Current (WRONG)**:
```json
{
  "hosting": {
    "rewrites": [
      {
        "source": "/api/**",
        "destination": "https://aletheiacodex.app/api/:splat"
      }
    ]
  }
}
```

**Fixed (CORRECT)**:
```json
{
  "hosting": {
    "rewrites": [
      {
        "source": "/api/**",
        "destination": "https://34.120.185.233/api/:splat"
      }
    ]
  }
}
```

**Why This Works**:
- Breaks the circular loop by pointing to a different host (Load Balancer IP: 34.120.185.233)
- Load Balancer handles routing to appropriate Cloud Functions
- Returns JSON responses instead of HTML

---

## Technical Context

### Correct Request Flow (After Fix)
```
User Browser
  ↓
https://aletheiacodex.app/api/review/pending
  ↓
Firebase Hosting (rewrites to Load Balancer)
  ↓
https://34.120.185.233/api/review/pending
  ↓
Load Balancer (routes based on URL map)
  ↓
Cloud Function: review-function
  ↓
Returns JSON response
```

### Load Balancer Details
- **IP Address**: 34.120.185.233
- **Configured in**: Sprint 1 (Infrastructure)
- **URL Map Routes**:
  - `/api/review/*` → review-function
  - `/api/graph/*` → graph-function
  - `/api/notes/*` → notes-function
  - `/api/orchestration/*` → orchestration-function
  - `/api/auth/*` → auth-function
  - `/api/user/*` → user-function

---

## Tasks

### 1. Update firebase.json Rewrite Configuration

**File**: `firebase.json` (root directory)

**Action**:
- [ ] Open `firebase.json` in the root directory
- [ ] Locate the `/api/**` rewrite rule (around line 25)
- [ ] Change the destination from `https://aletheiacodex.app/api/:splat` to `https://34.120.185.233/api/:splat`
- [ ] Save the file

**Before**:
```json
{
  "firestore": {
    "database": "(default)",
    "location": "nam5",
    "rules": "firestore.rules",
    "indexes": "firestore.indexes.json"
  },
  "functions": [...],
  "hosting": {
    "public": "web/build",
    "site": "aletheia-codex-prod",
    "ignore": [...],
    "rewrites": [
      {
        "source": "/api/**",
        "destination": "https://aletheiacodex.app/api/:splat"  // ❌ WRONG
      },
      {
        "source": "**",
        "destination": "/index.html"
      }
    ],
    "headers": [...]
  },
  "storage": {...}
}
```

**After**:
```json
{
  "firestore": {
    "database": "(default)",
    "location": "nam5",
    "rules": "firestore.rules",
    "indexes": "firestore.indexes.json"
  },
  "functions": [...],
  "hosting": {
    "public": "web/build",
    "site": "aletheia-codex-prod",
    "ignore": [...],
    "rewrites": [
      {
        "source": "/api/**",
        "destination": "https://34.120.185.233/api/:splat"  // ✅ CORRECT
      },
      {
        "source": "**",
        "destination": "/index.html"
      }
    ],
    "headers": [...]
  },
  "storage": {...}
}
```

---

### 2. Deploy to Production

**Commands**:
```bash
# Deploy Firebase Hosting with new configuration
firebase deploy --only hosting

# Verify deployment
curl -I https://aletheiacodex.app/api/review/pending
```

**Expected Output**:
```
HTTP/2 200
content-type: application/json
...
```

**NOT**:
```
HTTP/2 404
content-type: text/html
...
```

---

### 3. Verify API Endpoints

**Test Commands**:
```bash
# Test through Firebase Hosting (should return JSON)
curl https://aletheiacodex.app/api/review/pending

# Should see JSON response like:
# {"success": true, "data": [...]}

# NOT HTML like:
# <!DOCTYPE html>
```

**Browser Testing**:
- [ ] Visit `https://aletheiacodex.app`
- [ ] Log in with Firebase Auth
- [ ] Navigate to Review page
- [ ] Open DevTools → Network tab
- [ ] Verify API calls return JSON (not HTML)
- [ ] Confirm no "Unexpected token '<'" errors
- [ ] Verify no 404 errors
- [ ] Test Review functionality (approve/reject items)

---

### 4. Document and Commit

**Files Changed**:
- `firebase.json` (rewrite configuration only)

**Commit Message**:
```
fix(hosting): resolve circular rewrite in firebase.json

Firebase Hosting Configuration:
- Fix circular rewrite that pointed /api/** back to aletheiacodex.app
- Point /api/** to Load Balancer IP (34.120.185.233) instead
- Prevents infinite loop that returned HTML instead of JSON

Impact:
- Fixes 404 Not Found errors on API endpoints
- Fixes "Unexpected token '<', '<!doctype'... is not valid JSON" error
- Enables proper API communication through Load Balancer
- Review page now functional

Resolves Sprint 1.2.2 - Firebase Hosting circular rewrite
Related: Sprint 1.2 (API path duplication fix)
```

**Action**:
- [ ] Commit changes to `sprint-1` branch
- [ ] Push to GitHub
- [ ] Create session log documenting the fix

---

## Success Criteria

### Must Have ✅
- [ ] Firebase Hosting rewrites to Load Balancer IP (34.120.185.233)
- [ ] API calls return JSON responses (not HTML)
- [ ] No "Unexpected token '<'" errors in console
- [ ] No 404 Not Found errors
- [ ] Review page loads and displays data
- [ ] Changes deployed to production
- [ ] Application fully functional at `https://aletheiacodex.app`

### Should Have 📋
- [ ] Verified with curl commands
- [ ] Browser DevTools shows JSON responses
- [ ] Session log created
- [ ] Clear commit message

### Nice to Have 🎯
- [ ] Add comment in firebase.json explaining the Load Balancer rewrite
- [ ] Document the circular rewrite issue for future reference

---

## Acceptance Criteria

1. **Functional Testing**:
   - User can log in at `https://aletheiacodex.app`
   - Review page loads without errors
   - API calls return JSON data (not HTML)
   - No "Unexpected token '<'" errors in browser console
   - No 404 Not Found errors
   - Review items display correctly
   - Approve/reject functionality works

2. **Technical Verification**:
   - Firebase Hosting rewrites `/api/**` to `https://34.120.185.233/api/:splat`
   - curl commands return JSON (not HTML)
   - Responses have `Content-Type: application/json`
   - HTTP status codes are 200 OK (not 404)

3. **Code Quality**:
   - Clear commit message explaining the fix
   - Session log documents the work

---

## Why Sprint 1.2 Didn't Fix This

### What Sprint 1.2 Did
Sprint 1.2 fixed the **API path duplication** in `web/src/services/api.ts`:
- Changed `/review/pending` → `/pending`
- Changed `/review/approve` → `/approve`
- etc.

This was **necessary but not sufficient** to fix the issue.

### What Sprint 1.2 Missed
Sprint 1.2 did **NOT** fix the `firebase.json` circular rewrite. The session log shows:
- ✅ Fixed `web/src/services/api.ts`
- ❌ Did NOT fix `firebase.json`

### Why Both Fixes Are Needed
1. **firebase.json fix** (Sprint 1.2.2): Ensures requests reach the Load Balancer
2. **api.ts fix** (Sprint 1.2): Ensures correct paths are used

Without the firebase.json fix, requests never reach the backend, so the api.ts fix has no effect.

---

## Root Cause Timeline

### Sprint 1 (Infrastructure)
- ✅ Created Load Balancer with IP 34.120.185.233
- ✅ Configured URL map for routing

### Sprint 1.2 (Custom Domain)
- ✅ Configured `aletheiacodex.app` as Firebase Hosting custom domain
- ❌ Updated firebase.json rewrite to point to `aletheiacodex.app` (circular!)
- **Should have**: Pointed to Load Balancer IP instead

### Sprint 1.2 (API Path Fix)
- ✅ Fixed API path duplication in `web/src/services/api.ts`
- ❌ Did NOT fix firebase.json circular rewrite
- **Result**: Still broken because requests never reach backend

### Sprint 1.2.2 (This Sprint)
- ✅ Fix firebase.json to point to Load Balancer IP
- ✅ Complete the fix started in Sprint 1.2

---

## Prevention Strategies

### Testing Checklist for Future
1. **Always test rewrites with curl**:
   ```bash
   curl -I https://aletheiacodex.app/api/review/pending
   ```
   Should return JSON, not HTML

2. **Verify response content types**:
   - API endpoints should return `Content-Type: application/json`
   - NOT `Content-Type: text/html`

3. **Check for circular rewrites**:
   - Never rewrite to the same domain
   - Always point to the actual backend (Load Balancer IP)

4. **End-to-end testing**:
   - Test actual API calls in browser DevTools
   - Verify response content types
   - Check for 404 errors

---

## Dependencies

### Required Access
- GitHub repository write access (already granted)
- Firebase project access (already configured)
- Service account credentials (already authenticated)

### Required Tools
- Firebase CLI (already installed)
- Git (already configured)

### Blockers
- None expected (simple configuration change)

---

## Escalation Triggers

Escalate to Architect if:
1. **Load Balancer Issues**: Cannot reach Load Balancer at 34.120.185.233
2. **SSL Certificate Problems**: HTTPS errors when accessing Load Balancer IP
3. **CORS Errors**: Cross-origin issues after fixing rewrites
4. **Authentication Failures**: Firebase Auth tokens not accepted by backend
5. **Deployment Failures**: Cannot deploy to Firebase Hosting
6. **Unexpected Behavior**: Fix doesn't resolve the JSON parsing errors

**Escalation Process**:
1. Document the issue in `docs/artifacts/admin-frontend/escalations/sprint-1.2.2-blocker.md`
2. Include:
   - Error messages and stack traces
   - Network tab screenshots showing requests/responses
   - curl output for API endpoints
   - Attempted solutions and results
3. Notify Architect via inbox message

---

## Timeline

- **Minute 0-5**: Update firebase.json configuration
- **Minute 5-10**: Deploy to Firebase Hosting
- **Minute 10-20**: Test and verify API endpoints
- **Minute 20-30**: Document and commit changes

**Total Estimated Time**: 30 minutes

---

## Testing Commands Reference

### Test Load Balancer Directly
```bash
# Should return JSON
curl https://34.120.185.233/api/review/pending

# Check headers
curl -I https://34.120.185.233/api/review/pending
```

### Test Through Firebase Hosting (After Fix)
```bash
# Should return JSON (not HTML)
curl https://aletheiacodex.app/api/review/pending

# Check headers (should be application/json)
curl -I https://aletheiacodex.app/api/review/pending
```

### Test in Browser Console
```javascript
// Open DevTools Console on https://aletheiacodex.app
fetch('/api/review/pending')
  .then(r => {
    console.log('Content-Type:', r.headers.get('content-type'));
    return r.json();
  })
  .then(data => console.log('Success:', data))
  .catch(err => console.error('Error:', err));
```

---

## Notes

### Key Insight
The circular rewrite in `firebase.json` was the **primary blocker**. The API path duplication was a **secondary issue** that would only become apparent after fixing the circular rewrite.

### Lesson Learned
When updating Firebase Hosting configuration for custom domains, always ensure rewrites point to the actual backend (Load Balancer IP), not back to the same domain.

---

**Created**: 2025-01-13  
**Author**: Architect  
**Status**: Ready for Execution  
**Priority**: CRITICAL - Application is non-functional without this fix  
**Estimated Duration**: 30 minutes