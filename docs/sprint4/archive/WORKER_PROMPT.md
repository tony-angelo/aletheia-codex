# Sprint 4 Worker Thread Prompt

Copy everything below this line and paste into your worker thread, then attach:
1. Service account JSON key file
2. Repository credentials (if needed)

---

# AletheiaCodex Sprint 4: Note Input & AI Processing

You are a worker thread for the AletheiaCodex project. Your mission is to implement Sprint 4: Note Input & AI Processing.

## 🎯 Sprint Objective

Build a complete note input and processing system with navigation, allowing users to input notes via a chat-like interface, process them through AI, and navigate between different parts of the application.

## 📋 Required Reading (In Order)

**CRITICAL**: Read these documents in your workspace IN THIS EXACT ORDER:

1. **docs/sprint3/WORKER_THREAD_GUIDELINES.md** - MANDATORY rules for all worker threads
2. **docs/sprint4/SPRINT4_IMPLEMENTATION_GUIDE.md** - Complete technical specifications
3. **docs/sprint4/SPRINT4_WORKER_BRIEF.md** - Sprint overview and context

All documents are in the repository.

## 🔑 What You Have

You have been provided with:
1. **Service Account Key**: JSON file with full project access
2. **Repository Access**: Can read/write to GitHub repository
3. **Project Context**: Sprints 1-3 are complete and deployed

## 📊 Current State

### What's Already Working
- ✅ Neo4j HTTP API connection (Sprint 1)
- ✅ AI entity extraction with Gemini 2.0 Flash (Sprint 2)
- ✅ Review Queue API and UI (Sprint 3)
- ✅ Orchestration function for processing notes

### What You're Building
- 🎯 App-wide navigation system with routing
- 🎯 Note input interface (chat-like)
- 🎯 Note history and management
- 🎯 Real-time processing status
- 🎯 Integration with existing orchestration function
- 🎯 Backend API for note management

## 🎯 Success Criteria (15 Checkboxes)

Sprint 4 is ONLY complete when ALL of these are true:

### Code & Testing
- [ ] Navigation system implemented with routing
- [ ] Note input interface working
- [ ] Note history displaying correctly
- [ ] Processing status updates in real-time
- [ ] All unit tests passing locally
- [ ] Integration tests passing locally

### Deployment
- [ ] Backend updates deployed to Cloud Functions
- [ ] Frontend deployed to Firebase Hosting
- [ ] Firestore rules and indexes deployed
- [ ] All secrets configured

### Production Validation
- [ ] Can submit notes via UI in production
- [ ] Notes are processed by AI in production
- [ ] Extracted items appear in review queue
- [ ] Can navigate between pages in production
- [ ] Real-time updates working in production
- [ ] No critical errors in production logs

### Documentation
- [ ] ONE completion report created using template
- [ ] PR created with all changes

**If ANY checkbox is unchecked, the sprint is NOT complete.**

## 🚨 Critical Rules (From WORKER_THREAD_GUIDELINES.md)

### 1. Request Permissions, Don't Ask User to Do Manual Work

✅ **DO**: Request IAM roles when needed
```
I need the `roles/cloudfunctions.developer` role to deploy functions.
Please run: gcloud projects add-iam-policy-binding ...
```

❌ **DON'T**: Ask user to deploy manually
```
Please deploy the function using: gcloud functions deploy ...
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

✅ **DO**: Create ONE comprehensive report at the end using `docs/sprint3/COMPLETION_REPORT_TEMPLATE.md`

❌ **DON'T**: Create 12+ status documents

### 4. Create PR Only When 100% Complete

✅ **DO**: PR after full deployment and testing

❌ **DON'T**: PR before production validation

## 📁 Repository Structure

```
aletheia-codex/
├── functions/
│   ├── orchestration/          # Existing - UPDATE for note tracking
│   ├── review_api/             # Existing from Sprint 3
│   └── notes_api/              # NEW - Note management API
├── web/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navigation.tsx           # NEW
│   │   │   ├── NoteInput.tsx            # NEW
│   │   │   ├── NoteHistory.tsx          # NEW
│   │   │   ├── NoteCard.tsx             # NEW
│   │   │   ├── ProcessingStatus.tsx     # NEW
│   │   │   └── ExtractionResults.tsx    # NEW
│   │   ├── pages/
│   │   │   ├── NotesPage.tsx            # NEW
│   │   │   ├── ReviewPage.tsx           # NEW (move from App.tsx)
│   │   │   └── GraphPage.tsx            # NEW (placeholder)
│   │   ├── hooks/
│   │   │   ├── useNotes.ts              # NEW
│   │   │   └── useProcessing.ts         # NEW
│   │   ├── services/
│   │   │   ├── notes.ts                 # NEW
│   │   │   └── orchestration.ts         # NEW
│   │   └── App.tsx                      # UPDATE - Add routing
│   └── package.json                     # UPDATE - Add react-router-dom
└── docs/
    └── sprint4/
        ├── SPRINT4_IMPLEMENTATION_GUIDE.md
        ├── SPRINT4_WORKER_BRIEF.md
        ├── WORKER_PROMPT.md (this file)
        └── COMPLETION_REPORT.md (create at end)
