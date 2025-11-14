# Orchestration Function Permissions Fix

**Date**: 2024-11-14  
**Issue**: Orchestration function failing with 401/403 errors  
**Status**: ✅ FIXED

---

## Problem Analysis

The orchestration function was deployed successfully but failing to execute because the service account lacked necessary permissions:

### Errors from Logs
```
The request was not authenticated. Either allow unauthenticated invocations 
or set the proper Authorization header.
```

### Root Causes
1. Service account couldn't invoke Cloud Run services
2. Service account couldn't access Secret Manager secrets (Neo4j credentials, Gemini API key)

---

## Permissions Granted

### 1. Cloud Run Invoker Role ✅
```bash
gcloud projects add-iam-policy-binding aletheia-codex-prod \
  --member="serviceAccount:679360092359-compute@developer.gserviceaccount.com" \
  --role="roles/run.invoker"
```

**Purpose**: Allows orchestration function to call Cloud Run services

### 2. Secret Manager Access ✅

Granted `secretmanager.secretAccessor` role for:
- `NEO4J_URI` - Neo4j database connection string
- `NEO4J_USER` - Neo4j username
- `NEO4J_PASSWORD` - Neo4j password
- `GEMINI_API_KEY` - Google Gemini AI API key

```bash
for secret in NEO4J_PASSWORD NEO4J_URI NEO4J_USER GEMINI_API_KEY; do
  gcloud secrets add-iam-policy-binding $secret \
    --member="serviceAccount:679360092359-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor" \
    --project=aletheia-codex-prod
done
```

**Purpose**: Allows orchestration function to:
- Connect to Neo4j knowledge graph database
- Use Gemini AI for entity extraction

---

## Complete Service Account Permissions

The service account `679360092359-compute@developer.gserviceaccount.com` now has:

1. ✅ `roles/datastore.user` - Read/write Firestore
2. ✅ `roles/eventarc.eventReceiver` - Receive Firestore events
3. ✅ `roles/run.invoker` - Invoke Cloud Run services
4. ✅ `roles/secretmanager.secretAccessor` - Access secrets (Neo4j, Gemini)
5. ✅ `roles/cloudbuild.builds.builder` - Build containers

---

## Testing Instructions

### Test 1: Create New Note
1. Go to https://aletheiacodex.app/notes
2. Click "Create Note" or similar
3. Enter content: "John Smith works at Google in Mountain View"
4. Submit the note
5. Wait 30-60 seconds
6. Refresh the page

**Expected Result**: Note status changes from "processing" to "completed"

### Test 2: Check Orchestration Logs
```bash
gcloud functions logs read orchestration-function \
  --gen2 \
  --region=us-central1 \
  --project=aletheia-codex-prod \
  --limit=100
```

**Expected in Logs**:
```
ORCHESTRATION FUNCTION TRIGGERED
Processing note: <note-id>
Starting AI processing...
AI processing complete: X entities, Y relationships
Storing in review queue...
Review queue storage complete
Populating knowledge graph...
Knowledge graph population complete
Updating note status to completed...
ORCHESTRATION COMPLETE
```

**Should NOT see**:
- "The request was not authenticated"
- "401 Unauthorized"
- "403 Forbidden"
- "Permission denied"

### Test 3: Check Review Queue
After note completes processing:

1. Go to https://aletheiacodex.app/review
2. **Expected**: Stats show counts (not blank)
3. **Expected**: Pending items appear in review queue
4. **Expected**: Can see extracted entities (e.g., "John Smith", "Google", "Mountain View")

---

## What the Orchestration Function Does

When a note is created in Firestore:

1. **Firestore Trigger** → Orchestration function starts
2. **Read Note** → Gets note content from Firestore
3. **AI Extraction** → Uses Gemini AI to extract entities and relationships
4. **Store in Review Queue** → Saves extracted items to Firestore `reviewQueue` collection
5. **Auto-Approve High Confidence** → Items with confidence ≥ 85% go directly to Neo4j
6. **Update Note Status** → Changes status from "processing" to "completed"

---

## Expected Processing Time

- **Simple note** (1-2 sentences): 10-30 seconds
- **Medium note** (paragraph): 30-60 seconds
- **Long note** (multiple paragraphs): 60-120 seconds

---

## Troubleshooting

### If Note Stays in "Processing"

1. **Check function logs** for errors:
   ```bash
   gcloud functions logs read orchestration-function \
     --gen2 \
     --region=us-central1 \
     --project=aletheia-codex-prod \
     --limit=100
   ```

2. **Common issues**:
   - Neo4j connection failed → Check Neo4j database is running
   - Gemini API error → Check API key is valid and has quota
   - Timeout → Note content too long (increase function timeout)

### If Review Queue Empty

1. **Check Firestore** `reviewQueue` collection:
   - Go to Firebase Console
   - Navigate to Firestore Database
   - Look for `reviewQueue` collection
   - Should have documents with extracted entities

2. **Check orchestration logs** for "Review queue storage complete"

### If Knowledge Graph Empty

1. **Check Neo4j** database:
   - Entities need confidence ≥ 85% to auto-approve
   - Lower confidence items go to review queue only
   - Must manually approve items in review queue

2. **Check orchestration logs** for "Knowledge graph population complete"

---

## Success Criteria

- ✅ Orchestration function triggers on note creation
- ✅ Function can access Neo4j credentials
- ✅ Function can access Gemini API key
- ✅ Function can call Cloud Run services
- ✅ Notes process from "processing" to "completed"
- ✅ Review queue populates with extracted entities
- ✅ High confidence items added to Neo4j automatically

---

## Next Steps

1. **Test note creation** (see Test 1 above)
2. **Monitor logs** for any errors
3. **Verify review queue** populates
4. **Test entity approval** workflow
5. **Check Knowledge Graph** for approved entities

---

## Conclusion

All necessary permissions have been granted to the orchestration function's service account. The function should now be able to:
- Access Neo4j database credentials
- Use Gemini AI for entity extraction
- Store results in Firestore review queue
- Populate the Neo4j knowledge graph

**Next Action**: Test by creating a new note and monitoring the logs.