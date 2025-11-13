# Sprint 1 Guide - API Access Restoration

**Sprint Number**: 1  
**Sprint Goal**: Resolve organization policy blocker and restore API connectivity  
**Created**: January 2025  
**Author**: Architect  
**Target Completion**: 2-3 days  

---

## Sprint Overview

### Purpose
The application is currently non-functional due to a GCP organization policy that blocks public access to Cloud Functions. All API endpoints return 403 Forbidden, preventing the frontend from communicating with the backend. This sprint focuses on updating the frontend to work with the new IAP-based authentication and verifying all features work end-to-end.

### Success Criteria
- [x] Frontend can successfully call backend API endpoints
- [x] API client works with IAP authentication
- [x] Users can create notes
- [x] Users can view and interact with review queue
- [x] Users can view knowledge graph
- [x] All features work end-to-end
- [x] No 403 errors from API calls

### Sprint Context
This is a critical fix sprint. The application has been developed through Sprint 6 with all UI features implemented, but the organization policy prevents the frontend from accessing the backend. This sprint updates the frontend to work with the new IAP-based access pattern.

**Previous Work**: Sprints 1-6 completed all UI features (note input, review queue, knowledge graph, authentication)

**Current Blocker**: Frontend cannot access backend due to 403 errors

---

## Features by Domain

### Frontend Features

#### Feature 1: Update API Client for IAP Authentication
**Priority**: High  
**Assigned to**: Admin-Frontend  
**Estimated Effort**: 4-6 hours

**Description**:
Update the API client to work with the new IAP-based authentication. The frontend will continue to use Firebase Auth for user authentication, but requests will go through the Load Balancer with IAP, which validates the Firebase token before forwarding to backend.

**Acceptance Criteria**:
- [ ] API client updated to use new base URL (Load Balancer URL)
- [ ] Firebase Auth token included in requests
- [ ] API calls succeed (no 403 errors)
- [ ] Error handling works for authentication failures
- [ ] Token refresh works correctly
- [ ] All existing API calls work

**Technical Requirements**:
- Update API base URL to Load Balancer endpoint
- Ensure Firebase Auth token is included in Authorization header
- Handle 401/403 errors gracefully
- Implement token refresh logic
- Maintain existing API client interface
- No breaking changes to components using API client

**Dependencies**:
- Infrastructure must provide Load Balancer URL
- Backend must be updated and deployed

**Integration Points**:
- **Frontend ↔ Infrastructure**: Use Load Balancer URL
- **Frontend ↔ Backend**: API contracts remain unchanged

**Testing Requirements**:
- Test API calls with valid token
- Test API calls with expired token
- Test API calls with no token
- Test token refresh flow
- Test error handling

---

#### Feature 2: Verify Note Creation Flow
**Priority**: High  
**Assigned to**: Admin-Frontend  
**Estimated Effort**: 2-3 hours

**Description**:
Verify that the note creation flow works end-to-end with the new authentication. Users should be able to create notes, see processing status, and view results.

**Acceptance Criteria**:
- [ ] Users can create notes through UI
- [ ] Notes are successfully sent to backend
- [ ] Processing status updates in real-time
- [ ] Users can view note history
- [ ] Error messages display correctly
- [ ] Loading states work properly

**Technical Requirements**:
- Test note input component
- Test API call to create note
- Test Firestore listener for status updates
- Test note history display
- Verify error handling
- Verify loading states

**Dependencies**:
- Feature 1 (API client update) must be complete
- Backend must be working

**Integration Points**:
- **Frontend ↔ Backend**: POST /api/notes endpoint
- **Frontend ↔ Firestore**: Real-time status updates

**Testing Requirements**:
- Create note with valid content
- Create note with empty content (should fail)
- Verify processing status updates
- Verify note appears in history
- Test error scenarios

---

#### Feature 3: Verify Review Queue Flow
**Priority**: High  
**Assigned to**: Admin-Frontend  
**Estimated Effort**: 2-3 hours

**Description**:
Verify that the review queue works end-to-end with the new authentication. Users should be able to view pending items, approve/reject entities and relationships, and see updates in real-time.

**Acceptance Criteria**:
- [ ] Users can view pending review items
- [ ] Users can approve entities/relationships
- [ ] Users can reject entities/relationships
- [ ] Real-time updates work (Firestore listeners)
- [ ] Batch operations work
- [ ] Error messages display correctly

**Technical Requirements**:
- Test review queue page load
- Test API call to get pending items
- Test approve action
- Test reject action
- Test batch operations
- Verify Firestore listeners
- Verify error handling

**Dependencies**:
- Feature 1 (API client update) must be complete
- Backend must be working

**Integration Points**:
- **Frontend ↔ Backend**: GET /api/review/pending, POST /api/review/{id}/approve, POST /api/review/{id}/reject
- **Frontend ↔ Firestore**: Real-time updates

**Testing Requirements**:
- Load review queue page
- Approve an entity
- Reject an entity
- Test batch approve
- Test batch reject
- Verify real-time updates

---

#### Feature 4: Verify Knowledge Graph Flow
**Priority**: Medium  
**Assigned to**: Admin-Frontend  
**Estimated Effort**: 1-2 hours

**Description**:
Verify that the knowledge graph visualization works with the new authentication. Users should be able to view entities and relationships in the graph.

**Acceptance Criteria**:
- [ ] Users can view knowledge graph
- [ ] Entities display correctly
- [ ] Relationships display correctly
- [ ] Graph is interactive
- [ ] Error messages display correctly

**Technical Requirements**:
- Test knowledge graph page load
- Test API call to get graph data
- Test graph visualization
- Verify error handling
- Verify loading states

