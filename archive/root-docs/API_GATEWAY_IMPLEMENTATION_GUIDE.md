# API Gateway Implementation Guide

## Overview

This guide provides step-by-step instructions for implementing Google Cloud API Gateway to provide public access to Aletheia Codex Cloud Functions while working within organization policy constraints.

## Why API Gateway?

The GCP organization policy `iam.allowedPolicyMemberDomains` prevents direct public access to Cloud Functions. API Gateway solves this by:

1. **Public-facing gateway**: API Gateway itself is publicly accessible
2. **Private backend**: Cloud Functions remain private, accessed only by the gateway
3. **Security maintained**: Firebase Authentication tokens are validated
4. **Policy compliant**: Works within organization constraints

## Architecture

```
User Browser
    ↓ (HTTPS + Firebase Auth Token)
API Gateway (Public)
    ↓ (Service Account Auth)
Cloud Functions (Private)
    ↓
Firestore / Neo4j
```

## Prerequisites

✅ APIs enabled:
- API Gateway API (`apigateway.googleapis.com`)
- Service Management API (`servicemanagement.googleapis.com`)
- Service Control API (`servicecontrol.googleapis.com`)

✅ Cloud Functions deployed:
- `review-api-function` (us-central1)
- `graph-function` (us-central1)

✅ Firebase Authentication configured

## Implementation Steps

### Phase 1: Deploy API Gateway (30 minutes)

#### Step 1.1: Review OpenAPI Specification

The `api-gateway-config.yaml` file defines:
- **Review API endpoints**: `/api/review/*`
- **Graph API endpoints**: `/api/graph`
- **Security**: Firebase Authentication required for all endpoints
- **Backend routing**: Maps to Cloud Functions

#### Step 1.2: Run Deployment Script

```bash
cd aletheia-codex
./deploy-api-gateway.sh
```

This script will:
1. Create the API Gateway API
2. Create the API configuration from OpenAPI spec
3. Deploy the gateway
4. Output the gateway URL

**Expected output:**
```
✅ Deployment Complete!
Gateway URL: https://aletheia-codex-gateway-XXXXX.uc.gateway.dev
```

**Save this URL** - you'll need it for frontend configuration.

#### Step 1.3: Verify Gateway Deployment

```bash
# Check gateway status
gcloud api-gateway gateways describe aletheia-codex-gateway \
  --location=us-central1 \
  --project=aletheia-codex-prod

# Should show state: ACTIVE
```

### Phase 2: Update Frontend Configuration (30 minutes)

#### Step 2.1: Update Environment Variables

Create/update `web/.env.production`:

```env
REACT_APP_API_URL=https://aletheia-codex-gateway-XXXXX.uc.gateway.dev
REACT_APP_GRAPH_API_URL=https://aletheia-codex-gateway-XXXXX.uc.gateway.dev
```

#### Step 2.2: Update API Service Files

The frontend already uses relative paths (`/api/review`, `/api/graph`), so no code changes needed if using Firebase Hosting rewrites.

**Option A: Use Firebase Hosting Rewrites (Recommended)**

Update `firebase.json`:

```json
{
  "hosting": {
    "rewrites": [
      {
        "source": "/api/**",
        "run": {
          "serviceId": "aletheia-codex-gateway",
          "region": "us-central1"
        }
      },
      {
        "source": "**",
        "destination": "/index.html"
      }
    ]
  }
}
```

**Option B: Direct API Gateway URLs**

Update `web/src/services/api.ts`:

```typescript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://aletheia-codex-gateway-XXXXX.uc.gateway.dev/api/review';
```

Update `web/src/services/graphService.ts`:

```typescript
const GRAPH_API_URL = process.env.REACT_APP_GRAPH_API_URL || 'https://aletheia-codex-gateway-XXXXX.uc.gateway.dev/api/graph';
```

#### Step 2.3: Build and Deploy Frontend

```bash
cd web
npm run build
cd ..
firebase deploy --only hosting
```

### Phase 3: Testing (30 minutes)

#### Step 3.1: Test API Gateway Directly

First, get a Firebase authentication token:

1. Open browser console on https://aletheiacodex.app
2. Run:
```javascript
firebase.auth().currentUser.getIdToken().then(token => console.log(token))
```
3. Copy the token

Test endpoints:

```bash
# Set your token
TOKEN="YOUR_FIREBASE_TOKEN"
GATEWAY_URL="https://aletheia-codex-gateway-XXXXX.uc.gateway.dev"

# Test Review API
curl -H "Authorization: Bearer $TOKEN" \
  "$GATEWAY_URL/api/review/pending?limit=10"

# Test Graph API
curl -H "Authorization: Bearer $TOKEN" \
  "$GATEWAY_URL/api/graph?limit=10"

# Expected: 200 OK with JSON response
# NOT: 403 Forbidden
```

#### Step 3.2: Test in Browser

1. Open https://aletheiacodex.app
2. Sign in with your account
3. Navigate to Review Queue page
4. Open browser console (F12)
5. Check Network tab:
   - Should see requests to `/api/review/pending`
   - Status should be `200 OK` (not 403)
   - Response should contain data

6. Navigate to Knowledge Graph page
7. Check Network tab:
   - Should see requests to `/api/graph`
   - Status should be `200 OK`
   - Response should contain nodes

