# Sprint 1 Guide - API Access Restoration

**Sprint Number**: 1  
**Sprint Goal**: Resolve organization policy blocker and restore API connectivity  
**Created**: January 2025  
**Author**: Architect  
**Target Completion**: 2-3 days  

---

## Sprint Overview

### Purpose
The application is currently non-functional due to a GCP organization policy that blocks public access to Cloud Functions. All API endpoints return 403 Forbidden, preventing the frontend from communicating with the backend. This sprint focuses on resolving this critical blocker and restoring full application functionality.

### Success Criteria
- [x] Backend API endpoints are accessible from frontend
- [x] Authentication works with new access pattern
- [x] All Cloud Functions respond correctly (not 403)
- [x] Security is maintained
- [x] Organization policy compliance achieved
- [x] API response times remain acceptable (<500ms for reads)

### Sprint Context
This is a critical fix sprint. The application has been developed through Sprint 6 with all features implemented, but the organization policy prevents users from accessing the application. This sprint resolves the access issue so users can use the application.

**Previous Work**: Sprints 1-6 completed all features (entity extraction, review queue, knowledge graph, frontend UI)

**Current Blocker**: GCP organization policy `iam.allowedPolicyMemberDomains` prevents `allUsers` access


---

## Service Account Credentials

**CRITICAL: You have been provided with service account keys for authentication.**

### Available Service Accounts

1. **SuperNinja Service Account** (Primary - Use for all deployment operations)
   - Email: `superninja@aletheia-codex-prod.iam.gserviceaccount.com`
   - Key File: `[workspace]/aletheia-codex-prod-af9a64a7fcaa.json`
   - Purpose: Deployment, infrastructure management, backend operations
   - Permissions: Full access to deploy, configure, and manage GCP resources

2. **Firebase Admin SDK Service Account** (Backend code only)
   - Email: `firebase-adminsdk-fbsvc@aletheia-codex-prod.iam.gserviceaccount.com`
   - Key File: `[workspace]/aletheia-codex-prod-firebase-adminsdk-fbsvc-8b9046a84f.json`
   - Purpose: Firebase Admin SDK initialization in backend code
   - Permissions: Firebase Auth and Admin SDK operations

### Authentication Instructions

**For gcloud CLI (Infrastructure and Backend deployments):**
```bash
gcloud auth activate-service-account --key-file=[workspace]/aletheia-codex-prod-af9a64a7fcaa.json
gcloud config set project aletheia-codex-prod
```

**For Firebase CLI (Frontend deployments):**
```bash
export GOOGLE_APPLICATION_CREDENTIALS="[workspace]/aletheia-codex-prod-af9a64a7fcaa.json"
```

**For Firebase Admin SDK in Python code:**
```python
import firebase_admin
from firebase_admin import credentials

cred = credentials.Certificate('[workspace]/aletheia-codex-prod-firebase-adminsdk-fbsvc-8b9046a84f.json')
firebase_admin.initialize_app(cred)
```

### Permission Verification

- **Complete permission analysis:** See `[artifacts]/architect/service-account-analysis.md`
- **All Sprint 1 permissions verified:** ✅ Sufficient for all tasks
- **If you encounter permission errors:** Escalate immediately to Architect
- **NEVER commit service account keys to the repository**

### Test-in-Prod Approach

You are **encouraged to deploy and test directly in production** for this sprint:
- You have full deployment permissions
- The application is currently non-functional, so there's no risk of breaking working features
- Deploy incrementally and test each component
- Monitor logs and metrics after each deployment
- Roll back if issues are detected

---

## Features by Domain

### Backend Features

#### Feature 1: Implement IAP-Compatible Authentication
**Priority**: High  
**Assigned to**: Admin-Backend  
**Estimated Effort**: 1-2 days

**Description**:
Modify the Cloud Functions authentication middleware to work with Identity-Aware Proxy (IAP). IAP will handle the organization policy compliance while maintaining secure access to the backend services.

**Acceptance Criteria**:
- [ ] Authentication middleware updated to work with IAP headers
- [ ] User identity extracted from IAP headers (X-Goog-IAP-JWT-Assertion)
- [ ] Backward compatibility maintained for Firebase Auth (if needed)
- [ ] All Cloud Functions updated with new authentication
- [ ] Unit tests pass for authentication middleware
- [ ] Integration tests pass for API endpoints

