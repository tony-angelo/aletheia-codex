# Secret Management Guide - Neo4j Configuration

**Critical:** This guide documents the correct way to store and manage Neo4j secrets in Secret Manager to avoid authentication issues.

---

## ⚠️ Common Issue: Trailing Whitespace

**Problem:** Secrets stored with trailing whitespace (newlines, carriage returns) cause Neo4j authentication to fail with `503 Illegal metadata` errors.

**Symptoms:**
- Orchestration function fails with "Neo4j processing failed: Timeout of 60.0s exceeded, last exception: 503 Illegal metadata"
- gRPC logs show "Plugin added invalid metadata value" or "Illegal header value"
- Direct Neo4j connection works, but Cloud Function connection fails

**Root Cause:** Neo4j's gRPC client rejects credentials containing control characters or trailing whitespace.

---

## ✅ Correct Secret Storage

### Required Secrets

The orchestration function requires three Neo4j secrets:

1. **NEO4J_URI** - Neo4j connection URI
2. **NEO4J_USER** - Neo4j username
3. **NEO4J_PASSWORD** - Neo4j password

### Proper Storage Commands

**CRITICAL:** Always use `echo -n` to prevent adding trailing newlines.

```bash
# Store Neo4j URI (no trailing newline)
echo -n 'neo4j+s://your-instance-id.databases.neo4j.io' | \
  gcloud secrets versions add NEO4J_URI \
    --project=aletheia-codex-prod \
    --data-file=-

# Store Neo4j username (no trailing newline)
echo -n 'neo4j' | \
  gcloud secrets versions add NEO4J_USER \
    --project=aletheia-codex-prod \
    --data-file=-

# Store Neo4j password (no trailing newline)
echo -n 'your-neo4j-password-here' | \
  gcloud secrets versions add NEO4J_PASSWORD \
    --project=aletheia-codex-prod \
    --data-file=-
```

### PowerShell Commands (Windows)

```powershell
# Store Neo4j URI (no trailing newline)
[System.Text.Encoding]::UTF8.GetBytes('neo4j+s://your-instance-id.databases.neo4j.io') | `
  gcloud secrets versions add NEO4J_URI `
    --project=aletheia-codex-prod `
    --data-file=-

# Store Neo4j username (no trailing newline)
[System.Text.Encoding]::UTF8.GetBytes('neo4j') | `
  gcloud secrets versions add NEO4J_USER `
    --project=aletheia-codex-prod `
    --data-file=-

# Store Neo4j password (no trailing newline)
[System.Text.Encoding]::UTF8.GetBytes('your-neo4j-password-here') | `
  gcloud secrets versions add NEO4J_PASSWORD `
    --project=aletheia-codex-prod `
    --data-file=-
```

---

## 🔍 Verification

### Check Secret Lengths

```bash
# Verify URI length (should be exact character count, no extra bytes)
gcloud secrets versions access latest --secret=NEO4J_URI --project=aletheia-codex-prod | wc -c

# Verify USER length (should be 5 for 'neo4j')
gcloud secrets versions access latest --secret=NEO4J_USER --project=aletheia-codex-prod | wc -c

# Verify PASSWORD length (should match your password length exactly)
gcloud secrets versions access latest --secret=NEO4J_PASSWORD --project=aletheia-codex-prod | wc -c
```

### Check for Hidden Characters

```bash
# Display secret with visible control characters
gcloud secrets versions access latest --secret=NEO4J_URI --project=aletheia-codex-prod | od -c

# Should show ONLY the URI characters, no \r or \n at the end
```

### Expected Output (Clean Secret)

```
0000000   n   e   o   4   j   +   s   :   /   /   a   c   2   8   6   c
0000020   9   e   .   d   a   t   a   b   a   s   e   s   .   n   e   o
0000040   4   j   .   i   o
0000045
```

### Bad Output (Has Trailing Whitespace)

```
0000000   n   e   o   4   j   +   s   :   /   /   a   c   2   8   6   c
0000020   9   e   .   d   a   t   a   b   a   s   e   s   .   n   e   o
0000040   4   j   .   i   o  \r  \n    <-- PROBLEM: trailing \r\n
0000045
```

---

## 🔧 Fixing Existing Secrets

If you have secrets with trailing whitespace, update them:

```bash
# Get current values (they will be automatically stripped by the shell)
URI=$(gcloud secrets versions access latest --secret=NEO4J_URI --project=aletheia-codex-prod | tr -d '\r\n')
USER=$(gcloud secrets versions access latest --secret=NEO4J_USER --project=aletheia-codex-prod | tr -d '\r\n')
PASSWORD=$(gcloud secrets versions access latest --secret=NEO4J_PASSWORD --project=aletheia-codex-prod | tr -d '\r\n')

