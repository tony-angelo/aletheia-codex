# RUNBOOK: Phase 1.3.1 - Immediate Containment

## Overview

**Phase**: 1.3.1 - IMMEDIATE CONTAINMENT  
**Priority**: P0 - CRITICAL  
**Duration**: 15 minutes  
**Responsibility**: HUMAN (requires Organization Administrator privileges)  
**Environment**: Google Cloud Shell

---

## Objective

Re-enable the `iam.allowedPolicyMemberDomains` organization policy to restore the security baseline for the entire GCP organization.

---

## Prerequisites

### Required Access
- [ ] GCP Organization Administrator role
- [ ] Access to Google Cloud Shell
- [ ] Organization ID: `1037037147281`

### Verify Your Access

**Open Google Cloud Shell and run:**
```bash
# Check if you have org admin access
gcloud organizations get-iam-policy 1037037147281 \
  --flatten="bindings[].members" \
  --filter="bindings.role:roles/resourcemanager.organizationAdmin" \
  --format="table(bindings.members)"
```

**Expected Output**: Should show your email address

**If you don't have access**: Contact your GCP Organization Administrator before proceeding.

---

## Step-by-Step Execution

### Step 1: Get Google Workspace Customer ID

**Purpose**: Identify your organization's Customer ID to configure the policy correctly.

**Execute in Cloud Shell:**
```bash
# List organizations and get Customer ID
gcloud organizations list
```

**Expected Output:**
```
DISPLAY_NAME       ID              DIRECTORY_CUSTOMER_ID
Your Org Name      1037037147281   C03qt98jf
```

**Action**: 
- Note down the `DIRECTORY_CUSTOMER_ID` value (e.g., `C03qt98jf`)
- You will use this in the next step

**Record here**: `DIRECTORY_CUSTOMER_ID = ___________________`

---

### Step 2: Create Policy File

**Purpose**: Create the organization policy configuration file.

**Execute in Cloud Shell:**
```bash
# Navigate to home directory
cd ~

# Create policy file with placeholder
cat > policy-drs-re-enable.yaml << 'EOF'
constraint: constraints/iam.allowedPolicyMemberDomains
listPolicy:
  allowedValues:
  - REPLACE_WITH_CUSTOMER_ID
EOF

# Display the file to verify
cat policy-drs-re-enable.yaml
```

**Expected Output:**
```yaml
constraint: constraints/iam.allowedPolicyMemberDomains
listPolicy:
  allowedValues:
  - REPLACE_WITH_CUSTOMER_ID
```

---

### Step 3: Replace Customer ID in Policy File

**Purpose**: Insert your actual Customer ID into the policy file.

**Execute in Cloud Shell:**
```bash
# Replace the placeholder with your actual Customer ID
# IMPORTANT: Replace C03qt98jf with YOUR Customer ID from Step 1
sed -i 's/REPLACE_WITH_CUSTOMER_ID/C03qt98jf/g' policy-drs-re-enable.yaml

# Verify the replacement worked
cat policy-drs-re-enable.yaml
```

**Expected Output:**
```yaml
constraint: constraints/iam.allowedPolicyMemberDomains
listPolicy:
  allowedValues:
  - C03qt98jf  # Your actual Customer ID
```

**Verification Checklist:**
- [ ] File shows your actual Customer ID (not REPLACE_WITH_CUSTOMER_ID)
- [ ] Customer ID format is correct (starts with 'C' followed by alphanumeric)
- [ ] Organization ID is correct (1037037147281)

---

### Step 4: Apply Organization Policy

**Purpose**: Apply the policy at the organization level to restore security.

**⚠️ WARNING**: This will temporarily break the AletheiaCodex application. This is expected and necessary.

**Execute in Cloud Shell:**
```bash
# Apply the policy at organization level
gcloud resource-manager org-policies set-policy policy-drs-re-enable.yaml \
  --organization=1037037147281

# Wait for confirmation message
```

**Expected Output:**
```
Updated policy [iam.allowedPolicyMemberDomains] for organization [1037037147281].
```

**If you see an error:**
- Check that you have Organization Administrator role
- Verify the policy file syntax is correct
- Ensure Customer ID is valid

---

### Step 5: Verify Policy Was Applied

**Purpose**: Confirm the policy is active and correctly configured.

