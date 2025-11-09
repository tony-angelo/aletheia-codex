# Sprint 3 Reference Documentation

This document lists all reference materials available for Sprint 3 implementation.

---

## 📚 Core Project Documentation

These documents provide essential context about the AletheiaCodex project:

### Project Vision & Architecture
- **Location**: `docs/01_Project_Vision.md`
- **Purpose**: Understand project goals, features, and user personas
- **Key Sections**: Core features, v1.0 scope, user personas, glossary

- **Location**: `docs/02_Architecture_Overview.md`
- **Purpose**: Understand technical architecture and design decisions
- **Key Sections**: Multi-database architecture, AI abstraction layer, security model

### Database Schemas
- **Location**: `docs/05_Database_Schemas.md`
- **Purpose**: Understand Firestore and Neo4j data structures
- **Key Sections**: 
  - Firestore collections (users, notes, review_queue)
  - Neo4j node types (User, Person, Place, Organization, Concept, Moment, Thing)
  - Relationship types and patterns
  - Security query patterns

### Environment Setup
- **Location**: `docs/10_Environment_Setup.md`
- **Purpose**: GCP project configuration and setup
- **Key Sections**: APIs, Firebase, Neo4j, Secret Manager, IAM

- **Location**: `docs/10_Environment_Setup_Windows_VSCode.md`
- **Purpose**: Local development setup for Windows users
- **Key Sections**: VS Code configuration, local testing, debugging

### Secret Management
- **Location**: `docs/24_Secret_Management.md`
- **Purpose**: How to access and manage secrets
- **Key Sections**: Secret Manager integration, helper utilities, testing

---

## 🏃 Sprint-Specific Documentation

### Sprint 1: Neo4j HTTP API
- **Location**: `docs/sprint1/`
- **Status**: ✅ Complete
- **Key Learnings**: 
  - Neo4j Bolt protocol incompatible with Cloud Run
  - HTTP API (Query API v2) works perfectly
  - Secret sanitization critical (.strip() for \r\n)

### Sprint 2: AI Integration
- **Location**: `docs/sprint2/`
- **Status**: ✅ Complete
- **Key Achievements**:
  - Gemini 2.0 Flash integration
  - Entity extraction: >85% accuracy
  - Relationship detection: >75% accuracy
  - Cost: $0.0006 per document (94% under target)

### Sprint 3: Review Queue & User Interface
- **Location**: `docs/sprint3/` (this directory)
- **Status**: 🚧 In Progress
- **Documents**:
  - `WORKER_PROMPT.md` - Complete prompt for worker threads
  - `WORKER_THREAD_GUIDELINES.md` - MANDATORY rules
  - `SPRINT3_IMPLEMENTATION_GUIDE.md` - Technical specifications
  - `SPRINT3_WORKER_BRIEF.md` - Sprint overview
  - `README.md` - Quick start guide
  - `REFERENCE_DOCS.md` - This document

---

## 🔧 Technical Reference

### Firestore
- **Official Docs**: https://firebase.google.com/docs/firestore
- **Python SDK**: https://firebase.google.com/docs/firestore/quickstart#python
- **Security Rules**: https://firebase.google.com/docs/firestore/security/get-started
- **Real-time Updates**: https://firebase.google.com/docs/firestore/query-data/listen

### Neo4j
- **HTTP API Docs**: https://neo4j.com/docs/http-api/current/
- **Query API v2**: https://neo4j.com/docs/http-api/current/actions/query-api/
- **Cypher Query Language**: https://neo4j.com/docs/cypher-manual/current/

### Cloud Functions
- **Official Docs**: https://cloud.google.com/functions/docs
- **Python Runtime**: https://cloud.google.com/functions/docs/concepts/python-runtime
- **Environment Variables**: https://cloud.google.com/functions/docs/configuring/env-var
- **Secret Manager Integration**: https://cloud.google.com/functions/docs/configuring/secrets

### React & TypeScript
- **React Docs**: https://react.dev/
- **TypeScript Docs**: https://www.typescriptlang.org/docs/
- **Tailwind CSS**: https://tailwindcss.com/docs
- **Firebase SDK**: https://firebase.google.com/docs/web/setup

### Firebase Hosting
- **Official Docs**: https://firebase.google.com/docs/hosting
- **Deploy from CLI**: https://firebase.google.com/docs/hosting/quickstart
- **Custom Domains**: https://firebase.google.com/docs/hosting/custom-domain

---

## 📊 Code Examples

### Firestore Operations (Python)
```python
from google.cloud import firestore

db = firestore.Client()

# Add document
doc_ref = db.collection('review_queue').document()
doc_ref.set({
    'userId': 'user123',
    'status': 'pending',
    'createdAt': firestore.SERVER_TIMESTAMP
})

# Query documents
docs = db.collection('review_queue')\
    .where('userId', '==', 'user123')\
    .where('status', '==', 'pending')\
    .order_by('createdAt', direction=firestore.Query.DESCENDING)\
    .limit(10)\
    .stream()

for doc in docs:
    print(f'{doc.id} => {doc.to_dict()}')
```

