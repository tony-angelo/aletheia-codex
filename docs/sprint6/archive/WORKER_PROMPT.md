# Sprint 6 Worker Prompt: Functional UI Foundation

**READ THIS FIRST**: This is your complete briefing for Sprint 6. Everything you need is in this file or referenced from it.

---

## Mission Statement

**Build a functional UI foundation** with all pages, organized component library, and documented function library. This prepares the codebase for AI-assisted redesign in Sprint 7.

**Key Principle**: **Functional Over Beautiful** - Focus on making everything work, not making it pretty.

---

## Critical Context

### What Sprint 5 Accomplished
✅ Note processing workflow fixed and working  
✅ AI extraction functional (4 entities extracted from test)  
✅ Review queue populated automatically  
✅ Firestore trigger working perfectly  

### What's Missing (Sprint 6 Scope)
❌ Knowledge Graph page (currently just "Coming Soon" placeholder)  
❌ Dashboard/Home page with overview  
❌ User Profile/Settings page  
❌ Component library organization  
❌ Function library documentation  
❌ Filters and sorting on existing pages  

### Why This Sprint Matters
Sprint 5 proved the **core workflow works**. Now we need to complete the UI and organize the codebase so a design AI can analyze and improve it in Sprint 7.

---

## Success Criteria (9 Checkboxes)

Sprint 6 is ONLY complete when ALL 9 criteria are met:

### 0. ✅ Authentication Implemented (PREREQUISITE)
- Backend functions use `@require_auth` decorator
- Frontend services send Authorization headers
- Functions deployed without `--allow-unauthenticated`
- Authentication tested and working in production
- Authenticated requests succeed (200 OK)
- Unauthenticated requests fail (401 Unauthorized)

### 1. ✅ All Pages Functional
- Dashboard/Home page with overview statistics
- Knowledge Graph page with node browser and details view
- User Profile/Settings page with user information
- Enhanced NotesPage with filters and sorting
- Enhanced ReviewPage with bulk actions

### 2. ✅ Component Library Organized
- Components categorized into logical folders (common/, layout/, features/)
- Component documentation created (README.md in components/)
- Naming conventions established and documented
- Reusable patterns identified and documented

### 3. ✅ Function Library Documented
- All utility functions documented with JSDoc comments
- Function library reference created (README.md in utils/)
- Common patterns established and documented
- Code is AI-analyzable (clear structure, good naming)

### 4. ✅ Navigation Working
- All pages accessible via navigation menu
- Active page highlighting
- Breadcrumbs where appropriate
- Mobile-responsive navigation

### 5. ✅ Basic Testing
- Critical components have unit tests
- Testing patterns established
- Test documentation created
- All tests passing

### 6. ✅ UI Consistency
- Consistent styling across all pages (same color scheme, typography)
- Loading states for all async operations
- Error messages for all failure scenarios
- Toast notifications for user feedback

### 7. ✅ Deployed to Production
- All changes deployed to Firebase Hosting
- All pages tested in production environment
- No critical errors in production
- Performance acceptable (page load < 3s)

### 8. ✅ Documentation Complete
- Component library README with examples
- Function library README with API docs
- Architecture documentation updated
- Completion report created with screenshots

---

## Mandatory Reading Order

### 1st: Read This File (You're Here)
Get the mission, context, and completion criteria.

### 2nd: Read Worker Thread Guidelines
**Location**: `docs/WORKER_THREAD_GUIDELINES.md`

**Critical Rules**:
- Sprint is NOT complete until fully deployed and tested in production
- Request IAM roles/permissions when needed - don't ask user to do manual work
- Create PR only when 100% complete
- ONE completion report only

### 3rd: Read Implementation Guide
**Location**: `docs/sprint6/SPRINT6_IMPLEMENTATION_GUIDE.md`

**Contains**:
- Detailed technical specifications for each phase
- Code examples for all new components
- API endpoint specifications
- Testing strategy
- Deployment instructions

### 4th: Reference Documentation (As Needed)
**Location**: `docs/sprint6/REFERENCE_DOCS.md`

**Contains**:
- Links to all project documentation
- Component patterns and examples
- API specifications
- External resources

---

## Implementation Phases

### Phase 1: Knowledge Graph Page (Days 1-3)
**Goal**: Build functional Knowledge Graph page with node browsing

**Key Deliverables**:
1. Create Graph API endpoint (Cloud Function)
   - GET /nodes - List nodes
   - GET /nodes/{id} - Node details
   - GET /search - Search nodes

2. Create Graph Service (TypeScript)
   - graphService.ts with API client functions

3. Create Graph Components
   - NodeBrowser.tsx - Browse and search nodes
   - NodeDetails.tsx - Detailed node view
   - Update GraphPage.tsx - Replace placeholder

