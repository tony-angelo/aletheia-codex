# Phase 1.3.7: Deploy Remaining Services to Cloud Run

**Date**: 2024-01-13  
**Phase**: 1.3.7  
**Objective**: Deploy graph-api, notes-api, and orchestration-api to Cloud Run  
**Estimated Duration**: 30 minutes  
**Status**: Ready to Execute

---

## Overview

Currently, only `review-api` is deployed to Cloud Run. The remaining services (graph, notes, orchestration) need to be deployed and configured in Firebase Hosting.

---

## Current Status

### Deployed ✅
- **review-api**: Deployed to Cloud Run, working correctly

### Not Deployed ⏳
- **graph-api**: Frontend expects `/api/graph/**`
- **notes-api**: Frontend expects `/api/notes/**`
- **orchestration-api**: Frontend expects `/api/orchestration/**`

---

## Deployment Plan

### Service 1: graph-api

**Source Directory**: `functions/graph/`  
**Service Name**: `graph-api`  
**API Endpoints**: `/api/graph/**`

**Deploy Command**:
```bash
cd ~/aletheia-codex/functions
gcloud run deploy graph-api \
  --source=graph \
  --region=us-central1 \
  --platform=managed \
  --no-invoker-iam-check \
  --set-env-vars="GCP_PROJECT=aletheia-codex-prod" \
  --memory=512Mi \
  --cpu=1 \
  --project=aletheia-codex-prod
```

---

### Service 2: notes-api

**Source Directory**: `functions/notes_api/`  
**Service Name**: `notes-api`  
**API Endpoints**: `/api/notes/**`

**Deploy Command**:
```bash
cd ~/aletheia-codex/functions
gcloud run deploy notes-api \
  --source=notes_api \
  --region=us-central1 \
  --platform=managed \
  --no-invoker-iam-check \
  --set-env-vars="GCP_PROJECT=aletheia-codex-prod" \
  --memory=512Mi \
  --cpu=1 \
  --project=aletheia-codex-prod
```

---

### Service 3: orchestration-api

**Source Directory**: `functions/orchestration/`  
**Service Name**: `orchestration-api`  
**API Endpoints**: `/api/orchestration/**`

**Deploy Command**:
```bash
cd ~/aletheia-codex/functions
gcloud run deploy orchestration-api \
  --source=orchestration \
  --region=us-central1 \
  --platform=managed \
  --no-invoker-iam-check \
  --set-env-vars="GCP_PROJECT=aletheia-codex-prod" \
  --memory=512Mi \
  --cpu=1 \
  --project=aletheia-codex-prod
```

---

## Update Firebase Hosting Configuration

After deploying all services, update `firebase.json`:

```json
{
  "hosting": {
    "public": "web/build",
    "site": "aletheia-codex-prod",
    "ignore": [
      "firebase.json",
      "**/.*",
      "**/node_modules/**"
    ],
    "rewrites": [
      {
        "source": "/api/review/**",
        "run": {
          "serviceId": "review-api",
          "region": "us-central1",
          "invoker": "firebase-invoker@aletheia-codex-prod.iam.gserviceaccount.com"
        }
      },
      {
        "source": "/api/graph/**",
        "run": {
          "serviceId": "graph-api",
          "region": "us-central1",
          "invoker": "firebase-invoker@aletheia-codex-prod.iam.gserviceaccount.com"
        }
      },
      {
        "source": "/api/notes/**",
        "run": {
          "serviceId": "notes-api",
          "region": "us-central1",
          "invoker": "firebase-invoker@aletheia-codex-prod.iam.gserviceaccount.com"
        }
      },
      {
        "source": "/api/orchestration/**",
        "run": {
          "serviceId": "orchestration-api",
          "region": "us-central1",
          "invoker": "firebase-invoker@aletheia-codex-prod.iam.gserviceaccount.com"
        }
      },
      {
        "source": "**",
        "destination": "/index.html"
      }
    ],
    "headers": [
      {
        "source": "/api/**",
        "headers": [
          {
            "key": "Access-Control-Allow-Origin",
            "value": "https://aletheiacodex.app"
          },
          {
            "key": "Access-Control-Allow-Methods",
            "value": "GET, POST, PUT, DELETE, OPTIONS"
          },
          {
            "key": "Access-Control-Allow-Headers",
            "value": "Content-Type, Authorization"
          },
          {
            "key": "Access-Control-Max-Age",
            "value": "3600"
          }
        ]
      }
    ]
  }
}
```

---

## Deploy Firebase Hosting

After updating `firebase.json`:

```bash
cd ~/aletheia-codex
firebase deploy --only hosting --project aletheia-codex-prod
```

---

## Verification Steps

### Test Each Service

```bash
# Test graph-api
curl -X GET "https://aletheiacodex.app/api/graph/nodes" \
  -H "Content-Type: application/json"

# Test notes-api
curl -X GET "https://aletheiacodex.app/api/notes" \
  -H "Content-Type: application/json"

# Test orchestration-api
curl -X GET "https://aletheiacodex.app/api/orchestration/status" \
  -H "Content-Type: application/json"
```

**Expected**: All should return 401 "Missing Authorization header" (correct behavior)

---

## Browser Testing

1. Open `https://aletheiacodex.app`
2. Login with Firebase Auth
3. Test each page:
   - **Review Page** (`/review`) - Already working ✅
   - **Graph Page** (`/graph`) - Should work after deployment
   - **Notes Page** (`/notes`) - Should work after deployment
   - **Dashboard** (`/dashboard`) - Should work after deployment

---

## Important Notes

### Service Account Permissions

All Cloud Run services will use the same default compute service account, which already has `roles/datastore.user` permission (granted in Phase 1.3.6). No additional permissions needed.

### --no-invoker-iam-check Flag

All services must use `--no-invoker-iam-check` to bypass the Domain Restricted Sharing organization policy (same as review-api).

### Environment Variables

All services need `GCP_PROJECT=aletheia-codex-prod` environment variable for Firestore client initialization.

---

## Troubleshooting

### Issue: Build Fails

**Solution**: Check `requirements.txt` for each service. May need to downgrade pydantic to 1.10.13 (same as review-api).

### Issue: Import Errors

**Solution**: Check `sys.path` configuration in `main.py`. Should use:
```python
sys.path.insert(0, os.path.dirname(__file__))
```

### Issue: 500 Errors After Deployment

**Solution**: Check Cloud Run logs:
```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=SERVICE_NAME" \
  --limit=20 \
  --project=aletheia-codex-prod
```

---

## Success Criteria

- [ ] graph-api deployed to Cloud Run
- [ ] notes-api deployed to Cloud Run
- [ ] orchestration-api deployed to Cloud Run
- [ ] firebase.json updated with all service proxies
- [ ] Firebase Hosting deployed
- [ ] All API endpoints return 401 (not 500 or 404)
- [ ] Graph page loads without errors
- [ ] Notes page loads without errors
- [ ] All features working end-to-end

---

## Estimated Timeline

- Deploy graph-api: 5 minutes
- Deploy notes-api: 5 minutes
- Deploy orchestration-api: 5 minutes
- Update firebase.json: 2 minutes
- Deploy Firebase Hosting: 3 minutes
- Testing: 10 minutes
- **Total**: 30 minutes

---

**Created By**: Architect (SuperNinja AI Agent)  
**Date**: 2024-01-13  
**Status**: Ready to Execute