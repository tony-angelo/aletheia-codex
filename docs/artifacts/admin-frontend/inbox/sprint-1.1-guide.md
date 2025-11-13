# Sprint 1.1 Guide - Firebase Hosting Configuration Fix (Frontend)

**Sprint**: 1.1 (Remediation)  
**Node**: Admin-Frontend  
**Priority**: CRITICAL  
**Estimated Time**: 30 minutes  
**Status**: Ready to Start  

---

## Mission

**Fix Firebase Hosting configuration to properly serve the React application and proxy API calls to the Load Balancer.**

This is a continuation of Sprint 1. Admin-Infrastructure has successfully disabled IAP, but the application is now showing "Error: Forbidden" because Firebase Hosting is incorrectly configured.

---

## Context

### Current Problem

**Error shown:** "Error: Forbidden - Your client does not have permission to get URL / from this server"

**Root cause:** Firebase Hosting is trying to proxy the root path `/` to the Load Balancer, but the Load Balancer doesn't have a backend for `/`. The Load Balancer only handles `/api/*` paths.

### What Should Happen

```
User requests /           → Firebase Hosting serves React app (index.html)
User requests /api/graph  → Firebase Hosting proxies to Load Balancer
```

### What's Happening Now

```
User requests /           → Firebase Hosting tries to proxy to Load Balancer → 403 Error
User requests /api/graph  → Firebase Hosting proxies to Load Balancer → Should work
```

---

## Your Tasks

### Task 1: Review Current Firebase Configuration (5 minutes)

**Objective**: Understand the current firebase.json configuration

**Steps:**

1. **Checkout sprint-1 branch**
   ```bash
   cd aletheia-codex
   git checkout sprint-1
   git pull origin sprint-1
   ```

2. **Review firebase.json**
   ```bash
   cat firebase.json
   ```

3. **Identify the issue**
   - Look at the `hosting.rewrites` section
   - Check the order of rewrite rules
   - Verify the `/api/**` rule comes BEFORE the `**` rule

### Task 2: Fix Firebase Hosting Configuration (10 minutes)

**Objective**: Correct the rewrite rules to serve React app and proxy API calls

**Steps:**

1. **Edit firebase.json**

   The `hosting.rewrites` section should look like this:

   ```json
   "rewrites": [
     {
       "source": "/api/**",
       "destination": "https://aletheiacodex.app/api/:splat"
     },
     {
       "source": "**",
       "destination": "/index.html"
     }
   ]
   ```

   **Critical:** The `/api/**` rule MUST come BEFORE the `**` rule!

2. **Verify the fix**
   ```bash
   cat firebase.json | grep -A 10 "rewrites"
   ```

3. **Check for other issues**
   - Ensure `public` points to `web/build`
   - Verify `site` is set to `aletheia-codex-prod`
   - Check that CORS headers are still present

### Task 3: Build and Deploy (10 minutes)

**Objective**: Deploy the fixed configuration to Firebase Hosting

**Steps:**

1. **Authenticate with Firebase**
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="/workspace/aletheia-codex-prod-af9a64a7fcaa.json"
   ```

2. **Build the React application** (if needed)
   ```bash
   cd web
   npm install
   npm run build
   cd ..
   ```

3. **Deploy to Firebase Hosting**
   ```bash
   firebase deploy --only hosting
   ```

4. **Note the deployment URL**
   - Should be: `https://aletheia-codex-prod.web.app`

### Task 4: Test and Verify (5 minutes)

**Objective**: Verify the application is now accessible

**Steps:**

1. **Clear browser cache**
   - Open browser in incognito/private mode
   - Or clear cache and hard reload

2. **Test root path**
   ```bash
   curl -I https://aletheia-codex-prod.web.app
   ```
   **Expected:** HTTP 200 with HTML content

3. **Test in browser**
   - Open https://aletheia-codex-prod.web.app
   - Should see React application UI
   - Should NOT see "Error: Forbidden"

4. **Test API proxy** (optional)
   ```bash
   curl -I https://aletheia-codex-prod.web.app/api/graph
   ```
   **Expected:** HTTP 401 (unauthorized - needs Firebase token)

5. **Test Firebase Auth login**
   - Try to log in with Google or email/password
   - Verify login works
   - Check that authenticated requests work

---

## Expected firebase.json Configuration

Here's what your `firebase.json` should look like:

```json
{
  "firestore": {
    "database": "(default)",
    "location": "nam5",
    "rules": "firestore.rules",
    "indexes": "firestore.indexes.json"
  },
  "functions": [
    {
      "source": "functions",
      "codebase": "default",
      "disallowLegacyRuntimeConfig": true,
      "ignore": [
        "node_modules",
        ".git",
        "firebase-debug.log",
        "firebase-debug.*.log",
        "*.local"
      ],
      "predeploy": [
        "npm --prefix &quot;$RESOURCE_DIR&quot; run lint",
        "npm --prefix &quot;$RESOURCE_DIR&quot; run build"
      ]
    }
  ],
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
        "source": "/api/**",
        "destination": "https://aletheiacodex.app/api/:splat"
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
  },
  "storage": {
    "rules": "storage.rules"
  }
}
```

