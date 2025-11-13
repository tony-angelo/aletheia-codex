# Admin-Frontend Sprint 1 Initialization

**Date**: 2025-01-18  
**From**: Architect  
**To**: Admin-Frontend  
**Sprint**: Sprint 1 - API Access Restoration  
**Priority**: HIGH  

---

## 🎯 Mission Overview

You are the **Admin-Frontend** node for Sprint 1. Both Admin-Infrastructure and Admin-Backend have successfully completed their work. Your mission is to update the frontend to use the new Load Balancer URL and verify end-to-end functionality.

**Critical Context**: The infrastructure is operational and backend authentication is implemented. Your work is the final piece to restore full application functionality for users.

---

## ✅ What's Already Complete

### Infrastructure (Admin-Infrastructure) ✅
- ✅ Load Balancer operational at **https://aletheiacodex.app**
- ✅ IAP enabled on all 6 backend services
- ✅ SSL certificate active
- ✅ DNS configured (aletheiacodex.app → 34.120.185.233)
- ✅ Routing configured for all API endpoints
- ✅ Monitoring documented

### Backend (Admin-Backend) ✅
- ✅ IAP authentication implemented in all Cloud Functions
- ✅ Unified authentication module created (`shared/auth/unified_auth.py`)
- ✅ All functions updated to use IAP authentication
- ✅ 28 unit tests written and passing
- ✅ 94%+ code coverage
- ✅ Backward compatible with Firebase Auth

### API Routing Table
| Path | Backend Service | Cloud Function | Status |
|------|----------------|----------------|--------|
| `/api/ingest` | backend-ingestion | ingestion | ✅ Ready |
| `/api/orchestrate` | backend-orchestration | orchestration | ✅ Ready |
| `/api/graph/*` | backend-graphfunction | graphfunction | ✅ Ready |
| `/api/notes/*` | backend-notesapifunction | notesapifunction | ✅ Ready |
| `/api/review/*` | backend-reviewapifunction | reviewapifunction | ✅ Ready |

---

## 🔐 Authentication Setup Required

### Step 1: Authenticate with GCP

```bash
# Navigate to repository
cd aletheia-codex

# Authenticate using SuperNinja service account
gcloud auth activate-service-account --key-file=/workspace/aletheia-codex-prod-af9a64a7fcaa.json
gcloud config set project aletheia-codex-prod

# Verify authentication
gcloud auth list
```

### Step 2: Checkout Sprint Branch

```bash
# Checkout sprint-1 branch (shared by all Admin nodes)
git checkout sprint-1

# Pull latest changes (includes Infrastructure and Backend work)
git pull origin sprint-1

# Verify you can see previous work
ls infrastructure/load-balancer/
ls infrastructure/monitoring/
ls shared/auth/
ls functions/
```

**Important**: All Admin nodes work on the same `sprint-1` branch. This means:
- ✅ You can see Admin-Infrastructure's Load Balancer configuration
- ✅ You can see Admin-Backend's authentication implementation
- ✅ Your changes will complete the Sprint 1 integration
- ⚠️ Work in the `web/` directory to avoid conflicts

---

## 📋 Your Prime Directive

**Location**: `[artifacts]/admin-frontend/admin-frontend.txt`

Read your complete prime directive before beginning work. It contains:
- Your role and responsibilities
- Technical domain ownership
- Communication protocols
- Standards and best practices

---

## 📖 Sprint 1 Guide

**Location**: `[artifacts]/admin-frontend/inbox/sprint-1-guide.md`

Your Sprint 1 guide contains:
- Detailed feature requirements
- Acceptance criteria
- Implementation guidance
- Testing procedures

---

## 🎯 Your Sprint 1 Tasks

### Priority 1: Update API Client Configuration (CRITICAL)

**Objective**: Change API base URL from direct Cloud Functions to Load Balancer

**What You Need to Do**:

1. **Locate API Configuration** (15 minutes)
   - Find where API base URL is configured
   - Likely in: `web/src/config/`, `web/src/api/`, or environment files
   - Document current configuration

