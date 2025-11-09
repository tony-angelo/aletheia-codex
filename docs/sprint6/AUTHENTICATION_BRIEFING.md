# Authentication Implementation Guide

**Issue**: GCP Organization Policy (`iam.allowedPolicyMemberDomains`) prevents public access to Cloud Functions  
**Solution**: Implement Firebase Authentication for all HTTP-triggered Cloud Functions  
**Priority**: HIGH - Required before Sprint 6 can proceed  
**Estimated Time**: 4-6 hours

---

## Table of Contents
1. [Overview](#overview)
2. [Why This Solution](#why-this-solution)
3. [Implementation Steps](#implementation-steps)
4. [Testing](#testing)
5. [Deployment](#deployment)
6. [Verification](#verification)

---

## Overview

### Problem
The GCP project has an organization policy that prevents deploying Cloud Functions with `--allow-unauthenticated`. This blocks:
- Graph Function (Sprint 6 - NEW)
- Review Queue Function (existing)
- Any future HTTP-triggered functions

### Solution
Implement Firebase Authentication for all HTTP-triggered Cloud Functions. Functions will:
1. Verify Firebase ID tokens sent in Authorization headers
2. Extract user ID from verified tokens
3. Use user ID for authorization and data access
4. Return 401 for unauthenticated requests

### Benefits
- ✅ Works within existing security constraints
- ✅ Proper authentication and authorization
- ✅ Already have Firebase Auth (Sprint 4.5)
- ✅ Industry standard approach
- ✅ Enables per-user rate limiting and cost tracking

---

## Why This Solution

### Security ✅
- **Proper Authentication**: Only authenticated users can access functions
- **Token Verification**: Firebase tokens are cryptographically verified
- **No Public Access**: Functions require valid authentication
- **Audit Trail**: Can track which user made which request

### Compliance ✅
- **Meets Org Policy**: Works within existing security constraints
- **No Policy Changes**: Doesn't require organization admin access
- **Industry Standard**: Firebase Auth is widely used and trusted

### Functionality ✅
- **Already Implemented**: Firebase Auth working (Sprint 4.5)
- **Minimal Changes**: Small updates to existing code
- **Backward Compatible**: Existing features continue to work

---

## Implementation Steps

### Step 1: Create Authentication Middleware ✅ DONE

**File**: `functions/shared/auth/firebase_auth.py`

This file has been created with:
- `@require_auth` decorator for protecting functions
- `get_user_id_from_request()` helper function
- Comprehensive error handling
- Logging for debugging

**Usage**:
```python
from shared.auth.firebase_auth import require_auth

@functions_framework.http
@require_auth
def my_function(request):
    user_id = request.user_id  # Available after authentication
    # Function logic
```

### Step 2: Update Graph Function

**File**: `functions/graph/main.py`

**Changes Required**:
1. Import authentication decorator
2. Add `@require_auth` decorator to function
3. Remove `userId` from query parameters (use `request.user_id` instead)
4. Update CORS headers to include Authorization

**Before**:
```python
@functions_framework.http
def graph_function(request):
    # Get user ID from query params
    user_id = request.args.get('userId')
    if not user_id:
        return (jsonify({'error': 'userId required'}), 400, headers)
```

**After**:
```python
from shared.auth.firebase_auth import require_auth

@functions_framework.http
@require_auth  # Add authentication
def graph_function(request):
    # Get user ID from authentication
    user_id = request.user_id  # Set by @require_auth decorator
```

**Full Updated Code**:
```python
import functions_framework
from flask import jsonify, request
from shared.auth.firebase_auth import require_auth
from shared.db.neo4j_client import get_neo4j_client
import logging

logger = logging.getLogger(__name__)

@functions_framework.http
@require_auth  # Require authentication
def graph_function(request):
    """HTTP Cloud Function for graph operations (authenticated)."""
    
    # CORS headers - include Authorization
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',  # Added Authorization
        }
        return ('', 204, headers)
    
    headers = {'Access-Control-Allow-Origin': '*'}
    
    try:
        # Get authenticated user ID (set by @require_auth)
        user_id = request.user_id
        
        # Route based on path
        path = request.path
        
        if path == '/nodes':
            return get_nodes(user_id, request, headers)
        elif path.startswith('/nodes/'):
            node_id = path.split('/')[-1]
            return get_node_details(user_id, node_id, headers)
        elif path == '/search':
            return search_nodes(user_id, request, headers)
        else:
            return (jsonify({'error': 'Invalid path'}), 404, headers)
            
    except Exception as e:
        logger.error(f"Graph function error: {str(e)}", exc_info=True)
        return (jsonify({'error': str(e)}), 500, headers)

def get_nodes(user_id: str, request, headers):
    """Get list of nodes for authenticated user."""
    # user_id is now from authentication, not query params
    limit = int(request.args.get('limit', 50))
    offset = int(request.args.get('offset', 0))
    node_type = request.args.get('type')  # Optional filter
    
    client = get_neo4j_client()
    
    # Build query - user_id from authentication
    query = """
    MATCH (u:User {userId: $userId})-[:OWNS]->(n)
    """
    
    if node_type:
        query += f"WHERE '{node_type}' IN labels(n) "
    
    query += """
    RETURN n, labels(n) as types
    ORDER BY n.createdAt DESC
    SKIP $offset
    LIMIT $limit
    """
    
    result = client.execute_query(query, {
        'userId': user_id,
        'offset': offset,
        'limit': limit
    })
    
    nodes = []
    for record in result.get('data', []):
        node_data = record['n']
        node_data['types'] = record['types']
        nodes.append(node_data)
    
    return (jsonify({'nodes': nodes, 'total': len(nodes)}), 200, headers)

def get_node_details(user_id: str, node_id: str, headers):
    """Get detailed information about a node."""
    client = get_neo4j_client()
    
    # Get node with relationships - verify user owns it
    query = """
    MATCH (u:User {userId: $userId})-[:OWNS]->(n)
    WHERE elementId(n) = $nodeId
    OPTIONAL MATCH (n)-[r]-(related)
    RETURN n, labels(n) as types, 
           collect({
               relationship: type(r),
               direction: CASE 
                   WHEN startNode(r) = n THEN 'outgoing'
                   ELSE 'incoming'
               END,
               node: related,
               nodeTypes: labels(related)
           }) as relationships
    """
    
    result = client.execute_query(query, {
        'userId': user_id,
        'nodeId': node_id
    })
    
    if not result.get('data'):
        return (jsonify({'error': 'Node not found'}), 404, headers)
    
    record = result['data'][0]
    node_data = record['n']
    node_data['types'] = record['types']
    node_data['relationships'] = record['relationships']
    
    return (jsonify(node_data), 200, headers)

def search_nodes(user_id: str, request, headers):
    """Search nodes by name or properties."""
    query_text = request.args.get('query', '')
    if not query_text:
        return (jsonify({'error': 'query parameter required'}), 400, headers)
    
    client = get_neo4j_client()
    
    # Search by name (case-insensitive) - only user's nodes
    query = """
    MATCH (u:User {userId: $userId})-[:OWNS]->(n)
    WHERE toLower(n.name) CONTAINS toLower($query)
    RETURN n, labels(n) as types
    ORDER BY n.name
    LIMIT 50
    """
    
    result = client.execute_query(query, {
        'userId': user_id,
        'query': query_text
    })
    
    nodes = []
    for record in result.get('data', []):
        node_data = record['n']
        node_data['types'] = record['types']
        nodes.append(node_data)
    
    return (jsonify({'nodes': nodes, 'total': len(nodes)}), 200, headers)
```

### Step 3: Update Review Queue Function

**File**: `functions/review_queue/main.py`

**Changes Required**:
1. Import authentication decorator
2. Add `@require_auth` decorator
3. Remove `userId` from request body (use `request.user_id`)
4. Add security check to verify user owns the item

**Before**:
```python
@functions_framework.http
def review_queue_function(request):
    data = request.get_json()
    user_id = data.get('userId')  # From request body
```

**After**:
```python
from shared.auth.firebase_auth import require_auth

@functions_framework.http
@require_auth
def review_queue_function(request):
    user_id = request.user_id  # From authentication
```

**Full Updated Code**:
```python
import functions_framework
from flask import jsonify, request
from shared.auth.firebase_auth import require_auth
from google.cloud import firestore
from shared.db.neo4j_client import get_neo4j_client
import logging

logger = logging.getLogger(__name__)

@functions_framework.http
@require_auth  # Require authentication
def review_queue_function(request):
    """HTTP Cloud Function for review queue operations (authenticated)."""
    
    # CORS headers - include Authorization
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',  # Added Authorization
        }
        return ('', 204, headers)
    
    headers = {'Access-Control-Allow-Origin': '*'}
    
    try:
        # Get authenticated user ID
        user_id = request.user_id
        
        # Parse request
        data = request.get_json()
        action = data.get('action')
        item_id = data.get('itemId')
        
        if not action or not item_id:
            return (jsonify({'error': 'action and itemId required'}), 400, headers)
        
        # Get Firestore client
        db = firestore.Client()
        
        # Get review item and verify user owns it (SECURITY CHECK)
        item_ref = db.collection('reviewQueue').document(item_id)
        item = item_ref.get()
        
        if not item.exists:
            return (jsonify({'error': 'Item not found'}), 404, headers)
        
        item_data = item.to_dict()
        
        # Verify user owns this item
        if item_data.get('userId') != user_id:
            logger.warning(f"User {user_id} attempted to access item owned by {item_data.get('userId')}")
            return (jsonify({'error': 'Unauthorized'}), 403, headers)
        
        # Process action
        if action == 'approve':
            return approve_item(user_id, item_id, item_data, headers)
        elif action == 'reject':
            return reject_item(user_id, item_id, item_data, headers)
        else:
            return (jsonify({'error': 'Invalid action'}), 400, headers)
            
    except Exception as e:
        logger.error(f"Review queue error: {str(e)}", exc_info=True)
        return (jsonify({'error': str(e)}), 500, headers)

def approve_item(user_id: str, item_id: str, item_data: dict, headers):
    """Approve review item and add to Neo4j."""
    logger.info(f"Approving item {item_id} for user {user_id}")
    
    try:
        # Add to Neo4j
        neo4j_client = get_neo4j_client()
        
        if item_data['type'] == 'entity':
            # Create entity node
            entity = item_data['data']
            query = """
            MATCH (u:User {userId: $userId})
            CREATE (e:Entity {name: $name, type: $type})
            CREATE (u)-[:OWNS]->(e)
            RETURN elementId(e) as nodeId
            """
            result = neo4j_client.execute_query(query, {
                'userId': user_id,
                'name': entity.get('name'),
                'type': entity.get('type')
            })
            node_id = result['data'][0]['nodeId'] if result.get('data') else None
        else:
            # Create relationship
            # Implementation...
            node_id = None
        
        # Update Firestore
        db = firestore.Client()
        db.collection('reviewQueue').document(item_id).update({
            'status': 'approved',
            'reviewedAt': firestore.SERVER_TIMESTAMP
        })
        
        logger.info(f"Item {item_id} approved successfully")
        return (jsonify({'success': True, 'nodeId': node_id}), 200, headers)
        
    except Exception as e:
        logger.error(f"Failed to approve item: {str(e)}", exc_info=True)
        return (jsonify({'error': str(e)}), 500, headers)

def reject_item(user_id: str, item_id: str, item_data: dict, headers):
    """Reject review item."""
    logger.info(f"Rejecting item {item_id} for user {user_id}")
    
    try:
        # Update Firestore
        db = firestore.Client()
        db.collection('reviewQueue').document(item_id).update({
            'status': 'rejected',
            'reviewedAt': firestore.SERVER_TIMESTAMP
        })
        
        logger.info(f"Item {item_id} rejected successfully")
        return (jsonify({'success': True}), 200, headers)
        
    except Exception as e:
        logger.error(f"Failed to reject item: {str(e)}", exc_info=True)
        return (jsonify({'error': str(e)}), 500, headers)
```

### Step 4: Update requirements.txt

**Files**: 
- `functions/graph/requirements.txt`
- `functions/review_queue/requirements.txt`

**Add**:
```
firebase-admin==6.*
```

**Full requirements.txt**:
```
functions-framework==3.*
firebase-admin==6.*
google-cloud-firestore==2.*
google-cloud-secret-manager==2.*
requests==2.*
```

### Step 5: Update Frontend Services

#### A. Create Auth Helper

**File**: `web/src/utils/auth.ts`

```typescript
import { auth } from '../firebase/config';

/**
 * Get authentication headers with Firebase token
 * @returns Headers with Authorization bearer token
 * @throws Error if user is not authenticated
 */
export async function getAuthHeaders(): Promise<HeadersInit> {
  const user = auth.currentUser;
  
  if (!user) {
    throw new Error('Not authenticated. Please sign in.');
  }
  
  try {
    const token = await user.getIdToken();
    
    return {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    };
  } catch (error) {
    console.error('Failed to get auth token:', error);
    throw new Error('Failed to get authentication token. Please sign in again.');
  }
}

/**
 * Check if user is authenticated
 * @returns true if user is signed in
 */
export function isAuthenticated(): boolean {
  return auth.currentUser !== null;
}
```

#### B. Update Graph Service

**File**: `web/src/services/graphService.ts`

**Changes**:
1. Import `getAuthHeaders`
2. Add Authorization header to all requests
3. Remove `userId` from query parameters

**Before**:
```typescript
const params = new URLSearchParams({
  userId: user.uid,  // Remove this
  limit: String(options.limit || 50),
});
```

**After**:
```typescript
import { getAuthHeaders } from '../utils/auth';

const headers = await getAuthHeaders();  // Get auth headers

const params = new URLSearchParams({
  // userId removed - comes from auth token
  limit: String(options.limit || 50),
});

const response = await fetch(`${GRAPH_API_URL}/nodes?${params}`, {
  headers,  // Include auth headers
});
```

**Full Updated Code**:
```typescript
import { getAuthHeaders } from '../utils/auth';

const GRAPH_API_URL = process.env.REACT_APP_GRAPH_API_URL || 
  'https://us-central1-aletheia-codex-prod.cloudfunctions.net/graph-function';

export interface GraphNode {
  id: string;
  name: string;
  types: string[];
  properties: Record<string, any>;
  createdAt: string;
}

export interface NodeDetails extends GraphNode {
  relationships: Array<{
    relationship: string;
    direction: 'incoming' | 'outgoing';
    node: GraphNode;
    nodeTypes: string[];
  }>;
}

export interface NodesResponse {
  nodes: GraphNode[];
  total: number;
}

export const graphService = {
  /**
   * Get list of nodes for current user
   */
  async getNodes(options: {
    limit?: number;
    offset?: number;
    type?: string;
  } = {}): Promise<NodesResponse> {
    const headers = await getAuthHeaders();
    
    const params = new URLSearchParams({
      limit: String(options.limit || 50),
      offset: String(options.offset || 0),
    });
    
    if (options.type) {
      params.append('type', options.type);
    }
    
    const response = await fetch(`${GRAPH_API_URL}/nodes?${params}`, {
      headers,
    });
    
    if (!response.ok) {
      if (response.status === 401) {
        throw new Error('Authentication failed. Please sign in again.');
      }
      throw new Error(`Failed to fetch nodes: ${response.statusText}`);
    }
    
    return response.json();
  },
  
  /**
   * Get detailed information about a specific node
   */
  async getNodeDetails(nodeId: string): Promise<NodeDetails> {
    const headers = await getAuthHeaders();
    
    const response = await fetch(`${GRAPH_API_URL}/nodes/${nodeId}`, {
      headers,
    });
    
    if (!response.ok) {
      if (response.status === 401) {
        throw new Error('Authentication failed. Please sign in again.');
      }
      if (response.status === 404) {
        throw new Error('Node not found');
      }
      throw new Error(`Failed to fetch node details: ${response.statusText}`);
    }
    
    return response.json();
  },
  
  /**
   * Search nodes by name or properties
   */
  async searchNodes(query: string): Promise<NodesResponse> {
    const headers = await getAuthHeaders();
    
    const params = new URLSearchParams({ query });
    
    const response = await fetch(`${GRAPH_API_URL}/search?${params}`, {
      headers,
    });
    
    if (!response.ok) {
      if (response.status === 401) {
        throw new Error('Authentication failed. Please sign in again.');
      }
      throw new Error(`Failed to search nodes: ${response.statusText}`);
    }
    
    return response.json();
  },
};
```

#### C. Update Review Service

**File**: `web/src/services/reviewService.ts`

**Changes**:
1. Import `getAuthHeaders`
2. Add Authorization header to all requests
3. Remove `userId` from request body

**Full Updated Code**:
```typescript
import { getAuthHeaders } from '../utils/auth';

const REVIEW_API_URL = process.env.REACT_APP_REVIEW_API_URL || 
  'https://us-central1-aletheia-codex-prod.cloudfunctions.net/review-queue-function';

export const reviewService = {
  /**
   * Approve a review item
   */
  async approveItem(itemId: string): Promise<void> {
    const headers = await getAuthHeaders();
    
    const response = await fetch(REVIEW_API_URL, {
      method: 'POST',
      headers,
      body: JSON.stringify({
        action: 'approve',
        itemId,
        // userId removed - comes from auth token
      }),
    });
    
    if (!response.ok) {
      if (response.status === 401) {
        throw new Error('Authentication failed. Please sign in again.');
      }
      if (response.status === 403) {
        throw new Error('Unauthorized. You do not own this item.');
      }
      throw new Error(`Failed to approve item: ${response.statusText}`);
    }
  },
  
  /**
   * Reject a review item
   */
  async rejectItem(itemId: string): Promise<void> {
    const headers = await getAuthHeaders();
    
    const response = await fetch(REVIEW_API_URL, {
      method: 'POST',
      headers,
      body: JSON.stringify({
        action: 'reject',
        itemId,
        // userId removed - comes from auth token
      }),
    });
    
    if (!response.ok) {
      if (response.status === 401) {
        throw new Error('Authentication failed. Please sign in again.');
      }
      if (response.status === 403) {
        throw new Error('Unauthorized. You do not own this item.');
      }
      throw new Error(`Failed to reject item: ${response.statusText}`);
    }
  },
};
```

---

## Testing

### Local Testing (Before Deployment)

#### 1. Test Authentication Middleware

Create test file: `functions/shared/auth/test_firebase_auth.py`

```python
import pytest
from unittest.mock import Mock, patch
from firebase_auth import require_auth

def test_require_auth_missing_header():
    """Test that missing Authorization header returns 401"""
    request = Mock()
    request.headers.get.return_value = None
    
    @require_auth
    def test_function(request):
        return "Success"
    
    response, status_code = test_function(request)
    assert status_code == 401

def test_require_auth_invalid_format():
    """Test that invalid header format returns 401"""
    request = Mock()
    request.headers.get.return_value = "InvalidFormat"
    
    @require_auth
    def test_function(request):
        return "Success"
    
    response, status_code = test_function(request)
    assert status_code == 401

# Add more tests...
```

#### 2. Test Frontend Auth Helper

Create test file: `web/src/utils/__tests__/auth.test.ts`

```typescript
import { getAuthHeaders, isAuthenticated } from '../auth';
import { auth } from '../../firebase/config';

jest.mock('../../firebase/config');

describe('Auth Utils', () => {
  it('throws error when user is not authenticated', async () => {
    (auth.currentUser as any) = null;
    
    await expect(getAuthHeaders()).rejects.toThrow('Not authenticated');
  });
  
  it('returns headers with token when authenticated', async () => {
    const mockUser = {
      getIdToken: jest.fn().mockResolvedValue('mock-token'),
    };
    (auth.currentUser as any) = mockUser;
    
    const headers = await getAuthHeaders();
    
    expect(headers).toEqual({
      'Content-Type': 'application/json',
      'Authorization': 'Bearer mock-token',
    });
  });
});
```

### Integration Testing (After Deployment)

#### 1. Test Graph Function

```bash
# Get Firebase token
# (Sign in to the app and get token from browser console)
TOKEN="your-firebase-token-here"

# Test get nodes
curl -X GET \
  "https://us-central1-aletheia-codex-prod.cloudfunctions.net/graph-function/nodes?limit=10" \
  -H "Authorization: Bearer $TOKEN"

# Test get node details
curl -X GET \
  "https://us-central1-aletheia-codex-prod.cloudfunctions.net/graph-function/nodes/node-id-here" \
  -H "Authorization: Bearer $TOKEN"

# Test search
curl -X GET \
  "https://us-central1-aletheia-codex-prod.cloudfunctions.net/graph-function/search?query=test" \
  -H "Authorization: Bearer $TOKEN"

# Test without token (should return 401)
curl -X GET \
  "https://us-central1-aletheia-codex-prod.cloudfunctions.net/graph-function/nodes"
```

#### 2. Test Review Queue Function

```bash
# Test approve
curl -X POST \
  "https://us-central1-aletheia-codex-prod.cloudfunctions.net/review-queue-function" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"action": "approve", "itemId": "item-id-here"}'

# Test reject
curl -X POST \
  "https://us-central1-aletheia-codex-prod.cloudfunctions.net/review-queue-function" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"action": "reject", "itemId": "item-id-here"}'
```

---

## Deployment

### Step 1: Deploy Functions WITHOUT --allow-unauthenticated

```bash
# Deploy graph function (authenticated)
cd functions/graph
gcloud functions deploy graph-function \
  --gen2 \
  --runtime=python311 \
  --region=us-central1 \
  --source=. \
  --entry-point=graph_function \
  --trigger-http \
  --service-account=aletheia-functions@aletheia-codex-prod.iam.gserviceaccount.com \
  --set-env-vars GCP_PROJECT=aletheia-codex-prod \
  --memory=256MB \
  --timeout=60s
# NOTE: No --allow-unauthenticated flag

# Deploy review queue function (authenticated)
cd ../review_queue
gcloud functions deploy review-queue-function \
  --gen2 \
  --runtime=python311 \
  --region=us-central1 \
  --source=. \
  --entry-point=review_queue_function \
  --trigger-http \
  --service-account=review-queue-sa@aletheia-codex-prod.iam.gserviceaccount.com \
  --set-env-vars GCP_PROJECT=aletheia-codex-prod \
  --memory=256MB \
  --timeout=60s
# NOTE: No --allow-unauthenticated flag
```

### Step 2: Grant Invoker Permission

```bash
# Allow public invocation (but function verifies Firebase token)
gcloud functions add-invoker-policy-binding graph-function \
  --region=us-central1 \
  --member=allUsers

gcloud functions add-invoker-policy-binding review-queue-function \
  --region=us-central1 \
  --member=allUsers
```

**Important**: This allows the function to be invoked, but the function code itself verifies the Firebase authentication token. This is different from `--allow-unauthenticated`.

### Step 3: Deploy Frontend

```bash
cd web
npm run build
firebase deploy --only hosting
```

---

## Verification

### 1. Check Function Deployment

```bash
# Check graph function
gcloud functions describe graph-function \
  --region=us-central1 \
  --gen2

# Check review queue function
gcloud functions describe review-queue-function \
  --region=us-central1 \
  --gen2
```

### 2. Test Authentication

#### A. Test Without Token (Should Fail)
```bash
curl -X GET \
  "https://us-central1-aletheia-codex-prod.cloudfunctions.net/graph-function/nodes"

# Expected: 401 Unauthorized
# Response: {"error": "Missing Authorization header"}
```

#### B. Test With Invalid Token (Should Fail)
```bash
curl -X GET \
  "https://us-central1-aletheia-codex-prod.cloudfunctions.net/graph-function/nodes" \
  -H "Authorization: Bearer invalid-token"

# Expected: 401 Unauthorized
# Response: {"error": "Invalid authentication token"}
```

#### C. Test With Valid Token (Should Succeed)
```bash
# Get token from browser console after signing in:
# await firebase.auth().currentUser.getIdToken()

curl -X GET \
  "https://us-central1-aletheia-codex-prod.cloudfunctions.net/graph-function/nodes" \
  -H "Authorization: Bearer YOUR_VALID_TOKEN"

# Expected: 200 OK
# Response: {"nodes": [...], "total": X}
```

### 3. Test in Browser

1. **Sign In**: Go to app and sign in with Google
2. **Open Console**: Open browser developer console
3. **Test Graph Page**: Navigate to /graph
4. **Check Network Tab**: Verify requests include Authorization header
5. **Check Response**: Verify 200 OK responses (not 401)

### 4. Check Logs

```bash
# Check graph function logs
gcloud functions logs read graph-function \
  --region=us-central1 \
  --limit=50

# Look for:
# - "Authenticated request from user: USER_ID"
# - No "Missing Authorization header" errors
# - No "Invalid authentication token" errors

# Check review queue function logs
gcloud functions logs read review-queue-function \
  --region=us-central1 \
  --limit=50
```

---

## Troubleshooting

### Issue: "Missing Authorization header"

**Cause**: Frontend not sending Authorization header

**Solution**:
1. Check that `getAuthHeaders()` is being called
2. Verify user is signed in (`auth.currentUser` is not null)
3. Check network tab to see if header is included

### Issue: "Invalid authentication token"

**Cause**: Token is malformed or expired

**Solution**:
1. Check token format: `Bearer <token>`
2. Get fresh token: `await user.getIdToken(true)` (force refresh)
3. Verify Firebase project ID matches

### Issue: "Authentication token expired"

**Cause**: Token is older than 1 hour

**Solution**:
- Firebase SDK automatically refreshes tokens
- Call `getIdToken()` to get current token
- Frontend should handle 401 and prompt re-authentication

### Issue: CORS errors

**Cause**: CORS headers not configured correctly

**Solution**:
1. Verify OPTIONS handler includes Authorization in allowed headers
2. Check CORS headers in all responses
3. Ensure `Access-Control-Allow-Headers` includes `Authorization`

### Issue: "Unauthorized. You do not own this item"

**Cause**: User trying to access another user's data

**Solution**:
- This is correct behavior (security working)
- Verify user is accessing their own data
- Check userId in Firestore matches authenticated user

---

## Success Criteria

Authentication implementation is complete when:

- [ ] Authentication middleware created (`firebase_auth.py`)
- [ ] Graph function updated with `@require_auth`
- [ ] Review queue function updated with `@require_auth`
- [ ] Frontend auth helper created (`auth.ts`)
- [ ] Graph service updated to use auth headers
- [ ] Review service updated to use auth headers
- [ ] Functions deployed without `--allow-unauthenticated`
- [ ] Invoker permissions granted
- [ ] Frontend deployed
- [ ] All tests passing
- [ ] Authentication working in production
- [ ] No 401 errors for authenticated users
- [ ] 401 errors for unauthenticated requests

---

## Next Steps After Implementation

1. **Update Sprint 6 Documentation**: Document authentication approach
2. **Continue Sprint 6**: Proceed with building Graph page components
3. **Monitor Logs**: Watch for authentication errors
4. **User Testing**: Test with real users to ensure smooth experience

---

**End of Authentication Implementation Guide**