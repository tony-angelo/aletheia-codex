# Neo4j Authentication Troubleshooting Guide

## Quick Summary

**Problem:** Neo4j authentication fails in Cloud Functions but works locally.

**Most Likely Cause:** Driver caching issue in `neo4j_client.py`

**Quick Fix:** Replace `shared/db/neo4j_client.py` with `shared/db/neo4j_client_fixed.py`

---

## Detailed Analysis

### The Caching Problem

The current `neo4j_client.py` uses a module-level singleton pattern:

```python
_driver: Optional[Driver] = None

def get_neo4j_driver(project_id: str = "aletheia-codex-prod") -> Driver:
    global _driver
    if _driver is None:
        uri = get_secret(project_id, "NEO4J_URI")
        user = get_secret(project_id, "NEO4J_USER")
        password = get_secret(project_id, "NEO4J_PASSWORD")
        _driver = GraphDatabase.driver(uri, auth=(user, password))
    return _driver
```

**Why this causes issues:**

1. **Instance Reuse**: Cloud Functions reuse instances between invocations
2. **Stale Credentials**: If the driver is created with wrong credentials, it persists
3. **No Validation**: Cached driver is returned without verifying it still works
4. **Secret Changes**: If secrets are updated, cached driver still uses old values

### Why It Works Locally

- Each local script execution creates a fresh Python process
- No instance reuse between runs
- Driver is always created with current credentials
- No caching across executions

### Why It Fails in Cloud Functions

- Cloud Functions reuse instances for performance
- Module-level variables persist across invocations
- If first invocation fails, subsequent ones use the same failed driver
- No mechanism to detect and refresh stale connections

---

## Solution: Remove Driver Caching

### Option 1: Use Fixed Client (Recommended)

Replace the current client with the fixed version:

```bash
cd aletheia-codex
cp shared/db/neo4j_client_fixed.py shared/db/neo4j_client.py
```

**Key improvements:**
- No module-level caching
- Fresh driver on each invocation
- Immediate connectivity verification
- Comprehensive logging
- Proper resource management

### Option 2: Modify Existing Client

If you prefer to modify the existing client, make these changes:

1. **Remove the global driver variable:**
```python
# Remove this:
# _driver: Optional[Driver] = None
```

2. **Always create fresh driver:**
```python
def get_neo4j_driver(project_id: str = "aletheia-codex-prod") -> Driver:
    # Always create new driver
    uri = get_secret(project_id, "NEO4J_URI")
    user = get_secret(project_id, "NEO4J_USER")
    password = get_secret(project_id, "NEO4J_PASSWORD")
    driver = GraphDatabase.driver(uri, auth=(user, password))
    
    # Verify connectivity immediately
    driver.verify_connectivity()
    
    return driver
```

3. **Update orchestration function to close driver:**
```python
driver = get_neo4j_driver(PROJECT_ID)
try:
    with driver.session() as session:
        # Your queries here
        pass
finally:
    driver.close()
```

---

## Testing the Fix

### Step 1: Deploy Updated Code

```bash
cd aletheia-codex/functions/orchestration
# Make sure neo4j_client.py is updated
gcloud functions deploy orchestrate \
    --gen2 \
    --runtime=python311 \
    --region=us-central1 \
    --source=. \
    --entry-point=orchestrate \
    --trigger-http \
    --service-account=aletheia-functions@aletheia-codex-prod.iam.gserviceaccount.com
```

### Step 2: Test the Function

```bash
# Get identity token
TOKEN=$(gcloud auth print-identity-token)

# Invoke function
curl -X POST \
  https://us-central1-aletheia-codex-prod.cloudfunctions.net/orchestrate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "test-doc-123",
    "action": "process_document"
  }'
```

### Step 3: Check Logs

```bash
gcloud functions logs read orchestrate \
    --region=us-central1 \
    --limit=50
```

**Look for:**
- ✓ "Creating new Neo4j driver..."
- ✓ "Neo4j connection verified successfully"
- ✗ Any authentication errors

---

## Alternative Causes (If Fix Doesn't Work)

### 1. Network/IP Filtering

**Check:** Neo4j AuraDB console → Network settings

**Symptoms:**
- Connection timeout
- "Connection refused" errors

**Solution:**
- Disable IP filtering temporarily to test
- Or add Cloud Functions egress IPs to allowlist
- Or use VPC connector for static IP

### 2. Credential Issues

**Check:** Verify secrets contain correct values

```bash
gcloud secrets versions access latest --secret="NEO4J_URI"
gcloud secrets versions access latest --secret="NEO4J_USER"
gcloud secrets versions access latest --secret="NEO4J_PASSWORD"
```

**Symptoms:**
- "Unauthorized" error
- "Invalid credentials" error

**Solution:**
- Verify credentials work locally
- Check for special characters in password
- Ensure secrets are in correct format

### 3. Service Account Permissions

**Check:** IAM permissions on secrets

```bash
gcloud secrets get-iam-policy NEO4J_URI
gcloud secrets get-iam-policy NEO4J_USER
gcloud secrets get-iam-policy NEO4J_PASSWORD
```

**Required:** Service account needs `roles/secretmanager.secretAccessor`

**Solution:**
```bash
gcloud secrets add-iam-policy-binding NEO4J_URI \
    --member="serviceAccount:aletheia-functions@aletheia-codex-prod.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

---

## Verification Checklist

- [ ] Updated neo4j_client.py to remove caching
- [ ] Added driver.verify_connectivity() call
- [ ] Added proper driver.close() in finally block
- [ ] Deployed updated code to Cloud Functions
- [ ] Tested function invocation
- [ ] Checked logs for success messages
- [ ] Verified Neo4j queries execute successfully

---

## Performance Considerations

**Q: Won't creating a new driver on each invocation be slow?**

A: The performance impact is minimal because:
1. Driver creation is fast (~100ms)
2. Cloud Functions reuse instances, so not every request creates new driver
3. Connection pooling happens at the driver level
4. Correctness is more important than micro-optimizations

**Q: Should we implement connection pooling?**

A: The Neo4j driver already implements connection pooling internally. Creating a new driver doesn't mean creating new connections for every query.

---

## Long-term Solution

For production, consider:

1. **Health Checks**: Add periodic connectivity checks
2. **Retry Logic**: Implement exponential backoff for transient failures
3. **Monitoring**: Add metrics for connection success/failure rates
4. **Circuit Breaker**: Prevent cascading failures
5. **Connection Pooling**: Fine-tune driver configuration

---

## Contact & Support

If issues persist after trying these solutions:

1. Check Neo4j AuraDB console for connection logs
2. Review Cloud Functions logs for detailed error messages
3. Test connection from Cloud Shell (similar environment to Cloud Functions)
4. Consider opening support ticket with Neo4j if issue is on their side

---

## Additional Resources

- [Neo4j Python Driver Documentation](https://neo4j.com/docs/python-manual/current/)
- [Google Cloud Functions Best Practices](https://cloud.google.com/functions/docs/bestpractices/tips)
- [Secret Manager Documentation](https://cloud.google.com/secret-manager/docs)