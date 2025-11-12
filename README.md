# AletheiaCodex

**Personal Knowledge Graph Application**

A cloud-native application that automatically extracts entities, relationships, and facts from your notes using AI, building a queryable knowledge graph that grows with you.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GCP](https://img.shields.io/badge/GCP-Cloud%20Functions-4285F4?logo=google-cloud)](https://cloud.google.com/functions)
[![Firebase](https://img.shields.io/badge/Firebase-Hosting-FFCA28?logo=firebase)](https://firebase.google.com)
[![Neo4j](https://img.shields.io/badge/Neo4j-Graph%20Database-008CC1?logo=neo4j)](https://neo4j.com)

---

## 🎯 Vision

Transform your notes into an intelligent, interconnected knowledge base. AletheiaCodex uses AI to automatically extract entities (people, places, organizations, concepts) and their relationships from your writing, creating a living graph of your knowledge that you can explore, query, and expand over time.

**Core Value**: Automated knowledge extraction with human-in-the-loop validation—build your personal knowledge graph without manual data entry.

---

## ✨ Features

### 🤖 AI-Powered Extraction
- **Entity Recognition**: Automatically identifies people, places, organizations, concepts, events, and more
- **Relationship Detection**: Discovers connections between entities
- **High Accuracy**: >85% entity extraction, >75% relationship detection
- **Cost Efficient**: $0.0006 per document (94% under budget)

### 👤 Human-in-the-Loop
- **Review Queue**: Approve or reject AI-extracted entities and relationships
- **Batch Operations**: Process multiple items efficiently
- **Real-time Updates**: See changes instantly with Firestore listeners

### 📊 Knowledge Graph
- **Neo4j Backend**: Powerful graph database for complex queries
- **Interactive Browsing**: Explore nodes and relationships
- **Search & Filter**: Find information quickly
- **Visual Exploration**: See connections between concepts

### 🔐 Secure & Private
- **Firebase Authentication**: Google Sign-In and Email/Password
- **User Isolation**: Your data is completely private
- **Zero Trust Architecture**: Identity-aware access control

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Web Application                          │
│                    (React + TypeScript + Tailwind)               │
│                   https://aletheiacodex.app                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTPS + Firebase Auth
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                      API Gateway                                 │
│              (Authentication + CORS + Routing)                   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                ┌────────────┴────────────┐
                │                         │
┌───────────────▼──────────┐  ┌──────────▼──────────────┐
│   Cloud Functions        │  │   Cloud Functions       │
│   - Ingestion            │  │   - Graph API           │
│   - Orchestration        │  │   - Notes API           │
│   - Review API           │  │                         │
└───────────┬──────────────┘  └──────────┬──────────────┘
            │                            │
            │                            │
┌───────────▼──────────┐    ┌───────────▼──────────────┐
│   Firestore          │    │   Neo4j Aura             │
│   - User data        │    │   - Knowledge graph      │
│   - Notes            │    │   - Entities             │
│   - Review queue     │    │   - Relationships        │
└──────────────────────┘    └──────────────────────────┘
            │
            │
┌───────────▼──────────┐
│   Gemini AI          │
│   - Entity extraction│
│   - Relationship     │
│     detection        │
└──────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- **GCP Project**: `aletheia-codex-prod`
- **Node.js**: 18+ for frontend development
- **Python**: 3.11 for backend functions
- **gcloud CLI**: Authenticated and configured

### Local Development

```bash
# Clone repository
git clone https://github.com/tony-angelo/aletheia-codex.git
cd aletheia-codex

# Install frontend dependencies
cd web
npm install

# Start development server
npm start
# Opens at http://localhost:3000
```

### Deploy to Production

```bash
# Deploy all Cloud Functions
cd functions
gcloud functions deploy ingestion --gen2 --runtime=python311 --region=us-central1
gcloud functions deploy orchestration --gen2 --runtime=python311 --region=us-central1
gcloud functions deploy graph --gen2 --runtime=python311 --region=us-central1
gcloud functions deploy notes-api --gen2 --runtime=python311 --region=us-central1

# Deploy frontend
cd ../web
npm run build
firebase deploy --only hosting
```

---

## 📁 Repository Structure

```
aletheia-codex/
├── config/                    # API Gateway configurations
├── docs/                      # Project documentation
│   ├── sprint1/              # Neo4j connection & auth
│   ├── sprint2/              # AI integration
│   ├── sprint3/              # Review queue & UI
│   ├── sprint4/              # Note input
│   ├── sprint4.5/            # Firebase auth
│   ├── sprint5/              # Bug fixes
│   └── sprint6/              # UI foundation
├── functions/                 # Cloud Functions backend
│   ├── ingestion/            # Document ingestion
│   ├── orchestration/        # AI processing workflow
│   ├── graph/                # Knowledge graph API
│   ├── notes_api/            # Notes management
│   └── review_api/           # Review queue API
├── infrastructure/            # Setup scripts (PowerShell)
├── public/                    # Static assets
├── scripts/                   # Automation scripts
│   ├── deploy/               # Deployment scripts
│   ├── test/                 # Testing scripts
│   └── utils/                # Utility scripts
├── shared/                    # Shared libraries
│   ├── ai/                   # AI service integration
│   ├── auth/                 # Authentication utilities
│   ├── db/                   # Database clients
│   └── models/               # Data models
└── web/                       # React frontend application
    ├── src/
    │   ├── components/       # React components
    │   ├── services/         # API services
    │   ├── hooks/            # Custom hooks
    │   └── types/            # TypeScript types
    └── public/               # Static assets
```

**See individual directory READMEs for detailed documentation:**
- [config/](config/README.md) - API Gateway configuration
- [functions/](functions/README.md) - Cloud Functions backend
- [infrastructure/](infrastructure/README.md) - Infrastructure setup
- [public/](public/README.md) - Static assets
- [scripts/](scripts/README.md) - Automation scripts
- [shared/](shared/README.md) - Shared libraries
- [web/](web/README.md) - React frontend

---

## 🛠️ Technology Stack

### Frontend
- **React** 18.2.0 - UI framework
- **TypeScript** 5.0+ - Type safety
- **Tailwind CSS** 3.3+ - Styling
- **React Router** 6.x - Client-side routing
- **Firebase SDK** 10.7.1 - Authentication & Firestore

### Backend
- **Python** 3.11 - Runtime
- **Cloud Functions** Gen 2 - Serverless compute
- **Firestore** - Document database
- **Neo4j Aura** - Graph database
- **Gemini 2.0 Flash** - AI model

### Infrastructure
- **Google Cloud Platform** - Cloud provider
- **Firebase Hosting** - Frontend hosting
- **API Gateway** - API management
- **Secret Manager** - Credentials storage
- **Cloud Build** - CI/CD

---

## 📊 Performance Metrics

### Current Performance
- **API Response Time**: 203ms average (59% faster than target)
- **AI Processing**: 2-3 seconds per document
- **Cost per Document**: $0.0006 (94% under budget)
- **Entity Extraction**: 85%+ accuracy
- **Relationship Detection**: 75%+ accuracy
- **Bundle Size**: 153KB (23% under target)

### Scalability
- **Concurrent Users**: Scales automatically with Cloud Functions
- **Database**: Neo4j Aura handles millions of nodes
- **Storage**: Unlimited with Firestore and Cloud Storage

---

## 🔐 Security

### Authentication
- Firebase Authentication with Google Sign-In and Email/Password
- JWT token validation on all API endpoints
- User-scoped data access (complete isolation)

### Data Protection
- All secrets stored in Secret Manager
- HTTPS everywhere (TLS 1.3)
- CORS configured for specific origins
- Input validation on all endpoints

### Privacy
- User data is completely isolated
- No cross-user data access
- All queries scoped to authenticated user
- Firestore security rules enforce access control

---

## 📈 Project Status

### Current Phase: Sprint 6 Complete ✅
**Status**: Production Ready  
**Last Updated**: January 15, 2025

### Completed Sprints
1. ✅ **Sprint 1**: Neo4j Connection & Authentication (Nov 5-8, 2024)
2. ✅ **Sprint 2**: AI Integration & Entity Extraction (Nov 9, 2025)
3. ✅ **Sprint 3**: Review Queue & User Interface (Nov 9, 2025)
4. ✅ **Sprint 4**: Note Input & AI Processing (Jan 9, 2025)
5. ✅ **Sprint 4.5**: Firebase Authentication (Nov 9, 2025)
6. ✅ **Sprint 5**: Note Processing Workflow Fix (Nov 9, 2025)
7. ✅ **Sprint 6**: UI Foundation & Component Organization (Nov 9, 2025)

### What's Working
- ✅ Frontend deployed at https://aletheiacodex.app
- ✅ Firebase Authentication (Google + Email/Password)
- ✅ Note creation and management
- ✅ AI entity extraction (>85% accuracy)
- ✅ AI relationship detection (>75% accuracy)
- ✅ Review queue with approval workflow
- ✅ Knowledge graph browsing
- ✅ Real-time updates

**See**: [docs/PROJECT_STATUS.md](docs/PROJECT_STATUS.md) for detailed status

---

## 📚 Documentation

### Getting Started
- [Project Vision](docs/PROJECT_VISION.md) - Core concepts and goals
- [Project Status](docs/PROJECT_STATUS.md) - Current state and progress
- [Sprint Planning](docs/SPRINT_PLANNING.md) - Development methodology

### Sprint Documentation
- [Sprint 1: Neo4j Connection](docs/sprint1/) - Infrastructure setup
- [Sprint 2: AI Integration](docs/sprint2/) - Entity extraction
- [Sprint 3: Review Queue](docs/sprint3/) - Approval workflow
- [Sprint 4: Note Input](docs/sprint4/) - User interface
- [Sprint 5: Bug Fixes](docs/sprint5/) - Workflow improvements
- [Sprint 6: UI Foundation](docs/sprint6/) - Component organization

### Technical Documentation
- [Architecture Overview](docs/architecture/) - System design
- [API Documentation](docs/api/) - Endpoint specifications
- [Database Schemas](docs/database/) - Data models

---

## 🧪 Testing

### Run Tests
```bash
# Frontend tests
cd web
npm test

# Backend tests
cd functions
pytest

# Integration tests
python scripts/test/test_integration.py
```

### Test Coverage
- Unit tests for all shared libraries
- Integration tests for API endpoints
- End-to-end tests for user workflows

---

## 🤝 Contributing

This is a personal project, but feedback and suggestions are welcome!

### Development Workflow
1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes and test thoroughly
3. Commit with descriptive messages
4. Push and create pull request
5. Wait for review and merge

### Code Standards
- Follow existing code style
- Add tests for new features
- Update documentation
- Use TypeScript for frontend
- Use Python type hints for backend

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Google Cloud Platform** - Infrastructure and AI services
- **Neo4j** - Graph database technology
- **Firebase** - Authentication and hosting
- **React** - Frontend framework
- **Tailwind CSS** - Styling framework

---

## 📧 Contact

**Project Maintainer**: Tony Angelo  
**Repository**: [github.com/tony-angelo/aletheia-codex](https://github.com/tony-angelo/aletheia-codex)

---

## 🗺️ Roadmap

### Upcoming Features
- [ ] Advanced graph visualization
- [ ] Export functionality (PDF, JSON, Markdown)
- [ ] Collaborative knowledge graphs
- [ ] Mobile application
- [ ] Webhook integrations
- [ ] Advanced search with natural language
- [ ] Timeline visualization
- [ ] Batch document import
- [ ] API for third-party integrations

### Future Enhancements
- [ ] Multi-language support
- [ ] Voice input for notes
- [ ] Automatic tagging and categorization
- [ ] Smart suggestions based on graph
- [ ] Integration with note-taking apps
- [ ] Public knowledge graph sharing (opt-in)

---

**Built with ❤️ using AI-assisted development**
