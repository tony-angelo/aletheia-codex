# CORS Fix Implementation Guide

**Issue**: #26  
**Priority**: CRITICAL  
**Timeline**: 2-4 hours  
**Status**: Ready for Implementation

---

## Problem Summary

Review Queue and Knowledge Graph pages show "Failed to fetch" errors due to missing CORS headers in Cloud Functions. Browser blocks all API requests from `https://aletheia-codex-prod.web.app` because functions don't return proper CORS headers.

---

## Root Causes

1. **Missing CORS Headers**: Functions don't include `Access-Control-Allow-Origin` header
2. **No OPTIONS Handler**: Functions don't handle CORS preflight (OPTIONS) requests
3. **Wrong API URL**: Frontend uses Cloud Run URL instead of Cloud Functions URL

---

## Solution Overview

### Backend Changes (3 functions)
1. Add CORS headers to all responses
2. Handle OPTIONS requests for CORS preflight
3. Ensure headers include `Authorization` in allowed headers

### Frontend Changes (1 file)
1. Fix API base URL to use Cloud Functions URL

---

## Implementation Steps

### Step 1: Fix Review API Function (30 minutes)

**File**: `functions/review_api/main.py`

#### A. Add CORS Helper Function
Add this at the top of the file (after imports):

```python
# CORS configuration
ALLOWED_ORIGINS = [
    'https://aletheia-codex-prod.web.app',
    'http://localhost:3000'  # For local development
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

#### B. Update Main Handler
Find the main function handler and update it:

```python
@functions_framework.http
def handle_request(request: Request) -> flask.Response:
    """Main entry point for review API."""
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
        logger.error(f"Error handling request: {str(e)}", exc_info=True)
        response = jsonify({'error': 'Internal server error'}), 500
        return add_cors_headers(response, origin)
```

#### C. Update All Response Returns
Find all places where responses are returned and wrap them:

```python
# Before:
return jsonify({'data': result})

# After:
response = jsonify({'data': result})
return add_cors_headers(response, origin)
```

**Important**: Make sure `origin` variable is available in scope (pass it as parameter if needed).

### Step 2: Fix Graph Function (30 minutes)

**File**: `functions/graph/main.py`

Apply the same pattern as Review API:

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

@functions_framework.http
@require_auth
def graph_function(request: Request):
    """Main entry point for Graph API."""
    origin = request.headers.get('Origin')
    
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        return add_cors_headers(response, origin)
    
    try:
        user_id = request.user_id
        
        # Route based on path
        path = request.path
        
        if path == '/nodes' or path == '/':
            response = get_nodes(user_id, request)
        elif path.startswith('/nodes/'):
            node_id = path.split('/')[-1]
            response = get_node_details(user_id, node_id)
        elif path == '/search':
            query = request.args.get('q', '')
            response = search_nodes(user_id, query)
        else:
            response = jsonify({'error': 'Not found'}), 404
        
        return add_cors_headers(response, origin)
        
    except Exception as e:
        logger.error(f"Error in graph function: {str(e)}", exc_info=True)
        response = jsonify({'error': 'Internal server error'}), 500
        return add_cors_headers(response, origin)
```

**Note**: The `@require_auth` decorator should be BEFORE the CORS handling, but OPTIONS requests should bypass auth. Update the decorator if needed.

### Step 3: Fix Notes API Function (30 minutes)

**File**: `functions/notes_api/main.py`

Apply the same CORS pattern as above.

### Step 4: Fix Frontend API URL (15 minutes)

**File**: `web/src/services/api.ts`

#### Current Code:
```typescript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://us-central1-aletheia-codex-prod.cloudfunctions.net/review-api';
```

#### Updated Code:
```typescript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://us-central1-aletheia-codex-prod.cloudfunctions.net/review-api-function';
```

**Key Change**: Add `-function` suffix to match actual Cloud Function name.

### Step 5: Update Environment Variables (15 minutes)

**File**: `web/.env.production`

Add or update:
```bash
REACT_APP_API_URL=https://us-central1-aletheia-codex-prod.cloudfunctions.net/review-api-function
REACT_APP_GRAPH_API_URL=https://us-central1-aletheia-codex-prod.cloudfunctions.net/graph-function
```

**File**: `web/src/services/graphService.ts`

Update to use environment variable:
```typescript
const GRAPH_API_URL = process.env.REACT_APP_GRAPH_API_URL || 'https://us-central1-aletheia-codex-prod.cloudfunctions.net/graph-function';
```

### Step 6: Handle Auth Decorator with OPTIONS (Important!)

The `@require_auth` decorator will block OPTIONS requests. We need to handle OPTIONS BEFORE authentication.

**Option A**: Update decorator to allow OPTIONS:

**File**: `functions/shared/auth/firebase_auth.py`

```python
def require_auth(f):
    """
    Decorator to require Firebase authentication for Cloud Functions.
    Allows OPTIONS requests to pass through for CORS preflight.
    """
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
        
        # ... rest of authentication logic
```

**Option B**: Handle OPTIONS before decorator:

In each function, check for OPTIONS before applying decorator logic:

```python
@functions_framework.http
def my_function(request: Request):
    origin = request.headers.get('Origin')
    
    # Handle OPTIONS first (before auth)
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        return add_cors_headers(response, origin)
    
    # Now apply auth
    return authenticated_handler(request, origin)

@require_auth
def authenticated_handler(request, origin):
    # Actual function logic
    pass
```

**Recommendation**: Use Option A (update decorator) - cleaner and applies to all functions.

---

## Deployment Steps

