# Phase 1.3.5 Guide: Update Firebase Hosting Configuration

**Date**: 2024-01-13  
**Sprint**: Security Remediation (Post-Sprint 1)  
**Phase**: 1.3.5 - Update Firebase Hosting Configuration  
**Estimated Duration**: 15 minutes  
**Assigned To**: User (Manual Execution Required)

---

## Objective

Update Firebase Hosting configuration to proxy API requests to the Cloud Run service with the new URL format. The Cloud Run service URL has changed from the Load Balancer URL to the direct Cloud Run URL.

---

## Prerequisites

- [x] Phase 1.3.1 Complete (Organization policy re-enabled)
- [x] Phase 1.3.4 Complete (Cloud Run service updated with `--no-invoker-iam-check`)
- [ ] Access to Cloud Shell or local development environment
- [ ] Authenticated with `gcloud` CLI

---

## Current Configuration

### Current `firebase.json` (Incorrect)
```json
{
  "hosting": {
    "public": "build",
    "rewrites": [
      {
        "source": "/api/review/**",
        "destination": "https://34.120.185.233/api/review/:splat"
      }
    ]
  }
}
```

**Problem**: Points to Load Balancer IP, which is no longer the correct endpoint.

---

## New Configuration Required

### Updated `firebase.json` (Correct)
```json
{
  "hosting": {
    "public": "build",
    "rewrites": [
      {
        "source": "/api/review/**",
        "run": {
          "serviceId": "review-api",
          "region": "us-central1"
        }
      }
    ],
    "ignore": [
      "firebase.json",
      "**/.*",
      "**/node_modules/**"
    ]
  }
}
```

**Key Changes**:
1. Removed `destination` field (external URL)
2. Added `run` field with Cloud Run service details
3. Firebase Hosting will automatically proxy to Cloud Run service

---

## Step-by-Step Instructions

### Step 1: Navigate to Project Directory
```bash
cd ~/aletheia-codex
git checkout sprint-1
git pull origin sprint-1
```

### Step 2: Update `firebase.json`
```bash
cd web
cat > firebase.json << 'EOF'
{
  "hosting": {
    "public": "build",
    "rewrites": [
      {
        "source": "/api/review/**",
        "run": {
          "serviceId": "review-api",
          "region": "us-central1"
        }
      }
    ],
    "ignore": [
      "firebase.json",
      "**/.*",
      "**/node_modules/**"
    ]
  }
}
EOF
```

### Step 3: Verify Configuration
```bash
cat firebase.json
```

**Expected Output**: Should show the new configuration with `run` field

### Step 4: Deploy to Firebase Hosting
```bash
# Build the React app
npm run build

# Deploy to Firebase Hosting
firebase deploy --only hosting --project aletheia-codex-prod
```

**Expected Output**:
```
✔  Deploy complete!

Project Console: https://console.firebase.google.com/project/aletheia-codex-prod/overview
Hosting URL: https://aletheia-codex-prod.web.app
```

### Step 5: Verify Custom Domain
```bash
# Check custom domain status
firebase hosting:sites:list --project aletheia-codex-prod
```

**Expected**: `aletheiacodex.app` should be listed as a custom domain

---

## Verification Steps

### Test 1: Check Firebase Hosting Deployment
```bash
curl -I https://aletheia-codex-prod.web.app
```

**Expected**: HTTP 200 OK

### Test 2: Test API Proxy (Unauthenticated)
```bash
curl -X GET "https://aletheiacodex.app/api/review/pending" \
  -H "Content-Type: application/json" \
  -w "\n\nHTTP Status: %{http_code}\n"
```

**Expected**: 
- HTTP Status: 401 Unauthorized
- Response: `{"error":"Missing Authorization header"}`

**Analysis**: This is CORRECT - the API requires Firebase authentication

### Test 3: Check Custom Domain
```bash
curl -I https://aletheiacodex.app
```

**Expected**: HTTP 200 OK (serves React app)

---

## Firebase Hosting Rewrite Behavior

### How Firebase Hosting Proxies to Cloud Run

When using the `run` field in `firebase.json`:

1. **Request Flow**:
   ```
   User → https://aletheiacodex.app/api/review/pending
        → Firebase Hosting (recognizes /api/review/** pattern)
        → Proxies to Cloud Run service "review-api" in us-central1
        → Cloud Run service receives request
        → Returns response to Firebase Hosting
        → Firebase Hosting returns response to user
   ```

2. **Automatic Features**:
   - Firebase Hosting automatically handles SSL/TLS
   - Preserves request headers (including Authorization)
   - Maintains request path and query parameters
   - Handles CORS properly
   - No need for explicit URL configuration

3. **Benefits**:
   - No hardcoded URLs
   - Automatic service discovery
   - Better integration with Firebase ecosystem
   - Simplified configuration

---

## Troubleshooting

### Issue 1: "Service not found" Error
**Symptom**: Firebase Hosting returns 404 for API requests

**Solution**:
```bash
# Verify Cloud Run service exists
gcloud run services list --region=us-central1 --project=aletheia-codex-prod

# Verify service name matches firebase.json
gcloud run services describe review-api --region=us-central1 --project=aletheia-codex-prod
```

### Issue 2: CORS Errors in Browser
**Symptom**: Browser console shows CORS errors

**Solution**: Check that Cloud Run service has proper CORS headers configured in `main.py`:
```python
ALLOWED_ORIGINS = [
    'https://aletheia-codex-prod.web.app',
    'https://aletheiacodex.app',
    'http://localhost:3000'
]
```

### Issue 3: 403 Forbidden Errors
**Symptom**: API returns 403 instead of 401

**Solution**: Verify `--no-invoker-iam-check` is applied:
```bash
gcloud run services describe review-api \
  --region=us-central1 \
  --project=aletheia-codex-prod \
  --format="value(metadata.annotations.'run.googleapis.com/ingress')"
```

---

## Rollback Plan

If deployment fails or causes issues:

```bash
# Revert to previous firebase.json
git checkout HEAD~1 -- firebase.json

# Redeploy
npm run build
firebase deploy --only hosting --project aletheia-codex-prod
```

---

## Success Criteria

- [ ] `firebase.json` updated with `run` field
- [ ] Firebase Hosting deployed successfully
- [ ] Custom domain `aletheiacodex.app` accessible
- [ ] API requests return 401 (not 403 or 500)
- [ ] React app loads correctly
- [ ] No CORS errors in browser console

---

## Next Steps

After completing Phase 1.3.5:
1. Proceed to **Phase 1.3.6**: Frontend Testing with Authentication
2. Test authenticated API calls from browser
3. Verify complete user flow (login → API calls → data display)

---

## Notes

- Firebase Hosting automatically handles SSL certificates for custom domains
- The `run` field is the recommended way to proxy to Cloud Run services
- No need to expose Cloud Run URLs publicly - Firebase Hosting handles the proxy
- All authentication headers are preserved during proxying

---

**Created By**: Architect (SuperNinja AI Agent)  
**Date**: 2024-01-13  
**Status**: Ready for Execution