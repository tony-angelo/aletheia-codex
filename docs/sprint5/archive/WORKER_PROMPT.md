# Sprint 5 Worker Prompt: Note Processing Fix

**READ THIS FIRST**: This is your complete briefing for Sprint 5. Everything you need is in this file or referenced from it.

---

## Mission Statement

**Fix the broken note processing workflow end-to-end** so the application can be tested. This is a focused bug fix sprint - no new features, just make the core functionality work.

---

## Critical Context

### What's Broken
After Sprint 4.5, Google Sign-In works but note processing is completely broken:
- ❌ Notes submitted through UI don't appear in Firestore
- ❌ No processing happens
- ❌ No entities extracted
- ❌ Silent failures with no error messages

### What Success Looks Like
1. User submits a note through the UI
2. Note appears in Firestore `notes` collection
3. Orchestration function processes the note
4. AI extracts entities and relationships
5. Items appear in `review_queue` collection
6. User can approve items
7. Approved items appear in Neo4j graph

### Timeline
**3-5 days** - This is a focused debugging sprint

---

## Mandatory Reading Order

### 1st: Read This File (You're Here)
Get the mission, context, and completion criteria.

### 2nd: Read Worker Thread Guidelines
**Location**: `docs/WORKER_THREAD_GUIDELINES.md`

**Critical Rules**:
- Sprint is NOT complete until fully deployed and tested in production
- Request IAM roles/permissions when needed - don't ask user to do manual work
- Create PR only when 100% complete
- ONE completion report only

### 3rd: Read Implementation Guide
**Location**: `docs/sprint5/SPRINT5_IMPLEMENTATION_GUIDE.md`

**Contains**:
- Detailed investigation steps for each phase
- Code examples for logging and error handling
- Testing strategy
- Deployment instructions

### 4th: Reference Documentation (As Needed)
**Location**: `docs/sprint5/REFERENCE_DOCS.md`

**Contains**:
- Links to previous sprint documentation
- Architecture diagrams
- Database schemas
- API specifications

---

## Success Criteria (5 Checkboxes)

Sprint 5 is ONLY complete when ALL of these are true:

1. ✅ **Note Submission Works**
   - User can submit note through UI
   - Note appears in Firestore `notes` collection
   - No errors in browser console
   - Clear error messages if submission fails

2. ✅ **Function Triggers**
   - Orchestration function receives Firestore event
   - Function logs show entry and processing steps
   - Event data is accessible and parsed correctly

3. ✅ **AI Extraction Works**
   - Gemini API called successfully
   - Entities extracted from note content
   - Relationships identified between entities
   - Results are valid JSON with expected structure

4. ✅ **Review Queue Populated**
   - Items appear in `review_queue` collection
   - Items have correct structure (userId, noteId, type, data, status)
   - Items linked to source note
   - Batch writes complete successfully

5. ✅ **Approval Works End-to-End**
   - User can approve items in review queue
   - Approved items appear in Neo4j graph
   - Graph relationships created correctly
   - Complete workflow verified in production

---

## Implementation Phases

### Phase 1: Frontend → Firestore (Days 1-2)
**Goal**: Get notes writing to Firestore

**Key Tasks**:
1. Add comprehensive console logging to note submission
2. Test Firestore write directly from browser console
3. Verify auth token is present in requests
4. Check and fix Firestore security rules
5. Add error handling and user feedback

**Expected Issues**:
- Missing auth token in requests
- CORS errors
- Security rule violations
- Network errors

**Deliverable**: Notes successfully write to Firestore with clear error messages

### Phase 2: Firestore → Cloud Functions (Days 2-3)
**Goal**: Get orchestration function triggered

**Key Tasks**:
1. Check Cloud Function logs for trigger events
2. Verify Firestore trigger configuration
3. Add function entry logging
4. Test function with manual Firestore write
5. Verify event payload structure

**Expected Issues**:
- Function not being triggered
- Missing event data
- Auth verification failures
- Timeout errors

**Deliverable**: Function triggers on note creation with accessible event data

### Phase 3: Cloud Functions → AI Processing (Days 3-4)
**Goal**: Get AI extraction working

**Key Tasks**:
1. Add AI service logging
2. Verify Gemini API key
3. Test extraction with sample text
4. Add response validation
5. Add error recovery

**Expected Issues**:
- API key issues
- Rate limiting
- Prompt formatting errors
- Response parsing failures

**Deliverable**: AI successfully extracts entities and relationships

