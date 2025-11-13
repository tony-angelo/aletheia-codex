# ADR-001: Remove Identity-Aware Proxy (IAP) from Load Balancer

**Status**: Accepted  
**Date**: 2025-01-18  
**Decision Makers**: Architect, Project Owner  
**Sprint**: 1.1 (Remediation)  

---

## Context

During Sprint 1, we implemented a Load Balancer with Identity-Aware Proxy (IAP) to resolve a GCP organization policy that blocks `allUsers` access to Cloud Functions. However, this implementation has made the application completely inaccessible to users.

### The Problem

**Application Requirements:**
- Public SaaS application
- Self-service user registration via Firebase Auth (Google or email/password)
- Users should be able to sign up and access immediately
- No manual intervention required for user access

**IAP Characteristics:**
- Designed for internal corporate applications
- Requires manual GCP IAM grants for each user
- User must be explicitly granted `roles/iap.httpsResourceAccessor` role
- Not suitable for public SaaS with self-service registration

**Current Impact:**
- Application shows "You don't have access" (403 Forbidden)
- All users blocked, including the owner
- Every new user would require manual gcloud command to grant access
- Completely unsustainable for public SaaS

---

## Decision

**We will remove IAP from the Load Balancer while keeping the Load Balancer infrastructure.**

### Architecture Change

**Before (Sprint 1 - Broken):**
```
User → Load Balancer → IAP (blocks here!) → Cloud Functions → Firebase Auth
```

**After (Sprint 1.1 - Fixed):**
```
User → Load Balancer (public) → Cloud Functions → Firebase Auth validation
```

---

## Rationale

### Why Remove IAP

1. **Incompatible with Public SaaS Model**
   - IAP requires manual user grants
   - Cannot support self-service registration
   - Unsustainable for growing user base

2. **Firebase Auth is Sufficient**
   - Handles authentication
   - Supports self-service registration
   - Backend validates tokens
   - No manual intervention needed

3. **Load Balancer Alone Satisfies Requirements**
   - Provides organization policy compliance (no direct `allUsers` on Cloud Functions)
   - Enables public access through Load Balancer
   - Maintains SSL/TLS encryption
   - Provides routing and traffic management

### Why Keep Load Balancer

1. **Organization Policy Compliance**
   - Satisfies policy by not exposing Cloud Functions directly to `allUsers`
   - Access is through Load Balancer, not direct Cloud Function URLs

2. **Infrastructure Benefits**
   - SSL/TLS termination
   - URL-based routing
   - Single entry point
   - Future scalability (CDN, rate limiting, etc.)

3. **Already Implemented**
   - Load Balancer configuration is solid
   - DNS configured
   - SSL certificate active
   - No need to revert infrastructure

---

## Consequences

### Positive

1. **Application Accessible**
   - Users can access application immediately
   - Self-service registration works
   - No manual permission grants required

2. **Sustainable Architecture**
   - Scales with user growth
   - No operational overhead for user access
   - Standard SaaS authentication pattern

3. **Simplified Security Model**
   - Firebase Auth for authentication
   - Backend token validation
   - Clear security boundaries

4. **Maintains Compliance**
   - Organization policy satisfied (Load Balancer, not direct Cloud Functions)
   - No `allUsers` access to Cloud Functions directly

### Negative

1. **No IAP Audit Logging**
   - Lose IAP's built-in audit logging
   - Mitigation: Use Cloud Functions logging and Cloud Audit Logs

2. **Backend Responsible for Auth**
   - Backend must validate Firebase tokens
   - Mitigation: Already implemented and tested

3. **Wasted Sprint 1 Effort**
   - IAP implementation and testing was unnecessary
   - Lesson learned for future architecture decisions

### Neutral

1. **IAP Code Can Remain**
   - Backend IAP authentication code can stay (dormant)
   - May be useful for future admin-only endpoints
   - No harm in keeping it

---

