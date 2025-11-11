# Sprint 3 Implementation Guide - Review Queue & User Interface

**Sprint**: Sprint 3  
**Duration**: 2-3 weeks (estimated)  
**Focus**: User interaction, approval workflow, and basic web interface  
**Prerequisites**: Sprint 2 complete (AI integration deployed)

---

## Overview

Sprint 3 implements the review queue and user interface that allows users to review, approve, and manage extracted entities and relationships before they become permanent in the knowledge graph. This sprint bridges the gap between automated AI extraction and user-validated knowledge.

---

## Objectives

### Primary Goals
1. Implement review queue in Firestore
2. Build confidence scoring system
3. Create user approval workflow
4. Develop basic web interface
5. Implement real-time updates
6. Add batch approval capabilities

### Success Criteria
- ✅ Review queue functional with pending items
- ✅ Confidence scores displayed accurately
- ✅ Users can approve/reject entities and relationships
- ✅ Web interface responsive and intuitive
- ✅ Real-time updates working
- ✅ Batch operations efficient

---

## Architecture

### Component Overview

```
Document Processing
    ↓
AI Extraction (Sprint 2)
    ↓
Review Queue (Firestore) ← Sprint 3
    ↓
User Review (Web UI) ← Sprint 3
    ↓
Approval/Rejection
    ↓
Neo4j Graph (Approved Items)
```

### Key Components

1. **Review Queue** (`shared/review/`)
   - Firestore collection for pending items
   - Confidence-based prioritization
   - Status tracking (pending, approved, rejected)
   - User isolation

2. **Approval Workflow** (`shared/review/approval_workflow.py`)
   - Approve/reject entities
   - Approve/reject relationships
   - Batch operations
   - Audit logging

3. **Web Interface** (`web/`)
   - React-based UI
   - Real-time updates via Firestore listeners
   - Entity/relationship cards
   - Confidence visualization
   - Batch selection

4. **API Endpoints** (`functions/api/`)
   - Get pending items
   - Approve/reject items
   - Get user statistics
   - Batch operations

---

## Implementation Phases

### Phase 1: Review Queue Data Model (Week 1, Days 1-2)

**Objective**: Design and implement Firestore review queue structure

**Firestore Collections**:

```typescript
// Collection: review_queue
{
  id: string,                    // Auto-generated
  user_id: string,               // User who owns this item
  type: 'entity' | 'relationship', // Item type
  status: 'pending' | 'approved' | 'rejected',
  confidence: number,            // 0.0 to 1.0
  source_document_id: string,    // Original document
  created_at: timestamp,
  reviewed_at: timestamp | null,
  
  // For entities
  entity?: {
    name: string,
    type: string,                // Person, Place, Organization, etc.
    properties: object,
    extracted_text: string       // Context from document
  },
  
  // For relationships
  relationship?: {
    source_entity: string,
    target_entity: string,
    type: string,                // KNOWS, WORKS_AT, etc.
    properties: object,
    extracted_text: string
  }
}

// Collection: user_stats
{
  user_id: string,
  total_pending: number,
  total_approved: number,
  total_rejected: number,
  last_review_at: timestamp,
  average_confidence: number
}
```

**Files to Create**:
- `shared/review/queue_manager.py` - Queue operations
- `shared/review/models.py` - Data models
- `shared/models/review_item.py` - Review item model

**Key Functions**:
```python
class QueueManager:
    def add_to_queue(user_id, items, source_doc_id)
    def get_pending_items(user_id, limit=50, min_confidence=0.0)
    def get_item_by_id(item_id)
    def update_item_status(item_id, status, user_id)
    def get_user_stats(user_id)
    def delete_item(item_id)
```

**Testing**:
- Test item creation
- Test retrieval with filters
- Test status updates
- Test user isolation
- Test batch operations

---

### Phase 2: Approval Workflow (Week 1, Days 3-4)

**Objective**: Implement approval/rejection logic with Neo4j integration

