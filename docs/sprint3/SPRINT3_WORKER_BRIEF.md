# Sprint 3 Worker Thread Brief

**Sprint**: Sprint 3 - Review Queue & User Interface  
**Duration**: 2-3 weeks (estimated)  
**Priority**: HIGH  
**Prerequisites**: Sprint 2 deployed and working

---

## ⚠️ CRITICAL: Read This First

**Before starting, read these documents in order**:
1. `docs/sprint3/WORKER_THREAD_GUIDELINES.md` - MANDATORY rules
2. `docs/sprint3/SPRINT3_IMPLEMENTATION_GUIDE.md` - Technical specs
3. `docs/sprint3/SPRINT3_WORKER_BRIEF.md` - This document

**Original instructions below**:

**Key points**:
- Sprint is NOT complete until fully deployed and tested in production
- Request permissions/resources when needed - don't ask user to do manual work
- Create PR only when 100% complete
- One completion report only - no excessive documentation

---

## Mission

Build a review queue and web interface that allows users to review, approve, and manage AI-extracted entities and relationships before they become permanent in the knowledge graph.

---

## What You're Building

User approval workflow with real-time web interface:

```
AI Extraction → Review Queue (Firestore) → User Review (Web UI) → Approval → Neo4j Graph
```

---

## Implementation Phases

### Phase 1: Review Queue Data Model (2 days)

**Create**:
- `shared/review/queue_manager.py` - Queue operations
- `shared/review/models.py` - Data models
- `shared/models/review_item.py` - Review item model

**Firestore Collections**:
```typescript
// review_queue collection
{
  id: string,
  user_id: string,
  type: 'entity' | 'relationship',
  status: 'pending' | 'approved' | 'rejected',
  confidence: number,
  source_document_id: string,
  created_at: timestamp,
  reviewed_at: timestamp | null,
  entity?: {...},
  relationship?: {...}
}

// user_stats collection
{
  user_id: string,
  total_pending: number,
  total_approved: number,
  total_rejected: number,
  last_review_at: timestamp
}
```

**If you need Firestore index permissions**:
```
Request: roles/datastore.indexAdmin
Reason: To create composite indexes for review queue queries
```

**Test**: Queue operations, user isolation, queries

---

### Phase 2: Approval Workflow (2 days)

**Create**:
- `shared/review/approval_workflow.py` - Approval/rejection logic
- `shared/review/batch_processor.py` - Batch operations

**Features**:
- Approve/reject entities → Create in Neo4j
- Approve/reject relationships → Create in Neo4j
- Batch operations (approve/reject multiple)
- Audit logging

**Test**: Single and batch approvals, Neo4j integration

---

### Phase 3: API Endpoints (1 day)

**Create**:
- `functions/review_api/main.py` - Cloud Functions API
- `functions/review_api/requirements.txt` - Dependencies

**Endpoints**:
- GET /review/pending
- POST /review/approve
- POST /review/reject
- POST /review/batch-approve
- POST /review/batch-reject
- GET /review/stats

**If you need Cloud Functions deployment permissions**:
```
Request: roles/cloudfunctions.admin
Reason: To deploy review API endpoints
```

**Test**: All endpoints, authentication, error handling

---

### Phase 4: Web Interface Setup (2 days)

**Create**:
- React app with TypeScript
- Firebase integration (Auth + Firestore)
- Tailwind CSS styling

**Setup**:
```bash
npx create-react-app web --template typescript
cd web
npm install firebase react-query @tanstack/react-query tailwindcss
npx tailwindcss init
```

**If you need Firebase Hosting permissions**:
```
Request: roles/firebase.admin
Reason: To deploy web interface to Firebase Hosting
```

**Test**: Firebase connection, authentication flow

---

### Phase 5: UI Components (3 days)

**Create**:
- `EntityCard.tsx` - Display entity for review
- `RelationshipCard.tsx` - Display relationship for review
- `ReviewQueue.tsx` - Main review interface
- `ConfidenceBadge.tsx` - Confidence score display
- `BatchActions.tsx` - Batch operation controls

**Features**:
- Display entities and relationships
- Confidence score visualization (green/yellow/red)
- Approve/reject buttons
- Batch selection checkboxes
- Responsive design (mobile-friendly)

**Test**: Component rendering, user interactions, responsive design

---

### Phase 6: Real-Time Updates (2 days)

**Create**:
- Firestore listeners for real-time updates
- Custom React hooks (`useReviewQueue`, `useApproval`)
- Optimistic UI updates

**Features**:
- Real-time item additions
- Real-time status updates
- Connection handling and reconnection

**Test**: Real-time updates, offline handling, reconnection

---

### Phase 7: Integration & Deployment (3 days)

**Tasks**:
1. Connect UI to API endpoints
2. Add error handling and loading states
3. Deploy Cloud Functions (review API)
4. Deploy to Firebase Hosting (web app)
5. End-to-end testing in production
6. Verify all functionality works

**Deployment Commands**:
```bash
# Deploy review API
cd functions/review_api
gcloud functions deploy review-api \
    --gen2 \
    --runtime=python311 \
    --region=us-central1 \
    --source=. \
    --entry-point=handle_request \
    --trigger-http \
    --allow-unauthenticated

# Deploy web app
cd web
npm run build
firebase deploy --only hosting
```

**Test**: Complete workflow, user acceptance, performance

---

## Technical Specifications