**Success Criteria**:
- User can browse nodes from Neo4j
- User can search nodes by name
- User can view node details with relationships
- All functionality tested in production

### Phase 2: Dashboard & Settings Pages (Days 4-7)
**Goal**: Complete the application with Dashboard and Settings pages

**Key Deliverables**:
1. Create Dashboard Page
   - Overview statistics (notes, entities, relationships)
   - Recent activity
   - Quick actions

2. Create Settings Page
   - User profile information
   - Account settings
   - Preferences

3. Update Navigation
   - Add Dashboard and Settings links
   - Update active page highlighting

**Success Criteria**:
- Dashboard shows accurate statistics
- Settings page allows profile updates
- Navigation includes all pages
- All pages accessible and functional

### Phase 3: Component Library Organization (Days 8-10)
**Goal**: Organize components into logical structure

**Key Deliverables**:
1. Reorganize Components
   - Move to common/, layout/, features/ folders
   - Update all import paths
   - Ensure no broken imports

2. Create Component Documentation
   - README.md in components/ folder
   - Document each component category
   - Establish naming conventions
   - Document common patterns

**Success Criteria**:
- All components organized logically
- No broken imports
- Component README complete
- Code is AI-analyzable

### Phase 4: Function Library Documentation (Days 11-12)
**Goal**: Document all utility functions

**Key Deliverables**:
1. Add JSDoc Comments
   - Document all functions with parameters and return types
   - Add usage examples

2. Create Function Library README
   - README.md in utils/ folder
   - Document all utility categories
   - Provide API reference
   - Document common patterns

**Success Criteria**:
- All functions have JSDoc comments
- Function library README complete
- Common patterns documented
- Code is AI-analyzable

### Phase 5: Testing & Deployment (Days 13-14)
**Goal**: Ensure quality and deploy to production

**Key Deliverables**:
1. Add Basic Tests
   - Test critical components
   - Establish testing patterns
   - Document testing approach

2. Ensure UI Consistency
   - Consistent styling across pages
   - Loading states everywhere
   - Error messages everywhere
   - Toast notifications working

3. Deploy to Production
   - Build and deploy frontend
   - Deploy new Cloud Functions
   - Test all pages in production
   - Verify performance

**Success Criteria**:
- All tests passing
- UI consistent across pages
- Deployed to production
- No critical errors
- Performance acceptable

---

## Key Technical Details

### Current State

**Existing Pages** (3):
1. NotesPage - Functional
2. ReviewPage - Functional
3. GraphPage - Placeholder only

**Existing Components** (13):
- All in flat structure (no organization)
- No documentation
- No clear patterns

**Missing**:
- Knowledge Graph functionality
- Dashboard page
- Settings page
- Component organization
- Function documentation

### New Architecture

**Component Structure**:
```
web/src/components/
├── common/           # Shared UI (Button, Card, Input, etc.)
├── layout/           # Layout (Navigation, Header, Footer)
├── features/         # Feature-specific
│   ├── notes/       # Note components
│   ├── review/      # Review components
│   ├── graph/       # Graph components (NEW)
│   └── auth/        # Auth components
└── README.md        # Documentation
```

**New API Endpoints**:
- Graph Function (NEW)
  - GET /nodes
  - GET /nodes/{id}
  - GET /search

**New Pages**:
- DashboardPage (NEW)
- SettingsPage (NEW)
- GraphPage (REPLACE PLACEHOLDER)

---

## Testing Requirements

### Manual Testing
Before marking any phase complete, you MUST:
1. Test in browser with console open
2. Test all new pages and features
3. Test navigation between pages
4. Test responsive design (mobile, tablet, desktop)
5. Test error scenarios
6. Test loading states
7. Verify in production environment

### Automated Testing
Create basic tests for:
1. Critical components (NoteInput, ReviewQueue, NodeBrowser)
2. Utility functions
3. Service functions

### Production Testing
After deployment:
1. Test all pages live
2. Check browser console for errors
3. Verify performance (page load < 3s)
4. Test on different devices
5. Verify all functionality works

---

## Deployment

### Frontend Deployment
```bash
cd web
npm run build
firebase deploy --only hosting
```

### Backend Deployment
```bash
# Deploy graph function
cd functions/graph
gcloud functions deploy graph-function \
  --gen2 \
  --runtime=python311 \
  --region=us-central1 \
  --source=. \
  --entry-point=graph_function \
  --trigger-http \
  --allow-unauthenticated \
  --service-account=aletheia-functions@aletheia-codex-prod.iam.gserviceaccount.com \
  --set-env-vars GCP_PROJECT=aletheia-codex-prod \
  --memory=256MB \
  --timeout=60s
```

---

## Handling Blockers

