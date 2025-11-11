# Sprint 5 Reference Documentation

This document provides links and references to all documentation needed for Sprint 5.

---

## Table of Contents
1. [Project Documentation](#project-documentation)
2. [Architecture Documentation](#architecture-documentation)
3. [Previous Sprint Documentation](#previous-sprint-documentation)
4. [Database Schemas](#database-schemas)
5. [API Specifications](#api-specifications)
6. [External Resources](#external-resources)

---

## Project Documentation

### Project Vision
**Location**: `docs/project/PROJECT_VISION.md`

**Key Sections**:
- Core requirements and features
- User personas
- Success metrics
- Roadmap

### Project Status
**Location**: `docs/project/PROJECT_STATUS.md`

**Key Sections**:
- Current sprint status
- Completed sprints
- Known issues
- Next steps

### Sprint Planning Methodology
**Location**: `docs/project/SPRINT_PLANNING.md`

**Key Sections**:
- Sprint structure
- Roles and responsibilities
- Workflow process
- Documentation standards

---

## Architecture Documentation

### Architecture Overview
**Location**: `docs/architecture/02_Architecture_Overview.md`

**Key Sections**:
- System architecture diagram
- Component descriptions
- Technology stack
- Design decisions

### Database Schemas
**Location**: `docs/architecture/05_Database_Schemas.md`

**Key Sections**:
- Firestore collections (users, notes, review_queue)
- Neo4j node types (User, Person, Place, Organization, etc.)
- Relationship types
- Security patterns

### Secret Management
**Location**: `docs/architecture/24_Secret_Management.md`

**Key Sections**:
- Secret Manager integration
- Helper utilities
- Local development setup
- Security best practices

---

## Previous Sprint Documentation

### Sprint 1: Neo4j HTTP API
**Location**: `docs/sprint1/`

**Key Learnings**:
- Neo4j Bolt protocol incompatible with Cloud Run
- HTTP API implementation using Query API v2
- Secret management best practices
- Connection handling patterns

**Relevant Files**:
- `docs/sprint1/SPRINT_01_Neo4j_Authentication_Resolution.md`
- `docs/sprint1/SECRET_MANAGEMENT_GUIDE.md`
- `docs/sprint1/DEPLOYMENT_GUIDE.md`

### Sprint 2: AI Integration
**Location**: `docs/sprint2/`

**Key Learnings**:
- Gemini 2.0 Flash integration
- Entity extraction (>85% accuracy)
- Relationship detection (>75% accuracy)
- Cost optimization ($0.0006 per document)

**Relevant Files**:
- `docs/sprint2/SPRINT2_IMPLEMENTATION_GUIDE.md`
- `docs/sprint2/COMPLETION_REPORT.md`

### Sprint 3: Review Queue & UI
**Location**: `docs/sprint3/`

**Key Learnings**:
- Firestore-based review queue
- Approval workflow
- React-based web interface
- Real-time updates

**Relevant Files**:
- `docs/sprint3/SPRINT3_IMPLEMENTATION_GUIDE.md`
- `docs/sprint3/COMPLETION_REPORT.md`

### Sprint 4: Note Input & Processing
**Location**: `docs/sprint4/`

**Key Learnings**:
- Navigation system with routing
- Chat-like note input interface
- Real-time processing status
- Note history management

**Relevant Files**:
- `docs/sprint4/SPRINT4_IMPLEMENTATION_GUIDE.md`
- `docs/sprint4/COMPLETION_REPORT.md`

### Sprint 4.5: Authentication Fix
**Location**: `docs/sprint4.5/`

**Key Learnings**:
- Firebase Authentication integration
- Google Sign-In provider
- Auth token flow
- Security rules

**Relevant Files**:
- `docs/sprint4.5/SPRINT4.5_IMPLEMENTATION_GUIDE.md`
- `docs/sprint4.5/COMPLETION_REPORT.md`

---

## Database Schemas

### Firestore Collections

#### users Collection
```typescript
interface User {
  uid: string;              // Firebase Auth UID
  email: string;            // User email
  displayName?: string;     // Display name
  photoURL?: string;        // Profile photo URL
  createdAt: Timestamp;     // Account creation time
  lastLoginAt: Timestamp;   // Last login time
}
```

#### notes Collection
```typescript
interface Note {
  id: string;               // Auto-generated document ID
  userId: string;           // Owner's Firebase Auth UID
  content: string;          // Note text content
  status: 'pending' | 'processing' | 'processed' | 'failed';
  createdAt: Timestamp;     // Creation time
  processedAt?: Timestamp;  // Processing completion time
  error?: string;           // Error message if failed
}
```

#### review_queue Collection
```typescript
interface ReviewItem {
  id: string;               // Auto-generated document ID
  userId: string;           // Owner's Firebase Auth UID
  noteId: string;           // Source note ID
  type: 'entity' | 'relationship';
  data: Entity | Relationship;
  status: 'pending' | 'approved' | 'rejected';
  createdAt: Timestamp;     // Creation time
  reviewedAt?: Timestamp;   // Review time
}

interface Entity {
  name: string;             // Entity name
  type: string;             // Entity type (Person, Place, etc.)
  properties: Record<string, any>;
}

interface Relationship {
  sourceEntity: string;     // Source entity name
  targetEntity: string;     // Target entity name
  type: string;             // Relationship type
  properties: Record<string, any>;
}
```

### Neo4j Schema

#### Node Types
- **User**: User account node
- **Person**: Individual person
- **Place**: Physical location
- **Organization**: Company, institution, etc.
- **Concept**: Abstract idea or topic
- **Moment**: Specific point in time
- **Thing**: Universal catch-all for any entity type

#### Relationship Types
- **KNOWS**: Person knows Person
- **WORKS_AT**: Person works at Organization
- **LOCATED_IN**: Place/Organization located in Place
- **HAPPENED_AT**: Moment happened at Place
- **RELATED_TO**: Generic relationship
- **OWNS**: User owns any node
- Plus dynamic AI-generated relationship types

---

## API Specifications

### Orchestration Function
**Endpoint**: Firestore trigger (not HTTP)
**Trigger**: `google.cloud.firestore.document.v1.created`
**Collection**: `notes`

**Event Payload**:
```json
{
  "data": {
    "value": {
      "fields": {
        "userId": {"stringValue": "user-123"},
        "content": {"stringValue": "Note text..."},
        "status": {"stringValue": "pending"},
        "createdAt": {"timestampValue": "2024-01-15T10:00:00Z"}
      }
    }
  },
  "subject": "documents/notes/note-id-123"
}
```

**Processing Flow**:
1. Parse Firestore event
2. Extract note content
3. Call AI service for entity extraction
4. Create review queue items
5. Update note status to 'processed'

### Review Queue Function
**Endpoint**: `https://us-central1-aletheia-codex-prod.cloudfunctions.net/review-queue-function`
**Method**: POST
**Authentication**: Firebase ID token in Authorization header

**Request Body**:
```json
{
  "action": "approve" | "reject",
  "itemId": "review-item-id",
  "userId": "user-123"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Item approved successfully",
  "nodeId": "neo4j-node-id"  // Only for approve action
}
```

### AI Service (Internal)
**Function**: `extract_entities_and_relationships(text: str, user_id: str)`
**Model**: Gemini 2.0 Flash Experimental

**Input**:
```python
text = "I met John Smith at Google headquarters in Mountain View."
user_id = "user-123"
```

**Output**:
```json
{
  "entities": [
    {
      "name": "John Smith",
      "type": "Person",
      "properties": {}
    },
    {
      "name": "Google",
      "type": "Organization",
      "properties": {}
    },
    {
      "name": "Mountain View",
      "type": "Place",
      "properties": {}
    }
  ],
  "relationships": [
    {
      "sourceEntity": "John Smith",
      "targetEntity": "Google",
      "type": "WORKS_AT",
      "properties": {}
    },
    {
      "sourceEntity": "Google",
      "targetEntity": "Mountain View",
      "type": "LOCATED_IN",
      "properties": {}
    }
  ]
}
```

---

## External Resources

### Firebase Documentation
- [Firestore Security Rules](https://firebase.google.com/docs/firestore/security/get-started)
- [Firebase Authentication](https://firebase.google.com/docs/auth)
- [Firebase Hosting](https://firebase.google.com/docs/hosting)

### Google Cloud Documentation
- [Cloud Functions (2nd gen)](https://cloud.google.com/functions/docs/2nd-gen/overview)
- [Cloud Functions Logging](https://cloud.google.com/functions/docs/monitoring/logging)
- [Secret Manager](https://cloud.google.com/secret-manager/docs)
- [IAM Roles](https://cloud.google.com/iam/docs/understanding-roles)

### AI Documentation
- [Gemini API Documentation](https://ai.google.dev/docs)
- [Google AI Studio](https://aistudio.google.com/)
- [Vertex AI](https://cloud.google.com/vertex-ai/docs)

### Neo4j Documentation
- [Neo4j HTTP API](https://neo4j.com/docs/http-api/current/)
- [Cypher Query Language](https://neo4j.com/docs/cypher-manual/current/)
- [Neo4j Aura](https://neo4j.com/cloud/aura/)

### React Documentation
- [React 18](https://react.dev/)
- [React Router](https://reactrouter.com/)
- [TypeScript](https://www.typescriptlang.org/)
- [Tailwind CSS](https://tailwindcss.com/)

---

## Code Examples

### Firestore Write with Error Handling
```typescript
import { collection, addDoc, serverTimestamp } from 'firebase/firestore';
import { db, auth } from '../config/firebase';

async function createNote(content: string): Promise<string> {
  try {
    const user = auth.currentUser;
    if (!user) {
      throw new Error('Not authenticated');
    }

    const docRef = await addDoc(collection(db, 'notes'), {
      userId: user.uid,
      content,
      status: 'pending',
      createdAt: serverTimestamp()
    });

    console.log('Note created:', docRef.id);
    return docRef.id;
  } catch (error) {
    console.error('Failed to create note:', error);
    throw error;
  }
}
```

### Cloud Function with Logging
```python
import functions_framework
import logging
from google.cloud import firestore

logger = logging.getLogger(__name__)

@functions_framework.cloud_event
def orchestration_function(cloud_event):
    logger.info("Function triggered")
    
    try:
        # Parse event
        data = cloud_event.data
        logger.info(f"Event data: {data}")
        
        # Process note
        result = process_note(data)
        logger.info(f"Processing complete: {result}")
        
    except Exception as e:
        logger.error(f"Processing failed: {str(e)}", exc_info=True)
        raise
```

### Neo4j Query with HTTP API
```python
import requests
import json
from shared.utils.secret_manager import get_secret

def create_node(user_id: str, entity: dict):
    """Create node in Neo4j using HTTP API."""
    
    # Get credentials
    neo4j_uri = get_secret('neo4j-uri')
    neo4j_user = get_secret('neo4j-user')
    neo4j_password = get_secret('neo4j-password')
    
    # Build query
    query = """
    MATCH (u:User {userId: $userId})
    CREATE (e:Person {name: $name})
    CREATE (u)-[:OWNS]->(e)
    RETURN e
    """
    
    # Execute query
    response = requests.post(
        f"{neo4j_uri}/db/neo4j/query/v2",
        auth=(neo4j_user, neo4j_password),
        headers={'Content-Type': 'application/json'},
        json={
            'statement': query,
            'parameters': {
                'userId': user_id,
                'name': entity['name']
            }
        }
    )
    
    response.raise_for_status()
    return response.json()
```

---

## Troubleshooting

### Common Issues

#### Issue: "Permission Denied" on Firestore Write
**Symptoms**: 
- Error in browser console: `FirebaseError: Missing or insufficient permissions`
- Note doesn't appear in Firestore

**Causes**:
1. User not authenticated
2. Security rules blocking write
3. userId doesn't match auth.uid

**Solutions**:
1. Check `auth.currentUser` is not null
2. Verify security rules allow create
3. Ensure userId field matches auth.uid

#### Issue: Cloud Function Not Triggering
**Symptoms**:
- Note created in Firestore but not processed
- No function logs

**Causes**:
1. Trigger configuration incorrect
2. Trigger location doesn't match Firestore
3. Function deployment failed

**Solutions**:
1. Verify trigger event filters
2. Check trigger location is `us-central1`
3. Redeploy function with correct trigger

#### Issue: AI Extraction Fails
**Symptoms**:
- Function logs show API error
- No entities extracted

**Causes**:
1. API key invalid or missing
2. Rate limit exceeded
3. Prompt formatting error
4. Response parsing failure

**Solutions**:
1. Verify API key in Secret Manager
2. Check API quota in Google Cloud Console
3. Test prompt with simple text
4. Add response validation

#### Issue: Review Items Not Created
**Symptoms**:
- Entities extracted but review queue empty
- Batch write error in logs

**Causes**:
1. Security rules blocking write
2. Batch size too large (>500)
3. Transaction conflict

**Solutions**:
1. Check security rules allow create
2. Split large batches
3. Add retry logic

---

## Testing Checklist

### Manual Testing
- [ ] Sign in with Google
- [ ] Submit a simple note
- [ ] Check browser console for errors
- [ ] Check Firestore for note document
- [ ] Check Cloud Function logs
- [ ] Check review queue for items
- [ ] Approve an entity
- [ ] Check Neo4j for approved entity
- [ ] Submit note with special characters
- [ ] Submit very long note
- [ ] Test while signed out (should fail gracefully)

### Automated Testing
```bash
# Run end-to-end test
pytest tests/test_note_processing_e2e.py -v

# Run with logging
pytest tests/test_note_processing_e2e.py -v -s

# Run specific test
pytest tests/test_note_processing_e2e.py::test_note_submission -v
```

### Log Verification
```bash
# Check orchestration function logs
gcloud functions logs read orchestration-function \
  --project aletheia-codex-prod \
  --limit 100

# Filter for errors
gcloud functions logs read orchestration-function \
  --project aletheia-codex-prod \
  --limit 100 | grep ERROR

# Follow logs in real-time
gcloud functions logs tail orchestration-function \
  --project aletheia-codex-prod
```

---

## Deployment Commands

### Deploy Orchestration Function
```bash
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

### Deploy Review Queue Function
```bash
gcloud functions deploy review-queue-function \
  --gen2 \
  --runtime python311 \
  --region us-central1 \
  --source functions/review_queue \
  --entry-point review_queue_function \
  --trigger-http \
  --allow-unauthenticated \
  --service-account review-queue-sa@aletheia-codex-prod.iam.gserviceaccount.com \
  --set-env-vars GCP_PROJECT=aletheia-codex-prod \
  --memory 256MB \
  --timeout 60s
```

### Deploy Frontend
```bash
cd web
npm run build
firebase deploy --only hosting
```

### Deploy Firestore Rules
```bash
firebase deploy --only firestore:rules
```

---

## Contact and Support

### GitHub Repository
- **URL**: https://github.com/yourusername/aletheia-codex
- **Issues**: Create issue for blockers or questions
- **PRs**: Submit PR when sprint complete

### Documentation
- **Main Docs**: `docs/README.md`
- **Sprint Docs**: `docs/sprint5/`
- **Architecture**: `docs/architecture/`

### Tools
- [Firebase Console](https://console.firebase.google.com/project/aletheia-codex-prod)
- [Google Cloud Console](https://console.cloud.google.com/home/dashboard?project=aletheia-codex-prod)
- [Cloud Functions](https://console.cloud.google.com/functions/list?project=aletheia-codex-prod)
- [Firestore](https://console.firebase.google.com/project/aletheia-codex-prod/firestore)
- [Neo4j Aura](https://console.neo4j.io/)

---

**End of Reference Documentation**