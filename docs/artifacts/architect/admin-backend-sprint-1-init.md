# Admin-Backend Sprint 1 Initialization

**Date**: 2025-01-18  
**From**: Architect  
**To**: Admin-Backend  
**Sprint**: Sprint 1 - API Access Restoration  
**Priority**: HIGH  

---

## 🎯 Mission Overview

You are the **Admin-Backend** node for Sprint 1. Admin-Infrastructure has successfully completed the Load Balancer + IAP infrastructure setup. Your mission is to implement IAP authentication in the Cloud Functions so they can properly validate requests coming through the Load Balancer.

**Critical Context**: The infrastructure is ready and operational. Your work is the final piece needed to restore full API functionality.

---

## ✅ What's Already Complete (Admin-Infrastructure)

### Infrastructure Ready
- ✅ Load Balancer operational at **https://aletheiacodex.app**
- ✅ IAP enabled on all 6 backend services
- ✅ SSL certificate active
- ✅ DNS configured (aletheiacodex.app → 34.120.185.233)
- ✅ Routing configured for all API endpoints
- ✅ OAuth consent screen configured

### API Routing Table
| Path | Backend Service | Cloud Function |
|------|----------------|----------------|
| `/api/ingest` | backend-ingestion | ingestion |
| `/api/orchestrate` | backend-orchestration | orchestration |
| `/api/graph/*` | backend-graphfunction | graphfunction |
| `/api/notes/*` | backend-notesapifunction | notesapifunction |
| `/api/review/*` | backend-reviewapifunction | reviewapifunction |

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
# Checkout sprint-1 branch
git checkout sprint-1

