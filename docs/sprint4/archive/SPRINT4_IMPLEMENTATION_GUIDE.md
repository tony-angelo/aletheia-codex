# Sprint 4 Implementation Guide: Note Input & AI Processing

**Sprint**: Sprint 4 - Note Input & AI Processing  
**Duration**: 2-3 weeks  
**Priority**: HIGH  
**Prerequisites**: Sprint 2 (AI Integration) and Sprint 3 (Review Queue) complete

---

## 🎯 Sprint Objectives

Build a complete note input and processing system that allows users to:
1. Input notes via a chat-like interface
2. Process notes through AI extraction pipeline
3. View extraction results in real-time
4. Navigate between note input and review queue
5. Manage their note history

---

## 📋 What We're Building

### Core Features
1. **Note Input Interface**
   - Chat-like UI for entering notes
   - Support for text input
   - Real-time processing feedback
   - Processing status indicators

2. **AI Processing Pipeline**
   - Trigger orchestration function with note text
   - Monitor processing status
   - Handle errors gracefully
   - Display extraction results

3. **Navigation System**
   - App-wide navigation bar
   - Route between pages (Notes, Review Queue, Knowledge Graph)
   - User profile menu
   - Responsive design

4. **Note Management**
   - View note history
   - See processing status
   - View extracted entities/relationships
   - Delete notes

---

## 🏗️ Architecture Overview

### Frontend Components
```
web/
├── src/
│   ├── components/
│   │   ├── Navigation.tsx          # NEW - App navigation bar
│   │   ├── NoteInput.tsx           # NEW - Chat-like note input
│   │   ├── NoteHistory.tsx         # NEW - List of user's notes
│   │   ├── NoteCard.tsx            # NEW - Individual note display
│   │   ├── ProcessingStatus.tsx    # NEW - Processing indicator
│   │   └── ExtractionResults.tsx   # NEW - Show extracted items
│   ├── pages/
│   │   ├── NotesPage.tsx           # NEW - Main notes page
│   │   ├── ReviewPage.tsx          # MOVE - Review queue (from App.tsx)
│   │   └── GraphPage.tsx           # NEW - Knowledge graph view (placeholder)
│   ├── hooks/
│   │   ├── useNotes.ts             # NEW - Note management
│   │   └── useProcessing.ts        # NEW - Processing status
│   ├── services/
│   │   └── orchestration.ts        # NEW - Orchestration API client
│   └── App.tsx                     # UPDATE - Add routing
```

### Backend Integration
- Use existing `orchestration` Cloud Function
- Add note storage in Firestore
- Track processing status
- Link notes to review queue items

---

## 📊 Data Models

### Firestore Collections

#### `notes` Collection
```typescript
interface Note {
  id: string;
  userId: string;
  content: string;
  createdAt: Timestamp;
  updatedAt: Timestamp;
  status: 'processing' | 'completed' | 'failed';
  processingStartedAt?: Timestamp;
  processingCompletedAt?: Timestamp;
  error?: string;
  extractionSummary?: {
    entityCount: number;
    relationshipCount: number;
  };
  metadata: {
    source: 'web' | 'api';
    ipAddress?: string;
    userAgent?: string;
  };
}
```

#### `processing_status` Collection
```typescript
interface ProcessingStatus {
  id: string;  // Same as note ID
  userId: string;
  noteId: string;
  status: 'queued' | 'extracting' | 'reviewing' | 'completed' | 'failed';
  currentStep: string;
  progress: number;  // 0-100
  startedAt: Timestamp;
  completedAt?: Timestamp;
  error?: string;
  steps: {
    extraction: { status: string; completedAt?: Timestamp };
    review: { status: string; completedAt?: Timestamp };
    graphUpdate: { status: string; completedAt?: Timestamp };
  };
}
```

---

## 🎨 UI/UX Design

### Navigation Bar
```
┌─────────────────────────────────────────────────────────────┐
│ AletheiaCodex    [Notes] [Review] [Graph]    👤 User ▼     │
└─────────────────────────────────────────────────────────────┘
```

### Notes Page Layout
```
┌─────────────────────────────────────────────────────────────┐
│                        Notes Page                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Note Input (Chat-like)                            │    │
│  │  ┌──────────────────────────────────────────────┐  │    │
│  │  │ Type your note here...                       │  │    │
│  │  │                                              │  │    │
│  │  │                                              │  │    │
│  │  └──────────────────────────────────────────────┘  │    │
│  │                                    [Submit] [Clear] │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Recent Notes                                      │    │
│  │  ┌──────────────────────────────────────────────┐  │    │
│  │  │ 📝 Note from 2 hours ago                     │  │    │
│  │  │ Status: ✅ Completed (3 entities, 2 rels)    │  │    │
│  │  │ "Today I met John at the coffee shop..."     │  │    │
│  │  └──────────────────────────────────────────────┘  │    │
│  │  ┌──────────────────────────────────────────────┐  │    │
│  │  │ 📝 Note from yesterday                       │  │    │
│  │  │ Status: ⏳ Processing...                     │  │    │
│  │  │ "Learned about React hooks today..."         │  │    │
│  │  └──────────────────────────────────────────────┘  │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 Implementation Phases

### Phase 1: Navigation & Routing (Days 1-2)

#### 1.1 Install React Router
```bash
cd web
npm install react-router-dom @types/react-router-dom
```

#### 1.2 Create Navigation Component
**File**: `web/src/components/Navigation.tsx`

Features:
- App logo and title
- Navigation links (Notes, Review, Graph)
- User profile dropdown
- Sign out button
- Active route highlighting
- Responsive design

#### 1.3 Create Page Components
**Files**:
- `web/src/pages/NotesPage.tsx` - Main notes page
- `web/src/pages/ReviewPage.tsx` - Move review queue here
- `web/src/pages/GraphPage.tsx` - Placeholder for future

#### 1.4 Update App.tsx with Routing
```typescript
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Navigation from './components/Navigation';
import NotesPage from './pages/NotesPage';
import ReviewPage from './pages/ReviewPage';
import GraphPage from './pages/GraphPage';