**Key points:**
- `/api/**` rewrite comes FIRST
- `**` rewrite comes SECOND (serves index.html for all other paths)
- CORS headers are present for API calls

---

## Success Criteria

- [ ] firebase.json rewrites corrected (API rule before catch-all)
- [ ] React app builds successfully
- [ ] Deployed to Firebase Hosting
- [ ] Root path (/) serves React app (not 403 error)
- [ ] Application UI loads in browser
- [ ] Firebase Auth login works
- [ ] API calls are proxied to Load Balancer
- [ ] Documentation created
- [ ] Changes committed to sprint-1 branch

---

## Common Issues & Solutions

### Issue 1: Still seeing "Error: Forbidden"

**Causes:**
- Browser cache
- Firebase Hosting cache
- Rewrite rules in wrong order

**Solutions:**
```bash
# Clear browser cache or use incognito mode
# Wait 1-2 minutes for Firebase Hosting cache to clear
# Verify rewrite rules order in firebase.json
```

### Issue 2: API calls not working

**Symptoms:** API calls return 404 or CORS errors

**Solution:**
- Verify `/api/**` rewrite is present
- Check that destination URL is correct: `https://aletheiacodex.app/api/:splat`
- Verify CORS headers are present

### Issue 3: React app not loading

**Symptoms:** Blank page or 404 errors

**Solutions:**
```bash
# Verify build directory exists
ls -la web/build/

# Rebuild if needed
cd web && npm run build && cd ..

# Verify firebase.json public path
grep "public" firebase.json
# Should show: "public": "web/build"
```

### Issue 4: Firebase deploy fails

**Symptoms:** Authentication errors or permission denied

**Solutions:**
```bash
# Re-authenticate
export GOOGLE_APPLICATION_CREDENTIALS="/workspace/aletheia-codex-prod-af9a64a7fcaa.json"

# Verify project
firebase projects:list

# Use specific project
firebase use aletheia-codex-prod
```

---

## Testing Checklist

After deployment, verify:

- [ ] https://aletheia-codex-prod.web.app loads React app
- [ ] No "Error: Forbidden" message
- [ ] Can see login screen or application UI
- [ ] Firebase Auth login works
- [ ] Can navigate between pages
- [ ] API calls work (check browser console)
- [ ] No CORS errors in console

---

## Documentation

### Create: `web/FIREBASE-HOSTING-FIX.md`

```markdown
# Firebase Hosting Configuration Fix - Sprint 1.1

**Date**: 2025-01-18  
**Issue**: Error: Forbidden on root path  
**Cause**: Incorrect rewrite rule order in firebase.json  

## Problem

Firebase Hosting was trying to proxy the root path `/` to the Load Balancer, which doesn't have a backend for `/`. This caused a 403 Forbidden error.

## Solution

Fixed the rewrite rules order in firebase.json:

1. `/api/**` → Proxy to Load Balancer (https://aletheiacodex.app)
2. `**` → Serve React app (index.html)

The API rule must come BEFORE the catch-all rule.

## Changes Made

- Updated firebase.json rewrites section
- Verified CORS headers present
- Rebuilt React application
- Deployed to Firebase Hosting

## Verification

- Root path serves React app: ✅
- API calls proxied to Load Balancer: ✅
- Firebase Auth works: ✅
- No 403 errors: ✅

## Architecture

```
User → Firebase Hosting → React App (for /)
                        → Load Balancer (for /api/*)
                        → Cloud Functions
                        → Firebase Auth validation
```
```

---

## Commit Changes

```bash
git add firebase.json web/FIREBASE-HOSTING-FIX.md
git commit -m "fix(hosting): correct Firebase Hosting rewrite rules order

- Move /api/** rewrite before catch-all rule
- Fixes 403 Forbidden error on root path
- React app now serves correctly from Firebase Hosting
- API calls properly proxied to Load Balancer
- Sprint 1.1 remediation complete"

git push origin sprint-1
```

---

## References

- **Sprint 1.1 Overview**: `[artifacts]/architect/sprint-1.1-overview.md`
- **ADR-001**: `[artifacts]/architect/adr-001-remove-iap.md`
- **Firebase Hosting Docs**: https://firebase.google.com/docs/hosting/full-config

---

## Next Steps

After you complete this work:
1. Create session log in `[artifacts]/admin-frontend/outbox/session-log-sprint-1.1.md`
2. Report completion to Architect
3. Architect will validate and close Sprint 1.1

---

**This is the final fix needed to restore application access.**

---

**Architect**  
AletheiaCodex Project  
Sprint 1.1 Remediation  
2025-01-18