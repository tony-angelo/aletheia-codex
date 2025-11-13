# Sprint 1.2 Guide: Fix API Path Duplication

**Sprint**: 1.2  
**Domain**: Frontend  
**Admin Node**: Admin-Frontend  
**Priority**: CRITICAL  
**Estimated Duration**: 2-4 hours  
**Branch**: `sprint-1` (continue on existing branch)

---

## Sprint Goal

Fix API path duplication bug that causes "Unexpected token '<'" errors when accessing Review, Graph, Notes, and Orchestration endpoints.

---

## Problem Statement

### Current Issue
API calls are failing with duplicate path segments:
- **Actual**: `/api/review/review/pending`
- **Expected**: `/api/review/pending`

### Root Cause
In `web/src/services/api.ts` and related service files:
```typescript
// api.ts defines base URL with service prefix
const API_BASE_URL = '/api/review';

// Service files ALSO include the prefix in endpoint definitions
const endpoint = '/review/pending';  // ❌ Duplicate!

// Result: /api/review + /review/pending = /api/review/review/pending
```

### Impact
- Review page completely broken (403 Forbidden)
- Likely affects Graph, Notes, and Orchestration services
- Users cannot access core application features

---

## Technical Context

### Current Architecture
```
Frontend (aletheiacodex.app)
  ↓
Firebase Hosting
  ↓
firebase.json rewrites: /api/** → Load Balancer
  ↓
Load Balancer URL Map:
  - /api/review/* → review-function
  - /api/graph/* → graph-function
  - /api/notes/* → notes-function
  - /api/orchestration/* → orchestration-function
  - /api/auth/* → auth-function
  - /api/user/* → user-function
```

### Correct URL Pattern
- Frontend should call: `/api/review/pending`
- Firebase Hosting proxies to: `https://34.120.185.233/api/review/pending`
- Load Balancer routes to: `review-function`

---

## Tasks

### 1. Fix Review Service API Paths
**File**: `web/src/services/api.ts`

**Current Code** (likely):
```typescript
const API_BASE_URL = '/api/review';

export const reviewApi = {
  getPendingReviews: () => api.get('/review/pending'),
  getReviewById: (id: string) => api.get(`/review/${id}`),
  submitReview: (data: any) => api.post('/review/submit', data),
  // ... other endpoints
};
```

**Fixed Code**:
```typescript
const API_BASE_URL = '/api/review';

export const reviewApi = {
  getPendingReviews: () => api.get('/pending'),  // ✅ Remove /review prefix
  getReviewById: (id: string) => api.get(`/${id}`),  // ✅ Remove /review prefix
  submitReview: (data: any) => api.post('/submit', data),  // ✅ Remove /review prefix
  // ... other endpoints
};
```

**Action**:
- [ ] Open `web/src/services/api.ts`
- [ ] Locate all `reviewApi` endpoint definitions
- [ ] Remove `/review` prefix from each endpoint path
- [ ] Keep only the specific endpoint path (e.g., `/pending`, `/${id}`, `/submit`)

---

### 2. Fix Graph Service API Paths
**File**: `web/src/services/graphService.ts`

**Expected Issue**:
```typescript
const API_BASE_URL = '/api/graph';

// Likely has duplicate /graph prefix in endpoints
export const getGraph = () => api.get('/graph/data');  // ❌
```

**Fix**:
```typescript
const API_BASE_URL = '/api/graph';

export const getGraph = () => api.get('/data');  // ✅
```

**Action**:
- [ ] Open `web/src/services/graphService.ts`
- [ ] Check if `API_BASE_URL` includes `/api/graph`
- [ ] Remove `/graph` prefix from all endpoint definitions
- [ ] Keep only specific paths (e.g., `/data`, `/nodes`, `/edges`)

---

### 3. Fix Notes Service API Paths
**File**: `web/src/services/api.ts` or separate notes service file

**Expected Issue**:
```typescript
const API_BASE_URL = '/api/notes';

export const notesApi = {
  getNotes: () => api.get('/notes/list'),  // ❌
  createNote: (data: any) => api.post('/notes/create', data),  // ❌
};
```

**Fix**:
```typescript
const API_BASE_URL = '/api/notes';

export const notesApi = {
  getNotes: () => api.get('/list'),  // ✅
  createNote: (data: any) => api.post('/create', data),  // ✅
};
```

**Action**:
- [ ] Locate notes service code (check `api.ts` or separate file)
- [ ] Remove `/notes` prefix from endpoint definitions
- [ ] Keep only specific paths

---

### 4. Fix Orchestration Service API Paths
**File**: `web/src/services/orchestration.ts`

**Expected Issue**:
```typescript
const API_BASE_URL = '/api/orchestration';

export const startWorkflow = (data: any) => api.post('/orchestration/start', data);  // ❌
```

**Fix**:
```typescript
const API_BASE_URL = '/api/orchestration';

export const startWorkflow = (data: any) => api.post('/start', data);  // ✅
```

**Action**:
- [ ] Open `web/src/services/orchestration.ts`
- [ ] Remove `/orchestration` prefix from endpoint definitions
- [ ] Keep only specific paths

---

### 5. Verify Auth and User Services
**Files**: `web/src/services/api.ts` (auth and user sections)

