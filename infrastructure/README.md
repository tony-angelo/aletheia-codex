# Infrastructure Directory

## Overview
This directory contains infrastructure setup scripts and configuration for the Aletheia Codex project. These PowerShell scripts automate the provisioning of Google Cloud Platform resources, Firebase services, and Neo4j database.

## Purpose
- Automate GCP project setup
- Configure Firebase services
- Provision Neo4j Aura database
- Set up IAM permissions
- Configure Secret Manager
- Enable required APIs

## Directory Structure
```
infrastructure/
├── README.md                          # This file
├── setup-gcp-project.ps1              # Main GCP setup script
├── setup-firebase.ps1                 # Firebase configuration
├── setup-neo4j.ps1                    # Neo4j Aura setup
├── setup-secrets.ps1                  # Secret Manager configuration
└── setup-iam.ps1                      # IAM roles and permissions
```

## Setup Scripts

### 1. setup-gcp-project.ps1
**Purpose**: Initialize Google Cloud Platform project

**Usage**:
```powershell
.\setup-gcp-project.ps1 -ProjectId "aletheia-codex-prod" -BillingAccountId "BILLING_ID"
```

### 2. setup-firebase.ps1
**Purpose**: Configure Firebase services

**Usage**:
```powershell
.\setup-firebase.ps1 -ProjectId "aletheia-codex-prod"
```

### 3. setup-secrets.ps1
**Purpose**: Configure Secret Manager

**Secrets Created**:
- `NEO4J_URI` - Neo4j connection string
- `NEO4J_USER` - Neo4j username
- `NEO4J_PASSWORD` - Neo4j password
- `GEMINI_API_KEY` - Google AI API key

## Complete Setup Workflow

```powershell
# 1. Set up GCP project
.\setup-gcp-project.ps1 -ProjectId "aletheia-codex-prod"

# 2. Configure Firebase
.\setup-firebase.ps1 -ProjectId "aletheia-codex-prod"

# 3. Set up IAM
.\setup-iam.ps1 -ProjectId "aletheia-codex-prod"

# 4. Configure secrets
.\setup-secrets.ps1 -ProjectId "aletheia-codex-prod"
```

## Required APIs
- Cloud Functions API
- Cloud Run API
- Firestore API
- Secret Manager API
- Cloud Build API
- API Gateway API

## Cost Estimation
**Monthly Costs (Approximate)**:
- Cloud Functions: $5-20
- Firestore: $1-10
- Neo4j Aura: $0 (free tier) or $65+
- Secret Manager: $0.06 per secret
- **Total**: $10-100/month

## Related Documentation
- [Functions README](../functions/README.md)
- [Sprint 1 Documentation](../docs/sprint1/)
- [Project Status](../docs/PROJECT_STATUS.md)