**Dependencies**:
- Feature 1 (API client update) must be complete
- Backend must be working

**Integration Points**:
- **Frontend ↔ Backend**: GET /api/graph/nodes, GET /api/graph/node/{id}

**Testing Requirements**:
- Load knowledge graph page
- Verify entities display
- Verify relationships display
- Test graph interactions
- Test error scenarios

---

#### Feature 5: Update Environment Configuration
**Priority**: High  
**Assigned to**: Admin-Frontend  
**Estimated Effort**: 1 hour

**Description**:
Update environment configuration to use the new Load Balancer URL for API calls.

**Acceptance Criteria**:
- [ ] Environment variables updated with Load Balancer URL
- [ ] Development environment configured
- [ ] Production environment configured
- [ ] Configuration documented

**Technical Requirements**:
- Update .env files with new API base URL
- Update Firebase configuration if needed
- Document configuration changes
- Test in both dev and prod environments

**Dependencies**:
- Infrastructure must provide Load Balancer URL

**Integration Points**:
- **Frontend ↔ Infrastructure**: Use Load Balancer URL

**Testing Requirements**:
- Test in development environment
- Test in production environment
- Verify correct URL is used

---

## Architectural Guidance

### Overall Approach
The frontend continues to use Firebase Auth for user authentication. The key change is that API requests now go through the Load Balancer with IAP instead of directly to Cloud Functions. IAP validates the Firebase token before forwarding requests to the backend.

### Design Patterns

**Pattern 1: API Client Update**
- Update base URL to Load Balancer endpoint
- Continue including Firebase Auth token in Authorization header
- IAP validates token before forwarding to backend
- Backend extracts user identity from IAP headers

**Pattern 2: Error Handling**
- Handle 401/403 errors gracefully
- Prompt user to re-authenticate if token expired
- Display clear error messages
- Retry failed requests after token refresh

### Technical Constraints
- Must maintain existing API contracts
- Must not break existing components
- Must maintain user experience
- Must handle authentication errors gracefully

### Integration Considerations

**Frontend ↔ Infrastructure**:
- Use Load Balancer URL for all API calls
- Load Balancer URL provided by Infrastructure
- DNS routing handled by Infrastructure

**Frontend ↔ Backend**:
- API contracts remain unchanged
- Continue using same request/response formats
- Authentication handled transparently by IAP

### Performance Considerations
- IAP adds minimal latency (<10ms)
- No impact on frontend performance
- Monitor API response times
- Maintain loading states for user feedback

### Security Considerations
- Firebase Auth token still required
- IAP provides additional security layer
- No changes to user authentication flow
- Maintain secure token handling

---

## Escalation Criteria

### When to Escalate
Escalate to Architect when you encounter:

1. **API Connectivity Issues**
   - Cannot connect to Load Balancer
   - API calls still return 403
   - CORS errors occur

2. **Authentication Issues**
   - Firebase Auth token not accepted
   - Token refresh fails
   - User identity issues

3. **Integration Problems**
   - API contracts changed unexpectedly
   - Response formats different
   - Backend behavior unexpected

4. **Feature Verification Issues**
   - Features don't work as expected
   - Real-time updates broken
   - Data not displaying correctly

5. **Configuration Issues**
   - Environment configuration unclear
   - Load Balancer URL not provided
   - Multiple environments need different configs

### How to Escalate
1. Document the blocker using the escalation template at [artifacts]/templates/escalation-doc.md
2. Save to your outbox: [artifacts]/admin-frontend/outbox/escalation-[topic].md
3. Notify Human that escalation is ready
4. Wait for Architect response before proceeding

### What to Include in Escalation
- Clear description of the blocker
- Context and background
- What you've tried
- Browser console errors
- Network tab screenshots
- Questions for Architect

---

## Quality Standards

### Code Quality
- Follow code standards defined in [artifacts]/architect/code-standards.md
- Maintain test coverage >80%
- All tests must pass before sprint completion
- Code must be reviewed and approved

### Documentation
- Update inline code documentation (JSDoc)
- Update README files for modified components
- Document configuration changes
- Create session logs for each work session

### Testing
- Unit tests for API client changes
- Integration tests for user flows
- Manual testing in browser
- Test in multiple browsers

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
- Update API client configuration
- Update environment variables
- Test API connectivity
- Verify all features
- Commit changes regularly
- Create session logs

### 3. Testing
- Test in development environment
- Test in production environment
- Test all user flows
- Test error scenarios
- Validate against acceptance criteria

### 4. Documentation
- Update inline documentation
- Update README files
- Document configuration changes
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

### Previous Sprint Outcomes
- Sprint 6: UI Foundation & Component Organization (blocked by org policy)
- Sprint 5: Note Processing Workflow Fix (complete)
- Sprint 4.5: Firebase Authentication Implementation (complete)

### Architecture Documents
- [Domain Definitions]([artifacts]/architect/domain-definitions.md)
- [Escalation Workflow]([artifacts]/architect/escalation-workflow.md)

### External Resources
- [Firebase Auth Documentation](https://firebase.google.com/docs/auth)
- [Axios Documentation](https://axios-http.com/docs/intro)
- [React Query Documentation](https://tanstack.com/query/latest)

---

## Notes

### Important Considerations
- This is a critical fix sprint - application is non-functional without this
- Coordinate with Infrastructure for Load Balancer URL
- Test thoroughly in browser before considering complete
- Verify all features work end-to-end

### Known Issues
- All API calls currently return 403 Forbidden
- Frontend cannot communicate with backend
- Users cannot use any features

### Future Work
- Consider adding retry logic for failed requests
- Add better error messages for authentication failures
- Improve loading states

---

**End of Sprint Guide**