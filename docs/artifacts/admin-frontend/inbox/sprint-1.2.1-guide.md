# Sprint 1.2.1 Guide: Fix Firebase Hosting Circular Rewrite and API Path Duplication

**Sprint**: 1.2.1  
**Domain**: Frontend  
**Admin Node**: Admin-Frontend  
**Priority**: CRITICAL  
**Estimated Duration**: 1-2 hours  
**Branch**: `sprint-1` (continue on existing branch)

---

## Sprint Goal

Fix two critical issues preventing API calls from working:
1. **Circular rewrite** in `firebase.json` causing infinite loops
2. **Duplicate path prefixes** in API service endpoints

---

## Problem Statement

### Issue 1: Firebase Hosting Circular Rewrite
**Current Configuration** (`firebase.json`):
```json
{
  "source": "/api/**",
  "destination": "https://aletheiacodex.app/api/:splat"
}
```

**Problem**: This creates an infinite loop:
- User requests: `https://aletheiacodex.app/api/review/pending`
- Firebase Hosting rewrites to: `https://aletheiacodex.app/api/review/pending` (same URL!)
- Loops back to Firebase Hosting again
- Eventually returns HTML (`index.html` fallback) instead of JSON
- Frontend tries to parse HTML as JSON → **"Unexpected token '<', '<!doctype'... is not valid JSON"**

**Solution**: Point to the Load Balancer IP address instead:
```json
{
  "source": "/api/**",
  "destination": "https://34.120.185.233/api/:splat"
}
```

### Issue 2: API Path Duplication
**Current Code** (`web/src/services/api.ts`):
```typescript
const API_BASE_URL = '/api/review';

export const reviewApi = {
  getPendingItems: async (params) => {
    const endpoint = `/review/pending${...}`;  // ❌ Duplicate /review
    return apiRequest(endpoint);
  }
};
```

**Problem**: Creates duplicate paths:
- Base URL: `/api/review`
- Endpoint: `/review/pending`
- Result: `/api/review/review/pending` ❌

**Solution**: Remove service prefix from endpoints:
```typescript
const endpoint = `/pending${...}`;  // ✅ No duplicate
```

---

## Technical Context

### Correct Request Flow
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
- **URL Map Routes**:
  - `/api/review/*` → review-function
  - `/api/graph/*` → graph-function
  - `/api/notes/*` → notes-function
  - `/api/orchestration/*` → orchestration-function
  - `/api/auth/*` → auth-function
  - `/api/user/*` → user-function

---

## Tasks

### 1. Fix Firebase Hosting Rewrite Configuration
**File**: `firebase.json` (root directory)

**Current Code**:
```json
{
  "hosting": {
    "public": "web/build",
    "site": "aletheia-codex-prod",
    "rewrites": [
      {
        "source": "/api/**",
        "destination": "https://aletheiacodex.app/api/:splat"
      },
      {
        "source": "**",
        "destination": "/index.html"
      }
    ]
  }
}
```

**Fixed Code**:
```json
{
  "hosting": {
    "public": "web/build",
    "site": "aletheia-codex-prod",
    "rewrites": [
      {
        "source": "/api/**",
        "destination": "https://34.120.185.233/api/:splat"
      },
      {
        "source": "**",
        "destination": "/index.html"
      }
    ]
  }
}
```

**Action**:
- [ ] Open `firebase.json` in root directory
- [ ] Locate the `/api/**` rewrite rule
- [ ] Change destination from `https://aletheiacodex.app/api/:splat` to `https://34.120.185.233/api/:splat`
- [ ] Save the file

**Why This Works**:
- Breaks the circular loop by pointing to a different host (Load Balancer IP)
- Load Balancer handles routing to appropriate Cloud Functions
- Returns JSON responses instead of HTML

---

### 2. Fix Review API Path Duplication
**File**: `web/src/services/api.ts`

