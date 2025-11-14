# RUNBOOK: Phase 1.3.2 - Project-Level Policy Configuration

## Overview

**Phase**: 1.3.2 - PROJECT-LEVEL POLICY CONFIGURATION  
**Priority**: P1 - URGENT  
**Duration**: 10 minutes  
**Responsibility**: HUMAN (requires Project Owner/Editor privileges)  
**Environment**: Google Cloud Shell

---

## Objective

Configure project-level organization policy to allow Cloud Run services in the `aletheia-codex-prod` project to disable IAM checks, enabling public access without violating the organization-level Domain Restricted Sharing policy.

---

## Prerequisites

### Required Access
- [ ] Project Owner or Editor role for `aletheia-codex-prod`
- [ ] Access to Google Cloud Shell
- [ ] Phase 1.3.1 completed successfully

### Verify Your Access

**Open Google Cloud Shell and run:**
```bash
# Check if you have project-level access
gcloud projects get-iam-policy aletheia-codex-prod \
  --flatten="bindings[].members" \
  --filter="bindings.members:user:$(gcloud config get-value account)" \
  --format="table(bindings.role)"
```

**Expected Output**: Should show roles like `roles/owner` or `roles/editor`

---

## Step-by-Step Execution

### Step 1: Verify Phase 1.3.1 Completion

**Purpose**: Confirm the organization policy is active before proceeding.

**Execute in Cloud Shell:**
```bash
# Verify organization policy is active
gcloud resource-manager org-policies describe \
  iam.allowedPolicyMemberDomains \
  --organization=1037037147281
```

**Expected Output:**
```yaml
constraint: constraints/iam.allowedPolicyMemberDomains
etag: CPSH3cgGEMiN2fQB
listPolicy:
  allowedValues:
  - C03z7bnok
updateTime: '2025-11-14T15:00:04.513165Z'
```

**Verification Checklist:**
- [ ] Policy shows your Customer ID (C03z7bnok)
- [ ] updateTime is recent (from Phase 1.3.1)
- [ ] No errors in output

**If this fails**: Go back and complete Phase 1.3.1 first.

---

### Step 2: Create Project-Level Policy File

**Purpose**: Create the policy that allows Cloud Run services in this project to disable IAM checks.

**Execute in Cloud Shell:**
```bash
# Navigate to home directory
cd ~

# Create project-level policy file
cat > policy-run-iam-override.yaml << 'EOF'
constraint: constraints/run.managed.requireInvokerIam
booleanPolicy:
  enforced: false
EOF

# Display the file to verify
cat policy-run-iam-override.yaml
```

**Expected Output:**
```yaml
constraint: constraints/run.managed.requireInvokerIam
booleanPolicy:
  enforced: false
```

**What This Does:**
- Sets `run.managed.requireInvokerIam` to `false` for this project only
- Allows Cloud Run services to use `--no-invoker-iam-check` flag
- Does NOT affect organization-level security
- Scoped only to `aletheia-codex-prod` project

---

### Step 3: Apply Project-Level Policy

**Purpose**: Apply the policy to the `aletheia-codex-prod` project.

**Execute in Cloud Shell:**
```bash
# Apply the policy at project level
gcloud resource-manager org-policies set-policy \
  policy-run-iam-override.yaml \
  --project=aletheia-codex-prod

# Wait for confirmation message
```

**Expected Output:**
```
constraint: constraints/run.managed.requireInvokerIam
booleanPolicy:
  enforced: false
etag: BwYXXXXXXXX
updateTime: '2025-11-14T15:XX:XX.XXXXXXZ'
```

**Success Indicators:**
- ✅ No errors
- ✅ Shows `enforced: false`
- ✅ Has etag and updateTime

**If you see an error:**
- Check that you have Project Owner/Editor role
- Verify project ID is correct: `aletheia-codex-prod`
- Ensure policy file syntax is correct

---