**Execute in Cloud Shell:**
```bash
# Verify the policy was applied
gcloud resource-manager org-policies describe \
  iam.allowedPolicyMemberDomains \
  --organization=1037037147281
```

**Expected Output:**
```yaml
constraint: constraints/iam.allowedPolicyMemberDomains
listPolicy:
  allowedValues:
  - C03qt98jf  # Your Customer ID
etag: BwYXXXXXXXX
updateTime: '2025-11-14T...'
```

**Verification Checklist:**
- [ ] Policy shows your Customer ID in `allowedValues`
- [ ] No errors in the output
- [ ] `updateTime` shows recent timestamp

---

### Step 6: Verify Application Status (Expected Failure)

**Purpose**: Confirm the application is now blocked (this is correct and expected).

**Execute in Cloud Shell:**
```bash
# Test the review-api endpoint
echo "Testing review-api endpoint..."
curl -s https://aletheiacodex.app/api/review/pending

echo ""
echo "Testing direct Cloud Run URL..."
curl -s https://review-api-679360092359.us-central1.run.app/api/review/pending
```

**Expected Output (ONE OF THESE):**
```
Service Unavailable
```
OR
```
{"error":"Missing Authorization header"}
```
OR
```
403 Forbidden
```

**⚠️ IMPORTANT**: 
- If you see an error, **this is CORRECT and EXPECTED**
- The application is supposed to be broken at this point
- This confirms the organization policy is working
- We will fix this in Phase 1.3.2

**Verification Checklist:**
- [ ] Application returns an error (not working)
- [ ] Error is one of: 503, 403, or "Missing Authorization header"
- [ ] This confirms policy is enforced

---

## Validation Checklist - Phase 1.3.1

**Before proceeding to Phase 1.3.2, verify:**

- [ ] Organization policy successfully applied
- [ ] Policy verification shows correct Customer ID
- [ ] Application returns error (expected - temporary breakage)
- [ ] No errors during policy application
- [ ] Policy file saved in `~/policy-drs-re-enable.yaml`

---

## What Just Happened?

### Security Status

**BEFORE Phase 1.3.1:**
- ❌ Organization policy: DELETED
- ❌ Security posture: CRITICAL
- ❌ Blast radius: Organization-wide vulnerability
- ✅ Application: Working (but insecure)

**AFTER Phase 1.3.1:**
- ✅ Organization policy: ENFORCED
- ✅ Security posture: RESTORED
- ✅ Blast radius: CONTAINED
- ⚠️ Application: Broken (temporarily, by design)

### What Changed?

1. **Organization Policy Re-enabled**: The `iam.allowedPolicyMemberDomains` constraint is now active
2. **Domain Restriction Active**: Only principals from your Google Workspace domain can be added to IAM policies
3. **allUsers Blocked**: The `allUsers` principal can no longer be granted access
4. **Application Blocked**: The review-api service cannot be accessed because it was using `allUsers`

### Why This Is Correct

- The organization is now protected from identity misconfiguration
- The organization is now protected from data exfiltration attacks
- The security baseline has been restored
- The application breakage is temporary and will be fixed in Phase 1.3.2

---

## Troubleshooting

### Issue: "Permission denied" Error

**Symptoms:**
```
ERROR: (gcloud.resource-manager.org-policies.set-policy) User does not have permission to access organization [1037037147281]
```

**Solution:**
```bash
# Verify your roles
gcloud organizations get-iam-policy 1037037147281 \
  --flatten="bindings[].members" \
  --filter="bindings.members:user:YOUR_EMAIL@domain.com"

# If you don't have organizationAdmin role, contact your org admin
```

### Issue: "Invalid Customer ID" Error

**Symptoms:**
```
ERROR: Invalid value for allowedValues
```

**Solution:**
```bash
# Re-check your Customer ID
gcloud organizations list

# Verify the format (should start with 'C' followed by alphanumeric)
# Re-create the policy file with correct Customer ID
```

### Issue: Policy File Syntax Error

**Symptoms:**
```
ERROR: Failed to parse policy file
```

**Solution:**
```bash
# Verify YAML syntax
cat policy-drs-re-enable.yaml

# Check for:
# - Correct indentation (2 spaces)
# - No tabs (use spaces only)
# - Correct structure (name, spec, rules, values, allowedValues)

# If needed, recreate the file from Step 2
```