**Current Code** (lines 76-77):
```typescript
const endpoint = `/review/pending${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
return apiRequest(endpoint);
```

**Fixed Code**:
```typescript
const endpoint = `/pending${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
return apiRequest(endpoint);
```

**All Review Endpoints to Fix**:
```typescript
export const reviewApi = {
  getPendingItems: async (params) => {
    // Change: /review/pending → /pending
    const endpoint = `/pending${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
    return apiRequest(endpoint);
  },

  approveItem: async (itemId: string) => {
    // Change: /review/approve → /approve
    return apiRequest('/approve', {
      method: 'POST',
      body: JSON.stringify({ item_id: itemId }),
    });
  },

  rejectItem: async (itemId: string, reason?: string) => {
    // Change: /review/reject → /reject
    return apiRequest('/reject', {
      method: 'POST',
      body: JSON.stringify({ item_id: itemId, reason }),
    });
  },

  batchApproveItems: async (itemIds: string[]) => {
    // Change: /review/batch-approve → /batch-approve
    return apiRequest('/batch-approve', {
      method: 'POST',
      body: JSON.stringify({ item_ids: itemIds }),
    });
  },

  batchRejectItems: async (itemIds: string[], reason?: string) => {
    // Change: /review/batch-reject → /batch-reject
    return apiRequest('/batch-reject', {
      method: 'POST',
      body: JSON.stringify({ item_ids: itemIds, reason }),
    });
  },

  getItemById: async (itemId: string) => {
    // Change: /review/${itemId} → /${itemId}
    return apiRequest(`/${itemId}`);
  },

  updateItem: async (itemId: string, updates: any) => {
    // Change: /review/${itemId} → /${itemId}
    return apiRequest(`/${itemId}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    });
  },
};
```

**Action**:
- [ ] Open `web/src/services/api.ts`
- [ ] Find all `reviewApi` methods
- [ ] Remove `/review` prefix from every endpoint
- [ ] Keep only the specific path (e.g., `/pending`, `/approve`, `/${itemId}`)

---

### 3. Check and Fix Other Service Files (If They Exist)

#### Graph Service
**File**: `web/src/services/graphService.ts` (if exists)

**Expected Issue**:
```typescript
const API_BASE_URL = '/api/graph';
export const getGraph = () => api.get('/graph/data');  // ❌ Duplicate /graph
```

**Fix**:
```typescript
export const getGraph = () => api.get('/data');  // ✅ No duplicate
```

**Action**:
- [ ] Check if `web/src/services/graphService.ts` exists
- [ ] If yes, remove `/graph` prefix from all endpoints
- [ ] If no, skip this step

#### Notes Service
**File**: Check `web/src/services/api.ts` or separate notes file

**Expected Issue**:
```typescript
const API_BASE_URL = '/api/notes';
export const notesApi = {
  getNotes: () => api.get('/notes/list'),  // ❌ Duplicate /notes
};
```

**Fix**:
```typescript
export const notesApi = {
  getNotes: () => api.get('/list'),  // ✅ No duplicate
};
```

**Action**:
- [ ] Search for notes-related API code
- [ ] Remove `/notes` prefix from endpoints if found
- [ ] If no notes API exists, skip this step

#### Orchestration Service
**File**: `web/src/services/orchestration.ts` (if exists)

**Expected Issue**:
```typescript
const API_BASE_URL = '/api/orchestration';
export const startWorkflow = (data) => api.post('/orchestration/start', data);  // ❌
```

**Fix**:
```typescript
export const startWorkflow = (data) => api.post('/start', data);  // ✅
```

**Action**:
- [ ] Check if `web/src/services/orchestration.ts` exists
- [ ] If yes, remove `/orchestration` prefix from all endpoints
- [ ] If no, skip this step

---

### 4. Build and Test Locally
**Commands**:
```bash
cd web
npm run build
npm run preview  # Test locally before deploying
```

**Testing Checklist**:
- [ ] Open browser to `http://localhost:4173` (or preview port)
- [ ] Open DevTools → Network tab
- [ ] Navigate to Review page
- [ ] Verify API calls show correct paths (e.g., `/api/review/pending`)
- [ ] Confirm responses are JSON (not HTML)
- [ ] Check for no 403 Forbidden errors
- [ ] Verify data loads successfully

**Expected Network Requests**:
```
Request: GET /api/review/pending?limit=50
Status: 200 OK
Response: JSON data (not HTML)
```

---

### 5. Deploy to Production
**Commands**:
```bash
# Deploy Firebase Hosting with new configuration
firebase deploy --only hosting

# Verify deployment
curl -I https://aletheiacodex.app/api/review/pending
```

**Verification Steps**:
- [ ] Visit `https://aletheiacodex.app`
- [ ] Log in with Firebase Auth
- [ ] Navigate to Review page
- [ ] Open DevTools → Network tab
- [ ] Verify API calls return JSON (not HTML)
- [ ] Confirm no "Unexpected token '<'" errors
- [ ] Test Review functionality (approve/reject items)

---

### 6. Document and Commit
**Files Changed**:
- `firebase.json` (rewrite configuration)
- `web/src/services/api.ts` (review endpoints)
- `web/src/services/graphService.ts` (if exists)
- `web/src/services/orchestration.ts` (if exists)

**Commit Message**:
```
fix(frontend): resolve circular rewrite and API path duplication

Firebase Hosting Changes:
- Fix circular rewrite in firebase.json
- Point /api/** to Load Balancer IP (34.120.185.233) instead of aletheiacodex.app
- Prevents infinite loop that returned HTML instead of JSON

API Service Changes:
- Remove /review prefix from reviewApi endpoints
- Remove /graph prefix from graphService endpoints (if exists)
- Remove /notes prefix from notesApi endpoints (if exists)
- Remove /orchestration prefix from orchestration endpoints (if exists)
- Fixes duplicate path segments (e.g., /api/review/review/pending)

Resolves Sprint 1.2.1:
- Fixes "Unexpected token '<', '<!doctype'... is not valid JSON" error
- Enables proper API communication through Load Balancer
- Review page now functional

Related: Sprint 1 (Load Balancer), Sprint 1.1 (IAP removal), Sprint 1.2 (Custom domain)
```

**Action**:
- [ ] Commit all changes to `sprint-1` branch
- [ ] Push to GitHub
- [ ] Create session log documenting the fixes

---

## Success Criteria

### Must Have ✅
- [ ] Firebase Hosting rewrites to Load Balancer IP (not circular)
- [ ] Review API endpoints have no duplicate prefixes
- [ ] API calls return JSON responses (not HTML)
- [ ] No "Unexpected token '<'" errors in console
- [ ] Review page loads and displays data
- [ ] Changes deployed to production
- [ ] Application fully functional at `https://aletheiacodex.app`

### Should Have 📋
- [ ] Local testing completed before deployment
- [ ] Browser DevTools Network tab shows correct API paths
- [ ] All API services checked for duplicate prefixes
- [ ] Session log created documenting the fixes
- [ ] Clear commit message explaining both fixes

### Nice to Have 🎯
- [ ] Add comments in firebase.json explaining the Load Balancer rewrite
- [ ] Add comments in API services explaining the base URL pattern
- [ ] Document the circular rewrite issue for future reference
- [ ] Create a troubleshooting guide for similar issues

---

## Acceptance Criteria

1. **Functional Testing**:
   - User can log in at `https://aletheiacodex.app`
   - Review page loads without errors
   - API calls return JSON data (not HTML)
   - No "Unexpected token '<'" errors in browser console
   - Review items display correctly
   - Approve/reject functionality works

2. **Technical Verification**:
   - Firebase Hosting rewrites `/api/**` to `https://34.120.185.233/api/:splat`
   - API calls in Network tab show correct paths (e.g., `/api/review/pending`)
   - No duplicate path segments (e.g., no `/api/review/review/pending`)
   - Responses have `Content-Type: application/json`
   - HTTP status codes are 200 OK (not 403 Forbidden)

3. **Code Quality**:
   - All service files updated consistently
   - No remaining duplicate prefixes in any API service
   - Clear commit message explaining both fixes
   - Session log documents the work

---

## Root Cause Summary

### Why This Happened

1. **Circular Rewrite**:
   - Sprint 1 set up Load Balancer with IP 34.120.185.233
   - Sprint 1.2 configured custom domain `aletheiacodex.app`
   - Firebase Hosting was updated to rewrite `/api/**` but pointed back to the same domain
   - This created an infinite loop instead of forwarding to the Load Balancer

2. **Path Duplication**:
   - API service files were created with full paths including service prefixes
   - When `API_BASE_URL` was added, it duplicated the service prefix
   - This wasn't caught during initial testing because the circular rewrite prevented any API calls from reaching the backend

### How to Prevent This

1. **Always test rewrites with curl**:
   ```bash
   curl -I https://aletheiacodex.app/api/review/pending
   ```
   Should return JSON, not HTML

2. **Use Load Balancer IP in rewrites**:
   - Never rewrite to the same domain
   - Always point to the actual backend (Load Balancer IP)

3. **Consistent API path patterns**:
   - Document the base URL + endpoint pattern
   - Add comments explaining the path construction
   - Test all endpoints after refactoring

4. **End-to-end testing**:
   - Test actual API calls in browser DevTools
   - Verify response content types
   - Check for duplicate path segments

---

## Dependencies

### Required Access
- GitHub repository write access (already granted)
- Firebase project access (already configured)
- Service account credentials (already authenticated)

### Required Tools
- Node.js and npm (already installed)
- Firebase CLI (already installed)
- Git (already configured)

### Blockers
- None expected (straightforward configuration and code fixes)

---

## Escalation Triggers

Escalate to Architect if:
1. **Load Balancer Issues**: Cannot reach Load Balancer at 34.120.185.233
2. **SSL Certificate Problems**: HTTPS errors when accessing Load Balancer IP
3. **CORS Errors**: Cross-origin issues after fixing rewrites
4. **Authentication Failures**: Firebase Auth tokens not accepted by backend
5. **Deployment Failures**: Cannot deploy to Firebase Hosting
6. **Unexpected Behavior**: Fixes don't resolve the JSON parsing errors

**Escalation Process**:
1. Document the issue in `docs/artifacts/admin-frontend/escalations/sprint-1.2.1-blocker.md`
2. Include:
   - Error messages and stack traces
   - Network tab screenshots showing requests/responses
   - curl output for API endpoints
   - Attempted solutions and results
3. Notify Architect via inbox message

---

## Timeline

- **Hour 0-0.5**: Fix firebase.json rewrite configuration
- **Hour 0.5-1**: Fix API service path duplication
- **Hour 1-1.5**: Local testing and verification
- **Hour 1.5-2**: Production deployment and testing

**Total Estimated Time**: 1-2 hours

---

## Testing Commands

### Test Load Balancer Directly
```bash
# Should return JSON
curl -H "Authorization: Bearer YOUR_FIREBASE_TOKEN" \
  https://34.120.185.233/api/review/pending

# Should return JSON (not HTML)
curl -I https://34.120.185.233/api/review/pending
```

### Test Through Firebase Hosting
```bash
# Should return JSON (after fix)
curl -I https://aletheiacodex.app/api/review/pending

# Should NOT return HTML
curl https://aletheiacodex.app/api/review/pending | head -1
# Expected: { or [ (JSON)
# Not: <!DOCTYPE html>
```

### Test in Browser
```javascript
// Open DevTools Console on https://aletheiacodex.app
fetch('/api/review/pending')
  .then(r => r.json())
  .then(data => console.log('Success:', data))
  .catch(err => console.error('Error:', err));
```

---

## Notes

### Related Sprints
- **Sprint 1**: Load Balancer setup (IP: 34.120.185.233)
- **Sprint 1.1**: IAP removal (restored public access)
- **Sprint 1.2**: Custom domain configuration (aletheiacodex.app)
- **Sprint 1.2.1**: Fix circular rewrite and path duplication (this sprint)

### Key Learnings
1. Always test rewrites with actual HTTP requests
2. Never rewrite to the same domain (creates loops)
3. Document base URL patterns in code comments
4. Verify response content types in testing
5. Check for duplicate path segments after refactoring

---

**Created**: 2025-01-13  
**Author**: Architect  
**Status**: Ready for Execution  
**Priority**: CRITICAL - Application is non-functional without these fixes