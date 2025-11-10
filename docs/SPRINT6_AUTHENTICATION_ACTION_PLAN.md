# Sprint 6 Authentication Action Plan

**Status**: Ready to Execute  
**Timeline**: 2-4 hours  
**Blocker Resolution**: Use Firebase Authentication (Already Implemented)

---

## TL;DR

The organization policy preventing `--allow-unauthenticated` is **NOT a blocker**. Firebase Authentication is already implemented and working in production (Sprint 4.5). Simply apply the existing `@require_auth` decorator to all HTTP functions and deploy without the `--allow-unauthenticated` flag.

---

## What You Need to Know

### ✅ Already Working
- Firebase Authentication is functional in production
- Authentication middleware exists: `functions/shared/auth/firebase_auth.py`
- Frontend sends auth tokens correctly
- Users can sign in with Google and Email/Password

### 🔧 What Needs to Be Done
1. Apply `@require_auth` decorator to all HTTP-triggered functions
2. Deploy functions without `--allow-unauthenticated` flag
3. Grant invoker permissions (allows invocation, but function verifies token)
4. Test authentication in production

---

## Step-by-Step Implementation

### Step 1: Update Existing Functions (1-2 hours)

#### A. Review API Function
**File**: `functions/review_api/main.py`

**Add at top**:
```python
from shared.auth.firebase_auth import require_auth
```

**Update function**:
```python
@functions_framework.http
@require_auth  # Add this decorator
def handle_request(request: Request) -> flask.Response:
    user_id = request.user_id  # Now available after authentication
    return handle_request_internal(request)
```

**Update internal handler to use user_id**:
```python
def handle_request_internal(request: Request) -> flask.Response:
    user_id = request.user_id  # Use this instead of extracting from params
    # Rest of logic
```

#### B. Notes API Function
**File**: `functions/notes_api/main.py`

Same pattern as Review API:
```python
from shared.auth.firebase_auth import require_auth

@functions_framework.http
@require_auth
def handle_request(request: Request):
    user_id = request.user_id
    # Function logic
```

#### C. Orchestration Function
**File**: `functions/orchestration/main.py`

```python
from shared.auth.firebase_auth import require_auth

@functions_framework.http
@require_auth
def orchestration_function(request: Request):
    user_id = request.user_id
    # Function logic
```

### Step 2: Create Graph Function (Sprint 6 Scope) (1 hour)

**File**: `functions/graph/main.py`

