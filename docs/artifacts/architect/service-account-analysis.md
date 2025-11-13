# Service Account Analysis

**Document Version:** 1.0  
**Last Updated:** 2025-01-18  
**Status:** Complete

## Overview

This document provides a comprehensive analysis of the service account keys provided for the AletheiaCodex project, including their roles, permissions, and usage guidelines for Admin nodes.

## Service Accounts

### 1. SuperNinja Service Account

**Email:** `superninja@aletheia-codex-prod.iam.gserviceaccount.com`  
**Key File:** `aletheia-codex-prod-af9a64a7fcaa.json`  
**Purpose:** Primary service account for deployment, infrastructure management, and backend operations

#### Assigned Roles

| Role | Purpose | Permissions Level |
|------|---------|------------------|
| `roles/apigateway.admin` | Manage API Gateway resources | Full control over API Gateway |
| `roles/cloudfunctions.admin` | Deploy and manage Cloud Functions | Full control over Cloud Functions |
| `roles/datastore.user` | Access Firestore/Datastore | Read/write data operations |
| `roles/dns.admin` | Manage Cloud DNS | Full control over DNS zones and records |
| `roles/firebase.admin` | Manage Firebase resources | Full control over Firebase services |
| `roles/iam.serviceAccountAdmin` | Manage service accounts | Create, update, delete service accounts |
| `roles/iam.serviceAccountUser` | Use service accounts | Impersonate service accounts |
| `roles/logging.viewer` | View logs | Read-only access to Cloud Logging |
| `roles/resourcemanager.projectIamAdmin` | Manage project IAM | Full control over project IAM policies |
| `roles/run.admin` | Manage Cloud Run | Full control over Cloud Run services |
| `roles/secretmanager.admin` | Manage secrets | Full control over Secret Manager |
| `roles/serviceusage.serviceUsageAdmin` | Enable/disable APIs | Manage API enablement |
| `roles/storage.objectUser` | Access Cloud Storage | Read/write objects in Cloud Storage |

#### Capabilities Summary

✅ **Can Do:**
- Deploy Cloud Functions (2nd gen)
- Configure Load Balancers and IAP
- Manage DNS records
- Create and manage service accounts
- Enable/disable GCP APIs
- Manage secrets in Secret Manager
- Deploy Cloud Run services
- Read/write Firestore data
- Access Cloud Storage buckets
- View application logs
- Manage Firebase resources

❌ **Cannot Do:**
- Modify organization policies (requires org-level permissions)
- Create new GCP projects
- Manage billing
- Access Compute Engine VMs (no compute.admin role)

#### Usage Notes

- **Primary Account:** This is the main service account for all Admin nodes
- **Sufficient for Sprint 1:** Has all necessary permissions for Load Balancer + IAP setup
- **Deployment Ready:** Can deploy Cloud Functions and configure infrastructure
- **Test-in-Prod:** Has permissions to deploy and test directly in production

### 2. Firebase Admin SDK Service Account

**Email:** `firebase-adminsdk-fbsvc@aletheia-codex-prod.iam.gserviceaccount.com`  
**Key File:** `aletheia-codex-prod-firebase-adminsdk-fbsvc-8b9046a84f.json`  
**Purpose:** Firebase Admin SDK operations and authentication

#### Assigned Roles

| Role | Purpose | Permissions Level |
|------|---------|------------------|
| `roles/firebase.sdkAdminServiceAgent` | Firebase Admin SDK operations | Service agent for Firebase Admin SDK |
| `roles/firebaseauth.admin` | Manage Firebase Authentication | Full control over Firebase Auth |
| `roles/iam.serviceAccountTokenCreator` | Create service account tokens | Generate tokens for service accounts |

#### Capabilities Summary

✅ **Can Do:**
- Initialize Firebase Admin SDK
- Manage Firebase Authentication users
- Create custom authentication tokens
- Verify ID tokens
- Manage user sessions
- Access Firebase services programmatically

❌ **Cannot Do:**
- Deploy infrastructure
- Manage Cloud Functions
- Configure Load Balancers
- Modify IAM policies

#### Usage Notes

- **Backend Use Only:** This account is specifically for Firebase Admin SDK initialization
- **Authentication Focus:** Primary purpose is managing Firebase Authentication
- **Not for Deployment:** Should not be used for infrastructure or deployment tasks

## Permission Assessment for Sprint 1

### Required Permissions for Sprint 1 Tasks

#### Admin-Infrastructure Node
**Task:** Configure Load Balancer + IAP

**Required Permissions:**
- ✅ Create/manage Load Balancers (covered by `roles/cloudfunctions.admin` + `roles/run.admin`)
- ✅ Configure IAP (covered by `roles/resourcemanager.projectIamAdmin`)
- ✅ Manage SSL certificates (covered by `roles/cloudfunctions.admin`)
- ✅ Configure backend services (covered by `roles/cloudfunctions.admin`)
- ✅ Enable required APIs (covered by `roles/serviceusage.serviceUsageAdmin`)

**Status:** ✅ **SUFFICIENT** - SuperNinja account has all required permissions

#### Admin-Backend Node
**Task:** Implement IAP-compatible authentication