### Firestore Security Rules

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /review_queue/{itemId} {
      allow read, write: if request.auth != null 
        && request.auth.uid == resource.data.user_id;
    }
    
    match /user_stats/{userId} {
      allow read, write: if request.auth != null 
        && request.auth.uid == userId;
    }
  }
}
```

### Confidence Score Colors

- **Green** (≥0.8): High confidence
- **Yellow** (0.5-0.8): Medium confidence
- **Red** (<0.5): Low confidence

### API Authentication

- Firebase Authentication
- User token verification
- User isolation enforced

---

## Success Criteria

Sprint 3 is ONLY complete when:

```
✅ Review queue implemented in Firestore
✅ Approval workflow working with Neo4j
✅ API endpoints deployed to Cloud Functions
✅ API endpoints tested and working
✅ Web interface built and deployed to Firebase Hosting
✅ Web interface tested and working
✅ Real-time updates functional
✅ Batch operations working
✅ All tests passing (local AND production)
✅ End-to-end workflow verified in production
✅ No critical errors in production
✅ Documentation updated
✅ PR created with all changes
✅ User has confirmed completion
```

**DO NOT mark complete if any item is unchecked.**

---

## Documentation Requirements

### Required (ONLY)
1. **SPRINT3_COMPLETION_REPORT.md** - Final status with production results
2. Code comments and docstrings
3. Update PROJECT_STATUS.md to show Sprint 3 complete

### NOT Required
- ❌ Multiple intermediate summaries
- ❌ Progress reports during implementation
- ❌ Separate deployment reports
- ❌ Multiple status documents

---

## Performance Targets

- **API Response Time**: < 500ms
- **UI Render Time**: < 100ms
- **Real-Time Update Latency**: < 1s
- **Batch Operation**: < 2s per 10 items

---

## Handling Blockers

### If You Need Permissions

**DO THIS** ✅:
```
Use 'ask' tool:
"I need the [ROLE_NAME] role to [WHAT YOU'RE DOING].

Please run:
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:SERVICE_ACCOUNT" \
  --role="roles/[ROLE_NAME]"

This will allow me to:
1. [TASK 1]
2. [TASK 2]
3. Complete Sprint 3 deployment

Let me know when this is done."
```

**DO NOT DO THIS** ❌:
```
"Deployment requires [PERMISSION]. Please deploy manually.
Sprint 3 is complete except for deployment."
[Creates PR and marks complete]
```

### If You Need Resources

**Request them** - don't ask user to create manually.

Examples:
- Need API key → Request it
- Need database → Request permission to create it
- Need index → Request permission to create it

---

## Testing Approach

### Local Testing
1. Use provided GCP service account key
2. Test each component individually
3. Test integration between components
4. Test end-to-end workflow locally

### Production Testing
1. Deploy to Cloud Functions
2. Deploy to Firebase Hosting
3. Test with real user accounts
4. Verify end-to-end workflow
5. Check logs for errors
6. Validate performance metrics

**Both local AND production testing are required.**

---

## Key Files to Reference

### Sprint 3 Documentation
- `docs/sprint3/SPRINT3_IMPLEMENTATION_GUIDE.md` - Complete technical guide
- `docs/sprint3/README.md` - Sprint overview
- `WORKER_THREAD_GUIDELINES.md` - Critical instructions (READ THIS!)

### Sprint 2 Reference
- `shared/ai/ai_service.py` - AI integration
- `shared/db/graph_populator.py` - Neo4j population
- `shared/models/entity.py` - Entity model
- `shared/models/relationship.py` - Relationship model
- `functions/orchestration/main.py` - Current orchestration logic

### Project Documentation
- `docs/project/PROJECT_STATUS.md` - Current project status
- `docs/project/PROJECT_VISION.md` - Overall vision

---

## Important Notes

### Service Account Key
- User will provide key for testing
- Store securely, don't commit to git
- Use for local testing AND deployment
- Production uses Secret Manager

### Deployment
- You CAN deploy using the service account key
- DO NOT stop at "requires user action"
- Request permissions if you need them
- Complete deployment as part of the sprint

### Code Organization
- Follow existing patterns in `shared/` directory
- Use type hints consistently
- Add comprehensive error handling
- Include logging for debugging

---

## Completion Checklist

Before marking Sprint 3 complete:

```
□ All code implemented
□ All tests passing (local)
□ Review queue working in Firestore
□ Approval workflow working with Neo4j
□ API endpoints deployed to Cloud Functions
□ API endpoints tested in production
□ Web interface deployed to Firebase Hosting
□ Web interface tested in production
□ Real-time updates working
□ Batch operations working
□ End-to-end workflow verified
□ No critical errors in production
□ Performance targets met
□ SPRINT3_COMPLETION_REPORT.md created
□ PROJECT_STATUS.md updated
□ Code committed and pushed
□ PR created with all changes
□ User has confirmed completion
```

**If ANY checkbox is unchecked, Sprint 3 is NOT complete.**

---

## Questions?

Refer to:
1. `WORKER_THREAD_GUIDELINES.md` - Critical instructions
2. `SPRINT3_IMPLEMENTATION_GUIDE.md` - Technical details
3. Sprint 2 code for patterns and examples
4. Ask orchestrator for clarification using 'ask' tool

---

**Ready to Begin**: After Sprint 2 confirmed complete  
**Estimated Duration**: 2-3 weeks  
**Success Criteria**: All objectives met, deployed, tested, documented

---

**Remember**: Sprint is NOT complete until fully deployed and tested in production. Request permissions when needed. Create PR only when 100% done.

---

*End of Worker Thread Brief*