**Files to Create**:
- `shared/review/approval_workflow.py` - Main workflow logic
- `shared/review/batch_processor.py` - Batch operations

**Approval Workflow**:
```python
class ApprovalWorkflow:
    def approve_entity(item_id, user_id):
        """
        1. Get item from review queue
        2. Verify user ownership
        3. Create entity in Neo4j
        4. Update item status to 'approved'
        5. Update user stats
        6. Return success
        """
    
    def reject_entity(item_id, user_id, reason=None):
        """
        1. Get item from review queue
        2. Verify user ownership
        3. Update item status to 'rejected'
        4. Log rejection reason
        5. Update user stats
        6. Return success
        """
    
    def approve_relationship(item_id, user_id):
        """
        1. Get item from review queue
        2. Verify user ownership
        3. Verify both entities exist in Neo4j
        4. Create relationship in Neo4j
        5. Update item status to 'approved'
        6. Update user stats
        7. Return success
        """
    
    def batch_approve(item_ids, user_id):
        """
        Approve multiple items in a single operation
        """
    
    def batch_reject(item_ids, user_id, reason=None):
        """
        Reject multiple items in a single operation
        """
```

**Neo4j Integration**:
- Reuse `graph_populator.py` from Sprint 2
- Add approval metadata to nodes/relationships
- Track approval timestamp and user

**Testing**:
- Test single approval/rejection
- Test batch operations
- Test Neo4j integration
- Test error handling
- Test user isolation

---

### Phase 3: API Endpoints (Week 1, Day 5)

**Objective**: Create Cloud Functions for review queue operations

**Files to Create**:
- `functions/review_api/main.py` - API endpoints
- `functions/review_api/requirements.txt` - Dependencies

**Endpoints**:

```python
# GET /review/pending
def get_pending_items(request):
    """
    Get pending review items for user
    Query params: limit, min_confidence, type
    """

# POST /review/approve
def approve_item(request):
    """
    Approve a single item
    Body: {item_id: string}
    """

# POST /review/reject
def reject_item(request):
    """
    Reject a single item
    Body: {item_id: string, reason: string}
    """

# POST /review/batch-approve
def batch_approve_items(request):
    """
    Approve multiple items
    Body: {item_ids: string[]}
    """

# POST /review/batch-reject
def batch_reject_items(request):
    """
    Reject multiple items
    Body: {item_ids: string[], reason: string}
    """

# GET /review/stats
def get_user_stats(request):
    """
    Get user review statistics
    """
```

**Authentication**:
- Use Firebase Authentication
- Verify user tokens
- Enforce user isolation

**Testing**:
- Test each endpoint
- Test authentication
- Test error handling
- Test rate limiting

---

### Phase 4: Web Interface - Setup (Week 2, Days 1-2)

**Objective**: Set up React application with Firebase integration

**Technology Stack**:
- React 18
- TypeScript
- Firebase SDK (Auth, Firestore)
- Tailwind CSS
- React Query (data fetching)

**Project Structure**:
```
web/
├── public/
├── src/
│   ├── components/
│   │   ├── ReviewQueue.tsx
│   │   ├── EntityCard.tsx
│   │   ├── RelationshipCard.tsx
│   │   ├── ConfidenceBadge.tsx
│   │   └── BatchActions.tsx
│   ├── hooks/
│   │   ├── useReviewQueue.ts
│   │   ├── useApproval.ts
│   │   └── useAuth.ts
│   ├── services/
│   │   ├── firebase.ts
│   │   └── api.ts
│   ├── types/
│   │   └── review.ts
│   ├── App.tsx
│   └── index.tsx
├── package.json
└── tsconfig.json
```

**Setup Steps**:
```bash
# 1. Create React app
npx create-react-app web --template typescript

# 2. Install dependencies
cd web
npm install firebase react-query @tanstack/react-query tailwindcss

# 3. Configure Firebase
# Add Firebase config to src/services/firebase.ts

# 4. Configure Tailwind
npx tailwindcss init
```

