# Runbook: Phase 1.3.5 - Update Firebase Hosting Configuration

**Phase**: 1.3.5  
**Objective**: Update Firebase Hosting to proxy API requests to Cloud Run service  
**Estimated Duration**: 15 minutes  
**Prerequisites**: Phase 1.3.4 complete (Cloud Run service updated with `--no-invoker-iam-check`)

---

## Overview

This runbook guides you through updating the Firebase Hosting configuration to properly proxy API requests to the Cloud Run service. The current configuration points to an incorrect Load Balancer URL and needs to be updated to use the Cloud Run service directly.

---

## Prerequisites Checklist

- [ ] Phase 1.3.4 complete (Cloud Run service has `--no-invoker-iam-check` applied)
- [ ] Access to Cloud Shell or local development environment
- [ ] Authenticated with `gcloud` CLI
- [ ] Firebase CLI installed (`firebase --version`)
- [ ] Access to `sprint-1` branch

---

## Step 1: Authenticate and Setup

### 1.1 Authenticate with GCP
```bash
gcloud auth login
gcloud config set project aletheia-codex-prod
```

**Expected Output**: "You are now logged in as [your-email]"

### 1.2 Authenticate with Firebase
```bash
firebase login
```

**Expected Output**: "Success! Logged in as [your-email]"

### 1.3 Navigate to Project
```bash
cd ~/aletheia-codex
git checkout sprint-1
git pull origin sprint-1
cd web
```

**Expected Output**: "Already on 'sprint-1'" or "Switched to branch 'sprint-1'"

---

## Step 2: Backup Current Configuration

### 2.1 Create Backup
```bash
cp firebase.json firebase.json.backup
```

### 2.2 View Current Configuration
```bash
cat firebase.json
```

**Expected Output**: Should show current configuration (likely pointing to Load Balancer)

---

## Step 3: Update Firebase Configuration

### 3.1 Create New Configuration
```bash
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

### 3.2 Verify New Configuration
```bash
cat firebase.json
```

**Expected Output**: Should show the new configuration with `run` field

**Validation Checklist**:
- [ ] `"run"` field is present
- [ ] `"serviceId": "review-api"` is correct
- [ ] `"region": "us-central1"` is correct
- [ ] No `"destination"` field (old format)

---

## Step 4: Build React Application

### 4.1 Install Dependencies (if needed)
```bash
npm install
```

**Expected Output**: "up to date" or "added X packages"

### 4.2 Build Application
```bash
npm run build
```

**Expected Output**: 
```
Creating an optimized production build...
Compiled successfully.
```

**Validation**:
- [ ] Build completed without errors
- [ ] `build/` directory exists
- [ ] `build/index.html` exists

---

## Step 5: Deploy to Firebase Hosting

### 5.1 Deploy Hosting Configuration
```bash
firebase deploy --only hosting --project aletheia-codex-prod
```

**Expected Output**:
```
=== Deploying to 'aletheia-codex-prod'...

i  deploying hosting
i  hosting[aletheia-codex-prod]: beginning deploy...
i  hosting[aletheia-codex-prod]: found X files in build
✔  hosting[aletheia-codex-prod]: file upload complete
i  hosting[aletheia-codex-prod]: finalizing version...
✔  hosting[aletheia-codex-prod]: version finalized
i  hosting[aletheia-codex-prod]: releasing new version...
✔  hosting[aletheia-codex-prod]: release complete

✔  Deploy complete!

Project Console: https://console.firebase.google.com/project/aletheia-codex-prod/overview
Hosting URL: https://aletheia-codex-prod.web.app
```

**Validation Checklist**:
- [ ] Deploy completed successfully
- [ ] No errors in output
- [ ] Hosting URL displayed

---

## Step 6: Verification Tests

### 6.1 Test Firebase Hosting URL
```bash
curl -I https://aletheia-codex-prod.web.app
```

**Expected Output**: `HTTP/2 200`

### 6.2 Test Custom Domain
```bash
curl -I https://aletheiacodex.app
```

**Expected Output**: `HTTP/2 200`

### 6.3 Test API Proxy (Unauthenticated)
```bash
curl -X GET "https://aletheiacodex.app/api/review/pending" \
  -H "Content-Type: application/json" \
  -w "\n\nHTTP Status: %{http_code}\n"
```

**Expected Output**:
```json
{"error":"Missing Authorization header"}

HTTP Status: 401
```

**Analysis**: This is CORRECT - the API requires Firebase authentication

### 6.4 Verify Cloud Run Service URL
```bash
gcloud run services describe review-api \
  --region=us-central1 \
  --format="value(status.url)"
```

**Expected Output**: `https://review-api-h55nns6ojq-uc.a.run.app`

---

## Step 7: Browser Testing

### 7.1 Open Application in Browser
```bash
# Open in browser (or manually navigate)
echo "Open: https://aletheiacodex.app"
```

### 7.2 Check Browser Console
1. Open browser developer tools (F12)
2. Navigate to Console tab
3. Look for any errors

**Expected**: No CORS errors, no 403 errors

### 7.3 Check Network Tab
1. Open Network tab in developer tools
2. Refresh the page
3. Look for API requests to `/api/review/*`

