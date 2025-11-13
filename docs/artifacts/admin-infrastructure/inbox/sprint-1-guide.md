# Sprint 1 Guide - API Access Restoration

**Sprint Number**: 1  
**Sprint Goal**: Resolve organization policy blocker and restore API connectivity  
**Created**: January 2025  
**Author**: Architect  
**Target Completion**: 2-3 days  

---

## Sprint Overview

### Purpose
The application is currently non-functional due to a GCP organization policy that blocks public access to Cloud Functions. All API endpoints return 403 Forbidden. This sprint focuses on configuring a Load Balancer with Identity-Aware Proxy (IAP) to comply with the organization policy while restoring API access.

### Success Criteria
- [x] Load Balancer configured and operational
- [x] Identity-Aware Proxy (IAP) configured
- [x] Cloud Functions accessible through Load Balancer
- [x] Frontend can access backend through Load Balancer
- [x] Organization policy compliance achieved
- [x] Security maintained
- [x] All services monitored and healthy

### Sprint Context
This is a critical fix sprint. The application has been developed through Sprint 6 with all features implemented, but the organization policy prevents access to Cloud Functions. This sprint implements the infrastructure solution (Load Balancer + IAP) to resolve the access issue.

**Previous Work**: Sprints 1-6 completed all features, but organization policy blocks access

**Current Blocker**: GCP organization policy `iam.allowedPolicyMemberDomains` prevents `allUsers` access to Cloud Functions

---

## Features by Domain

### Infrastructure Features

#### Feature 1: Configure Load Balancer
**Priority**: High  
**Assigned to**: Admin-Infrastructure  
**Estimated Effort**: 4-6 hours

**Description**:
Set up a Google Cloud Load Balancer to sit in front of the Cloud Functions. The Load Balancer will route requests to the appropriate Cloud Functions and integrate with IAP for authentication.

**Acceptance Criteria**:
- [ ] Load Balancer created in GCP
- [ ] Backend services configured for each Cloud Function
- [ ] URL map configured for routing
- [ ] Health checks configured
- [ ] SSL certificate configured
- [ ] Load Balancer is operational

**Technical Requirements**:
- Create global HTTP(S) Load Balancer
- Configure backend services for:
  * Ingestion function
  * Orchestration function
  * Graph API function
  * Notes API function
  * Review API function
- Configure URL map for routing:
  * `/api/ingest` → ingestion function
  * `/api/orchestrate` → orchestration function
  * `/api/graph/*` → graph function
  * `/api/notes/*` → notes_api function
  * `/api/review/*` → review_api function
- Configure health checks for each backend
- Obtain and configure SSL certificate
- Test Load Balancer routing

**Dependencies**:
- Cloud Functions must be deployed
- SSL certificate must be available

**Integration Points**:
- **Infrastructure ↔ Backend**: Load Balancer routes to Cloud Functions
- **Infrastructure ↔ Frontend**: Frontend uses Load Balancer URL

**Validation Requirements**:
- Test each route manually
- Verify health checks pass
- Verify SSL works
- Check Load Balancer logs

---

#### Feature 2: Configure Identity-Aware Proxy (IAP)
**Priority**: High  
**Assigned to**: Admin-Infrastructure  
**Estimated Effort**: 3-4 hours

**Description**:
Configure Identity-Aware Proxy (IAP) on the Load Balancer to handle authentication and comply with the organization policy. IAP will validate Firebase Auth tokens before forwarding requests to Cloud Functions.

**Acceptance Criteria**:
- [ ] IAP enabled on Load Balancer
- [ ] OAuth consent screen configured
- [ ] IAP access policy configured
- [ ] Firebase Auth integrated with IAP
- [ ] IAP validates tokens correctly
- [ ] Authenticated requests reach backend

**Technical Requirements**:
- Enable IAP on Load Balancer backend services
- Configure OAuth consent screen
- Set up IAP access policy:
  * Allow authenticated users
  * Integrate with Firebase Auth
- Configure IAP to accept Firebase Auth tokens
- Test IAP authentication flow
- Verify IAP headers are passed to backend

**Dependencies**:
- Feature 1 (Load Balancer) must be complete
- Firebase Auth must be configured

**Integration Points**:
- **Infrastructure ↔ Backend**: IAP passes authentication headers
- **Infrastructure ↔ Frontend**: IAP validates Firebase tokens

**Validation Requirements**:
- Test with valid Firebase token
- Test with invalid token (should fail)
- Test with no token (should fail)
- Verify IAP headers reach backend

---

#### Feature 3: Update DNS and Routing
**Priority**: High  
**Assigned to**: Admin-Infrastructure  
**Estimated Effort**: 2-3 hours

**Description**:
Update DNS configuration to route API requests through the Load Balancer. Configure custom domain if needed.

