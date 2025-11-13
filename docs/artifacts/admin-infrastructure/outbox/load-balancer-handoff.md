# Load Balancer Configuration Handoff

**Date**: 2025-01-18  
**From**: Admin-Infrastructure  
**To**: Admin-Backend, Admin-Frontend, User  
**Sprint**: Sprint 1  
**Status**: Load Balancer Operational (DNS and IAP configuration needed)  

---

## 🎯 Executive Summary

Load Balancer configuration is **complete and operational**. All backend services are connected, routing is configured, and the infrastructure is ready for integration. 

**Critical Next Steps**:
1. **DNS Configuration** (User action required)
2. **OAuth Consent Screen Setup** (Admin-Backend or Console)
3. **IAP Enablement** (After OAuth setup)

---

## 📊 Load Balancer Details

### Primary Information
- **Load Balancer URL**: `https://aletheiacodex.app`
- **Static IP Address**: `34.120.185.233`
- **Status**: Operational (pending DNS configuration)
- **SSL Certificate**: Provisioning (will complete 15-60 minutes after DNS)

### Infrastructure Components
- ✅ 6 Network Endpoint Groups (NEGs) created
- ✅ 6 Backend Services configured
- ✅ URL Map with routing rules configured
- ✅ SSL Certificate created (Google-managed)
- ✅ Target HTTPS Proxy configured
- ✅ Forwarding Rule created on port 443
- ⏸️ IAP enablement pending OAuth consent screen

---

## 🔧 DNS Configuration Required

**CRITICAL**: DNS must be configured for the Load Balancer to be accessible and for SSL certificate provisioning.

### DNS Records to Create

```
Record Type: A
Hostname: aletheiacodex.app
Value: 34.120.185.233
TTL: 300 (or default)

Record Type: A
Hostname: www.aletheiacodex.app
Value: 34.120.185.233
TTL: 300 (or default)
```

### DNS Configuration Steps
1. Access your DNS provider (Google Domains, Cloudflare, etc.)
2. Navigate to DNS management for aletheiacodex.app
3. Add/update A record for `aletheiacodex.app` → `34.120.185.233`
4. Add/update A record for `www.aletheiacodex.app` → `34.120.185.233`
5. Save changes
6. Wait 5-15 minutes for DNS propagation
7. Verify with: `nslookup aletheiacodex.app` (should return 34.120.185.233)

### After DNS Configuration
- SSL certificate will automatically provision (15-60 minutes)
- Load Balancer will be accessible at https://aletheiacodex.app
- Can begin end-to-end testing

---

## 🔐 IAP Configuration (Pending)

Identity-Aware Proxy (IAP) requires OAuth consent screen configuration before enablement.

### OAuth Consent Screen Setup

**Who Should Do This**: Admin-Backend or via GCP Console

**Steps**:
1. Go to GCP Console → APIs & Services → OAuth consent screen
2. Select "Internal" or "External" user type
3. Configure application information:
   - App name: "AletheiaCodex"
   - User support email: [your email]
   - Developer contact: [your email]
4. Add authorized domains: `aletheiacodex.app`
5. Configure scopes (if needed)
6. Save and continue

### IAP Enablement Commands

**After OAuth consent screen is configured**, run these commands:

```bash
# Enable IAP on all backend services
gcloud compute backend-services update backend-graphfunction --global --iap=enabled
gcloud compute backend-services update backend-notesapifunction --global --iap=enabled
gcloud compute backend-services update backend-orchestrate --global --iap=enabled
gcloud compute backend-services update backend-orchestration --global --iap=enabled
gcloud compute backend-services update backend-reviewapifunction --global --iap=enabled
gcloud compute backend-services update backend-ingestion --global --iap=enabled
```

### IAP Access Configuration

Grant IAP access to appropriate service accounts:

```bash
# Grant IAP access to service accounts
gcloud iap web add-iam-policy-binding \
    --resource-type=backend-services \
    --service=backend-graphfunction \
    --member=serviceAccount:[service-account-email] \
    --role=roles/iap.httpsResourceAccessor
```

---

## 🔀 API Routing Configuration

### Routing Table

