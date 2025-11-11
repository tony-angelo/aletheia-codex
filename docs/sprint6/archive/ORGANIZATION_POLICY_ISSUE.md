# Organization Policy Blocking Cloud Functions Access

**Issue**: GCP Organization Policy prevents public access to Cloud Functions  
**Status**: Requires Organization Administrator Action  
**Priority**: CRITICAL - Blocking production deployment

---

## Executive Summary

The Aletheia Codex application cannot be accessed in production because a GCP organization policy prevents making Cloud Functions publicly accessible. All code is ready and deployed, but requests are blocked at the infrastructure level with 403 Forbidden errors.

**Root Cause**: Organization IAM policy constraint `iam.allowedPolicyMemberDomains` prevents adding `allUsers` or `allAuthenticatedUsers` to Cloud Functions and Cloud Run services.

---

## Current Situation

### What's Working ✅
- All code implemented with proper CORS handling
- Firebase authentication integrated
- Frontend deployed to Firebase Hosting
- Cloud Functions deployed (private)
- Firebase Hosting rewrites configured

### What's Blocked ❌
- Public access to Cloud Functions
- Cloud Run service invocation
- API requests from frontend
- Review Queue page functionality
- Knowledge Graph page functionality

### Error Messages
```
403 Forbidden
Access to fetch at 'https://us-central1-aletheia-codex-prod.cloudfunctions.net/review-api-function/review/pending' 
from origin 'https://aletheia-codex-prod.web.app' has been blocked by CORS policy: 
Response to preflight request doesn't pass access control check: 
No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

**Why**: Requests are blocked at infrastructure level BEFORE reaching our code, so CORS headers are never added.

---

## Technical Details

### Organization Policy Constraint

**Policy**: `iam.allowedPolicyMemberDomains`  
**Effect**: Prevents adding `allUsers` or `allAuthenticatedUsers` to IAM policies  
**Scope**: Organization-wide  
**Impact**: Blocks all public Cloud Functions and Cloud Run services

### Failed Deployment Attempts

1. **Cloud Functions Gen 2 with `--allow-unauthenticated`**
   ```bash
   ERROR: One or more users named in the policy do not belong to a permitted customer, 
   perhaps due to an organization policy.
   ```

2. **Cloud Functions Gen 1 with `--allow-unauthenticated`**
   ```bash
   ERROR: One or more users named in the policy do not belong to a permitted customer, 
   perhaps due to an organization policy.
   ```

3. **Cloud Run IAM Policy Binding**
   ```bash
   ERROR: FAILED_PRECONDITION: One or more users named in the policy do not belong to 
   a permitted customer, perhaps due to an organization policy.
   ```

4. **Firebase Hosting Rewrites**
   - Configured successfully
   - Still blocked because underlying Cloud Run service requires public access

### Architecture

```
User Browser
    ↓ (HTTPS request)
