# Worker Thread Briefing: CORS Fix for Review and Graph Pages

**Mode**: Complex  
**Priority**: CRITICAL  
**Timeline**: 2-4 hours  
**Issue**: #26  
**Status**: Ready to Execute

---

## Context

User testing revealed that Review Queue and Knowledge Graph pages are completely broken, showing "Error: Failed to fetch" immediately after loading. The root cause has been identified: **missing CORS headers in Cloud Functions**.

---

## Problem Summary

### What's Broken
- ❌ Review page shows "Failed to fetch"
- ❌ Graph page shows "Failed to fetch"
- ❌ Cannot see pending review items
- ❌ Cannot approve/reject entities
- ❌ Cannot browse knowledge graph

### What's Working
- ✅ Authentication (user signed in with Google)
- ✅ Notes creation (notes appear in Notes page)
- ✅ Functions are deployed and accessible

### Root Cause
Browser blocks all API requests due to missing CORS headers. Console shows:
```
Access to fetch at 'https://review-api-h55nns6ojq-uc.a.run.app/review/pending' 
from origin 'https://aletheia-codex-prod.web.app' has been blocked by CORS policy: 
Response to preflight request doesn't pass access control check: 
No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

---

## Your Task

Fix CORS errors by:
1. Adding CORS headers to all Cloud Function responses
2. Handling OPTIONS requests (CORS preflight)
3. Fixing API URLs in frontend
4. Deploying and testing

**Timeline**: 2-4 hours

---

## Implementation Steps

### Step 1: Fix Review API Function (30 minutes)

**File**: `functions/review_api/main.py`

Add CORS helper function at the top:

```python
# CORS configuration
ALLOWED_ORIGINS = [
    'https://aletheia-codex-prod.web.app',
    'http://localhost:3000'
]

def add_cors_headers(response, origin):
    """Add CORS headers to response."""
    if origin in ALLOWED_ORIGINS:
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        response.headers['Access-Control-Max-Age'] = '3600'
    return response
```

Update main handler to handle OPTIONS and add CORS to all responses:

```python
@functions_framework.http
def handle_request(request: Request) -> flask.Response:
    origin = request.headers.get('Origin')
    
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        return add_cors_headers(response, origin)
    
    # Process request
    try:
        response = handle_request_internal(request)
        return add_cors_headers(response, origin)
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        response = jsonify({'error': 'Internal server error'}), 500
        return add_cors_headers(response, origin)
```

**Important**: Wrap ALL response returns with `add_cors_headers(response, origin)`.

### Step 2: Fix Graph Function (30 minutes)

**File**: `functions/graph/main.py`

Apply the same CORS pattern. See `docs/CORS_FIX_IMPLEMENTATION_GUIDE.md` for complete code.

### Step 3: Fix Notes API Function (30 minutes)

**File**: `functions/notes_api/main.py`

Apply the same CORS pattern.

### Step 4: Fix Auth Decorator (15 minutes)

**File**: `functions/shared/auth/firebase_auth.py`

Update `@require_auth` decorator to allow OPTIONS requests:

```python
def require_auth(f):
    @wraps(f)
    def decorated_function(request):
        # Allow OPTIONS requests (CORS preflight) without authentication
        if request.method == 'OPTIONS':
            return f(request)
        
        # Get Authorization header
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            logger.warning("Missing Authorization header")
            return jsonify({'error': 'Missing Authorization header'}), 401
        
        # ... rest of authentication logic (keep existing code)
```

### Step 5: Fix Frontend API URLs (15 minutes)

**File**: `web/src/services/api.ts`

Change:
```typescript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://us-central1-aletheia-codex-prod.cloudfunctions.net/review-api';
```

To:
```typescript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://us-central1-aletheia-codex-prod.cloudfunctions.net/review-api-function';
```

**Key**: Add `-function` suffix.

**File**: `web/src/services/graphService.ts`

Update to use correct URL:
```typescript
const GRAPH_API_URL = process.env.REACT_APP_GRAPH_API_URL || 'https://us-central1-aletheia-codex-prod.cloudfunctions.net/graph-function';
```

### Step 6: Deploy Backend (30 minutes)

```bash
# Deploy Review API
cd functions/review_api
gcloud functions deploy review-api-function \
  --gen2 \
  --runtime=python311 \
  --region=us-central1 \
  --source=. \
  --entry-point=handle_request \
  --trigger-http \
  --service-account=review-api-sa@aletheia-codex-prod.iam.gserviceaccount.com \
  --set-env-vars GCP_PROJECT=aletheia-codex-prod \
  --memory=512MB \
  --timeout=60s

gcloud functions add-invoker-policy-binding review-api-function \
  --region=us-central1 \
  --member=allUsers