```

## 🔧 Technology Stack

### Frontend
- **React 18**: UI framework
- **React Router**: Navigation and routing
- **TypeScript**: Type safety
- **Firebase SDK**: Firestore real-time updates
- **Existing**: Tailwind CSS or custom CSS

### Backend
- **Cloud Functions**: API endpoints (Python 3.11)
- **Firestore**: Note storage and real-time updates
- **Existing**: Orchestration function, Review API

## 📝 Implementation Phases

### Phase 1: Navigation & Routing (Days 1-2)
1. Install react-router-dom
2. Create Navigation component
3. Create page components (Notes, Review, Graph)
4. Update App.tsx with routing
5. Test navigation locally

### Phase 2: Note Input Interface (Days 3-5)
1. Create NoteInput component (chat-like textarea)
2. Create ProcessingStatus component (progress indicator)
3. Create ExtractionResults component (show extracted items)
4. Add form validation and error handling
5. Test locally

### Phase 3: Note Management (Days 6-8)
1. Create Firestore note operations (notes.ts service)
2. Create NoteHistory component (list of notes)
3. Create NoteCard component (individual note display)
4. Create useNotes hook (state management)
5. Test real-time updates locally

### Phase 4: Orchestration Integration (Days 9-11)
1. Create orchestration API client (orchestration.ts)
2. Create useProcessing hook (processing state)
3. Update orchestration function to track note IDs
4. Test processing flow locally
5. Verify extracted items appear in review queue

### Phase 5: Backend API (Days 12-13)
1. Create notes_api Cloud Function
2. Implement endpoints (POST /notes/process, GET /notes, DELETE /notes/{id})
3. Add authentication middleware
4. Update Firestore security rules
5. Test API locally

### Phase 6: Integration & Testing (Days 14-16)
1. Test end-to-end workflow locally
2. Test error scenarios
3. Test performance
4. Write unit tests
5. Write integration tests

### Phase 7: Deployment (Days 17-18)
1. Deploy orchestration function updates
2. Deploy notes_api function
3. Deploy Firestore rules and indexes
4. Build and deploy frontend
5. Test in production

### Phase 8: Production Validation (Day 19)
1. Test note submission in production
2. Test AI processing in production
3. Test navigation in production
4. Verify real-time updates work
5. Check production logs
6. Measure performance

### Phase 9: Completion Report (Day 20)
1. Use template: `docs/sprint3/COMPLETION_REPORT_TEMPLATE.md`
2. Fill ALL sections with production data
3. Verify all 15 checkboxes
4. Create PR
5. Mark sprint complete

## 🎯 Performance Targets

- **Note submission**: <500ms
- **Processing start**: <2s
- **Status update latency**: <200ms
- **Page load time**: <2s
- **Navigation transition**: <100ms

## 🔐 Security Requirements

1. **Authentication**: All API endpoints require Firebase Auth token
2. **Authorization**: Users can only access their own notes
3. **Input Validation**: Validate note content (max length, format)
4. **Rate Limiting**: Prevent abuse of processing endpoint
5. **Firestore Rules**: Enforce user-based access control

## 📊 What to Track

### Metrics to Monitor
- Note submission times
- Processing times
- Status update latency
- Page load times
- Navigation performance
- Error rates

### Logs to Check
- Cloud Functions logs (orchestration, notes_api)
- Firestore operation logs
- Frontend console errors
- Processing errors

## 🚀 Getting Started

### Step 1: Read Documentation (30 minutes)
1. Read `docs/sprint3/WORKER_THREAD_GUIDELINES.md` (MANDATORY)
2. Read `docs/sprint4/SPRINT4_IMPLEMENTATION_GUIDE.md` (technical specs)
3. Read `docs/sprint4/SPRINT4_WORKER_BRIEF.md` (context)

### Step 2: Set Up Environment (30 minutes)
1. Authenticate with service account key
2. Pull latest code from repository
3. Install dependencies (npm install in web/)
4. Set up local development environment

### Step 3: Create Todo.md (15 minutes)
1. Break down implementation into tasks
2. Organize by phase
3. Add checkboxes for tracking
4. Confirm plan with user

### Step 4: Implement (15-18 days)
1. Follow phases in order
2. Test after each component
3. Request permissions when needed
4. Commit changes regularly

### Step 5: Deploy & Test (2 days)
1. Deploy everything to production
2. Test all functionality in production
3. Verify performance targets
4. Check production logs

### Step 6: Complete (1 day)
1. Create ONE completion report using template
2. Fill out ALL sections
3. Verify all 15 checkboxes
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
- [ ] ONE completion report created using template
- [ ] PR created with all changes
- [ ] User has confirmed completion

**If ANY item is unchecked, the sprint is NOT complete.**

## 🎯 Your Mission

Build a complete note input and processing system with navigation that allows users to:
1. Enter notes via a chat-like interface
2. See processing status in real-time
3. Navigate between Notes, Review Queue, and Knowledge Graph
4. Manage their note history
5. See extracted items in the review queue

**Remember**: The sprint is only complete when everything is deployed, tested, and working in production. Request permissions when needed, but never ask the user to deploy or test manually.

Good luck! 🚀

---

**END OF PROMPT** - Attach service account key and begin!