**Acceptance Criteria**:
- [ ] DNS configured to point to Load Balancer
- [ ] Custom domain configured (if applicable)
- [ ] SSL certificate matches domain
- [ ] DNS propagation complete
- [ ] Frontend can access API through domain

**Technical Requirements**:
- Configure DNS A record to Load Balancer IP
- Configure custom domain (e.g., api.aletheiacodex.app)
- Verify SSL certificate matches domain
- Test DNS resolution
- Update frontend configuration with new URL

**Dependencies**:
- Feature 1 (Load Balancer) must be complete
- Feature 2 (IAP) must be complete

**Integration Points**:
- **Infrastructure ↔ Frontend**: Frontend uses new API URL

**Validation Requirements**:
- Test DNS resolution
- Test API access through domain
- Verify SSL works
- Test from different networks

---

#### Feature 4: Deploy Updated Cloud Functions
**Priority**: High  
**Assigned to**: Admin-Infrastructure  
**Estimated Effort**: 2-3 hours

**Description**:
Deploy the updated Cloud Functions with IAP-compatible authentication to the GCP environment.

**Acceptance Criteria**:
- [ ] All Cloud Functions deployed successfully
- [ ] Functions use updated authentication
- [ ] Functions are accessible through Load Balancer
- [ ] Health checks pass
- [ ] No deployment errors

**Technical Requirements**:
- Deploy all Cloud Functions:
  * ingestion
  * orchestration
  * graph
  * notes_api
  * review_api
- Verify deployment success
- Check function logs for errors
- Test each function through Load Balancer
- Verify authentication works

**Dependencies**:
- Backend must provide updated code
- Feature 1 (Load Balancer) must be complete
- Feature 2 (IAP) must be complete

**Integration Points**:
- **Infrastructure ↔ Backend**: Deploy backend code

**Validation Requirements**:
- Verify all functions deployed
- Test each function endpoint
- Check logs for errors
- Verify authentication works

---

#### Feature 5: Configure Monitoring and Logging
**Priority**: Medium  
**Assigned to**: Admin-Infrastructure  
**Estimated Effort**: 2-3 hours

**Description**:
Set up monitoring and logging for the Load Balancer, IAP, and Cloud Functions to track performance and errors.

**Acceptance Criteria**:
- [ ] Load Balancer metrics monitored
- [ ] IAP authentication events logged
- [ ] Cloud Functions logs accessible
- [ ] Alerts configured for errors
- [ ] Dashboard created for monitoring

**Technical Requirements**:
- Configure Cloud Monitoring for Load Balancer
- Enable IAP audit logging
- Configure Cloud Logging for functions
- Set up alerts for:
  * High error rates
  * Authentication failures
  * Performance degradation
- Create monitoring dashboard

**Dependencies**:
- Features 1-4 must be complete

**Integration Points**:
- **Infrastructure ↔ All**: Monitor all services

**Validation Requirements**:
- Verify metrics are collected
- Verify logs are accessible
- Test alerts
- Review dashboard

---

#### Feature 6: Deploy Updated Frontend
**Priority**: High  
**Assigned to**: Admin-Infrastructure  
**Estimated Effort**: 1-2 hours

**Description**:
Deploy the updated frontend with the new Load Balancer URL to Firebase Hosting.

**Acceptance Criteria**:
- [ ] Frontend deployed to Firebase Hosting
- [ ] Frontend uses Load Balancer URL
- [ ] Deployment successful
- [ ] Frontend accessible at https://aletheiacodex.app
- [ ] No deployment errors

**Technical Requirements**:
- Build frontend with updated configuration
- Deploy to Firebase Hosting
- Verify deployment success
- Test frontend access
- Verify API calls work

**Dependencies**:
- Frontend must provide updated code
- Features 1-3 must be complete

**Integration Points**:
- **Infrastructure ↔ Frontend**: Deploy frontend code

**Validation Requirements**:
- Verify frontend deployed
- Test frontend access
- Test API calls from frontend
- Verify end-to-end functionality

---

## Architectural Guidance

### Overall Approach
The solution uses a Google Cloud Load Balancer with Identity-Aware Proxy (IAP) to provide secure access to Cloud Functions while complying with the organization policy. The architecture is:

```
User → Firebase Auth → Frontend → Load Balancer (IAP) → Cloud Functions
```

IAP validates the Firebase Auth token before forwarding requests to Cloud Functions. The backend extracts user identity from IAP headers.

### Design Patterns

**Pattern 1: Load Balancer Routing**
- Global HTTP(S) Load Balancer
- Backend services for each Cloud Function
- URL map for routing based on path
- Health checks for each backend

**Pattern 2: IAP Authentication**
- IAP enabled on Load Balancer
- Validates Firebase Auth tokens
- Passes authentication headers to backend
- Complies with organization policy