### Phase 4: Review Queue Creation (Day 4)
**Goal**: Get items into review queue

**Key Tasks**:
1. Add review queue write logging
2. Verify batch writes work
3. Check security rules
4. Test approval workflow
5. Verify Neo4j writes

**Expected Issues**:
- Batch write failures
- Security rule violations
- Transaction errors

**Deliverable**: Review items created and approval workflow works

### Phase 5: End-to-End Testing (Day 5)
**Goal**: Verify complete workflow

**Key Tasks**:
1. Write automated test script
2. Test happy path
3. Test error cases
4. Test edge cases
5. Document any remaining issues

**Deliverable**: All tests passing, complete workflow verified

---

## Key Technical Details

### Current Architecture
```
User (Browser)
  ↓ (Firebase Auth)
  ↓ (Firestore Write)
Firestore: notes collection
  ↓ (Firestore Trigger)
Cloud Function: orchestration-function
  ↓ (Gemini API Call)
AI Service: Entity Extraction
  ↓ (Firestore Write)
Firestore: review_queue collection
  ↓ (User Approval)
Cloud Function: review-queue-function
  ↓ (Neo4j Write)
Neo4j: Knowledge Graph
```

### Critical Files to Modify

**Frontend**:
- `web/src/components/NoteInput.tsx` - Add logging and error handling
- `web/src/services/api.ts` - Add auth headers
- `web/src/services/errorHandler.ts` - Create error handling service

**Backend**:
- `functions/orchestration/main.py` - Add comprehensive logging
- `shared/ai/gemini_service.py` - Add AI service logging
- `shared/services/review_queue_service.py` - Add review queue logging

**Configuration**:
- `firestore.rules` - Fix security rules if needed
- `functions/orchestration/requirements.txt` - Ensure all dependencies present

### Logging Strategy

**Every operation must log**:
1. **Entry**: "Starting [operation]"
2. **Parameters**: Log all input parameters
3. **Progress**: Log each major step
4. **Results**: Log output/results
5. **Errors**: Log full error details with stack trace

**Example**:
```python
logger.info("=" * 80)
logger.info("OPERATION STARTED")
logger.info("=" * 80)
logger.info(f"Parameter 1: {param1}")
logger.info(f"Parameter 2: {param2}")

try:
    # Do work
    result = do_something()
    logger.info(f"Result: {result}")
    
    logger.info("=" * 80)
    logger.info("OPERATION COMPLETE")
    logger.info("=" * 80)
except Exception as e:
    logger.error("=" * 80)
    logger.error("OPERATION FAILED")
    logger.error(f"Error: {str(e)}")
    logger.error("=" * 80)
    logger.exception("Full traceback:")
    raise
```

---

## Testing Requirements

### Manual Testing
Before marking any phase complete, you MUST:
1. Test in browser with console open
2. Submit a test note
3. Check Firestore for note document
4. Check Cloud Function logs
5. Check review queue for items
6. Approve an item
7. Check Neo4j for approved item

### Automated Testing
Create and run end-to-end test script:
```python
# tests/test_note_processing_e2e.py
def test_note_processing_end_to_end():
    # 1. Create test note
    # 2. Wait for processing
    # 3. Check note status
    # 4. Check review queue
    # 5. Verify entities
    # 6. Verify relationships
```

### Log Verification
```bash
# Check function logs
gcloud functions logs read orchestration-function \
  --project aletheia-codex-prod \
  --limit 100

# Follow logs in real-time
gcloud functions logs tail orchestration-function \
  --project aletheia-codex-prod
```

---

## Deployment

### Deploy Functions
```bash
# Deploy orchestration function
gcloud functions deploy orchestration-function \
  --gen2 \
  --runtime python311 \
  --region us-central1 \
  --source functions/orchestration \
  --entry-point orchestration_function \
  --trigger-event-filters="type=google.cloud.firestore.document.v1.created" \
  --trigger-event-filters="database=(default)" \
  --trigger-location=us-central1 \
  --service-account orchestration-sa@aletheia-codex-prod.iam.gserviceaccount.com \
  --set-env-vars GCP_PROJECT=aletheia-codex-prod \
  --memory 512MB \
  --timeout 540s
```

### Deploy Frontend
```bash
cd web
npm run build
firebase deploy --only hosting
```

---

## Handling Blockers