### Step 1: Deploy Backend Functions (30 minutes)

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

# Grant invoker permission
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

# Deploy Notes API (if updated)
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

### Step 2: Deploy Frontend (15 minutes)

```bash
cd web
npm run build
firebase deploy --only hosting
```

---

## Testing Procedures

### Test 1: CORS Preflight (OPTIONS)

```bash
# Test Review API OPTIONS
curl -X OPTIONS \
  -H "Origin: https://aletheia-codex-prod.web.app" \
  -H "Access-Control-Request-Method: GET" \
  -H "Access-Control-Request-Headers: Content-Type, Authorization" \
  -v \
  https://us-central1-aletheia-codex-prod.cloudfunctions.net/review-api-function/review/pending

# Expected Response Headers:
# Access-Control-Allow-Origin: https://aletheia-codex-prod.web.app
# Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
# Access-Control-Allow-Headers: Content-Type, Authorization
# Access-Control-Max-Age: 3600
# Status: 200 OK

# Test Graph API OPTIONS
curl -X OPTIONS \
  -H "Origin: https://aletheia-codex-prod.web.app" \
  -H "Access-Control-Request-Method: GET" \
  -H "Access-Control-Request-Headers: Content-Type, Authorization" \
  -v \
  https://us-central1-aletheia-codex-prod.cloudfunctions.net/graph-function
```

### Test 2: Actual API Calls

```bash
# Get Firebase token from browser console:
# await firebase.auth().currentUser.getIdToken()

# Test Review API with auth
curl -X GET \
  -H "Origin: https://aletheia-codex-prod.web.app" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -v \
  https://us-central1-aletheia-codex-prod.cloudfunctions.net/review-api-function/review/pending

# Expected: 200 OK with CORS headers and data

# Test Graph API with auth
curl -X GET \
  -H "Origin: https://aletheia-codex-prod.web.app" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -v \
  https://us-central1-aletheia-codex-prod.cloudfunctions.net/graph-function?limit=10&offset=0

# Expected: 200 OK with CORS headers and data
```

### Test 3: Browser Testing

1. **Clear Browser Cache**: Ctrl+Shift+Delete → Clear cached images and files
2. **Open DevTools**: F12 → Console tab
3. **Navigate to Review Page**: Should load without errors
4. **Check Console**: No CORS errors
5. **Check Network Tab**: 
   - OPTIONS requests return 200 OK
   - GET requests return 200 OK
   - All responses have CORS headers
6. **Navigate to Graph Page**: Should load without errors
7. **Test Functionality**:
   - Can see review items
   - Can approve/reject items
   - Can browse graph nodes
   - Can search nodes

---

## Success Criteria

All of these must be true:

- [ ] Review API returns CORS headers on all responses
- [ ] Graph API returns CORS headers on all responses
- [ ] OPTIONS requests return 200 OK with CORS headers
- [ ] Review page loads without "Failed to fetch" error
- [ ] Graph page loads without "Failed to fetch" error
- [ ] Can see pending review items
- [ ] Can approve/reject items
- [ ] Can browse knowledge graph nodes
- [ ] No CORS errors in browser console
- [ ] Network tab shows 200 OK responses
- [ ] All API calls include proper headers

---

## Troubleshooting

### Issue: Still getting CORS errors after deployment

**Cause**: Browser cached old responses  
**Solution**: Hard refresh (Ctrl+Shift+R) or clear cache

### Issue: OPTIONS returns 401 Unauthorized

**Cause**: Auth decorator blocking OPTIONS  
**Solution**: Update `@require_auth` decorator to allow OPTIONS (see Step 6)

### Issue: Wrong API URL still being used

**Cause**: Environment variable not updated  
**Solution**: 
1. Update `.env.production`
2. Rebuild frontend: `npm run build`
3. Redeploy: `firebase deploy --only hosting`

### Issue: CORS headers not appearing

**Cause**: `add_cors_headers()` not being called  
**Solution**: Verify all response returns are wrapped with `add_cors_headers(response, origin)`

### Issue: "Origin not allowed"

**Cause**: Origin not in `ALLOWED_ORIGINS` list  
**Solution**: Add origin to list in function code

---

## Code Checklist

Before deploying, verify:

- [ ] `add_cors_headers()` function added to all 3 functions
- [ ] `ALLOWED_ORIGINS` includes production URL
- [ ] OPTIONS handler added before auth check
- [ ] All responses wrapped with `add_cors_headers()`
- [ ] `@require_auth` decorator allows OPTIONS
- [ ] Frontend API URLs updated
- [ ] Environment variables updated
- [ ] All functions include `Authorization` in allowed headers

---

## Timeline

- **Backend Updates**: 1.5 hours (3 functions × 30 min)
- **Frontend Updates**: 30 minutes
- **Deployment**: 45 minutes
- **Testing**: 30 minutes
- **Total**: 2-4 hours

---

## Related Files

### Backend
- `functions/review_api/main.py`
- `functions/graph/main.py`
- `functions/notes_api/main.py`
- `functions/shared/auth/firebase_auth.py`

### Frontend
- `web/src/services/api.ts`
- `web/src/services/graphService.ts`
- `web/.env.production`

---

## Additional Notes

- CORS is a browser security feature - it's working as intended
- The fix is straightforward: add proper headers to responses
- OPTIONS requests must return 200 OK without authentication
- All actual API calls still require authentication
- This doesn't weaken security - it just allows the browser to make requests

---

**Status**: Ready for Implementation  
**Priority**: CRITICAL  
**Issue**: #26

---

**END OF IMPLEMENTATION GUIDE**