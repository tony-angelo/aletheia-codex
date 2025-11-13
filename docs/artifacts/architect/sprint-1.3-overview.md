# Sprint 1.3 Overview: Cloud Run Migration

**Sprint**: 1.3  
**Goal**: Migrate Cloud Functions to Cloud Run to resolve organization policy blocker  
**Priority**: 🚨 CRITICAL  
**Estimated Duration**: 4-6 hours  
**Status**: Ready to Execute

---

## Sprint Goal

Migrate Python Cloud Functions to Cloud Run services to bypass GCP organization policy restrictions and enable public API access through Firebase Hosting.

---

## Problem Statement

### Current Blocker
- GCP Organization Policy `iam.allowedPolicyMemberDomains` blocks public access to Cloud Functions
- Firebase Hosting cannot rewrite to external URLs (Load Balancer)
- All API endpoints return 403 Forbidden or 404 Not Found
- Application is completely non-functional

### Why Cloud Run Solves This
1. **Not affected by Cloud Functions organization policy**
2. **Firebase Hosting can rewrite to Cloud Run services by name**
3. **Supports public access through Load Balancer**
4. **Better production architecture** (more control, better scaling)

---

## Architecture Change

### Current (Broken)
```
Firebase Hosting → Cloud Functions (BLOCKED by org policy)
```

### Target (Working)
```
Firebase Hosting → Cloud Run Services (public access allowed)
```

---

## Services to Migrate

### 1. Review API
- **Source**: `functions/review_api/main.py`
- **Cloud Run Service**: `review-api`
- **Endpoints**: `/api/review/*`

### 2. Graph API
- **Source**: `functions/graph/main.py`
- **Cloud Run Service**: `graph-api`
- **Endpoints**: `/api/graph/*`

### 3. Notes API
- **Source**: `functions/notes_api/main.py`
- **Cloud Run Service**: `notes-api`
- **Endpoints**: `/api/notes/*`

### 4. Orchestration API
- **Source**: `functions/orchestration/main.py`
- **Cloud Run Service**: `orchestration-api`
- **Endpoints**: `/api/orchestration/*`

---

## Domain Assignments

### Admin-Infrastructure
**Responsibility**: Deploy Cloud Run services and configure Load Balancer

**Tasks**:
1. Create Dockerfiles for each service
2. Build Docker images
3. Push images to Google Container Registry
4. Deploy Cloud Run services
5. Configure public access (allow unauthenticated)
6. Update Load Balancer backends to Cloud Run services
7. Test Cloud Run endpoints directly

**Deliverables**:
- 4 Cloud Run services deployed
- Load Balancer updated with Cloud Run backends
- Public URLs for each service
- Documentation of service URLs

---

### Admin-Frontend
**Responsibility**: Update Firebase Hosting configuration

**Tasks**:
1. Update `firebase.json` rewrites to Cloud Run services
2. Deploy updated Firebase Hosting configuration
3. Test API endpoints through Firebase Hosting
4. Verify end-to-end functionality

**Deliverables**:
- Updated `firebase.json` with Cloud Run rewrites
- Deployed Firebase Hosting configuration
- Working API endpoints
- End-to-end testing results

---

### Admin-Backend
**Responsibility**: Verify authentication and update Cloud Run services if needed

**Tasks**:
1. Review authentication in Cloud Run context
2. Update environment variables for Cloud Run
3. Test authentication with Cloud Run services
4. Verify Firebase Auth integration

**Deliverables**:
- Authentication verified in Cloud Run
- Environment variables configured
- Integration tests passing

---

## Success Criteria

### Must Have ✅
- [ ] All 4 services deployed to Cloud Run
- [ ] Services accessible publicly (no 403 errors)
- [ ] Firebase Hosting rewrites to Cloud Run services
- [ ] API endpoints return JSON (not HTML)
- [ ] Review page loads and displays data
- [ ] User authentication works end-to-end
- [ ] Application fully functional

### Should Have 📋
- [ ] Load Balancer updated with Cloud Run backends
- [ ] Monitoring configured for Cloud Run services
- [ ] Logs accessible in Cloud Logging
- [ ] Documentation updated

### Nice to Have 🎯
- [ ] CI/CD pipeline for Cloud Run deployments
- [ ] Automated testing for Cloud Run services
- [ ] Performance benchmarks

---

## Timeline

### Phase 1: Infrastructure Setup (2-3 hours)
- Admin-Infrastructure creates Dockerfiles
- Admin-Infrastructure builds and deploys Cloud Run services
- Admin-Infrastructure configures public access

### Phase 2: Frontend Integration (1 hour)
- Admin-Frontend updates Firebase Hosting configuration
- Admin-Frontend deploys and tests

### Phase 3: Backend Verification (1 hour)
- Admin-Backend verifies authentication
- Admin-Backend tests integration

### Phase 4: End-to-End Testing (1 hour)
- All admins test functionality
- Verify all endpoints working
- Document results

**Total Estimated Time**: 4-6 hours

---

## Dependencies

### Required Access
- GCP project access (already granted)
- Service account credentials (already configured)
- GitHub repository access (already granted)

### Required Tools
- Docker (for building images)
- gcloud CLI (for deploying to Cloud Run)
- Firebase CLI (for deploying hosting)

### Blockers
- None expected (Cloud Run not affected by organization policy)

---

## Risks & Mitigation

### Risk 1: Docker Build Issues
**Mitigation**: Use official Python base images, test locally first

### Risk 2: Cloud Run Cold Starts
**Mitigation**: Configure minimum instances, use warm-up requests

### Risk 3: Authentication Issues
**Mitigation**: Test Firebase Auth integration thoroughly

### Risk 4: CORS Configuration
**Mitigation**: Configure CORS headers in Cloud Run services

---

## Rollback Plan

If Cloud Run migration fails:
1. Keep existing Cloud Functions (even though blocked)
2. Document issues encountered
3. Escalate to Architect for alternative solution
4. Consider requesting organization policy exception

**Note**: Rollback is unlikely to be needed as Cloud Run is well-tested and documented.

---

## Testing Strategy

### Unit Testing
- Test each Cloud Run service independently
- Verify authentication works
- Test all endpoints

### Integration Testing
- Test Firebase Hosting → Cloud Run flow
- Verify CORS headers
- Test with actual Firebase Auth tokens

### End-to-End Testing
- User login flow
- Review page functionality
- All API operations (GET, POST, PUT, DELETE)

---

## Documentation Requirements

### Admin-Infrastructure
- Dockerfile for each service
- Cloud Run deployment scripts
- Service URLs and configuration
- Load Balancer update documentation

### Admin-Frontend
- Updated `firebase.json` configuration
- Deployment verification steps
- Testing results

### Admin-Backend
- Authentication configuration
- Environment variables
- Integration test results

---

## Post-Sprint Actions

### Immediate
1. Verify application is fully functional
2. Monitor Cloud Run services for issues
3. Document any lessons learned

### Follow-Up
1. Set up monitoring and alerting
2. Configure CI/CD for Cloud Run
3. Optimize Cloud Run configuration (memory, CPU, instances)
4. Review costs and optimize

---

## Related Documents

- `critical-issue-analysis.md` - Root cause analysis
- `sprint-1-completion-analysis.md` - Previous sprint summary
- Sprint guides (to be created for each admin)

---

**Created**: 2025-01-13  
**Author**: Architect  
**Status**: Ready for Execution  
**Priority**: 🚨 CRITICAL