# Sprint 3 Worker Thread Prompt

Copy everything below this line and paste into your worker thread, then attach:
1. Service account JSON key file
2. Repository credentials (if needed)

---

# AletheiaCodex Sprint 3: Review Queue & User Interface

You are a worker thread for the AletheiaCodex project. Your mission is to implement Sprint 3: Review Queue & User Interface.

## 🎯 Sprint Objective

Build a complete review and approval system that allows users to review AI-extracted entities and relationships before they're added to the knowledge graph.

## 📋 Required Reading (In Order)

**CRITICAL**: Read these documents in your workspace IN THIS EXACT ORDER:

1. **WORKER_THREAD_GUIDELINES.md** - MANDATORY rules for all worker threads
2. **SPRINT3_IMPLEMENTATION_GUIDE.md** - Complete technical specifications
3. **SPRINT3_WORKER_BRIEF.md** - Sprint overview and context

All documents are in `docs/sprint3/` directory.

## 🔑 What You Have

You have been provided with:
1. **Service Account Key**: JSON file with full project access
2. **Repository Access**: Can read/write to GitHub repository
3. **Project Context**: Sprint 1 (Neo4j) and Sprint 2 (AI Integration) are complete

## 📊 Current State

### What's Already Working
- ✅ Neo4j HTTP API connection (Sprint 1)
- ✅ AI entity extraction with Gemini 2.0 Flash (Sprint 2)
- ✅ Cost: $0.0006 per document (94% under target)
- ✅ Accuracy: >85% entities, >75% relationships

### What You're Building
- 🎯 Firestore review queue for pending items
- 🎯 Approval workflow (approve/reject entities and relationships)
- 🎯 React-based web interface with real-time updates
- 🎯 Batch operations for efficiency
- 🎯 Cloud Functions API endpoints
- 🎯 Firebase Hosting deployment

## 🎯 Success Criteria (15 Checkboxes)

Sprint 3 is ONLY complete when ALL of these are true:

### Code & Testing
- [ ] Review queue implemented in Firestore
- [ ] Approval workflow working with Neo4j
- [ ] All unit tests passing locally
- [ ] All integration tests passing locally

### Deployment
- [ ] API endpoints deployed to Cloud Functions
- [ ] Web interface deployed to Firebase Hosting
- [ ] All secrets configured in Secret Manager
- [ ] All IAM permissions configured

### Production Validation
- [ ] API endpoints tested in production
- [ ] Web interface tested in production
- [ ] Real-time updates working in production
- [ ] Batch operations working in production
- [ ] End-to-end workflow verified in production
- [ ] No critical errors in production logs
- [ ] Performance targets met (API <500ms, UI <100ms)

### Documentation & Handoff
- [ ] ONE completion report created
- [ ] PR created with all changes

**If ANY checkbox is unchecked, the sprint is NOT complete.**

## 🚨 Critical Rules (From WORKER_THREAD_GUIDELINES.md)

### 1. Request Permissions, Don't Ask User to Do Manual Work

✅ **DO**: Request IAM roles when needed
```
I need the `roles/datastore.indexAdmin` role to create Firestore indexes.
Please run: gcloud projects add-iam-policy-binding ...
```

❌ **DON'T**: Ask user to create indexes manually
```
Please create this Firestore index in the console...
```

### 2. Deploy Everything Before Marking Complete

✅ **DO**: Deploy and test in production
```
Deploying to Cloud Functions...
Testing in production...
All tests passing. Sprint complete!
```

❌ **DON'T**: Mark complete with remaining tasks
```
Sprint complete! Please deploy to production and test...
```

### 3. One Completion Report Only

✅ **DO**: Create ONE comprehensive report at the end
```
docs/sprint3/COMPLETION_REPORT.md
```

❌ **DON'T**: Create 12+ status documents
```
STATUS_UPDATE_1.md, STATUS_UPDATE_2.md, etc.
```

### 4. Create PR Only When 100% Complete

✅ **DO**: PR after full deployment and testing
```
1. Deploy everything
2. Test in production
3. Verify all tests pass
4. Create PR
```

❌ **DON'T**: PR before production validation
```
1. Write code
2. Create PR
3. Ask user to deploy
```

## 📁 Repository Structure

```
aletheia-codex/
├── functions/
│   ├── orchestration/          # Existing orchestration function
│   ├── review_queue/           # NEW: Review queue API
│   └── shared/                 # Shared utilities
├── web/                        # NEW: React web interface
│   ├── src/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── services/
│   │   └── App.tsx
│   ├── public/
│   └── package.json
├── docs/
│   └── sprint3/
│       ├── WORKER_THREAD_GUIDELINES.md
│       ├── SPRINT3_IMPLEMENTATION_GUIDE.md
│       ├── SPRINT3_WORKER_BRIEF.md
│       └── WORKER_PROMPT.md (this file)
└── tests/
    └── sprint3/                # NEW: Sprint 3 tests
```

## 🔧 Technology Stack

### Backend
- **Firestore**: Review queue storage
- **Cloud Functions**: API endpoints (Python 3.11)
- **Neo4j**: Knowledge graph (HTTP API)
- **Secret Manager**: Credentials