### Technical Constraints
- Must comply with organization policy (no `allUsers` access)
- Must maintain security
- Must not break existing functionality
- Must maintain acceptable performance

### Integration Considerations

**Infrastructure ↔ Backend**:
- Load Balancer routes to Cloud Functions
- IAP passes authentication headers
- Backend extracts user identity from headers

**Infrastructure ↔ Frontend**:
- Frontend uses Load Balancer URL
- Frontend sends Firebase Auth token
- IAP validates token

### Performance Considerations
- Load Balancer adds minimal latency (<10ms)
- IAP adds minimal latency (<10ms)
- Monitor API response times
- Configure appropriate timeouts

### Security Considerations
- IAP provides additional security layer
- SSL/TLS encryption end-to-end
- User identity verified by Google
- No direct public access to Cloud Functions
- Audit logging enabled

---

## Escalation Criteria

### When to Escalate
Escalate to Architect when you encounter:

1. **Load Balancer Configuration Issues**
   - Cannot create Load Balancer
   - Routing not working
   - Health checks failing

2. **IAP Configuration Issues**
   - Cannot enable IAP
   - IAP not validating tokens
   - OAuth consent screen issues

3. **Organization Policy Issues**
   - Solution doesn't comply with policy
   - Additional policy constraints discovered
   - Alternative approach needed

4. **DNS/Domain Issues**
   - Cannot configure DNS
   - SSL certificate issues
   - Domain not accessible

5. **Deployment Issues**
   - Functions fail to deploy
   - Frontend deployment fails
   - Configuration errors

### How to Escalate
1. Document the blocker using the escalation template at [artifacts]/templates/escalation-doc.md
2. Save to your outbox: [artifacts]/admin-infrastructure/outbox/escalation-[topic].md
3. Notify Human that escalation is ready
4. Wait for Architect response before proceeding

### What to Include in Escalation
- Clear description of the blocker
- Context and background
- What you've tried
- GCP console screenshots
- Error messages
- Questions for Architect

---

## Quality Standards

### Deployment Scripts
- Idempotent (can run multiple times safely)
- Error handling for all operations
- Clear output messages
- Rollback capability
- Documented usage

### Configuration Files
- Valid syntax
- Documented with comments
- Version controlled
- No hardcoded secrets
- Environment-specific values separated

### Infrastructure
- Infrastructure as Code where possible
- Least privilege access control
- Security rules enforced
- Monitoring and alerting configured
- Backup and recovery procedures

### Documentation
- Document all configuration changes
- Update deployment procedures
- Create runbooks for operations
- Document troubleshooting steps

### Git Standards
- Follow git standards defined in [artifacts]/architect/git-standards.md
- Descriptive commit messages
- Logical commit organization
- Branch: `sprint-1`

---

## Sprint Workflow

### 1. Sprint Initialization
- Review this sprint guide thoroughly
- Understand the Load Balancer + IAP approach
- Identify dependencies and risks
- Create implementation plan
- Set up sprint branch if needed

### 2. Implementation
- Configure Load Balancer
- Configure IAP
- Update DNS
- Deploy Cloud Functions
- Deploy Frontend
- Configure monitoring
- Create session logs

### 3. Validation
- Test Load Balancer routing
- Test IAP authentication
- Test end-to-end functionality
- Verify monitoring
- Check logs for errors

### 4. Documentation
- Document configuration changes
- Update deployment procedures
- Create runbooks
- Create final session log

### 5. Sprint Completion
- Verify all acceptance criteria met
- Ensure all services operational
- Commit all changes
- Push branch to repository
- Notify Docmaster-Sprint

---

## References

### Related Documentation
- [Project Vision](../../../PROJECT_VISION.md)
- [Git Standards]([artifacts]/architect/git-standards.md)

### Previous Sprint Outcomes
- Sprint 6: UI Foundation & Component Organization (blocked by org policy)

### Architecture Documents
- [Domain Definitions]([artifacts]/architect/domain-definitions.md)
- [Escalation Workflow]([artifacts]/architect/escalation-workflow.md)

### External Resources
- [Load Balancer Documentation](https://cloud.google.com/load-balancing/docs)
- [IAP Documentation](https://cloud.google.com/iap/docs)
- [Cloud Functions Documentation](https://cloud.google.com/functions/docs)
- [Firebase Hosting Documentation](https://firebase.google.com/docs/hosting)

---

## Notes

### Important Considerations
- This is a critical fix sprint - application is non-functional without this
- Coordinate with Backend for updated authentication code
- Coordinate with Frontend for Load Balancer URL
- Test thoroughly before considering complete

### Known Issues
- Organization policy blocks `allUsers` access to Cloud Functions
- All API endpoints currently return 403 Forbidden

### Future Work
- Consider additional security enhancements
- Optimize Load Balancer configuration
- Add more comprehensive monitoring

---

**End of Sprint Guide**