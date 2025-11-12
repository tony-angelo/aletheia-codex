# Functions Directory

## Overview
This directory contains the Cloud Functions backend for Aletheia Codex. These serverless functions handle document ingestion, AI processing, knowledge graph management, and API endpoints for the web application.

## Purpose
- Process user-submitted documents and notes
- Extract entities and relationships using AI
- Manage knowledge graph in Neo4j
- Provide REST API for frontend
- Handle authentication and authorization

## Directory Structure
```
functions/
├── README.md                          # This file
├── ingestion/
│   ├── main.py                        # Document ingestion endpoint
│   └── requirements.txt               # Dependencies
├── orchestration/
│   ├── main.py                        # AI orchestration workflow
│   └── requirements.txt               # Dependencies
├── graph/
│   ├── main.py                        # Knowledge graph API
│   └── requirements.txt               # Dependencies
├── notes_api/
│   ├── main.py                        # Notes management API
│   └── requirements.txt               # Dependencies
└── shared/                            # Shared code (symlinked from ../shared/)
    ├── ai/                            # AI service integration
    ├── auth/                          # Authentication utilities
    ├── db/                            # Database clients
    └── models/                        # Data models
```

## Cloud Functions

### 1. Ingestion Function
**Endpoint**: `POST /ingest`
**Purpose**: Accept and validate document uploads

**Features**:
- Accepts text, PDF, and other document formats
- Validates file size and format
- Stores documents in Firestore
- Triggers orchestration workflow

### 2. Orchestration Function
**Endpoint**: `POST /orchestrate`
**Purpose**: Coordinate AI processing workflow

**Performance**:
- **Processing Time**: ~2-3 seconds per document
- **Cost**: $0.0006 per document (94% under budget)
- **Accuracy**: >85% entity extraction, >75% relationships

### 3. Graph Function
**Endpoint**: `GET /graph/nodes`, `GET /graph/node/{id}`
**Purpose**: Query knowledge graph data

### 4. Notes API Function
**Endpoint**: `POST /notes`, `GET /notes`, `GET /notes/{id}`
**Purpose**: Manage user notes

## Technology Stack

### Runtime
- **Python**: 3.11
- **Framework**: Cloud Functions Gen 2
- **Region**: us-central1

### Dependencies
- **google-cloud-firestore**: 2.14.0
- **google-cloud-aiplatform**: 1.38.1
- **neo4j**: 5.15.0
- **firebase-admin**: 6.3.0

## Deployment

### Deploy All Functions
```bash
# Deploy ingestion function
gcloud functions deploy ingestion \
  --gen2 \
  --runtime=python311 \
  --region=us-central1 \
  --trigger-http

# Deploy orchestration function
gcloud functions deploy orchestration \
  --gen2 \
  --runtime=python311 \
  --region=us-central1 \
  --trigger-http
```

## Performance Metrics
- **API Response Time**: 203ms average
- **AI Processing**: 2-3 seconds per document
- **Cost per Document**: $0.0006
- **Accuracy**: 85%+ entity extraction

## Related Documentation
- [Shared Libraries](../shared/README.md)
- [Web Application](../web/README.md)
- [Sprint 2 Documentation](../docs/sprint2/)