2. **Update API Base URL** (30 minutes)
   ```javascript
   // OLD (Direct Cloud Functions URLs)
   const API_BASE = 'https://us-central1-aletheia-codex-prod.cloudfunctions.net';
   
   // NEW (Load Balancer URL)
   const API_BASE = 'https://aletheiacodex.app';
   ```

3. **Update All API Endpoints** (1 hour)
   ```javascript
   // Ingestion
   const INGEST_URL = `${API_BASE}/api/ingest`;
   
   // Orchestration
   const ORCHESTRATE_URL = `${API_BASE}/api/orchestrate`;
   
   // Graph
   const GRAPH_URL = `${API_BASE}/api/graph`;
   
   // Notes
   const NOTES_URL = `${API_BASE}/api/notes`;
   
   // Review
   const REVIEW_URL = `${API_BASE}/api/review`;
   ```

4. **Update Environment Variables** (15 minutes)
   - Update `.env` files (development, production)
   - Update any hardcoded URLs in the codebase
   - Ensure consistent configuration across environments

### Priority 2: Test Integration (CRITICAL)

**Objective**: Verify all frontend functionality works with Load Balancer

**What You Need to Do**:

1. **Local Testing** (1 hour)
   ```bash
   # Start local development server
   cd web
   npm install
   npm run dev
   
   # Test in browser
   # - Login with Firebase Auth
   # - Test all API calls
   # - Verify data loads correctly
   # - Check browser console for errors
   ```

2. **Test Each Feature** (1-2 hours)
   - **Document Ingestion**: Upload and process documents
   - **Entity Extraction**: Verify entities are extracted
   - **Knowledge Graph**: View and navigate graph
   - **Notes**: Create, read, update, delete notes
   - **Review Queue**: Review and approve entities

3. **Test Authentication Flow** (30 minutes)
   - Login with Firebase Auth
   - Verify token is sent to backend
   - Verify IAP validates token
   - Verify user identity is correct
   - Test logout and re-login

4. **Test Error Handling** (30 minutes)
   - Test with invalid token (should show error)
   - Test with expired token (should refresh)
   - Test network errors (should show user-friendly message)
   - Test API errors (should display appropriately)

### Priority 3: Deploy Updated Frontend (CRITICAL)

**Objective**: Deploy frontend to Firebase Hosting

**What You Need to Do**:

1. **Build Production Bundle** (15 minutes)
   ```bash
   cd web
   npm run build
   
   # Verify build output
   ls -la dist/  # or build/ depending on your setup
   ```

2. **Deploy to Firebase Hosting** (15 minutes)
   ```bash
   # Authenticate with Firebase
   export GOOGLE_APPLICATION_CREDENTIALS="/workspace/aletheia-codex-prod-af9a64a7fcaa.json"
   
   # Deploy
   firebase deploy --only hosting
   
   # Note the deployed URL
   ```

3. **Verify Production Deployment** (30 minutes)
   - Access deployed URL
   - Test all features in production
   - Verify Load Balancer integration
   - Check browser console for errors
   - Test on different browsers/devices

---

## 📚 Key Documentation to Review

### From Admin-Infrastructure

1. **Load Balancer Handoff** (MUST READ)
   - Location: `[artifacts]/admin-infrastructure/outbox/load-balancer-handoff.md`
   - Contains: Load Balancer URL, API routing, integration details

2. **Sprint 1 Final Summary** (MUST READ)
   - Location: `[artifacts]/admin-infrastructure/outbox/sprint-1-final-summary.md`
   - Contains: Complete infrastructure status, what's ready for you

### From Admin-Backend

1. **Backend Handoff** (MUST READ)
   - Location: `[artifacts]/docmaster-sprint/inbox/sprint-1-handoff-from-admin-backend.md`
   - Contains: Authentication implementation details, API changes

2. **Backend Session Log** (Reference)
   - Location: `[artifacts]/admin-backend/outbox/session-log-2025-01-18.md`
   - Contains: Detailed backend work, technical decisions