function App() {
  return (
    <BrowserRouter>
      <Navigation />
      <Routes>
        <Route path="/" element={<Navigate to="/notes" />} />
        <Route path="/notes" element={<NotesPage />} />
        <Route path="/review" element={<ReviewPage />} />
        <Route path="/graph" element={<GraphPage />} />
      </Routes>
    </BrowserRouter>
  );
}
```

---

### Phase 2: Note Input Interface (Days 3-5)

#### 2.1 Create Note Input Component
**File**: `web/src/components/NoteInput.tsx`

Features:
- Large textarea for note input
- Character count
- Submit button
- Clear button
- Loading state during processing
- Error handling
- Success feedback

#### 2.2 Create Processing Status Component
**File**: `web/src/components/ProcessingStatus.tsx`

Features:
- Progress bar
- Current step indicator
- Estimated time remaining
- Cancel button (optional)
- Error display

#### 2.3 Create Extraction Results Component
**File**: `web/src/components/ExtractionResults.tsx`

Features:
- Display extracted entities
- Display extracted relationships
- Confidence scores
- Link to review queue
- Expandable/collapsible sections

---

### Phase 3: Note Management (Days 6-8)

#### 3.1 Create Firestore Note Operations
**File**: `web/src/services/notes.ts`

Functions:
```typescript
// Create new note
async function createNote(userId: string, content: string): Promise<Note>

// Get user's notes
async function getUserNotes(userId: string, limit?: number): Promise<Note[]>

// Get single note
async function getNote(noteId: string): Promise<Note>

// Update note status
async function updateNoteStatus(noteId: string, status: NoteStatus): Promise<void>

// Delete note
async function deleteNote(noteId: string): Promise<void>

// Listen to note updates
function subscribeToNote(noteId: string, callback: (note: Note) => void): Unsubscribe
```

#### 3.2 Create Note History Component
**File**: `web/src/components/NoteHistory.tsx`

Features:
- List of user's recent notes
- Pagination or infinite scroll
- Filter by status
- Sort by date
- Search functionality
- Click to expand/view details

#### 3.3 Create Note Card Component
**File**: `web/src/components/NoteCard.tsx`

Features:
- Note preview (first 100 chars)
- Status badge
- Timestamp
- Entity/relationship count
- Expand to see full note
- Delete button
- Link to review queue items

---

### Phase 4: Orchestration Integration (Days 9-11)

#### 4.1 Create Orchestration API Client
**File**: `web/src/services/orchestration.ts`

Functions:
```typescript
// Trigger note processing
async function processNote(noteId: string, content: string): Promise<ProcessingStatus>

// Get processing status
async function getProcessingStatus(noteId: string): Promise<ProcessingStatus>

// Cancel processing (if supported)
async function cancelProcessing(noteId: string): Promise<void>
```

#### 4.2 Create Processing Hook
**File**: `web/src/hooks/useProcessing.ts`

Features:
- Submit note for processing
- Track processing status
- Real-time status updates
- Error handling
- Retry logic

#### 4.3 Create Notes Hook
**File**: `web/src/hooks/useNotes.ts`

Features:
- Load user's notes
- Create new note
- Delete note
- Real-time updates
- Pagination
- Filtering

---

### Phase 5: Backend Updates (Days 12-13)

#### 5.1 Update Orchestration Function
**File**: `functions/orchestration/main.py`

Changes:
- Accept note ID parameter
- Update processing status in Firestore
- Link extracted items to note ID
- Add error handling for status updates

#### 5.2 Create Note Processing Endpoint
**File**: `functions/notes_api/main.py` (NEW)

Endpoints:
```python
POST /notes/process
  - Create note in Firestore
  - Trigger orchestration function
  - Return note ID and initial status

GET /notes/{noteId}/status
  - Get current processing status
  - Return progress and current step

GET /notes
  - Get user's notes
  - Support filtering and pagination

DELETE /notes/{noteId}
  - Delete note and associated data
  - Clean up review queue items
