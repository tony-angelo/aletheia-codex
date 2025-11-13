# Authentication Module

## Overview

This module provides authentication for AletheiaCodex Cloud Functions, supporting both Identity-Aware Proxy (IAP) and Firebase Authentication.

## Architecture

### Authentication Priority

1. **IAP Authentication (Production)**: Checked first when `X-Goog-IAP-JWT-Assertion` header is present
2. **Firebase Authentication (Development)**: Fallback when `Authorization: Bearer` header is present

### Modules

#### `iap_auth.py`
Handles IAP JWT token validation and user extraction.

**Key Functions:**
- `validate_iap_jwt(jwt_token, expected_audience)`: Validates IAP JWT signature and claims
- `extract_user_from_iap_token(decoded_token)`: Extracts user email from token
- `get_user_from_iap(request)`: Complete IAP authentication flow

**Configuration:**
- Environment variable: `IAP_AUDIENCE` (format: `/projects/<number>/apps/<project-id>`)

#### `firebase_auth.py`
Handles Firebase ID token validation (legacy, maintained for backward compatibility).

**Key Functions:**
- `verify_firebase_token(id_token)`: Validates Firebase ID token
- `get_user_id_from_request(request)`: Extracts user ID from Firebase token
- `require_auth`: Decorator for Firebase-only authentication (deprecated)

#### `unified_auth.py`
Combines IAP and Firebase authentication with automatic fallback.

**Key Functions:**
- `get_user_id_from_request(request)`: Tries IAP first, falls back to Firebase
- `require_auth`: Decorator for Cloud Functions (recommended)

## Usage

### Cloud Functions

```python
import functions_framework
from shared.auth.unified_auth import require_auth

@functions_framework.http
@require_auth
def my_function(request):
    # User is authenticated, user_id is available
    user_id = request.user_id
    
    # Your function logic here
    return jsonify({"status": "success", "user": user_id})
```

### Authentication Flow

1. **Request arrives** at Cloud Function
2. **Decorator intercepts** request
3. **CORS preflight** handled (OPTIONS method)
4. **Authentication check**:
   - If `X-Goog-IAP-JWT-Assertion` header present → IAP authentication
   - Else if `Authorization: Bearer` header present → Firebase authentication
   - Else → 401 Unauthorized
5. **User ID extracted** and added to `request.user_id`
6. **Function executes** with authenticated user

### Error Handling

All authentication failures return:
```json
{
  "error": "Authentication failed: <reason>"
}
```

Status code: `401 Unauthorized`

CORS headers included in all responses.

## Configuration

### Environment Variables

**IAP_AUDIENCE** (required for IAP):
```bash
IAP_AUDIENCE=/projects/<project-number>/apps/<project-id>
```

Get project number:
```bash
gcloud projects describe aletheia-codex-prod --format="value(projectNumber)"
```

### Cloud Function Deployment

Update `env.yaml` or deployment command:
```bash
gcloud functions deploy my-function \
  --set-env-vars IAP_AUDIENCE=/projects/123456789/apps/aletheia-codex-prod
```

## Testing

### Running Tests

```bash
# Run all authentication tests
pytest shared/tests/ -v

# Run with coverage
pytest shared/tests/ --cov=shared/auth --cov-report=term-missing

# Run specific test file
pytest shared/tests/test_iap_auth.py -v
pytest shared/tests/test_unified_auth.py -v
```

### Test Coverage

- `iap_auth.py`: 94% coverage
- `unified_auth.py`: 100% coverage
- Total: 28 test cases, all passing

### Mock Authentication in Tests

```python
from unittest.mock import Mock, patch

# Mock IAP authentication
with patch('shared.auth.unified_auth.iap_auth.get_user_from_iap') as mock_iap:
    mock_iap.return_value = ('user@example.com', None)
    # Test your function

# Mock Firebase authentication
with patch('shared.auth.unified_auth.firebase_auth.get_user_id_from_request') as mock_firebase:
    mock_firebase.return_value = ('user@example.com', None)
    # Test your function
```

## Security Considerations

### JWT Validation

- **Signature verification**: Uses Google's public keys
- **Expiration check**: Tokens must not be expired
- **Issuer validation**: Must be `https://cloud.google.com/iap`
- **Audience validation**: Must match expected audience

### User Identity

- **Email as user ID**: Consistent across both auth methods
- **No client trust**: User ID always extracted from validated token
- **Data isolation**: Each user's data is isolated by user_id

### Error Messages

- **Generic errors**: Don't leak sensitive information to clients
- **Detailed logging**: Full error details logged for debugging
- **Security events**: Authentication failures logged for monitoring

## Migration Guide

### From Firebase Auth Only

**Before:**
```python
from shared.auth.firebase_auth import require_auth

@functions_framework.http
@require_auth
def my_function(request):
    user_id = request.user_id
    # ...
```

**After:**
```python
from shared.auth.unified_auth import require_auth

@functions_framework.http
@require_auth
def my_function(request):
    user_id = request.user_id
    # No other changes needed!
```

### Backward Compatibility

- **API contracts**: No changes to request/response formats
- **User ID format**: Same format (email) for both auth methods
- **Error handling**: Same error responses and status codes
- **CORS**: Same CORS configuration

## Troubleshooting

### IAP Authentication Fails

1. **Check IAP_AUDIENCE**: Ensure environment variable is set correctly
2. **Verify IAP configuration**: Check Load Balancer and IAP settings
3. **Check logs**: Look for detailed error messages in Cloud Logging
4. **Test JWT manually**: Use jwt.io to decode and inspect token

### Firebase Authentication Fails

1. **Check token format**: Must be `Authorization: Bearer <token>`
2. **Verify token validity**: Token must not be expired
3. **Check Firebase project**: Ensure correct project configuration
4. **Test token**: Use Firebase Admin SDK to verify token manually

### Both Authentication Methods Fail

1. **Check headers**: Ensure either IAP or Authorization header is present
2. **Verify CORS**: Check CORS configuration allows required headers
3. **Check logs**: Review Cloud Function logs for detailed errors
4. **Test locally**: Use curl or Postman to test authentication

## Performance

### Latency

- **IAP validation**: ~5-10ms (after public key cache warm-up)
- **Firebase validation**: ~10-20ms
- **Total overhead**: Minimal impact on API response times

### Optimization

- **Public key caching**: Google's public keys cached automatically
- **Connection pooling**: Reused for key fetching
- **Efficient validation**: Fast JWT signature verification

## References

- [Identity-Aware Proxy Documentation](https://cloud.google.com/iap/docs)
- [IAP JWT Validation](https://cloud.google.com/iap/docs/signed-headers-howto)
- [Firebase Authentication](https://firebase.google.com/docs/auth)
- [Cloud Functions Security](https://cloud.google.com/functions/docs/securing)

---

**Version**: 1.0.0  
**Sprint**: 1  
**Last Updated**: 2025-01-18