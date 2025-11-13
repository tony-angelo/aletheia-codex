# Sprint 1.3 Guide: Deploy Cloud Run Services

**Sprint**: 1.3  
**Domain**: Infrastructure  
**Admin Node**: Admin-Infrastructure  
**Priority**: 🚨 CRITICAL  
**Estimated Duration**: 2-3 hours  
**Branch**: `sprint-1.3` (create new branch from sprint-1)

---

## Sprint Goal

Deploy Python Cloud Functions to Cloud Run services to bypass GCP organization policy and enable public API access.

---

## Problem Statement

### Current Issue
- GCP Organization Policy blocks public access to Cloud Functions (403 Forbidden)
- Firebase Hosting cannot rewrite to external URLs (Load Balancer)
- All API endpoints are non-functional
- Application cannot be used

### Solution
Migrate to Cloud Run services which:
- Are NOT affected by Cloud Functions organization policy
- Can be accessed publicly
- Work with Firebase Hosting rewrites
- Provide better production architecture

---

## Services to Deploy

### 1. Review API
- **Source**: `functions/review_api/main.py`
- **Service Name**: `review-api`
- **Region**: `us-central1`
- **Port**: 8080

### 2. Graph API
- **Source**: `functions/graph/main.py`
- **Service Name**: `graph-api`
- **Region**: `us-central1`
- **Port**: 8080

### 3. Notes API
- **Source**: `functions/notes_api/main.py`
- **Service Name**: `notes-api`
- **Region**: `us-central1`
- **Port**: 8080

### 4. Orchestration API
- **Source**: `functions/orchestration/main.py`
- **Service Name**: `orchestration-api`
- **Region**: `us-central1`
- **Port**: 8080

---

## Tasks

### 1. Create New Branch

```bash
cd /workspace/aletheia-codex
git checkout sprint-1
git pull origin sprint-1
git checkout -b sprint-1.3
```

---

### 2. Create Dockerfiles for Each Service

#### 2.1 Review API Dockerfile

**File**: `functions/review_api/Dockerfile`

```dockerfile
# Use official Python runtime as base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy shared directory
COPY shared/ /workspace/shared/

# Copy function code
COPY review_api/ /app/

# Install dependencies
RUN pip install --no-cache-dir functions-framework flask google-cloud-firestore google-cloud-logging firebase-admin

# Set environment variables
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Run the function
CMD exec functions-framework --target=review_api --port=$PORT
```

**Action**:
- [ ] Create `functions/review_api/Dockerfile`
- [ ] Copy the content above
- [ ] Save the file

---

#### 2.2 Graph API Dockerfile

**File**: `functions/graph/Dockerfile`

```dockerfile
# Use official Python runtime as base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy shared directory
COPY shared/ /workspace/shared/

# Copy function code
COPY graph/ /app/

# Install dependencies
RUN pip install --no-cache-dir functions-framework flask google-cloud-firestore google-cloud-logging firebase-admin

# Set environment variables
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Run the function
CMD exec functions-framework --target=graph_api --port=$PORT
```

**Action**:
- [ ] Create `functions/graph/Dockerfile`
- [ ] Copy the content above
- [ ] Save the file

---

#### 2.3 Notes API Dockerfile

**File**: `functions/notes_api/Dockerfile`

```dockerfile
# Use official Python runtime as base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy shared directory
COPY shared/ /workspace/shared/

# Copy function code
COPY notes_api/ /app/

# Install dependencies
RUN pip install --no-cache-dir functions-framework flask google-cloud-firestore google-cloud-logging firebase-admin

# Set environment variables
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Run the function
CMD exec functions-framework --target=notes_api --port=$PORT
```

**Action**:
- [ ] Create `functions/notes_api/Dockerfile`
- [ ] Copy the content above
- [ ] Save the file

---

#### 2.4 Orchestration API Dockerfile

**File**: `functions/orchestration/Dockerfile`

```dockerfile
# Use official Python runtime as base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy shared directory
COPY shared/ /workspace/shared/

# Copy function code
COPY orchestration/ /app/

# Install dependencies
RUN pip install --no-cache-dir functions-framework flask google-cloud-firestore google-cloud-logging firebase-admin

# Set environment variables
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Run the function
CMD exec functions-framework --target=orchestration_api --port=$PORT
```

**Action**:
- [ ] Create `functions/orchestration/Dockerfile`
- [ ] Copy the content above
- [ ] Save the file

---

### 3. Authenticate with GCP

