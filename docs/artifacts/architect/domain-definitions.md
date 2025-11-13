# Domain Definitions - AletheiaCodex Project

**Document Type**: Architecture Definition  
**Created**: January 2025  
**Author**: Architect Node  
**Status**: Active  

---

## Overview

This document defines the technical domains for the AletheiaCodex project. Each domain represents a distinct area of technical responsibility with clear boundaries, interfaces, and ownership.

The domain structure is based on:
- Repository organization (`functions/`, `web/`, `infrastructure/`)
- Technology stack boundaries (Python backend, React frontend, GCP infrastructure)
- Deployment units (Cloud Functions, Firebase Hosting, GCP resources)
- Functional responsibilities (API services, UI, infrastructure management)

---

## Domain Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                            │
│                   (React + TypeScript)                      │
│                  https://aletheiacodex.app                  │
└────────────────────────────┬────────────────────────────────┘
                             │
                             │ HTTPS REST API
                             │ Firebase Auth Tokens
                             │
┌────────────────────────────▼────────────────────────────────┐
│                         Backend                             │
│                  (Python Cloud Functions)                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │Ingestion │  │Orchestr. │  │Graph API │  │Notes API │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Shared Libraries                       │   │
│  │  AI Services | DB Clients | Models | Auth          │   │
│  └─────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────┘
                             │
                             │ Deployment & Configuration
                             │