**Expected**: 
- Requests go to `https://aletheiacodex.app/api/review/*`
- Status: 401 (if not logged in) or 200 (if logged in)
- No 403 Forbidden errors

---

## Step 8: Commit Changes

### 8.1 Stage Changes
```bash
cd ~/aletheia-codex/web
git add firebase.json
```

### 8.2 Commit Changes
```bash
git commit -m "fix(hosting): update Firebase Hosting to proxy to Cloud Run service

- Changed from Load Balancer URL to Cloud Run service proxy
- Updated firebase.json to use 'run' field with serviceId
- Removed hardcoded destination URL
- Enables automatic Cloud Run service discovery"
```

### 8.3 Push Changes
```bash
git push origin sprint-1
```

**Expected Output**: "Writing objects: 100%"

---

## Troubleshooting

### Issue 1: "Service not found" Error

**Symptom**: Firebase Hosting returns 404 for API requests

**Diagnosis**:
```bash
# Verify Cloud Run service exists
gcloud run services list --region=us-central1 --project=aletheia-codex-prod | grep review-api
```

**Solution**: Ensure service name in `firebase.json` matches exactly: `review-api`

---

### Issue 2: CORS Errors in Browser

**Symptom**: Browser console shows CORS errors

**Diagnosis**: Check Cloud Run service CORS configuration

**Solution**: Verify `main.py` has correct CORS headers:
```python
ALLOWED_ORIGINS = [
    'https://aletheia-codex-prod.web.app',
    'https://aletheiacodex.app',
    'http://localhost:3000'
]
```

---

### Issue 3: 403 Forbidden Errors

**Symptom**: API returns 403 instead of 401

**Diagnosis**:
```bash
# Check if --no-invoker-iam-check is applied
gcloud run services describe review-api \
  --region=us-central1 \
  --format="value(metadata.annotations)" | grep invoker-iam-disabled
```

**Expected Output**: `run.googleapis.com/invoker-iam-disabled=true`

**Solution**: If not present, re-run Phase 1.3.4

---

### Issue 4: Build Fails

**Symptom**: `npm run build` fails with errors

**Diagnosis**: Check error message

**Common Solutions**:
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
npm run build
```

---

### Issue 5: Deploy Fails

**Symptom**: `firebase deploy` fails

**Diagnosis**: Check error message

**Common Solutions**:
```bash
# Re-authenticate
firebase login --reauth

# Verify project
firebase projects:list

# Try deploy again
firebase deploy --only hosting --project aletheia-codex-prod
```

---

## Rollback Plan

If deployment causes issues:

### Rollback Step 1: Restore Backup
```bash
cd ~/aletheia-codex/web
cp firebase.json.backup firebase.json
```

### Rollback Step 2: Redeploy
```bash
npm run build
firebase deploy --only hosting --project aletheia-codex-prod
```

### Rollback Step 3: Verify
```bash
curl -I https://aletheiacodex.app
```

---

## Success Criteria

- [ ] `firebase.json` updated with `run` field
- [ ] Firebase Hosting deployed successfully
- [ ] Custom domain `aletheiacodex.app` accessible (HTTP 200)
- [ ] API requests return 401 (not 403 or 500)
- [ ] React app loads correctly in browser
- [ ] No CORS errors in browser console
- [ ] Changes committed to `sprint-1` branch

---

## Post-Deployment Validation

### Validation Checklist

1. **Application Loads**:
   - [ ] Navigate to `https://aletheiacodex.app`
   - [ ] Page loads without errors
   - [ ] No console errors

2. **API Routing**:
   - [ ] API requests go to `/api/review/*`
   - [ ] Requests return 401 (unauthenticated) or 200 (authenticated)
   - [ ] No 403 Forbidden errors

3. **Authentication Flow**:
   - [ ] Login page accessible
   - [ ] Can sign in with Firebase Auth
   - [ ] After login, API requests include Authorization header

4. **Custom Domain**:
   - [ ] `aletheiacodex.app` resolves correctly
   - [ ] SSL certificate valid
   - [ ] No redirect loops

---

## Next Steps

After completing Phase 1.3.5:

1. **Proceed to Phase 1.3.6**: Frontend Testing with Authentication
   - Test authenticated API calls from browser
   - Verify complete user flow (login → API calls → data display)
   - Validate all features work end-to-end

2. **Document Results**: Update status report with Phase 1.3.5 completion

---

## Notes

- Firebase Hosting automatically handles SSL certificates for custom domains
- The `run` field is the recommended way to proxy to Cloud Run services
- No need to expose Cloud Run URLs publicly - Firebase Hosting handles the proxy
- All authentication headers are preserved during proxying
- Firebase Hosting caches static assets but not API responses

---

## Reference Documentation

- [Firebase Hosting Rewrites](https://firebase.google.com/docs/hosting/full-config#rewrites)
- [Cloud Run Integration](https://firebase.google.com/docs/hosting/cloud-run)
- [Custom Domain Setup](https://firebase.google.com/docs/hosting/custom-domain)

---

**Created By**: Architect (SuperNinja AI Agent)  
**Date**: 2024-01-13  
**Phase**: 1.3.5  
**Status**: Ready for Execution