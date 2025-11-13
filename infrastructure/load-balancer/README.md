# Load Balancer Configuration - Sprint 1

**Date**: 2025-01-18  
**Status**: ✅ Complete (IAP configuration pending OAuth setup)  
**Load Balancer IP**: 34.120.185.233  
**Load Balancer URL**: https://aletheiacodex.app  

---

## Summary

Successfully configured Google Cloud Load Balancer with all backend services connected and routing configured. The Load Balancer is operational and ready to route traffic to Cloud Functions once DNS is configured.

---

## Infrastructure Components Created

### 1. Network Endpoint Groups (NEGs)
Created 6 serverless NEGs connecting to Cloud Functions:

| NEG Name | Type | Cloud Function | Region |
|----------|------|----------------|--------|
| neg-graphfunction | Serverless | graphfunction (Gen 2) | us-central1 |
| neg-notesapifunction | Serverless | notesapifunction (Gen 2) | us-central1 |
| neg-orchestrate | Serverless | orchestrate (Gen 2) | us-central1 |
| neg-orchestration | Serverless | orchestration (Gen 2) | us-central1 |
| neg-reviewapifunction | Serverless | reviewapifunction (Gen 2) | us-central1 |
| neg-ingestion | Serverless | ingestion (Gen 1) | us-central1 |

### 2. Backend Services
Created 6 backend services with NEGs attached:

| Backend Service | NEG | Protocol | Load Balancing Scheme |
|----------------|-----|----------|----------------------|
| backend-graphfunction | neg-graphfunction | HTTP | EXTERNAL_MANAGED |
| backend-notesapifunction | neg-notesapifunction | HTTP | EXTERNAL_MANAGED |
| backend-orchestrate | neg-orchestrate | HTTP | EXTERNAL_MANAGED |
| backend-orchestration | neg-orchestration | HTTP | EXTERNAL_MANAGED |
| backend-reviewapifunction | neg-reviewapifunction | HTTP | EXTERNAL_MANAGED |
| backend-ingestion | neg-ingestion | HTTP | EXTERNAL_MANAGED |

### 3. URL Map
Created URL map with routing rules:

| Path | Backend Service | Cloud Function |
|------|----------------|----------------|
| `/api/ingest` | backend-ingestion | ingestion |
| `/api/ingest/*` | backend-ingestion | ingestion |
| `/api/orchestrate` | backend-orchestration | orchestration |
| `/api/orchestrate/*` | backend-orchestration | orchestration |
| `/api/graph` | backend-graphfunction | graphfunction |
| `/api/graph/*` | backend-graphfunction | graphfunction |
| `/api/notes` | backend-notesapifunction | notesapifunction |
| `/api/notes/*` | backend-notesapifunction | notesapifunction |
| `/api/review` | backend-reviewapifunction | reviewapifunction |
| `/api/review/*` | backend-reviewapifunction | reviewapifunction |
| Default | backend-orchestration | orchestration |

### 4. SSL Certificate
- **Name**: aletheia-ssl-cert
- **Type**: Google-managed
- **Domains**: aletheiacodex.app, www.aletheiacodex.app
- **Status**: PROVISIONING (will complete after DNS configuration)
- **Provisioning Time**: 15-60 minutes after DNS is configured

### 5. Target HTTPS Proxy
- **Name**: aletheia-https-proxy
- **URL Map**: aletheia-lb-url-map
- **SSL Certificate**: aletheia-ssl-cert

### 6. Static IP Address
- **Name**: aletheia-lb-ip
- **IP Address**: 34.120.185.233
- **Type**: IPv4
- **Scope**: Global

### 7. Forwarding Rule
- **Name**: aletheia-https-forwarding-rule
- **IP Address**: 34.120.185.233
- **Target**: aletheia-https-proxy
- **Port**: 443 (HTTPS)

---

## DNS Configuration Required

**CRITICAL**: DNS must be configured for SSL certificate provisioning and Load Balancer access.

### DNS Records to Create