```bash
# Set service account credentials
export GOOGLE_APPLICATION_CREDENTIALS=/workspace/aletheia-codex-prod-af9a64a7fcaa.json

# Authenticate gcloud
gcloud auth activate-service-account --key-file=$GOOGLE_APPLICATION_CREDENTIALS

# Set project
gcloud config set project aletheia-codex-prod
```

**Action**:
- [ ] Run authentication commands
- [ ] Verify authentication: `gcloud auth list`

---

### 4. Build and Deploy Cloud Run Services

#### 4.1 Deploy Review API

```bash
cd /workspace/aletheia-codex/functions

# Build and deploy in one command
gcloud run deploy review-api \
  --source=review_api \
  --region=us-central1 \
  --platform=managed \
  --allow-unauthenticated \
  --set-env-vars="GCP_PROJECT=aletheia-codex-prod" \
  --memory=512Mi \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=10 \
  --timeout=60s
```

**Expected Output**:
```
Service [review-api] revision [review-api-00001-xxx] has been deployed and is serving 100 percent of traffic.
Service URL: https://review-api-xxxxx-uc.a.run.app
```

**Action**:
- [ ] Run deployment command
- [ ] Save the Service URL
- [ ] Test: `curl https://review-api-xxxxx-uc.a.run.app`

---

#### 4.2 Deploy Graph API

```bash
gcloud run deploy graph-api \
  --source=graph \
  --region=us-central1 \
  --platform=managed \
  --allow-unauthenticated \
  --set-env-vars="GCP_PROJECT=aletheia-codex-prod" \
  --memory=512Mi \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=10 \
  --timeout=60s
```

**Action**:
- [ ] Run deployment command
- [ ] Save the Service URL
- [ ] Test: `curl https://graph-api-xxxxx-uc.a.run.app`

---

#### 4.3 Deploy Notes API

```bash
gcloud run deploy notes-api \
  --source=notes_api \
  --region=us-central1 \
  --platform=managed \
  --allow-unauthenticated \
  --set-env-vars="GCP_PROJECT=aletheia-codex-prod" \
  --memory=512Mi \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=10 \
  --timeout=60s
```

**Action**:
- [ ] Run deployment command
- [ ] Save the Service URL
- [ ] Test: `curl https://notes-api-xxxxx-uc.a.run.app`

---

#### 4.4 Deploy Orchestration API

```bash
gcloud run deploy orchestration-api \
  --source=orchestration \
  --region=us-central1 \
  --platform=managed \
  --allow-unauthenticated \
  --set-env-vars="GCP_PROJECT=aletheia-codex-prod" \
  --memory=512Mi \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=10 \
  --timeout=60s
```

**Action**:
- [ ] Run deployment command
- [ ] Save the Service URL
- [ ] Test: `curl https://orchestration-api-xxxxx-uc.a.run.app`

---

### 5. Verify Cloud Run Services

#### 5.1 List All Services

```bash
gcloud run services list --region=us-central1
```

**Expected Output**:
```
SERVICE              REGION       URL                                          LAST DEPLOYED BY
review-api           us-central1  https://review-api-xxxxx-uc.a.run.app       ...
graph-api            us-central1  https://graph-api-xxxxx-uc.a.run.app        ...
notes-api            us-central1  https://notes-api-xxxxx-uc.a.run.app        ...
orchestration-api    us-central1  https://orchestration-api-xxxxx-uc.a.run.app ...
```

**Action**:
- [ ] Run list command
- [ ] Verify all 4 services are deployed
- [ ] Document all Service URLs

---

#### 5.2 Test Each Service

```bash
# Test Review API
curl https://review-api-xxxxx-uc.a.run.app

# Test Graph API
curl https://graph-api-xxxxx-uc.a.run.app

# Test Notes API
curl https://notes-api-xxxxx-uc.a.run.app

# Test Orchestration API
curl https://orchestration-api-xxxxx-uc.a.run.app
```

**Expected Response** (for each):
```json
{
  "success": true,
  "message": "API is working",
  "timestamp": "2025-01-13T..."
}
```

**Action**:
- [ ] Test all 4 services
- [ ] Verify JSON responses (not HTML)
- [ ] Verify no 403 Forbidden errors

---

### 6. Update Load Balancer (Optional but Recommended)

#### 6.1 Create Serverless NEGs for Cloud Run

```bash
# Review API NEG
gcloud compute network-endpoint-groups create review-api-neg \
  --region=us-central1 \
  --network-endpoint-type=serverless \
  --cloud-run-service=review-api

# Graph API NEG
gcloud compute network-endpoint-groups create graph-api-neg \
  --region=us-central1 \
  --network-endpoint-type=serverless \
  --cloud-run-service=graph-api

# Notes API NEG
gcloud compute network-endpoint-groups create notes-api-neg \
  --region=us-central1 \
  --network-endpoint-type=serverless \
  --cloud-run-service=notes-api

# Orchestration API NEG
gcloud compute network-endpoint-groups create orchestration-api-neg \
  --region=us-central1 \
  --network-endpoint-type=serverless \
  --cloud-run-service=orchestration-api
```

