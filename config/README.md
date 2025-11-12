# Config Directory

## Overview
This directory contains API Gateway configuration files for the Aletheia Codex backend services. These configurations define how external requests are routed to Cloud Functions through Google Cloud API Gateway.

## Purpose
- Define API endpoints and routing rules
- Configure authentication and CORS policies
- Manage API versioning and deployment
- Enable secure access to backend functions

## Directory Structure
```
config/
├── README.md                      # This file
├── api-gateway-config.yaml        # v1 - Initial configuration
├── api-gateway-config-v2.yaml     # v2 - Enhanced with CORS
└── api-gateway-config-v5.yaml     # v5 - Current production config
```

## Configuration Files

### api-gateway-config-v5.yaml (Current Production)
The active production configuration with:
- **Authentication**: Firebase ID token validation
- **CORS Support**: Full cross-origin resource sharing
- **Endpoints**:
  - `POST /ingest` - Document ingestion
  - `POST /orchestrate` - AI orchestration
  - `GET /review` - Review queue retrieval
  - `POST /review/approve` - Entity approval
  - `POST /review/reject` - Entity rejection
  - `GET /graph/nodes` - Knowledge graph nodes
  - `GET /graph/node/{id}` - Node details

### api-gateway-config-v2.yaml
Enhanced version with CORS headers and improved error handling.

### api-gateway-config.yaml
Original configuration - kept for reference.

## Key Features

### Authentication
All endpoints require Firebase Authentication:
```yaml
securityDefinitions:
  firebase:
    authorizationUrl: ""
    flow: "implicit"
    type: "oauth2"
    x-google-issuer: "https://securetoken.google.com/aletheia-codex-prod"
```

### CORS Configuration
Supports cross-origin requests from the web application:
```yaml
x-google-backend:
  cors:
    allow_origins: ["https://aletheiacodex.app"]
    allow_methods: ["GET", "POST", "OPTIONS"]
    allow_headers: ["Authorization", "Content-Type"]
```

## Deployment

### Deploy Configuration
```bash
# Deploy API Gateway configuration
gcloud api-gateway api-configs create CONFIG_ID \
  --api=aletheia-codex-api \
  --openapi-spec=config/api-gateway-config-v5.yaml \
  --project=aletheia-codex-prod

# Update gateway
gcloud api-gateway gateways update aletheia-codex-gateway \
  --api=aletheia-codex-api \
  --api-config=CONFIG_ID \
  --location=us-central1
```

## Integration Points
- **Frontend**: React app calls API Gateway endpoints
- **Backend**: Cloud Functions receive authenticated requests
- **Security**: Firebase tokens validated at gateway level

## Related Documentation
- [Functions README](../functions/README.md) - Backend implementation
- [Web README](../web/README.md) - Frontend integration
- [Sprint 6 Documentation](../docs/sprint6/) - Implementation details