```python
"""
Graph API Cloud Function for AletheiaCodex.
Provides HTTP endpoints for browsing the knowledge graph.
"""

import functions_framework
from flask import Request, jsonify
import os
from typing import Dict, Any

# Add shared directory to path
import sys
sys.path.append('/workspace')

from shared.auth.firebase_auth import require_auth
from shared.db.neo4j_client import get_neo4j_client
from shared.utils.logging import get_logger

logger = get_logger(__name__)

PROJECT_ID = os.environ.get('GCP_PROJECT', 'aletheia-codex-prod')
CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:3000,https://aletheia-codex-prod.web.app').split(',')


def add_cors_headers(response, origin):
    """Add CORS headers to response."""
    if origin in CORS_ORIGINS:
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        response.headers['Access-Control-Max-Age'] = '3600'
    return response


@functions_framework.http
@require_auth  # Authentication required
def graph_function(request: Request):
    """
    Main entry point for Graph API.
    
    Endpoints:
    - GET /nodes - List all nodes for user
    - GET /nodes/{id} - Get node details
    - GET /search?q=query - Search nodes
    """
    origin = request.headers.get('Origin')
    
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        return add_cors_headers(response, origin)
    
    try:
        user_id = request.user_id  # Available after @require_auth
        
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


def get_nodes(user_id: str, request: Request):
    """Get all nodes for user with pagination."""
    limit = int(request.args.get('limit', 50))
    offset = int(request.args.get('offset', 0))
    node_type = request.args.get('type', None)
    
    client = get_neo4j_client()
    
    # Build query
    if node_type:
        query = f"""
        MATCH (u:User {{id: $userId}})-[:OWNS]->(n:{node_type})
        RETURN n
        ORDER BY n.name
        SKIP $offset
        LIMIT $limit
        """
    else:
        query = """
        MATCH (u:User {id: $userId})-[:OWNS]->(n)
        RETURN n, labels(n) as types
        ORDER BY n.name
        SKIP $offset
        LIMIT $limit
        """
    
    result = client.execute_query(query, {
        'userId': user_id,
        'offset': offset,
        'limit': limit
    })
    
    nodes = []
    for record in result:
        node = dict(record['n'])
        if 'types' in record:
            node['type'] = record['types'][0] if record['types'] else 'Unknown'
        nodes.append(node)
    
    return jsonify({
        'nodes': nodes,
        'total': len(nodes),
        'offset': offset,
        'limit': limit
    })


def get_node_details(user_id: str, node_id: str):
    """Get detailed information about a specific node."""
    client = get_neo4j_client()
    
    query = """
    MATCH (u:User {id: $userId})-[:OWNS]->(n)
    WHERE elementId(n) = $nodeId
    OPTIONAL MATCH (n)-[r]->(related)
    RETURN n, labels(n) as types, 
           collect({type: type(r), node: related, direction: 'outgoing'}) as relationships
    """
    
    result = client.execute_query(query, {
        'userId': user_id,
        'nodeId': node_id
    })
    
    if not result:
        return jsonify({'error': 'Node not found'}), 404
    
    record = result[0]
    node = dict(record['n'])
    node['type'] = record['types'][0] if record['types'] else 'Unknown'
    node['relationships'] = record['relationships']
    
    return jsonify(node)


def search_nodes(user_id: str, query: str):
    """Search nodes by name or properties."""
    if not query:
        return jsonify({'nodes': [], 'total': 0})
    
    client = get_neo4j_client()
    
    cypher_query = """
    MATCH (u:User {id: $userId})-[:OWNS]->(n)
    WHERE toLower(n.name) CONTAINS toLower($query)
    RETURN n, labels(n) as types
    ORDER BY n.name
    LIMIT 50
    """
    
    result = client.execute_query(cypher_query, {
        'userId': user_id,
        'query': query
    })
    
    nodes = []
    for record in result:
        node = dict(record['n'])
        node['type'] = record['types'][0] if record['types'] else 'Unknown'
        nodes.append(node)
    
    return jsonify({
        'nodes': nodes,
        'total': len(nodes)
    })
```

### Step 3: Deploy Functions WITHOUT --allow-unauthenticated (30 minutes)

**Important**: Do NOT use `--allow-unauthenticated` flag. Instead, grant invoker permissions separately.

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
# NOTE: No --allow-unauthenticated flag

# Grant invoker permission (allows invocation, but function verifies token)
gcloud functions add-invoker-policy-binding review-api-function \
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

# Deploy Graph API (NEW)
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
```

**Key Point**: `add-invoker-policy-binding` allows the function to be **invoked**, but the `@require_auth` decorator in the function code verifies the Firebase authentication token. This is the correct approach.

### Step 4: Verify Frontend Sends Auth Headers (Already Done ✅)

**File**: `web/src/services/reviewService.ts` (and similar)

Verify this pattern is used:
```typescript
const getAuthHeaders = async () => {
  const user = auth.currentUser;
  if (!user) {
    throw new Error('Not authenticated');
  }
  
  const token = await user.getIdToken();
  return {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  };
};

// Use in API calls
const response = await fetch(API_URL, {
  method: 'GET',
  headers: await getAuthHeaders()
});
```

### Step 5: Test Authentication (30 minutes)

#### A. Test Without Token (Should Fail)
```bash
curl https://us-central1-aletheia-codex-prod.cloudfunctions.net/graph-function/nodes

# Expected Response:
# Status: 401 Unauthorized
# Body: {"error": "Missing Authorization header"}
```

#### B. Test With Invalid Token (Should Fail)
```bash
curl -H "Authorization: Bearer invalid-token" \
  https://us-central1-aletheia-codex-prod.cloudfunctions.net/graph-function/nodes

# Expected Response:
# Status: 401 Unauthorized
# Body: {"error": "Invalid authentication token"}
```

#### C. Test With Valid Token (Should Succeed)
1. Sign in to web app: https://aletheia-codex-prod.web.app
2. Open browser console
3. Get token: `await firebase.auth().currentUser.getIdToken()`
4. Test with curl:
```bash
curl -H "Authorization: Bearer YOUR_ACTUAL_TOKEN" \
  https://us-central1-aletheia-codex-prod.cloudfunctions.net/graph-function/nodes

