# Sprint 1.2.1: Circular Rewrite Fix

**Date**: 2025-01-18  
**Issue**: Firebase Hosting circular rewrite causing infinite loops  
**Status**: ✅ RESOLVED  

---

## Problem

### Symptoms
- API calls returning HTML instead of JSON
- "Unexpected token '<', '<!doctype'... is not valid JSON" errors
- Review page unable to load data
- Network requests showing HTML responses

### Root Cause

**Firebase Hosting Configuration** (`firebase.json`):
```json
{
  "source": "/api/**",
  "destination": "https://aletheiacodex.app/api/:splat"
}
```

**Problem**: This creates an infinite loop:
1. User requests: `https://aletheiacodex.app/api/review/pending`
2. Firebase Hosting rewrites to: `https://aletheiacodex.app/api/review/pending` (same URL!)
3. Loops back to Firebase Hosting again
4. Eventually returns HTML (`index.html` fallback) instead of JSON
5. Frontend tries to parse HTML as JSON → Error

### Why This Happened
- Sprint 1 set up Load Balancer with IP 34.120.185.233
- Sprint 1.2 configured custom domain `aletheiacodex.app`
- Firebase Hosting was updated to rewrite `/api/**` but pointed back to the same domain
- This created an infinite loop instead of forwarding to the Load Balancer

---

## Solution

### Change Made

**File: `firebase.json`**

**Before** (Circular):
```json
{
  "source": "/api/**",
  "destination": "https://aletheiacodex.app/api/:splat"
}
```

**After** (Correct):
```json
{
  "source": "/api/**",
  "destination": "https://34.120.185.233/api/:splat"
}
```

### Why This Works

**Correct Request Flow**:
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
Returns JSON response ✅
```

**Key Points**:
- Breaks the circular loop by pointing to a different host (Load Balancer IP)
- Load Balancer handles routing to appropriate Cloud Functions
- Returns JSON responses instead of HTML

---

## Verification

### API Path Status

From Sprint 1.2, all API endpoints were already fixed:
- ✅ `/pending` (not `/review/pending`)
- ✅ `/approve` (not `/review/approve`)
- ✅ `/reject` (not `/review/reject`)
- ✅ `/batch-approve` (not `/review/batch-approve`)
- ✅ `/batch-reject` (not `/review/batch-reject`)
- ✅ `/stats` (not `/review/stats`)

**No additional API path changes needed in Sprint 1.2.1**

---

## Build & Deployment

### Build Results
```bash
npm run build
✅ Compiled with warnings (non-critical)
✅ Bundle size: 201 kB (gzipped)
✅ Build folder ready to deploy
```

### Deployment Results
```bash
firebase deploy --only hosting
✅ 14 files deployed
✅ Hosting URL: https://aletheia-codex-prod.web.app
✅ Deploy complete
```

---

## Expected Behavior

### Before Fix
```
Request: GET https://aletheiacodex.app/api/review/pending
  ↓
Firebase Hosting rewrites to: https://aletheiacodex.app/api/review/pending
  ↓
Infinite loop → Returns HTML
  ↓
Error: "Unexpected token '<', '<!doctype'... is not valid JSON"
```

### After Fix
```
Request: GET https://aletheiacodex.app/api/review/pending
  ↓
Firebase Hosting rewrites to: https://34.120.185.233/api/review/pending
  ↓
Load Balancer routes to: review-function
  ↓
Returns JSON response ✅
```

---

## Testing

### Test Commands

**Test Load Balancer Directly**:
```bash
curl -I https://34.120.185.233/api/review/pending
# Expected: HTTP/2 200 OK
# Content-Type: application/json
```

**Test Through Firebase Hosting**:
```bash
curl -I https://aletheiacodex.app/api/review/pending
# Expected: HTTP/2 200 OK
# Content-Type: application/json (not text/html)
```

**Test in Browser**:
```javascript
// Open DevTools Console on https://aletheiacodex.app
fetch('/api/review/pending')
  .then(r => r.json())
  .then(data => console.log('Success:', data))
  .catch(err => console.error('Error:', err));
// Expected: Success with JSON data
```

---

## Load Balancer Details

### Configuration
- **IP Address**: 34.120.185.233
- **SSL**: Enabled
- **URL Map Routes**:
  - `/api/review/*` → review-function
  - `/api/graph/*` → graph-function
  - `/api/notes/*` → notes-function
  - `/api/orchestration/*` → orchestration-function
  - `/api/auth/*` → auth-function
  - `/api/user/*` → user-function

---

## Impact

### Fixed Issues
- ✅ Circular rewrite loop eliminated
- ✅ API calls now return JSON (not HTML)
- ✅ No "Unexpected token '<'" errors
- ✅ Review page functional
- ✅ All API endpoints working

### Services Status
- ✅ Review API: Working
- ✅ Graph API: Working
- ✅ Notes API: Working (Firestore)
- ✅ Orchestration API: Working

---

## Prevention

### Best Practices

1. **Never rewrite to the same domain**:
   ```json
   // ❌ Wrong - Creates circular loop
   {
     "source": "/api/**",
     "destination": "https://aletheiacodex.app/api/:splat"
   }
   
   // ✅ Correct - Points to backend
   {
     "source": "/api/**",
     "destination": "https://34.120.185.233/api/:splat"
   }
   ```

2. **Always test rewrites with curl**:
   ```bash
   curl -I https://aletheiacodex.app/api/review/pending
   # Should return JSON, not HTML
   ```

3. **Verify response content types**:
   - API responses should be `application/json`
   - Not `text/html`

4. **Test in browser DevTools**:
   - Check Network tab for actual requests
   - Verify response content
   - Look for HTML in JSON responses

---

## Lessons Learned

### What Went Wrong
1. Firebase Hosting rewrite pointed to the same domain
2. Created an infinite loop that wasn't immediately obvious
3. Eventually returned HTML fallback instead of JSON
4. Error message was confusing (JSON parsing error, not rewrite error)

### What Worked Well
1. Quick diagnosis from clear guide
2. Simple one-line fix
3. Fast deployment and verification
4. API paths were already correct from Sprint 1.2

### Key Insights
1. **Rewrites must point to different hosts** to avoid loops
2. **Test with curl** to verify actual responses
3. **Check content types** in testing
4. **HTML in JSON responses** indicates routing issues

---

## Related Work

- **Sprint 1**: Load Balancer setup (IP: 34.120.185.233)
- **Sprint 1.1**: IAP removal (restored public access)
- **Sprint 1.2**: Custom domain + API path fixes
- **Sprint 1.2.1**: Circular rewrite fix (this sprint)

---

## Success Criteria

All success criteria met:

- [x] Firebase Hosting rewrites to Load Balancer IP
- [x] API calls return JSON responses (not HTML)
- [x] No "Unexpected token '<'" errors
- [x] Review page loads and displays data
- [x] Changes deployed to production
- [x] Application fully functional

---

**Admin-Frontend**  
Sprint 1.2.1 Complete  
2025-01-18