3. **Authentication Documentation** (Reference)
   - Location: `[sprint-1]/shared/auth/README.md`
   - Contains: How IAP authentication works

### Your Documentation

1. **Service Account Analysis**
   - Location: `[artifacts]/architect/service-account-analysis.md`
   - Contains: Service account permissions and usage

2. **Code Standards**
   - Location: `[artifacts]/architect/code-standards.md`
   - Contains: TypeScript/JavaScript coding standards

3. **API Standards**
   - Location: `[artifacts]/architect/api-standards.md`
   - Contains: API design standards

4. **Git Standards**
   - Location: `[artifacts]/architect/git-standards.md`
   - Contains: Branch naming, commit messages, merge strategy

---

## 🔑 API Integration Details

### Load Balancer URL
**Base URL**: `https://aletheiacodex.app`

### API Endpoints
All endpoints now use the Load Balancer URL:

```javascript
// API Configuration
const API_CONFIG = {
  baseURL: 'https://aletheiacodex.app',
  endpoints: {
    ingest: '/api/ingest',
    orchestrate: '/api/orchestrate',
    graph: '/api/graph',
    notes: '/api/notes',
    review: '/api/review'
  }
};
```

### Authentication
**No changes required to authentication logic!**

- Frontend continues to use Firebase Auth
- Firebase token is sent in `Authorization` header
- IAP validates the token automatically
- Backend extracts user identity from IAP headers

**Example API Call**:
```javascript
// Get Firebase token
const token = await firebase.auth().currentUser.getIdToken();

// Make API call (same as before, just different URL)
const response = await fetch('https://aletheiacodex.app/api/graph/entities', {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});
```

### CORS
CORS is handled by the Load Balancer and IAP. No frontend changes needed.

### Error Handling
Handle these potential errors:

```javascript
// 401 Unauthorized - Invalid or missing token
if (response.status === 401) {
  // Refresh token or redirect to login
}

// 403 Forbidden - IAP denied access
if (response.status === 403) {
  // Show error message, user not authorized
}

// 502 Bad Gateway - Backend service unavailable
if (response.status === 502) {
  // Show error message, try again later
}
```

---

## 📊 Success Criteria

Your work is complete when:

- [ ] API base URL updated to Load Balancer
- [ ] All API endpoints updated with new paths
- [ ] Environment variables updated
- [ ] All hardcoded URLs removed
- [ ] Local testing complete - all features working
- [ ] Authentication flow tested and working
- [ ] Error handling tested
- [ ] Production build successful
- [ ] Deployed to Firebase Hosting
- [ ] Production deployment tested and verified
- [ ] No console errors in browser
- [ ] All features functional end-to-end
- [ ] Documentation updated

---

## 🔄 Git Workflow

### Working on Sprint 1

```bash
# Make changes to files in web/ directory
# ... edit files ...

# Stage and commit changes
git add web/
git commit -m "feat(frontend): update API client to use Load Balancer"

# Push to sprint-1 branch
git push origin sprint-1
```

### Branch Details
- **Shared Branch**: All Admin nodes work on `sprint-1`
- **Your Directory**: Work in `web/` directory
- **Previous Work**: Infrastructure in `infrastructure/`, Backend in `functions/` and `shared/`
- See `[artifacts]/architect/sprint-1-branch-strategy.md` for details

---

## 📝 Reporting Requirements

### Daily Session Logs

Create session logs at: `[artifacts]/admin-frontend/session-logs/YYYY-MM-DD.md`

Use the template at: `[artifacts]/templates/session-log.md`

### Escalations

If you encounter blockers, use the escalation template at: `[artifacts]/templates/escalation-doc.md`

Place escalations in: `[artifacts]/admin-frontend/outbox/`

---

## 🤝 Coordination with Other Nodes

### Admin-Infrastructure (Complete) ✅
- ✅ Load Balancer operational
- ✅ IAP enabled
- ✅ SSL certificate active
- ✅ DNS configured
- ✅ Monitoring documented