**Testing**:
- Test Firebase connection
- Test authentication flow
- Test Firestore listeners

---

### Phase 5: Web Interface - Components (Week 2, Days 3-5)

**Objective**: Build UI components for review queue

**Component 1: EntityCard**
```typescript
interface EntityCardProps {
  item: ReviewItem;
  onApprove: (id: string) => void;
  onReject: (id: string) => void;
  selected: boolean;
  onSelect: (id: string) => void;
}

// Features:
// - Display entity name and type
// - Show confidence score with color coding
// - Display extracted context
// - Show properties
// - Approve/Reject buttons
// - Checkbox for batch selection
```

**Component 2: RelationshipCard**
```typescript
interface RelationshipCardProps {
  item: ReviewItem;
  onApprove: (id: string) => void;
  onReject: (id: string) => void;
  selected: boolean;
  onSelect: (id: string) => void;
}

// Features:
// - Display source → relationship → target
// - Show confidence score
// - Display extracted context
// - Show properties
// - Approve/Reject buttons
// - Checkbox for batch selection
```

**Component 3: ReviewQueue**
```typescript
interface ReviewQueueProps {
  userId: string;
}

// Features:
// - List all pending items
// - Filter by type (entity/relationship)
// - Filter by confidence threshold
// - Sort by confidence, date
// - Batch selection
// - Batch approve/reject
// - Real-time updates
// - Pagination
```

**Component 4: ConfidenceBadge**
```typescript
interface ConfidenceBadgeProps {
  confidence: number;
}

// Features:
// - Color-coded badge (red < 0.5, yellow 0.5-0.8, green > 0.8)
// - Percentage display
// - Tooltip with explanation
```

**Component 5: BatchActions**
```typescript
interface BatchActionsProps {
  selectedIds: string[];
  onApproveAll: () => void;
  onRejectAll: () => void;
  onClearSelection: () => void;
}

// Features:
// - Show count of selected items
// - Batch approve button
// - Batch reject button
// - Clear selection button
```

**Testing**:
- Test each component in isolation
- Test user interactions
- Test real-time updates
- Test batch operations
- Test responsive design

---

### Phase 6: Real-Time Updates (Week 3, Days 1-2)

**Objective**: Implement Firestore listeners for real-time UI updates

**Implementation**:
```typescript
// Hook: useReviewQueue
export function useReviewQueue(userId: string) {
  const [items, setItems] = useState<ReviewItem[]>([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    // Subscribe to Firestore collection
    const unsubscribe = firestore
      .collection('review_queue')
      .where('user_id', '==', userId)
      .where('status', '==', 'pending')
      .orderBy('confidence', 'desc')
      .onSnapshot((snapshot) => {
        const newItems = snapshot.docs.map(doc => ({
          id: doc.id,
          ...doc.data()
        }));
        setItems(newItems);
        setLoading(false);
      });
    
    return () => unsubscribe();
  }, [userId]);
  
  return { items, loading };
}
```

**Features**:
- Real-time item additions
- Real-time status updates
- Real-time deletions
- Optimistic UI updates
- Error handling

**Testing**:
- Test real-time additions
- Test real-time updates
- Test real-time deletions
- Test connection loss handling
- Test reconnection

---

### Phase 7: Integration & Deployment (Week 3, Days 3-5)

**Objective**: Integrate all components and deploy to production

**Integration Tasks**:
1. Connect web UI to API endpoints
2. Integrate authentication flow
3. Add error handling and loading states
4. Implement analytics tracking
5. Add user feedback (toasts, notifications)

**Deployment Steps**:

**Backend (Cloud Functions)**:
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
    --allow-unauthenticated \
    --service-account=aletheia-functions@aletheia-codex-prod.iam.gserviceaccount.com
```

**Frontend (Firebase Hosting)**:
```bash
# Build React app
cd web
npm run build

