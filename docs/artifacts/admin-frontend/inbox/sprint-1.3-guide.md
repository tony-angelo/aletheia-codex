# Sprint 1.3 Guide: Update Firebase Hosting for Cloud Run

**Sprint**: 1.3  
**Domain**: Frontend  
**Admin Node**: Admin-Frontend  
**Priority**: 🚨 CRITICAL  
**Estimated Duration**: 1 hour  
**Branch**: `sprint-1.3` (use existing branch from Admin-Infrastructure)

---

## Sprint Goal

Update Firebase Hosting configuration to use Cloud Run services instead of Cloud Functions, enabling functional API endpoints.

---

## Prerequisites

### Required from Admin-Infrastructure
- ✅ All 4 Cloud Run services deployed
- ✅ Service URLs documented
- ✅ Handoff document created

**Wait for Admin-Infrastructure to complete their work before starting.**

---

## Problem Statement

### Current Issue
- Firebase Hosting rewrites point to Cloud Functions
- Cloud Functions are blocked by organization policy (403 Forbidden)
- All API endpoints are non-functional

### Solution
Update Firebase Hosting rewrites to use Cloud Run services which:
- Are NOT blocked by organization policy
- Support public access
- Work with Firebase Hosting rewrites

---

## Tasks

### 1. Get Cloud Run Service Information

**Read**: `docs/artifacts/admin-infrastructure/outbox/cloud-run-handoff.md`

**Extract**:
- Review API service name and region
- Graph API service name and region
- Notes API service name and region
- Orchestration API service name and region

**Expected Information**:
```
review-api (us-central1)
graph-api (us-central1)
notes-api (us-central1)
orchestration-api (us-central1)
```

**Action**:
- [ ] Read handoff document
- [ ] Note down all service names and regions

---

### 2. Checkout Sprint 1.3 Branch

```bash
cd /workspace/aletheia-codex
git checkout sprint-1.3
git pull origin sprint-1.3
```

**Action**:
- [ ] Checkout sprint-1.3 branch
- [ ] Pull latest changes from Admin-Infrastructure

---

### 3. Update firebase.json Configuration

**File**: `firebase.json`

**Current Configuration** (Broken):
```json
{
  "hosting": {
    "rewrites": [
      {
        "source": "/api/review/**",
        "function": "reviewapifunction"
      },
      {
        "source": "/api/graph/**",
        "function": "graphfunction"
      },
      {
        "source": "/api/notes/**",
        "function": "notesapifunction"
      },
      {
        "source": "**",
        "destination": "/index.html"
      }
    ]
  }
}
```

**New Configuration** (Working):
```json
{
  "hosting": {
    "public": "web/build",
    "site": "aletheia-codex-prod",
    "ignore": [
      "firebase.json",
      "**/.*",
      "**/node_modules/**"
    ],
    "rewrites": [
      {
        "source": "/api/review/**",
        "run": {
          "serviceId": "review-api",
          "region": "us-central1"
        }
      },
      {
        "source": "/api/graph/**",
        "run": {
          "serviceId": "graph-api",
          "region": "us-central1"
        }
      },
      {
        "source": "/api/notes/**",
        "run": {
          "serviceId": "notes-api",
          "region": "us-central1"
        }
      },
      {
        "source": "/api/orchestration/**",
        "run": {
          "serviceId": "orchestration-api",
          "region": "us-central1"
        }
      },
      {
        "source": "**",
        "destination": "/index.html"
      }
    ],
    "headers": [
      {
        "source": "/api/**",
        "headers": [
          {
            "key": "Access-Control-Allow-Origin",
            "value": "https://aletheiacodex.app"
          },
          {
            "key": "Access-Control-Allow-Methods",
            "value": "GET, POST, PUT, DELETE, OPTIONS"
          },
          {
            "key": "Access-Control-Allow-Headers",
            "value": "Content-Type, Authorization"
          },
          {
            "key": "Access-Control-Max-Age",
            "value": "3600"
          }
        ]
      }
    ]
  }
}
```

**Key Changes**:
- Changed from `"function": "functionname"` to `"run": { "serviceId": "...", "region": "..." }`
- Added orchestration API rewrite
- Kept CORS headers configuration

