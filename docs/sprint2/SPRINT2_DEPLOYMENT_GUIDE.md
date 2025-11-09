# Sprint 2 Deployment Guide
# AI Integration & Entity Extraction

**Date**: November 9, 2025  
**Status**: Ready for Deployment  
**Estimated Time**: 2-3 hours

---

## Overview

This guide walks through deploying the Sprint 2 AI integration to production. The deployment includes:

1. Updated orchestration function with AI integration
2. Shared modules (AI, models, graph population, cost monitoring)
3. Production testing and validation
4. Cost monitoring verification

---

## Prerequisites

### Required Access
- ✅ GCP project access (aletheia-codex-prod)
- ✅ Cloud Functions deployment permissions
- ✅ Firestore access
- ✅ Neo4j Aura access
- ✅ Secret Manager access

### Required Secrets
- ✅ GEMINI_API_KEY (already configured)
- ✅ NEO4J_URI (already configured)
- ✅ NEO4J_USER (already configured)
- ✅ NEO4J_PASSWORD (already configured)

### Local Setup
- ✅ gcloud CLI installed and authenticated
- ✅ Git repository cloned and up to date
- ✅ On main branch with latest changes

---

## Deployment Steps

### Step 1: Verify Code Changes

The following files have been updated/created:

**Updated:**
- `functions/orchestration/main.py` - AI-integrated orchestration function

**Added:**
- `functions/orchestration/shared/ai/` - AI service modules
- `functions/orchestration/shared/models/` - Entity and relationship models
- `functions/orchestration/shared/db/graph_populator.py` - Graph population
- `functions/orchestration/shared/db/graph_queries.py` - Cypher queries
- `functions/orchestration/shared/utils/cost_*.py` - Cost monitoring

**Verify structure:**
```bash
cd aletheia-codex/functions/orchestration
tree -L 3 shared/
```

Expected output:
```
shared/
├── ai/
│   ├── __init__.py
│   ├── ai_service.py
│   ├── base_provider.py
│   ├── gemini_provider.py
│   └── prompts/
│       ├── __init__.py
│       ├── entity_extraction.py
│       └── relationship_detection.py
├── db/
│   ├── __init__.py
│   ├── firestore_client.py
│   ├── graph_populator.py
│   ├── graph_queries.py
│   └── neo4j_client.py
├── models/
│   ├── __init__.py
│   ├── entity.py
│   └── relationship.py
└── utils/
    ├── __init__.py
    ├── cost_config.py
    ├── cost_monitor.py
    ├── logging.py
    └── text_chunker.py
```

---

### Step 2: Deploy Orchestration Function

**Option A: Using Bash Script (Linux/Mac)**
```bash
cd aletheia-codex
./deploy_orchestration.sh
```

**Option B: Using PowerShell Script (Windows)**
```powershell
cd aletheia-codex
.\deploy_orchestration.ps1
```

**Option C: Manual Deployment**
```bash
cd aletheia-codex/functions/orchestration

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
    --set-env-vars GCP_PROJECT=aletheia-codex-prod \
    --allow-unauthenticated
```

**Expected Output:**
```
Deploying function (may take a while - up to 2 minutes)...
✓ Deploying function...done.
✓ Setting IAM Policy...done.
availableMemoryMb: 512
buildId: ...
entryPoint: orchestrate
httpsTrigger:
  url: https://us-central1-aletheia-codex-prod.cloudfunctions.net/orchestrate
...
state: ACTIVE
timeout: 540s
updateTime: '2025-11-09T...'
```

**Verify Deployment:**
```bash
gcloud functions describe orchestrate --region=us-central1 --gen2
```

Look for: `state: ACTIVE`

---

### Step 3: Create Test Document

**3.1: Create Firestore Document**

Navigate to Firestore in GCP Console:
```
https://console.cloud.google.com/firestore/data/documents?project=aletheia-codex-prod
```

Create a new document:
- **Collection**: `documents`
- **Document ID**: `test-ai-doc-1`
- **Fields**:
  ```
  title: "Sprint 2 AI Integration Test"
  user_id: "test-user-ai"
  status: "uploaded"
  created_at: (current timestamp)
  ```

**3.2: Upload Test Content to Cloud Storage**

Navigate to Cloud Storage:
```
https://console.cloud.google.com/storage/browser/aletheia-codex-prod-documents?project=aletheia-codex-prod
```