┌────────────────────────────▼────────────────────────────────┐
│                      Infrastructure                         │
│              (GCP + Firebase + Deployment)                  │
│  Cloud Functions | Firestore | Neo4j | Firebase Hosting    │
└─────────────────────────────────────────────────────────────┘
```

---

## Domain 1: Backend

### Identification
- **Admin Node**: Admin-Backend
- **Directory**: `[main]/functions/` and `[main]/shared/`
- **Technology**: Python 3.11, Google Cloud Functions Gen 2
- **Deployment Unit**: Cloud Functions (ingestion, orchestration, graph, notes_api, review_api)

### Responsibilities

#### Core Functions
1. **API Endpoints**
   - Implement RESTful API endpoints for frontend
   - Handle HTTP requests and responses
   - Validate request data
   - Return appropriate status codes and error messages

2. **AI Integration**
   - Integrate with Google Gemini API
   - Implement entity extraction logic
   - Implement relationship detection logic
   - Manage AI prompts and responses
   - Handle AI service errors and retries

3. **Database Operations**
   - Firestore CRUD operations for notes, review queue, metadata
   - Neo4j graph operations for entities and relationships
   - Transaction management
   - Data validation and integrity
   - Query optimization

4. **Authentication & Authorization**
   - Firebase Auth token verification
   - User identity extraction
   - Authorization middleware
   - User data isolation

5. **Shared Libraries**
   - Maintain shared Python libraries
   - AI service abstractions
   - Database client abstractions
   - Data models and validation
   - Utility functions

6. **Orchestration Workflow**
   - Coordinate AI processing pipeline
   - Manage document ingestion flow
   - Handle async processing
   - Error handling and recovery

### Key Files and Components

#### Cloud Functions
- `functions/ingestion/main.py` - Document ingestion endpoint
- `functions/orchestration/main.py` - AI processing workflow
- `functions/graph/main.py` - Knowledge graph API
- `functions/notes_api/main.py` - Notes management API
- `functions/review_api/main.py` - Review queue API

#### Shared Libraries
- `shared/ai/` - AI service integration (Gemini)
- `shared/auth/` - Authentication utilities
- `shared/db/` - Database clients (Firestore, Neo4j)
- `shared/models/` - Data models (Note, Entity, Relationship)
- `shared/review/` - Review queue logic
- `shared/utils/` - Utility functions

### Interfaces

#### Outbound (Backend → Frontend)
- **Protocol**: HTTPS REST API
- **Authentication**: Firebase Auth tokens in Authorization header
- **Content-Type**: application/json
- **Endpoints**:
  - `POST /ingest` - Accept document uploads
  - `POST /orchestrate` - Trigger AI processing
  - `GET /graph/nodes` - Query knowledge graph
  - `GET /graph/node/{id}` - Get specific node
  - `POST /notes` - Create note
  - `GET /notes` - List notes
  - `GET /notes/{id}` - Get specific note
  - `GET /review/pending` - Get pending review items
  - `POST /review/approve` - Approve entity/relationship
  - `POST /review/reject` - Reject entity/relationship

#### Outbound (Backend → External Services)
- **Gemini API**: AI entity extraction and relationship detection
- **Firestore**: Document storage and queries
- **Neo4j AuraDB**: Graph database operations via HTTP API

#### Inbound (Frontend → Backend)
- HTTP requests with Firebase Auth tokens
- JSON payloads for data submission

### Dependencies
- **External Services**: Google Gemini API, Neo4j AuraDB, Cloud Firestore
- **Frontend**: Provides API for frontend consumption
- **Infrastructure**: Deployed and configured by Infrastructure domain

### Quality Standards
- **API Response Time**: < 500ms for read operations, < 3s for AI operations
- **Error Handling**: Comprehensive error messages with appropriate HTTP status codes
- **Authentication**: All endpoints require valid Firebase Auth tokens
- **Data Validation**: Validate all input data before processing
- **Testing**: Unit tests for all functions, integration tests for workflows
- **Code Quality**: Type hints, docstrings, PEP 8 compliance
- **Logging**: Structured logging for debugging and monitoring

### Performance Targets
- **Entity Extraction**: > 85% accuracy
- **Relationship Detection**: > 75% accuracy
- **Cost per Document**: < $0.01
- **Processing Time**: < 3 seconds per document
- **API Uptime**: > 99.5%

---

## Domain 2: Frontend

### Identification
- **Admin Node**: Admin-Frontend
- **Directory**: `[main]/web/`
- **Technology**: React, TypeScript, Tailwind CSS
- **Deployment Unit**: Firebase Hosting (https://aletheiacodex.app)

### Responsibilities

#### Core Functions
1. **User Interface Components**
   - Implement React components for all UI elements
   - Maintain component library
   - Ensure responsive design
   - Implement accessibility features

2. **Page Layouts & Routing**
   - Implement page components
   - Configure React Router
   - Handle navigation
   - Manage page state

3. **State Management**
   - Manage application state
   - Handle user session state
   - Implement real-time updates with Firestore listeners
   - Cache data appropriately

4. **API Integration**
   - Integrate with backend API endpoints
   - Handle API requests and responses
   - Implement error handling
   - Manage loading states

5. **Authentication UI**
   - Implement login/signup forms
   - Handle Firebase Auth flows
   - Manage user session
   - Implement protected routes

6. **Real-time Features**
   - Implement Firestore listeners for real-time updates
   - Handle WebSocket connections (if applicable)
   - Update UI in response to data changes

### Key Files and Components

#### Pages
- `web/src/pages/Home.tsx` - Landing page
- `web/src/pages/Notes.tsx` - Note input and management
- `web/src/pages/ReviewQueue.tsx` - Entity/relationship review
- `web/src/pages/KnowledgeGraph.tsx` - Graph visualization
- `web/src/pages/Login.tsx` - Authentication

#### Components
- `web/src/components/NoteInput.tsx` - Chat-like note input
- `web/src/components/ReviewCard.tsx` - Review item card
- `web/src/components/GraphVisualization.tsx` - Graph display
- `web/src/components/Navigation.tsx` - Navigation bar
- `web/src/components/AuthForm.tsx` - Login/signup form

#### Services
- `web/src/services/api.ts` - API client
- `web/src/services/auth.ts` - Authentication service
- `web/src/firebase/config.ts` - Firebase configuration

### Interfaces

#### Outbound (Frontend → Backend)
- **Protocol**: HTTPS REST API
- **Authentication**: Firebase Auth tokens in Authorization header
- **Content-Type**: application/json
- **Base URL**: Cloud Functions endpoints

#### Inbound (User → Frontend)
- User interactions (clicks, form submissions, navigation)
- Browser events

#### Inbound (Backend → Frontend)
- API responses (JSON)
- Real-time updates via Firestore listeners

### Dependencies
- **Backend**: Consumes backend API endpoints
- **Firebase**: Authentication and real-time database
- **Infrastructure**: Deployed and hosted by Infrastructure domain

### Quality Standards
- **Performance**: 
  - First Contentful Paint < 1.5s
  - Time to Interactive < 3s
  - Bundle size < 200KB (gzipped)
- **Accessibility**: WCAG 2.1 Level AA compliance
- **Browser Support**: Modern browsers (Chrome, Firefox, Safari, Edge)
- **Responsive Design**: Mobile-first, works on all screen sizes
- **Code Quality**: 
  - TypeScript strict mode
  - ESLint compliance
  - Component documentation
  - Unit tests for components
- **User Experience**:
  - Clear error messages
  - Loading indicators
  - Optimistic UI updates
  - Smooth transitions

### User Experience Targets
- **Task Completion**: Users can complete core tasks in < 3 clicks
- **Error Recovery**: Clear error messages with actionable guidance
- **Feedback**: Immediate feedback for all user actions
- **Consistency**: Consistent UI patterns across all pages

---

## Domain 3: Infrastructure

### Identification
- **Admin Node**: Admin-Infrastructure
- **Directory**: `[main]/infrastructure/`, `[main]/scripts/`, deployment configs
- **Technology**: Google Cloud Platform, Firebase, deployment scripts
- **Deployment Unit**: GCP resources, Firebase project, deployment pipelines

### Responsibilities

#### Core Functions
1. **Cloud Infrastructure Setup**
   - Configure GCP project
   - Set up Cloud Functions
   - Configure Firestore
   - Set up Neo4j AuraDB connection
   - Manage IAM roles and permissions

2. **Firebase Configuration**
   - Configure Firebase project
   - Set up Firebase Hosting
   - Configure Firebase Authentication
   - Manage security rules

3. **Deployment Automation**
   - Create deployment scripts
   - Automate Cloud Functions deployment
   - Automate frontend deployment
   - Implement CI/CD pipelines (planned)

4. **Environment Management**
   - Manage environment variables
   - Configure secrets in Secret Manager
   - Maintain separate dev/staging/prod environments

5. **Monitoring & Logging**
   - Set up Cloud Logging
   - Configure monitoring dashboards
   - Set up alerts
   - Track performance metrics

6. **Security & Compliance**
   - Implement security best practices
   - Manage API keys and secrets
   - Configure firewall rules
   - Handle organization policies

### Key Files and Components

#### Configuration Files
- `firebase.json` - Firebase configuration
- `firestore.rules` - Firestore security rules
- `storage.rules` - Cloud Storage security rules
- `.firebaserc` - Firebase project configuration
- `infrastructure/` - Infrastructure as code (if applicable)

#### Deployment Scripts
- `scripts/deploy-functions.sh` - Deploy Cloud Functions
- `scripts/deploy-frontend.sh` - Deploy frontend
- `scripts/setup-env.sh` - Environment setup

### Interfaces

#### Outbound (Infrastructure → GCP)
- GCP API calls for resource management
- Firebase CLI commands for deployment

#### Outbound (Infrastructure → Backend)
- Deployment of Cloud Functions
- Configuration of environment variables

#### Outbound (Infrastructure → Frontend)
- Deployment to Firebase Hosting
- Configuration of Firebase project

### Dependencies
- **Backend**: Deploys and configures backend services
- **Frontend**: Deploys and hosts frontend application
- **External Services**: GCP, Firebase, Neo4j AuraDB

### Quality Standards
- **Infrastructure as Code**: All infrastructure defined in code
- **Documentation**: Complete setup and deployment documentation
- **Security**: 
  - Secrets stored in Secret Manager
  - Least privilege IAM roles
  - Security rules enforced
- **Reliability**:
  - Automated deployments
  - Rollback capability
  - Health checks
- **Monitoring**:
  - Comprehensive logging
  - Performance metrics
  - Error tracking
  - Alerting for critical issues

### Operational Targets
- **Deployment Time**: < 5 minutes for full deployment
- **Uptime**: > 99.5% for all services
- **Recovery Time**: < 15 minutes for critical issues
- **Cost Management**: Stay within budget targets

---

## Domain Boundaries

### Clear Separations

1. **Backend ↔ Frontend**
   - Backend does NOT implement UI components
   - Frontend does NOT implement business logic or data processing
   - Communication only through defined REST API

2. **Backend ↔ Infrastructure**
   - Backend does NOT manage deployment or infrastructure
   - Infrastructure does NOT implement application logic
   - Infrastructure provides deployment and configuration

3. **Frontend ↔ Infrastructure**
   - Frontend does NOT manage hosting or deployment
   - Infrastructure does NOT implement UI components
   - Infrastructure provides hosting and configuration

### Integration Points

1. **API Contract**
   - Backend defines and implements API endpoints
   - Frontend consumes API endpoints
   - Infrastructure deploys and exposes endpoints

2. **Authentication**
   - Infrastructure configures Firebase Auth
   - Frontend implements auth UI and flows
   - Backend validates auth tokens

3. **Data Flow**
   - Frontend sends data to Backend via API
   - Backend processes and stores data
   - Backend returns data to Frontend via API
   - Infrastructure ensures connectivity

---

## Admin Node Considerations

### Admin-Backend
- **Primary Focus**: Python code in `functions/` and `shared/`
- **Deployment**: Uses `gcloud functions deploy` commands
- **Testing**: Python unit tests and integration tests
- **Dependencies**: Manages Python requirements.txt files

### Admin-Frontend
- **Primary Focus**: TypeScript/React code in `web/`
- **Deployment**: Uses `firebase deploy --only hosting` command
- **Testing**: Jest/React Testing Library tests
- **Dependencies**: Manages package.json and npm packages

### Admin-Infrastructure
- **Primary Focus**: Configuration files, deployment scripts, GCP setup
- **Deployment**: Executes deployment scripts, manages GCP resources
- **Testing**: Deployment validation, infrastructure tests
- **Dependencies**: Manages GCP resources, Firebase configuration

---

## Cross-Domain Coordination

### Sprint Planning
- Architect assigns features to appropriate domains
- Features may span multiple domains (e.g., new API endpoint requires Backend + Frontend work)
- Admin nodes coordinate through Architect for cross-domain features

### Integration Testing
- Backend provides API documentation for Frontend
- Frontend provides UI mockups for Backend API design
- Infrastructure ensures both can communicate

### Deployment Coordination
- Infrastructure deploys Backend first
- Infrastructure deploys Frontend after Backend is verified
- Rollback procedures coordinate across domains

---

## Version History

**v1.0.0** - Initial domain definitions
- Defined three domains: Backend, Frontend, Infrastructure
- Established domain boundaries and interfaces
- Documented responsibilities and quality standards
- Created Admin node mapping

---

**End of Domain Definitions**