**Action**:
- [ ] Open `firebase.json`
- [ ] Replace the entire `hosting` section with the new configuration
- [ ] Verify all 4 Cloud Run services are included
- [ ] Save the file

---

### 4. Build Frontend (if needed)

```bash
cd /workspace/aletheia-codex/web

# Check if build directory exists and is recent
ls -la build/

# If build is old or missing, rebuild
npm run build
```

**Action**:
- [ ] Check if build exists
- [ ] Rebuild if necessary
- [ ] Verify build completes successfully

---

### 5. Deploy Firebase Hosting

```bash
cd /workspace/aletheia-codex

# Set credentials
export GOOGLE_APPLICATION_CREDENTIALS=/workspace/aletheia-codex-prod-af9a64a7fcaa.json

# Deploy hosting only
firebase deploy --only hosting --project aletheia-codex-prod
```

**Expected Output**:
```
✔ Deploy complete!

Project Console: https://console.firebase.google.com/project/aletheia-codex-prod/overview
Hosting URL: https://aletheia-codex-prod.web.app
```

**Action**:
- [ ] Run deployment command
- [ ] Verify deployment successful
- [ ] Note deployment time

---

### 6. Test API Endpoints

#### 6.1 Test Through Firebase Hosting

```bash
# Test Review API
curl https://aletheiacodex.app/api/review/pending

# Test Graph API
curl https://aletheiacodex.app/api/graph/data

# Test Notes API
curl https://aletheiacodex.app/api/notes/list

# Test Orchestration API
curl https://aletheiacodex.app/api/orchestration/status
```

**Expected Response** (for each):
```json
{
  "success": true,
  "message": "API is working",
  "timestamp": "2025-01-13T..."
}
```

**NOT**:
```html
<!doctype html>
<html>
  <head>
    <title>Page Not Found</title>
  </head>
  ...
</html>
```

**Action**:
- [ ] Test all 4 API endpoints
- [ ] Verify JSON responses (not HTML)
- [ ] Verify no 403 Forbidden errors
- [ ] Verify no 404 Not Found errors

---

#### 6.2 Test in Browser

**Steps**:
1. Open browser to `https://aletheiacodex.app`
2. Open DevTools → Network tab
3. Log in with test credentials:
   - Email: `sprint1@domain.com`
   - Password: `Password1234!`
4. Navigate to Review page
5. Check Network tab for API calls

**Expected**:
- ✅ API calls to `/api/review/pending` return 200 OK
- ✅ Response is JSON (not HTML)
- ✅ Review page loads and displays data
- ✅ No console errors

**Action**:
- [ ] Test in browser
- [ ] Verify API calls successful
- [ ] Verify Review page works
- [ ] Take screenshots of successful API calls

---

### 7. End-to-End Testing

#### 7.1 User Authentication
- [ ] Log in with test credentials
- [ ] Verify authentication works
- [ ] Check Firebase Auth token is sent

#### 7.2 Review Page
- [ ] Navigate to Review page
- [ ] Verify pending items load
- [ ] Test approve/reject functionality
- [ ] Verify batch operations work

#### 7.3 Other Pages
- [ ] Test Dashboard
- [ ] Test Knowledge Graph (if accessible)
- [ ] Test Notes (if accessible)
- [ ] Test Settings

**Action**:
- [ ] Complete all end-to-end tests
- [ ] Document any issues
- [ ] Verify all functionality works

---

### 8. Commit and Push Changes

```bash
cd /workspace/aletheia-codex

# Add firebase.json
git add firebase.json

# Commit
git commit -m "feat(frontend): update Firebase Hosting to use Cloud Run services

- Change rewrites from Cloud Functions to Cloud Run services
- Add orchestration API rewrite
- Keep CORS headers configuration

Firebase Hosting now rewrites to:
- review-api (Cloud Run)
- graph-api (Cloud Run)
- notes-api (Cloud Run)
- orchestration-api (Cloud Run)

Tested and verified:
- All API endpoints return JSON (not HTML)
- No 403 Forbidden errors
- No 404 Not Found errors
- Review page fully functional

Resolves Sprint 1.3 - Cloud Run migration (Frontend)"

# Push
git push origin sprint-1.3
```

**Action**:
- [ ] Commit changes
- [ ] Push to GitHub
- [ ] Verify push successful

---

