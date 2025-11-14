# Knowledge Graph API Fix Guide

**Issue**: Knowledge Graph shows "Unexpected token '<', "<!doctype "... is not valid JSON"  
**Root Cause**: Firebase Auth token has wrong audience claim  
**Solution**: Fix token verification in graph-api

---

## Problem Analysis

### Error from Logs
```
Invalid ID token: Firebase ID token has incorrect "aud" (audience) claim. 
Expected "aletheia-codex-prod" but got "32555940559.apps.googleusercontent.com". 
Make sure the ID token comes from the same Firebase project as the service account 
used to authenticate this SDK.
```

### What's Happening
1. Frontend sends Firebase Auth token to graph-api
2. graph-api tries to verify token
3. Token has audience `32555940559.apps.googleusercontent.com` (OAuth client ID)
4. graph-api expects audience `aletheia-codex-prod` (project ID)
5. Verification fails → Returns 401 error
6. Firebase Hosting sees 401 → Returns HTML error page
7. Frontend tries to parse HTML as JSON → "Unexpected token '<'" error

---

## Solution Options

### Option 1: Fix Token Verification (Recommended)

The Firebase Admin SDK should accept tokens with OAuth client ID as audience.

**Update `functions/graph_api/shared/auth/firebase_auth.py`**:

```python
def verify_firebase_token(id_token: str) -> Dict[str, Any]:
    """
    Verify Firebase ID token.
    
    Args:
        id_token: Firebase ID token from Authorization header
        
    Returns:
        Decoded token with user information
        
    Raises:
        ValueError: If token is invalid
    """
    try:
        # Verify the token - this will accept tokens with correct audience
        decoded_token = auth.verify_id_token(id_token, check_revoked=True)
        return decoded_token
    except auth.InvalidIdTokenError as e:
        logger.error(f"Invalid ID token: {str(e)}")
        raise ValueError(f"Invalid authentication token: {str(e)}")
    except auth.ExpiredIdTokenError:
        logger.error("ID token has expired")
        raise ValueError("Authentication token has expired")
    except auth.RevokedIdTokenError:
        logger.error("ID token has been revoked")
        raise ValueError("Authentication token has been revoked")
    except Exception as e:
        logger.error(f"Token verification failed: {str(e)}")
        raise ValueError(f"Token verification failed: {str(e)}")
```

The issue is that the current code might be too strict. The Firebase Admin SDK should handle this automatically.

### Option 2: Check Firebase Admin Initialization

Ensure Firebase Admin is initialized with correct credentials:

```python
# In graph_api/main.py
import firebase_admin
from firebase_admin import credentials

# Initialize Firebase Admin with service account
cred = credentials.ApplicationDefault()
firebase_admin.initialize_app(cred, {
    'projectId': 'aletheia-codex-prod',
})
```

### Option 3: Use Custom Token Verification

If the Firebase Admin SDK is being too strict, use custom verification:

```python
from google.oauth2 import id_token
from google.auth.transport import requests

def verify_firebase_token(id_token_string: str) -> Dict[str, Any]:
    """Verify Firebase ID token with custom verification."""
    try:
        # Verify token with Google's public keys
        request = requests.Request()
        decoded_token = id_token.verify_oauth2_token(
            id_token_string, 
            request,
            audience=None  # Don't check audience
        )
        
        # Verify issuer
        if decoded_token['iss'] not in [
            'https://securetoken.google.com/aletheia-codex-prod',
            'https://accounts.google.com'
        ]:
            raise ValueError('Invalid token issuer')
        
        return decoded_token
    except Exception as e:
        logger.error(f"Token verification failed: {str(e)}")
        raise ValueError(f"Invalid authentication token: {str(e)}")
```

---

## Quick Fix: Check Current Implementation

Let me check what's actually in the code:

```bash
cd /workspace/aletheia-codex
cat functions/graph_api/shared/auth/firebase_auth.py
```

Look for the `verify_firebase_token` function and see if it's doing anything unusual.

---

## Deployment Steps

### 1. Update the Code

Choose one of the solutions above and update the code.

### 2. Redeploy graph-api

```bash
cd /workspace/aletheia-codex/functions

gcloud run deploy graph-api \
  --source=graph_api \
  --region=us-central1 \
  --platform=managed \
  --allow-unauthenticated \
  --no-invoker-iam-check \
  --set-env-vars="GCP_PROJECT=aletheia-codex-prod" \
  --memory=512Mi \
  --cpu=1 \
  --project=aletheia-codex-prod
```

### 3. Test

```bash
# Get a Firebase token from browser console
# In browser console on aletheiacodex.app:
# firebase.auth().currentUser.getIdToken().then(token => console.log(token))

# Test the API
TOKEN="<paste-token-here>"
curl -H "Authorization: Bearer $TOKEN" \
  "https://graph-api-679360092359.us-central1.run.app?limit=10&offset=0"
```

---

## Alternative: Temporary Workaround

If fixing the token verification is complex, we can temporarily disable authentication for testing:

**WARNING: This is insecure and should only be used for testing!**

```python
# In graph_api/main.py
@functions_framework.http
def graph_function(request: Request):
    """Graph API endpoint (temporarily without auth for testing)."""
    
    # TEMPORARY: Skip authentication
    user_id = "test-user-id"  # Hardcode for testing
    
    # ... rest of the code
```

**DO NOT use this in production!**

---

## Verification Steps

### 1. Check API Response

```bash
# Should return JSON, not HTML
curl -H "Authorization: Bearer $TOKEN" \
  "https://graph-api-679360092359.us-central1.run.app?limit=10&offset=0"
```

**Expected**: JSON response (even if empty)
```json
{
  "nodes": [],
  "total": 0
}
```

**Not Expected**: HTML error page
```html
<!doctype html>
<html>
...
```

### 2. Check Browser

1. Go to https://aletheiacodex.app/graph
2. Open browser console (F12)
3. Should see: "No nodes found" or list of nodes
4. Should NOT see: "Unexpected token '<'" error

### 3. Check Logs

```bash
gcloud run services logs read graph-api \
  --region=us-central1 \
  --project=aletheia-codex-prod \
  --limit=20
```

**Should see**: Successful requests with 200 status
**Should NOT see**: "Invalid ID token" errors

---

## Root Cause Deep Dive

The issue is that Firebase Auth tokens can have different audience claims depending on how they're obtained:

1. **Web SDK tokens**: audience = OAuth client ID (e.g., `32555940559.apps.googleusercontent.com`)
2. **Admin SDK tokens**: audience = project ID (e.g., `aletheia-codex-prod`)

The Firebase Admin SDK should accept both, but it seems to be rejecting the web SDK tokens.

**Solution**: Either:
- Fix the verification to accept web SDK tokens
- Or ensure the frontend is sending the correct token format

---

## Next Steps

1. **Check current firebase_auth.py implementation**
2. **Apply appropriate fix** (Option 1, 2, or 3)
3. **Redeploy graph-api**
4. **Test in browser**
5. **Verify no JSON parse errors**

---

## Success Criteria

- ✅ graph-api returns JSON (not HTML)
- ✅ Knowledge Graph page loads without errors
- ✅ Can see nodes or "No nodes found" message
- ✅ No "Unexpected token '<'" errors
- ✅ No "Invalid ID token" errors in logs