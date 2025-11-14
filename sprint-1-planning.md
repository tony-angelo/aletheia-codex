# Sprint 1 Planning - AletheiaCodex

## Current Project Status Analysis

Based on PROJECT_STATUS.md and PROJECT_VISION.md:

### Completed Work (Sprints 1-6)
- ✅ Backend Cloud Functions deployed and working
- ✅ AI entity extraction (>85% accuracy)
- ✅ Relationship detection (>75% accuracy)
- ✅ Review queue implemented
- ✅ Frontend deployed at https://aletheiacodex.app
- ✅ Firebase Authentication working
- ✅ React UI components created

### Current Blocker (Sprint 6)
- ❌ Organization policy blocks public access to Cloud Functions
- ❌ All API endpoints return 403 Forbidden
- ❌ Frontend cannot communicate with backend

### Root Cause
GCP organization policy `iam.allowedPolicyMemberDomains` prevents `allUsers` access to Cloud Run services (which Cloud Functions Gen 2 uses).

## Sprint 1 Goal

**Resolve the organization policy blocker and restore full application functionality**

This is the highest priority issue because the application is currently non-functional. Users cannot use any features because the frontend cannot communicate with the backend.

## Sprint 1 Features

### Backend Domain
1. **Implement IAP-Compatible Authentication**
   - Modify Cloud Functions to work with Identity-Aware Proxy
   - Update authentication middleware
   - Test with IAP configuration

2. **Alternative: Adjust Access Pattern**
   - If IAP is not feasible, implement alternative access pattern
   - Ensure compliance with organization policy
   - Maintain security standards

### Frontend Domain
1. **Update API Client for New Authentication**
   - Modify API client to work with new authentication
   - Update token handling
   - Test API connectivity

2. **Verify All Features Work**
   - Test note creation
   - Test review queue
   - Test knowledge graph
   - Ensure end-to-end functionality

### Infrastructure Domain
1. **Configure Load Balancer + IAP**
   - Set up Load Balancer
   - Configure Identity-Aware Proxy
   - Update DNS and routing
   - Test access patterns

2. **Alternative: Adjust Organization Policy**
   - If feasible, work with organization admin
   - Document policy requirements
   - Implement approved solution

3. **Validate Deployment**
   - Ensure all services accessible
   - Verify security rules
   - Test end-to-end connectivity
   - Monitor for errors

## Success Criteria

- [ ] Frontend can successfully call backend API endpoints
- [ ] Users can create notes
- [ ] Users can view review queue
- [ ] Users can approve/reject entities
- [ ] Users can view knowledge graph
- [ ] All API endpoints return appropriate responses (not 403)
- [ ] Application is fully functional end-to-end
- [ ] Security is maintained
- [ ] Organization policy compliance achieved

## Timeline

**Estimated Duration**: 2-3 days

**Priority**: CRITICAL - Application is non-functional without this fix