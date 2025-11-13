# Sprint 1.1 Guide - IAP Remediation (Infrastructure)

**Sprint**: 1.1 (Remediation)  
**Node**: Admin-Infrastructure  
**Priority**: CRITICAL  
**Estimated Time**: 30 minutes  
**Status**: Ready to Start  

---

## Mission

**Disable IAP (Identity-Aware Proxy) on all Load Balancer backend services to restore public access to the application.**

This is a continuation of Sprint 1. You successfully configured the Load Balancer and enabled IAP, but we've discovered that IAP is incompatible with our public SaaS application model. Your task is to disable IAP while keeping the Load Balancer infrastructure.

---

## Context

### What Happened in Sprint 1

You successfully completed:
- ✅ Load Balancer configuration
- ✅ Backend services setup
- ✅ URL routing
- ✅ SSL certificate
- ✅ DNS configuration
- ✅ IAP enablement

### The Problem

**IAP is blocking all user access** because it requires manual GCP IAM grants for every user. This is incompatible with our self-service Firebase Auth registration model.

**Current State:**
- Application shows "You don't have access" (403 Forbidden)
- All users blocked, including the owner
- IAP requires manual permission grants per user
- Unsustainable for public SaaS

### The Solution

**Remove IAP, Keep Load Balancer**

```
User → Load Balancer (public) → Cloud Functions → Firebase Auth validation
```

This provides:
- ✅ Organization policy compliance (Load Balancer, not direct Cloud Functions)
- ✅ Public access for users
- ✅ Self-service registration
- ✅ No manual permission grants

---

## Your Tasks

### Task 1: Disable IAP on All Backend Services (15 minutes)

**Objective**: Remove IAP from all 5 backend services

**Steps:**

1. **Authenticate with GCP**
   ```bash
   cd aletheia-codex
   git checkout sprint-1
   git pull origin sprint-1
   
   gcloud auth activate-service-account --key-file=/workspace/aletheia-codex-prod-af9a64a7fcaa.json
   gcloud config set project aletheia-codex-prod
   ```

2. **Run the Disable IAP Script**
   ```bash
   # The script is already on sprint-1 branch
   chmod +x infrastructure/load-balancer/disable-iap.sh
   ./infrastructure/load-balancer/disable-iap.sh
   ```

   **OR manually disable IAP:**
   ```bash
   gcloud compute backend-services update backend-graphfunction --global --no-iap
   gcloud compute backend-services update backend-notesapifunction --global --no-iap
   gcloud compute backend-services update backend-orchestration --global --no-iap
   gcloud compute backend-services update backend-reviewapifunction --global --no-iap
   gcloud compute backend-services update backend-ingestion --global --no-iap
   ```

3. **Verify IAP is Disabled**
   ```bash
   # Check each backend service
   for service in backend-graphfunction backend-notesapifunction backend-orchestration backend-reviewapifunction backend-ingestion; do
     enabled=$(gcloud compute backend-services describe $service --global --format="value(iap.enabled)")
     echo "$service: IAP enabled = $enabled"
   done
   ```

   **Expected Output:** All should show empty or "False"

### Task 2: Test Public Access (10 minutes)

**Objective**: Verify Load Balancer is publicly accessible

**Steps:**

1. **Test Load Balancer Endpoint**
   ```bash
   # Test that Load Balancer responds (should get HTML or redirect, not 403)
   curl -I https://aletheiacodex.app
   ```

   **Expected:** HTTP 200 or 301/302 redirect (NOT 403 Forbidden)

2. **Test API Endpoints**
   ```bash
   # These should return 401 (unauthorized) not 403 (forbidden)
   # 401 means backend is accessible and checking auth
   # 403 means IAP is blocking
   
   curl -I https://aletheiacodex.app/api/graph
   curl -I https://aletheiacodex.app/api/notes
   curl -I https://aletheiacodex.app/api/review
   ```

   **Expected:** HTTP 401 Unauthorized (backend is accessible, just needs auth token)

3. **Verify in Browser**
   - Open https://aletheiacodex.app in browser
   - Should see application UI (not "You don't have access" error)
   - May see login screen or application interface

### Task 3: Document Changes (5 minutes)

**Objective**: Document the IAP removal

