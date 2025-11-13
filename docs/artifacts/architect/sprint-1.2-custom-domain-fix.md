# Sprint 1.2 - Custom Domain Configuration Fix

**Date**: 2025-01-18  
**Priority**: HIGH  
**Issue**: Users cannot access app at production URL (https://aletheiacodex.app)  
**Status**: Ready to Implement  

---

## Problem Statement

Users should access the application at `https://aletheiacodex.app/` (the production URL), but currently:
- ❌ `https://aletheiacodex.app/` shows 403 Forbidden
- ✅ `https://aletheia-codex-prod.web.app/dashboard` works

**Root Cause**: The custom domain `aletheiacodex.app` is pointing to the Load Balancer IP instead of Firebase Hosting.

---

## Current (Incorrect) Architecture

```
aletheiacodex.app (DNS A record)
    ↓
34.120.185.233 (Load Balancer IP)
    ↓
Load Balancer (configured for /api/* only)
    ↓
403 Forbidden (no backend for root path)
```

**Why this is wrong:**
- Load Balancer is for API calls, not serving the React app
- Load Balancer has no backend for root path `/`
- Users get 403 Forbidden error

---

## Correct Architecture

```
aletheiacodex.app (Firebase Hosting custom domain)
    ↓
Firebase Hosting
    ↓
    ├─ / → React App
    └─ /api/* → Load Balancer (internal) → Cloud Functions
```

**Why this is correct:**
- Firebase Hosting serves the React app
- Firebase Hosting proxies API calls to Load Balancer
- Users access production URL seamlessly
- Load Balancer is internal, not public-facing

---

## Solution Overview

### Step 1: Add Custom Domain to Firebase Hosting
Configure `aletheiacodex.app` as a custom domain in Firebase Hosting.

### Step 2: Update DNS Records
Change DNS from Load Balancer IP to Firebase Hosting records.

### Step 3: Update firebase.json (if needed)
Ensure API proxy uses Load Balancer URL correctly.

### Step 4: Wait for SSL Certificate
Firebase Hosting will provision SSL certificate for custom domain.

---

## Implementation Plan

### Phase 1: Firebase Hosting Custom Domain Setup

**Who**: Admin-Frontend or Manual (Firebase Console)

**Steps:**

1. **Add Custom Domain in Firebase Console**
   - Go to Firebase Console → Hosting
   - Click "Add custom domain"
   - Enter: `aletheiacodex.app`
   - Firebase will provide DNS records

2. **Note the DNS Records**
   Firebase will provide records like:
   ```
   Type: A
   Name: aletheiacodex.app
   Value: [Firebase Hosting IP addresses]
   
   Type: TXT
   Name: aletheiacodex.app
   Value: [Verification token]
   ```

### Phase 2: Update DNS Configuration

**Who**: User (DNS Provider)

**Steps:**

1. **Remove Current A Record**
   ```
   DELETE:
   Type: A
   Name: aletheiacodex.app
   Value: 34.120.185.233
   ```

2. **Add Firebase Hosting Records**
   ```
   ADD:
   Type: A
   Name: aletheiacodex.app
   Value: [Firebase Hosting IPs - provided by Firebase]
   
   Type: TXT
   Name: aletheiacodex.app
   Value: [Verification token - provided by Firebase]
   ```

3. **Wait for DNS Propagation**
   - Typically 5-15 minutes
   - Can take up to 48 hours in some cases

### Phase 3: SSL Certificate Provisioning

**Who**: Firebase (Automatic)

**Timeline:**
- Firebase automatically provisions SSL certificate
- Takes 15-60 minutes after DNS verification
- No action required

### Phase 4: Verification

**Who**: Admin-Frontend

**Steps:**

1. **Verify DNS Resolution**
   ```bash
   nslookup aletheiacodex.app
   # Should show Firebase Hosting IPs
   ```

2. **Test Application Access**
   ```bash
   curl -I https://aletheiacodex.app
   # Should return 200 OK
   ```

3. **Test in Browser**
   - Open https://aletheiacodex.app
   - Should see React application
   - Should NOT see 403 error

4. **Test API Calls**
   - Log in to application
   - Test features (document ingestion, graph, notes)
   - Verify API calls work through Load Balancer

---

## firebase.json Configuration

The current configuration should already be correct:

```json
{
  "hosting": {
    "public": "web/build",
    "site": "aletheia-codex-prod",
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
  }
}
```

**Note:** The API proxy destination can remain as `https://aletheiacodex.app/api/:splat` because:
- Firebase Hosting will handle the custom domain
- The proxy will route to the Load Balancer internally
- This creates a clean architecture

**Alternative (if issues):** Change API proxy to Load Balancer IP:
```json
{
  "source": "/api/**",
  "destination": "https://34.120.185.233/api/:splat"
}
```

---

## Load Balancer Configuration

**No changes needed to Load Balancer!**

The Load Balancer remains configured for API endpoints:
- `/api/ingest`
- `/api/orchestrate`
- `/api/graph/*`
- `/api/notes/*`
- `/api/review/*`

It will receive API calls from Firebase Hosting's proxy, not directly from users.

---

## Timeline

| Phase | Duration | Who |
|-------|----------|-----|
| Add custom domain to Firebase | 5 min | Admin-Frontend or Console |
| Update DNS records | 5 min | User |
| DNS propagation | 5-15 min | Automatic |
| SSL certificate provisioning | 15-60 min | Firebase (automatic) |
| Verification and testing | 10 min | Admin-Frontend |
| **Total** | **40-95 minutes** | |

---

## Success Criteria

- [ ] Custom domain added to Firebase Hosting
- [ ] DNS records updated
- [ ] DNS resolves to Firebase Hosting
- [ ] SSL certificate provisioned
- [ ] https://aletheiacodex.app loads React app
- [ ] No 403 Forbidden errors
- [ ] Firebase Auth login works
- [ ] API calls work through Load Balancer
- [ ] All features functional

---

## Rollback Plan

If issues occur:

1. **Revert DNS to Load Balancer** (temporary)
   ```
   Type: A
   Name: aletheiacodex.app
   Value: 34.120.185.233
   ```

2. **Users access via Firebase default URL**
   - https://aletheia-codex-prod.web.app

3. **Investigate and fix issues**

4. **Retry custom domain setup**

---

## Alternative Approaches

### Option 1: Use Firebase Hosting Custom Domain (RECOMMENDED)
- ✅ Clean architecture
- ✅ Firebase handles SSL
- ✅ Single entry point for users
- ✅ Load Balancer is internal

### Option 2: Load Balancer with Cloud Run for Frontend
- ❌ More complex
- ❌ Need to containerize React app
- ❌ Additional infrastructure
- ❌ Not necessary for this use case

### Option 3: Keep Both URLs
- ❌ Confusing for users
- ❌ Two URLs to maintain
- ❌ Not professional

---

## Documentation Updates Needed

After implementation:

1. **Update README.md**
   - Production URL: https://aletheiacodex.app
   - Remove references to aletheia-codex-prod.web.app

2. **Update Architecture Diagrams**
   - Show custom domain flow
   - Clarify Load Balancer is internal

3. **Update User Documentation**
   - Access instructions
   - Login procedures

---

## Next Steps

**Immediate:**
1. User adds custom domain in Firebase Console
2. User updates DNS records
3. Wait for DNS propagation and SSL provisioning
4. Admin-Frontend verifies and tests

**After Verification:**
1. Update all documentation
2. Announce production URL to users
3. Close Sprint 1.2

---

## References

- **Firebase Custom Domain Docs**: https://firebase.google.com/docs/hosting/custom-domain
- **DNS Configuration Guide**: https://firebase.google.com/docs/hosting/custom-domain#set-up
- **SSL Certificate Info**: https://firebase.google.com/docs/hosting/custom-domain#ssl

---

**Architect**  
AletheiaCodex Project  
2025-01-18