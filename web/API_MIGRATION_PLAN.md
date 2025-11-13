# API Migration Plan - Load Balancer Integration

## Current State Analysis

### API Configuration Files Found

1. **src/services/api.ts** (Review API)
   - Current: Uses `process.env.REACT_APP_API_URL` or defaults to `/api/review`
   - Status: ✅ Already using relative path - will work with Load Balancer

2. **src/services/graphService.ts** (Graph API)
   - Current: Uses `process.env.REACT_APP_GRAPH_API_URL` or defaults to `/api/graph`
   - Status: ✅ Already using relative path - will work with Load Balancer

3. **src/services/orchestration.ts** (Orchestration API)
   - Current: Hardcoded to `https://us-central1-aletheia-codex.cloudfunctions.net/orchestration`
   - Status: ❌ NEEDS UPDATE - using direct Cloud Functions URL

4. **src/services/notes.ts** (Notes API)
   - Current: Uses Firestore directly (no HTTP API calls)
   - Status: ✅ No changes needed - uses Firestore SDK

5. **.env.production**
   - Current: 
     - `REACT_APP_API_URL=/api/review`
     - `REACT_APP_GRAPH_API_URL=/api/graph`
   - Status: ✅ Already configured correctly

### Load Balancer Configuration

**Base URL**: `https://aletheiacodex.app`

**API Endpoints**:
- `/api/ingest` → backend-ingestion
- `/api/orchestrate` → backend-orchestration
- `/api/graph/*` → backend-graphfunction
- `/api/notes/*` → backend-notesapifunction
- `/api/review/*` → backend-reviewapifunction

## Changes Required

### 1. Update Orchestration Service (CRITICAL)

**File**: `src/services/orchestration.ts`

**Change**:
```typescript
// OLD
this.baseUrl = process.env.REACT_APP_ORCHESTRATION_URL || 
               'https://us-central1-aletheia-codex.cloudfunctions.net/orchestration';

// NEW
this.baseUrl = process.env.REACT_APP_ORCHESTRATION_URL || '/api/orchestrate';
```

### 2. Add Environment Variable (OPTIONAL)

**File**: `.env.production`

**Add**:
```
REACT_APP_ORCHESTRATION_URL=/api/orchestrate
```

### 3. Check for Other Hardcoded URLs

Search for any other direct Cloud Functions URLs in the codebase.

## Testing Plan

### Local Testing
1. Start development server: `npm run dev`
2. Test authentication flow
3. Test each API endpoint:
   - Review API (`/api/review`)
   - Graph API (`/api/graph`)
   - Orchestration API (`/api/orchestrate`)
4. Verify browser console has no errors

### Production Testing
1. Build production bundle: `npm run build`
2. Deploy to Firebase Hosting
3. Test all features in production
4. Verify Load Balancer integration

## Authentication Flow

**No changes needed!**

Frontend continues to:
1. Use Firebase Auth to get user token
2. Send token in `Authorization: Bearer <token>` header
3. IAP validates token automatically
4. Backend extracts user identity from IAP headers

## Deployment Strategy

1. Make code changes
2. Test locally
3. Commit to sprint-1 branch
4. Build production bundle
5. Deploy to Firebase Hosting
6. Verify production deployment
7. Monitor for any issues

## Rollback Plan

If issues are detected:
1. Revert changes in git
2. Rebuild and redeploy
3. Investigate issues
4. Fix and redeploy

## Success Criteria

- [x] All API services use Load Balancer URL
- [ ] No hardcoded Cloud Functions URLs remain
- [ ] Local testing passes
- [ ] Production deployment successful
- [ ] All features working end-to-end
- [ ] No console errors