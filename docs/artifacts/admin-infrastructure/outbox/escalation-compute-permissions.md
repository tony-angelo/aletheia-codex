# Escalation: Missing Compute Engine Permissions for Load Balancer Configuration

**Date**: 2025-01-18  
**From**: Admin-Infrastructure  
**To**: Architect  
**Sprint**: Sprint 1  
**Priority**: High  
**Status**: Open  

---

## Blocker Summary

The SuperNinja service account lacks the necessary Compute Engine permissions to create and configure Load Balancers, backend services, URL maps, and network endpoint groups. These permissions are critical for implementing the Load Balancer + IAP solution required to resolve the organization policy blocker and restore API connectivity.

---

## Context

### Feature/Task Affected
**Sprint Guide Reference**: Feature 1 - Configure Load Balancer

### Current Progress
- **Completed**: 
  - Repository setup and authentication
  - GCP authentication with SuperNinja service account
  - Infrastructure assessment (Cloud Functions inventory)
  - IAP API enabled
  - Identified all Cloud Run services backing Gen 2 Cloud Functions

- **Blocked at**: 
  - Cannot list or create Compute Engine resources (backend services, URL maps, network endpoint groups)
  - Cannot configure Load Balancer infrastructure

- **Impact**: 
  - Cannot proceed with Sprint 1 primary objective
  - All Load Balancer configuration tasks are blocked
  - IAP configuration depends on Load Balancer setup

### Timeline Impact
- **Estimated Delay**: 1-2 hours (pending permission grant)
- **Affected Features**: 
  - Feature 1: Configure Load Balancer (blocked)
  - Feature 2: Configure IAP (blocked - depends on Feature 1)
  - Feature 3: Update DNS and Routing (blocked - depends on Feature 1)
  - Feature 4: Deploy Updated Cloud Functions (can proceed partially)
  - Feature 5: Configure Monitoring (blocked - depends on Feature 1)
  - Feature 6: Deploy Updated Frontend (blocked - depends on Features 1-3)
- **Critical Path**: Yes - this is the primary blocker for the entire sprint

---

## Problem Description

### What's Happening
When attempting to list or create Compute Engine resources, I receive permission denied errors indicating that the SuperNinja service account lacks the required `compute.*` permissions.

### Expected Behavior
According to the service account analysis document (`[artifacts]/architect/service-account-analysis.md`), the SuperNinja account should have sufficient permissions for all Sprint 1 infrastructure tasks, including Load Balancer configuration.

### Actual Behavior
The SuperNinja service account has the following roles:
- `roles/apigateway.admin`
- `roles/cloudfunctions.admin`
- `roles/datastore.user`
- `roles/dns.admin`
- `roles/firebase.admin`
- `roles/iam.serviceAccountAdmin`
- `roles/iam.serviceAccountUser`
- `roles/logging.viewer`
- `roles/resourcemanager.projectIamAdmin`
- `roles/run.admin`
- `roles/secretmanager.admin`
- `roles/serviceusage.serviceUsageAdmin`
- `roles/storage.objectUser`

**Missing**: `roles/compute.admin` or equivalent compute permissions

### Error Messages/Logs

```
# Attempting to list backend services
$ gcloud compute backend-services list
WARNING: Some requests did not succeed.
 - Required 'compute.backendServices.list' permission for 'projects/aletheia-codex-prod'

Listed 0 items.

# Attempting to list URL maps
$ gcloud compute url-maps list
WARNING: Some requests did not succeed.
 - Required 'compute.urlMaps.list' permission for 'projects/aletheia-codex-prod'

Listed 0 items.

# Attempting to list network endpoint groups
$ gcloud compute network-endpoint-groups list
WARNING: Some requests did not succeed.
 - Required 'compute.networkEndpointGroups.list' permission for 'projects/aletheia-codex-prod'

Listed 0 items.
```

---

## Investigation

### What I've Tried

1. **Attempt 1**: Verified service account authentication
   - Result: Successfully authenticated as `superninja@aletheia-codex-prod.iam.gserviceaccount.com`
   - Conclusion: Authentication is working correctly

2. **Attempt 2**: Checked IAM roles assigned to SuperNinja account
   - Result: Confirmed roles listed above, no compute-related roles present
   - Conclusion: Missing compute permissions as suspected

3. **Attempt 3**: Enabled Compute Engine API
   - Result: API was already enabled by user
   - Conclusion: API enablement is not the issue

4. **Attempt 4**: Attempted to use Cloud Run API directly
   - Result: Can successfully list and describe Cloud Run services
   - Conclusion: `roles/run.admin` is working, but insufficient for Load Balancer configuration

### Research Conducted
- **Documentation reviewed**: 
  - GCP Load Balancer documentation
  - IAM roles for Compute Engine
  - Service account analysis document
  - Sprint 1 guide

- **Root Cause**: The service account analysis document states "Can configure Load Balancers and IAP" but the actual IAM roles don't include compute permissions needed for Load Balancer resources.

### Root Cause Analysis
- **Suspected Cause**: Discrepancy between service account analysis document and actual IAM roles assigned
- **Evidence**: 
  - Service account analysis claims sufficient permissions for Load Balancer configuration
  - Actual IAM roles lack `roles/compute.admin` or equivalent
  - All compute resource operations fail with permission errors
- **Uncertainty**: Whether the intent was to use a different approach (e.g., Terraform with different credentials) or if the compute role was simply not granted

---

## Proposed Solutions

### Option 1: Grant Compute Admin Role
**Description**: Add `roles/compute.admin` role to the SuperNinja service account

**Pros**:
- Straightforward solution
- Provides all necessary permissions for Load Balancer configuration
- Aligns with service account analysis document claims
- Fastest path to unblocking sprint work

