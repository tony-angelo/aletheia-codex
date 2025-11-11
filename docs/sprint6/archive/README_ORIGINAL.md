# Sprint 6: Functional UI Foundation

**Status**: Ready for Implementation  
**Duration**: 2-3 weeks  
**Objective**: Build functional UI foundation with all pages, organized component library, and documented function library

---

## Quick Start

### For Worker Thread
1. **Read**: `WORKER_PROMPT.md` (start here - everything you need)
2. **Reference**: `SPRINT6_IMPLEMENTATION_GUIDE.md` (detailed technical specs)
3. **Lookup**: `REFERENCE_DOCS.md` (links to all other documentation)

### For Orchestrator/User
- **Worker Brief**: `WORKER_PROMPT.md` - Copy/paste this to worker thread
- **Implementation Guide**: `SPRINT6_IMPLEMENTATION_GUIDE.md` - Technical details
- **Reference Hub**: `REFERENCE_DOCS.md` - All documentation links

---

## What's This Sprint About?

Sprint 5 proved the **core workflow works** (note processing, AI extraction, review queue). Now we need to:

1. **Complete the UI** - Build missing pages (Graph, Dashboard, Settings)
2. **Organize Components** - Restructure into logical categories
3. **Document Functions** - Create function library documentation
4. **Prepare for AI** - Structure code for AI-assisted redesign in Sprint 7

**Key Principle**: **Functional Over Beautiful** - Make it work, not pretty.

---

## Success Criteria (8 Checkboxes)

Sprint 6 is complete when ALL of these work:

1. ✅ **All Pages Functional** - Dashboard, Graph, Settings, enhanced Notes/Review
2. ✅ **Component Library Organized** - Categorized, documented, clear patterns
3. ✅ **Function Library Documented** - JSDoc comments, README, API reference
4. ✅ **Navigation Working** - All pages accessible, active highlighting
5. ✅ **Basic Testing** - Critical components tested, patterns established
6. ✅ **UI Consistency** - Consistent styling, loading states, error messages
7. ✅ **Deployed to Production** - All changes live, tested, no errors
8. ✅ **Documentation Complete** - Component/function READMEs, completion report

---

## Implementation Phases

### Phase 1: Knowledge Graph Page (Days 1-3)
**Goal**: Build functional Knowledge Graph page

**Deliverables**:
- Graph API endpoint (Cloud Function)
- Graph service (TypeScript)
- NodeBrowser component
- NodeDetails component
- Updated GraphPage

### Phase 2: Dashboard & Settings (Days 4-7)
**Goal**: Complete the application

**Deliverables**:
- Dashboard page with statistics
- Settings page with profile
- Updated navigation
- All pages accessible

### Phase 3: Component Organization (Days 8-10)
**Goal**: Organize component library

**Deliverables**:
- Reorganize into common/, layout/, features/
- Component documentation (README)
- Naming conventions
- Pattern documentation

### Phase 4: Function Documentation (Days 11-12)
**Goal**: Document utility functions

**Deliverables**:
- JSDoc comments on all functions
- Function library README
- API reference
- Common patterns

### Phase 5: Testing & Deployment (Days 13-14)
**Goal**: Ensure quality and deploy

**Deliverables**:
- Basic tests for critical components
- UI consistency across pages
- Production deployment
- Completion report

---

## Current State

### Existing (3 pages, 13 components)
- ✅ NotesPage - Functional
- ✅ ReviewPage - Functional
- ⚠️ GraphPage - Placeholder only
- 13 components in flat structure (no organization)

### Missing (Sprint 6 Scope)
- ❌ Knowledge Graph functionality
- ❌ Dashboard page
- ❌ Settings page
- ❌ Component organization
- ❌ Function documentation

---

## New Architecture

### Component Structure
```
web/src/components/
├── common/           # Shared UI (Button, Card, Input)
├── layout/           # Layout (Navigation, Header)
├── features/         # Feature-specific
│   ├── notes/       # Note components
│   ├── review/      # Review components
│   ├── graph/       # Graph components (NEW)
│   └── auth/        # Auth components
└── README.md        # Documentation
```

### New Pages
- DashboardPage (NEW)
- SettingsPage (NEW)
- GraphPage (REPLACE PLACEHOLDER)

### New API
- Graph Function (NEW)
  - GET /nodes
  - GET /nodes/{id}
  - GET /search

---

## Key Files

### Documentation
- `WORKER_PROMPT.md` - Start here (single-file briefing)
- `SPRINT6_IMPLEMENTATION_GUIDE.md` - Detailed technical specs
- `REFERENCE_DOCS.md` - Links to all other docs
- `COMPLETION_REPORT_TEMPLATE.md` - Template for completion report

### Code to Create
**Backend**:
- `functions/graph/main.py` - Graph API endpoint

**Frontend**:
- `web/src/pages/DashboardPage.tsx`
- `web/src/pages/SettingsPage.tsx`
- `web/src/pages/GraphPage.tsx` (replace)
- `web/src/components/features/graph/NodeBrowser.tsx`
- `web/src/components/features/graph/NodeDetails.tsx`
- `web/src/services/graphService.ts`

**Documentation**:
- `web/src/components/README.md`
- `web/src/utils/README.md`

---

## Testing

### Manual Testing
1. Test all pages in browser
2. Test navigation between pages
3. Test responsive design
4. Test error scenarios
5. Test loading states
6. Verify in production

### Automated Testing
```bash
cd web
npm test
```

### Production Testing
```bash
# Deploy and test
cd web
npm run build
firebase deploy --only hosting
```

---

## Deployment

### Frontend
```bash
cd web
npm run build
firebase deploy --only hosting
```

### Backend
```bash
cd functions/graph
gcloud functions deploy graph-function \
  --gen2 \
  --runtime=python311 \
  --region=us-central1 \
  --source=. \
  --entry-point=graph_function \
  --trigger-http \
  --allow-unauthenticated
```

---

## Common Issues

### Import Path Errors
**Solution**: Update imports after reorganization

### CORS Errors
**Solution**: Add CORS headers to Cloud Function

### Authentication Failures
**Solution**: Ensure Firebase token is sent

### Build Failures
**Solution**: Check TypeScript errors

---

## Resources

### Documentation
- [Worker Thread Guidelines](../WORKER_THREAD_GUIDELINES.md)
- [Sprint 5 Completion](../sprint5/SPRINT5_COMPLETION_REPORT.md)
- [Architecture Overview](../02_Architecture_Overview.md)

### Tools
- [Firebase Console](https://console.firebase.google.com/project/aletheia-codex-prod)
- [Google Cloud Console](https://console.cloud.google.com/home/dashboard?project=aletheia-codex-prod)
- [Neo4j Aura](https://console.neo4j.io/)

### External Docs
- [React Documentation](https://react.dev/)
- [TypeScript Documentation](https://www.typescriptlang.org/docs/)
- [Tailwind CSS](https://tailwindcss.com/docs)

---

## Next Steps After Sprint 6

Once Sprint 6 is complete:

**Sprint 7**: UI Redesign
- Use design AI to analyze existing components
- Propose UI/UX improvements
- Implement professional redesign
- Polish and refine

---

**Let's build a solid foundation! 🚀**