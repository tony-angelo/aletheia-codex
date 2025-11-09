# Sprint 4 Deployment Guide

## Overview
This guide provides step-by-step instructions for deploying Sprint 4: Note Input & AI Processing to production.

## Prerequisites
- gcloud CLI installed and authenticated
- Firebase CLI installed and authenticated
- Access to aletheia-codex GCP project
- Node.js 18+ installed

## Deployment Order
Deploy in this specific order to ensure dependencies are met:

1. Firestore Rules & Indexes
2. Orchestration Function (updated)
3. Notes API Function (new)
4. Frontend Application

## 1. Deploy Firestore Rules & Indexes

### Firestore Security Rules
```bash
cd aletheia-codex
firebase deploy --only firestore:rules
```

**Verification**:
```bash
# Check rules in Firebase Console
# Navigate to: Firestore Database > Rules
# Verify 'notes' collection rules are present
```

### Firestore Indexes
```bash
firebase deploy --only firestore:indexes
```

**Verification**:
```bash
# Check indexes in Firebase Console
# Navigate to: Firestore Database > Indexes
# Verify 3 new indexes for 'notes' collection
```

## 2. Deploy Orchestration Function (Updated)

### Update Environment Variables
```bash
cd functions/orchestration

# Verify environment variables
gcloud functions describe orchestration \
  --region=us-central1 \
  --format="value(environmentVariables)"
```

### Deploy Function
```bash
gcloud functions deploy orchestration \
  --gen2 \
  --runtime=python311 \
  --region=us-central1 \
  --source=. \
  --entry-point=orchestrate \
  --trigger-http \
  --allow-unauthenticated \
  --timeout=540s \
  --memory=512MB \
  --set-env-vars GCP_PROJECT=aletheia-codex,NEO4J_URI=<uri>,NEO4J_USER=<user>,NEO4J_PASSWORD=<password>,GEMINI_API_KEY=<key>
```

**Verification**:
```bash
# Test with curl
curl -X POST https://us-central1-aletheia-codex.cloudfunctions.net/orchestration \
  -H "Content-Type: application/json" \
  -d '{
    "noteId": "test-note-123",
    "content": "Test note for deployment verification",
    "userId": "test-user"
  }'

# Expected: 200 response with extraction summary
```

## 3. Deploy Notes API Function (New)

### Create Shared Directory Symlink
```bash
cd functions/notes_api
ln -s ../orchestration/shared shared
```

### Deploy Function
```bash
gcloud functions deploy notes_api \
  --gen2 \
  --runtime=python311 \
  --region=us-central1 \
  --source=. \
  --entry-point=notes_api \
  --trigger-http \
  --allow-unauthenticated \
  --timeout=60s \
  --memory=256MB \
  --set-env-vars GCP_PROJECT=aletheia-codex
```

**Verification**:
```bash
# Test GET endpoint
curl -X GET https://us-central1-aletheia-codex.cloudfunctions.net/notes_api/notes \
  -H "Authorization: Bearer test-user"

# Expected: 200 response with notes array
```

## 4. Deploy Frontend Application

### Update Environment Variables
Create/update `.env.production`:
```bash
cd web
cat > .env.production << EOF
REACT_APP_FIREBASE_API_KEY=<key>
REACT_APP_FIREBASE_AUTH_DOMAIN=aletheia-codex.firebaseapp.com
REACT_APP_FIREBASE_PROJECT_ID=aletheia-codex
REACT_APP_FIREBASE_STORAGE_BUCKET=aletheia-codex.appspot.com
REACT_APP_FIREBASE_MESSAGING_SENDER_ID=<id>
REACT_APP_FIREBASE_APP_ID=<id>
REACT_APP_ORCHESTRATION_URL=https://us-central1-aletheia-codex.cloudfunctions.net/orchestration
EOF
```

### Build Application
```bash
npm run build
```

**Verification**:
```bash
# Check build output
ls -lh build/
# Should see optimized production files
```