**Cons**:
- Broad permissions (may be more than minimally required)
- Requires organization admin action

**Implementation Effort**: 5 minutes (for user to grant role)

**Risks**: Minimal - service account is already highly privileged

---

### Option 2: Grant Specific Compute Permissions
**Description**: Add granular compute permissions via custom role or specific predefined roles

**Pros**:
- Follows principle of least privilege
- More secure approach
- Better long-term practice

**Cons**:
- Requires identifying exact permissions needed
- More complex to implement
- May need iteration if permissions are insufficient

**Implementation Effort**: 30-60 minutes (to identify and grant specific permissions)

**Risks**: May still be missing some permissions, requiring additional iterations

---

### Option 3: Use Alternative Load Balancer Approach
**Description**: Explore using API Gateway or other serverless load balancing solutions that don't require Compute Engine permissions

**Pros**:
- May work with existing permissions
- Potentially simpler architecture

**Cons**:
- Deviates from sprint plan
- May not support IAP integration
- Requires architectural redesign
- Unknown feasibility

**Implementation Effort**: 4-8 hours (research + implementation)

**Risks**: High - may not be viable solution for organization policy compliance

---

## Questions for Architect

1. **Permission Grant**: Can you grant `roles/compute.admin` to the SuperNinja service account, or should I use a different approach?

2. **Service Account Analysis**: The service account analysis document states the SuperNinja account "Can configure Load Balancers and IAP" - was this based on planned permissions or actual permissions?

3. **Alternative Approach**: Is there an alternative approach to Load Balancer + IAP that doesn't require Compute Engine permissions?

4. **Terraform/IaC**: Should I be using Terraform or another IaC tool with different credentials instead of gcloud CLI?

5. **Minimal Permissions**: If granting compute.admin is too broad, what specific compute permissions are needed for Load Balancer + IAP configuration?

---

## Additional Information

### Environment Details
- **Platform**: GCP Project `aletheia-codex-prod`
- **Service Account**: `superninja@aletheia-codex-prod.iam.gserviceaccount.com`
- **Region**: `us-central1`
- **APIs Enabled**: Compute Engine API, Cloud Run API, IAP API, Cloud Functions API

### Cloud Functions Inventory
**Gen 1 Functions**:
- `ingestion`: https://us-central1-aletheia-codex-prod.cloudfunctions.net/ingestion

**Gen 2 Functions (Cloud Run Services)**:
- `graphfunction`: https://graphfunction-679360092359.us-central1.run.app
- `notesapifunction`: https://notesapifunction-679360092359.us-central1.run.app
- `orchestrate`: https://orchestrate-679360092359.us-central1.run.app
- `orchestration`: https://orchestration-679360092359.us-central1.run.app
- `reviewapifunction`: https://reviewapifunction-679360092359.us-central1.run.app

### Required Load Balancer Configuration
Based on sprint guide, need to configure:
- Global HTTP(S) Load Balancer
- Backend services for each function
- URL map with routing:
  - `/api/ingest` → ingestion function
  - `/api/orchestrate` → orchestration function
  - `/api/graph/*` → graph function
  - `/api/notes/*` → notes_api function
  - `/api/review/*` → review_api function
- Health checks for each backend
- SSL certificate
- IAP configuration on backend services

---

## Workaround

### Temporary Solution
**Description**: While waiting for permission grant, I can:
1. Document the Load Balancer configuration requirements in detail
2. Prepare configuration scripts/commands ready to execute once permissions are granted
3. Work on Feature 4 (Cloud Functions deployment) which doesn't require compute permissions
4. Review and prepare IAP configuration documentation

**Limitations**: Cannot actually create or test Load Balancer infrastructure

**Duration**: Can sustain until permissions are granted (no time limit, but blocks sprint completion)

---

## Impact Assessment

### Sprint Impact
- **Features Blocked**: 
  - Feature 1: Configure Load Balancer (completely blocked)
  - Feature 2: Configure IAP (blocked - depends on Feature 1)
  - Feature 3: Update DNS and Routing (blocked - depends on Feature 1)
  - Feature 5: Configure Monitoring (partially blocked - can't monitor Load Balancer)
  - Feature 6: Deploy Updated Frontend (blocked - needs Load Balancer URL)

- **Features At Risk**: 
  - Feature 4: Deploy Updated Cloud Functions (can proceed but can't test through Load Balancer)

- **Features Unaffected**: 
  - None - all features depend on Load Balancer configuration

### Quality Impact
- **Testing**: Cannot test Load Balancer routing or IAP authentication
- **Documentation**: Can document configuration but cannot verify
- **Technical Debt**: None - this is a permission issue, not a technical debt issue

### Timeline Impact
- **Best Case**: 1-2 hours (if compute.admin granted immediately)
- **Likely Case**: 2-4 hours (including permission grant and configuration)
- **Worst Case**: 1-2 days (if alternative approach needed)

---

## Next Steps

### Immediate Actions
1. Document Load Balancer configuration requirements in detail
2. Prepare gcloud commands for Load Balancer setup (ready to execute once permissions granted)
3. Review IAP configuration documentation
4. Create session log documenting progress and blocker

### Pending Architect Response
1. Permission grant for compute resources OR
2. Guidance on alternative approach OR
3. Clarification on intended implementation method

### Alternative Work
While blocked on Load Balancer configuration, I can:
- Review backend code for IAP compatibility requirements
- Prepare Cloud Functions deployment scripts
- Document monitoring and logging requirements
- Prepare frontend configuration updates

---

## Resolution (To be filled by Architect)

### Architect Response
[Architect will fill this section with guidance]

### Recommended Approach
[Architect will specify the recommended solution]

### Updated Requirements
[Any changes to requirements or acceptance criteria]

### Additional Guidance
[Any additional architectural guidance]

---

**End of Escalation Document**