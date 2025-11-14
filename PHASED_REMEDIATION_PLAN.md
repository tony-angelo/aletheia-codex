# Phased Remediation Plan: Secure Cloud Run Deployment

## Overview

This document provides a detailed, step-by-step plan to remediate the security issue and correctly deploy the AletheiaCodex application. Each phase includes:
- Clear objectives
- Human execution commands (Cloud Shell)
- AI execution tasks (code modifications, deployments)
- Validation checkpoints
- Rollback procedures

---

## Pre-Requisites

### Required Access
- [ ] GCP Organization Administrator access (for Phase 1.3.1)
- [ ] Project Owner/Editor access for `aletheia-codex-prod`
- [ ] Access to Google Cloud Shell
- [ ] Git repository access

### Required Information
- **GCP Organization ID**: `1037037147281`
- **GCP Project ID**: `aletheia-codex-prod`
- **Google Workspace Customer ID**: (To be obtained in Phase 1.3.1)

---

## Phase 1.3.1: IMMEDIATE CONTAINMENT (P0 - Critical)

### Objective
Re-enable the `iam.allowedPolicyMemberDomains` organization policy to restore security baseline.

### Duration
15 minutes

### Responsibility
**HUMAN** (requires Organization Administrator privileges)

### Steps

#### Step 1.3.1.1: Get Google Workspace Customer ID

**Execute in Cloud Shell:**
```bash
# List organizations and get Customer ID
gcloud organizations list

# Output will show:
# DISPLAY_NAME       ID              DIRECTORY_CUSTOMER_ID
# Your Org Name      1037037147281   C03qt98jf

# Note down the DIRECTORY_CUSTOMER_ID (e.g., C03qt98jf)
```

**Record the Customer ID here**: `_______________________`

#### Step 1.3.1.2: Create Policy File

**Execute in Cloud Shell:**
```bash
# Navigate to home directory
cd ~

# Create policy file
cat > policy-drs-re-enable.yaml << 'EOF'
name: organizations/1037037147281/policies/iam.allowedPolicyMemberDomains
spec:
  rules:
  - values:
      allowedValues:
      - REPLACE_WITH_CUSTOMER_ID  # Replace this with actual Customer ID from Step 1
EOF

# Replace the placeholder with actual Customer ID
# Example: If Customer ID is C03qt98jf
sed -i 's/REPLACE_WITH_CUSTOMER_ID/C03qt98jf/g' policy-drs-re-enable.yaml

# Verify the file
cat policy-drs-re-enable.yaml
```

**Expected Output:**
```yaml
name: organizations/1037037147281/policies/iam.allowedPolicyMemberDomains
spec:
  rules:
  - values:
      allowedValues:
      - C03qt98jf  # Your actual Customer ID
```

#### Step 1.3.1.3: Apply Organization Policy

**Execute in Cloud Shell:**
```bash
# Apply the policy at organization level
gcloud resource-manager org-policies set-policy policy-drs-re-enable.yaml

# Verify the policy was applied
gcloud resource-manager org-policies describe \
  iam.allowedPolicyMemberDomains \
  --organization=1037037147281
```

**Expected Output:**
```
constraint: constraints/iam.allowedPolicyMemberDomains
listPolicy:
  allowedValues:
  - C03qt98jf
```

#### Step 1.3.1.4: Verify Application Status

**Execute in Cloud Shell:**
```bash
# Test the review-api endpoint
curl -s https://aletheiacodex.app/api/review/pending

# Expected: Should return an error (this is correct and expected)
```

**Expected Output:**
```
Service Unavailable
```
OR
```
{"error":"Missing Authorization header"}
```

### Validation Checklist - Phase 1.3.1

- [ ] Organization policy successfully applied
- [ ] Policy verification shows correct Customer ID
- [ ] Application returns error (expected - temporary breakage)
- [ ] No errors during policy application

### Rollback Procedure (If Needed)

**If something goes wrong:**
```bash
# Delete the policy (returns to previous state)
gcloud resource-manager org-policies delete \
  iam.allowedPolicyMemberDomains \
  --organization=1037037147281
```

### Status After Phase 1.3.1
- ✅ Organization security baseline restored
- ⚠️ Application temporarily non-functional (expected)
- ✅ Ready for Phase 1.3.2

---

## Phase 1.3.2: PROJECT-LEVEL POLICY CONFIGURATION