### 9. Create Session Log

**File**: `docs/artifacts/admin-frontend/outbox/sprint-1.3-session-log.md`

Document:
- Configuration changes made
- Deployment results
- Testing results (curl and browser)
- Screenshots of successful API calls
- Any issues encountered
- Time spent on each task

**Action**:
- [ ] Create session log
- [ ] Commit to artifacts branch
- [ ] Push to GitHub

---

### 10. Create Completion Summary

**File**: `SPRINT_1.3_COMPLETION_SUMMARY.md`

```markdown
# Sprint 1.3 Completion Summary - Frontend

## Status
✅ COMPLETE

## Changes Made

### Firebase Hosting Configuration
- Updated `firebase.json` to use Cloud Run services
- Changed from Cloud Functions to Cloud Run rewrites
- Added orchestration API rewrite

### Deployment
- Deployed updated Firebase Hosting configuration
- Verified deployment successful

## Testing Results

### API Endpoints
- ✅ Review API: Working (returns JSON)
- ✅ Graph API: Working (returns JSON)
- ✅ Notes API: Working (returns JSON)
- ✅ Orchestration API: Working (returns JSON)

### Browser Testing
- ✅ User authentication works
- ✅ Review page loads and displays data
- ✅ No console errors
- ✅ No 403 Forbidden errors
- ✅ No 404 Not Found errors

## Application Status

**The AletheiaCodex application is now FULLY FUNCTIONAL:**
- ✅ Accessible at https://aletheiacodex.app
- ✅ User authentication working
- ✅ All API endpoints returning JSON
- ✅ Review page functional
- ✅ No errors in browser console

## Next Steps

- Monitor application for any issues
- Verify all features work as expected
- Consider merging sprint-1.3 to main

## Time Spent

- Configuration: 15 minutes
- Deployment: 10 minutes
- Testing: 25 minutes
- Documentation: 10 minutes
- **Total**: ~1 hour
```

**Action**:
- [ ] Create completion summary
- [ ] Commit to sprint-1.3 branch
- [ ] Push to GitHub

---

## Success Criteria

### Must Have ✅
- [ ] `firebase.json` updated with Cloud Run rewrites
- [ ] Firebase Hosting deployed successfully
- [ ] All API endpoints return JSON (not HTML)
- [ ] No 403 Forbidden errors
- [ ] No 404 Not Found errors
- [ ] Review page loads and displays data
- [ ] User authentication works
- [ ] Session log created
- [ ] Changes committed and pushed

### Should Have 📋
- [ ] Browser testing completed
- [ ] Screenshots of successful API calls
- [ ] Completion summary created

### Nice to Have 🎯
- [ ] Performance benchmarks
- [ ] Load testing results

---

## Troubleshooting

### Issue: Deployment Fails
**Solution**: Check Firebase CLI authentication, verify project ID, check build directory

### Issue: API Endpoints Return 404
**Solution**: Verify Cloud Run service names match exactly, check region is correct

### Issue: API Endpoints Return 403
**Solution**: Verify Cloud Run services have `--allow-unauthenticated` flag

### Issue: CORS Errors
**Solution**: Verify CORS headers in `firebase.json`, check Cloud Run service CORS configuration

---

## Escalation Triggers

Escalate to Architect if:
1. **Deployment Failures**: Cannot deploy Firebase Hosting
2. **API Errors**: API endpoints still return errors after deployment
3. **Authentication Issues**: Firebase Auth not working with Cloud Run
4. **CORS Issues**: Cross-origin errors persist
5. **Unexpected Behavior**: Application behaves differently than expected

**Escalation Process**:
1. Document the issue in `docs/artifacts/admin-frontend/escalations/sprint-1.3-blocker.md`
2. Include error messages, screenshots, and attempted solutions
3. Notify Architect via inbox message

---

## Timeline

- **Minute 0-15**: Update firebase.json configuration
- **Minute 15-25**: Deploy Firebase Hosting
- **Minute 25-50**: Test API endpoints and browser functionality
- **Minute 50-60**: Documentation and commit

**Total Estimated Time**: 1 hour

---

**Created**: 2025-01-13  
**Author**: Architect  
**Status**: Ready for Execution (after Admin-Infrastructure completes)  
**Priority**: 🚨 CRITICAL