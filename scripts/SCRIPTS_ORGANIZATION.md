# Scripts Organization

## Directory Structure

```
scripts/
├── deployment/           # Deployment and setup scripts
├── testing/             # Testing and verification scripts
├── troubleshooting/     # Diagnostic and fix scripts
└── SCRIPTS_ORGANIZATION.md
```

## Deployment Scripts
Location: `scripts/deployment/`

- `deploy_all_functions.ps1` - Deploy all Cloud Functions
- `deploy_ingestion_standalone.ps1` - Deploy standalone ingestion function
- `cleanup_and_deploy_ingestion.ps1` - Clean up and redeploy ingestion
- `redeploy_ingestion_fixed.ps1` - Redeploy with fixed standalone version

## Testing Scripts
Location: `scripts/testing/`

- `test_sprint1_deployment.ps1` - Comprehensive Sprint 1 test suite
- `test_ingestion_authenticated.ps1` - Test ingestion with authentication

## Troubleshooting Scripts
Location: `scripts/troubleshooting/`

- `fix_neo4j_secrets.ps1` - Fix Neo4j password in Secret Manager
- `manual_fix_password.ps1` - Manually update Neo4j password
- `fix_ingestion_permissions.ps1` - Fix function IAM permissions
- `fix_service_account_permissions.ps1` - Fix service account permissions
- `apply_neo4j_fix.ps1` - Apply Neo4j client fixes

## Archived Scripts
Location: `scripts/archived/`

These scripts were used during development but are superseded by newer versions:

- `fix_ingestion_deployment.ps1` - Superseded by redeploy_ingestion_fixed.ps1
- `fix_ingestion_deployment_v2.ps1` - Superseded by redeploy_ingestion_fixed.ps1

## Usage Guidelines

### Deployment
1. Use `deploy_all_functions.ps1` for initial deployment
2. Use `redeploy_ingestion_fixed.ps1` if ingestion needs redeployment

### Testing
1. Run `test_sprint1_deployment.ps1` for comprehensive testing
2. Use `test_ingestion_authenticated.ps1` for quick ingestion verification

### Troubleshooting
1. Use `fix_service_account_permissions.ps1` if getting 403 errors
2. Use `fix_neo4j_secrets.ps1` if Neo4j password is corrupted
3. Use `manual_fix_password.ps1` for manual password updates

## Documentation
All scripts are documented in:
- `docs/sprint1/SPRINT1_COMPLETE_GUIDE.md` - Master documentation
- Individual script headers contain usage instructions
