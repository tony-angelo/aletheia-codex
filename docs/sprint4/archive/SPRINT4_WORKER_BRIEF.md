# Sprint 4 Worker Thread Brief: Note Input & AI Processing

**Sprint**: Sprint 4 - Note Input & AI Processing  
**Duration**: 2-3 weeks (estimated)  
**Priority**: HIGH  
**Prerequisites**: Sprints 1-3 deployed and working

---

## ⚠️ CRITICAL: Read This First

**Before starting, read these documents in order**:
1. `docs/sprint3/WORKER_THREAD_GUIDELINES.md` - MANDATORY rules
2. `docs/sprint4/SPRINT4_IMPLEMENTATION_GUIDE.md` - Technical specs
3. `docs/sprint4/SPRINT4_WORKER_BRIEF.md` - This document

---

## 🎯 Mission Overview

Build the core user-facing feature: a note input system where users can enter text, have it processed by AI, and see the results. This connects the existing AI processing (Sprint 2) with the review queue (Sprint 3).

### The Problem We're Solving

Currently, the Sprint 3 UI only shows the Review Queue, but there's no way for users to:
- Input new notes
- Trigger AI processing
- See processing status
- Navigate to other parts of the app
- Manage their note history

### What We're Building

A complete note input and management system with:
1. **Navigation**: App-wide nav bar to switch between pages
2. **Note Input**: Chat-like interface for entering notes
3. **Processing**: Real-time status updates as AI processes notes
4. **History**: View and manage past notes
5. **Integration**: Connect to existing orchestration and review queue

---

## 📊 Current State of the Application

### ✅ What's Working (Sprints 1-3)

**Sprint 1: Neo4j Integration**
- Neo4j HTTP API connection working
- Can create nodes and relationships
- Security properly configured

**Sprint 2: AI Integration**
- Gemini 2.0 Flash extracting entities and relationships
- Orchestration function processing notes
- 85%+ accuracy on entities, 75%+ on relationships
- Cost: $0.0006 per document

**Sprint 3: Review Queue**
- Review Queue API deployed and working
- Web UI for reviewing extracted items
- Can approve/reject entities and relationships
- Real-time updates via Firestore

### ❌ What's Missing (Sprint 4 Scope)

**No Note Input**
- Users can't enter new notes
- No way to trigger AI processing
- No processing status visibility

**No Navigation**
- Only one page (Review Queue)
- Can't switch between features
- No app structure

**No Note Management**
- Can't see note history
- Can't track processing status
- Can't manage past notes

---

## 🏗️ Architecture Context

### How It All Fits Together

```
User Input (Sprint 4)
    ↓
Note Storage (Firestore)
    ↓
Orchestration Function (Sprint 2)
    ↓
AI Extraction (Gemini)
    ↓
Review Queue (Sprint 3)
    ↓
User Approval
    ↓
Knowledge Graph (Neo4j - Sprint 1)
```

### Data Flow

1. **User enters note** → Saved to Firestore `notes` collection
2. **Trigger processing** → Call orchestration function with note ID
3. **AI extracts entities** → Gemini processes note text
4. **Items added to review queue** → Firestore `review_queue` collection
5. **User reviews items** → Approve/reject via Sprint 3 UI
6. **Approved items** → Added to Neo4j knowledge graph

---

## 🎨 User Experience Goals

### Current Experience (Sprint 3 Only)
```
User opens app → See Review Queue → No way to add notes ❌
```

### Target Experience (After Sprint 4)
```
User opens app → See Notes page → Enter note → See processing → 
Navigate to Review Queue → Approve items → See in Knowledge Graph
```

### Key UX Principles

1. **Intuitive Navigation**: Clear nav bar, obvious page transitions
2. **Immediate Feedback**: Show processing status in real-time
3. **Clear Status**: User always knows what's happening
4. **Error Handling**: Helpful error messages, retry options
5. **Responsive Design**: Works on desktop and mobile

---

## 🔧 Technical Approach

### Frontend Architecture

**Current (Sprint 3)**:
```
App.tsx
  └── ReviewQueue component (entire app)
```

**Target (Sprint 4)**:
```
App.tsx (with React Router)
  ├── Navigation component
  └── Routes
      ├── /notes → NotesPage
      │   ├── NoteInput
      │   ├── ProcessingStatus
      │   └── NoteHistory
      ├── /review → ReviewPage (existing Sprint 3 UI)
      └── /graph → GraphPage (placeholder)
```

### Backend Architecture

**Existing**:
- `orchestration` function - Processes notes with AI
- `review_api` function - Manages review queue

**New**:
- `notes_api` function - Manages notes (CRUD operations)

**Updates**:
- `orchestration` function - Track note IDs, update status

---

## 📋 Detailed Requirements

### 1. Navigation System

**Requirements**:
- App-wide navigation bar at top
- Links to: Notes, Review, Graph (placeholder)
- User profile dropdown with sign out
- Active route highlighting
- Responsive (mobile menu)

**Technical**:
- Use React Router v6
- Persistent across page changes
- Accessible (keyboard navigation)

### 2. Note Input Interface

**Requirements**:
- Large textarea for note input (chat-like)
- Character count (max 10,000 chars)
- Submit button (disabled when empty)
- Clear button
- Loading state during submission
- Success/error feedback

**Technical**:
- Auto-resize textarea
- Debounced character count
- Form validation
- Error handling

### 3. Processing Status

**Requirements**:
- Show current processing step
- Progress bar (0-100%)
- Estimated time remaining
- Real-time updates
- Error display if processing fails

**Technical**:
- Firestore real-time listener
- Update every 500ms
- Timeout after 5 minutes
- Retry logic

### 4. Note History