### Deploy to Firebase Hosting
```bash
firebase deploy --only hosting
```

**Verification**:
```bash
# Visit production URL
open https://aletheia-codex.web.app

# Verify:
# - Page loads without errors
# - Navigation works
# - Can access Notes page
```

## Post-Deployment Verification

### 1. Smoke Tests
Run these tests immediately after deployment:

```bash
# Test 1: Frontend loads
curl -I https://aletheia-codex.web.app
# Expected: 200 OK

# Test 2: Orchestration function responds
curl -X POST https://us-central1-aletheia-codex.cloudfunctions.net/orchestration \
  -H "Content-Type: application/json" \
  -d '{"noteId":"test","content":"test","userId":"test"}'
# Expected: 200 with JSON response

# Test 3: Notes API responds
curl https://us-central1-aletheia-codex.cloudfunctions.net/notes_api/notes \
  -H "Authorization: Bearer test"
# Expected: 200 with JSON response
```

### 2. Functional Tests
Perform these manual tests in production:

1. **Note Submission**
   - Navigate to Notes page
   - Submit a test note
   - Verify processing starts
   - Wait for completion
   - Check review queue for extracted items

2. **Navigation**
   - Click through all navigation links
   - Verify each page loads correctly
   - Check browser console for errors

3. **Real-time Updates**
   - Open app in two tabs
   - Submit note in one tab
   - Verify it appears in other tab

### 3. Monitor Logs
```bash
# Orchestration function logs
gcloud functions logs read orchestration \
  --region=us-central1 \
  --limit=50

# Notes API logs
gcloud functions logs read notes_api \
  --region=us-central1 \
  --limit=50

# Check for errors
gcloud functions logs read orchestration \
  --region=us-central1 \
  --filter="severity>=ERROR" \
  --limit=20
```

### 4. Performance Check
```bash
# Check function execution times
gcloud functions logs read orchestration \
  --region=us-central1 \
  --format="value(timestamp,executionId,resource.labels.function_name)" \
  --limit=10

# Monitor costs
gcloud billing accounts list
```

## Rollback Procedures

### If Frontend Issues
```bash
# Rollback to previous version
firebase hosting:rollback

# Or deploy specific version
firebase deploy --only hosting --version <previous-version>
```

### If Function Issues
```bash
# Rollback orchestration function
gcloud functions deploy orchestration \
  --source=<previous-version-path> \
  --region=us-central1

# Or disable function temporarily
gcloud functions delete orchestration --region=us-central1
```

### If Firestore Rules Issues
```bash
# Restore previous rules from backup
firebase deploy --only firestore:rules --config firebase.backup.json
```

## Troubleshooting

### Common Issues

**Issue**: Frontend can't connect to functions
- Check CORS settings in functions
- Verify environment variables
- Check network tab in browser DevTools

**Issue**: Firestore permission denied
- Verify rules are deployed
- Check user authentication
- Verify userId matches in rules

**Issue**: Function timeout
- Check function logs for bottlenecks
- Increase timeout if needed
- Optimize code

**Issue**: High costs
- Check function invocation count
- Review Gemini API usage
- Implement rate limiting

## Success Criteria
- [ ] All functions deployed successfully
- [ ] Frontend deployed and accessible
- [ ] Firestore rules and indexes active
- [ ] Smoke tests pass
- [ ] Functional tests pass
- [ ] No critical errors in logs
- [ ] Performance acceptable (< 30s processing)
- [ ] Costs within budget

## Deployment Checklist
- [ ] Backup current production state
- [ ] Deploy Firestore rules
- [ ] Deploy Firestore indexes
- [ ] Deploy orchestration function
- [ ] Deploy notes_api function
- [ ] Build frontend
- [ ] Deploy frontend
- [ ] Run smoke tests
- [ ] Run functional tests
- [ ] Monitor logs for 1 hour
- [ ] Update documentation
- [ ] Notify team of deployment