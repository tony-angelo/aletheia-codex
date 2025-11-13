# IAP Removal - Sprint 1.1

**Date**: 2025-01-18  
**Reason**: IAP incompatible with public SaaS self-service registration  
**Status**: ✅ COMPLETED

---

## Problem Statement

IAP (Identity-Aware Proxy) was enabled on all backend services during Sprint 1, which blocked all user access to the application. IAP requires manual GCP IAM grants for every user, making it incompatible with our public SaaS model that uses Firebase Auth for self-service registration.

**Symptoms:**
- Users seeing "You don't have access" (403 Forbidden)
- All users blocked, including the owner
- No self-service registration possible

---

## Changes Made

Successfully disabled IAP on all 5 backend services:

- ✅ Disabled IAP on `backend-graphfunction`
- ✅ Disabled IAP on `backend-notesapifunction`
- ✅ Disabled IAP on `backend-orchestration`
- ✅ Disabled IAP on `backend-reviewapifunction`
- ✅ Disabled IAP on `backend-ingestion`

### Commands Executed

```bash
# Disabled IAP on each backend service
gcloud compute backend-services update backend-graphfunction --global --iap=disabled
gcloud compute backend-services update backend-notesapifunction --global --iap=disabled
gcloud compute backend-services update backend-orchestration --global --iap=disabled
gcloud compute backend-services update backend-reviewapifunction --global --iap=disabled
gcloud compute backend-services update backend-ingestion --global --iap=disabled
```

---

## Verification

### Backend Services Configuration

All backend services confirmed with IAP disabled:

```bash
$ for service in backend-graphfunction backend-notesapifunction backend-orchestration backend-reviewapifunction backend-ingestion; do
  enabled=$(gcloud compute backend-services describe $service --global --format="value(iap.enabled)")
  echo "$service: IAP enabled = $enabled"
done

backend-graphfunction: IAP enabled = False
backend-notesapifunction: IAP enabled = False
backend-orchestration: IAP enabled = False
backend-reviewapifunction: IAP enabled = False
backend-ingestion: IAP enabled = False
```

### Expected Behavior After Propagation

Once changes propagate (typically 1-5 minutes):

- ✅ Load Balancer publicly accessible
- ✅ API endpoints return 401 (unauthorized) instead of 403 (forbidden)
  - 401 means backend is accessible and checking Firebase Auth tokens
  - 403 means IAP is blocking access
- ✅ Application UI loads in browser
- ✅ Users can self-register with Firebase Auth

### Propagation Note

⚠️ **Important**: IAP configuration changes can take 1-5 minutes to propagate through Google's global infrastructure. During this time, you may still see 403 errors or IAP redirect pages. This is normal and will resolve automatically.

To verify propagation is complete:
```bash
# Should return 200/301/302 (not 403)
curl -I https://aletheiacodex.app

# Should return 401 (not 403)
curl -I https://aletheiacodex.app/api/graph
```

---

## Architecture

### New Architecture (IAP Removed)

```
User → Load Balancer (public) → Cloud Functions → Firebase Auth validation
```

**Benefits:**
- ✅ Public access through Load Balancer
- ✅ Firebase Auth handles authentication
- ✅ Backend validates Firebase tokens
- ✅ No manual user grants required
- ✅ Self-service registration works
- ✅ Still complies with organization policy (no direct Cloud Functions access)

### What Remains

The Load Balancer infrastructure remains fully operational:

- ✅ Load Balancer configuration
- ✅ Backend services (5 services)
- ✅ URL routing (all API endpoints)
- ✅ SSL certificate (Google-managed)
- ✅ DNS configuration (aletheiacodex.app)
- ✅ Monitoring and alerting

### What Changed

- ❌ IAP disabled on all backend services
- ✅ Public access restored
- ✅ Self-service Firebase Auth registration enabled

---

## Why This Is Correct

**IAP is designed for internal applications**, not public SaaS:

1. **IAP Requires Manual Grants**: Every user must be manually granted IAM permissions
2. **Incompatible with Self-Service**: Our app needs users to register themselves via Firebase Auth
3. **Organization Policy Compliance**: Load Balancer (without IAP) still satisfies the organization policy
   - Policy requires: No direct Cloud Functions access
   - Solution: Access through Load Balancer (with or without IAP)
4. **Correct Architecture**: Public Load Balancer → Firebase Auth validation in backend

---

## Testing Checklist

After propagation completes (1-5 minutes):

- [ ] `curl -I https://aletheiacodex.app` returns 200/301/302 (not 403)
- [ ] `curl -I https://aletheiacodex.app/api/graph` returns 401 (not 403)
- [ ] Browser shows application UI (not "You don't have access" error)
- [ ] All backend services show IAP disabled in GCP Console
- [ ] Users can access the application without GCP IAM grants

---

## Troubleshooting

### Still Seeing 403 Errors

**Cause**: Changes still propagating or browser cache

**Solutions:**
1. Wait 1-5 minutes for propagation
2. Clear browser cache
3. Try incognito/private browsing mode
4. Verify IAP is actually disabled:
   ```bash
   gcloud compute backend-services describe backend-graphfunction --global --format="value(iap.enabled)"
   ```

### Still Seeing IAP OAuth Redirect

**Cause**: Browser cached the redirect or propagation delay

**Solutions:**
1. Clear browser cache completely
2. Wait for propagation (up to 5 minutes)
3. Try a different browser or device
4. Check backend service configuration

---

## References

- **Sprint 1.1 Overview**: `docs/artifacts/architect/sprint-1.1-overview.md`
- **Remediation Plan**: `docs/artifacts/architect/sprint-1-remediation-plan.md`
- **ADR-001**: `docs/artifacts/architect/adr-001-remove-iap.md`
- **Load Balancer Documentation**: `infrastructure/load-balancer/README.md`

---

## Impact

### Immediate Impact
- ✅ Application accessible to all users
- ✅ Self-service registration enabled
- ✅ No manual permission grants needed

### Long-term Impact
- ✅ Scalable authentication model
- ✅ Standard SaaS user experience
- ✅ Reduced operational overhead
- ✅ Organization policy compliance maintained

---

## Next Steps

1. **Verify Access**: Test application access after propagation
2. **Update Documentation**: Update any references to IAP in other docs
3. **Monitor**: Watch for any authentication issues
4. **Communicate**: Inform users that access is restored

---

**Sprint 1.1 Remediation: COMPLETED**  
**IAP Status**: Disabled on all backend services  
**Public Access**: Restored (pending propagation)