### Issue: Application Still Works After Policy Applied

**Symptoms:**
- Application returns data instead of error
- No 403 or 503 errors

**This is UNEXPECTED**. Possible causes:
1. Policy hasn't propagated yet (wait 2-3 minutes)
2. Policy wasn't applied correctly (verify in Step 5)
3. Service is using a different authentication method

**Solution:**
```bash
# Wait 3 minutes for policy propagation
sleep 180

# Test again
curl -s https://aletheiacodex.app/api/review/pending

# If still working, verify policy
gcloud resource-manager org-policies describe \
  iam.allowedPolicyMemberDomains \
  --organization=1037037147281

# Check if policy shows your Customer ID
```

---

## Rollback Procedure

**⚠️ ONLY USE IF ABSOLUTELY NECESSARY**

If you need to rollback (e.g., critical business need, wrong organization):

```bash
# Delete the organization policy (returns to previous state)
gcloud resource-manager org-policies delete \
  iam.allowedPolicyMemberDomains \
  --organization=1037037147281

# Confirm deletion
gcloud resource-manager org-policies describe \
  iam.allowedPolicyMemberDomains \
  --organization=1037037147281

# Expected: "Policy not found" or empty response
```

**⚠️ WARNING**: Rollback returns the organization to the vulnerable state. Only use if:
- You applied the policy to the wrong organization
- There is a critical business emergency
- You have explicit approval from security leadership

---

## Next Steps

### Immediate
1. ✅ Phase 1.3.1 is complete
2. ⏭️ Proceed to Phase 1.3.2: Project-Level Policy Configuration
3. 📋 Phase 1.3.2 will restore application functionality securely

### What Phase 1.3.2 Will Do
- Configure project-level policy to allow Cloud Run IAM bypass
- Does NOT compromise organization security
- Scoped only to `aletheia-codex-prod` project
- Uses modern GCP security pattern

### Timeline
- Phase 1.3.1: ✅ Complete (~15 minutes)
- Phase 1.3.2: ⏭️ Next (~10 minutes)
- Phase 1.3.3-1.3.8: ⏳ Remaining (~55 minutes)
- **Total remaining**: ~65 minutes

---

## Documentation

### Files Created
- `~/policy-drs-re-enable.yaml` - Organization policy configuration

### Commands Executed
```bash
gcloud organizations list
cat > policy-drs-re-enable.yaml << 'EOF' ... EOF
sed -i 's/REPLACE_WITH_CUSTOMER_ID/C03qt98jf/g' policy-drs-re-enable.yaml
gcloud resource-manager org-policies set-policy policy-drs-re-enable.yaml
gcloud resource-manager org-policies describe iam.allowedPolicyMemberDomains --organization=1037037147281
curl -s https://aletheiacodex.app/api/review/pending
```

### Policy Applied
- **Constraint**: `iam.allowedPolicyMemberDomains`
- **Scope**: Organization `1037037147281`
- **Effect**: Restricts IAM bindings to Customer ID only
- **Status**: ACTIVE

---

## Sign-Off

**Phase 1.3.1 Completion Checklist:**

- [ ] Customer ID obtained and verified
- [ ] Policy file created with correct Customer ID
- [ ] Organization policy applied successfully
- [ ] Policy verification completed
- [ ] Application confirmed broken (expected)
- [ ] All validation checks passed
- [ ] Ready to proceed to Phase 1.3.2

**Completed By**: _______________________

**Date**: _______________________

**Time**: _______________________

**Customer ID Used**: _______________________

**Notes**: _______________________

---

## Quick Reference

### Key Information
- **Organization ID**: `1037037147281`
- **Policy Name**: `iam.allowedPolicyMemberDomains`
- **Policy File**: `~/policy-drs-re-enable.yaml`
- **Your Customer ID**: `___________________` (fill in)

### Key Commands
```bash
# View policy
gcloud resource-manager org-policies describe \
  iam.allowedPolicyMemberDomains \
  --organization=1037037147281

# Test application
curl -s https://aletheiacodex.app/api/review/pending

# View policy file
cat ~/policy-drs-re-enable.yaml
```

---

**END OF PHASE 1.3.1 RUNBOOK**

**Next**: [RUNBOOK_PHASE_1.3.2.md](RUNBOOK_PHASE_1.3.2.md)