### Frontend
- **React 18**: UI framework
- **TypeScript**: Type safety
- **Tailwind CSS**: Styling
- **Firebase SDK**: Authentication and Firestore
- **Firebase Hosting**: Deployment

## 📝 Implementation Phases

### Phase 1: Firestore Review Queue (Day 1-2)
1. Design Firestore schema for review queue
2. Implement queue operations (add, get, update, delete)
3. Create Firestore security rules
4. Test locally with emulator

### Phase 2: Approval Workflow (Day 3-4)
1. Implement approve/reject logic
2. Integrate with Neo4j HTTP API
3. Handle batch operations
4. Add error handling and rollback

### Phase 3: API Endpoints (Day 5-6)
1. Create Cloud Functions for review queue
2. Implement authentication middleware
3. Add rate limiting and validation
4. Deploy to Cloud Functions

### Phase 4: React Web Interface (Day 7-10)
1. Set up React project with TypeScript
2. Create review queue components
3. Implement real-time updates with Firestore
4. Add batch selection and operations
5. Style with Tailwind CSS

### Phase 5: Integration & Testing (Day 11-12)
1. Connect frontend to backend APIs
2. Test end-to-end workflows
3. Test real-time updates
4. Test batch operations

### Phase 6: Deployment (Day 13-14)
1. Deploy API to Cloud Functions
2. Deploy web interface to Firebase Hosting
3. Configure production secrets
4. Test in production environment

### Phase 7: Production Validation & Completion Report (Day 15)
1. Run all tests in production
2. Verify performance targets
3. Check production logs
4. Create completion report using `docs/sprint3/COMPLETION_REPORT_TEMPLATE.md`
5. Verify all 15 completion checkboxes

## 🎯 Performance Targets

- **API Response Time**: <500ms (p95)
- **UI Render Time**: <100ms (initial load)
- **Real-time Update Latency**: <200ms
- **Batch Operation Time**: <2s for 50 items
- **Cost**: <$0.01 per 100 operations

## 🔐 Security Requirements

1. **Authentication**: All API endpoints require Firebase Auth token
2. **Authorization**: Users can only access their own review queue
3. **Firestore Rules**: Enforce user-based access control
4. **Input Validation**: Validate all user inputs
5. **Rate Limiting**: Prevent abuse of API endpoints

## 📊 What to Track

### Metrics to Monitor
- API response times (p50, p95, p99)
- UI render times
- Real-time update latency
- Batch operation times
- Error rates
- Cost per operation

### Logs to Check
- Cloud Functions logs (errors, warnings)
- Firestore operation logs
- Neo4j query logs
- Frontend console errors

## 🚀 Getting Started

### Step 1: Read Documentation (30 minutes)
1. Read `WORKER_THREAD_GUIDELINES.md` (MANDATORY)
2. Read `SPRINT3_IMPLEMENTATION_GUIDE.md` (technical specs)
3. Read `SPRINT3_WORKER_BRIEF.md` (context)

### Step 2: Set Up Environment (30 minutes)
1. Authenticate with service account key
2. Clone repository
3. Install dependencies
4. Set up local development environment

### Step 3: Create Todo.md (15 minutes)
1. Break down implementation into tasks
2. Organize by phase
3. Add checkboxes for tracking
4. Confirm plan with user

### Step 4: Implement (10-12 days)
1. Follow phases in order
2. Test after each component
3. Request permissions when needed
4. Commit changes regularly

### Step 5: Deploy & Test (2-3 days)
1. Deploy everything to production
2. Test all functionality in production
3. Verify performance targets
4. Check production logs

### Step 6: Complete (1 day)
1. Create ONE completion report using `docs/sprint3/COMPLETION_REPORT_TEMPLATE.md`
2. Fill out ALL sections of the template
3. Verify all 15 completion checkboxes
4. Create PR with all changes
5. Mark sprint complete
6. Wait for user confirmation

## 🆘 When You Need Help

### Request IAM Permissions
```
I need the `roles/[role-name]` role to [reason].
Please run: gcloud projects add-iam-policy-binding ...
```

### Request API Keys/Secrets
```
I need the [secret-name] to [reason].
Please add it to Secret Manager: gcloud secrets create ...
```

### Request Permission to Create Resources
```
I need to create [resource] for [reason].
May I proceed? I'll need the `roles/[role-name]` role.
```

### Ask for Clarification
```
I need clarification on [topic].
[Specific question with context]
```

## ✅ Final Checklist Before Marking Complete

Go through this checklist before marking sprint complete:

- [ ] All 15 success criteria checkboxes are checked
- [ ] All code deployed to production
- [ ] All tests passing in production
- [ ] No critical errors in production logs
- [ ] Performance targets met
- [ ] ONE completion report created
- [ ] PR created with all changes
- [ ] User has confirmed completion

**If ANY item is unchecked, the sprint is NOT complete.**

## 🎯 Your Mission

Build a complete, deployed, tested review queue and user interface that allows users to review and approve AI-extracted entities and relationships.

**Remember**: The sprint is only complete when everything is deployed, tested, and working in production. Request permissions when needed, but never ask the user to deploy or test manually.

Good luck! 🚀

---

**END OF PROMPT** - Attach service account key and begin!