Upload a file:
- **Path**: `raw/test-ai-doc-1.txt`
- **Content**:
  ```
  I met Sarah Johnson at Google yesterday. She works as a software engineer 
  in Mountain View, California. We discussed the AletheiaCodex project and 
  how it uses Neo4j for knowledge graph storage. Sarah mentioned that Google 
  has been using similar technology for their Knowledge Graph since 2012.
  ```

---

### Step 4: Test the Deployment

**4.1: Test API Call**

```bash
curl -X POST \
  https://us-central1-aletheia-codex-prod.cloudfunctions.net/orchestrate \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "test-ai-doc-1",
    "user_id": "test-user-ai"
  }'
```

**Expected Response:**
```json
{
  "status": "success",
  "document_id": "test-ai-doc-1",
  "user_id": "test-user-ai",
  "entities_extracted": 6,
  "relationships_detected": 4,
  "entities_in_review_queue": 6,
  "relationships_in_review_queue": 4,
  "entities_in_graph": 5,
  "relationships_in_graph": 3,
  "processing_cost": 0.0006,
  "cost_breakdown": {
    "entity_extraction": 0.0003,
    "relationship_detection": 0.0002,
    "total": 0.0006
  }
}
```

**4.2: Verify Firestore Updates**

Check `documents/test-ai-doc-1`:
- `status` should be `"completed"`
- `entities_extracted` should be present
- `relationships_detected` should be present
- `processing_cost` should be present

Check `review_queue` collection:
- Should have 6 entity documents
- Should have 4 relationship documents
- All should have `status: "pending"`

Check `usage_logs` collection:
- Should have 2 entries (entity extraction + relationship detection)
- Should have cost information

**4.3: Verify Neo4j Graph**

Connect to Neo4j Aura and run:

```cypher
// Check user node
MATCH (u:User {user_id: "test-user-ai"})
RETURN u

// Check entities
MATCH (u:User {user_id: "test-user-ai"})-[:OWNS]->(e)
RETURN e, labels(e)

// Check relationships
MATCH (u:User {user_id: "test-user-ai"})-[:OWNS]->(source)-[r]->(target)<-[:OWNS]-(u)
RETURN source.name, type(r), target.name, r.confidence
```

**Expected Results:**
- User node exists
- 5-6 entity nodes (Sarah Johnson, Google, Mountain View, California, AletheiaCodex, Neo4j)
- 3-4 relationships (WORKS_AT, LOCATED_IN, RELATED_TO)

---

### Step 5: Validate Cost Monitoring

**5.1: Check Usage Logs**

Query Firestore `usage_logs` collection:
```javascript
// In Firestore console
db.collection('usage_logs')
  .where('user_id', '==', 'test-user-ai')
  .orderBy('timestamp', 'desc')
  .limit(10)
```

**Expected Fields:**
- `user_id`: "test-user-ai"
- `provider`: "gemini"
- `model`: "gemini-2.0-flash-exp"
- `operation`: "extract_entities" or "detect_relationships"
- `input_tokens`: ~150
- `output_tokens`: ~500 or ~150
- `cost`: ~0.0003 or ~0.0002
- `timestamp`: recent

**5.2: Verify Cost Targets**

Average cost per document should be: **~$0.0006**
- Target: <$0.01 per document
- Status: ✅ **94% under budget**

---

### Step 6: Monitor Logs

**6.1: View Function Logs**

```bash
gcloud functions logs read orchestrate \
  --region=us-central1 \
  --gen2 \
  --limit=50
```

**Look for:**
- ✅ "Processing document: test-ai-doc-1"
- ✅ "Extracting entities..."
- ✅ "Extracted X entities"
- ✅ "Detecting relationships..."
- ✅ "Detected X relationships"
- ✅ "Populating knowledge graph..."
- ✅ "Graph populated: X entities, X relationships"
- ✅ "Updated document test-ai-doc-1 status to: completed"

**Look for errors:**
- ❌ Any ERROR level logs
- ❌ Any exceptions or stack traces
- ❌ Any "failed" status updates

**6.2: Check for Warnings**

Acceptable warnings:
- Token counting fallback (uses heuristic)
- Cache misses (first run)

Unacceptable warnings:
- Authentication failures
- Rate limit errors
- Neo4j connection errors
- Firestore write errors

---

## Troubleshooting

### Issue: Deployment Fails

