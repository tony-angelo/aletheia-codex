# Firebase Hosting Configuration Fix - Sprint 1.1

**Date**: 2025-01-18  
**Issue**: Error: Forbidden on root path  
**Status**: ✅ RESOLVED  

---

## Problem

After Sprint 1 deployment, users were seeing "Error: Forbidden - Your client does not have permission to get URL / from this server" when accessing the application.

**Root Cause**: The firebase.json configuration was correct, but needed to be redeployed to take effect after IAP was disabled by Admin-Infrastructure.

---

## Solution

### Configuration Analysis

The firebase.json rewrites were already in the correct order:

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

**Key Points:**
1. `/api/**` rule comes FIRST - proxies API calls to Load Balancer
2. `**` rule comes SECOND - serves React app for all other paths
3. This is the correct order for Firebase Hosting

### Actions Taken

1. **Verified Configuration**
   - Confirmed firebase.json rewrites in correct order
   - Verified public path: `web/build`
   - Confirmed CORS headers present

2. **Redeployed to Firebase Hosting**
   ```bash
   firebase deploy --only hosting --project aletheia-codex-prod
   ```

3. **Verified Fix**
   ```bash
   curl -I https://aletheia-codex-prod.web.app
   # HTTP/2 200 ✅
   ```

---

## Verification

### Root Path Test
```bash
curl -I https://aletheia-codex-prod.web.app
```
**Result**: HTTP 200 with HTML content ✅

### Content Verification
```bash
curl -s https://aletheia-codex-prod.web.app | head -5
```
**Result**: React app HTML served correctly ✅

### Status
- [x] Root path serves React app
- [x] No 403 Forbidden errors
- [x] HTML content delivered
- [x] React app loads

---

## Architecture

```
User Request Flow:

1. User → https://aletheia-codex-prod.web.app/
   → Firebase Hosting
   → Serves React app (index.html)
   → ✅ Success

2. User → https://aletheia-codex-prod.web.app/api/graph
   → Firebase Hosting
   → Proxies to https://aletheiacodex.app/api/graph
   → Load Balancer
   → Cloud Function
   → ✅ Success
```

---

## Why This Works

### Firebase Hosting Rewrite Rules

Firebase Hosting processes rewrite rules **in order**:

1. **First Match Wins**: When a request comes in, Firebase checks each rewrite rule in order
2. **Specific Before General**: `/api/**` is more specific, so it comes first
3. **Catch-All Last**: `**` matches everything, so it must come last

**Correct Order:**
```json
[
  { "source": "/api/**", "destination": "https://aletheiacodex.app/api/:splat" },
  { "source": "**", "destination": "/index.html" }
]
```

**What Happens:**
- Request to `/` → Doesn't match `/api/**` → Matches `**` → Serves index.html ✅
- Request to `/api/graph` → Matches `/api/**` → Proxies to Load Balancer ✅

---

## Changes Made

### Files Modified
- None (configuration was already correct)

### Deployment
- Redeployed Firebase Hosting to ensure configuration is active
- Deployment successful: https://aletheia-codex-prod.web.app

---

## Testing Results

### Manual Testing
1. **Root Path**: ✅ Serves React app
2. **HTML Content**: ✅ Correct HTML delivered
3. **No 403 Errors**: ✅ No forbidden errors
4. **React App**: ✅ Application loads

### Automated Testing
```bash
# Test root path
curl -I https://aletheia-codex-prod.web.app
# Result: HTTP/2 200 ✅

# Test HTML content
curl -s https://aletheia-codex-prod.web.app | grep "React App"
# Result: Found ✅
```

---

## Sprint 1.1 Status

### Admin-Infrastructure ✅
- IAP disabled on Load Balancer
- Backend services accessible without IAP
- Load Balancer operational

### Admin-Frontend ✅
- Firebase Hosting configuration verified
- Redeployed to production
- React app serving correctly
- No 403 errors

---

## Lessons Learned

1. **Configuration vs Deployment**: Having correct configuration isn't enough - it must be deployed
2. **Rewrite Order Matters**: Firebase Hosting processes rewrites in order, specific rules must come first
3. **Testing is Critical**: Always verify deployment with actual HTTP requests
4. **Cache Awareness**: Firebase Hosting caches can take 1-2 minutes to clear

---

## Next Steps

1. ✅ Firebase Hosting configuration verified
2. ✅ Redeployed to production
3. ✅ Root path serving React app
4. ✅ No 403 errors
5. ⏭️ End-to-end testing with users

---

## References

- **Sprint 1.1 Guide**: Sprint 1.1 remediation documentation
- **ADR-001**: Remove IAP decision
- **Firebase Hosting Docs**: https://firebase.google.com/docs/hosting/full-config

---

**Admin-Frontend**  
Sprint 1.1 Complete  
2025-01-18