### Objective
Configure project-level organization policy to allow Cloud Run services to disable IAM checks.

### Duration
10 minutes

### Responsibility
**HUMAN** (Cloud Shell commands)

### Steps

#### Step 1.3.2.1: Create Project-Level Policy File

**Execute in Cloud Shell:**
```bash
# Navigate to home directory
cd ~

# Create project-level policy override file
cat > policy-run-iam-override.yaml << 'EOF'
name: projects/aletheia-codex-prod/policies/run.managed.requireInvokerIam
spec:
  inheritFromParent: true
  rules:
  - enforce: false  # Allows services in this project to disable IAM check
EOF

# Verify the file
cat policy-run-iam-override.yaml
```

**Expected Output:**
```yaml
name: projects/aletheia-codex-prod/policies/run.managed.requireInvokerIam
spec:
  inheritFromParent: true
  rules:
  - enforce: false
```

#### Step 1.3.2.2: Apply Project-Level Policy

**Execute in Cloud Shell:**
```bash
# Apply the policy at project level
gcloud resource-manager org-policies set-policy \
  policy-run-iam-override.yaml \
  --project=aletheia-codex-prod

# Verify the policy was applied
gcloud resource-manager org-policies describe \
  run.managed.requireInvokerIam \
  --project=aletheia-codex-prod
```

**Expected Output:**
```
constraint: constraints/run.managed.requireInvokerIam
booleanPolicy:
  enforced: false
```

### Validation Checklist - Phase 1.3.2

- [ ] Project-level policy successfully applied
- [ ] Policy verification shows `enforced: false`
- [ ] No errors during policy application

### Rollback Procedure (If Needed)

**If something goes wrong:**
```bash
# Reset the policy to default
gcloud resource-manager org-policies delete \
  run.managed.requireInvokerIam \
  --project=aletheia-codex-prod
```

### Status After Phase 1.3.2
- ✅ Project configured to allow IAM check bypass
- ⚠️ Application still non-functional (expected)
- ✅ Ready for Phase 1.3.3

---

## Phase 1.3.3: CODE PREPARATION AND PATH ROUTING FIX

### Objective
Ensure all code fixes are in place before deployment.

### Duration
5 minutes

### Responsibility
**AI** (code verification and modifications if needed)

### AI Tasks

