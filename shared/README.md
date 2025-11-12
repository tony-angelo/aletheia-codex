# Shared Directory

## Overview
This directory contains shared libraries and utilities used across multiple Cloud Functions and components of the Aletheia Codex project.

## Purpose
- Provide reusable code across functions
- Centralize common functionality
- Ensure consistent implementations
- Simplify maintenance and updates
- Reduce code duplication

## Directory Structure
```
shared/
├── README.md                          # This file
├── ai/                                # AI service integration
│   ├── gemini_service.py              # Gemini AI client
│   ├── entity_extractor.py            # Entity extraction
│   └── relationship_detector.py       # Relationship detection
├── auth/                              # Authentication utilities
│   └── firebase_auth.py               # Firebase auth decorator
├── db/                                # Database clients
│   ├── firestore_client.py            # Firestore operations
│   └── neo4j_client.py                # Neo4j operations
└── models/                            # Data models
    ├── note.py                        # Note model
    ├── entity.py                      # Entity model
    └── relationship.py                # Relationship model
```

## AI Services (`ai/`)

### gemini_service.py
Interface with Google Gemini AI

**Configuration**:
- Model: gemini-2.0-flash-exp
- Temperature: 0.1
- Max tokens: 2048

### entity_extractor.py
Extract entities from text using AI

**Performance**:
- Accuracy: >85%
- Processing: ~1-2 seconds
- Cost: ~$0.0003 per extraction

### relationship_detector.py
Detect relationships between entities

**Performance**:
- Accuracy: >75%
- Processing: ~1-2 seconds
- Cost: ~$0.0003 per detection

## Authentication (`auth/`)

### firebase_auth.py
Firebase authentication decorator

**Usage**:
```python
from shared.auth.firebase_auth import require_auth

@require_auth
def my_function(request, user_id):
    return {"message": f"Hello {user_id}"}
```

## Database Clients (`db/`)

### firestore_client.py
Firestore database operations

**Features**:
- CRUD operations
- Batch operations
- Query builders

### neo4j_client.py
Neo4j graph database operations

**Features**:
- HTTP API integration
- Node CRUD operations
- Relationship management
- Cypher query execution

## Data Models (`models/`)

### note.py
Note data model with validation

### entity.py
Entity data model with approval workflow

### relationship.py
Relationship data model with approval workflow

## Code Reuse Benefits

- **Consistency**: Same logic across all functions
- **Maintainability**: Single source of truth
- **Performance**: Optimized operations
- **Testing**: Centralized test coverage

## Related Documentation
- [Functions README](../functions/README.md)
- [Sprint 2 Documentation](../docs/sprint2/)
