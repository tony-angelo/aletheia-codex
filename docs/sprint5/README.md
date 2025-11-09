# Sprint 5: Note Processing Fix

**Status**: Ready for Implementation  
**Duration**: 3-5 days  
**Objective**: Fix the broken note processing workflow end-to-end

---

## Quick Start

### For Worker Thread
1. **Read**: `WORKER_PROMPT.md` (start here - everything you need)
2. **Reference**: `SPRINT5_IMPLEMENTATION_GUIDE.md` (detailed technical specs)
3. **Lookup**: `REFERENCE_DOCS.md` (links to all other documentation)

### For Orchestrator/User
- **Worker Brief**: `WORKER_PROMPT.md` - Copy/paste this to worker thread
- **Implementation Guide**: `SPRINT5_IMPLEMENTATION_GUIDE.md` - Technical details
- **Reference Hub**: `REFERENCE_DOCS.md` - All documentation links

---

## What's This Sprint About?

After Sprint 4.5, Google Sign-In works but note processing is completely broken:
- ❌ Notes submitted through UI don't appear in Firestore
- ❌ No processing happens
- ❌ No entities extracted
- ❌ Silent failures with no error messages

**This sprint fixes all of that** by:
1. Adding comprehensive logging everywhere
2. Fixing auth token flow
3. Fixing Firestore writes
4. Fixing function triggers
5. Fixing AI extraction
6. Fixing review queue creation

---

## Success Criteria (5 Checkboxes)

Sprint 5 is complete when ALL of these work:

1. ✅ **Note Submission Works**
   - User submits note → appears in Firestore
   - Clear error messages if fails

2. ✅ **Function Triggers**
   - Orchestration function receives event
   - Logs show processing steps

3. ✅ **AI Extraction Works**
   - Gemini API extracts entities
   - Results are valid JSON

4. ✅ **Review Queue Populated**
   - Items appear in review_queue collection
   - Correct structure and links

5. ✅ **Approval Works**
   - User approves items
   - Items appear in Neo4j graph

---

## Implementation Phases

### Phase 1: Frontend → Firestore (Days 1-2)
**Goal**: Get notes writing to Firestore
- Add logging to note submission
- Verify auth token
- Fix security rules
- Add error handling

### Phase 2: Firestore → Cloud Functions (Days 2-3)
**Goal**: Get orchestration function triggered
- Check function logs
- Verify trigger configuration
- Add function logging
- Fix event parsing

### Phase 3: Cloud Functions → AI Processing (Days 3-4)
**Goal**: Get AI extraction working
- Add AI service logging
- Verify API key
- Test extraction
- Add error recovery

### Phase 4: Review Queue Creation (Day 4)
**Goal**: Get items into review queue
- Add review queue logging
- Verify batch writes
- Test approval workflow
- Verify Neo4j writes

### Phase 5: End-to-End Testing (Day 5)
**Goal**: Verify complete workflow
- Write automated tests
- Test happy path
- Test error cases
- Document results

---

## Key Files

### Documentation
- `WORKER_PROMPT.md` - Start here (single-file briefing)
- `SPRINT5_IMPLEMENTATION_GUIDE.md` - Detailed technical specs
- `REFERENCE_DOCS.md` - Links to all other docs

### Code to Modify
**Frontend**:
- `web/src/components/NoteInput.tsx`
- `web/src/services/api.ts`
- `web/src/services/errorHandler.ts` (create)

**Backend**:
- `functions/orchestration/main.py`
- `shared/ai/gemini_service.py`
- `shared/services/review_queue_service.py`

---

## Testing

### Manual Testing
1. Sign in with Google
2. Submit a test note
3. Check browser console
4. Check Firestore
5. Check function logs
6. Check review queue
7. Approve an item
8. Check Neo4j

### Automated Testing
```bash
pytest tests/test_note_processing_e2e.py -v
```

### Log Verification
```bash
gcloud functions logs read orchestration-function \
  --project aletheia-codex-prod \
  --limit 100
```

---

## Deployment

### Deploy Functions
```bash
# Orchestration function
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

## Common Issues

### "Permission Denied" on Note Submission
- Check user is authenticated
- Verify security rules
- Check userId matches auth.uid

### Function Not Triggering
- Verify trigger configuration
- Check trigger location
- Redeploy function

### AI Extraction Fails
- Verify API key
- Check API quota
- Test with simple text

### Review Items Not Created
- Check security rules
- Verify batch size < 500
- Add retry logic

---

## Resources

### Documentation
- [Worker Thread Guidelines](../WORKER_THREAD_GUIDELINES.md)
- [Architecture Overview](../architecture/02_Architecture_Overview.md)
- [Database Schemas](../architecture/05_Database_Schemas.md)

### Tools
- [Firebase Console](https://console.firebase.google.com/project/aletheia-codex-prod)
- [Google Cloud Console](https://console.cloud.google.com/home/dashboard?project=aletheia-codex-prod)
- [Cloud Functions Logs](https://console.cloud.google.com/functions/list?project=aletheia-codex-prod)

### External Docs
- [Firestore Security Rules](https://firebase.google.com/docs/firestore/security/get-started)
- [Cloud Functions Logging](https://cloud.google.com/functions/docs/monitoring/logging)
- [Gemini API](https://ai.google.dev/docs)

---

## Next Steps After Sprint 5

Once note processing is working:

**Sprint 6**: Functional UI Foundation
- All pages present with basic elements
- Component library organized
- Function library documented
- Ready for AI analysis

**Sprint 7**: UI Redesign
- Use design AI service
- Implement new design
- Polish and refine

---

## Questions?

- Check `WORKER_PROMPT.md` first
- Check `SPRINT5_IMPLEMENTATION_GUIDE.md` for technical details
- Check `REFERENCE_DOCS.md` for links to other docs
- Create GitHub issue if still unclear

---

**Let's get note processing working! 🚀**