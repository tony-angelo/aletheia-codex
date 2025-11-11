# CORS & Organization Policy Workaround

## Current Situation

The GCP project has an organization policy (`iam.allowedPolicyMemberDomains`) that prevents public access to Cloud Functions and Cloud Run services. This is blocking our deployment of authenticated endpoints.

## What's Working ✅

1. **Firebase Authentication Implementation** - Complete
   - Auth middleware created
   - Frontend utilities working
   - Services updated to use tokens

2. **Cloud Functions** - Deployed but not accessible due to org policy
   - Graph Function: https://us-central1-aletheia-codex-prod.cloudfunctions.net/graph-function
   - Review API: https://us-central1-aletheia-codex-prod.cloudfunctions.net/review-api

3. **Frontend** - Deployed and updated
   - https://aletheia-codex-prod.web.app
   - Updated to use Cloud Run URLs
   - Authentication utilities integrated

## Problem ❌

The organization policy prevents:
- Adding `allUsers` to Cloud Run invoker role
- Adding `allUsers` to Cloud Functions invoker role
- Any public access to services

This means:
- CORS preflight requests are blocked (403)
- Even authenticated requests can't reach the functions
- The functions return 403 before our code runs

## Solutions

### Option 1: Organization Policy Exception (Recommended)
**Ask GCP Org Admin** to allow public invocations for this project.

**Request Template:**
```
To: GCP Organization Admin
Project: aletheia-codex-prod
Request: Allow allUsers invocations for Cloud Functions/Run services
Reason: Web application requires public access with Firebase Authentication verification
Security: Functions verify Firebase ID tokens, not truly public
```

**What Admin Should Do:**
1. Go to IAM & Admin → Organization Policies
2. Find "Domain restricted sharing" constraint
3. Add exception for project: `aletheia-codex-prod`
4. OR allow `allUsers` in permitted domains

### Option 2: Use API Gateway (More Complex)
Create an API Gateway that handles authentication and forwards to functions.

**Steps:**
1. Deploy functions without public access
2. Create API Gateway with Firebase JWT authentication
3. Configure gateway to forward authenticated requests
4. Update frontend to use gateway URL

**Pros:** Works within org policy
**Cons:** More complex, additional cost

### Option 3: Use Internal Load Balancer with Cloud Armor
Create internal resources with Cloud Armor authentication.

**Pros:** Very secure
**Cons:** Complex, expensive, overkill for this use case

### Option 4: Deploy to Different GCP Project
Deploy to a project without the restrictive organization policy.

**Pros:** Quick solution
**Cons:** Need to migrate resources, separate billing

### Option 5: Local Development Proxy (Temporary)
Create a local proxy server for development.

**Implementation:**
```bash
# Create proxy server
npm install -g http-proxy-middleware
# Configure to forward requests and handle CORS
```

## Current Status

**Backend:** ✅ Ready (functions deployed with auth)
**Frontend:** ✅ Ready (auth utils implemented) 
**Deployment:** ❌ Blocked by org policy

## Next Steps

1. **Immediate:** Contact GCP org admin for policy exception
2. **Alternative:** If org policy can't be changed, implement Option 2 (API Gateway)
3. **Development:** Use local proxy for continued development

## Testing Checklist Once Policy Exception is Granted

- [ ] CORS preflight succeeds (200/204)
- [ ] Unauthenticated requests return 401
- [ ] Authenticated requests succeed (200)
- [ ] Review Queue loads properly
- [ ] Knowledge Graph loads properly
- [ ] User can approve entities
- [ ] Approved entities appear in graph

## Files Ready for Production

All authentication implementation is complete and ready:
- `shared/auth/firebase_auth.py` - Firebase Auth middleware
- `functions/graph/main.py` - Graph function with auth
- `functions/review_api/main.py` - Review API with auth
- `web/src/utils/auth.ts` - Frontend auth utilities
- `web/src/services/*.ts` - Updated services

## Notes for Sprint 6 Completion Report

- Firebase Authentication implementation: ✅ COMPLETE
- Functions deployed with authentication: ✅ COMPLETE  
- Frontend updated with auth: ✅ COMPLETE
- Blocked by organization policy: ❌ OBSTACLE
- Requires org admin intervention to resolve

The technical implementation is complete and ready. The only remaining issue is the organization policy blocking public access to the services.