| Path | Backend Service | Cloud Function | Description |
|------|----------------|----------------|-------------|
| `/api/ingest` | backend-ingestion | ingestion | Document ingestion |
| `/api/ingest/*` | backend-ingestion | ingestion | Ingestion sub-paths |
| `/api/orchestrate` | backend-orchestration | orchestration | Workflow orchestration |
| `/api/orchestrate/*` | backend-orchestration | orchestration | Orchestration sub-paths |
| `/api/graph` | backend-graphfunction | graphfunction | Graph queries |
| `/api/graph/*` | backend-graphfunction | graphfunction | Graph sub-paths |
| `/api/notes` | backend-notesapifunction | notesapifunction | Notes management |
| `/api/notes/*` | backend-notesapifunction | notesapifunction | Notes sub-paths |
| `/api/review` | backend-reviewapifunction | reviewapifunction | Review queue |
| `/api/review/*` | backend-reviewapifunction | reviewapifunction | Review sub-paths |
| Default | backend-orchestration | orchestration | Fallback |

### Example API Calls

```bash
# Ingestion endpoint
curl https://aletheiacodex.app/api/ingest

# Orchestration endpoint
curl https://aletheiacodex.app/api/orchestrate

# Graph endpoint
curl https://aletheiacodex.app/api/graph/entities

# Notes endpoint
curl https://aletheiacodex.app/api/notes/list

# Review endpoint
curl https://aletheiacodex.app/api/review/queue
```

---

## 👨‍💻 For Admin-Backend

### What You Need to Do

1. **Configure OAuth Consent Screen** (Priority 1):
   - Set up OAuth consent screen in GCP Console
   - Configure authorized domains
   - Create OAuth client ID for IAP

2. **Implement IAP Authentication** (Priority 2):
   - Extract JWT from `X-Goog-IAP-JWT-Assertion` header
   - Validate JWT signature using Google's public keys
   - Extract user identity from JWT claims
   - Update all Cloud Functions to use IAP authentication

3. **Deploy Updated Cloud Functions** (Priority 3):
   - Deploy functions with IAP authentication
   - Test authentication flow
   - Verify user identity extraction

### Integration Details

**Load Balancer URL**: `https://aletheiacodex.app`

**IAP Headers**:
- `X-Goog-IAP-JWT-Assertion`: Contains JWT with user identity
- `X-Goog-Authenticated-User-Email`: User email (after IAP validation)
- `X-Goog-Authenticated-User-ID`: User ID (after IAP validation)

**Authentication Flow**:
1. User authenticates with Firebase Auth
2. Frontend sends request with Firebase token
3. IAP validates Firebase token
4. IAP adds authentication headers
5. Backend extracts user identity from headers

### Testing

```bash
# Test with valid Firebase token
curl -H "Authorization: Bearer [firebase-token]" https://aletheiacodex.app/api/graph

# Test without token (should fail after IAP enabled)
curl https://aletheiacodex.app/api/graph
```

---

## 🎨 For Admin-Frontend

### What You Need to Do

1. **Update API Client Configuration** (Priority 1):
   ```javascript
   // Old (direct Cloud Functions URLs)
   const API_BASE = 'https://us-central1-aletheia-codex-prod.cloudfunctions.net';
   
   // New (Load Balancer URL)
   const API_BASE = 'https://aletheiacodex.app';
   ```

2. **Update API Endpoints** (Priority 2):
   ```javascript
   // Ingestion
   const INGEST_URL = `${API_BASE}/api/ingest`;
   
   // Orchestration
   const ORCHESTRATE_URL = `${API_BASE}/api/orchestrate`;
   
   // Graph
   const GRAPH_URL = `${API_BASE}/api/graph`;
   
   // Notes
   const NOTES_URL = `${API_BASE}/api/notes`;
   
   // Review
   const REVIEW_URL = `${API_BASE}/api/review`;
   ```

3. **Test Integration** (Priority 3):
   - Verify all API calls work through Load Balancer
   - Test authentication flow
   - Verify error handling
   - Test all endpoints

### Integration Details

**API Base URL**: `https://aletheiacodex.app`

**Authentication**: Keep existing Firebase Auth token handling - IAP will validate tokens automatically

**CORS**: Load Balancer will handle CORS (if configured)

### Testing

```javascript
// Test API call through Load Balancer
fetch('https://aletheiacodex.app/api/graph/entities', {
  headers: {
    'Authorization': `Bearer ${firebaseToken}`
  }
})
.then(response => response.json())
.then(data => console.log(data));
```

---

## 📚 Documentation