**Action**:
- [ ] Create all 4 NEGs
- [ ] Verify creation: `gcloud compute network-endpoint-groups list`

---

#### 6.2 Update Backend Services

```bash
# Update Review backend
gcloud compute backend-services update review-backend \
  --global \
  --remove-backends --backends=review-function-neg \
  --add-backend=review-api-neg

# Update Graph backend
gcloud compute backend-services update graph-backend \
  --global \
  --remove-backends --backends=graph-function-neg \
  --add-backend=graph-api-neg

# Update Notes backend
gcloud compute backend-services update notes-backend \
  --global \
  --remove-backends --backends=notes-function-neg \
  --add-backend=notes-api-neg

# Update Orchestration backend
gcloud compute backend-services update orchestration-backend \
  --global \
  --remove-backends --backends=orchestration-function-neg \
  --add-backend=orchestration-api-neg
```

**Action**:
- [ ] Update all backend services
- [ ] Verify: `gcloud compute backend-services list`

---

#### 6.3 Test Load Balancer

```bash
# Test through Load Balancer
curl https://34.120.185.233/api/review/pending -H "Host: aletheiacodex.app" -k
```

**Expected**: JSON response (not 403 Forbidden)

**Action**:
- [ ] Test Load Balancer
- [ ] Verify JSON responses
- [ ] Document results

---

### 7. Create Service URLs Documentation

**File**: `CLOUD_RUN_SERVICES.md`

```markdown
# Cloud Run Services

## Deployed Services

### Review API
- **Service Name**: review-api
- **Region**: us-central1
- **URL**: https://review-api-xxxxx-uc.a.run.app
- **Status**: ✅ Deployed

### Graph API
- **Service Name**: graph-api
- **Region**: us-central1
- **URL**: https://graph-api-xxxxx-uc.a.run.app
- **Status**: ✅ Deployed

### Notes API
- **Service Name**: notes-api
- **Region**: us-central1
- **URL**: https://notes-api-xxxxx-uc.a.run.app
- **Status**: ✅ Deployed

### Orchestration API
- **Service Name**: orchestration-api
- **Region**: us-central1
- **URL**: https://orchestration-api-xxxxx-uc.a.run.app
- **Status**: ✅ Deployed

## Configuration

- **Memory**: 512Mi
- **CPU**: 1
- **Min Instances**: 0
- **Max Instances**: 10
- **Timeout**: 60s
- **Authentication**: Allow unauthenticated (public access)

## Testing

All services tested and returning JSON responses (not 403 Forbidden).

## Next Steps

Admin-Frontend needs to update Firebase Hosting configuration to use these Cloud Run services.
```

**Action**:
- [ ] Create `CLOUD_RUN_SERVICES.md`
- [ ] Fill in actual Service URLs
- [ ] Commit to sprint-1.3 branch

---

### 8. Commit and Push Changes

```bash
cd /workspace/aletheia-codex

# Add all files
git add functions/review_api/Dockerfile
git add functions/graph/Dockerfile
git add functions/notes_api/Dockerfile
git add functions/orchestration/Dockerfile
git add CLOUD_RUN_SERVICES.md

# Commit
git commit -m "feat(infrastructure): deploy Cloud Run services

- Create Dockerfiles for all 4 services (review, graph, notes, orchestration)
- Deploy to Cloud Run with public access
- Update Load Balancer backends to Cloud Run NEGs
- Document service URLs and configuration

Services deployed:
- review-api: https://review-api-xxxxx-uc.a.run.app
- graph-api: https://graph-api-xxxxx-uc.a.run.app
- notes-api: https://notes-api-xxxxx-uc.a.run.app
- orchestration-api: https://orchestration-api-xxxxx-uc.a.run.app

Resolves Sprint 1.3 - Cloud Run migration (Infrastructure)"

# Push
git push origin sprint-1.3
```

**Action**:
- [ ] Commit all changes
- [ ] Push to GitHub
- [ ] Verify push successful

---

### 9. Create Session Log

**File**: `docs/artifacts/admin-infrastructure/outbox/sprint-1.3-session-log.md`

Document:
- Services deployed
- Service URLs
- Testing results
- Load Balancer updates
- Any issues encountered
- Time spent on each task

