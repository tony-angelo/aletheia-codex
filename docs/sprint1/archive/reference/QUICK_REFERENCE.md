# Sprint 1 Quick Reference Guide

**Last Updated**: November 8, 2025  
**Status**: 95% Complete  
**For**: Quick access to key information

---

## 🎯 Current Status

### Sprint 1 Completion: 95%

**What's Complete**:
- ✅ All infrastructure deployed and verified
- ✅ IAM permissions configured
- ✅ Test scripts created (Bash + PowerShell)
- ✅ Comprehensive documentation
- ✅ Service account documented

**What's Remaining** (5%):
- ⚠️ Resume Neo4j Aura instance (5 minutes)
- ⚠️ Retest orchestration function (10 minutes)
- ⚠️ Verify graph data creation (optional)

---

## 🔑 Key Information

### GCP Project
- **Project ID**: aletheia-codex-prod
- **Project Number**: 679360092359
- **Region**: us-central1

### Cloud Functions
- **Ingestion**: https://us-central1-aletheia-codex-prod.cloudfunctions.net/ingestion
- **Orchestrate**: https://us-central1-aletheia-codex-prod.cloudfunctions.net/orchestrate

### Service Account
- **Email**: superninja@aletheia-codex-prod.iam.gserviceaccount.com
- **Roles**: Cloud Functions Invoker, Cloud Functions Viewer, Cloud Run Invoker, Logs Viewer, Secret Manager Secret Accessor

### Neo4j
- **URI**: neo4j+s://ac286c9e.databases.neo4j.io
- **Password**: 44 characters in Secret Manager (NEO4J_PASSWORD)
- **Console**: https://console.neo4j.io

---

## 🚀 Quick Commands

### Authentication
```bash
# Authenticate with service account
gcloud auth activate-service-account --key-file=service-account-key.json

# Set project
gcloud config set project aletheia-codex-prod

# Get identity token
gcloud auth print-identity-token
```

### Check Function Status
```bash
# List all functions
gcloud functions list --region=us-central1

# Check orchestrate function
gcloud functions describe orchestrate --region=us-central1
```

### Test Document Creation
```bash
token=$(gcloud auth print-identity-token)

curl -X POST \
  -H "Authorization: Bearer $token" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test","content":"Test content","source":"test"}' \
  https://us-central1-aletheia-codex-prod.cloudfunctions.net/ingestion
```

### Trigger Orchestration
```bash
token=$(gcloud auth print-identity-token)

curl -X POST \
  -H "Authorization: Bearer $token" \
  -H "Content-Type: application/json" \
  -d '{"document_id":"YOUR_DOC_ID","action":"process_document"}' \
  https://us-central1-aletheia-codex-prod.cloudfunctions.net/orchestrate
```

### Check Logs
```bash
# Orchestrate function logs
gcloud logging read "resource.type=cloud_function AND resource.labels.function_name=orchestrate" \
  --limit=20 --freshness=10m

# Ingestion function logs
gcloud logging read "resource.type=cloud_function AND resource.labels.function_name=ingestion" \
  --limit=20 --freshness=10m
```

### Check Secrets
```bash
# Neo4j password
gcloud secrets versions access latest --secret="NEO4J_PASSWORD"

# Neo4j URI
gcloud secrets versions access latest --secret="NEO4J_URI"
```

---

## 🧪 Run Test Scripts

### Bash (Linux/Mac)
```bash
cd aletheia-codex
./scripts/testing/test_orchestration_neo4j.sh
```

### PowerShell (Windows)
```powershell
cd aletheia-codex
./scripts/testing/test_orchestration_neo4j.ps1
```

---

## ⚠️ Known Issues

### Issue 1: Neo4j Connection Failure
- **Error**: "503 Illegal metadata"
- **Cause**: Neo4j Aura instance paused (free tier auto-pauses)
- **Fix**: 
  1. Go to https://console.neo4j.io
  2. Find instance and click "Resume"
  3. Wait 1-2 minutes
  4. Retry operation

### Issue 2: 403 Forbidden on Orchestrate
- **Error**: "Permission denied"
- **Cause**: Missing Cloud Run Invoker role
- **Fix**: Already resolved - role added to service account

### Issue 3: Invalid JSON Payload
- **Error**: "Invalid JSON payload"
- **Cause**: Shell escaping issues with curl
- **Fix**: Create JSON file and use `curl -d @file.json`

---

## 📚 Documentation Links

### Core Documents
- **Implementation Report**: `docs/sprint1/IMPLEMENTATION_COMPLETION_REPORT.md`
- **Worker Thread Report**: `docs/sprint1/SPRINT1_WORKER_THREAD_COMPLETION_REPORT.md`
- **Documentation Index**: `docs/sprint1/DOCUMENTATION_INDEX.md`

### Test Scripts
- **Bash**: `scripts/testing/test_orchestration_neo4j.sh`
- **PowerShell**: `scripts/testing/test_orchestration_neo4j.ps1`

### Troubleshooting
- **Neo4j Issues**: `docs/sprint1/TROUBLESHOOTING_NEO4J.md`
- **Quick Fixes**: `docs/sprint1/QUICK_FIX_GUIDE.md`

---

## 🔗 Console Links

### GCP
- [Functions](https://console.cloud.google.com/functions?project=aletheia-codex-prod)
- [Logs](https://console.cloud.google.com/logs?project=aletheia-codex-prod)
- [Secrets](https://console.cloud.google.com/security/secret-manager?project=aletheia-codex-prod)
- [Firestore](https://console.cloud.google.com/firestore?project=aletheia-codex-prod)

### Neo4j
- [Aura Console](https://console.neo4j.io)

### GitHub
- [Repository](https://github.com/tony-angelo/aletheia-codex)
- [Pull Request #1](https://github.com/tony-angelo/aletheia-codex/pull/1)

---

## 🎯 Next Actions

### To Complete Sprint 1 (100%)
1. Resume Neo4j Aura instance (5 min)
2. Retest orchestration function (10 min)
3. Verify graph data (optional, 10 min)

### For Sprint 2 Preparation
1. Review Sprint 2 requirements
2. Design Neo4j schema for entities
3. Set up Gemini API access
4. Plan entity extraction approach

---

## 📞 Support

### For Issues
1. Check this quick reference
2. Review troubleshooting docs
3. Check completion reports for detailed info
4. Review GitHub issues

### For Questions
- Check documentation index for relevant docs
- Review implementation completion report
- Check existing Sprint 1 documentation

---

**Quick Reference Maintained By**: SuperNinja AI Worker Thread  
**Last Updated**: November 8, 2025  
**Sprint**: Sprint 1 - Neo4j Connectivity & Production Readiness