# Deploy Graph Function
cd ../graph
gcloud functions deploy graph-function \
  --gen2 \
  --runtime=python311 \
  --region=us-central1 \
  --source=. \
  --entry-point=graph_function \
  --trigger-http \
  --service-account=graph-sa@aletheia-codex-prod.iam.gserviceaccount.com \
  --set-env-vars GCP_PROJECT=aletheia-codex-prod \
  --memory=512MB \
  --timeout=60s

gcloud functions add-invoker-policy-binding graph-function \
  --region=us-central1 \
  --member=allUsers

# Deploy Notes API
cd ../notes_api
gcloud functions deploy notes-api-function \
  --gen2 \
  --runtime=python311 \
  --region=us-central1 \
  --source=. \
  --entry-point=handle_request \
  --trigger-http \
  --service-account=notes-api-sa@aletheia-codex-prod.iam.gserviceaccount.com \
  --set-env-vars GCP_PROJECT=aletheia-codex-prod \
  --memory=512MB \
  --timeout=60s

gcloud functions add-invoker-policy-binding notes-api-function \
  --region=us-central1 \
  --member=allUsers
```

### Step 7: Deploy Frontend (15 minutes)

```bash
cd web
npm run build
firebase deploy --only hosting
```

---

## Testing Procedures

### Test 1: CORS Preflight

```bash
curl -X OPTIONS \
  -H "Origin: https://aletheia-codex-prod.web.app" \
  -H "Access-Control-Request-Method: GET" \
  -H "Access-Control-Request-Headers: Content-Type, Authorization" \
  -v \
  https://us-central1-aletheia-codex-prod.cloudfunctions.net/review-api-function/review/pending

# Expected: 200 OK with CORS headers
```

### Test 2: Browser Testing

1. Clear browser cache (Ctrl+Shift+Delete)
2. Open DevTools (F12) → Console tab
3. Navigate to Review page
4. Verify: No CORS errors in console
5. Verify: Can see review items
6. Navigate to Graph page
7. Verify: Can see graph nodes
8. Check Network tab: All requests return 200 OK

---

## Success Criteria

Fix is complete when ALL of these are true:

- [ ] Review page loads without "Failed to fetch" error
- [ ] Graph page loads without "Failed to fetch" error
- [ ] Can see pending review items
- [ ] Can approve/reject items
- [ ] Can browse knowledge graph nodes
- [ ] No CORS errors in browser console
- [ ] Network tab shows 200 OK responses
- [ ] OPTIONS requests return 200 OK with CORS headers
- [ ] All API calls include Authorization header
- [ ] Functions deployed successfully

---

## Important Notes

### CORS Basics
- CORS is a browser security feature
- Browser sends OPTIONS request first (preflight)
- Server must return proper headers
- OPTIONS requests must return 200 OK WITHOUT authentication
- Actual API calls still require authentication

### Common Mistakes to Avoid
- ❌ Don't forget to wrap ALL responses with `add_cors_headers()`
- ❌ Don't block OPTIONS requests with auth decorator
- ❌ Don't forget to add `Authorization` to allowed headers
- ❌ Don't use wrong API URLs in frontend
- ❌ Don't forget to rebuild frontend after changes

### Key Points
- OPTIONS requests bypass authentication (for CORS preflight)
- All other requests still require Firebase auth token
- CORS headers must be on EVERY response
- Origin must be in ALLOWED_ORIGINS list

---

## Documentation Reference

Complete implementation details in:
- `docs/CORS_FIX_IMPLEMENTATION_GUIDE.md` - Full implementation guide
- `ISSUE_CORS_FIX.md` - Issue description
- GitHub Issue #26 - Tracking issue

---

## Troubleshooting

### Still getting CORS errors?
- Clear browser cache (Ctrl+Shift+R)
- Check console for exact error
- Verify CORS headers in Network tab

### OPTIONS returns 401?
- Auth decorator is blocking OPTIONS
- Update decorator to allow OPTIONS

### Wrong URL being used?
- Update environment variables
- Rebuild frontend
- Redeploy hosting

---

## Timeline

- **Backend Updates**: 1.5 hours
- **Frontend Updates**: 30 minutes
- **Deployment**: 45 minutes
- **Testing**: 30 minutes
- **Total**: 2-4 hours

---

## Deliverables

1. **Updated Functions**: All 3 functions with CORS headers
2. **Updated Frontend**: Correct API URLs
3. **Deployed Code**: All changes live in production
4. **Test Results**: All pages working without errors
5. **Completion Report**: Document what was fixed and tested

---

## After Completion

1. Test all pages in production
2. Verify no CORS errors in console
3. Create completion report
4. Close GitHub Issue #26
5. Update user that pages are working

---

**Status**: Ready to Execute  
**Priority**: CRITICAL  
**Issue**: #26  
**Timeline**: 2-4 hours

---

**END OF BRIEFING**