### If You Need IAM Permissions
**DO THIS**:
```
I need the following IAM role to proceed:
- Role: roles/datastore.indexAdmin
- Service Account: orchestration-sa@aletheia-codex-prod.iam.gserviceaccount.com
- Reason: To create Firestore indexes programmatically

Command to grant:
gcloud projects add-iam-policy-binding aletheia-codex-prod \
  --member="serviceAccount:orchestration-sa@aletheia-codex-prod.iam.gserviceaccount.com" \
  --role="roles/datastore.indexAdmin"

Please run this command and let me know when complete.
```

**DON'T DO THIS**:
```
Can you create the Firestore index manually? Here are the steps...
```

### If You Need API Keys
**DO THIS**:
```
I need a Gemini API key to proceed. Please:
1. Go to https://aistudio.google.com/app/apikey
2. Create a new API key
3. Add it to Secret Manager as 'gemini-api-key'
4. Let me know when complete
```

### If You Encounter Errors
**DO THIS**:
1. Log the full error with stack trace
2. Investigate the root cause
3. Implement a fix
4. Test the fix
5. Document the solution

**DON'T DO THIS**:
1. Mark the task as complete with errors
2. Ask user to debug
3. Skip error handling

---

## Completion Requirements

### Before Creating PR
- [ ] All 5 success criteria checkboxes are ✅
- [ ] All code changes committed
- [ ] All functions deployed to production
- [ ] Frontend deployed to production
- [ ] End-to-end test passing in production
- [ ] All logs verified
- [ ] No critical errors in production

### PR Requirements
- [ ] Clear title: "Sprint 5: Note Processing Fix"
- [ ] Description includes:
  - What was broken
  - What was fixed
  - How to test
  - Links to logs showing it works
- [ ] All files included
- [ ] No merge conflicts

### Completion Report Requirements
Create ONE completion report with:
1. **Summary**: What was accomplished
2. **Issues Found**: Root causes identified
3. **Solutions Implemented**: How each issue was fixed
4. **Testing Results**: Evidence that it works
5. **Deployment Status**: All deployments complete
6. **Next Steps**: Any follow-up needed

**DO NOT CREATE**:
- Multiple status reports
- Daily updates
- Progress reports
- Intermediate summaries

---

## Common Pitfalls to Avoid

### ❌ DON'T
1. Mark sprint complete without testing in production
2. Create PR before all deployments are done
3. Ask user to perform manual tasks
4. Skip logging and error handling
5. Assume something works without testing
6. Create 12+ status documents

### ✅ DO
1. Test every change in production
2. Add comprehensive logging everywhere
3. Request permissions when needed
4. Handle all errors gracefully
5. Verify with actual logs and data
6. Create ONE completion report

---

## Resources

### Documentation
- Implementation Guide: `docs/sprint5/SPRINT5_IMPLEMENTATION_GUIDE.md`
- Worker Guidelines: `docs/WORKER_THREAD_GUIDELINES.md`
- Reference Docs: `docs/sprint5/REFERENCE_DOCS.md`
- Architecture: `docs/architecture/02_Architecture_Overview.md`

### Tools
- [Firebase Console](https://console.firebase.google.com/project/aletheia-codex-prod)
- [Google Cloud Console](https://console.cloud.google.com/home/dashboard?project=aletheia-codex-prod)
- [Cloud Functions Logs](https://console.cloud.google.com/functions/list?project=aletheia-codex-prod)

### Commands
```bash
# View function logs
gcloud functions logs read orchestration-function --project aletheia-codex-prod --limit 100

# Deploy function
gcloud functions deploy orchestration-function --gen2 --runtime python311 --region us-central1 --source functions/orchestration --entry-point orchestration_function

# Deploy frontend
cd web && npm run build && firebase deploy --only hosting

# Run tests
pytest tests/test_note_processing_e2e.py -v
```

---

## Final Checklist Before Starting

- [ ] Read this entire file
- [ ] Read WORKER_THREAD_GUIDELINES.md
- [ ] Read SPRINT5_IMPLEMENTATION_GUIDE.md
- [ ] Understand the 5 success criteria
- [ ] Know how to handle blockers
- [ ] Ready to add comprehensive logging
- [ ] Ready to test in production
- [ ] Ready to create ONE completion report

---

## Questions?

If you're unclear about anything:
1. Check the Implementation Guide
2. Check the Reference Docs
3. Check previous sprint documentation
4. If still unclear, ask for clarification

**Remember**: This sprint is about fixing what's broken, not adding new features. Focus on making the core workflow work with comprehensive logging so we can debug any future issues.

---

**Good luck! Let's get note processing working! 🚀**