**Symptoms:**
- Deployment command returns error
- Function state is not ACTIVE

**Solutions:**
1. Check service account permissions:
   ```bash
   gcloud projects get-iam-policy aletheia-codex-prod \
     --flatten="bindings[].members" \
     --filter="bindings.members:aletheia-functions@aletheia-codex-prod.iam.gserviceaccount.com"
   ```

2. Verify requirements.txt is valid:
   ```bash
   cd functions/orchestration
   pip install -r requirements.txt --dry-run
   ```

3. Check function logs for build errors:
   ```bash
   gcloud functions logs read orchestrate --region=us-central1 --gen2 --limit=100
   ```

---

### Issue: Function Returns 500 Error

**Symptoms:**
- API call returns 500 Internal Server Error
- Logs show exceptions

**Solutions:**
1. Check if secrets are accessible:
   ```bash
   gcloud secrets versions access latest --secret="GEMINI_API_KEY"
   gcloud secrets versions access latest --secret="NEO4J_URI"
   ```

2. Verify Neo4j connectivity:
   - Check if Neo4j Aura instance is running
   - Verify credentials are correct
   - Test HTTP API endpoint

3. Check Firestore permissions:
   - Verify service account has Firestore access
   - Check if collections exist

---

### Issue: No Entities Extracted

**Symptoms:**
- Function completes successfully
- But entities_extracted = 0

**Solutions:**
1. Check document content:
   - Verify content exists in Cloud Storage
   - Check if content is meaningful text
   - Ensure content is not empty

2. Check Gemini API:
   - Verify API key is valid
   - Check for rate limiting
   - Review API quotas

3. Check confidence thresholds:
   - Default: 0.7 for entities, 0.6 for relationships
   - May need adjustment for specific content

---

### Issue: High Costs

**Symptoms:**
- Cost per document > $0.01
- Usage logs show high token counts

**Solutions:**
1. Check document length:
   - Very long documents cost more
   - Consider chunking for long documents

2. Review token counting:
   - Check input_tokens in usage logs
   - Verify token estimation is accurate

3. Adjust processing:
   - Increase confidence thresholds
   - Reduce number of API calls
   - Implement caching

---

## Rollback Procedure

If deployment fails or causes issues:

**1. Redeploy Previous Version**
```bash
cd aletheia-codex/functions/orchestration
cp main_backup_pre_ai.py main.py

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
    --set-env-vars GCP_PROJECT=aletheia-codex-prod \
    --allow-unauthenticated
```

**2. Verify Rollback**
```bash
gcloud functions describe orchestrate --region=us-central1 --gen2
```

**3. Test Previous Functionality**
Test with a simple document to ensure basic functionality works.

---

## Success Criteria

Deployment is successful when:

- ✅ Function deploys without errors
- ✅ Function state is ACTIVE
- ✅ Test document processes successfully
- ✅ Entities are extracted (>0)
- ✅ Relationships are detected (>0)
- ✅ Items appear in review queue
- ✅ High-confidence items appear in Neo4j
- ✅ Cost tracking logs are created
- ✅ Cost per document < $0.01
- ✅ No critical errors in logs
- ✅ Function responds within timeout (540s)

---

## Post-Deployment Tasks

After successful deployment:

1. **Update Documentation**
   - Mark Sprint 2 as deployed in PROJECT_STATUS.md
   - Create SPRINT2_DEPLOYMENT_REPORT.md
   - Update SPRINT2_COMPLETION_REPORT.md

2. **Monitor Production**
   - Set up log-based alerts
   - Monitor cost trends
   - Track error rates
   - Review entity/relationship quality

3. **User Communication**
   - Notify users of new features
   - Provide documentation
   - Gather feedback

4. **Plan Sprint 3**
   - Review queue UI
   - User approval workflow
   - Real-time updates

---

## Additional Resources

- **Sprint 2 Completion Report**: `docs/sprint2/SPRINT2_COMPLETION_REPORT.md`
- **Project Status**: `docs/project/PROJECT_STATUS.md`
- **Neo4j HTTP API Documentation**: `docs/sprint1/NEO4J_HTTP_API_DECISION.md`
- **Cost Monitoring Guide**: See `shared/utils/cost_monitor.py` docstrings

---

**Deployment Guide Version**: 1.0  
**Last Updated**: November 9, 2025  
**Next Review**: After Sprint 3 completion