# Neo4j Cloud Function Connection Issue - Bug Report for Jules

## Problem Summary

Cloud Function fails to connect to Neo4j Aura with "503 Illegal metadata" error, despite:
- ✅ Secrets being correctly formatted in Secret Manager
- ✅ Direct Python connections working perfectly
- ✅ Same secret retrieval method working outside Cloud Functions

## Environment

- **Platform:** Google Cloud Functions Gen 2 (Cloud Run)
- **Runtime:** Python 3.11
- **Function:** `orchestrate` (us-central1)
- **Project:** aletheia-codex-prod
- **Neo4j Driver:** Tested with both 5.15.0 and 6.0.3
- **Neo4j Instance:** Aura Free Tier (neo4j+s://ac286c9e.databases.neo4j.io)

## Error Details

### Primary Error
```
Neo4j processing failed: Timeout of 60.0s exceeded, last exception: 503 Illegal metadata
```

### gRPC Logs
```
E0000 00:00:1762618022.689779       7 plugin_credentials.cc:82] Plugin added invalid metadata value.
E0000 00:00:1762618022.689718       7 plugin_credentials.cc:79] validate_metadata_from_plugin: INTERNAL:Illegal header value
```

## Code That Fails

### Location
`shared/db/neo4j_client.py` - `create_neo4j_driver()` function

### Relevant Code
```python
from neo4j import GraphDatabase
from google.cloud import secretmanager

# Retrieve secrets from Secret Manager
client = secretmanager.SecretManagerServiceClient()
uri_response = client.access_secret_version(request={"name": f"projects/{project_id}/secrets/NEO4J_URI/versions/latest"})
user_response = client.access_secret_version(request={"name": f"projects/{project_id}/secrets/NEO4J_USER/versions/latest"})
pass_response = client.access_secret_version(request={"name": f"projects/{project_id}/secrets/NEO4J_PASSWORD/versions/latest"})

# Decode and clean
uri = uri_response.payload.data.decode("UTF-8").strip().replace('\n', '').replace('\r', '').replace('\t', '')
user = user_response.payload.data.decode("UTF-8").strip().replace('\n', '').replace('\r', '').replace('\t', '')
password = pass_response.payload.data.decode("UTF-8").strip().replace('\n', '').replace('\r', '').replace('\t', '')

# Create driver - THIS FAILS
driver = GraphDatabase.driver(
    uri,
    auth=(user, password),
    connection_timeout=60,
    max_connection_lifetime=3600,
    max_connection_pool_size=50,
    connection_acquisition_timeout=60
)

# Verify connectivity - NEVER REACHES HERE
driver.verify_connectivity()
```

## What Works

### 1. Direct Python Connection (Outside Cloud Functions)
```python
from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    "neo4j+s://ac286c9e.databases.neo4j.io",
    auth=("neo4j", "LrVUYKHm7Uu8KWTYlDNnDnWYALD8v9KzdTzPl11WB6E")
)
driver.verify_connectivity()  # ✅ SUCCESS
driver.close()
```

**Result:** ✅ Works perfectly every time

### 2. Secret Retrieval Test (Same Method as Function)
```python
from google.cloud import secretmanager
from neo4j import GraphDatabase

client = secretmanager.SecretManagerServiceClient()

# Retrieve exactly as function does
uri_response = client.access_secret_version(request={"name": "projects/aletheia-codex-prod/secrets/NEO4J_URI/versions/latest"})
user_response = client.access_secret_version(request={"name": "projects/aletheia-codex-prod/secrets/NEO4J_USER/versions/latest"})
pass_response = client.access_secret_version(request={"name": "projects/aletheia-codex-prod/secrets/NEO4J_PASSWORD/versions/latest"})

uri = uri_response.payload.data.decode("UTF-8").strip().replace('\n', '').replace('\r', '').replace('\t', '')
user = user_response.payload.data.decode("UTF-8").strip().replace('\n', '').replace('\r', '').replace('\t', '')
password = pass_response.payload.data.decode("UTF-8").strip().replace('\n', '').replace('\r', '').replace('\t', '')

driver = GraphDatabase.driver(uri, auth=(user, password))
driver.verify_connectivity()  # ✅ SUCCESS
driver.close()
```

**Result:** ✅ Works perfectly

## What Fails

### Cloud Function Execution
- **Function Name:** orchestrate
- **Revision:** orchestrate-00019-doy (latest)
- **Error:** 503 Illegal metadata (gRPC level)
- **Timing:** Fails during `GraphDatabase.driver()` call, before `verify_connectivity()`

## Secret Verification

### NEO4J_URI
```bash
$ gcloud secrets versions access latest --secret=NEO4J_URI --project=aletheia-codex-prod | od -An -tx1
 6e 65 6f 34 6a 2b 73 3a 2f 2f 61 63 32 38 36 63
 39 65 2e 64 61 74 61 62 61 73 65 73 2e 6e 65 6f
 34 6a 2e 69 6f
```
- **Length:** 37 characters
- **Value:** `neo4j+s://ac286c9e.databases.neo4j.io`
- **Status:** ✅ Clean, no trailing whitespace

### NEO4J_USER
```bash
$ gcloud secrets versions access latest --secret=NEO4J_USER --project=aletheia-codex-prod | od -An -tx1
 6e 65 6f 34 6a
```
- **Length:** 5 characters
- **Value:** `neo4j`
- **Status:** ✅ Clean, no trailing whitespace

### NEO4J_PASSWORD
```bash
$ gcloud secrets versions access latest --secret=NEO4J_PASSWORD --project=aletheia-codex-prod | wc -c
43
```
- **Length:** 43 characters
- **Value:** `LrVUYKHm7Uu8KWTYlDNnDnWYALD8v9KzdTzPl11WB6E`
- **Status:** ✅ Clean, no trailing whitespace

## Troubleshooting Steps Attempted

### 1. Secret Format Fixes ✅
- Updated all three secrets to remove trailing whitespace
- Verified with hex dump (`od -c`)
- Confirmed lengths match expected values

### 2. Function Redeployments ✅
- Deployed 3 new revisions (00017, 00018, 00019)
- Each deployment created fresh Cloud Run instances
- Waited for cache expiry between attempts

### 3. Neo4j Driver Version Changes ✅
- Upgraded from neo4j 5.15.0 to 6.0.3
- Tested both versions - same error

### 4. Code Modifications ✅
- Added explicit string cleaning: `str(value).strip()`
- Added type conversion to ensure pure strings
- Added extensive logging (logs don't appear in Cloud Functions)

### 5. Cache Clearing ✅
- Waited 20+ minutes for cache expiry
- Redeployed function multiple times
- Created new Cloud Run revisions

## Key Observations

### 1. gRPC Error Timing
The error occurs at the gRPC plugin level, not at Neo4j authentication:
```
plugin_credentials.cc:79] validate_metadata_from_plugin: INTERNAL:Illegal header value
plugin_credentials.cc:82] Plugin added invalid metadata value
```

This suggests the issue is with how credentials are passed to gRPC, not with Neo4j itself.

### 2. Missing Logs
Logs that should appear don't show up in Cloud Functions:
```python
logger.info(f"Connecting to Neo4j:")  # ❌ Never appears
logger.info(f"  URI: {uri}")          # ❌ Never appears
logger.info(f"  User: {user}")        # ❌ Never appears
```

But earlier logs do appear:
```python
logger.info(f"Creating Neo4j driver...")  # ✅ Appears
```

This suggests the code is failing silently between these log statements.

### 3. Environment-Specific
- ✅ Works: Local Python script
- ✅ Works: Python script with Secret Manager
- ❌ Fails: Cloud Functions Gen 2
- ❌ Fails: Cloud Run (underlying platform)

## Hypotheses

### Hypothesis 1: gRPC Configuration Issue
Cloud Run may have gRPC settings that conflict with Neo4j's Bolt protocol over TLS.

**Evidence:**
- Error is at gRPC plugin level, not Neo4j level
- Same code works outside Cloud Run
- Error message: "Illegal header value" suggests metadata/header issue

### Hypothesis 2: TLS/SSL Certificate Issue
Cloud Run's TLS handling may interfere with Neo4j's `neo4j+s://` protocol.

**Evidence:**
- Protocol uses TLS (`+s`)
- gRPC error suggests metadata validation failure
- Could be certificate chain or SNI issue

### Hypothesis 3: Network/Proxy Configuration
Cloud Run may route traffic through a proxy that mangles Neo4j connection metadata.

**Evidence:**
- gRPC metadata validation fails
- Direct connections work
- Cloud Run has different network path

### Hypothesis 4: Neo4j Driver + Cloud Run Incompatibility
Known issue between Neo4j Python driver and Cloud Run environment.

**Evidence:**
- Tested with two driver versions (5.15.0, 6.0.3)
- Both fail identically
- No known workarounds found

## Reproduction Steps

### 1. Deploy Function
```bash
cd functions/orchestration
gcloud functions deploy orchestrate \
  --gen2 \
  --runtime=python311 \
  --region=us-central1 \
  --source=. \
  --entry-point=orchestrate \
  --trigger-http \
  --project=aletheia-codex-prod
```

### 2. Invoke Function
```bash
curl -X POST \
  -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
  -H "Content-Type: application/json" \
  -d '{"document_id": "test-doc", "action": "process_document"}' \
  https://orchestrate-h55nns6ojq-uc.a.run.app
```

### 3. Observe Error
```json
{"error":"Neo4j processing failed: Timeout of 60.0s exceeded, last exception: 503 Illegal metadata"}
```

### 4. Check Logs
```bash
gcloud logging read \
  'resource.type=cloud_run_revision AND resource.labels.service_name=orchestrate' \
  --limit=50 \
  --project=aletheia-codex-prod
```

**Expected:** gRPC errors about "Illegal header value"

## Files for Reference

### Function Code
- **Main:** `functions/orchestration/main.py`
- **Neo4j Client:** `shared/db/neo4j_client.py`
- **Requirements:** `functions/orchestration/requirements.txt`

### Test Scripts
- **Direct Connection:** `/workspace/test_neo4j_direct.py` (✅ Works)
- **Secret Retrieval:** `/workspace/test_secret_retrieval.py` (✅ Works)
- **Function Test:** `/workspace/test_with_new_document.py` (❌ Fails)

### Documentation
- **Full Analysis:** `/workspace/NEO4J_CONNECTION_TEST_RESULTS.md`
- **Secret Guide:** `/workspace/SECRET_MANAGEMENT_GUIDE.md`
- **Cache Issue:** `/workspace/CACHE_ISSUE_RESOLUTION.md`

## Questions for Jules

1. **Is this a known issue** with Neo4j Python driver and Cloud Run/Cloud Functions Gen 2?

2. **Are there gRPC configuration options** in Cloud Run that could affect Neo4j connections?

3. **Could this be a TLS/SSL issue** with the `neo4j+s://` protocol in Cloud Run?

4. **Are there network proxy settings** in Cloud Run that could interfere with Bolt protocol?

5. **Should we use a different connection method** (e.g., REST API instead of Bolt)?

6. **Are there Cloud Run environment variables** that could help (e.g., gRPC settings)?

7. **Could this be related to Cloud Run's security sandbox** blocking certain connection types?

## Desired Outcome

Get the Cloud Function to successfully connect to Neo4j Aura using the Bolt protocol (`neo4j+s://`), just like the direct Python script does.

## Workarounds Considered

### Option 1: Use Neo4j HTTP API
Instead of Bolt protocol, use Neo4j's HTTP API.
- **Pro:** Might avoid gRPC issues
- **Con:** Different API, requires code rewrite

### Option 2: Deploy to Different Platform
Use Cloud Run directly instead of Cloud Functions.
- **Pro:** More control over environment
- **Con:** More complex deployment

### Option 3: Use Connection Proxy
Route through a proxy service.
- **Pro:** Might bypass Cloud Run restrictions
- **Con:** Added complexity and latency

### Option 4: Contact Neo4j Support
Get official guidance from Neo4j.
- **Pro:** Authoritative answer
- **Con:** May take time

## Additional Context

- **Project:** aletheia-codex (document processing with knowledge graphs)
- **Sprint:** Sprint 1 (95% complete, blocked by this issue)
- **Timeline:** Issue discovered 2024-11-08, 6+ hours debugging
- **Impact:** Cannot create knowledge graphs from processed documents

## Contact

- **Repository:** tony-angelo/aletheia-codex
- **Issue:** #4 (Neo4j Secret Manager Configuration)
- **PR:** #5 (Documentation updates)

---

**Status:** Awaiting Jules analysis and recommendations
**Priority:** HIGH (blocks Sprint 1 completion)
**Complexity:** Infrastructure/Environment issue, not code bug