**Check**:
```typescript
// These should already be correct, but verify:
const AUTH_BASE_URL = '/api/auth';
export const authApi = {
  login: (data: any) => api.post('/login', data),  // ✅ Correct (no /auth prefix)
};

const USER_BASE_URL = '/api/user';
export const userApi = {
  getProfile: () => api.get('/profile'),  // ✅ Correct (no /user prefix)
};
```

**Action**:
- [ ] Verify auth endpoints don't have `/auth` prefix
- [ ] Verify user endpoints don't have `/user` prefix
- [ ] These likely work already (no reported issues)

---

### 6. Build and Test Locally
**Commands**:
```bash
cd web
npm run build
npm run preview  # Test locally before deploying
```

**Testing Checklist**:
- [ ] Navigate to Review page
- [ ] Check browser DevTools Network tab
- [ ] Verify API calls use correct paths (e.g., `/api/review/pending`)
- [ ] Confirm no 403 Forbidden errors
- [ ] Test Graph, Notes, Orchestration features if accessible

---

### 7. Deploy to Production
**Commands**:
```bash
cd web
npm run build
firebase deploy --only hosting
```

**Verification**:
- [ ] Visit `https://aletheiacodex.app`
- [ ] Log in with Firebase Auth
- [ ] Navigate to Review page
- [ ] Verify data loads successfully
- [ ] Test other features (Graph, Notes, Orchestration)

---

### 8. Document and Commit
**Files to Update**:
- `web/src/services/api.ts`
- `web/src/services/graphService.ts`
- `web/src/services/orchestration.ts`
- Any other service files with API calls

**Commit Message**:
```
fix(frontend): remove duplicate service prefixes from API endpoints

- Remove /review prefix from reviewApi endpoints
- Remove /graph prefix from graphService endpoints
- Remove /notes prefix from notesApi endpoints
- Remove /orchestration prefix from orchestration endpoints
- Fixes 403 Forbidden errors caused by duplicate path segments

Resolves Sprint 1.2 - API path duplication bug
```

**Action**:
- [ ] Commit all changes to `sprint-1` branch
- [ ] Push to GitHub
- [ ] Create session log documenting the fix

---

## Success Criteria

### Must Have ✅
- [ ] Review page loads without errors
- [ ] API calls use correct paths (no duplicates)
- [ ] All service endpoints verified (Review, Graph, Notes, Orchestration)
- [ ] Changes deployed to production
- [ ] Application fully functional at `https://aletheiacodex.app`

### Should Have 📋
- [ ] Local testing completed before deployment
- [ ] Browser DevTools Network tab shows correct API paths
- [ ] Session log created documenting the fix
- [ ] Code committed with clear commit message

### Nice to Have 🎯
- [ ] Add comments in code explaining the base URL + endpoint pattern
- [ ] Create a code standard document for API service patterns
- [ ] Add unit tests for API path construction

---

## Acceptance Criteria

1. **Functional Testing**:
   - User can log in at `https://aletheiacodex.app`
   - Review page loads and displays data
   - No 403 Forbidden errors in browser console
   - Graph, Notes, and Orchestration features work (if accessible)

2. **Technical Verification**:
   - API calls in Network tab show correct paths (e.g., `/api/review/pending`)
   - No duplicate path segments (e.g., no `/api/review/review/pending`)
   - Firebase Hosting correctly proxies to Load Balancer

3. **Code Quality**:
   - All service files updated consistently
   - Clear commit message explaining the fix
   - Session log documents the work

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
- None expected (straightforward code fix)

---

## Escalation Triggers

Escalate to Architect if:
1. **Pattern Mismatch**: The actual code structure differs significantly from this guide
2. **Additional Services**: More services are affected than identified (Review, Graph, Notes, Orchestration)
3. **Configuration Issues**: Firebase Hosting or Load Balancer routing needs adjustment
4. **Testing Failures**: Fix doesn't resolve the 403 Forbidden errors
5. **Deployment Issues**: Cannot deploy to Firebase Hosting

**Escalation Process**:
1. Document the issue in `docs/artifacts/admin-frontend/escalations/sprint-1.2-blocker.md`
2. Include error messages, screenshots, and attempted solutions
3. Notify Architect via inbox message

---

## Timeline

- **Hour 0-1**: Code review and fix implementation
- **Hour 1-2**: Local testing and verification
- **Hour 2-3**: Production deployment and testing
- **Hour 3-4**: Documentation and session log

**Total Estimated Time**: 2-4 hours

---

## Notes

### Why This Happened
- Sprint 1 focused on infrastructure (Load Balancer) and backend (authentication)
- Frontend API client was updated to use Load Balancer URL but endpoint paths weren't reviewed
- The duplicate prefix pattern wasn't caught during initial testing
- This is a common mistake when refactoring API base URLs

### Prevention for Future
- Add API path construction tests
- Document the base URL + endpoint pattern in code comments
- Include API path verification in deployment checklist
- Test all API endpoints after infrastructure changes

### Related Work
- Sprint 1: Load Balancer setup (completed)
- Sprint 1.1: IAP removal (completed)
- Sprint 1.2: Custom domain configuration (completed)
- Sprint 1.2: API path fix (this sprint)

---

## References

- **Load Balancer URL Map**: Configured in Sprint 1 (Infrastructure)
- **Firebase Hosting Config**: `web/firebase.json` (rewrites `/api/**`)
- **Service Files**: `web/src/services/` directory
- **Conversation History**: Documents the bug discovery and root cause analysis

---

**Created**: 2025-01-13  
**Author**: Architect  
**Status**: Ready for Execution