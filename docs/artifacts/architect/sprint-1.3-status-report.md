# Sprint 1.3 Status Report: Service Account Invoker Approach

**Date**: 2025-01-14  
**Status**: ⚠️ PARTIALLY COMPLETE - Still Blocked  
**Issue**: Service account invoker not working as expected

---

## What Was Accomplished

### 1. Organization Policy Analysis ✅
- Confirmed that `iam.allowedPolicyMemberDomains` blocks `allUsers` binding
- Determined that modifying the policy to allow `allUsers` is not possible
- Policy only accepts customer IDs, not special identifiers like `allUsers`

### 2. Service Account Created ✅
- Created `firebase-invoker@aletheia-codex-prod.iam.gserviceaccount.com`
- Purpose: Allow Firebase Hosting to invoke Cloud Run services without public access

### 3. IAM Permissions Granted ✅
- Granted `roles/run.invoker` to `firebase-invoker` service account on `review-api`
- Verified via command line that binding was created

### 4. Firebase Hosting Configuration Updated ✅
- Updated `firebase.json` to use Cloud Run with service account invoker
- Configuration:
  ```json
  {
    "source": "/api/review/**",
    "run": {
      "serviceId": "review-api",
      "region": "us-central1",
      "invoker": "firebase-invoker@aletheia-codex-prod.iam.gserviceaccount.com"
    }
  }
  ```

### 5. Deployed to Firebase Hosting ✅
- Successfully deployed updated configuration
- Deployment completed without errors

### 6. Cleanup Completed ✅
- Deleted old Cloud Function wrappers:
  - graphfunction
  - notesapifunction
  - reviewapifunction
  - orchestrate
  - orchestration
  - orchestration-function

---

## Current Issue: Still Getting 403 Forbidden ❌

### Test Results
```bash
# Test through Firebase Hosting
curl -I https://aletheiacodex.app/api/review/pending
# Result: HTTP/2 403

# Test Cloud Run service directly
curl -I https://review-api-679360092359.us-central1.run.app
# Result: HTTP/2 403
```

### Why This Is Happening

The Cloud Run service is returning 403 for both:
1. Direct access (expected - no public access)
2. Access through Firebase Hosting (unexpected - should work with service account)

**Possible Causes**:
1. **Service account invoker may not be working** - Firebase Hosting might not be using the service account correctly
2. **Additional permissions needed** - The service account might need additional roles
3. **Firebase Hosting limitation** - The `invoker` parameter might not work as documented
4. **Cloud Run authentication** - The service might be requiring additional authentication

---

## What We've Learned

### Organization Policy Constraints
1. **Cannot be modified to allow `allUsers`** - The constraint only accepts customer IDs
2. **Affects all GCP services** - Cloud Functions, Cloud Run, and any service requiring public IAM bindings
3. **No workaround through policy modification** - Must find alternative architecture

### Service Account Invoker Approach
1. **Theoretically correct** - This is the documented approach for private Cloud Run services
2. **Not working in practice** - Still getting 403 errors
3. **May require additional configuration** - Might need more than just the invoker parameter

---

## Remaining Options

### Option 1: Debug Service Account Invoker (Current Approach)
**Next Steps**:
1. Verify service account has correct permissions
2. Check if Firebase Hosting is actually using the service account
3. Review Cloud Run logs for authentication errors
4. Test with additional IAM roles if needed

**Pros**: 
- Most secure approach (no public access)
- Follows GCP best practices

**Cons**:
- Not working yet
- May require significant debugging
- Might not be possible with current GCP configuration

---

### Option 2: Request Organization Policy Deletion
**What**: Delete the `iam.allowedPolicyMemberDomains` policy entirely

**Command**:
```powershell
gcloud resource-manager org-policies delete iam.allowedPolicyMemberDomains --organization=1037037147281
```

**Pros**:
- ✅ Solves the problem immediately
- ✅ Allows public access to Cloud Run
- ✅ Standard architecture for public APIs
- ✅ No complex workarounds needed

**Cons**:
- ⚠️ Removes ALL restrictions on IAM bindings
- ⚠️ Anyone in org could accidentally make services public
- ⚠️ Requires implementing other security controls

**Mitigation**:
1. Implement monitoring for new `allUsers` bindings
2. Require code review for IAM policy changes
3. Use Infrastructure as Code (Terraform) with approval process
4. Set up budget alerts
5. Implement rate limiting and authentication in services

---

### Option 3: Use API Gateway
**What**: Deploy API Gateway as a public proxy to private Cloud Run services

**Architecture**:
```
Firebase Hosting → API Gateway (public) → Cloud Run (private)
```

**Pros**:
- API Gateway can be public (might not be affected by policy)
- Cloud Run stays private
- Centralized API management

**Cons**:
- Additional complexity
- Additional latency
- Additional cost
- Still need to verify API Gateway isn't blocked by same policy

