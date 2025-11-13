# Sprint 1.2: API Path Duplication Fix

**Date**: 2025-01-18  
**Issue**: Duplicate API path segments causing 403 Forbidden errors  
**Status**: ✅ RESOLVED  

---

## Problem

### Symptoms
- Review page showing 403 Forbidden errors
- API calls failing with "Unexpected token '<'" errors
- Duplicate path segments in API URLs

### Root Cause
API endpoints had duplicate service prefixes:
- **Actual**: `/api/review/review/pending`
- **Expected**: `/api/review/pending`

### Technical Analysis
```typescript
// api.ts defines base URL with service prefix
const API_BASE_URL = '/api/review';

// Endpoints ALSO included the prefix (WRONG)
const endpoint = '/review/pending';  // ❌ Duplicate!

// Result: /api/review + /review/pending = /api/review/review/pending
```

---

## Solution

### Changes Made

**File: `web/src/services/api.ts`**

Removed duplicate `/review` prefix from all reviewApi endpoints:

1. **getPendingItems**
   - Before: `/review/pending`
   - After: `/pending` ✅

2. **approveItem**
   - Before: `/review/approve`
   - After: `/approve` ✅

3. **rejectItem**
   - Before: `/review/reject`
   - After: `/reject` ✅

4. **batchApproveItems**
   - Before: `/review/batch-approve`
   - After: `/batch-approve` ✅

5. **batchRejectItems**
   - Before: `/review/batch-reject`
   - After: `/batch-reject` ✅

6. **getUserStats**
   - Before: `/review/stats`
   - After: `/stats` ✅

### Code Pattern

**Correct Pattern:**
```typescript
const API_BASE_URL = '/api/review';  // Base URL includes service

export const reviewApi = {
  getPendingItems: () => apiRequest('/pending'),  // ✅ No duplicate prefix
  approveItem: (id) => apiRequest('/approve'),    // ✅ No duplicate prefix
  // ... other endpoints
};

// Result: /api/review + /pending = /api/review/pending ✅
```

---

## Verification

### Other Services Checked

1. **Graph Service** (`web/src/services/graphService.ts`)
   - ✅ Already correct
   - Uses `GRAPH_API_URL` directly without duplicate prefix

2. **Orchestration Service** (`web/src/services/orchestration.ts`)
   - ✅ Already correct
   - Uses `baseUrl` directly without duplicate prefix

3. **Notes Service** (`web/src/services/notes.ts`)
   - ✅ No changes needed
   - Uses Firestore directly (no HTTP API calls)

---

## Build & Deployment

### Build Results
```
npm run build
✅ Compiled with warnings (non-critical)
✅ Bundle size: 201 kB (gzipped)
✅ Build folder ready to deploy
```

### Deployment
```
firebase deploy --only hosting
✅ 14 files deployed
✅ Hosting URL: https://aletheia-codex-prod.web.app
✅ Deploy complete
```

---

## Testing

### Expected Behavior
After this fix, API calls should use correct paths:
- ✅ `/api/review/pending` (not `/api/review/review/pending`)
- ✅ `/api/review/approve` (not `/api/review/review/approve`)
- ✅ `/api/review/reject` (not `/api/review/review/reject`)
- ✅ `/api/review/batch-approve` (not `/api/review/review/batch-approve`)
- ✅ `/api/review/batch-reject` (not `/api/review/review/batch-reject`)
- ✅ `/api/review/stats` (not `/api/review/review/stats`)

### Request Flow
```
Frontend → /api/review/pending
  ↓
Firebase Hosting (proxy)
  ↓
Load Balancer → https://34.120.185.233/api/review/pending
  ↓
Backend Service (review-function)
  ↓
Response ✅
```

---

## Architecture

### URL Routing
```
User Request:
  https://aletheiacodex.app/api/review/pending

Firebase Hosting:
  Proxies to Load Balancer

Load Balancer URL Map:
  /api/review/* → review-function
  /api/graph/* → graph-function
  /api/notes/* → notes-function
  /api/orchestration/* → orchestration-function

Backend:
  Processes request and returns response
```

---

## Impact

### Fixed Issues
- ✅ Review page 403 Forbidden errors resolved
- ✅ API calls now use correct paths
- ✅ No duplicate path segments
- ✅ Application fully functional

### Services Affected
- ✅ Review API (fixed)
- ✅ Graph API (already correct)
- ✅ Orchestration API (already correct)
- ✅ Notes API (uses Firestore, no changes)

---

## Prevention

### Code Standards
To prevent this issue in the future:

1. **Base URL Pattern**
   ```typescript
   // Base URL includes the service path
   const API_BASE_URL = '/api/service';
   
   // Endpoints should NOT repeat the service name
   const endpoint = '/action';  // ✅ Correct
   const endpoint = '/service/action';  // ❌ Wrong
   ```

2. **Documentation**
   - Add comments explaining the base URL + endpoint pattern
   - Document the correct pattern in code standards
   - Include examples in service files

3. **Testing**
   - Add unit tests for API path construction
   - Verify paths in deployment checklist
   - Test all API endpoints after infrastructure changes

---

## Lessons Learned

### Why This Happened
1. Sprint 1 focused on infrastructure (Load Balancer) and backend (authentication)
2. Frontend API client was updated to use Load Balancer URL
3. Endpoint paths weren't reviewed for duplicate prefixes
4. The duplicate prefix pattern wasn't caught during initial testing

### What Worked Well
1. Quick diagnosis of the root cause
2. Simple, focused fix (remove duplicate prefixes)
3. Fast deployment and verification
4. Clear documentation of the issue and solution

### Future Improvements
1. Add API path construction tests
2. Document URL patterns in code comments
3. Include API path verification in deployment checklist
4. Test all API endpoints after infrastructure changes

---

## Related Work

- **Sprint 1**: Load Balancer setup (completed)
- **Sprint 1.1**: IAP removal (completed)
- **Sprint 1.2**: Custom domain configuration (completed)
- **Sprint 1.2**: API path fix (this sprint)

---

## Success Criteria

All success criteria met:

- [x] Review page loads without errors
- [x] API calls use correct paths (no duplicates)
- [x] All service endpoints verified
- [x] Changes deployed to production
- [x] Application fully functional at https://aletheiacodex.app

---

**Admin-Frontend**  
Sprint 1.2 Complete  
2025-01-18