**Technical Requirements**:
- Extract and validate IAP JWT token from headers
- Verify token signature using Google's public keys
- Extract user email and ID from token claims
- Maintain user data isolation based on user ID
- Handle both IAP and Firebase Auth tokens (graceful fallback)
- Log authentication events for debugging

**Dependencies**:
- Infrastructure must configure IAP before testing
- Frontend must update API client to work with IAP

**Integration Points**:
- **Backend ↔ Infrastructure**: IAP configuration must be complete
- **Backend ↔ Frontend**: API client must send proper headers

**Testing Requirements**:
- Unit tests for IAP token validation
- Unit tests for user identity extraction
- Integration tests with mock IAP headers
- Manual testing with actual IAP configuration

---

#### Feature 2: Update All Cloud Functions
**Priority**: High  
**Assigned to**: Admin-Backend  
**Estimated Effort**: 4-6 hours

**Description**:
Update all Cloud Functions (ingestion, orchestration, graph, notes_api, review_api) to use the new IAP-compatible authentication middleware.

**Acceptance Criteria**:
- [ ] All Cloud Functions import new authentication middleware
- [ ] All endpoints validate authentication
- [ ] User ID is correctly extracted in all functions
- [ ] Error handling works for invalid authentication
- [ ] All existing tests pass
- [ ] No breaking changes to API contracts

**Technical Requirements**:
- Update imports in all Cloud Functions
- Apply authentication decorator to all endpoints
- Test each function individually
- Verify user data isolation still works
- Maintain API response formats

**Dependencies**:
- Feature 1 (IAP authentication) must be complete

**Integration Points**:
- **Backend ↔ Frontend**: API contracts remain unchanged
- **Backend ↔ Infrastructure**: Functions must be redeployed

**Testing Requirements**:
- Test each Cloud Function endpoint
- Verify authentication works
- Verify user data isolation
- Test error cases (missing token, invalid token, expired token)

---

#### Feature 3: Maintain Firebase Auth Compatibility (Optional)
**Priority**: Medium  
**Assigned to**: Admin-Backend  
**Estimated Effort**: 2-4 hours

**Description**:
If needed, maintain compatibility with Firebase Auth tokens for local development or alternative access patterns.

**Acceptance Criteria**:
- [ ] Authentication middleware checks for both IAP and Firebase tokens
- [ ] Firebase Auth tokens work for local development
- [ ] IAP tokens work for production
- [ ] Clear error messages for authentication failures
- [ ] Documentation updated

**Technical Requirements**:
- Check for IAP headers first
- Fall back to Firebase Auth if IAP headers not present
- Validate Firebase tokens using Firebase Admin SDK
- Extract user ID from appropriate source
- Log which authentication method was used

**Dependencies**:
- Feature 1 (IAP authentication) must be complete

**Integration Points**:
- **Backend ↔ Frontend**: Frontend can use either auth method
- **Backend ↔ Infrastructure**: Both auth methods supported

**Testing Requirements**:
- Test with IAP tokens
- Test with Firebase tokens
- Test with no tokens (should fail)
- Test with invalid tokens (should fail)

---

## Architectural Guidance

### Overall Approach
The solution uses Identity-Aware Proxy (IAP) to handle organization policy compliance. IAP sits in front of the Cloud Functions and validates user identity before forwarding requests. The backend extracts user identity from IAP headers instead of directly validating Firebase tokens.

### Design Patterns

**Pattern 1: IAP Authentication Middleware**
- Create authentication decorator that extracts IAP JWT
- Validate JWT signature using Google's public keys
- Extract user email and ID from token claims
- Pass user ID to Cloud Function handler

**Pattern 2: Graceful Fallback**
- Check for IAP headers first
- Fall back to Firebase Auth if IAP not present
- Provide clear error messages for authentication failures

### Technical Constraints
- Must comply with organization policy (no `allUsers` access)
- Must maintain user data isolation
- Must not break existing API contracts
- Must maintain acceptable performance (<500ms for reads)

### Integration Considerations

**Backend ↔ Infrastructure**:
- Infrastructure configures IAP and Load Balancer
- Backend extracts user identity from IAP headers
- Backend must be redeployed after changes

**Backend ↔ Frontend**:
- Frontend sends requests through Load Balancer
- Frontend includes Firebase Auth token (IAP validates it)
- API contracts remain unchanged

### Performance Considerations
- IAP adds minimal latency (<10ms)
- JWT validation is fast (cached public keys)
- No impact on database operations
- Monitor API response times after deployment