**Create**: `infrastructure/load-balancer/IAP-REMOVAL.md`

```markdown
# IAP Removal - Sprint 1.1

**Date**: 2025-01-18  
**Reason**: IAP incompatible with public SaaS self-service registration  

## Changes Made

- Disabled IAP on backend-graphfunction
- Disabled IAP on backend-notesapifunction
- Disabled IAP on backend-orchestration
- Disabled IAP on backend-reviewapifunction
- Disabled IAP on backend-ingestion

## Verification

- Load Balancer publicly accessible: ✅
- API endpoints return 401 (not 403): ✅
- Application UI loads in browser: ✅

## Architecture

Load Balancer remains operational without IAP:
- Public access through Load Balancer
- Firebase Auth handles authentication
- Backend validates Firebase tokens
- No manual user grants required

## References

- ADR-001: Remove IAP
- Sprint 1.1 Remediation Plan
```

### Task 4: Commit Changes (5 minutes)

**Objective**: Commit documentation to sprint-1 branch

```bash
git add infrastructure/load-balancer/IAP-REMOVAL.md
git commit -m "feat(infrastructure): disable IAP on all backend services

- Disabled IAP on all 5 backend services
- Verified public access restored
- Load Balancer remains operational
- Application now accessible to all users
- Sprint 1.1 remediation complete"

git push origin sprint-1
```

---

## Success Criteria

- [ ] IAP disabled on all 5 backend services
- [ ] Verification shows IAP is disabled (empty or False)
- [ ] Load Balancer returns 200/301/302 (not 403)
- [ ] API endpoints return 401 (not 403)
- [ ] Application UI loads in browser
- [ ] Documentation created
- [ ] Changes committed to sprint-1 branch

---

## Testing Checklist

- [ ] `curl -I https://aletheiacodex.app` returns 200/301/302
- [ ] `curl -I https://aletheiacodex.app/api/graph` returns 401
- [ ] Browser shows application UI (not 403 error)
- [ ] All backend services show IAP disabled

---

## Important Notes

### What Stays

- ✅ Load Balancer configuration
- ✅ Backend services
- ✅ URL routing
- ✅ SSL certificate
- ✅ DNS configuration
- ✅ All infrastructure from Sprint 1

### What Changes

- ❌ IAP disabled on backend services
- ✅ Public access restored
- ✅ Self-service registration works

### Why This Is Correct

**IAP is for internal applications**, not public SaaS:
- IAP requires manual user grants
- Our app needs self-service Firebase Auth registration
- Load Balancer without IAP is the correct architecture
- Still satisfies organization policy (no direct Cloud Functions access)

---

## Troubleshooting

### Issue: Script fails with permission error

**Solution:**
```bash
# Verify authentication
gcloud auth list

# Re-authenticate if needed
gcloud auth activate-service-account --key-file=/workspace/aletheia-codex-prod-af9a64a7fcaa.json
```

### Issue: IAP still shows as enabled

**Solution:**
```bash
# Manually disable on specific service
gcloud compute backend-services update backend-graphfunction --global --no-iap

# Wait 30 seconds and check again
sleep 30
gcloud compute backend-services describe backend-graphfunction --global --format="value(iap.enabled)"
```

### Issue: Still getting 403 errors

**Solution:**
- Wait 1-2 minutes for changes to propagate
- Clear browser cache
- Try incognito/private browsing mode
- Check that IAP is actually disabled (see verification step)

---

## References

- **Sprint 1.1 Overview**: `[artifacts]/architect/sprint-1.1-overview.md`
- **Remediation Plan**: `[artifacts]/architect/sprint-1-remediation-plan.md`
- **ADR-001**: `[artifacts]/architect/adr-001-remove-iap.md`
- **Disable IAP Script**: `[sprint-1]/infrastructure/load-balancer/disable-iap.sh`

---

## Next Steps

After you complete this work:
1. Create session log in `[artifacts]/admin-infrastructure/outbox/session-log-sprint-1.1.md`
2. Report completion to Architect
3. Architect will validate and move to Admin-Backend

---

**This is a critical fix. The application is currently inaccessible to all users.**

---

**Architect**  
AletheiaCodex Project  
Sprint 1.1 Remediation  
2025-01-18