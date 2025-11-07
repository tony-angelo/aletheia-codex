# Neo4j Authentication Issue Analysis

## Problem Summary
Neo4j authentication fails when the Cloud Function tries to connect, but works locally with the same credentials.

**Error:** `Neo.ClientError.Security.Unauthorized`

## Environment Comparison

### Local Environment (WORKING)
- Python 3.x with virtual environment
- Direct credential access
- Windows 10 with PowerShell
- Neo4j driver 5.15.0
- Direct internet connection

### Cloud Function Environment (FAILING)
- Python 3.11 runtime
- Google Cloud Functions Gen2
- Region: us-central1
- Service Account: `aletheia-functions@aletheia-codex-prod.iam.gserviceaccount.com`
- Secrets retrieved from Secret Manager
- Neo4j driver 5.15.0

## Known Facts

1. **Secrets are correct**: Local testing with same credentials works
2. **Secret retrieval works**: Secrets can be accessed from Secret Manager
3. **IAM permissions correct**: Service account has `secretAccessor` role
4. **Secret names match**: `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`
5. **Code syntax fixed**: Cypher queries corrected
6. **Function deployed**: State is ACTIVE

## Potential Root Causes

### 1. Driver Caching Issue (HIGH PROBABILITY)
**Problem:** Module-level singleton `_driver` may cache stale credentials

```python
_driver: Optional[Driver] = None

def get_neo4j_driver(project_id: str = "aletheia-codex-prod") -> Driver:
    global _driver
    if _driver is None:
        # Credentials retrieved here
        _driver = GraphDatabase.driver(uri, auth=(user, password))
    return _driver
```

**Why this matters:**
- Cloud Functions may reuse instances between invocations
- If credentials change, cached driver still uses old credentials
- Driver created with wrong credentials persists across invocations

**Solution:**
- Force driver recreation on each invocation
- Add credential validation before returning cached driver
- Implement driver refresh mechanism

### 2. Network/Egress IP Issue (MEDIUM PROBABILITY)
**Problem:** Cloud Function egress IP may not be whitelisted in Neo4j

**Why this matters:**
- Neo4j AuraDB may have IP filtering enabled
- Cloud Functions use dynamic egress IPs
- Local machine IP is different from Cloud Function IPs

**Solution:**
- Check Neo4j AuraDB network settings
- Verify if IP filtering is enabled
- Consider using VPC connector for static IP

### 3. Connection String Format (LOW PROBABILITY)
**Problem:** URI format may need adjustment for Cloud Functions

**Current format:** `neo4j+s://xxxxx.databases.neo4j.io`

**Considerations:**
- SSL/TLS certificate validation
- Connection timeout settings
- DNS resolution in Cloud Functions

### 4. Credential Encoding Issue (LOW PROBABILITY)
**Problem:** Password may contain special characters that need escaping

**Why this matters:**
- Secret Manager returns UTF-8 decoded strings
- Special characters in password may cause issues
- URL encoding may be needed

### 5. Authentication Method Mismatch (LOW PROBABILITY)
**Problem:** Neo4j may expect different auth method

**Current:** Basic auth with username/password
**Alternatives:** Token-based auth, certificate auth

## Diagnostic Steps

### Step 1: Verify Secret Values
```bash
gcloud secrets versions access latest --secret="NEO4J_URI"
gcloud secrets versions access latest --secret="NEO4J_USER"
gcloud secrets versions access latest --secret="NEO4J_PASSWORD"
```

### Step 2: Test Connection from Cloud Function
Add detailed logging to capture:
- Exact URI being used
- Username being used
- Password length (not actual password)
- Driver version
- Connection attempt timestamp

### Step 3: Check Neo4j Logs
- Access Neo4j AuraDB console
- Check connection logs
- Look for failed authentication attempts
- Note source IP addresses

### Step 4: Test with Fresh Driver
Modify code to force new driver on each invocation:
```python
def get_neo4j_driver(project_id: str = "aletheia-codex-prod") -> Driver:
    # Don't use cached driver - always create new
    uri = get_secret(project_id, "NEO4J_URI")
    user = get_secret(project_id, "NEO4J_USER")
    password = get_secret(project_id, "NEO4J_PASSWORD")
    return GraphDatabase.driver(uri, auth=(user, password))
```

### Step 5: Add Connection Verification
```python
driver = get_neo4j_driver(project_id)
driver.verify_connectivity()  # This will fail fast if auth is wrong
```

## Recommended Fix Priority

1. **IMMEDIATE**: Remove driver caching, create fresh driver each time
2. **HIGH**: Add detailed logging for debugging
3. **MEDIUM**: Check Neo4j network settings
4. **LOW**: Investigate connection string variations

## Testing Plan

1. Deploy modified code without driver caching
2. Invoke function and capture detailed logs
3. Compare logs with local execution
4. Check Neo4j console for connection attempts
5. Verify source IP in Neo4j logs
6. Test with explicit connection verification

## Next Steps

1. Modify `neo4j_client.py` to remove caching
2. Add comprehensive logging
3. Redeploy function
4. Test and capture logs
5. Analyze results
6. Implement permanent fix based on findings