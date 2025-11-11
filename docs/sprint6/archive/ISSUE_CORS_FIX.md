# CRITICAL: CORS Errors Blocking Review and Graph Pages

## Issue Summary

**Severity**: CRITICAL - Blocks core functionality  
**Affected Pages**: Review Queue, Knowledge Graph  
**Root Cause**: Missing CORS headers in Cloud Functions  
**Status**: Identified, ready for fix

---

## Problem Description

Users cannot access the Review Queue or Knowledge Graph pages. Both pages show "Error: Failed to fetch" immediately after loading. The application is deployed and authentication is working, but API calls are being blocked by the browser due to CORS policy violations.

---

## Root Cause Analysis

### 1. CORS Headers Missing
Cloud Functions are not returning proper CORS headers in responses, causing browsers to block requests from `https://aletheia-codex-prod.web.app`.

**Error Message**:
```
Access to fetch at 'https://review-api-h55nns6ojq-uc.a.run.app/review/pending' 
from origin 'https://aletheia-codex-prod.web.app' has been blocked by CORS policy: 
Response to preflight request doesn't pass access control check: 
No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

### 2. Wrong API URL
Frontend is using Cloud Run URL (`review-api-h55nns6ojq-uc.a.run.app`) instead of Cloud Functions URL (`us-central1-aletheia-codex-prod.cloudfunctions.net/review-api-function`).

### 3. OPTIONS Preflight Failing
Browser sends OPTIONS requests before actual API calls (CORS preflight), but functions don't handle OPTIONS requests properly.

---

## Evidence

### Console Errors
- **Review Page**: CORS error on `/review/pending` and `/review/stats`
- **Graph Page**: CORS error on `/graph-function?limit=50&offset=0`
- **Dashboard**: Firestore permissions error (separate issue)

### Network Tab
- All API requests show "Failed to load response data"
- No response bodies returned
- Requests blocked before reaching server

### User Impact
- ✅ Authentication working (user signed in)
- ✅ Notes creation working (notes appear in Notes page)
- ❌ Review Queue not accessible ("Failed to fetch")
- ❌ Knowledge Graph not accessible ("Failed to fetch")
- ❌ Cannot approve/reject entities
- ❌ Cannot browse knowledge graph

---

## Technical Details

### Affected Functions
1. **review-api-function**: `https://us-central1-aletheia-codex-prod.cloudfunctions.net/review-api-function`
2. **graph-function**: `https://us-central1-aletheia-codex-prod.cloudfunctions.net/graph-function`

### Required CORS Headers
```
Access-Control-Allow-Origin: https://aletheia-codex-prod.web.app
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization
Access-Control-Max-Age: 3600
```

### Frontend Origin
```
https://aletheia-codex-prod.web.app
```

---

## Solution Required

### 1. Fix CORS Headers in Cloud Functions
Add proper CORS headers to all HTTP responses in:
- `functions/review_api/main.py`
- `functions/graph/main.py`
- `functions/notes_api/main.py` (if affected)

### 2. Handle OPTIONS Requests
Add OPTIONS request handlers for CORS preflight:
```python
if request.method == 'OPTIONS':
    response = jsonify({'status': 'ok'})
    response.headers['Access-Control-Allow-Origin'] = 'https://aletheia-codex-prod.web.app'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['Access-Control-Max-Age'] = '3600'
    return response
```

### 3. Fix API URLs in Frontend
Update `web/src/services/api.ts` to use correct Cloud Functions URLs:
```typescript
const API_BASE_URL = 'https://us-central1-aletheia-codex-prod.cloudfunctions.net/review-api-function';
```

### 4. Add CORS to All Responses
Ensure every response includes CORS headers:
```python
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = 'https://aletheia-codex-prod.web.app'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response
```

---

## Testing Checklist

After fix is deployed:
- [ ] Review page loads without errors
- [ ] Graph page loads without errors
- [ ] Can see pending review items
- [ ] Can approve/reject items
- [ ] Can browse knowledge graph nodes
- [ ] No CORS errors in console
- [ ] Network tab shows 200 OK responses

---

## Priority

**CRITICAL** - This blocks core functionality of the application. Users cannot:
- Review AI-extracted entities
- Approve/reject items
- Browse their knowledge graph
- Use the main features of the application

---

## Related Files

### Backend
- `functions/review_api/main.py`
- `functions/graph/main.py`
- `functions/notes_api/main.py`

### Frontend
- `web/src/services/api.ts`
- `web/src/services/graphService.ts`
- `web/src/pages/ReviewPage.tsx`
- `web/src/pages/GraphPage.tsx`

---

## Additional Notes

- Authentication is working correctly (user signed in with Google)
- Notes creation is working (notes appear in Notes page)
- The issue is purely CORS-related, not authentication or authorization
- Functions are deployed and accessible, but browser blocks requests due to missing CORS headers

---

**Reported by**: User testing  
**Date**: November 10, 2025  
**Environment**: Production (`https://aletheia-codex-prod.web.app`)  
**Browser**: Chrome (CORS errors visible in console)

---

## Next Steps

1. Create worker thread to fix CORS issues
2. Update Cloud Functions with proper CORS headers
3. Fix API URLs in frontend
4. Deploy and test
5. Verify all pages working