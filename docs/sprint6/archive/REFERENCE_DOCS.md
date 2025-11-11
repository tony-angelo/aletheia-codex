# Sprint 6 Reference Documentation

This document provides links and references to all documentation needed for Sprint 6.

---

## Table of Contents
1. [Project Documentation](#project-documentation)
2. [Sprint 5 Learnings](#sprint-5-learnings)
3. [Current Codebase](#current-codebase)
4. [Technology Stack](#technology-stack)
5. [External Resources](#external-resources)

---

## Project Documentation

### Core Documents
- **Project Vision**: `docs/01_Project_Vision.md`
- **Architecture Overview**: `docs/02_Architecture_Overview.md`
- **Database Schemas**: `docs/05_Database_Schemas.md`
- **Project Status**: `docs/project/PROJECT_STATUS.md`

### Worker Guidelines
- **Worker Thread Guidelines**: `docs/WORKER_THREAD_GUIDELINES.md` - **MANDATORY READING**

### Sprint Documentation
- **Sprint 5 Completion**: `docs/sprint5/SPRINT5_COMPLETION_REPORT.md`
- **Sprint 5 Workflow**: `docs/sprint5/WORKFLOW_ARCHITECTURE.md`

---

## Sprint 5 Learnings

### What Was Fixed
1. ✅ **Orchestration Function Trigger** - Changed from HTTP to Firestore trigger
2. ✅ **Note Processing Workflow** - Automatic processing on note creation
3. ✅ **AI Extraction** - 4 entities extracted from test note
4. ✅ **Review Queue** - Items automatically populated

### Key Achievements
- **Trigger Latency**: < 1 second
- **Processing Time**: ~2 seconds per note
- **Success Rate**: 100%
- **Architecture**: Event-driven, fully automated

### Known Issues (Non-Critical)
- GraphPopulator error (doesn't prevent workflow completion)
- Approval workflow needs user testing

---

## Current Codebase

### Existing Pages (3)
1. **NotesPage** (`web/src/pages/NotesPage.tsx`)
   - Note input component
   - Note history
   - Processing status

2. **ReviewPage** (`web/src/pages/ReviewPage.tsx`)
   - Review queue display
   - Approval workflow
   - Entity and relationship cards

3. **GraphPage** (`web/src/pages/GraphPage.tsx`)
   - **Currently**: Placeholder only ("Coming Soon")
   - **Sprint 6**: Full implementation

### Existing Components (13)
Located in `web/src/components/` (flat structure):
- BatchActions.tsx
- ConfidenceBadge.tsx
- EntityCard.tsx
- ExtractionResults.tsx
- Navigation.tsx
- NoteCard.tsx
- NoteHistory.tsx
- NoteInput.tsx
- ProcessingStatus.tsx
- RelationshipCard.tsx
- ReviewQueue.tsx
- SignIn.tsx
- SignUp.tsx

### Existing Services
Located in `web/src/services/`:
- `notesService.ts` - Note CRUD operations
- `reviewService.ts` - Review queue operations
- `api.ts` - API client utilities

### Existing Functions
Located in `functions/`:
- `orchestration/` - Note processing (Firestore trigger)
- `review_queue/` - Review approval (HTTP)

---

## Technology Stack

### Frontend
- **Framework**: React 18
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State**: React Hooks
- **Auth**: Firebase Authentication
- **Database**: Firestore

### Backend
- **Runtime**: Python 3.11
- **Platform**: Cloud Functions Gen 2
- **Database**: Firestore + Neo4j Aura
- **AI**: Gemini 2.0 Flash Experimental

### Deployment
- **Frontend**: Firebase Hosting
- **Backend**: Cloud Functions
- **Region**: us-central1

---

## Database Schemas

### Firestore Collections

#### notes
```typescript
interface Note {
  id: string;
  userId: string;
  content: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  createdAt: Timestamp;
  processedAt?: Timestamp;
  extractionSummary?: {
    entityCount: number;
    relationshipCount: number;
  };
}
```

#### reviewQueue
```typescript
interface ReviewItem {
  id: string;
  userId: string;
  noteId: string;
  type: 'entity' | 'relationship';
  data: Entity | Relationship;
  status: 'pending' | 'approved' | 'rejected';
  createdAt: Timestamp;
  reviewedAt?: Timestamp;
}
```

### Neo4j Schema

#### Node Types
- **User**: User account
- **Person**: Individual person
- **Place**: Physical location
- **Organization**: Company, institution
- **Concept**: Abstract idea
- **Thing**: Universal catch-all

#### Relationship Types
- **OWNS**: User owns node
- **KNOWS**: Person knows Person
- **WORKS_AT**: Person works at Organization
- **LOCATED_IN**: Place/Organization in Place
- **RELATED_TO**: Generic relationship

---

## API Specifications

### Existing APIs

#### Orchestration Function
- **Type**: Firestore Trigger
- **Event**: `google.cloud.firestore.document.v1.created`
- **Collection**: `notes/{noteId}`
- **Region**: us-central1
- **Trigger Location**: nam5

#### Review Queue Function
- **Type**: HTTP
- **URL**: `https://us-central1-aletheia-codex-prod.cloudfunctions.net/review-queue-function`
- **Methods**: POST
- **Auth**: Firebase ID token

**Endpoints**:
- `POST /approve` - Approve review item
- `POST /reject` - Reject review item

### New API (Sprint 6)

#### Graph Function
- **Type**: HTTP
- **URL**: `https://us-central1-aletheia-codex-prod.cloudfunctions.net/graph-function`
- **Methods**: GET
- **Auth**: User ID in query params

**Endpoints**:
- `GET /nodes?userId={userId}&limit={limit}&offset={offset}&type={type}`
- `GET /nodes/{nodeId}?userId={userId}`
- `GET /search?userId={userId}&query={query}`

---

## Component Patterns

### Standard Component Structure
```typescript
import React, { useState, useEffect } from 'react';

interface MyComponentProps {
  title: string;
  onAction: () => void;
  optional?: boolean;
}

export const MyComponent: React.FC<MyComponentProps> = ({ 
  title, 
  onAction, 
  optional 
}) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    // Load data
  }, []);
  
  if (loading) {
    return <LoadingSpinner />;
  }
  
  if (error) {
    return <ErrorMessage message={error} />;
  }
  
  return (
    <div className="component-container">
      {/* Component content */}
    </div>
  );
};
```

### Async Data Loading Pattern
```typescript
const [data, setData] = useState<DataType[]>([]);
const [loading, setLoading] = useState(true);
const [error, setError] = useState<string | null>(null);

useEffect(() => {
  loadData();
}, []);

const loadData = async () => {
  try {
    setLoading(true);
    setError(null);
    const result = await fetchData();
    setData(result);
  } catch (err) {
    setError(err instanceof Error ? err.message : 'Failed to load');
  } finally {
    setLoading(false);
  }
};
```

---

## Styling Guidelines

### Tailwind CSS Classes

**Colors**:
- Primary: `bg-indigo-600`, `text-indigo-600`
- Success: `bg-green-600`, `text-green-600`
- Error: `bg-red-600`, `text-red-600`
- Neutral: `bg-gray-100`, `text-gray-900`

**Spacing**:
- Padding: `p-4`, `px-6`, `py-4`
- Margin: `m-4`, `mx-auto`, `my-8`
- Gap: `gap-4`, `space-y-4`

**Layout**:
- Container: `max-w-7xl mx-auto px-4 sm:px-6 lg:px-8`
- Grid: `grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4`
- Flex: `flex items-center justify-between`

**Responsive**:
- Mobile: default (no prefix)
- Tablet: `sm:` (640px+)
- Desktop: `md:` (768px+), `lg:` (1024px+)

---

## Testing Patterns

### Component Testing
```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';

describe('MyComponent', () => {
  it('renders correctly', () => {
    render(<MyComponent />);
    expect(screen.getByText(/expected text/i)).toBeInTheDocument();
  });
  
  it('handles user interaction', async () => {
    const onAction = jest.fn();
    render(<MyComponent onAction={onAction} />);
    
    fireEvent.click(screen.getByRole('button'));
    
    await waitFor(() => {
      expect(onAction).toHaveBeenCalled();
    });
  });
});
```

---

## Deployment Commands

### Frontend
```bash
cd web
npm run build
firebase deploy --only hosting
```

### Backend
```bash
# Deploy function
cd functions/graph
gcloud functions deploy graph-function \
  --gen2 \
  --runtime=python311 \
  --region=us-central1 \
  --source=. \
  --entry-point=graph_function \
  --trigger-http \
  --allow-unauthenticated \
  --service-account=aletheia-functions@aletheia-codex-prod.iam.gserviceaccount.com \
  --set-env-vars GCP_PROJECT=aletheia-codex-prod \
  --memory=256MB \
  --timeout=60s
```

### Check Logs
```bash
# Function logs
gcloud functions logs read graph-function \
  --project aletheia-codex-prod \
  --limit 100

# Follow logs
gcloud functions logs tail graph-function \
  --project aletheia-codex-prod
```

---

## External Resources

### Documentation
- [React Documentation](https://react.dev/)
- [TypeScript Documentation](https://www.typescriptlang.org/docs/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Firebase Documentation](https://firebase.google.com/docs)
- [Cloud Functions Documentation](https://cloud.google.com/functions/docs)
- [Neo4j Documentation](https://neo4j.com/docs/)

### Tools
- [Firebase Console](https://console.firebase.google.com/project/aletheia-codex-prod)
- [Google Cloud Console](https://console.cloud.google.com/home/dashboard?project=aletheia-codex-prod)
- [Neo4j Aura Console](https://console.neo4j.io/)

---

## Common Issues and Solutions

### Issue: Import Path Errors After Reorganization
**Solution**: Update all import paths to reflect new component structure

### Issue: CORS Errors on API Calls
**Solution**: Verify CORS headers in Cloud Function:
```python
headers = {'Access-Control-Allow-Origin': '*'}
```

### Issue: Authentication Failures
**Solution**: Ensure Firebase ID token is sent in requests:
```typescript
const user = auth.currentUser;
const token = await user?.getIdToken();
```

### Issue: Build Failures
**Solution**: Check TypeScript errors and missing dependencies:
```bash
npm install
npm run build
```

---

**End of Reference Documentation**