### Complete Documentation
- **Location**: `infrastructure/load-balancer/README.md` (sprint-1-infrastructure branch)
- **Contents**: 
  - Complete infrastructure details
  - Deployment scripts
  - Troubleshooting guide
  - Integration guide
  - Testing procedures

### Deployment Scripts
- `create-negs.sh` - Create Network Endpoint Groups
- `create-backend-services.sh` - Create backend services
- `create-load-balancer.sh` - Create Load Balancer components
- `enable-iap.sh` - Enable IAP on backend services
- `url-map-config.yaml` - URL map configuration

---

## 🧪 Testing Checklist

### After DNS Configuration

- [ ] Verify DNS resolution: `nslookup aletheiacodex.app` returns 34.120.185.233
- [ ] Test Load Balancer connectivity: `curl -I https://aletheiacodex.app`
- [ ] Verify SSL certificate: `openssl s_client -connect aletheiacodex.app:443`
- [ ] Test each API endpoint through Load Balancer
- [ ] Verify routing works correctly
- [ ] Check Load Balancer logs in Cloud Console

### After IAP Configuration

- [ ] Test with valid Firebase token (should succeed)
- [ ] Test without token (should return 401)
- [ ] Test with invalid token (should return 401)
- [ ] Verify IAP headers are passed to backend
- [ ] Test user identity extraction in backend

---

## 🚨 Troubleshooting

### SSL Certificate Not Provisioning
- **Symptom**: Certificate status remains "PROVISIONING" for >60 minutes
- **Cause**: DNS not configured or not propagated
- **Solution**: Verify DNS A records, wait for propagation
- **Check**: `nslookup aletheiacodex.app`

### 502 Bad Gateway
- **Symptom**: Load Balancer returns 502 error
- **Cause**: Backend services unhealthy or Cloud Functions not responding
- **Solution**: Check Cloud Functions logs, verify backend health
- **Check**: `gcloud compute backend-services get-health backend-[name] --global`

### 403 Forbidden (After IAP Enabled)
- **Symptom**: API calls return 403 Forbidden
- **Cause**: User not authorized or IAP misconfigured
- **Solution**: Grant IAP access roles, verify OAuth configuration
- **Check**: IAM policies on backend services

### Routing Not Working
- **Symptom**: Requests go to wrong backend
- **Cause**: URL map misconfigured
- **Solution**: Verify URL map configuration
- **Check**: `gcloud compute url-maps describe aletheia-lb-url-map`

---

## 📞 Support

### Questions or Issues?

**For Infrastructure Questions**:
- Review: `infrastructure/load-balancer/README.md`
- Check: GCP Console → Network Services → Load Balancing

**For IAP Questions**:
- Review: [IAP Documentation](https://cloud.google.com/iap/docs)
- Check: GCP Console → Security → Identity-Aware Proxy

**For Escalation**:
- Create escalation document in `docs/artifacts/admin-infrastructure/outbox/`
- Follow escalation template
- Notify Architect

---

## ✅ Success Criteria

### Load Balancer Configuration
- [x] Load Balancer created and operational
- [x] All backend services connected
- [x] URL routing configured correctly
- [x] SSL certificate created (provisioning)
- [x] Static IP reserved
- [x] Documentation complete

### Pending Completion
- [ ] DNS configured (user action)
- [ ] SSL certificate provisioned (after DNS)
- [ ] OAuth consent screen configured (Admin-Backend)
- [ ] IAP enabled on backend services (after OAuth)
- [ ] End-to-end testing complete (after DNS and IAP)

---

## 🎯 Next Steps Summary

### Immediate (User Action Required)
1. **Configure DNS** - Point aletheiacodex.app to 34.120.185.233
2. **Wait for DNS propagation** - 5-15 minutes
3. **Verify SSL certificate provisioning** - 15-60 minutes after DNS

### Admin-Backend
1. **Configure OAuth consent screen** - GCP Console
2. **Enable IAP on backend services** - Run enable-iap.sh
3. **Implement IAP authentication** - Update Cloud Functions
4. **Deploy updated functions** - Test authentication

### Admin-Frontend
1. **Update API base URL** - Change to https://aletheiacodex.app
2. **Test all endpoints** - Verify routing works
3. **Deploy updated frontend** - Firebase Hosting

---

**Load Balancer is ready! Waiting for DNS configuration to complete setup.**

---

**Admin-Infrastructure**  
Sprint 1 - Feature 1 Complete  
2025-01-18