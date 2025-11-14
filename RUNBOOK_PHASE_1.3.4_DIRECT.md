# RUNBOOK: Phase 1.3.4 - Cloud Run Service Update (Direct Approach)

## Overview

**Phase**: 1.3.4 - CLOUD RUN SERVICE UPDATE (DIRECT)  
**Priority**: P1 - URGENT  
**Duration**: 15 minutes  
**Responsibility**: HUMAN (Cloud Shell commands)  
**Environment**: Google Cloud Shell

**Note**: This runbook skips Phase 1.3.2 and 1.3.3 because the `constraints/run.managed.requireInvokerIam` constraint is not available in your GCP environment. We'll proceed directly to updating the Cloud Run service.

---

## Objective

Update the Cloud Run service to use the `--no-invoker-iam-check` flag, which allows public access without requiring the `allUsers` IAM binding, thus avoiding conflict with the Domain Restricted Sharing policy.

---

## Prerequisites

### Required Access
- [ ] Project Owner or Editor role for `aletheia-codex-prod`
- [ ] Access to Google Cloud Shell
- [ ] Phase 1.3.1 completed successfully (organization policy active)

### Verify Prerequisites

**Execute in Cloud Shell:**
```bash
# Verify organization policy is still active
gcloud resource-manager org-policies describe \
  iam.allowedPolicyMemberDomains \
  --organization=1037037147281

# Verify you have project access
gcloud projects get-iam-policy aletheia-codex-prod \
  --flatten="bindings[].members" \
  --filter="bindings.members:user:$(gcloud config get-value account)" \
  --format="table(bindings.role)"
```

---

## Step-by-Step Execution

### Step 1: Check Current Service Configuration

**Purpose**: Understand the current state of the review-api service.

**Execute in Cloud Shell:**
```bash
# Check current service details
gcloud run services describe review-api \
  --region=us-central1 \
  --project=aletheia-codex-prod \
  --format="yaml(spec.template.metadata.annotations,status.url)"
```

**Expected Output:**
```yaml
spec:
  template:
    metadata:
      annotations:
        run.googleapis.com/ingress: all
status:
  url: https://review-api-679360092359.us-central1.run.app
```

---

### Step 2: Remove Existing allUsers IAM Binding (If Exists)

**Purpose**: Remove any existing `allUsers` IAM binding before updating the service.

**Execute in Cloud Shell:**
```bash
# Check current IAM policy
echo "=== Current IAM Policy ==="
gcloud run services get-iam-policy review-api \
  --region=us-central1 \
  --project=aletheia-codex-prod

# If allUsers binding exists, remove it
echo ""
echo "=== Removing allUsers binding (if exists) ==="
gcloud run services remove-iam-policy-binding review-api \
  --region=us-central1 \
  --member="allUsers" \
  --role="roles/run.invoker" \
  --project=aletheia-codex-prod

# Note: This command may fail if binding doesn't exist - that's OK
```

**Expected Output (if binding exists):**
```
Updated IAM policy for service [review-api].
```