### Step 4: Verify Project-Level Policy

**Purpose**: Confirm the policy was applied correctly.

**Execute in Cloud Shell:**
```bash
# Verify the policy was applied
gcloud resource-manager org-policies describe \
  run.managed.requireInvokerIam \
  --project=aletheia-codex-prod
```

**Expected Output:**
```yaml
constraint: constraints/run.managed.requireInvokerIam
booleanPolicy:
  enforced: false
etag: BwYXXXXXXXX
updateTime: '2025-11-14T15:XX:XX.XXXXXXZ'
```

**Verification Checklist:**
- [ ] Constraint is `constraints/run.managed.requireInvokerIam`
- [ ] `enforced: false` is shown
- [ ] etag and updateTime are present
- [ ] No errors in output

---

### Step 5: Verify Application Status (Still Requires Auth)

**Purpose**: Confirm the application still requires authentication (no change yet).

**Execute in Cloud Shell:**
```bash
# Test the review-api endpoint
echo "Testing review-api endpoint..."
curl -s https://aletheiacodex.app/api/review/pending

echo ""
echo "Testing direct Cloud Run URL..."
curl -s https://review-api-679360092359.us-central1.run.app/api/review/pending
```

**Expected Output:**
```
Testing review-api endpoint...
{"error":"Missing Authorization header"}

Testing direct Cloud Run URL...
{"error":"Missing Authorization header"}
```

**Note**: The application should still require authentication at this point. This is correct. Phase 1.3.4 will update the Cloud Run service to use the new policy.

---

## Validation Checklist - Phase 1.3.2

**Before proceeding to Phase 1.3.3, verify:**

- [ ] Organization policy still active (from Phase 1.3.1)
- [ ] Project-level policy successfully applied
- [ ] Policy verification shows `enforced: false`
- [ ] Application still requires authentication (unchanged)
- [ ] No errors during policy application
- [ ] Policy file saved in `~/policy-run-iam-override.yaml`

---

## What Just Happened?

### Policy Hierarchy

**Organization Level** (Phase 1.3.1):
- Policy: `iam.allowedPolicyMemberDomains`
- Effect: Restricts IAM bindings to Customer ID only
- Scope: ALL projects in organization
- Status: ENFORCED ✅

**Project Level** (Phase 1.3.2):
- Policy: `run.managed.requireInvokerIam`
- Effect: Allows Cloud Run services to disable IAM check
- Scope: ONLY `aletheia-codex-prod` project
- Status: DISABLED (enforced: false) ✅

### Security Posture

**Organization Security**: MAINTAINED ✅
- Domain Restricted Sharing still active
- No `allUsers` IAM bindings allowed
- Organization-wide protection in place

**Project Flexibility**: ENABLED ✅
- Cloud Run services can use `--no-invoker-iam-check`
- Modern security pattern available
- Scoped to single project only

### What's Next?

Phase 1.3.3 will verify the code is ready for deployment.
Phase 1.3.4 will update the Cloud Run service to use this new policy.

---

## Troubleshooting

### Issue: "Permission denied" Error

**Symptoms:**
```
ERROR: (gcloud.resource-manager.org-policies.set-policy) User does not have permission to access project [aletheia-codex-prod]
```

**Solution:**
```bash
# Verify your project roles
gcloud projects get-iam-policy aletheia-codex-prod \
  --flatten="bindings[].members" \
  --filter="bindings.members:user:$(gcloud config get-value account)"

# If you don't have owner/editor role, contact project admin
```

### Issue: Policy File Syntax Error

**Symptoms:**
```
ERROR: Failed to parse policy file
```

**Solution:**
```bash
# Verify YAML syntax
cat policy-run-iam-override.yaml

# Check for:
# - Correct indentation (2 spaces)
# - No tabs (use spaces only)
# - Correct structure (constraint, booleanPolicy, enforced)

# If needed, recreate the file from Step 2
```