### If You Need IAM Permissions
**DO THIS**:
```
I need the following IAM role to proceed:
- Role: roles/cloudfunctions.developer
- Service Account: aletheia-functions@aletheia-codex-prod.iam.gserviceaccount.com
- Reason: To deploy new Cloud Functions

Command to grant:
gcloud projects add-iam-policy-binding aletheia-codex-prod \
  --member="serviceAccount:aletheia-functions@aletheia-codex-prod.iam.gserviceaccount.com" \
  --role="roles/cloudfunctions.developer"

Please run this command and let me know when complete.
```

**DON'T DO THIS**:
```
Can you deploy the Cloud Function manually? Here are the steps...
```

### If You Need API Keys
**DO THIS**:
```
I need access to Neo4j credentials. Please verify they exist in Secret Manager:
- neo4j-uri
- neo4j-user
- neo4j-password

If missing, please add them and let me know when complete.
```

### If You Encounter Errors
**DO THIS**:
1. Log the full error with stack trace
2. Investigate the root cause
3. Implement a fix
4. Test the fix
5. Document the solution

**DON'T DO THIS**:
1. Mark the task as complete with errors
2. Ask user to debug
3. Skip error handling

---

## Completion Requirements

### Before Creating PR
- [ ] All 8 success criteria checkboxes are ✅
- [ ] All code changes committed
- [ ] All functions deployed to production
- [ ] Frontend deployed to production
- [ ] All pages tested in production
- [ ] All tests passing
- [ ] No critical errors in production
- [ ] Performance acceptable (page load < 3s)

### PR Requirements
- [ ] Clear title: "Sprint 6: Functional UI Foundation"
- [ ] Description includes:
  - What was built
  - Screenshots of new pages
  - How to test
  - Links to deployed pages
- [ ] All files included
- [ ] No merge conflicts

### Completion Report Requirements
Create ONE completion report with:
1. **Summary**: What was accomplished
2. **New Features**: List of new pages and components
3. **Organization**: How components were reorganized
4. **Documentation**: What was documented
5. **Testing Results**: Evidence that everything works
6. **Deployment Status**: All deployments complete
7. **Screenshots**: Screenshots of all new pages
8. **Next Steps**: Recommendations for Sprint 7

**DO NOT CREATE**:
- Multiple status reports
- Daily updates
- Progress reports
- Intermediate summaries

---

## Common Pitfalls to Avoid

### ❌ DON'T
1. Make it pretty (that's Sprint 7)
2. Add features not in scope
3. Optimize performance (that's Sprint 7)
4. Redesign existing pages (that's Sprint 7)
5. Create 12+ status documents
6. Mark complete without production testing

### ✅ DO
1. Focus on functionality
2. Organize components logically
3. Document everything
4. Test thoroughly
5. Deploy to production
6. Create ONE completion report

---

## Key Principles

1. **Functional Over Beautiful**: Make it work, not pretty
2. **Organization Over Optimization**: Structure, not performance
3. **Documentation Over Perfection**: Document what exists
4. **AI-Ready**: Structure code for AI analysis

---

## Resources

### Documentation
- Implementation Guide: `docs/sprint6/SPRINT6_IMPLEMENTATION_GUIDE.md`
- Worker Guidelines: `docs/WORKER_THREAD_GUIDELINES.md`
- Reference Docs: `docs/sprint6/REFERENCE_DOCS.md`
- Sprint 5 Completion: `docs/sprint5/SPRINT5_COMPLETION_REPORT.md`

### Tools
- [Firebase Console](https://console.firebase.google.com/project/aletheia-codex-prod)
- [Google Cloud Console](https://console.cloud.google.com/home/dashboard?project=aletheia-codex-prod)
- [Neo4j Aura Console](https://console.neo4j.io/)

### Commands
```bash
# Deploy frontend
cd web && npm run build && firebase deploy --only hosting

# Deploy function
cd functions/graph && gcloud functions deploy graph-function --gen2 --runtime=python311 --region=us-central1 --source=. --entry-point=graph_function --trigger-http --allow-unauthenticated

# Run tests
cd web && npm test

# Check logs
gcloud functions logs read graph-function --project aletheia-codex-prod --limit 100
```

---

## Final Checklist Before Starting

- [ ] Read this entire file
- [ ] Read WORKER_THREAD_GUIDELINES.md
- [ ] Read SPRINT6_IMPLEMENTATION_GUIDE.md
- [ ] Understand the 8 success criteria
- [ ] Know how to handle blockers
- [ ] Ready to organize components
- [ ] Ready to document functions
- [ ] Ready to test in production
- [ ] Ready to create ONE completion report

---

## Questions?

If you're unclear about anything:
1. Check the Implementation Guide
2. Check the Reference Docs
3. Check Sprint 5 documentation
4. If still unclear, ask for clarification

**Remember**: This sprint is about completing the UI and organizing the codebase, not making it beautiful. The redesign happens in Sprint 7.

---

**Good luck! Let's build a solid foundation! 🚀**