**Expected Output (if binding doesn't exist):**
```
ERROR: Policy binding with the specified member and role not found!
```

**Note**: Either output is acceptable. We just want to ensure no `allUsers` binding exists.

---

### Step 3: Update Cloud Run Service with --no-invoker-iam-check

**Purpose**: Update the service to disable the IAM invoker check, allowing public access without `allUsers` binding.

**⚠️ CRITICAL STEP**: This is the modern solution that bypasses the need for `allUsers` IAM binding.

**Execute in Cloud Shell:**
```bash
# Update the service to disable IAM check
gcloud run services update review-api \
  --region=us-central1 \
  --no-invoker-iam-check \
  --project=aletheia-codex-prod

# Wait for update to complete (should take 10-30 seconds)
```

**Expected Output:**
```
Deploying...
✓ Deploying... Done.
  ✓ Updating Service...
Done.
Service [review-api] revision [review-api-00012-xxx] has been deployed and is serving 100 percent of traffic.
Service URL: https://review-api-679360092359.us-central1.run.app
```

**Success Indicators:**
- ✅ No errors
- ✅ Shows "Done"
- ✅ New revision number (e.g., 00012)
- ✅ Service URL displayed

**If you see an error:**
- Check that you have Project Owner/Editor role
- Verify the service name is correct: `review-api`
- Ensure region is correct: `us-central1`

---

### Step 4: Verify Service Configuration

**Purpose**: Confirm the service is configured correctly with IAM check disabled.

**Execute in Cloud Shell:**
```bash
# Check service configuration
gcloud run services describe review-api \
  --region=us-central1 \
  --project=aletheia-codex-prod \
  --format="yaml(spec.template.metadata.annotations)"
```

**Expected Output:**
```yaml
spec:
  template:
    metadata:
      annotations:
        run.googleapis.com/ingress: all
        run.googleapis.com/ingress-status: all
```

**Verification Checklist:**
- [ ] `ingress: all` is present
- [ ] No errors in output

---

### Step 5: Verify No allUsers IAM Binding

**Purpose**: Confirm that no `allUsers` IAM binding exists (organization policy compliance).

**Execute in Cloud Shell:**
```bash
# Check IAM policy
echo "=== Checking IAM Policy ==="
gcloud run services get-iam-policy review-api \
  --region=us-central1 \
  --project=aletheia-codex-prod
```

**Expected Output:**
```yaml
bindings:
- members:
  - serviceAccount:superninja@aletheia-codex-prod.iam.gserviceaccount.com
  role: roles/run.invoker
etag: BwYXXXXXXXX
version: 1
```

**SUCCESS INDICATOR**: No `allUsers` in the output

**Verification Checklist:**
- [ ] No `allUsers` member in bindings
- [ ] Only service accounts or specific users listed
- [ ] Organization policy compliance maintained

---

### Step 6: Test API Endpoint (Should Still Require Auth)

**Purpose**: Test the API endpoint to see current behavior.

**Execute in Cloud Shell:**
```bash
# Test direct Cloud Run URL
echo "=== Testing Direct Cloud Run URL ==="
curl -s https://review-api-679360092359.us-central1.run.app/api/review/pending

echo ""
echo "=== Testing Firebase Hosting Proxy ==="
curl -s https://aletheiacodex.app/api/review/pending
```

**Expected Output:**
```
=== Testing Direct Cloud Run URL ===
{"error":"Missing Authorization header"}

=== Testing Firebase Hosting Proxy ===
{"error":"Missing Authorization header"}
```

**Note**: The "Missing Authorization header" error is **CORRECT** at this point. The service is accessible but requires authentication. Phase 1.3.5 will deploy the code with path routing fixes.

**Verification Checklist:**
- [ ] Returns JSON (not HTML or 503/403)
- [ ] Error is "Missing Authorization header"
- [ ] Both URLs work (direct and proxy)

---

## Validation Checklist - Phase 1.3.4

**Before proceeding to Phase 1.3.5, verify:**

- [ ] Service update completed successfully
- [ ] New revision deployed
- [ ] No `allUsers` IAM binding present
- [ ] Service returns JSON error (not 403/503)
- [ ] Both direct URL and proxy URL work
- [ ] Error message is "Missing Authorization header"
- [ ] Organization policy still active

---

## What Just Happened?

### Service Configuration

**BEFORE Phase 1.3.4:**
- Service: Requires IAM check
- Access: Blocked by organization policy
- IAM Binding: May have had `allUsers` (blocked)

**AFTER Phase 1.3.4:**
- Service: IAM check disabled (`--no-invoker-iam-check`)
- Access: Publicly accessible at network level
- IAM Binding: No `allUsers` (organization policy compliant)

### Security Posture

**Organization Level**: MAINTAINED ✅
- Domain Restricted Sharing still active
- No `allUsers` IAM bindings
- Organization-wide protection in place

**Service Level**: MODERN APPROACH ✅
- Public access via ingress (not IAM)
- No violation of organization policy
- Compliant with GCP best practices

### How This Works

The `--no-invoker-iam-check` flag tells Cloud Run:
1. **Don't check IAM** for incoming requests
2. **Allow all traffic** that passes ingress rules
3. **Bypass the need** for `allUsers` IAM binding
4. **Maintain compliance** with organization policies

This is the modern, recommended approach for public Cloud Run services when Domain Restricted Sharing is enforced.

---

## Troubleshooting

### Issue: "Permission denied" Error

**Symptoms:**
```
ERROR: (gcloud.run.services.update) User does not have permission
```

**Solution:**
```bash
# Verify your project roles
gcloud projects get-iam-policy aletheia-codex-prod \
  --flatten="bindings[].members" \
  --filter="bindings.members:user:$(gcloud config get-value account)"

# If you don't have owner/editor role, contact project admin
```

### Issue: Service Still Returns 403

**Symptoms:**
- curl returns 403 Forbidden
- Service was working before

**Solution:**
```bash
# Check service logs for errors
gcloud run services logs read review-api \
  --region=us-central1 \
  --project=aletheia-codex-prod \
  --limit=50

# Verify ingress settings
gcloud run services describe review-api \
  --region=us-central1 \
  --project=aletheia-codex-prod \
  --format="value(spec.template.metadata.annotations)"
```

### Issue: Update Command Fails

**Symptoms:**
```
ERROR: (gcloud.run.services.update) The service [review-api] could not be found
```

**Solution:**
```bash
# Verify service exists
gcloud run services list \
  --region=us-central1 \
  --project=aletheia-codex-prod

# Check if service is in different region
gcloud run services list --project=aletheia-codex-prod
```

---

## Rollback Procedure

**⚠️ ONLY USE IF ABSOLUTELY NECESSARY**

If the update causes issues:

```bash
# Rollback to previous revision
gcloud run services update-traffic review-api \
  --region=us-central1 \
  --to-revisions=PREVIOUS_REVISION=100 \
  --project=aletheia-codex-prod

# Check service logs for errors
gcloud run services logs read review-api \
  --region=us-central1 \
  --project=aletheia-codex-prod \
  --limit=50
```

---

## Next Steps

### Immediate
1. ✅ Phase 1.3.4 is complete
2. ⏭️ Proceed to Phase 1.3.5: Deploy Path Routing Fix
3. 📋 Phase 1.3.5 will deploy the code changes

### What Phase 1.3.5 Will Do
- Pull latest code from repository
- Deploy review-api with path routing fixes
- Test endpoints to verify they work
- Confirm no "Endpoint not found" errors

### Timeline
- Phase 1.3.1: ✅ Complete (~15 minutes)
- Phase 1.3.2: ⏭️ Skipped (constraint not available)
- Phase 1.3.3: ⏭️ Skipped (not needed)
- Phase 1.3.4: ✅ Complete (~15 minutes)
- Phase 1.3.5-1.3.8: ⏳ Remaining (~40 minutes)
- **Total remaining**: ~40 minutes

---

## Documentation

### Commands Executed
```bash
gcloud run services describe review-api --region=us-central1 --project=aletheia-codex-prod
gcloud run services get-iam-policy review-api --region=us-central1 --project=aletheia-codex-prod
gcloud run services remove-iam-policy-binding review-api --region=us-central1 --member="allUsers" --role="roles/run.invoker" --project=aletheia-codex-prod
gcloud run services update review-api --region=us-central1 --no-invoker-iam-check --project=aletheia-codex-prod
curl -s https://review-api-679360092359.us-central1.run.app/api/review/pending
curl -s https://aletheiacodex.app/api/review/pending
```

### Service Configuration
- **Service**: review-api
- **Region**: us-central1
- **Project**: aletheia-codex-prod
- **IAM Check**: Disabled
- **Ingress**: All
- **IAM Binding**: No allUsers

---

## Sign-Off

**Phase 1.3.4 Completion Checklist:**

- [ ] Service update completed successfully
- [ ] New revision deployed
- [ ] No `allUsers` IAM binding
- [ ] Service accessible (returns JSON)
- [ ] Organization policy still active
- [ ] All validation checks passed
- [ ] Ready to proceed to Phase 1.3.5

**Completed By**: _______________________

**Date**: _______________________

**Time**: _______________________

**New Revision**: _______________________

**Notes**: _______________________

---

## Quick Reference

### Key Information
- **Service**: review-api
- **Region**: us-central1
- **Project**: aletheia-codex-prod
- **Service URL**: https://review-api-679360092359.us-central1.run.app
- **Proxy URL**: https://aletheiacodex.app/api/review/*

### Key Commands
```bash
# View service details
gcloud run services describe review-api \
  --region=us-central1 \
  --project=aletheia-codex-prod

# View IAM policy
gcloud run services get-iam-policy review-api \
  --region=us-central1 \
  --project=aletheia-codex-prod

# Test endpoint
curl -s https://aletheiacodex.app/api/review/pending

# View logs
gcloud run services logs read review-api \
  --region=us-central1 \
  --project=aletheia-codex-prod \
  --limit=50
```

---

**END OF PHASE 1.3.4 RUNBOOK**

**Next**: [RUNBOOK_PHASE_1.3.5.md](RUNBOOK_PHASE_1.3.5.md)