```

#### 5.3 Update Firestore Security Rules
**File**: `firestore.rules`

Add rules for:
- `notes` collection (user can only access their own)
- `processing_status` collection (user can only access their own)

---

### Phase 6: Integration & Testing (Days 14-16)

#### 6.1 End-to-End Workflow Testing
Test complete flow:
1. User enters note
2. Note is saved to Firestore
3. Orchestration function is triggered
4. Processing status updates in real-time
5. Extracted items appear in review queue
6. User can navigate to review queue
7. User can approve/reject items
8. Items are added to knowledge graph

#### 6.2 Error Handling Testing
Test error scenarios:
- Network failures
- API errors
- Invalid input
- Processing timeouts
- Authentication errors

#### 6.3 Performance Testing
Measure:
- Note submission time
- Processing time
- UI responsiveness
- Real-time update latency

---

### Phase 7: Deployment (Days 17-18)

#### 7.1 Deploy Backend Updates
```bash
# Deploy orchestration function updates
cd functions/orchestration
gcloud functions deploy orchestration-function --gen2 ...

# Deploy new notes API
cd functions/notes_api
gcloud functions deploy notes-api --gen2 ...
```

#### 7.2 Deploy Firestore Updates
```bash
# Deploy security rules
firebase deploy --only firestore:rules

# Deploy indexes
firebase deploy --only firestore:indexes
```

#### 7.3 Deploy Frontend
```bash
cd web
npm run build
firebase deploy --only hosting
```

#### 7.4 Production Testing
- Test all features in production
- Verify real-time updates work
- Check performance metrics
- Review production logs

---

## 🎯 Success Criteria

Sprint 4 is complete when:

### Code & Testing
- [ ] Navigation system implemented with routing
- [ ] Note input interface working
- [ ] Note history displaying correctly
- [ ] Processing status updates in real-time
- [ ] All unit tests passing
- [ ] Integration tests passing

### Deployment
- [ ] Backend updates deployed to Cloud Functions
- [ ] Frontend deployed to Firebase Hosting
- [ ] Firestore rules and indexes deployed
- [ ] All secrets configured

### Production Validation
- [ ] Can submit notes via UI
- [ ] Notes are processed by AI
- [ ] Extracted items appear in review queue
- [ ] Can navigate between pages
- [ ] Real-time updates working
- [ ] No critical errors in logs
- [ ] Performance targets met

### User Experience
- [ ] Intuitive navigation
- [ ] Clear processing feedback
- [ ] Responsive design
- [ ] Error messages are helpful
- [ ] Loading states are clear

---

## 📊 Performance Targets

| Metric | Target |
|--------|--------|
| Note submission | <500ms |
| Processing start | <2s |
| Status update latency | <200ms |
| Page load time | <2s |
| Navigation transition | <100ms |

---

## 🔐 Security Requirements

1. **Authentication**: All API endpoints require Firebase Auth token
2. **Authorization**: Users can only access their own notes
3. **Input Validation**: Validate note content (length, format)
4. **Rate Limiting**: Prevent abuse of processing endpoint
5. **Data Privacy**: Notes are private to user

---

## 🎨 Design Guidelines

### Color Scheme
- Primary: Blue (#3B82F6)
- Success: Green (#10B981)
- Warning: Yellow (#F59E0B)
- Error: Red (#EF4444)
- Background: White (#FFFFFF)
- Text: Dark Gray (#1F2937)

### Typography
- Headings: Inter, sans-serif
- Body: Inter, sans-serif
- Code: Fira Code, monospace

### Spacing
- Use 4px base unit
- Consistent padding/margins
- Responsive breakpoints

---

## 📝 Testing Requirements

### Unit Tests
- Test all React components
- Test all hooks
- Test all service functions
- Aim for >80% coverage

### Integration Tests
- Test note submission flow
- Test processing status updates
- Test navigation
- Test error handling

### E2E Tests
- Test complete user workflow
- Test across different browsers
- Test responsive design

---

## 🚀 Deployment Checklist

Before deploying:
- [ ] All tests passing
- [ ] Code reviewed
- [ ] Documentation updated
- [ ] Environment variables configured
- [ ] Secrets in Secret Manager
- [ ] Firestore rules tested
- [ ] Performance validated
- [ ] Security reviewed

---

## 📚 Reference Materials

### React Router
- Docs: https://reactrouter.com/
- Tutorial: https://reactrouter.com/en/main/start/tutorial

### Firestore Real-time Updates
- Docs: https://firebase.google.com/docs/firestore/query-data/listen
- Best practices: https://firebase.google.com/docs/firestore/best-practices

### Cloud Functions
- Docs: https://cloud.google.com/functions/docs
- Triggers: https://cloud.google.com/functions/docs/calling

---

## 🎯 Sprint 4 Deliverables

1. **Navigation System**: App-wide navigation with routing
2. **Note Input Interface**: Chat-like UI for entering notes
3. **Note Management**: View and manage note history
4. **Processing Pipeline**: Real-time processing status
5. **Backend Integration**: Updated orchestration and new notes API
6. **Production Deployment**: All components deployed and tested

---

**END OF IMPLEMENTATION GUIDE**