### Admin-Backend (Complete) ✅
- ✅ IAP authentication implemented
- ✅ All Cloud Functions updated
- ✅ Unit tests passing
- ✅ Ready for integration

### Your Work (Final Piece) 🎯
- 🔄 Update API client configuration
- 🔄 Test end-to-end functionality
- 🔄 Deploy to production
- ✅ Complete Sprint 1!

---

## ⚠️ Important Notes

### Test-in-Prod Approach
- You have full deployment permissions
- Infrastructure and backend are ready
- Deploy and test directly in production
- Monitor for any issues
- Roll back if problems detected

### Load Balancer URL
- **Always use**: `https://aletheiacodex.app`
- **Never use**: Direct Cloud Functions URLs
- All API calls should go through Load Balancer

### Authentication
- **No changes needed** to Firebase Auth logic
- IAP validates tokens automatically
- Backend handles user identity extraction
- Just update the API URLs

### Testing
- Test locally first
- Then test in production
- Verify all features work
- Check browser console for errors

---

## 🚀 Getting Started Checklist

- [ ] Authenticate with GCP using service account
- [ ] Checkout sprint-1 branch
- [ ] Pull latest changes (Infrastructure + Backend work)
- [ ] Read your prime directive: `[artifacts]/admin-frontend/admin-frontend.txt`
- [ ] Read your sprint guide: `[artifacts]/admin-frontend/inbox/sprint-1-guide.md`
- [ ] Read infrastructure handoff: `[artifacts]/admin-infrastructure/outbox/load-balancer-handoff.md`
- [ ] Read backend handoff: `[artifacts]/docmaster-sprint/inbox/sprint-1-handoff-from-admin-backend.md`
- [ ] Create your todo.md file
- [ ] Begin Priority Task 1: Update API Client Configuration

---

## 📞 Support

### Questions or Issues?

1. **Review documentation first** - Most answers are in the handoff documents
2. **Check browser console** - Frontend errors show detailed information
3. **Test API endpoints directly** - Use curl to verify backend is working
4. **Escalate if blocked** - Use the escalation template

### Testing API Endpoints Directly

```bash
# Get Firebase token (from browser console or Firebase CLI)
TOKEN="your-firebase-token"

# Test each endpoint
curl -H "Authorization: Bearer $TOKEN" https://aletheiacodex.app/api/graph/entities
curl -H "Authorization: Bearer $TOKEN" https://aletheiacodex.app/api/notes
curl -H "Authorization: Bearer $TOKEN" https://aletheiacodex.app/api/review
```

### Escalation Process

If you encounter blockers:
1. Create escalation document using template
2. Place in `[artifacts]/admin-frontend/outbox/`
3. Commit to artifacts branch
4. Notify Architect

---

## 🎯 Timeline Estimate

- **Priority 1** (Update API Client): 2-3 hours
- **Priority 2** (Test Integration): 2-3 hours
- **Priority 3** (Deploy Frontend): 1 hour
- **Total Estimated Time**: 5-7 hours (1 day)

---

## 🎉 Sprint 1 Completion

When you complete your work:

✅ Infrastructure operational (Admin-Infrastructure)  
✅ Backend authentication implemented (Admin-Backend)  
✅ Frontend integrated with Load Balancer (You!)  
✅ **Sprint 1 COMPLETE!**

Your work completes Sprint 1 and restores full application functionality!

---

## ✅ Ready to Begin!

You have everything you need to complete Sprint 1 frontend work:

✅ Infrastructure is ready and operational  
✅ Backend authentication is implemented  
✅ Complete documentation provided  
✅ Clear tasks and acceptance criteria  
✅ Full deployment permissions  
✅ Support and escalation process in place  

**Start with Priority 1: Update API Client Configuration**

Good luck! You're the final piece to complete Sprint 1!

---

**Architect**  
AletheiaCodex Project  
2025-01-18

---

**End of Initialization Document**