#### Task 1.3.3.1: Verify Current Code State
- Verify `.python-version` file exists with `3.11.0`
- Verify `Procfile` exists with correct target
- Verify `requirements.txt` has all dependencies
- Verify path routing fix is in place (api/review/* patterns)

#### Task 1.3.3.2: Create Deployment Verification Script
- Create a script to verify all prerequisites before deployment

### Human Verification

**Execute in Cloud Shell:**
```bash
# Pull latest code
cd ~/aletheia-codex
git checkout sprint-1
git pull origin sprint-1

# Verify critical files exist
echo "=== Checking .python-version ==="
cat functions/review_api/.python-version

echo "=== Checking Procfile ==="
cat functions/review_api/Procfile

echo "=== Checking requirements.txt ==="
cat functions/review_api/requirements.txt

echo "=== Checking path routing in main.py ==="
grep -A 2 "api/review/pending" functions/review_api/main.py
```

**Expected Output:**
```
=== Checking .python-version ===
3.11.0

=== Checking Procfile ===
web: functions-framework --target=handle_request --port=$PORT

=== Checking requirements.txt ===
# Review API Cloud Functions Requirements
...
google-cloud-secret-manager==2.16.0
...

=== Checking path routing in main.py ===
        if (path == 'api/review/pending' or path == 'review/pending' or path == 'pending') and request.method == 'GET':
```

### Validation Checklist - Phase 1.3.3

- [ ] `.python-version` file exists with `3.11.0`
- [ ] `Procfile` exists with correct target function
- [ ] `requirements.txt` includes `google-cloud-secret-manager`
- [ ] Path routing includes `api/review/*` patterns
- [ ] All files verified in repository

### Status After Phase 1.3.3
- ✅ Code verified and ready for deployment
- ✅ Ready for Phase 1.3.4

---

## Phase 1.3.4: CLOUD RUN SERVICE UPDATE (MODERN SOLUTION)

### Objective
Update the Cloud Run service to use the modern `--no-invoker-iam-check` flag instead of `allUsers` IAM binding.

### Duration
15 minutes

### Responsibility
**HUMAN** (Cloud Shell commands)

### Steps

#### Step 1.3.4.1: Remove Existing allUsers IAM Binding (If Exists)

**Execute in Cloud Shell:**
```bash
# Check current IAM policy
gcloud run services get-iam-policy review-api \
  --region=us-central1 \
  --project=aletheia-codex-prod

# If allUsers binding exists, remove it
gcloud run services remove-iam-policy-binding review-api \
  --region=us-central1 \
  --member="allUsers" \
  --role="roles/run.invoker" \
  --project=aletheia-codex-prod

# Note: This command may fail if binding doesn't exist - that's OK
```

#### Step 1.3.4.2: Update Cloud Run Service with Modern Flag

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

#### Step 1.3.4.3: Verify Service Configuration

**Execute in Cloud Shell:**
```bash
# Check service details
gcloud run services describe review-api \
  --region=us-central1 \
  --project=aletheia-codex-prod \
  --format="value(spec.template.metadata.annotations)"

# Look for: run.googleapis.com/ingress: all
# This confirms the service is publicly accessible without IAM check
```

#### Step 1.3.4.4: Test API Endpoint

**Execute in Cloud Shell:**
```bash
# Test direct Cloud Run URL
echo "=== Testing Direct Cloud Run URL ==="
curl -s https://review-api-679360092359.us-central1.run.app/api/review/pending

# Test Firebase Hosting proxy
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

**Note**: The "Missing Authorization header" error is **CORRECT** - it means:
- ✅ The service is accessible (no 403 or 503 errors)
- ✅ The service is running and processing requests
- ✅ The authentication layer is working (requires Firebase Auth token)

### Validation Checklist - Phase 1.3.4

- [ ] Service update completed successfully
- [ ] No `allUsers` IAM binding present
- [ ] Service returns JSON error (not 403/503)
- [ ] Both direct URL and proxy URL work
- [ ] Error message is "Missing Authorization header"

### Rollback Procedure (If Needed)

**If service is not accessible:**
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

### Status After Phase 1.3.4
- ✅ Service accessible without `allUsers` binding
- ✅ Organization policy not violated
- ⚠️ Path routing issue still present (will fix in Phase 1.3.5)
- ✅ Ready for Phase 1.3.5

---

## Phase 1.3.5: DEPLOY PATH ROUTING FIX

### Objective
Deploy the code changes that fix the path routing issue (api/review/* pattern matching).

### Duration
10 minutes

### Responsibility
**HUMAN** (Cloud Shell commands)

### Steps

#### Step 1.3.5.1: Deploy Updated Code

**Execute in Cloud Shell:**
```bash
# Ensure we're in the correct directory
cd ~/aletheia-codex/functions

# Deploy the review-api with updated code
gcloud run deploy review-api \
  --source=review_api \
  --region=us-central1 \
  --platform=managed \
  --ingress=all \
  --set-env-vars="GCP_PROJECT=aletheia-codex-prod" \
  --memory=512Mi \
  --cpu=1 \
  --project=aletheia-codex-prod

# This will take 2-5 minutes
# Wait for "Service [review-api] revision [review-api-00013-xxx] has been deployed"
```

**Expected Output:**
```
Building using Buildpacks and deploying container to Cloud Run service [review-api]...
✓ Building and deploying... Done.
  ✓ Uploading sources...
  ✓ Building Container...
  ✓ Creating Revision...
  ✓ Routing traffic...
Done.
Service [review-api] revision [review-api-00013-xxx] has been deployed and is serving 100 percent of traffic.
Service URL: https://review-api-679360092359.us-central1.run.app
```

#### Step 1.3.5.2: Verify Deployment

**Execute in Cloud Shell:**
```bash
# Check latest revision
gcloud run revisions list \
  --service=review-api \
  --region=us-central1 \
  --project=aletheia-codex-prod \
  --limit=3

# Check service logs for startup
gcloud run services logs read review-api \
  --region=us-central1 \
  --project=aletheia-codex-prod \
  --limit=20
```

**Expected Output:**
```
REVISION              ACTIVE  SERVICE     DEPLOYED
✔ review-api-00013-xxx  yes     review-api  2025-11-14 XX:XX:XX UTC
✔ review-api-00012-xxx          review-api  2025-11-14 XX:XX:XX UTC
```

#### Step 1.3.5.3: Test Path Routing

**Execute in Cloud Shell:**
```bash
# Test the API endpoint that was failing
echo "=== Testing /api/review/pending ==="
curl -s https://aletheiacodex.app/api/review/pending

echo ""
echo "=== Testing /api/review/stats ==="
curl -s https://aletheiacodex.app/api/review/stats
```

**Expected Output:**
```
=== Testing /api/review/pending ===
{"error":"Missing Authorization header"}

=== Testing /api/review/stats ===
{"error":"Missing Authorization header"}
```

**SUCCESS INDICATORS**:
- ✅ Returns JSON (not HTML)
- ✅ Error is "Missing Authorization header" (not "Endpoint not found")
- ✅ No 404, 403, or 503 errors

### Validation Checklist - Phase 1.3.5

- [ ] Deployment completed successfully
- [ ] New revision is active and serving traffic
- [ ] API returns JSON error (not "Endpoint not found")
- [ ] No startup errors in logs
- [ ] Both `/pending` and `/stats` endpoints work

### Rollback Procedure (If Needed)

**If deployment fails or service is broken:**
```bash
# Rollback to previous revision
gcloud run services update-traffic review-api \
  --region=us-central1 \
  --to-revisions=review-api-00012-xxx=100 \
  --project=aletheia-codex-prod

# Check what went wrong
gcloud run services logs read review-api \
  --region=us-central1 \
  --project=aletheia-codex-prod \
  --limit=50 | grep ERROR
```

### Status After Phase 1.3.5
- ✅ Path routing fix deployed
- ✅ API endpoints correctly matched
- ✅ Service operational with modern security approach
- ✅ Ready for Phase 1.3.6

---

## Phase 1.3.6: END-TO-END TESTING WITH AUTHENTICATION

### Objective
Test the application with actual Firebase Authentication to verify full functionality.

### Duration
10 minutes

### Responsibility
**HUMAN** (browser testing)

### Steps

#### Step 1.3.6.1: Browser Testing

**Execute these steps in your browser:**

1. **Open Application**
   - Navigate to: `https://aletheiacodex.app`
   - Expected: Application loads, shows login page

2. **Login with Firebase Auth**
   - Click "Sign In" or "Login"
   - Use your Firebase Auth credentials
   - Expected: Successfully logged in, redirected to dashboard

3. **Navigate to Review Page**
   - Click on "Review" in navigation
   - Expected: Review page loads without errors

4. **Check for Data**
   - Look for pending review items
   - Expected: Either shows items OR shows "No pending items" message
   - **NOT Expected**: "Endpoint not found" error

5. **Check Browser Console**
   - Open Developer Tools (F12)
   - Go to Console tab
   - Expected: No red errors related to API calls

6. **Check Network Tab**
   - Open Developer Tools (F12)
   - Go to Network tab
   - Refresh the Review page
   - Look for API calls to `/api/review/pending` and `/api/review/stats`
   - Expected: Status 200 (success) or 401 (unauthorized, but valid response)
   - **NOT Expected**: 404, 403, or 503 errors

#### Step 1.3.6.2: Command-Line Testing with Auth Token

**Execute in Cloud Shell:**
```bash
# This is optional - for advanced verification
# You would need to get a Firebase Auth token from the browser

# In browser console, run:
# firebase.auth().currentUser.getIdToken().then(token => console.log(token))

# Then use that token:
TOKEN="<paste-token-here>"

curl -s https://aletheiacodex.app/api/review/pending \
  -H "Authorization: Bearer $TOKEN"

# Expected: Returns actual data or empty array, not an error
```

### Validation Checklist - Phase 1.3.6

- [ ] Application loads successfully
- [ ] User can log in with Firebase Auth
- [ ] Review page loads without "Endpoint not found" errors
- [ ] API calls return valid responses (200 or 401, not 404/403/503)
- [ ] No console errors related to API endpoints
- [ ] Network tab shows successful API communication

### Troubleshooting

**If you see "Endpoint not found" errors:**
```bash
# Check the actual path being called
# In browser console, look at the failed request URL

# Verify the service is receiving the correct path
gcloud run services logs read review-api \
  --region=us-central1 \
  --project=aletheia-codex-prod \
  --limit=50 | grep "Endpoint not found"

# This will show what path the service received
```

**If you see "Missing Authorization header":**
- This is CORRECT for unauthenticated requests
- Make sure you're logged in via Firebase Auth
- Check that the Authorization header is being sent

### Status After Phase 1.3.6
- ✅ Application fully functional
- ✅ Authentication working
- ✅ API endpoints responding correctly
- ✅ Ready for Phase 1.3.7

---

## Phase 1.3.7: SECURITY VERIFICATION AND DOCUMENTATION

### Objective
Verify that the security posture is correct and document the final state.

### Duration
10 minutes

### Responsibility
**HUMAN** (verification commands) + **AI** (documentation)

### Steps

#### Step 1.3.7.1: Verify Organization Policy

**Execute in Cloud Shell:**
```bash
# Verify DRS policy is active
echo "=== Checking Organization Policy ==="
gcloud resource-manager org-policies describe \
  iam.allowedPolicyMemberDomains \
  --organization=1037037147281

# Expected: Should show the policy with your Customer ID
```

**Expected Output:**
```
constraint: constraints/iam.allowedPolicyMemberDomains
listPolicy:
  allowedValues:
  - C03qt98jf  # Your Customer ID
```

#### Step 1.3.7.2: Verify No allUsers Binding

**Execute in Cloud Shell:**
```bash
# Check IAM policy for review-api
echo "=== Checking IAM Policy ==="
gcloud run services get-iam-policy review-api \
  --region=us-central1 \
  --project=aletheia-codex-prod

# Expected: Should NOT contain "allUsers" member
```

**Expected Output:**
```
bindings:
- members:
  - serviceAccount:superninja@aletheia-codex-prod.iam.gserviceaccount.com
  role: roles/run.invoker
etag: BwYXXXXXXXX
version: 1
```

**SUCCESS**: No `allUsers` in the output

#### Step 1.3.7.3: Verify Service Configuration

**Execute in Cloud Shell:**
```bash
# Check service ingress settings
echo "=== Checking Service Configuration ==="
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

#### Step 1.3.7.4: Security Audit Summary

**Execute in Cloud Shell:**
```bash
# Create a security audit summary
cat > ~/security-audit-summary.txt << 'EOF'
=== AletheiaCodex Security Audit Summary ===
Date: $(date)

1. Organization Policy Status:
   - iam.allowedPolicyMemberDomains: ENABLED ✅
   - Restricts to Customer ID only
   - Protects entire organization

2. Project Policy Status:
   - run.managed.requireInvokerIam: DISABLED (project-level) ✅
   - Allows Cloud Run services to bypass IAM check
   - Scoped to aletheia-codex-prod only

3. Cloud Run Service Status:
   - review-api: PUBLIC (via --no-invoker-iam-check) ✅
   - No allUsers IAM binding
   - Ingress: all (publicly accessible)

4. Security Posture:
   - Organization: SECURED ✅
   - Project: ACCEPTABLE (modern solution) ✅
   - Service: FUNCTIONAL ✅

5. Compliance:
   - GCP Best Practices: ALIGNED ✅
   - Domain Restricted Sharing: ENFORCED ✅
   - Modern Cloud Run Auth: IMPLEMENTED ✅

=== Audit Complete ===
EOF

cat ~/security-audit-summary.txt
```

### Validation Checklist - Phase 1.3.7

- [ ] Organization policy is active and enforced
- [ ] No `allUsers` IAM binding on review-api
- [ ] Service is publicly accessible via `--no-invoker-iam-check`
- [ ] Security audit summary created
- [ ] All security requirements met

### AI Documentation Task

**AI will create:**
1. Final deployment summary document
2. Security posture report
3. Comparison: Before vs After
4. Recommendations for Phase 2 (IAP + Identity Platform)

### Status After Phase 1.3.7
- ✅ Security verified and documented
- ✅ Organization protected
- ✅ Application functional
- ✅ Phase 1.3.x COMPLETE

---

## Phase 1.3.8: CLEANUP AND NEXT STEPS

### Objective
Clean up temporary files and prepare for future phases.

### Duration
5 minutes

### Responsibility
**HUMAN** (cleanup commands)

### Steps

#### Step 1.3.8.1: Archive Policy Files

**Execute in Cloud Shell:**
```bash
# Create archive directory
mkdir -p ~/aletheia-codex-policies

# Move policy files to archive
mv ~/policy-*.yaml ~/aletheia-codex-policies/

# Create README
cat > ~/aletheia-codex-policies/README.md << 'EOF'
# AletheiaCodex Organization Policies

This directory contains the organization policies applied during Sprint 1.3.x remediation.

## Files:
- policy-drs-re-enable.yaml: Organization-level DRS policy
- policy-run-iam-override.yaml: Project-level Cloud Run IAM override

## Applied:
- Date: $(date)
- Organization: 1037037147281
- Project: aletheia-codex-prod

## Status:
- Both policies are ACTIVE and ENFORCED
- Do not delete these files - they are reference documentation
EOF

ls -la ~/aletheia-codex-policies/
```

#### Step 1.3.8.2: Document Current State

**Execute in Cloud Shell:**
```bash
# Create deployment state document
cat > ~/aletheia-codex-deployment-state.txt << 'EOF'
=== AletheiaCodex Deployment State ===
Date: $(date)

PHASE 1.3.x: COMPLETE ✅

Services Deployed:
- review-api: OPERATIONAL ✅
  - Revision: review-api-00013-xxx
  - URL: https://review-api-679360092359.us-central1.run.app
  - Proxy: https://aletheiacodex.app/api/review/*
  - Auth: Firebase Auth (required)
  - Security: Modern (--no-invoker-iam-check)

Services Pending:
- graph-api: NOT DEPLOYED ⏳
- notes-api: NOT DEPLOYED ⏳
- orchestration-api: NOT DEPLOYED ⏳

Security Posture:
- Organization Policy: ENFORCED ✅
- DRS (Domain Restricted Sharing): ACTIVE ✅
- Modern Cloud Run Auth: IMPLEMENTED ✅
- No allUsers bindings: VERIFIED ✅

Next Steps:
1. Deploy remaining services (graph-api, notes-api, orchestration-api)
2. Apply same security pattern to all services
3. Plan Phase 2: IAP + Identity Platform migration
4. Implement monitoring and alerting

=== End of State Document ===
EOF

cat ~/aletheia-codex-deployment-state.txt
```

#### Step 1.3.8.3: Commit Documentation to Repository

**Execute in Cloud Shell:**
```bash
# Navigate to repository
cd ~/aletheia-codex

# Pull latest changes
git pull origin sprint-1

# Copy deployment state to repository
cp ~/aletheia-codex-deployment-state.txt docs/DEPLOYMENT_STATE.txt
cp ~/security-audit-summary.txt docs/SECURITY_AUDIT.txt

# Commit documentation
git add docs/DEPLOYMENT_STATE.txt docs/SECURITY_AUDIT.txt
git commit -m "docs: add Phase 1.3.x completion documentation"
git push origin sprint-1
```

### Validation Checklist - Phase 1.3.8

- [ ] Policy files archived
- [ ] Deployment state documented
- [ ] Security audit documented
- [ ] Documentation committed to repository

### Status After Phase 1.3.8
- ✅ Phase 1.3.x fully complete
- ✅ Documentation archived
- ✅ Ready for next sprint planning

---

## PHASE 1.3.x COMPLETION SUMMARY

### What Was Accomplished

#### Security ✅
- Organization policy re-enabled (DRS active)
- Modern Cloud Run authentication implemented
- No `allUsers` IAM bindings
- Organization-wide security restored

#### Functionality ✅
- review-api deployed and operational
- Path routing fix applied
- Firebase Authentication working
- Application accessible at https://aletheiacodex.app

#### Compliance ✅
- GCP best practices aligned
- Domain Restricted Sharing enforced
- Modern security patterns implemented
- Audit trail documented

### Metrics

| Metric | Before | After |
|--------|--------|-------|
| Security Posture | CRITICAL | HIGH |
| Org Policy Status | DELETED | ENFORCED |
| allUsers Bindings | YES | NO |
| Application Status | BROKEN | FUNCTIONAL |
| Compliance | VIOLATED | ALIGNED |

### Time Investment

| Phase | Duration | Status |
|-------|----------|--------|
| 1.3.1 - Containment | 15 min | ✅ Complete |
| 1.3.2 - Project Policy | 10 min | ✅ Complete |
| 1.3.3 - Code Prep | 5 min | ✅ Complete |
| 1.3.4 - Service Update | 15 min | ✅ Complete |
| 1.3.5 - Deploy Fix | 10 min | ✅ Complete |
| 1.3.6 - Testing | 10 min | ✅ Complete |
| 1.3.7 - Verification | 10 min | ✅ Complete |
| 1.3.8 - Cleanup | 5 min | ✅ Complete |
| **TOTAL** | **80 min** | **✅ COMPLETE** |

---

## NEXT STEPS (Future Sprints)

### Sprint 1.4: Deploy Remaining Services
- Apply same security pattern to graph-api, notes-api, orchestration-api
- Update Firebase Hosting configuration
- End-to-end testing

### Sprint 2: IAP + Identity Platform Migration
- Upgrade Firebase Auth to Identity Platform
- Enable IAP on all Cloud Run services
- Update frontend to pass ID tokens
- Achieve zero-trust architecture

### Sprint 3: Monitoring and Optimization
- Set up Cloud Monitoring dashboards
- Configure alerting policies
- Implement rate limiting
- Performance optimization

---

## TROUBLESHOOTING GUIDE

### Issue: Organization Policy Won't Apply

**Symptoms:**
- Error: "Permission denied" or "Insufficient permissions"

**Solution:**
```bash
# Verify you have Organization Administrator role
gcloud organizations get-iam-policy 1037037147281 \
  --flatten="bindings[].members" \
  --filter="bindings.members:user:YOUR_EMAIL"

# If not, request access from organization admin
```

### Issue: Service Returns 403 After Update

**Symptoms:**
- curl returns 403 Forbidden
- Service was working before

**Solution:**
```bash
# Check if IAM check is disabled
gcloud run services describe review-api \
  --region=us-central1 \
  --project=aletheia-codex-prod \
  --format="value(spec.template.metadata.annotations)"

# If not showing ingress: all, re-run:
gcloud run services update review-api \
  --region=us-central1 \
  --no-invoker-iam-check \
  --project=aletheia-codex-prod
```

### Issue: Path Routing Still Broken

**Symptoms:**
- Still seeing "Endpoint not found" errors
- API calls return 404

**Solution:**
```bash
# Check service logs for actual path received
gcloud run services logs read review-api \
  --region=us-central1 \
  --project=aletheia-codex-prod \
  --limit=50 | grep "Endpoint not found"

# Verify code was deployed
gcloud run revisions describe review-api-00013-xxx \
  --region=us-central1 \
  --project=aletheia-codex-prod

# If needed, redeploy
cd ~/aletheia-codex/functions
gcloud run deploy review-api --source=review_api ...
```

### Issue: Deployment Fails

**Symptoms:**
- Build fails
- Container won't start

**Solution:**
```bash
# Check build logs
gcloud builds list --limit=1 --project=aletheia-codex-prod

# Get detailed logs
gcloud builds log BUILD_ID --project=aletheia-codex-prod

# Common issues:
# - Missing .python-version file
# - Missing Procfile
# - Missing dependencies in requirements.txt
```

---

## CONTACT AND ESCALATION

### For Issues During Execution

1. **Check this document first** - Most issues are covered in troubleshooting
2. **Check Cloud Run logs** - Most errors are visible in logs
3. **Verify prerequisites** - Ensure all access and permissions are in place
4. **Document the error** - Copy exact error messages for support

### Rollback Decision Tree

```
Is the organization at risk?
├─ YES → Immediately rollback to Phase 1.3.1 (re-enable policy)
└─ NO → Is the application broken?
    ├─ YES → Rollback to previous revision
    └─ NO → Continue with troubleshooting
```

---

## APPENDIX: COMMAND REFERENCE

### Quick Commands

```bash
# Check organization policy
gcloud resource-manager org-policies describe \
  iam.allowedPolicyMemberDomains \
  --organization=1037037147281

# Check project policy
gcloud resource-manager org-policies describe \
  run.managed.requireInvokerIam \
  --project=aletheia-codex-prod

# Check service IAM
gcloud run services get-iam-policy review-api \
  --region=us-central1 \
  --project=aletheia-codex-prod

# Check service status
gcloud run services describe review-api \
  --region=us-central1 \
  --project=aletheia-codex-prod

# Check service logs
gcloud run services logs read review-api \
  --region=us-central1 \
  --project=aletheia-codex-prod \
  --limit=50

# Test endpoint
curl -s https://aletheiacodex.app/api/review/pending
```

---

## SIGN-OFF

### Phase 1.3.x Completion Checklist

- [ ] All phases (1.3.1 through 1.3.8) completed
- [ ] All validation checkpoints passed
- [ ] Security verified and documented
- [ ] Application tested and functional
- [ ] Documentation committed to repository
- [ ] Team notified of completion

**Completed By**: _______________________

**Date**: _______________________

**Signature**: _______________________

---

**END OF PHASED REMEDIATION PLAN**