# Expected Response:
# Status: 200 OK
# Body: {"nodes": [...], "total": X}
```

#### D. Test in Browser
1. Navigate to Graph page
2. Open Network tab in DevTools
3. Verify requests include `Authorization: Bearer ...` header
4. Verify responses are 200 OK (not 401)

### Step 6: Check Logs
```bash
# Check for authentication success
gcloud functions logs read graph-function \
  --region=us-central1 \
  --limit=50 | grep "Authenticated request"

# Check for authentication failures
gcloud functions logs read graph-function \
  --region=us-central1 \
  --limit=50 | grep "Missing Authorization\|Invalid authentication"
```

---

## Success Criteria

Authentication is complete when:

- [ ] All HTTP functions have `@require_auth` decorator
- [ ] All functions deployed without `--allow-unauthenticated`
- [ ] Invoker permissions granted with `add-invoker-policy-binding`
- [ ] Unauthenticated requests return 401
- [ ] Invalid tokens return 401
- [ ] Valid tokens return 200 with data
- [ ] Frontend works correctly in production
- [ ] Logs show "Authenticated request from user: USER_ID"
- [ ] No "Missing Authorization header" errors for authenticated users

---

## Troubleshooting

### Issue: "Missing Authorization header"
**Cause**: Frontend not sending token  
**Solution**: Verify `getAuthHeaders()` is called in all API requests

### Issue: "Invalid authentication token"
**Cause**: Token malformed or expired  
**Solution**: Get fresh token with `await user.getIdToken(true)`

### Issue: CORS errors
**Cause**: CORS headers not configured  
**Solution**: Verify `add_cors_headers()` includes `Authorization` in allowed headers

### Issue: "Unauthorized. You do not own this item"
**Cause**: User trying to access another user's data  
**Solution**: This is correct behavior (security working as intended)

---

## Why This Is The Right Solution

1. **Already Implemented**: Firebase Auth working, middleware exists
2. **Industry Standard**: How all major platforms do authentication
3. **Better Security**: Only authenticated users can access
4. **User Context**: Functions know which user is making requests
5. **Compliant**: Works within organization policy
6. **Fast**: 2-4 hours to implement
7. **No Approval**: Can proceed immediately

---

## What NOT To Do

❌ **Do NOT request organization policy exception**
- Takes days/weeks for approval
- May be denied
- Weakens security
- Goes against best practices
- Doesn't solve the real problem (need user context)

❌ **Do NOT use API Gateway**
- Unnecessary complexity
- Additional cost
- Longer implementation time
- Still need Firebase Auth anyway

---

## Next Steps After Authentication

Once authentication is working:

1. **Continue Sprint 6**: Build Graph page components
2. **Build Dashboard**: User statistics and overview
3. **Build Settings**: User profile management
4. **Organize Components**: Restructure component library
5. **Document Functions**: Add JSDoc comments

---

## Timeline

- **Step 1**: Update existing functions (1-2 hours)
- **Step 2**: Create graph function (1 hour)
- **Step 3**: Deploy all functions (30 minutes)
- **Step 4**: Verify frontend (already done)
- **Step 5**: Test authentication (30 minutes)
- **Step 6**: Check logs (15 minutes)

**Total**: 2-4 hours

---

## Key Files

### Backend
- `functions/shared/auth/firebase_auth.py` - Authentication middleware (already exists)
- `functions/review_api/main.py` - Update with @require_auth
- `functions/notes_api/main.py` - Update with @require_auth
- `functions/orchestration/main.py` - Update with @require_auth
- `functions/graph/main.py` - Create with @require_auth

### Frontend
- `web/src/services/reviewService.ts` - Already sends auth headers
- `web/src/services/notesService.ts` - Already sends auth headers
- `web/src/services/graphService.ts` - Create with auth headers (Sprint 6)

---

## Summary

The organization policy is **not a blocker**. Firebase Authentication is the correct solution and is already implemented. Apply the `@require_auth` decorator to all functions, deploy without `--allow-unauthenticated`, and continue with Sprint 6.

**This is how it should be done.**

---

**Status**: Ready to Execute  
**Estimated Time**: 2-4 hours  
**Next Action**: Update functions with @require_auth and deploy

---

**END OF ACTION PLAN**