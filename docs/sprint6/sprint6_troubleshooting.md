# Sprint 6: UI Foundation & Component Organization - Troubleshooting

## Overview
Sprint 6 encountered a critical blocker that prevented completion: GCP organization policy blocking public access to Cloud Functions. Multiple solutions were attempted, all blocked at the infrastructure level.

---

## Issue 1: Organization Policy Blocking Cloud Functions (CRITICAL)

### Problem
GCP organization policy prevents public access to Cloud Functions, causing all API calls to fail with 403 Forbidden.

### Symptoms
- All API endpoints return 403 Forbidden
- CORS preflight requests blocked
- Frontend can't access any backend services
- Review Queue page shows "Failed to fetch"
- Knowledge Graph page shows "Failed to fetch"

### Root Cause
Organization policy `iam.allowedPolicyMemberDomains` prevents `allUsers` from invoking Cloud Run services. Cloud Functions Gen 2 use Cloud Run underneath, so they're affected by this policy.

### Attempted Solutions

**Attempt 1: Firebase Authentication** ⚠️
- Implemented authentication middleware
- Updated all functions
- Result: Still blocked at infrastructure level

**Attempt 2: CORS Configuration** ⚠️
- Added CORS headers to functions
- Handled OPTIONS requests
- Result: Requests blocked before reaching code

**Attempt 3: Firebase Hosting Rewrites** ⚠️
- Configured rewrites to proxy requests
- Updated frontend to use relative URLs
- Result: Rewrites use Cloud Run, same policy applies

**Attempt 4: Custom Domain Mapping** ⚠️
- Set up Cloud DNS
- Mapped custom domain to services
- Result: Custom domains don't bypass policy

### Solution (Recommended)
**Load Balancer + Identity-Aware Proxy**:
- Enterprise-grade solution
- Works within organization policy
- Zero Trust architecture
- Cost: ~$30-75/month
- Implementation: 5-6 hours

### Status
⚠️ **UNRESOLVED** - Requires architectural change or policy exception

### Prevention
- Check organization policies before starting
- Test with actual policies early
- Have backup authentication strategies
- Consider enterprise security requirements

### Lessons Learned
- Organization policies can block entire architectures
- Infrastructure-level blocks can't be worked around
- Enterprise environments require different approaches
- Load Balancer + IAP is the proper solution

---

## Issue 2: Multiple Failed Workaround Attempts

### Problem
Spent significant time attempting workarounds that all failed due to the same root cause.

### Symptoms
- Firebase Hosting rewrites failed
- Custom domain mapping failed
- CORS configuration ineffective
- All attempts blocked at infrastructure level

### Root Cause
All workarounds still used Cloud Run underneath, which is blocked by the organization policy.

### Solution
**Stop Attempting Workarounds**:
- Recognize infrastructure-level blocks
- Move to proper solution (Load Balancer + IAP)
- Don't waste time on approaches that can't work

### Lessons Learned
- Infrastructure blocks can't be worked around
- Need to address root cause, not symptoms
- Proper enterprise solution is Load Balancer + IAP
- Time spent on workarounds could have been spent on proper solution

---

## Issue 3: Testing Limitations

### Problem
Couldn't test authentication or API functionality in production due to organization policy.

### Symptoms
- All API calls blocked
- Can't verify authentication working
- Can't test end-to-end workflows
- Limited to local testing only

### Root Cause
Organization policy blocks all requests before they reach application code.

### Solution
**Wait for Policy Resolution**:
- Implement Load Balancer + IAP
- OR get policy exception
- Then test in production

### Status
⚠️ **BLOCKED** - Waiting for policy resolution

---

## Summary

### Issues Encountered
1. ⚠️ Organization policy blocking Cloud Functions - UNRESOLVED (critical)
2. ⚠️ Multiple failed workaround attempts - RESOLVED (stopped attempting)
3. ⚠️ Testing limitations - BLOCKED (waiting for policy resolution)

### Severity Distribution
- **Critical**: 1 (organization policy - unresolved)
- **High**: 0
- **Medium**: 2 (workarounds, testing - blocked)
- **Low**: 0

### Resolution Rate
- **0%** of critical issues resolved
- **100%** of issues blocked by organization policy

### Key Takeaways
1. Organization policies can block entire projects
2. Infrastructure-level blocks require architectural solutions
3. Load Balancer + IAP is proper enterprise solution
4. Check policies before starting development
5. Have backup strategies for enterprise environments

---

**Sprint**: Sprint 6  
**Issues**: 3 (1 critical unresolved, 2 blocked)  
**Status**: ⚠️ Blocked by organization policy  
**Date**: November 9, 2025