```
Type: A
Name: aletheiacodex.app
Value: 34.120.185.233
TTL: 300

Type: A
Name: www.aletheiacodex.app
Value: 34.120.185.233
TTL: 300
```

### DNS Configuration Steps
1. Access your DNS provider (e.g., Google Domains, Cloudflare, etc.)
2. Add A record for `aletheiacodex.app` pointing to `34.120.185.233`
3. Add A record for `www.aletheiacodex.app` pointing to `34.120.185.233`
4. Wait for DNS propagation (typically 5-15 minutes)
5. SSL certificate will automatically provision after DNS is configured

---

## IAP Configuration (Pending)

Identity-Aware Proxy (IAP) configuration requires OAuth consent screen setup. This should be completed by Admin-Backend or through GCP Console.

### IAP Setup Steps (To Be Completed)

1. **Configure OAuth Consent Screen**:
   - Go to GCP Console > APIs & Services > OAuth consent screen
   - Configure application name, support email, etc.
   - Add authorized domains: aletheiacodex.app

2. **Enable IAP on Backend Services**:
   ```bash
   gcloud compute backend-services update backend-graphfunction --global --iap=enabled
   gcloud compute backend-services update backend-notesapifunction --global --iap=enabled
   gcloud compute backend-services update backend-orchestrate --global --iap=enabled
   gcloud compute backend-services update backend-orchestration --global --iap=enabled
   gcloud compute backend-services update backend-reviewapifunction --global --iap=enabled
   gcloud compute backend-services update backend-ingestion --global --iap=enabled
   ```

3. **Configure IAP Access**:
   - Grant `roles/iap.httpsResourceAccessor` to appropriate service accounts
   - Configure IAP to accept Firebase Auth tokens

4. **Backend Integration**:
   - Admin-Backend needs to implement IAP header validation
   - Extract user identity from `X-Goog-IAP-JWT-Assertion` header
   - Validate JWT signature

---

## Testing the Load Balancer

### Once DNS is Configured

1. **Test Load Balancer Connectivity**:
   ```bash
   curl -I https://aletheiacodex.app
   ```

2. **Test Routing to Each Backend**:
   ```bash
   # Test ingestion endpoint
   curl https://aletheiacodex.app/api/ingest
   
   # Test orchestration endpoint
   curl https://aletheiacodex.app/api/orchestrate
   
   # Test graph endpoint
   curl https://aletheiacodex.app/api/graph
   
   # Test notes endpoint
   curl https://aletheiacodex.app/api/notes
   
   # Test review endpoint
   curl https://aletheiacodex.app/api/review
   ```

3. **Verify SSL Certificate**:
   ```bash
   openssl s_client -connect aletheiacodex.app:443 -servername aletheiacodex.app
   ```

### Expected Behavior

- **Before IAP**: Endpoints should be accessible (403 errors from org policy should be resolved)
- **After IAP**: Endpoints will require authentication (401 Unauthorized without valid token)

---

## Integration Guide for Other Admin Nodes

### For Admin-Backend

**What You Need to Do**:

1. **Implement IAP Authentication**:
   - Extract JWT from `X-Goog-IAP-JWT-Assertion` header
   - Validate JWT signature using Google's public keys
   - Extract user identity from JWT claims
   - Update all Cloud Functions to use IAP authentication

2. **Configure OAuth Consent Screen**:
   - Set up OAuth consent screen in GCP Console
   - Configure authorized domains
   - Create OAuth client ID for IAP

3. **Update Cloud Functions**:
   - Deploy updated functions with IAP authentication
   - Test authentication flow
   - Verify user identity extraction

**Load Balancer Details**:
- **URL**: https://aletheiacodex.app
- **IP**: 34.120.185.233
- **Routing**: See routing table above

### For Admin-Frontend

**What You Need to Do**:

1. **Update API Client Configuration**:
   - Replace direct Cloud Functions URLs with Load Balancer URL
   - Update base URL to: `https://aletheiacodex.app`
   - Keep existing Firebase Auth token handling

