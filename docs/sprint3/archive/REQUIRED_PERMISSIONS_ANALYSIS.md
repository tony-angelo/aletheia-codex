# Required Permissions Analysis for Sprint 2 Testing

**Date:** November 9, 2025  
**Current Service Account:** `superninja@aletheia-codex-prod.iam.gserviceaccount.com`

---

## 🔍 Current Permissions

The service account currently has these roles:

```
✅ roles/cloudfunctions.admin       - Can deploy and manage Cloud Functions
✅ roles/firestore.serviceAgent     - Firestore service agent (read-only in practice)
✅ roles/iam.serviceAccountAdmin    - Can manage service accounts
✅ roles/iam.serviceAccountUser     - Can use service accounts
✅ roles/logging.viewer             - Can view logs
✅ roles/run.admin                  - Can manage Cloud Run services
✅ roles/secretmanager.admin        - Can manage secrets
```

---

## ❌ Missing Permissions

To complete the remaining Sprint 2 tasks, the service account needs:

### 1. Firestore Write Access
**Required for:** Creating test documents

**Options:**

#### Option A: Add Firestore User Role (Recommended)
```bash
gcloud projects add-iam-policy-binding aletheia-codex-prod \
  --member="serviceAccount:superninja@aletheia-codex-prod.iam.gserviceaccount.com" \
  --role="roles/datastore.user"
```

**Permissions granted:**
- `datastore.databases.get`
- `datastore.entities.create` ✅ (needed)
- `datastore.entities.update` ✅ (needed)
- `datastore.entities.get` ✅ (needed)
- `datastore.entities.list`

#### Option B: Add Firestore Owner Role (More Permissive)
```bash
gcloud projects add-iam-policy-binding aletheia-codex-prod \
  --member="serviceAccount:superninja@aletheia-codex-prod.iam.gserviceaccount.com" \
  --role="roles/datastore.owner"
```

**Permissions granted:**
- All datastore.* permissions
- Can create, read, update, delete documents

### 2. Neo4j Access (Already Available via Secret Manager)
**Status:** ✅ Already have `roles/secretmanager.admin`

The deployed function can access Neo4j credentials from Secret Manager, so no additional permissions needed.

---

## 📋 Tasks Breakdown

### Task 1: Create Test Document in Firestore
**Status:** ❌ Blocked by permissions  
**Required Permission:** `datastore.entities.create`  
**Current Capability:** Cannot write to Firestore

**What I can do with additional permissions:**
```python
# Create test document
doc_ref = db.collection('documents').document('test-ai-sprint2-final')
doc_ref.set({
    'title': 'Sprint 2 AI Test Document',
    'content': '[Test content with entities]',
    'user_id': 'test-user-sprint2',
    'status': 'pending',
    'file_path': 'raw/test-ai-sprint2.txt',
    'created_at': firestore.SERVER_TIMESTAMP,
    'updated_at': firestore.SERVER_TIMESTAMP
})
```

### Task 2: Test the Deployed Function
**Status:** ✅ Can do now  
**Required Permission:** None (function is public with Bearer token)  
**Current Capability:** Can call the function

**What I can do now:**
```bash
TOKEN=$(gcloud auth print-identity-token)
curl -X POST \
  "https://us-central1-aletheia-codex-prod.cloudfunctions.net/orchestrate" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"document_id": "test-ai-sprint2-final", "user_id": "test-user-sprint2"}'
```

### Task 3: Verify AI Extraction Results
**Status:** ⚠️ Partially blocked  
**Required Permission:** `datastore.entities.get` (for reading Firestore)  
**Current Capability:** Can read logs, but cannot read Firestore directly

**What I can do now:**
- ✅ Read function logs to see execution
- ✅ Check for errors in logs
- ❌ Cannot read `review_queue` collection directly
- ❌ Cannot read `usage_logs` collection directly

**What I can do with additional permissions:**
```python
# Read review queue
review_queue = db.collection('review_queue').where('document_id', '==', 'test-ai-sprint2-final').get()
for item in review_queue:
    print(f"Entity: {item.to_dict()}")

# Read usage logs
usage_logs = db.collection('usage_logs').where('document_id', '==', 'test-ai-sprint2-final').get()
for log in usage_logs:
    print(f"Cost: {log.to_dict()}")
```

### Task 4: Validate Cost Monitoring
**Status:** ⚠️ Partially blocked  
**Required Permission:** `datastore.entities.get` (for reading Firestore)  
**Current Capability:** Can see costs in logs, but cannot read usage_logs collection

**What I can do now:**
- ✅ Read function logs to see token usage
- ✅ Calculate costs from logs
- ❌ Cannot read `usage_logs` collection directly

**What I can do with additional permissions:**
```python
# Read usage logs and calculate total cost
usage_logs = db.collection('usage_logs').where('document_id', '==', 'test-ai-sprint2-final').get()
total_cost = sum(log.to_dict().get('cost', 0) for log in usage_logs)
print(f"Total cost: ${total_cost:.6f}")
```

---

## 🎯 Recommended Solution

### Option 1: Grant Firestore User Role (Recommended)