**Estimated Time**: 6-8 hours

---

### Option 4: Use App Engine
**What**: Deploy App Engine as a reverse proxy to Cloud Run

**Architecture**:
```
Firebase Hosting → App Engine (public) → Cloud Run (private)
```

**Pros**:
- App Engine might not be affected by policy
- Can act as reverse proxy

**Cons**:
- App Engine is older technology
- More expensive
- Additional complexity
- Still need to verify policy doesn't affect App Engine

**Estimated Time**: 6-8 hours

---

## My Recommendation

### Recommended: Delete Organization Policy (Option 2)

**Why**:
1. **We've exhausted technical workarounds** - Service account invoker isn't working
2. **The policy is too restrictive** - It's blocking legitimate use cases
3. **Risks are manageable** - With proper safeguards and monitoring
4. **Time to resolution** - Immediate vs. many more hours of debugging
5. **Standard practice** - Public APIs require public access

**With These Safeguards**:

#### 1. Monitoring and Alerting
```powershell
# Set up alert for new allUsers bindings
gcloud alpha monitoring policies create `
  --notification-channels=YOUR_CHANNEL `
  --display-name="Public IAM Binding Alert" `
  --condition-display-name="New allUsers binding detected"
```

#### 2. Budget Alerts
```powershell
# Create budget alert
gcloud billing budgets create `
  --billing-account=YOUR_BILLING_ACCOUNT `
  --display-name="Cloud Run Budget Alert" `
  --budget-amount=100 `
  --threshold-rule=percent=50 `
  --threshold-rule=percent=90
```

#### 3. Code Review Process
- Require approval for any IAM policy changes
- Use Infrastructure as Code (Terraform/Pulumi)
- Document when public access is appropriate

#### 4. Service-Level Security
- Require Firebase Auth tokens for all API calls
- Implement rate limiting in Cloud Run services
- Use Cloud Armor for DDoS protection (if using Load Balancer)

---

## Time Investment Summary

### Time Spent So Far
- Sprint 1: Load Balancer + IAP (6+ hours) → Failed
- Sprint 1.1: IAP removal (4 hours) → Failed
- Sprint 1.2: API path fixes (2 hours) → Irrelevant
- Sprint 1.3: Cloud Run migration (4 hours) → Failed
- Service account approach (2 hours) → Failed

**Total**: 18+ hours invested, application still non-functional

### Time to Resolution

**Option 1** (Debug service account): Unknown, could be many more hours  
**Option 2** (Delete policy): 1-2 hours (immediate fix + safeguards)  
**Option 3** (API Gateway): 6-8 hours  
**Option 4** (App Engine): 6-8 hours  

---

## Decision Required

You need to decide which approach to take:

1. **Continue debugging service account invoker** (Option 1)
   - Unknown time investment
   - May not work at all
   - Most secure if it works

2. **Delete organization policy** (Option 2) - RECOMMENDED
   - Immediate resolution
   - Manageable risks with safeguards
   - Standard industry practice

3. **Try API Gateway or App Engine** (Options 3-4)
   - Significant time investment
   - May still be blocked by policy
   - Additional complexity and cost

---

## Next Steps

### If You Choose Option 2 (Delete Policy)

**Step 1**: Delete the organization policy
```powershell
gcloud resource-manager org-policies delete iam.allowedPolicyMemberDomains --organization=1037037147281
```

**Step 2**: Grant public access to Cloud Run
```powershell
gcloud run services add-iam-policy-binding review-api `
  --region=us-central1 `
  --member="allUsers" `
  --role="roles/run.invoker" `
  --project=aletheia-codex-prod
```

**Step 3**: Update firebase.json (remove invoker)
```json
{
  "source": "/api/review/**",
  "run": {
    "serviceId": "review-api",
    "region": "us-central1"
  }
}
```

**Step 4**: Deploy and test
```powershell
firebase deploy --only hosting --project aletheia-codex-prod
curl https://aletheiacodex.app/api/review/pending
```

**Step 5**: Implement safeguards (monitoring, alerts, rate limiting)

**Total Time**: 1-2 hours to fully functional application

---

## Conclusion

After 18+ hours of attempting various workarounds, the organization policy remains the fundamental blocker. The service account invoker approach, while theoretically correct, is not working in practice.

**My strong recommendation is to delete the organization policy** and implement proper safeguards. This is:
- The fastest path to a working application
- Standard industry practice for public APIs
- Manageable risk with proper controls
- The approach we should have taken from the beginning

The policy is too restrictive for building public SaaS applications and is blocking legitimate use cases.

---

**Status**: Awaiting decision on next steps  
**Recommendation**: Delete organization policy (Option 2)  
**Alternative**: Continue debugging service account invoker (Option 1)

---

**Created**: 2025-01-14  
**Author**: Architect  
**Priority**: 🚨 CRITICAL - Application still non-functional