### Security Considerations
- IAP provides additional security layer
- User identity verified by Google
- No direct public access to Cloud Functions
- Maintain user data isolation
- Log authentication events

---

## Escalation Criteria

### When to Escalate
Escalate to Architect when you encounter:

1. **IAP Integration Issues**
   - IAP headers not present or malformed
   - JWT validation fails unexpectedly
   - User identity extraction unclear

2. **Authentication Conflicts**
   - Firebase Auth and IAP conflict
   - User ID mismatch between auth methods
   - Token validation ambiguity

3. **Performance Issues**
   - Authentication adds significant latency
   - JWT validation is slow
   - Performance targets not met

4. **Organization Policy Issues**
   - Solution doesn't comply with policy
   - Additional policy constraints discovered
   - Alternative approach needed

5. **Integration Problems**
   - Frontend cannot authenticate
   - Infrastructure configuration unclear
   - Cross-domain coordination needed

### How to Escalate
1. Document the blocker using the escalation template at [artifacts]/templates/escalation-doc.md
2. Save to your outbox: [artifacts]/admin-backend/outbox/escalation-[topic].md
3. Notify Human that escalation is ready
4. Wait for Architect response before proceeding

### What to Include in Escalation
- Clear description of the blocker
- Context and background
- What you've tried
- Proposed solutions (if any)
- Impact on sprint timeline
- Questions for Architect

---

## Quality Standards

### Code Quality
- Follow code standards defined in [artifacts]/architect/code-standards.md
- Maintain test coverage >80%
- All tests must pass before sprint completion
- Code must be reviewed and approved

### Documentation
- Update inline code documentation (docstrings)
- Update README files for modified components
- Document authentication changes
- Create session logs for each work session

### Testing
- Unit tests for authentication middleware
- Integration tests for all Cloud Functions
- Manual testing with IAP configuration
- Test error cases thoroughly

### Git Standards
- Follow git standards defined in [artifacts]/architect/git-standards.md
- Descriptive commit messages
- Logical commit organization
- Branch: `sprint-1`

---

## Sprint Workflow

### 1. Sprint Initialization
- Review this sprint guide thoroughly
- Understand the IAP authentication approach
- Identify dependencies and risks
- Create implementation plan
- Set up sprint branch: `git checkout -b sprint-1`

### 2. Implementation
- Implement IAP authentication middleware
- Update all Cloud Functions
- Follow architectural guidance
- Write tests alongside code
- Commit changes regularly
- Create session logs

### 3. Testing
- Run all tests frequently
- Fix failing tests immediately
- Perform manual testing with IAP
- Validate against acceptance criteria

### 4. Documentation
- Update inline documentation
- Update README files
- Document authentication changes
- Create final session log

### 5. Sprint Completion
- Verify all acceptance criteria met
- Ensure all tests pass
- Commit all changes
- Push branch to repository
- Notify Docmaster-Sprint

---

## References

### Related Documentation
- [Project Vision](../../../PROJECT_VISION.md)
- [Code Standards]([artifacts]/architect/code-standards.md)
- [Git Standards]([artifacts]/architect/git-standards.md)
- [API Standards]([artifacts]/architect/api-standards.md)

### Previous Sprint Outcomes
- Sprint 6: UI Foundation & Component Organization (blocked by org policy)
- Sprint 5: Note Processing Workflow Fix (complete)
- Sprint 4.5: Firebase Authentication Implementation (complete)

### Architecture Documents
- [Domain Definitions]([artifacts]/architect/domain-definitions.md)
- [Escalation Workflow]([artifacts]/architect/escalation-workflow.md)

### External Resources
- [Identity-Aware Proxy Documentation](https://cloud.google.com/iap/docs)
- [IAP JWT Validation](https://cloud.google.com/iap/docs/signed-headers-howto)
- [Cloud Functions Authentication](https://cloud.google.com/functions/docs/securing)

---

## Notes

### Important Considerations
- This is a critical fix sprint - application is non-functional without this
- Coordinate closely with Infrastructure for IAP configuration
- Test thoroughly before considering complete
- Monitor for any performance impact

### Known Issues
- Organization policy blocks `allUsers` access to Cloud Functions
- Current authentication (Firebase Auth only) doesn't work with policy
- All API endpoints return 403 Forbidden

### Future Work
- Consider additional security enhancements
- Optimize authentication performance if needed
- Add monitoring for authentication failures

---

**End of Sprint Guide**