**Required Permissions:**
- ✅ Deploy Cloud Functions (covered by `roles/cloudfunctions.admin`)
- ✅ Access Firestore (covered by `roles/datastore.user`)
- ✅ Manage secrets (covered by `roles/secretmanager.admin`)
- ✅ View logs (covered by `roles/logging.viewer`)

**Status:** ✅ **SUFFICIENT** - SuperNinja account has all required permissions

#### Admin-Frontend Node
**Task:** Update API client for Load Balancer

**Required Permissions:**
- ✅ Deploy frontend (covered by `roles/firebase.admin`)
- ✅ Access Cloud Storage (covered by `roles/storage.objectUser`)
- ✅ View logs (covered by `roles/logging.viewer`)

**Status:** ✅ **SUFFICIENT** - SuperNinja account has all required permissions

### Overall Assessment

**✅ ALL PERMISSIONS SUFFICIENT FOR SPRINT 1**

The SuperNinja service account has all necessary permissions to complete Sprint 1 tasks. No additional permissions are required.

## Security Considerations

### Best Practices

1. **Key Storage:**
   - Keys are stored in `/workspace` directory
   - Keys should be treated as highly sensitive credentials
   - Never commit keys to version control
   - Rotate keys periodically

2. **Principle of Least Privilege:**
   - SuperNinja account has broad permissions for deployment
   - Firebase Admin SDK account has limited, focused permissions
   - Consider creating more granular service accounts for production

3. **Audit Logging:**
   - All service account actions are logged in Cloud Audit Logs
   - Use `roles/logging.viewer` to monitor service account activity
   - Review logs regularly for suspicious activity

4. **Key Rotation:**
   - Rotate service account keys every 90 days
   - Update keys in all environments when rotating
   - Test new keys before revoking old keys

### Known Limitations

1. **Organization Policy Blocker:**
   - Current blocker: `iam.allowedPolicyMemberDomains` prevents `allUsers` access
   - Solution: Load Balancer + IAP (Sprint 1)
   - Service accounts have sufficient permissions to implement solution

2. **No Compute Engine Access:**
   - SuperNinja account lacks `roles/compute.admin`
   - Not required for current architecture (Cloud Functions + Firebase)
   - Add if future architecture requires Compute Engine VMs

3. **No Billing Access:**
   - Service accounts cannot manage billing
   - Billing must be managed through Cloud Console
   - Not required for deployment operations

## Usage Guidelines for Admin Nodes

### Authentication Setup

All Admin nodes should authenticate using the SuperNinja service account:

```bash
# Set environment variable
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/aletheia-codex-prod-af9a64a7fcaa.json"

# Or authenticate gcloud CLI
gcloud auth activate-service-account --key-file=/path/to/aletheia-codex-prod-af9a64a7fcaa.json
```

### Firebase Admin SDK Setup

Backend code should use the Firebase Admin SDK service account:

```python
import firebase_admin
from firebase_admin import credentials

cred = credentials.Certificate('/path/to/aletheia-codex-prod-firebase-adminsdk-fbsvc-8b9046a84f.json')
firebase_admin.initialize_app(cred)
```

### Deployment Commands

Admin nodes can use standard deployment commands:

```bash
# Deploy Cloud Functions
gcloud functions deploy FUNCTION_NAME --runtime python311 --trigger-http

# Deploy Firebase Hosting
firebase deploy --only hosting

# Enable APIs
gcloud services enable APINAME.googleapis.com
```

### Testing in Production

Admin nodes are encouraged to test-in-prod with these guidelines:

1. **Use Staging Environments When Available:**
   - Test major changes in staging first
   - Use production for final validation

2. **Deploy with Caution:**
   - Review changes before deploying
   - Monitor logs after deployment
   - Have rollback plan ready

3. **Incremental Deployments:**
   - Deploy one component at a time
   - Verify each component before proceeding
   - Use traffic splitting for gradual rollouts

## Recommendations

### Immediate Actions (Sprint 1)

1. ✅ **No additional permissions needed** - Current permissions are sufficient
2. ✅ **Proceed with Sprint 1** - All Admin nodes can execute their tasks
3. ✅ **Use SuperNinja account** - Primary account for all deployment operations

### Future Considerations

1. **Create Granular Service Accounts:**
   - Separate accounts for frontend, backend, and infrastructure
   - Implement principle of least privilege
   - Reduce blast radius of compromised keys

2. **Implement Key Rotation:**
   - Set up automated key rotation
   - Use Secret Manager for key storage
   - Update deployment pipelines to use rotated keys

3. **Add Monitoring:**
   - Set up alerts for service account usage
   - Monitor for unusual activity patterns
   - Track API quota usage

4. **Consider Workload Identity:**
   - Migrate to Workload Identity for GKE/Cloud Run
   - Eliminate need for service account keys
   - Improve security posture

## Conclusion

The provided service accounts have **sufficient permissions** for all Sprint 1 tasks. Admin nodes can proceed with:

- ✅ Infrastructure configuration (Load Balancer + IAP)
- ✅ Backend deployment (Cloud Functions with IAP auth)
- ✅ Frontend deployment (Firebase Hosting)
- ✅ Testing and validation in production

**No additional permissions or service accounts are required at this time.**

---

**Next Steps:**
1. Admin nodes should authenticate using the SuperNinja service account
2. Proceed with Sprint 1 execution
3. Monitor service account usage during deployment
4. Review this document after Sprint 1 for any permission gaps