**Command:**
```bash
gcloud projects add-iam-policy-binding aletheia-codex-prod \
  --member="serviceAccount:superninja@aletheia-codex-prod.iam.gserviceaccount.com" \
  --role="roles/datastore.user"
```

**Why this is recommended:**
- ✅ Minimal permissions (principle of least privilege)
- ✅ Allows reading and writing Firestore documents
- ✅ Sufficient for all testing tasks
- ✅ Does not grant excessive permissions

**What this enables:**
- ✅ Create test documents
- ✅ Read review_queue collection
- ✅ Read usage_logs collection
- ✅ Verify AI extraction results
- ✅ Validate cost monitoring

### Option 2: User Creates Test Document Manually (Current Approach)

**What user needs to do:**
1. Go to Firebase Console
2. Create document in `documents` collection
3. Provide document ID to me
4. I can then test the function and read logs

**Pros:**
- ✅ No permission changes needed
- ✅ User maintains full control

**Cons:**
- ❌ Requires manual user action
- ❌ Cannot verify results in Firestore directly
- ❌ Can only see results in logs

---

## 📊 Comparison

| Task | Without Permissions | With datastore.user Role |
|------|-------------------|------------------------|
| Create test document | ❌ User must do manually | ✅ Can do automatically |
| Test function | ✅ Can do now | ✅ Can do now |
| Read review_queue | ❌ Cannot read | ✅ Can read and verify |
| Read usage_logs | ❌ Cannot read | ✅ Can read and verify |
| Verify AI extraction | ⚠️ Logs only | ✅ Full verification |
| Validate costs | ⚠️ Logs only | ✅ Full validation |
| Complete testing | ⚠️ Partial | ✅ Complete |

---

## 🚀 What I Can Do Right Now

Even without additional permissions, I can:

### 1. Test the Function (if document exists)
```bash
# Call the function with an existing document
TOKEN=$(gcloud auth print-identity-token)
curl -X POST \
  "https://us-central1-aletheia-codex-prod.cloudfunctions.net/orchestrate" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"document_id": "EXISTING_DOC_ID", "user_id": "test-user-sprint2"}'
```

### 2. Monitor Function Execution
```bash
# View function logs in real-time
gcloud functions logs read orchestrate --region=us-central1 --follow
```

### 3. Analyze Logs for Results
```bash
# Search logs for entity extraction
gcloud functions logs read orchestrate --region=us-central1 --limit=100 | grep -i "entity"

# Search logs for cost information
gcloud functions logs read orchestrate --region=us-central1 --limit=100 | grep -i "cost"

# Search logs for errors
gcloud functions logs read orchestrate --region=us-central1 --limit=100 | grep -i "error"
```

### 4. Verify Function Status
```bash
# Check function is running
gcloud functions describe orchestrate --region=us-central1

# Check recent invocations
gcloud functions logs read orchestrate --region=us-central1 --limit=20
```

---

## 💡 Recommendation

**For complete autonomous testing, grant the `roles/datastore.user` role:**

```bash
gcloud projects add-iam-policy-binding aletheia-codex-prod \
  --member="serviceAccount:superninja@aletheia-codex-prod.iam.gserviceaccount.com" \
  --role="roles/datastore.user"
```

**This will enable me to:**
1. ✅ Create test documents automatically
2. ✅ Test the deployed function
3. ✅ Verify AI extraction results in Firestore
4. ✅ Validate cost monitoring in usage_logs
5. ✅ Complete Sprint 2 testing to 100%

**Estimated time to complete with permissions:** 10-15 minutes  
**Estimated time to complete without permissions:** 15-20 minutes (requires user manual steps)

---

## 🔒 Security Considerations

**The `roles/datastore.user` role is safe because:**
- ✅ It's a standard Google-managed role
- ✅ It follows principle of least privilege
- ✅ It only grants read/write access to Firestore
- ✅ It does not grant admin or delete permissions
- ✅ It's commonly used for application service accounts

**Alternative: Create custom role with minimal permissions:**
```bash
gcloud iam roles create firestoreTestWriter \
  --project=aletheia-codex-prod \
  --title="Firestore Test Writer" \
  --description="Minimal permissions for testing" \
  --permissions="datastore.entities.create,datastore.entities.get,datastore.entities.list" \
  --stage=GA
```

---

## 📝 Summary

**Current Status:**
- ✅ Function deployed and working
- ✅ Can test function if document exists
- ✅ Can monitor logs
- ❌ Cannot create test documents
- ❌ Cannot read Firestore collections directly

**To Complete Sprint 2 Testing:**

**Option A: Grant permissions (10-15 minutes)**
```bash
gcloud projects add-iam-policy-binding aletheia-codex-prod \
  --member="serviceAccount:superninja@aletheia-codex-prod.iam.gserviceaccount.com" \
  --role="roles/datastore.user"
```

**Option B: User creates document manually (15-20 minutes)**
- User creates test document in Firebase Console
- I test function and analyze logs
- Partial verification only

**Recommendation:** Option A for complete autonomous testing

---

**Created:** November 9, 2025  
**Status:** Awaiting user decision on permissions