**Action**:
- [ ] Create session log
- [ ] Commit to artifacts branch
- [ ] Push to GitHub

---

### 10. Handoff to Admin-Frontend

**Create**: `docs/artifacts/admin-infrastructure/outbox/cloud-run-handoff.md`

```markdown
# Cloud Run Services Handoff

## Status
✅ All Cloud Run services deployed and tested

## Service URLs

### Review API
- **Service Name**: review-api
- **URL**: https://review-api-xxxxx-uc.a.run.app
- **Region**: us-central1

### Graph API
- **Service Name**: graph-api
- **URL**: https://graph-api-xxxxx-uc.a.run.app
- **Region**: us-central1

### Notes API
- **Service Name**: notes-api
- **URL**: https://notes-api-xxxxx-uc.a.run.app
- **Region**: us-central1

### Orchestration API
- **Service Name**: orchestration-api
- **URL**: https://orchestration-api-xxxxx-uc.a.run.app
- **Region**: us-central1

## Firebase Hosting Configuration

Admin-Frontend needs to update `firebase.json` with:

```json
{
  "hosting": {
    "rewrites": [
      {
        "source": "/api/review/**",
        "run": {
          "serviceId": "review-api",
          "region": "us-central1"
        }
      },
      {
        "source": "/api/graph/**",
        "run": {
          "serviceId": "graph-api",
          "region": "us-central1"
        }
      },
      {
        "source": "/api/notes/**",
        "run": {
          "serviceId": "notes-api",
          "region": "us-central1"
        }
      },
      {
        "source": "/api/orchestration/**",
        "run": {
          "serviceId": "orchestration-api",
          "region": "us-central1"
        }
      },
      {
        "source": "**",
        "destination": "/index.html"
      }
    ]
  }
}
```

## Testing Results

All services tested and returning JSON responses:
- ✅ Review API: Working
- ✅ Graph API: Working
- ✅ Notes API: Working
- ✅ Orchestration API: Working

No 403 Forbidden errors. Public access enabled.

## Next Steps

Admin-Frontend should:
1. Update `firebase.json` with Cloud Run rewrites
2. Deploy Firebase Hosting
3. Test API endpoints through Firebase Hosting
4. Verify end-to-end functionality
```

**Action**:
- [ ] Create handoff document
- [ ] Fill in actual Service URLs
- [ ] Commit to artifacts branch

---

## Success Criteria

### Must Have ✅
- [ ] All 4 Cloud Run services deployed
- [ ] Services accessible publicly (no 403 errors)
- [ ] Service URLs documented
- [ ] Load Balancer updated (optional)
- [ ] Handoff document created for Admin-Frontend
- [ ] Session log created
- [ ] All changes committed and pushed

### Should Have 📋
- [ ] Load Balancer backends updated to Cloud Run
- [ ] Testing results documented
- [ ] Dockerfiles committed to repository

### Nice to Have 🎯
- [ ] Monitoring configured
- [ ] Logs verified in Cloud Logging
- [ ] Performance benchmarks

---

## Troubleshooting

### Issue: Docker Build Fails
**Solution**: Check Dockerfile syntax, verify base image, check dependencies

### Issue: Deployment Fails
**Solution**: Check service account permissions, verify project ID, check region

### Issue: Service Returns 403
**Solution**: Verify `--allow-unauthenticated` flag was used, check IAM permissions

### Issue: Service Returns 500
**Solution**: Check logs: `gcloud run services logs read SERVICE_NAME --region=us-central1`

---

## Escalation Triggers

Escalate to Architect if:
1. **Deployment Failures**: Cannot deploy Cloud Run services
2. **Permission Issues**: Service account lacks required permissions
3. **Service Errors**: Services return errors after deployment
4. **Load Balancer Issues**: Cannot update Load Balancer backends
5. **Unexpected Behavior**: Services behave differently than Cloud Functions

**Escalation Process**:
1. Document the issue in `docs/artifacts/admin-infrastructure/escalations/sprint-1.3-blocker.md`
2. Include error messages, logs, and attempted solutions
3. Notify Architect via inbox message

---

## Timeline

- **Hour 0-0.5**: Create Dockerfiles
- **Hour 0.5-1.5**: Deploy Cloud Run services
- **Hour 1.5-2**: Update Load Balancer (optional)
- **Hour 2-2.5**: Test and verify
- **Hour 2.5-3**: Documentation and handoff

**Total Estimated Time**: 2-3 hours

---

**Created**: 2025-01-13  
**Author**: Architect  
**Status**: Ready for Execution  
**Priority**: 🚨 CRITICAL