# Deploy to Firebase Hosting
firebase deploy --only hosting
```

**Testing**:
- End-to-end testing
- User acceptance testing
- Performance testing
- Security testing
- Cross-browser testing

---

## Technical Specifications

### Firestore Security Rules

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Review queue - user can only access their own items
    match /review_queue/{itemId} {
      allow read, write: if request.auth != null 
        && request.auth.uid == resource.data.user_id;
      allow create: if request.auth != null 
        && request.auth.uid == request.resource.data.user_id;
    }
    
    // User stats - user can only access their own stats
    match /user_stats/{userId} {
      allow read, write: if request.auth != null 
        && request.auth.uid == userId;
    }
  }
}
```

### Confidence Score Color Coding

```typescript
function getConfidenceColor(confidence: number): string {
  if (confidence >= 0.8) return 'green';   // High confidence
  if (confidence >= 0.5) return 'yellow';  // Medium confidence
  return 'red';                             // Low confidence
}

function getConfidenceLabel(confidence: number): string {
  if (confidence >= 0.8) return 'High';
  if (confidence >= 0.5) return 'Medium';
  return 'Low';
}
```

### API Response Format

```typescript
// Success response
{
  success: true,
  data: {
    // Response data
  }
}

// Error response
{
  success: false,
  error: {
    code: string,
    message: string,
    details?: any
  }
}
```

---

## Testing Strategy

### Unit Tests
- Test queue manager functions
- Test approval workflow logic
- Test API endpoint handlers
- Test React components
- Test custom hooks

### Integration Tests
- Test Firestore operations
- Test Neo4j integration
- Test API endpoints
- Test authentication flow
- Test real-time updates

### End-to-End Tests
- Test complete approval workflow
- Test batch operations
- Test error scenarios
- Test edge cases
- Test user experience

### Performance Tests
- Test with large item counts
- Test batch operation performance
- Test real-time update performance
- Test API response times
- Test UI rendering performance

---

## Success Metrics

### Functional Metrics
- ✅ Review queue operational
- ✅ Approval/rejection working
- ✅ Batch operations functional
- ✅ Real-time updates working
- ✅ UI responsive and intuitive

### Performance Metrics
- ✅ API response time < 500ms
- ✅ UI render time < 100ms
- ✅ Real-time update latency < 1s
- ✅ Batch operation time < 2s per 10 items

### User Experience Metrics
- ✅ Intuitive interface (user testing)
- ✅ Clear confidence indicators
- ✅ Smooth interactions
- ✅ Helpful error messages
- ✅ Responsive design (mobile-friendly)

---

## Deployment Checklist

### Pre-Deployment
- [ ] All code complete and tested
- [ ] Security rules configured
- [ ] API endpoints deployed
- [ ] Web app built and tested
- [ ] Documentation complete

### Deployment
- [ ] Deploy Cloud Functions
- [ ] Deploy Firebase Hosting
- [ ] Configure custom domain (optional)
- [ ] Enable analytics
- [ ] Set up monitoring

### Post-Deployment
- [ ] Verify all endpoints working
- [ ] Test authentication flow
- [ ] Verify real-time updates
- [ ] Monitor error rates
- [ ] Gather user feedback

---

## Known Limitations

1. **No Offline Support**: Requires internet connection
2. **Basic Filtering**: Advanced search not implemented
3. **No Undo**: Approved/rejected items cannot be undone
4. **Limited Batch Size**: Max 50 items per batch operation
5. **No Mobile App**: Web-only interface

---

## Future Enhancements

### Sprint 4 Preview
- Natural language query interface
- Graph visualization
- Advanced search and filtering
- Export functionality

### Long-Term
- Mobile app (iOS/Android)
- Offline support
- Advanced analytics
- Collaborative review
- AI-assisted review suggestions

---

**Sprint 3 Start**: TBD (after Sprint 2 deployment)  
**Estimated Completion**: 2-3 weeks from start  
**Success Criteria**: All objectives met, deployed to production

---

*End of Sprint 3 Implementation Guide*