#### Step 3.3: Verify Functionality

**Review Queue Page:**
- ✅ Page loads without errors
- ✅ Pending items displayed
- ✅ Can approve/reject items
- ✅ No 403 errors in console

**Knowledge Graph Page:**
- ✅ Page loads without errors
- ✅ Nodes displayed
- ✅ Can search nodes
- ✅ Can view node details
- ✅ No 403 errors in console

### Phase 4: Monitoring & Troubleshooting

#### Monitoring

View API Gateway logs:

```bash
gcloud logging read "resource.type=api AND resource.labels.service=aletheia-codex-api" \
  --project=aletheia-codex-prod \
  --limit=50 \
  --format=json
```

View Cloud Functions logs:

```bash
# Review API logs
gcloud functions logs read review-api-function \
  --region=us-central1 \
  --project=aletheia-codex-prod \
  --limit=50

# Graph API logs
gcloud functions logs read graph-function \
  --region=us-central1 \
  --project=aletheia-codex-prod \
  --limit=50
```

#### Common Issues

**Issue 1: 401 Unauthorized**

**Cause**: Firebase token missing or invalid

**Solution**:
1. Verify user is signed in
2. Check token is being sent in Authorization header
3. Verify token hasn't expired (tokens expire after 1 hour)

**Issue 2: 403 Forbidden**

**Cause**: Service account doesn't have permission to invoke Cloud Functions

**Solution**:
```bash
# Grant Cloud Functions Invoker role to App Engine service account
gcloud functions add-iam-policy-binding review-api-function \
  --region=us-central1 \
  --member="serviceAccount:aletheia-codex-prod@appspot.gserviceaccount.com" \
  --role="roles/cloudfunctions.invoker" \
  --project=aletheia-codex-prod

gcloud functions add-iam-policy-binding graph-function \
  --region=us-central1 \
  --member="serviceAccount:aletheia-codex-prod@appspot.gserviceaccount.com" \
  --role="roles/cloudfunctions.invoker" \
  --project=aletheia-codex-prod
```

**Issue 3: 502 Bad Gateway**

**Cause**: Cloud Function not responding or timing out

**Solution**:
1. Check Cloud Function logs for errors
2. Verify Cloud Function is deployed and active
3. Test Cloud Function directly (if possible)

**Issue 4: CORS Errors**

**Cause**: CORS headers not configured properly

**Solution**:
The Cloud Functions already have CORS headers configured. If issues persist:
1. Verify `Access-Control-Allow-Origin` header in response
2. Check browser console for specific CORS error
3. Ensure preflight OPTIONS requests are handled

**Issue 5: Gateway Not Found**

**Cause**: Gateway deployment failed or not complete

**Solution**:
```bash
# Check gateway status
gcloud api-gateway gateways describe aletheia-codex-gateway \
  --location=us-central1 \
  --project=aletheia-codex-prod

# If state is not ACTIVE, wait a few minutes and check again
# Gateway deployment can take 5-10 minutes
```

## Security Considerations

### Authentication Flow

1. User signs in with Firebase Authentication
2. Frontend gets Firebase ID token
3. Frontend includes token in `Authorization: Bearer TOKEN` header
4. API Gateway validates token using Firebase JWT validation
5. If valid, request is forwarded to Cloud Function
6. Cloud Function receives validated user info

### Service Account Permissions

The App Engine default service account needs:
- `roles/cloudfunctions.invoker` on each Cloud Function
- This allows the gateway to invoke private functions

### Token Validation

API Gateway validates Firebase tokens using:
- Issuer: `https://securetoken.google.com/aletheia-codex-prod`
- JWKS URI: Google's public keys
- Audience: `aletheia-codex-prod`

## Cost Estimation

API Gateway pricing (as of 2024):
- **First 2 million calls/month**: Free
- **Additional calls**: $3.00 per million calls
- **Data transfer**: Standard GCP rates

For development/testing:
- **Expected cost**: $0-5/month
- **Production (low traffic)**: $5-15/month

## Next Steps After Implementation

### Immediate (Sprint 6)
1. ✅ Verify Review Queue page works
2. ✅ Verify Knowledge Graph page works
3. ✅ Continue Sprint 6 development

### Future (Sprint 7+)
1. Migrate to Load Balancer + Identity-Aware Proxy
2. Implement rate limiting
3. Add API monitoring and alerting
4. Set up custom domain for API Gateway

## Rollback Plan

If API Gateway causes issues:

```bash
# Delete gateway
gcloud api-gateway gateways delete aletheia-codex-gateway \
  --location=us-central1 \
  --project=aletheia-codex-prod

# Revert frontend to use direct Cloud Function URLs (if they were working)
# Or request organization policy exception
```

## Success Criteria

✅ API Gateway deployed and active
✅ Review Queue page loads and displays data
✅ Knowledge Graph page loads and displays data
✅ No 403 Forbidden errors
✅ All API calls return 200 OK
✅ User can interact with both pages

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review API Gateway logs
3. Review Cloud Function logs
4. Check browser console for errors
5. Verify Firebase Authentication is working

## References

- [API Gateway Documentation](https://cloud.google.com/api-gateway/docs)
- [OpenAPI 2.0 Specification](https://swagger.io/specification/v2/)
- [Firebase Authentication](https://firebase.google.com/docs/auth)