# Store clean versions
echo -n "$URI" | gcloud secrets versions add NEO4J_URI --project=aletheia-codex-prod --data-file=-
echo -n "$USER" | gcloud secrets versions add NEO4J_USER --project=aletheia-codex-prod --data-file=-
echo -n "$PASSWORD" | gcloud secrets versions add NEO4J_PASSWORD --project=aletheia-codex-prod --data-file=-
```

---

## ⏰ Cache Considerations

### Secret Caching in Cloud Functions

The orchestration function caches secrets for **5 minutes** (300 seconds) for performance. After updating secrets:

1. **Wait 5 minutes** for cache to expire, OR
2. **Wait 15-20 minutes** for function cold start (recommended), OR
3. **Redeploy the function** to force cache clear (requires Cloud Functions Admin role)

### Testing After Secret Update

```bash
# Wait for cache expiry
echo "Waiting 5 minutes for cache to expire..."
sleep 300

# Test the orchestration function
curl -X POST \
  -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
  -H "Content-Type: application/json" \
  -d '{"document_id": "test-doc-id", "action": "process_document"}' \
  https://orchestrate-h55nns6ojq-uc.a.run.app
```

---

## 📋 Initial Setup Checklist

When setting up Neo4j secrets for the first time:

- [ ] Obtain Neo4j Aura credentials (URI, username, password)
- [ ] Verify Neo4j instance is running (not paused)
- [ ] Create secrets using `echo -n` (bash) or `[System.Text.Encoding]::UTF8.GetBytes()` (PowerShell)
- [ ] Verify secret lengths match expected values
- [ ] Check for hidden characters using `od -c`
- [ ] Test direct Neo4j connection with credentials
- [ ] Deploy/redeploy orchestration function
- [ ] Test orchestration function end-to-end

---

## 🚨 Troubleshooting

### Issue: "503 Illegal metadata" Error

**Symptoms:**
```
{"error":"Neo4j processing failed: Timeout of 60.0s exceeded, last exception: 503 Illegal metadata"}
```

**Solution:**
1. Check secret lengths - they should match exact character counts
2. Use `od -c` to check for trailing `\r` or `\n`
3. Update secrets using `echo -n` (see "Fixing Existing Secrets" above)
4. Wait 5-20 minutes for cache expiry
5. Test again

### Issue: Direct Connection Works, Function Fails

**Cause:** Function is using cached secrets with trailing whitespace

**Solution:**
1. Verify secrets are clean (no trailing whitespace)
2. Wait for cache expiry (5-20 minutes)
3. Or redeploy function to clear cache

### Issue: Neo4j Instance Paused

**Symptoms:**
```
ServiceUnavailable: Unable to connect to neo4j+s://...
```

**Solution:**
1. Log into Neo4j Aura console: https://console.neo4j.io
2. Resume the paused instance
3. Wait 60 seconds for instance to start
4. Test connection again

---

## 📚 Related Documentation

- [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) - Main deployment guide
- [FINAL_STATUS_REPORT.md](/workspace/FINAL_STATUS_REPORT.md) - Detailed analysis of secret issue
- [GitHub Issue #4](https://github.com/tony-angelo/aletheia-codex/issues/4) - Secret management issue tracking

---

## 🎓 Best Practices

1. **Always use `echo -n`** when storing secrets via command line
2. **Verify secret contents** after storage, not just length
3. **Use hex dump** (`od -c`) to check for hidden characters
4. **Document secret formats** in your deployment guide
5. **Test with actual secrets** from Secret Manager, not hardcoded values
6. **Consider cache TTL** when rotating secrets
7. **Monitor function logs** for authentication errors

---

**Last Updated:** 2024-11-08  
**Issue Reference:** [#4](https://github.com/tony-angelo/aletheia-codex/issues/4)