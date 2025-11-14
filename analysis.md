# AletheiaCodex Project Analysis

## Project Overview
AletheiaCodex is a personal knowledge graph application that automatically extracts entities and relationships from text using AI (Google Gemini), storing them in a Neo4j graph database with a React frontend.

## Technology Stack

### Backend (Python 3.11)
- **Platform**: Google Cloud Functions Gen 2
- **AI**: Google Gemini 2.0 Flash
- **Databases**: 
  - Cloud Firestore (metadata, notes, review queue)
  - Neo4j AuraDB (knowledge graph)
- **Authentication**: Firebase Auth

### Frontend (TypeScript/React)
- **Framework**: React with TypeScript
- **Styling**: Tailwind CSS
- **Hosting**: Firebase Hosting
- **Domain**: https://aletheiacodex.app

### Shared Libraries (Python)
- Common utilities used across Cloud Functions
- AI services, database clients, models

## Repository Structure Analysis

```
aletheia-codex/
├── functions/          # Backend Cloud Functions (Python)
│   ├── ingestion/      # Document ingestion endpoint
│   ├── orchestration/  # AI processing workflow
│   ├── graph/          # Knowledge graph API
│   ├── notes_api/      # Notes management API
│   ├── review_api/     # Review queue API
│   └── shared/         # Symlink to ../shared/
├── shared/             # Shared Python libraries
│   ├── ai/             # AI service integration
│   ├── auth/           # Authentication utilities
│   ├── db/             # Database clients
│   ├── models/         # Data models
│   ├── review/         # Review queue logic
│   └── utils/          # Utility functions
├── web/                # Frontend React application
│   └── src/
│       ├── components/ # React components
│       ├── pages/      # Page components
│       ├── services/   # API services
│       ├── hooks/      # Custom React hooks
│       └── firebase/   # Firebase config
├── scripts/            # Deployment and utility scripts
├── infrastructure/     # Infrastructure as code
└── docs/               # Documentation
```

## Domain Identification

Based on the repository structure and technology stack, I identify **THREE natural domains**:

### 1. Backend Domain
**Directory**: `functions/` and `shared/`
**Technology**: Python 3.11, Cloud Functions Gen 2
**Responsibilities**:
- Cloud Functions implementation
- AI integration (Gemini)
- Database operations (Firestore, Neo4j)
- API endpoints
- Authentication middleware
- Shared libraries and utilities

**Key Components**:
- Ingestion function
- Orchestration function
- Graph API function
- Notes API function
- Review API function
- Shared AI services
- Shared database clients
- Shared models

### 2. Frontend Domain
**Directory**: `web/`
**Technology**: React, TypeScript, Tailwind CSS
**Responsibilities**:
- User interface components
- Page layouts and routing
- State management
- API integration
- Firebase Auth integration
- Real-time updates (Firestore listeners)

**Key Components**:
- Note input interface
- Review queue UI
- Knowledge graph visualization
- Authentication UI
- Navigation system

### 3. Infrastructure Domain
**Directory**: `infrastructure/`, `scripts/`, deployment configs
**Technology**: GCP, Firebase, deployment scripts
**Responsibilities**:
- Cloud infrastructure setup
- Deployment automation
- Environment configuration
- CI/CD pipelines (planned)
- Monitoring and logging

**Key Components**:
- Firebase configuration
- GCP project setup
- Deployment scripts
- Environment variables
- Security rules

## Domain Interfaces

### Backend ↔ Frontend
- **Protocol**: HTTPS REST API
- **Authentication**: Firebase Auth tokens
- **Endpoints**: 
  - `/ingest` - Document ingestion
  - `/orchestrate` - AI processing
  - `/graph/*` - Knowledge graph queries
  - `/notes/*` - Notes management
  - `/review/*` - Review queue operations

### Backend ↔ Infrastructure
- **Deployment**: Cloud Functions deployment
- **Configuration**: Environment variables, secrets
- **Monitoring**: Cloud Logging

### Frontend ↔ Infrastructure
- **Hosting**: Firebase Hosting
- **Deployment**: Firebase deploy
- **Configuration**: Firebase config

## Current Project Status

### Completed (Sprint 1-5)
- ✅ Backend Cloud Functions deployed
- ✅ AI entity extraction working (>85% accuracy)
- ✅ Relationship detection working (>75% accuracy)
- ✅ Review queue implemented
- ✅ Frontend deployed at https://aletheiacodex.app
- ✅ Firebase Authentication working

### Current Blocker (Sprint 6)
- ❌ Organization policy blocks public access to Cloud Functions
- ❌ All API endpoints return 403 Forbidden
- ❌ Frontend cannot communicate with backend

### Recommended Next Steps
- Implement Load Balancer + Identity-Aware Proxy (IAP)
- Or adjust organization policy to allow authenticated access

## Sprint Planning Considerations

### Sprint 1 Focus (Immediate Priority)
**Goal**: Resolve the organization policy blocker and restore API connectivity

**Features**:
1. **Backend**: Implement IAP-compatible authentication or alternative access pattern
2. **Frontend**: Update API client to work with new authentication
3. **Infrastructure**: Configure Load Balancer + IAP or adjust policies

This is critical because the application is currently non-functional due to the 403 errors.

### Future Sprints
- Natural language query interface
- Timeline visualization
- Advanced search
- Export capabilities
- Performance optimization