Firebase Hosting (public)
    ↓ (rewrite /api/* to functions)
Cloud Functions Gen 2
    ↓ (uses Cloud Run underneath)
Cloud Run Service (BLOCKED - requires public access)
    ↓ (403 Forbidden - never reaches here)
Application Code (CORS headers, Firebase auth)
```

**Problem**: Blocked at Cloud Run layer, never reaches application code.

---

## Solution: Organization Policy Exception

### Required Action

A GCP Organization Administrator must grant an exception for this project to allow public Cloud Run services.

### Step 1: Check Current Policy

```bash
gcloud resource-manager org-policies describe iam.allowedPolicyMemberDomains \
  --organization=YOUR_ORG_ID
```

### Step 2: Create Policy Exception

Create a file `policy.yaml`:

```yaml
name: organizations/YOUR_ORG_ID/policies/iam.allowedPolicyMemberDomains
spec:
  rules:
    - allowAll: true
      condition:
        expression: resource.matchTag('YOUR_ORG_ID/environment', 'production')
        title: Allow public access for production services
```

Or for project-specific exception:

```yaml
name: organizations/YOUR_ORG_ID/policies/iam.allowedPolicyMemberDomains
spec:
  inheritFromParent: true
  rules:
    - allowAll: true
      condition:
        expression: resource.name.startsWith('projects/aletheia-codex-prod/')
        title: Allow public access for Aletheia Codex project
```

### Step 3: Apply Policy

```bash
gcloud resource-manager org-policies set-policy policy.yaml \
  --organization=YOUR_ORG_ID
```

### Step 4: Add IAM Bindings

Once policy is updated, run:

```bash
# Review API Function
gcloud run services add-iam-policy-binding review-api-function \
  --region=us-central1 \
  --member=allUsers \
  --role=roles/run.invoker \
  --platform=managed

# Graph Function
gcloud run services add-iam-policy-binding graph-function \
  --region=us-central1 \
  --member=allUsers \
  --role=roles/run.invoker \
  --platform=managed

# Notes API Function
gcloud run services add-iam-policy-binding notes-api-function \
  --region=us-central1 \
  --member=allUsers \
  --role=roles/run.invoker \
  --platform=managed
```

---

## Alternative Solutions

If organization policy cannot be changed, consider these alternatives:

### Option 1: API Gateway

Deploy Google Cloud API Gateway:
- Gateway handles public access
- Gateway forwards to private functions
- May not be subject to same policy
- Additional cost and complexity

**Estimated Time**: 4-6 hours  
**Cost**: ~$3-10/month

### Option 2: App Engine

Deploy APIs on App Engine instead of Cloud Functions:
- Different IAM model
- May bypass organization policy
- Requires code refactoring

**Estimated Time**: 8-12 hours  
**Cost**: Similar to Cloud Functions

### Option 3: Cloud Endpoints

Use Cloud Endpoints for API management:
- Handles authentication differently
- May work with organization policy
- Additional configuration required

**Estimated Time**: 6-8 hours  
**Cost**: ~$5-15/month

### Option 4: Custom Domain with Load Balancer

Set up custom domain with Cloud Load Balancer:
- Load balancer handles public access
- Forwards to private backends
- More complex setup

**Estimated Time**: 6-10 hours  
**Cost**: ~$18/month (load balancer)

---

## Security Considerations

### Current Security Model

Even with public access, the application is secure:

1. **Firebase Authentication Required**
   - All API endpoints require valid Firebase ID token
   - Tokens verified using Firebase Admin SDK
   - Unauthorized requests return 401

2. **User Data Isolation**
   - Each user can only access their own data
   - User ID extracted from verified token
   - Database queries filtered by user ID

3. **CORS Protection**
   - Only allowed origins can make requests
   - Prevents unauthorized cross-origin access

4. **HTTPS Only**
   - All traffic encrypted in transit
   - No plain HTTP allowed

### Why Public Access is Safe

"Public access" means:
- ✅ Anyone can **send requests** to the endpoint
- ❌ But requests **must include valid Firebase token**
- ❌ Without token, requests are **rejected with 401**
- ❌ With invalid token, requests are **rejected with 401**

**Analogy**: Like a building with a public entrance but requiring ID badge to get past security.

---

## Impact Assessment

### Current Impact

- ❌ Review Queue page: Not functional
- ❌ Knowledge Graph page: Not functional
- ❌ Notes processing: Not functional
- ✅ User authentication: Working
- ✅ Notes creation: Working (UI only)
- ✅ Frontend: Deployed and accessible

### Business Impact

- **Users cannot review extracted entities**: Core feature blocked
- **Users cannot browse knowledge graph**: Core feature blocked
- **Users cannot approve/reject items**: Workflow blocked
- **Application appears broken**: Poor user experience

### Timeline Impact

- **Code complete**: ✅ Done
- **Deployment ready**: ✅ Done
- **Blocked by**: Organization policy
- **Resolution time**: Depends on org admin response

---

## Recommended Action Plan

### Immediate (Today)

1. **Contact GCP Organization Administrator**
   - Explain the issue
   - Request policy exception
   - Provide this documentation

2. **Provide Justification**
   - Production application blocked
   - Security model is sound (Firebase auth)
   - Only affects this specific project
   - Temporary exception while exploring alternatives

### Short Term (This Week)

1. **If policy exception granted**
   - Apply IAM bindings (5 minutes)
   - Test application (15 minutes)
   - Verify all features working
   - Close Issue #26

2. **If policy exception denied**
   - Evaluate alternative solutions
   - Choose best approach (API Gateway recommended)
   - Implement chosen solution
   - Estimated: 4-8 hours

### Long Term (Next Sprint)

1. **Review security architecture**
   - Evaluate if API Gateway provides benefits
   - Consider moving to App Engine
   - Document security model
   - Update deployment procedures

---

## Contact Information

### Project Details

- **Project ID**: `aletheia-codex-prod`
- **Organization**: (Your GCP Organization)
- **Region**: `us-central1`
- **Services Affected**:
  - `review-api-function` (Cloud Run)
  - `graph-function` (Cloud Run)
  - `notes-api-function` (Cloud Run)

### Required Permissions

The organization administrator needs:
- `roles/orgpolicy.policyAdmin` (to modify org policies)
- Or `roles/resourcemanager.organizationAdmin`

### Support Resources

- **GCP Documentation**: https://cloud.google.com/resource-manager/docs/organization-policy/org-policy-constraints
- **IAM Policy Constraints**: https://cloud.google.com/iam/docs/conditions-overview
- **Cloud Run IAM**: https://cloud.google.com/run/docs/authenticating/public

---

## Testing After Policy Update

Once the organization policy is updated and IAM bindings are added:

### Test 1: Direct API Call

```bash
curl https://us-central1-aletheia-codex-prod.cloudfunctions.net/review-api-function/review/pending
```

**Expected**: 401 Unauthorized (requires Firebase token)  
**Not**: 403 Forbidden

### Test 2: CORS Preflight

```bash
curl -X OPTIONS \
  -H "Origin: https://aletheia-codex-prod.web.app" \
  -H "Access-Control-Request-Method: GET" \
  -v \
  https://aletheia-codex-prod.web.app/api/review/pending
```

**Expected**: 200 OK with CORS headers

### Test 3: Browser Testing

1. Open https://aletheia-codex-prod.web.app
2. Sign in with Google
3. Navigate to Review Queue page
4. **Expected**: See pending items, no errors
5. Navigate to Knowledge Graph page
6. **Expected**: See graph nodes, no errors

---

## Conclusion

The Aletheia Codex application is fully developed and ready for production use. The only blocker is a GCP organization policy that prevents public access to Cloud Functions.

**Action Required**: Organization administrator must grant policy exception for project `aletheia-codex-prod` to allow public Cloud Run services.

**Timeline**: Once policy is updated, application will be fully functional within 5 minutes.

**Alternative**: If policy cannot be changed, implement API Gateway solution (4-6 hours additional work).

---

**Document Version**: 1.0  
**Date**: November 10, 2025  
**Status**: Awaiting Organization Administrator Action  
**Priority**: CRITICAL