## Implementation Plan

### Phase 1: Disable IAP (Admin-Infrastructure)
- Disable IAP on all 5 backend services
- Verify IAP is disabled
- Test public access

### Phase 2: Code Cleanup (Admin-Backend) - Optional
- Remove or comment out IAP authentication code
- Simplify to Firebase Auth only
- Update tests
- Deploy updated functions

### Phase 3: Verification (Admin-Frontend)
- Test application access
- Verify Firebase Auth login
- Test self-service registration
- Confirm all features work

---

## Alternatives Considered

### Alternative 1: Keep IAP, Grant Access to All Users
**Rejected because:**
- Would require granting `allUsers` the IAP role
- Defeats the purpose of IAP
- Still requires manual grants for domain users
- Doesn't solve the core problem

### Alternative 2: Use IAP with External Identities
**Rejected because:**
- Complex configuration required
- Token exchange mechanism needed
- Significant additional development
- Overkill for the use case

### Alternative 3: Revert to Direct Cloud Functions Access
**Rejected because:**
- Violates organization policy
- Loses Load Balancer benefits
- Would need to re-enable `allUsers` access

### Alternative 4: Use API Gateway Instead of Load Balancer
**Rejected because:**
- Would require re-implementation
- API Gateway has similar IAP issues
- Load Balancer is already working
- No clear benefit

---

## Validation

### Success Metrics

1. **Application Access**
   - ✅ Application loads at https://aletheiacodex.app
   - ✅ No 403 Forbidden errors
   - ✅ Users can access without manual grants

2. **Authentication**
   - ✅ Firebase Auth login works
   - ✅ Self-service registration works
   - ✅ Backend validates tokens correctly

3. **Functionality**
   - ✅ All features work end-to-end
   - ✅ Document ingestion works
   - ✅ Knowledge graph accessible
   - ✅ Notes and review features work

4. **Compliance**
   - ✅ Organization policy satisfied
   - ✅ No direct `allUsers` on Cloud Functions
   - ✅ Access through Load Balancer only

---

## Lessons Learned

### What Went Wrong

1. **Insufficient Requirements Analysis**
   - Didn't clarify "public SaaS" vs "internal application"
   - Didn't document self-service registration requirement
   - Didn't validate IAP suitability for use case

2. **No Architecture Review**
   - Implemented solution without validating against requirements
   - Didn't consider long-term sustainability
   - Didn't test with actual user scenarios

3. **Inadequate Testing**
   - No end-to-end testing with actual users
   - No verification of self-service registration
   - Assumed IAP would work without testing access

### Process Improvements

1. **Add Architecture Review Step**
   - Review proposed solutions before implementation
   - Validate technology choices against requirements
   - Consider long-term sustainability

2. **Clarify Requirements**
   - Document application type (public vs internal)
   - Document user access model (self-service vs managed)
   - Document scalability requirements

3. **Improve Testing**
   - Require end-to-end testing with actual users
   - Test self-service registration flows
   - Verify no manual intervention required

4. **Update Acceptance Criteria**
   - Include "public access" in criteria
   - Include "self-service registration" in criteria
   - Include "no manual grants" in criteria

---

## References

- **Sprint 1 Remediation Plan**: `[artifacts]/architect/sprint-1-remediation-plan.md`
- **Sprint 1.1 Overview**: `[artifacts]/architect/sprint-1.1-overview.md`
- **IAP Documentation**: https://cloud.google.com/iap/docs
- **Firebase Auth Documentation**: https://firebase.google.com/docs/auth

---

## Decision History

| Date | Status | Notes |
|------|--------|-------|
| 2025-01-18 | Proposed | Initial proposal to remove IAP |
| 2025-01-18 | Accepted | Approved by Architect and Project Owner |
| 2025-01-18 | Implementing | Sprint 1.1 in progress |

---

**Architect**  
AletheiaCodex Project  
2025-01-18