2. **Update API Endpoints**:
   ```javascript
   // Old (direct Cloud Functions URLs)
   const API_BASE = 'https://us-central1-aletheia-codex-prod.cloudfunctions.net';
   
   // New (Load Balancer URL)
   const API_BASE = 'https://aletheiacodex.app';
   ```

3. **Test Integration**:
   - Verify all API calls work through Load Balancer
   - Test authentication flow
   - Verify error handling

**API Endpoints**:
- Ingestion: `https://aletheiacodex.app/api/ingest`
- Orchestration: `https://aletheiacodex.app/api/orchestrate`
- Graph: `https://aletheiacodex.app/api/graph/*`
- Notes: `https://aletheiacodex.app/api/notes/*`
- Review: `https://aletheiacodex.app/api/review/*`

---

## Monitoring and Logging

### View Load Balancer Metrics
```bash
# View Load Balancer metrics in GCP Console
# Navigation: Cloud Console > Network Services > Load Balancing > aletheia-https-forwarding-rule
```

### View Backend Service Health
```bash
gcloud compute backend-services get-health backend-graphfunction --global
gcloud compute backend-services get-health backend-notesapifunction --global
gcloud compute backend-services get-health backend-orchestrate --global
gcloud compute backend-services get-health backend-orchestration --global
gcloud compute backend-services get-health backend-reviewapifunction --global
gcloud compute backend-services get-health backend-ingestion --global
```

### View Load Balancer Logs
```bash
# View logs in Cloud Logging
# Filter: resource.type="http_load_balancer"
```

---

## Troubleshooting

### SSL Certificate Not Provisioning
- **Cause**: DNS not configured or not propagated
- **Solution**: Verify DNS A records point to 34.120.185.233
- **Check**: `nslookup aletheiacodex.app` should return 34.120.185.233

### 502 Bad Gateway Errors
- **Cause**: Backend services not healthy or Cloud Functions not responding
- **Solution**: Check Cloud Functions logs and backend service health
- **Check**: `gcloud compute backend-services get-health backend-[name] --global`

### 403 Forbidden Errors
- **Cause**: IAP not configured or user not authorized
- **Solution**: Complete IAP setup and grant appropriate IAM roles
- **Check**: Verify OAuth consent screen is configured

### Routing Not Working
- **Cause**: URL map misconfigured
- **Solution**: Verify URL map configuration
- **Check**: `gcloud compute url-maps describe aletheia-lb-url-map`

---

## Next Steps

1. **Configure DNS** (CRITICAL):
   - Add A records for aletheiacodex.app and www.aletheiacodex.app
   - Point to 34.120.185.233
   - Wait for DNS propagation

2. **Complete IAP Setup**:
   - Configure OAuth consent screen
   - Enable IAP on backend services
   - Test IAP authentication

3. **Backend Integration** (Admin-Backend):
   - Implement IAP authentication in Cloud Functions
   - Deploy updated functions
   - Test authentication flow

4. **Frontend Integration** (Admin-Frontend):
   - Update API client to use Load Balancer URL
   - Test all API endpoints
   - Verify authentication works

5. **Monitoring Setup**:
   - Configure alerts for Load Balancer errors
   - Set up dashboards for monitoring
   - Configure log-based metrics

---

## Success Criteria

- [x] Load Balancer created and configured
- [x] All backend services connected to Load Balancer
- [x] URL routing configured correctly
- [ ] IAP enabled on all backend services (pending OAuth setup)
- [x] SSL certificate created (provisioning in progress)
- [x] Static IP address reserved
- [x] Forwarding rule created
- [x] Load Balancer URL documented and shared
- [ ] DNS configured (requires user action)
- [ ] SSL certificate provisioned (after DNS)
- [ ] End-to-end testing complete (after DNS and IAP)

---

**Load Balancer Configuration Complete!**

**Next**: Configure DNS, complete IAP setup, and coordinate with Admin-Backend and Admin-Frontend for integration.

---

**Admin-Infrastructure**  
Sprint 1 - Feature 1  
2025-01-18