# 🚀 Neo4j Fix - Deployment Checklist

## Pre-Deployment Checklist

### ✅ Preparation (On Your Local Machine)

- [ ] **Pull latest changes from GitHub**
  ```powershell
  cd C:\dev\aletheia-codex
  git pull origin main
  ```

- [ ] **Review the fix**
  - [ ] Read `README_NEO4J_FIX.md` (5 min)
  - [ ] Review `CODE_COMPARISON.md` to understand changes (5 min)
  - [ ] Optional: Read `NEO4J_FIX_SUMMARY.md` for full details

- [ ] **Verify you have required tools**
  - [ ] Git installed and configured
  - [ ] gcloud CLI installed and authenticated
  - [ ] PowerShell (Windows) or Bash (Linux/Mac)

---

## Deployment Steps

### Option A: Automated Deployment (Recommended)

**Windows:**
```powershell
cd C:\dev\aletheia-codex
.\apply_neo4j_fix.ps1
```

**Linux/Mac:**
```bash
cd /path/to/aletheia-codex
./apply_neo4j_fix.sh
```

**What the script does:**
1. ✅ Backs up current `neo4j_client.py`
2. ✅ Applies the fix
3. ✅ Commits changes to git
4. ✅ Pushes to GitHub
5. ✅ Deploys to Cloud Functions

**Expected output:**
```
================================================
Neo4j Authentication Fix - Deployment Script
================================================

[1/5] Backing up original neo4j_client.py...
✓ Backup created: shared/db/neo4j_client.py.backup

[2/5] Applying fix (replacing with neo4j_client_fixed.py)...
✓ Fix applied

[3/5] Committing changes to git...
✓ Changes committed

[4/5] Pushing to GitHub...
✓ Pushed to GitHub

[5/5] Deploying to Cloud Functions...
✓ Deployed to Cloud Functions

================================================
✓ Fix Applied Successfully!
================================================
```

### Option B: Manual Deployment

If you prefer manual control:

1. **Apply the fix:**
   ```powershell
   cd C:\dev\aletheia-codex
   cp shared/db/neo4j_client_fixed.py shared/db/neo4j_client.py
   ```

2. **Commit and push:**
   ```powershell
   git add shared/db/neo4j_client.py
   git commit -m "Fix: Remove Neo4j driver caching"
   git push origin main
   ```

3. **Deploy to Cloud Functions:**
   ```powershell
   cd functions/orchestration
   gcloud functions deploy orchestrate `
       --gen2 `
       --runtime=python311 `
       --region=us-central1 `
       --source=. `
       --entry-point=orchestrate `
       --trigger-http `
       --service-account=aletheia-functions@aletheia-codex-prod.iam.gserviceaccount.com
   ```

---

## Post-Deployment Testing

### Step 1: Invoke the Function

```powershell
# Get authentication token
$TOKEN = gcloud auth print-identity-token

# Invoke function with test payload
curl -X POST `
  https://us-central1-aletheia-codex-prod.cloudfunctions.net/orchestrate `
  -H "Authorization: Bearer $TOKEN" `
  -H "Content-Type: application/json" `
  -d '{"document_id": "test-doc-123", "action": "process_document"}'
```

**Expected response:**
```json
{
  "status": "success",
  "document_id": "test-doc-123",
  "chunks_processed": 10
}
```

### Step 2: Check Logs

```powershell
gcloud functions logs read orchestrate --region=us-central1 --limit=50
```

**Look for these SUCCESS indicators:**
```
✓ Creating new Neo4j driver...
✓ Retrieving secret: NEO4J_URI
✓ Successfully retrieved secret: NEO4J_URI (length: 47)
✓ Retrieving secret: NEO4J_USER
✓ Successfully retrieved secret: NEO4J_USER (length: 5)
✓ Retrieving secret: NEO4J_PASSWORD
✓ Successfully retrieved secret: NEO4J_PASSWORD (length: 32)
✓ Connecting to Neo4j:
✓   URI: neo4j+s://xxxxx.databases.neo4j.io
✓   User: neo4j
✓   Password length: 32
✓ Verifying Neo4j connectivity...
✓ Neo4j connection verified successfully
```

**Watch out for these FAILURE indicators:**
```
✗ Failed to retrieve secret
✗ Failed to create Neo4j driver
✗ Neo.ClientError.Security.Unauthorized
✗ Connection refused
```

### Step 3: Verify Data in Neo4j

1. Log into Neo4j AuraDB console
2. Run query to check for test document:
   ```cypher
   MATCH (d:Document {id: "test-doc-123"})
   RETURN d
   ```
3. Verify chunks were created:
   ```cypher
   MATCH (d:Document {id: "test-doc-123"})-[:HAS_CHUNK]->(c:Chunk)
   RETURN count(c) as chunk_count
   ```

---

## Success Criteria

Mark each as complete when verified:

- [ ] **Deployment successful**
  - [ ] No errors during deployment
  - [ ] Function status shows ACTIVE
  - [ ] New version deployed

- [ ] **Function invocation successful**
  - [ ] HTTP 200 response received
  - [ ] Response contains success status
  - [ ] No timeout errors

- [ ] **Logs show success**
  - [ ] "Creating new Neo4j driver..." present
  - [ ] "Neo4j connection verified successfully" present
  - [ ] No "Unauthorized" errors
  - [ ] No "Failed to create driver" errors

- [ ] **Data stored correctly**
  - [ ] Document node created in Neo4j
  - [ ] Chunks created and linked
  - [ ] Embeddings stored
  - [ ] Firestore status updated to "completed"

---

## Troubleshooting

### Issue: Deployment fails

**Check:**
- [ ] gcloud CLI authenticated: `gcloud auth list`
- [ ] Correct project set: `gcloud config get-value project`
- [ ] Service account exists and has permissions

**Solution:**
```powershell
gcloud auth login
gcloud config set project aletheia-codex-prod
```

### Issue: Function invocation fails with 403

**Check:**
- [ ] Identity token is valid
- [ ] User has invoker permissions

**Solution:**
```powershell
gcloud functions add-invoker-policy-binding orchestrate `
    --region=us-central1 `
    --member="user:tony@aletheiacodex.com"
