# Orchestration Function Fix Guide

**Issue**: Notes stuck in "processing" status  
**Root Cause**: Orchestration function deployed incorrectly as Cloud Run HTTP service instead of Firestore-triggered Cloud Function  
**Solution**: Deploy as Cloud Function with Firestore trigger

---

## Problem Analysis

### Current State
1. **Frontend** creates notes directly in Firestore with `status: 'processing'`
2. **Orchestration function** should be triggered automatically when note is created
3. **Current deployment**: Deployed to Cloud Run as HTTP service (WRONG)
4. **Correct deployment**: Should be Cloud Function with Firestore trigger

### Evidence
From Cloud Run logs:
```
Failed to find attribute 'app' in 'main'.
Worker exited with code 4
App failed to load.
```

This happens because:
- Cloud Run expects an HTTP app
- Orchestration function is a CloudEvent handler (Firestore trigger)
- They are incompatible

---

## Solution: Deploy as Cloud Function

### Option 1: Deploy via gcloud CLI (Recommended)

```bash
cd /workspace/aletheia-codex/functions/orchestration

gcloud functions deploy orchestration-function \
  --gen2 \
  --runtime=python311 \
  --region=us-central1 \
  --source=. \
  --entry-point=orchestration_function \
  --trigger-event-filters="type=google.cloud.firestore.document.v1.created" \
  --trigger-event-filters="database=(default)" \
  --trigger-location=nam5 \
  --trigger-event-filters-path-pattern="document=notes/{noteId}" \
  --set-env-vars="GCP_PROJECT=aletheia-codex-prod" \
  --service-account=679360092359-compute@developer.gserviceaccount.com \
  --memory=512Mi \
  --timeout=540s \
  --max-instances=10 \
  --project=aletheia-codex-prod
```

**Key Parameters**:
- `--gen2`: Use Cloud Functions 2nd generation
- `--trigger-event-filters`: Firestore document created event
- `--trigger-location=nam5`: Match Firestore location
- `--trigger-event-filters-path-pattern`: Trigger on notes collection

### Option 2: Delete Cloud Run Service First

If the Cloud Run service exists, delete it first:

```bash
# Delete the incorrectly deployed Cloud Run service
gcloud run services delete orchestration-api \
  --region=us-central1 \
  --project=aletheia-codex-prod

# Then deploy as Cloud Function (use command from Option 1)
```

---

## Verification Steps

### 1. Check Function Deployment
```bash
gcloud functions describe orchestration-function \
  --gen2 \
  --region=us-central1 \
  --project=aletheia-codex-prod
```

**Expected Output**:
```
name: projects/aletheia-codex-prod/locations/us-central1/functions/orchestration-function
state: ACTIVE
eventTrigger:
  eventType: google.cloud.firestore.document.v1.created
  eventFilters:
  - attribute: database
    value: (default)
  triggerRegion: nam5
  eventFiltersPathPattern:
    document: notes/{noteId}
```

### 2. Test Note Processing

**Create a test note**:
1. Go to https://aletheiacodex.app/notes
2. Create a new note with some content
3. Wait 10-30 seconds

**Check note status**:
```bash
# View function logs
gcloud functions logs read orchestration-function \
  --gen2 \
  --region=us-central1 \
  --project=aletheia-codex-prod \
  --limit=50
```

**Expected in logs**:
```
ORCHESTRATION FUNCTION TRIGGERED
Processing note: <note-id>
AI extraction started
Entities extracted: X
Relationships extracted: Y
Note processing completed
```

### 3. Verify in Firestore

Check that:
1. Note status changed from `processing` to `completed`
2. `processingCompletedAt` timestamp is set
3. `extractionSummary` contains entity and relationship counts

### 4. Check Review Queue

```bash
# Check if review queue items were created
gcloud firestore databases export gs://aletheia-codex-prod.appspot.com/temp \
  --collection-ids=reviewQueue \
  --project=aletheia-codex-prod
```

Or check in Firebase Console:
https://console.firebase.google.com/project/aletheia-codex-prod/firestore/data/reviewQueue

---

## Alternative: Use Firebase Functions

If Cloud Functions deployment fails, you can use Firebase Functions:

### 1. Update firebase.json

Add functions configuration:
```json
{
  "functions": [
    {
      "source": "functions/orchestration",
      "codebase": "orchestration",
      "runtime": "python311",
      "ignore": [
        "node_modules",
        ".git",
        "firebase-debug.log",
        "firebase-debug.*.log",
        "*.local"
      ]
    }
  ]
}
```

### 2. Deploy via Firebase CLI

```bash
cd /workspace/aletheia-codex
firebase deploy --only functions:orchestration --project aletheia-codex-prod
```

---

## Troubleshooting

### Issue: Function not triggering

**Check Firestore location**:
```bash
gcloud firestore databases describe --project=aletheia-codex-prod
```

**Ensure trigger location matches**:
- If Firestore is in `nam5`, use `--trigger-location=nam5`
- If Firestore is in `us-central1`, use `--trigger-location=us-central1`

### Issue: Permission errors

**Grant Firestore permissions**:
```bash
gcloud projects add-iam-policy-binding aletheia-codex-prod \
  --member="serviceAccount:679360092359-compute@developer.gserviceaccount.com" \
  --role="roles/datastore.user"
```

### Issue: Function timeout

**Increase timeout**:
```bash
gcloud functions deploy orchestration-function \
  --gen2 \
  --timeout=540s \
  --update-env-vars="GCP_PROJECT=aletheia-codex-prod" \
  --project=aletheia-codex-prod
```

---

## Expected Results After Fix

### Notes Page
- ✅ New notes process automatically
- ✅ Status changes from "processing" to "completed"
- ✅ Processing time displayed

### Review Page
- ✅ Stats show counts (not blank)
- ✅ Pending items appear in review queue
- ✅ Can approve/reject entities and relationships

### Dashboard
- ✅ Entities count increases
- ✅ Relationships count increases
- ✅ Recent notes show "completed" status

---

## Rollback Plan

If function deployment fails:

```bash
# Delete the function
gcloud functions delete orchestration-function \
  --gen2 \
  --region=us-central1 \
  --project=aletheia-codex-prod

# Redeploy Cloud Run service (if needed)
cd /workspace/aletheia-codex/functions/orchestration
gcloud run deploy orchestration-api \
  --source=. \
  --region=us-central1 \
  --platform=managed \
  --allow-unauthenticated \
  --project=aletheia-codex-prod
```

---

## Next Steps

1. **Deploy orchestration function** (use Option 1 command above)
2. **Verify deployment** (check function status)
3. **Test with new note** (create note and watch logs)
4. **Verify processing** (check note status changes)
5. **Check review queue** (verify entities/relationships created)

---

## Success Criteria

- ✅ Orchestration function deployed as Cloud Function (not Cloud Run)
- ✅ Function triggers automatically when note created
- ✅ Notes process from "processing" to "completed"
- ✅ Review queue populated with entities/relationships
- ✅ Stats display correctly on Review page