### Issue: Wrong Project

**Symptoms:**
```
ERROR: Project [wrong-project-id] not found
```

**Solution:**
```bash
# Verify current project
gcloud config get-value project

# Set correct project
gcloud config set project aletheia-codex-prod

# Retry the command
```

---

## Rollback Procedure

**⚠️ ONLY USE IF ABSOLUTELY NECESSARY**

If you need to rollback (e.g., wrong project, policy conflict):

```bash
# Delete the project-level policy (returns to default)
gcloud resource-manager org-policies delete \
  run.managed.requireInvokerIam \
  --project=aletheia-codex-prod

# Confirm deletion
gcloud resource-manager org-policies describe \
  run.managed.requireInvokerIam \
  --project=aletheia-codex-prod

# Expected: "Policy not found" or empty response
```

**Note**: Rollback only affects this project. Organization policy remains active.

---

## Next Steps

### Immediate
1. ✅ Phase 1.3.2 is complete
2. ⏭️ Proceed to Phase 1.3.3: Code Preparation and Verification
3. 📋 Phase 1.3.3 will verify all code fixes are in place

### What Phase 1.3.3 Will Do
- Verify `.python-version` file exists
- Verify `Procfile` exists
- Verify path routing fix is in place
- Verify all dependencies are correct
- Prepare for deployment in Phase 1.3.4

### Timeline
- Phase 1.3.1: ✅ Complete (~15 minutes)
- Phase 1.3.2: ✅ Complete (~10 minutes)
- Phase 1.3.3-1.3.8: ⏳ Remaining (~55 minutes)
- **Total remaining**: ~55 minutes

---

## Documentation

### Files Created
- `~/policy-run-iam-override.yaml` - Project-level policy configuration

### Commands Executed
```bash
gcloud resource-manager org-policies describe iam.allowedPolicyMemberDomains --organization=1037037147281
cat > policy-run-iam-override.yaml << 'EOF' ... EOF
gcloud resource-manager org-policies set-policy policy-run-iam-override.yaml --project=aletheia-codex-prod
gcloud resource-manager org-policies describe run.managed.requireInvokerIam --project=aletheia-codex-prod
curl -s https://aletheiacodex.app/api/review/pending
```

### Policies Applied
- **Constraint**: `run.managed.requireInvokerIam`
- **Scope**: Project `aletheia-codex-prod`
- **Effect**: Allows Cloud Run services to disable IAM check
- **Status**: ACTIVE (enforced: false)

---

## Sign-Off

**Phase 1.3.2 Completion Checklist:**

- [ ] Organization policy verified active
- [ ] Project-level policy file created
- [ ] Project-level policy applied successfully
- [ ] Policy verification completed
- [ ] Application status unchanged (still requires auth)
- [ ] All validation checks passed
- [ ] Ready to proceed to Phase 1.3.3

**Completed By**: _______________________

**Date**: _______________________

**Time**: _______________________

**Notes**: _______________________

---

## Quick Reference

### Key Information
- **Organization ID**: `1037037147281`
- **Project ID**: `aletheia-codex-prod`
- **Policy Name**: `run.managed.requireInvokerIam`
- **Policy File**: `~/policy-run-iam-override.yaml`
- **Policy Effect**: `enforced: false`

### Key Commands
```bash
# View project policy
gcloud resource-manager org-policies describe \
  run.managed.requireInvokerIam \
  --project=aletheia-codex-prod

# View organization policy
gcloud resource-manager org-policies describe \
  iam.allowedPolicyMemberDomains \
  --organization=1037037147281

# Test application
curl -s https://aletheiacodex.app/api/review/pending

# View policy file
cat ~/policy-run-iam-override.yaml
```

---

**END OF PHASE 1.3.2 RUNBOOK**

**Next**: [RUNBOOK_PHASE_1.3.3.md](RUNBOOK_PHASE_1.3.3.md)