**Requirements**:
- List of user's recent notes (last 50)
- Show: preview, status, timestamp, entity/rel count
- Click to expand full note
- Delete button
- Filter by status
- Sort by date

**Technical**:
- Firestore query with pagination
- Real-time updates
- Optimistic UI updates
- Confirmation before delete

### 5. Extraction Results

**Requirements**:
- Show extracted entities with confidence
- Show extracted relationships with confidence
- Link to review queue
- Expandable sections
- Color-coded by confidence

**Technical**:
- Query review_queue by note ID
- Group by type (entity/relationship)
- Sort by confidence
- Link to review page with filters

---

## 🎯 Success Metrics

### Functional Requirements
- ✅ User can enter and submit notes
- ✅ Processing starts within 2 seconds
- ✅ Status updates in real-time
- ✅ Extracted items appear in review queue
- ✅ User can navigate between pages
- ✅ User can view note history

### Performance Requirements
- Note submission: <500ms
- Processing start: <2s
- Status update latency: <200ms
- Page load: <2s
- Navigation: <100ms

### Quality Requirements
- Zero critical bugs in production
- >80% test coverage
- Responsive design (mobile + desktop)
- Accessible (WCAG 2.1 AA)
- Error rate <1%

---

## 🚨 Known Challenges

### Challenge 1: Real-time Status Updates

**Issue**: Need to show processing status in real-time as orchestration function runs

**Solution**: 
- Orchestration function updates Firestore `processing_status` collection
- Frontend listens to Firestore changes
- Update UI every time status changes

### Challenge 2: Linking Notes to Review Items

**Issue**: Need to connect notes to extracted items in review queue

**Solution**:
- Add `noteId` field to review queue items
- Orchestration function includes note ID when creating review items
- Frontend can query review items by note ID

### Challenge 3: Navigation State Management

**Issue**: Need to preserve state when navigating between pages

**Solution**:
- Use React Router for client-side routing
- Store critical state in Firestore (persists across sessions)
- Use URL parameters for filters/pagination

### Challenge 4: Error Handling

**Issue**: Many things can fail (API, network, processing, etc.)

**Solution**:
- Comprehensive error handling at every level
- User-friendly error messages
- Retry logic with exponential backoff
- Fallback UI states

---

## 📚 Reference Materials

### Existing Code to Study

**Sprint 2 - Orchestration Function**:
- `functions/orchestration/main.py` - How AI processing works
- Understand input/output format
- See how entities/relationships are extracted

**Sprint 3 - Review Queue**:
- `web/src/components/ReviewQueue.tsx` - UI patterns to follow
- `web/src/hooks/useReviewQueue.ts` - Firestore real-time updates
- `web/src/services/api.ts` - API client patterns

### External Resources

**React Router**:
- Docs: https://reactrouter.com/
- Tutorial: https://reactrouter.com/en/main/start/tutorial

**Firestore Real-time**:
- Docs: https://firebase.google.com/docs/firestore/query-data/listen
- Best practices: https://firebase.google.com/docs/firestore/best-practices

**Cloud Functions**:
- Docs: https://cloud.google.com/functions/docs
- Python runtime: https://cloud.google.com/functions/docs/concepts/python-runtime

---

## 🎯 Sprint 4 Phases Summary

### Week 1: Frontend Foundation
- Days 1-2: Navigation & routing
- Days 3-5: Note input interface
- Days 6-7: Note management UI

### Week 2: Backend & Integration
- Days 8-9: Firestore operations
- Days 10-11: Orchestration integration
- Days 12-13: Notes API
- Day 14: Integration testing

### Week 3: Deployment & Validation
- Days 15-16: Local testing
- Days 17-18: Production deployment
- Day 19: Production validation
- Day 20: Completion report

---

## ✅ Definition of Done

Sprint 4 is complete when:

1. **User can input notes** via chat-like interface
2. **Processing happens automatically** when note is submitted
3. **Status updates in real-time** as processing progresses
4. **Extracted items appear** in review queue
5. **Navigation works** between Notes, Review, and Graph pages
6. **Note history displays** user's past notes
7. **Everything is deployed** to production
8. **Everything is tested** in production
9. **Performance targets met** (all metrics)
10. **No critical errors** in production logs
11. **Completion report created** using template
12. **PR created** with all changes

---

## 🚀 Getting Started

### Step 1: Understand Current State
1. Review Sprint 3 UI (https://aletheia-codex-prod.web.app)
2. Understand what's missing (navigation, note input)
3. Review existing code structure

### Step 2: Plan Implementation
1. Read SPRINT4_IMPLEMENTATION_GUIDE.md
2. Create detailed todo.md
3. Confirm plan with user

### Step 3: Start Building
1. Begin with Phase 1 (Navigation)
2. Test each component as you build
3. Request permissions when needed
4. Commit regularly

---

## 💡 Tips for Success

1. **Start with Navigation**: Get routing working first, then build pages
2. **Test Incrementally**: Don't wait until the end to test
3. **Use Existing Patterns**: Follow Sprint 3 code style and patterns
4. **Real-time Updates**: Use Firestore listeners, not polling
5. **Error Handling**: Handle errors at every level
6. **Mobile First**: Design for mobile, enhance for desktop
7. **Request Permissions**: Don't ask user to do manual work
8. **Deploy Early**: Deploy to production as soon as possible
9. **Monitor Logs**: Check Cloud Functions logs frequently
10. **Document Everything**: Update completion report as you go

---

## 🎯 Your Mission

Transform the Sprint 3 Review Queue into a complete application with note input, processing, navigation, and history management. Make it easy and intuitive for users to add notes and see them processed by AI.

**Remember**: Sprint is only complete when deployed, tested, and working in production!

Good luck! 🚀

---

**END OF WORKER BRIEF**