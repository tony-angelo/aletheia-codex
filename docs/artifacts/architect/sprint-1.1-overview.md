# Sprint 1.1 Overview - IAP Remediation

**Date**: 2025-01-18  
**Sprint**: 1.1 (Remediation)  
**Priority**: CRITICAL  
**Status**: In Progress  

---

## Purpose

Sprint 1.1 is a critical remediation sprint to fix the IAP (Identity-Aware Proxy) implementation from Sprint 1 that is blocking all user access to the application.

---

## Problem Statement

Sprint 1 implemented IAP on the Load Balancer, which is **incompatible with a public SaaS application** that requires self-service user registration via Firebase Auth.

**Current Issue:**
- Application shows "You don't have access" (403 Forbidden)
- IAP requires manual GCP IAM grants for every user
- Completely unsustainable for public SaaS
- Breaks self-service Firebase Auth registration

---

## Solution: Remove IAP, Keep Load Balancer

### Correct Architecture

```
User → Load Balancer (public) → Cloud Functions → Firebase Auth validation
```

**This provides:**
- ✅ Organization policy compliance (Load Balancer, not direct Cloud Functions access)
- ✅ Public access for users
- ✅ Self-service Firebase Auth registration
- ✅ No manual permission grants required
- ✅ Sustainable architecture

---

## Sprint 1.1 Goals

1. **Disable IAP** on all Load Balancer backend services
2. **Remove IAP code** from backend (optional cleanup)
3. **Verify public access** restored
4. **Test end-to-end** with actual users
5. **Document architecture** decision

---

## Admin Nodes Involved

### 1. Admin-Infrastructure (First)
**Tasks:**
- Disable IAP on all 5 backend services
- Verify IAP is disabled
- Test Load Balancer public access
- Document changes

**Estimated Time:** 30 minutes

### 2. Admin-Backend (Second)
**Tasks:**
- Remove IAP authentication code (optional cleanup)
- Simplify to Firebase Auth only
- Update tests
- Deploy updated functions

**Estimated Time:** 1-2 hours

### 3. Admin-Frontend (Third)
**Tasks:**
- Verify application access restored
- Test Firebase Auth login
- Test all features end-to-end
- Document verification

**Estimated Time:** 30 minutes

---

## Success Criteria

- [ ] IAP disabled on all backend services
- [ ] Application accessible at https://aletheiacodex.app
- [ ] Firebase Auth login works
- [ ] Self-service user registration works
- [ ] All features functional
- [ ] No 403 errors
- [ ] IAP code removed from backend (optional)
- [ ] Architecture Decision Record created
- [ ] All documentation updated

---

## Timeline

**Total Estimated Time:** 2-3 hours

**Sequence:**
1. Admin-Infrastructure: 30 minutes
2. Admin-Backend: 1-2 hours (optional cleanup)
3. Admin-Frontend: 30 minutes (verification)

---

## References

- **Remediation Plan**: `[artifacts]/architect/sprint-1-remediation-plan.md`
- **Sprint 1 Original**: `[artifacts]/admin-*/inbox/sprint-1-guide.md`
- **Architecture Decision Record**: `[artifacts]/architect/adr-001-remove-iap.md` (to be created)

---

**Architect**  
AletheiaCodex Project  
2025-01-18