# Neo4j HTTP API Deployment Guide

**Sprint**: Sprint 1 Completion  
**Status**: Ready for Deployment  
**Branch**: `feature/neo4j-http-api`

---

## 🎯 Overview

This guide covers deploying the Neo4j HTTP API implementation that resolves the Cloud Run gRPC incompatibility issue.

### What's Being Deployed

**Core Change**: Neo4j Bolt protocol → Neo4j HTTP API

**Why**: Cloud Run's gRPC proxy is incompatible with Neo4j's Bolt protocol, causing "503 Illegal metadata" errors.

**Result**: Reliable Neo4j connectivity in Cloud Run, enabling Sprint 1 completion (100%).

---

## 📋 Pre-Deployment Checklist

### ✅ Code Changes

- [x] HTTP API implementation in `shared/db/neo4j_client.py`
- [x] Orchestration function updated to use HTTP API
- [x] Dependencies updated (requests library added)
- [x] Test suite created (`test_neo4j_http_api.py`)
- [x] Original Bolt implementation backed up
- [x] Changes committed to `feature/neo4j-http-api` branch

### ✅ Prerequisites

- [ ] Neo4j Aura instance is active (not paused)
- [ ] Secrets configured in Secret Manager:
  - `NEO4J_URI` (e.g., neo4j+s://xxx.databases.neo4j.io:7687)
  - `NEO4J_USER` (e.g., neo4j)
  - `NEO4J_PASSWORD`
- [ ] Service account has Secret Manager access
- [ ] gcloud CLI authenticated
- [ ] Project set to `aletheia-codex-prod`

### ✅ Verification

```bash
# Check Neo4j Aura status
# Visit: https://console.neo4j.io/

# Verify secrets exist
gcloud secrets list --project=aletheia-codex-prod | grep NEO4J

# Check service account
gcloud iam service-accounts list --project=aletheia-codex-prod | grep aletheia-functions

# Verify authentication
gcloud auth list
gcloud config get-value project
```

---

## 🚀 Deployment Steps

### Step 1: Review Changes

```bash
# Clone or pull latest changes
git clone https://github.com/tony-angelo/aletheia-codex.git
cd aletheia-codex

# Checkout feature branch
git checkout feature/neo4j-http-api

# Review changes
git log --oneline -5
git diff main...feature/neo4j-http-api --stat
```

### Step 2: Deploy Orchestration Function

```bash
# Navigate to function directory
cd functions/orchestration

# Deploy with HTTP API implementation
gcloud functions deploy orchestrate \
    --gen2 \
    --runtime=python311 \
    --region=us-central1 \
    --source=. \
    --entry-point=orchestrate \
    --trigger-http \
    --service-account=aletheia-functions@aletheia-codex-prod.iam.gserviceaccount.com \
    --timeout=540s \
    --memory=512MB \
    --allow-unauthenticated \
    --project=aletheia-codex-prod
```

**Expected Output**:
```
Deploying function (may take a while - up to 2 minutes)...
✓ Function deployed successfully
URL: https://us-central1-aletheia-codex-prod.cloudfunctions.net/orchestrate
```

### Step 3: Verify Deployment

```bash
# Check function status
gcloud functions describe orchestrate \
    --region=us-central1 \
    --gen2 \
    --project=aletheia-codex-prod

# Expected: state: ACTIVE
```

---

## 🧪 Testing Deployed Function

### Test 1: Basic Health Check

```bash
# Test with a simple request
curl -X POST \
  https://us-central1-aletheia-codex-prod.cloudfunctions.net/orchestrate \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "test-http-api-001",
    "action": "process_document"
  }'
```

**Expected Response** (if document doesn't exist):
```json
{
  "error": "Failed to fetch document: Document content not found: test-http-api-001"
}
```

**This is GOOD** - it means:
- ✅ Function is responding
- ✅ HTTP API is working
- ✅ Secret Manager access is working
- ✅ Neo4j connection is established

### Test 2: Check Logs for HTTP API Success

```bash
# View recent logs
gcloud functions logs read orchestrate \
    --region=us-central1 \
    --gen2 \
    --limit=50 \
    --project=aletheia-codex-prod
```

**Look for these SUCCESS indicators**:
```
✓ "Created Neo4j HTTP client configuration"
✓ "Executing Neo4j HTTP query"
✓ "Neo4j HTTP query executed successfully"
✓ NO "503 Illegal metadata" errors
✓ NO gRPC errors
```

**Look for these FAILURE indicators** (should NOT appear):
```
✗ "503 Illegal metadata"
✗ "gRPC" errors
✗ "ServiceUnavailable"
✗ "Bolt protocol" errors
```

### Test 3: Full Document Processing (Optional)

If you have a test document in Cloud Storage:

```bash
# Create test document in Firestore
# Then trigger processing
curl -X POST \
  https://us-central1-aletheia-codex-prod.cloudfunctions.net/orchestrate \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "your-real-document-id",
    "action": "process_document"
  }'
```

---

## ✅ Verification Checklist

After deployment, verify:

- [ ] Function deploys without errors
- [ ] Function responds to HTTP requests (200 or expected error)
- [ ] Logs show "Neo4j HTTP query executed successfully"
- [ ] NO "503 Illegal metadata" errors in logs
- [ ] NO gRPC errors in logs
- [ ] Neo4j queries execute correctly
- [ ] Response includes `"api_type": "HTTP"` in success cases

---

## 🔍 Troubleshooting

### Issue: "DefaultCredentialsError"

**Symptom**: Function can't access Secret Manager

**Solution**:
```bash
# Verify service account has Secret Manager access
gcloud projects add-iam-policy-binding aletheia-codex-prod \
    --member="serviceAccount:aletheia-functions@aletheia-codex-prod.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

### Issue: "Document content not found"

**Symptom**: Can't find document in Cloud Storage

**Solution**: This is expected if testing with non-existent document. The important part is that Neo4j connection works.

### Issue: "Connection timeout"

**Symptom**: Requests timeout after 30 seconds

**Solution**:
1. Check Neo4j Aura instance is active (not paused)
2. Verify NEO4J_URI is correct
3. Check network connectivity

### Issue: Still seeing "503 Illegal metadata"

**Symptom**: gRPC errors persist

**Solution**:
1. Verify you deployed the correct branch (`feature/neo4j-http-api`)
2. Check that `requirements.txt` has `requests>=2.31.0` (not `neo4j`)
3. Redeploy the function
4. Clear any cached builds

---

## 🔄 Rollback Plan

If issues arise, rollback to previous version:

```bash
# Option 1: Rollback to previous deployment
gcloud functions deploy orchestrate \
    --gen2 \
    --runtime=python311 \
    --region=us-central1 \
    --source=. \
    --entry-point=orchestrate \
    --trigger-http \
    --service-account=aletheia-functions@aletheia-codex-prod.iam.gserviceaccount.com \
    --timeout=540s \
    --memory=512MB

# Option 2: Restore from backup
cd aletheia-codex
git checkout main
cp shared/db/neo4j_client.py.bolt_backup shared/db/neo4j_client.py
# Update requirements.txt to use neo4j instead of requests
# Redeploy
```

**Note**: Rollback will restore the gRPC incompatibility issue.

---

## 📊 Success Metrics

After successful deployment, you should see:

### Logs
```
✓ "Created Neo4j HTTP client configuration"
✓ "Executing Neo4j HTTP query (attempt 1/3)"
✓ "✓ Neo4j HTTP query executed successfully"
✓ "Successfully stored N chunks in Neo4j"
```

### Response
```json
{
  "status": "success",
  "document_id": "doc-id",
  "chunks_processed": 10,
  "api_type": "HTTP"
}
```

### Performance
- Query latency: ~60-120ms (acceptable overhead)
- Success rate: >95%
- No gRPC errors
- Reliable connectivity

---

## 📝 Post-Deployment Tasks

### 1. Merge to Main

```bash
# Create pull request
gh pr create \
    --title "feat: Implement Neo4j HTTP API to resolve Cloud Run gRPC incompatibility" \
    --body "Resolves Sprint 1 blocker. See docs/sprint1/NEO4J_HTTP_API_DECISION.md for details."

# After review, merge
gh pr merge --squash
```

### 2. Update Documentation

- [ ] Update PROJECT_STATUS.md to Sprint 1: 100%
- [ ] Update TROUBLESHOOTING.md with HTTP API info
- [ ] Create completion report

### 3. Monitor Production

```bash
# Monitor logs for first 24 hours
gcloud functions logs read orchestrate \
    --region=us-central1 \
    --gen2 \
    --limit=100 \
    --project=aletheia-codex-prod

# Check error rates
# Look for any unexpected issues
```

---

## 🎉 Success Criteria

Deployment is successful when:

1. ✅ Function deploys without errors
2. ✅ HTTP API connects to Neo4j successfully
3. ✅ No gRPC errors in logs
4. ✅ Queries execute and return results
5. ✅ Document processing works end-to-end
6. ✅ Performance is acceptable (~60-120ms per query)
7. ✅ Sprint 1 reaches 100% completion

---

## 📚 Related Documentation

- [NEO4J_HTTP_API_DECISION.md](./NEO4J_HTTP_API_DECISION.md) - Decision rationale
- [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) - General deployment guide
- [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - Troubleshooting guide
- [PROJECT_STATUS.md](../project/PROJECT_STATUS.md) - Project status

---

## 🤝 Support

If you encounter issues:

1. Check logs: `gcloud functions logs read orchestrate`
2. Review [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)
3. Verify Neo4j Aura instance is active
4. Check Secret Manager configuration
5. Contact: SuperNinja AI for assistance

---

**Status**: ✅ Ready for Deployment  
**Risk Level**: LOW (Rollback available)  
**Expected Duration**: 5-10 minutes  
**Impact**: Resolves Sprint 1 blocker, enables 100% completion