```

### Issue: Still getting "Unauthorized" errors

**Check:**
- [ ] Secrets exist and are accessible
- [ ] Service account has secretAccessor role
- [ ] Neo4j credentials are correct

**Solution:**
See `TROUBLESHOOTING_GUIDE.md` for detailed steps

### Issue: Function times out

**Check:**
- [ ] Neo4j instance is running
- [ ] Network connectivity from Cloud Functions
- [ ] No IP filtering blocking connections

**Solution:**
Check Neo4j AuraDB console for network settings

---

## Rollback Procedure

If the fix causes issues:

1. **Restore backup:**
   ```powershell
   cd C:\dev\aletheia-codex
   cp shared/db/neo4j_client.py.backup shared/db/neo4j_client.py
   ```

2. **Commit and push:**
   ```powershell
   git add shared/db/neo4j_client.py
   git commit -m "Rollback: Restore original neo4j_client.py"
   git push origin main
   ```

3. **Redeploy:**
   ```powershell
   cd functions/orchestration
   gcloud functions deploy orchestrate `
       --gen2 `
       --runtime=python311 `
       --region=us-central1 `
       --source=. `
       --entry-point=orchestrate `
       --trigger-http `
       --service-account=aletheia-functions@aletheia-codex-prod.iam.gserviceaccount.com
   ```

---

## Monitoring After Deployment

### First 24 Hours

- [ ] **Monitor function invocations**
  ```powershell
  gcloud functions logs read orchestrate --region=us-central1 --limit=100
  ```

- [ ] **Check error rates**
  - View in Cloud Console → Cloud Functions → orchestrate → Logs
  - Look for any new error patterns

- [ ] **Verify performance**
  - Check execution times
  - Monitor memory usage
  - Verify no timeouts

### First Week

- [ ] **Process real documents**
  - Test with actual user documents
  - Verify end-to-end pipeline works
  - Check data quality in Neo4j

- [ ] **Monitor costs**
  - Check Cloud Functions invocations
  - Monitor Secret Manager access
  - Verify Neo4j connection counts

---

## Documentation Reference

| Document | Purpose | When to Use |
|----------|---------|-------------|
| `README_NEO4J_FIX.md` | Quick start guide | **Start here** |
| `DEPLOYMENT_CHECKLIST.md` | Step-by-step deployment | **During deployment** |
| `NEO4J_FIX_SUMMARY.md` | Complete technical overview | Understanding the fix |
| `CODE_COMPARISON.md` | Code changes | Reviewing what changed |
| `TROUBLESHOOTING_GUIDE.md` | Problem solving | If issues occur |
| `neo4j_auth_analysis.md` | Technical analysis | Deep understanding |
| `test_neo4j_connection.py` | Testing script | Local testing |

---

## Support Contacts

If you encounter issues:

1. **Check documentation first**
   - Review `TROUBLESHOOTING_GUIDE.md`
   - Check `NEO4J_FIX_SUMMARY.md`

2. **Verify environment**
   - Check Cloud Functions logs
   - Review Neo4j AuraDB console
   - Verify Secret Manager values

3. **Test locally**
   - Use `test_neo4j_connection.py`
   - Test from Cloud Shell
   - Compare with local execution

---

## Final Notes

- **Backup created:** `shared/db/neo4j_client.py.backup`
- **Easy rollback:** Just restore backup and redeploy
- **Low risk:** Changes are isolated to one file
- **High confidence:** Addresses root cause directly

**Estimated time:** 10-15 minutes total
**Risk level:** Low
**Success probability:** High

---

## Completion Sign-off

Once all steps are complete:

- [ ] Deployment successful
- [ ] Testing passed
- [ ] Logs show success
- [ ] Data verified in Neo4j
- [ ] No errors in production
- [ ] Team notified of changes

**Deployed by:** _________________
**Date:** _________________
**Time:** _________________
**Result:** ☐ Success  ☐ Rollback needed

---

*Ready to deploy? Start with `.\apply_neo4j_fix.ps1` and follow this checklist!* 🚀