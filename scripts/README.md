# Scripts Directory

## Overview
This directory contains automation scripts for deployment, testing, and maintenance of the Aletheia Codex project.

## Purpose
- Automate deployment workflows
- Facilitate testing and validation
- Provide utility functions
- Simplify maintenance tasks

## Directory Structure
```
scripts/
├── README.md                          # This file
├── deploy/                            # Deployment scripts
├── test/                              # Testing scripts
├── utils/                             # Utility scripts
└── fix/                               # Fix scripts
```

## Deployment Scripts

### deploy-functions.sh
Deploy all Cloud Functions to production

### deploy-frontend.sh
Build and deploy React application

### deploy-all.sh
Deploy complete application stack

## Testing Scripts

### test-api.sh
Test all API endpoints

### test-auth.sh
Validate authentication configuration

### test-integration.py
Run comprehensive integration tests

## Utility Scripts

### backup-firestore.sh
Backup Firestore data

### export-neo4j.sh
Export Neo4j knowledge graph

### clean-logs.sh
Clean old Cloud Function logs

## Best Practices

### Error Handling
- Always use `set -e` in bash scripts
- Implement proper error messages
- Return appropriate exit codes

### Security
- Never hardcode credentials
- Use environment variables
- Validate all inputs

## Related Documentation
- [Functions README](../functions/README.md)
- [Infrastructure README](../infrastructure/README.md)