# Pull latest changes
git pull origin sprint-1
```

---

## 📋 Your Prime Directive

**Location**: `[artifacts]/admin-backend/admin-backend.txt`

Read your complete prime directive before beginning work. It contains:
- Your role and responsibilities
- Technical domain ownership
- Communication protocols
- Standards and best practices

---

## 📖 Sprint 1 Guide

**Location**: `[artifacts]/admin-backend/inbox/sprint-1-guide.md`

Your Sprint 1 guide contains:
- Detailed feature requirements
- Acceptance criteria
- Implementation guidance
- Testing procedures

---

## 🎯 Your Sprint 1 Tasks

### Priority 1: Implement IAP Authentication (CRITICAL)

**Objective**: Update all Cloud Functions to extract and validate IAP JWT headers

**What You Need to Do**:

1. **Create IAP Authentication Module** (2-3 hours)
   - Create `shared/auth/iap_auth.py`
   - Implement JWT extraction from `X-Goog-IAP-JWT-Assertion` header
   - Implement JWT signature validation using Google's public keys
   - Extract user identity from JWT claims
   - Add error handling for invalid/missing tokens

2. **Update Cloud Functions** (2-3 hours)
   - Update all 6 Cloud Functions to use IAP authentication:
     - `functions/ingestion/main.py`
     - `functions/orchestration/main.py`
     - `functions/graphfunction/main.py`
     - `functions/notesapifunction/main.py`
     - `functions/reviewapifunction/main.py`
     - `functions/orchestrate/main.py` (if different from orchestration)
   - Add IAP authentication middleware to each function
   - Extract user identity and pass to function logic
   - Update error responses for authentication failures

3. **Test Authentication Locally** (1 hour)
   - Create test script to simulate IAP headers
   - Test JWT validation logic
   - Test error handling
   - Verify user identity extraction

### Priority 2: Deploy Updated Functions (CRITICAL)

**Objective**: Deploy all Cloud Functions with IAP authentication

**What You Need to Do**:

1. **Deploy Functions** (1-2 hours)
   ```bash
   # Deploy each function with updated code
   # Example for orchestration function:
   cd functions/orchestration
   gcloud functions deploy orchestration \
     --gen2 \
     --runtime=python311 \
     --region=us-central1 \
     --source=. \
     --entry-point=orchestration \
     --trigger-http \
     --service-account=aletheia-functions@aletheia-codex-prod.iam.gserviceaccount.com \
     --timeout=540s \
     --memory=512MB
   ```

2. **Verify Deployments** (30 minutes)
   - Check deployment status for all functions
   - Verify functions are running
   - Check logs for any deployment errors

### Priority 3: Test Integration (CRITICAL)

**Objective**: Verify all endpoints work through Load Balancer with IAP

**What You Need to Do**:

1. **Test Each Endpoint** (1-2 hours)
   ```bash
   # Get Firebase token for testing
   # Test each endpoint through Load Balancer
   
   # Example: Test orchestration endpoint
   curl -H "Authorization: Bearer [firebase-token]" \
     https://aletheiacodex.app/api/orchestrate
   
   # Test all endpoints:
   # - /api/ingest
   # - /api/orchestrate
   # - /api/graph/*
   # - /api/notes/*
   # - /api/review/*
   ```

2. **Verify Authentication** (30 minutes)
   - Test with valid Firebase token (should succeed)
   - Test without token (should return 401)
   - Test with invalid token (should return 401)
   - Verify user identity is extracted correctly

3. **Check Logs** (30 minutes)
   - Review Cloud Functions logs
   - Verify IAP headers are being received
   - Check for any authentication errors
   - Verify user identity logging

---

## 📚 Key Documentation to Review

### From Admin-Infrastructure

1. **Load Balancer Handoff** (MUST READ)
   - Location: `[artifacts]/admin-infrastructure/outbox/load-balancer-handoff.md`
   - Contains: IAP integration details, API routing, testing guidance

2. **Sprint 1 Final Summary** (MUST READ)
   - Location: `[artifacts]/admin-infrastructure/outbox/sprint-1-final-summary.md`
   - Contains: Complete infrastructure status, what's ready, what you need to do

3. **Infrastructure Documentation** (Reference)
   - Location: `[sprint-1-infrastructure]/infrastructure/load-balancer/README.md`
   - Contains: Complete Load Balancer configuration details

### Your Documentation

1. **Service Account Analysis**
   - Location: `[artifacts]/architect/service-account-analysis.md`
   - Contains: Service account permissions and usage

2. **Code Standards**
   - Location: `[artifacts]/architect/code-standards.md`
   - Contains: Python coding standards (PEP 8)

3. **API Standards**
   - Location: `[artifacts]/architect/api-standards.md`
   - Contains: API design standards

4. **Git Standards**
   - Location: `[artifacts]/architect/git-standards.md`
   - Contains: Branch naming, commit messages, merge strategy

---

## 🔑 IAP Authentication Details

### IAP Headers

When requests come through the Load Balancer with IAP enabled, these headers are added:

```
X-Goog-IAP-JWT-Assertion: [JWT token with user identity]
X-Goog-Authenticated-User-Email: [user email]
X-Goog-Authenticated-User-ID: [user ID]
```

### JWT Structure

The `X-Goog-IAP-JWT-Assertion` header contains a JWT with:

```json
{
  "iss": "https://cloud.google.com/iap",
  "sub": "accounts.google.com:[user-id]",
  "email": "user@example.com",
  "aud": "/projects/[project-number]/global/backendServices/[service-id]",
  "iat": 1234567890,
  "exp": 1234567890
}
```

### Validation Steps

1. Extract JWT from `X-Goog-IAP-JWT-Assertion` header
2. Decode JWT header to get key ID (kid)
3. Fetch Google's public keys from: `https://www.gstatic.com/iap/verify/public_key-jwk`
4. Verify JWT signature using public key
5. Verify JWT claims (issuer, audience, expiration)
6. Extract user identity from claims

### Python Implementation Example

```python
import jwt
import requests
from functools import lru_cache

@lru_cache(maxsize=1)
def get_iap_public_keys():
    """Fetch and cache IAP public keys"""
    response = requests.get('https://www.gstatic.com/iap/verify/public_key-jwk')
    return response.json()

def validate_iap_jwt(iap_jwt, expected_audience):
    """Validate IAP JWT and extract user identity"""
    try:
        # Get public keys
        keys = get_iap_public_keys()
        
        # Decode and verify JWT
        decoded_jwt = jwt.decode(
            iap_jwt,
            keys,
            algorithms=['ES256'],
            audience=expected_audience
        )
        
        # Extract user identity
        return {
            'email': decoded_jwt.get('email'),
            'user_id': decoded_jwt.get('sub'),
            'authenticated': True
        }
    except Exception as e:
        return {
            'authenticated': False,
            'error': str(e)
        }
```

---

## 📊 Success Criteria

Your work is complete when:

- [ ] IAP authentication module created and tested
- [ ] All 6 Cloud Functions updated with IAP authentication
- [ ] All functions deployed successfully
- [ ] All endpoints accessible through Load Balancer
- [ ] Authentication works with valid Firebase tokens
- [ ] Authentication rejects invalid/missing tokens
- [ ] User identity extracted correctly
- [ ] Logs show proper authentication flow
- [ ] No 403 errors on authenticated requests
- [ ] Documentation updated

---

## 🔄 Git Workflow

### Working on Sprint 1

```bash
# Make changes to files
# ... edit files ...

# Stage and commit changes
git add .
git commit -m "feat(backend): implement IAP authentication middleware"

# Push to sprint-1 branch
git push origin sprint-1
```

### Branch Details
- Work directly on the `sprint-1` branch
- All Admin nodes share this branch
- Coordinate to avoid conflicts
- See `[artifacts]/architect/sprint-1-branch-setup.md` for details

---

## 📝 Reporting Requirements

### Daily Session Logs

Create session logs at: `[artifacts]/admin-backend/session-logs/YYYY-MM-DD.md`

Use the template at: `[artifacts]/templates/session-log.md`

### Escalations

If you encounter blockers, use the escalation template at: `[artifacts]/templates/escalation-doc.md`

Place escalations in: `[artifacts]/admin-backend/outbox/`

---

## 🤝 Coordination with Other Nodes

### Admin-Infrastructure (Complete)
- ✅ Load Balancer operational
- ✅ IAP enabled
- ✅ Infrastructure ready for your integration

### Admin-Frontend (Waiting for You)
- ⏳ Waiting for backend IAP implementation
- ⏳ Will update API client after your work is complete
- ⏳ Will test end-to-end after your deployment

**Timeline**: Admin-Frontend will begin after you complete and verify IAP authentication

---

## ⚠️ Important Notes

### Test-in-Prod Approach
- You have full deployment permissions
- The application is currently non-functional due to organization policy
- Deploy and test directly in production
- Monitor logs after each deployment
- Roll back if issues are detected

### Load Balancer URL
- **Always use**: `https://aletheiacodex.app`
- **Never use**: Direct Cloud Functions URLs
- All testing should go through the Load Balancer

### IAP is Already Enabled
- IAP is enabled on all backend services
- Your job is to implement authentication in the functions
- Don't try to enable/disable IAP - it's already configured

---

## 🚀 Getting Started Checklist

- [ ] Authenticate with GCP using service account
- [ ] Checkout sprint-1 branch
- [ ] Read your prime directive: `[artifacts]/admin-backend/admin-backend.txt`
- [ ] Read your sprint guide: `[artifacts]/admin-backend/inbox/sprint-1-guide.md`
- [ ] Read infrastructure handoff: `[artifacts]/admin-infrastructure/outbox/load-balancer-handoff.md`
- [ ] Read infrastructure summary: `[artifacts]/admin-infrastructure/outbox/sprint-1-final-summary.md`
- [ ] Create your todo.md file
- [ ] Begin Priority Task 1: Implement IAP Authentication

---

## 📞 Support

### Questions or Issues?

1. **Review documentation first** - Most answers are in the handoff documents
2. **Check logs** - Cloud Functions logs show detailed error information
3. **Test locally** - Create test scripts to validate logic
4. **Escalate if blocked** - Use the escalation template

### Escalation Process

If you encounter blockers:
1. Create escalation document using template
2. Place in `[artifacts]/admin-backend/outbox/`
3. Commit to artifacts branch
4. Notify Architect

---

## 🎯 Timeline Estimate

- **Priority 1** (IAP Authentication): 3-4 hours
- **Priority 2** (Deploy Functions): 1-2 hours
- **Priority 3** (Test Integration): 1-2 hours
- **Total Estimated Time**: 5-8 hours (1 day)

---

## ✅ Ready to Begin!

You have everything you need to complete Sprint 1 backend work:

✅ Infrastructure is ready and operational  
✅ Complete documentation provided  
✅ Clear tasks and acceptance criteria  
✅ Full deployment permissions  
✅ Support and escalation process in place  

**Start with Priority 1: Implement IAP Authentication**

Good luck! The project depends on your success.

---

**Architect**  
AletheiaCodex Project  
2025-01-18

---

**End of Initialization Document**