### Neo4j HTTP API (Python)
```python
import requests
import json

def query_neo4j(cypher_query, parameters=None):
    url = f"{NEO4J_URI}/db/neo4j/query/v2"
    headers = {
        "Authorization": f"Bearer {NEO4J_PASSWORD}",
        "Content-Type": "application/json"
    }
    payload = {
        "statement": cypher_query,
        "parameters": parameters or {}
    }
    
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()
```

### React Component with Firestore (TypeScript)
```typescript
import { useEffect, useState } from 'react';
import { collection, query, where, onSnapshot } from 'firebase/firestore';
import { db } from './firebase';

function ReviewQueue({ userId }: { userId: string }) {
  const [items, setItems] = useState([]);

  useEffect(() => {
    const q = query(
      collection(db, 'review_queue'),
      where('userId', '==', userId),
      where('status', '==', 'pending')
    );

    const unsubscribe = onSnapshot(q, (snapshot) => {
      const newItems = snapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data()
      }));
      setItems(newItems);
    });

    return () => unsubscribe();
  }, [userId]);

  return (
    <div>
      {items.map(item => (
        <div key={item.id}>{item.name}</div>
      ))}
    </div>
  );
}
```

---

## 🔐 Security Patterns

### Firestore Security Rules
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /review_queue/{itemId} {
      allow read, write: if request.auth != null 
        && request.auth.uid == resource.data.userId;
    }
  }
}
```

### Neo4j Query Security Pattern
```cypher
// ALWAYS start queries with User node
MATCH (u:User {firebaseUid: $userId})
MATCH (u)-[:OWNS]->(item)
WHERE item.id = $itemId
RETURN item
```

### Cloud Functions Authentication
```python
from firebase_admin import auth

def verify_token(request):
    """Verify Firebase Auth token from request"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        raise ValueError('Missing or invalid Authorization header')
    
    token = auth_header.split('Bearer ')[1]
    decoded_token = auth.verify_id_token(token)
    return decoded_token['uid']
```

---

## 🎯 Performance Targets

### API Endpoints
- **Response Time**: <500ms (p95)
- **Throughput**: >100 requests/second
- **Error Rate**: <1%

### Web Interface
- **Initial Load**: <2 seconds
- **Render Time**: <100ms
- **Real-time Update Latency**: <200ms

### Batch Operations
- **50 items**: <2 seconds
- **100 items**: <5 seconds
- **500 items**: <30 seconds

### Cost
- **Per Operation**: <$0.0001
- **Per 100 Operations**: <$0.01
- **Per 1000 Operations**: <$0.10

---

## 📝 Testing Guidelines

### Unit Tests
- Test individual functions in isolation
- Mock external dependencies (Firestore, Neo4j)
- Aim for >80% code coverage

### Integration Tests
- Test component interactions
- Use Firestore emulator for local testing
- Test error handling and edge cases

### End-to-End Tests
- Test complete workflows in production
- Verify real-time updates work
- Test batch operations with real data
- Check production logs for errors

---

## 🆘 Common Issues & Solutions

### Issue: Firestore Permission Denied
**Solution**: Check security rules and ensure user is authenticated

### Issue: Neo4j Connection Timeout
**Solution**: Verify HTTP API endpoint and credentials in Secret Manager

### Issue: Real-time Updates Not Working
**Solution**: Check Firestore listener setup and ensure proper cleanup

### Issue: Batch Operation Timeout
**Solution**: Implement chunking for large batches (50-100 items per chunk)

### Issue: CORS Errors in Web Interface
**Solution**: Configure CORS in Cloud Functions or use Firebase Hosting rewrites

---

## 📞 Getting Help

### When You Need Permissions
Request specific IAM roles with exact gcloud commands:
```
I need the `roles/datastore.indexAdmin` role to create Firestore indexes.
Please run: gcloud projects add-iam-policy-binding ...
```

### When You Need Secrets
Request specific secrets with creation commands:
```
I need the [secret-name] to [reason].
Please add it to Secret Manager: gcloud secrets create ...
```

### When You Need Clarification
Ask specific questions with context:
```
I need clarification on [topic].
[Specific question with relevant context]
```

---

## ✅ Quick Reference Checklist

Before starting implementation:
- [ ] Read WORKER_THREAD_GUIDELINES.md
- [ ] Read SPRINT3_IMPLEMENTATION_GUIDE.md
- [ ] Read SPRINT3_WORKER_BRIEF.md
- [ ] Review 01_Project_Vision.md
- [ ] Review 05_Database_Schemas.md
- [ ] Understand Sprint 1 & 2 outcomes

During implementation:
- [ ] Test locally after each component
- [ ] Request permissions when needed
- [ ] Commit changes regularly
- [ ] Update documentation as you go

Before marking complete:
- [ ] All 15 success criteria met
- [ ] Deployed to production
- [ ] Tested in production
- [ ] Performance targets met
- [ ] ONE completion report created
- [ ] PR created with all changes

---

**This document is your reference hub. Bookmark it and refer back as needed!**