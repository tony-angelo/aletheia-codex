# Sprint 4.5 Worker Thread Prompt

Copy everything below this line and paste into your worker thread, then attach:
1. Service account JSON key file

---

# AletheiaCodex Sprint 4.5: Firebase Authentication Implementation

You are a worker thread for the AletheiaCodex project. Your mission is to implement Sprint 4.5: Firebase Authentication.

## 🎯 Sprint Objective

Replace mock authentication with real Firebase Authentication to enable:
- Email/Password sign-in and sign-up
- Google Sign-In
- Proper user authentication
- Notes persisting to Firestore
- Review queue working with real users

## 📋 Required Reading (In Order)

**CRITICAL**: Read these documents in your workspace IN THIS EXACT ORDER:

1. **docs/sprint3/WORKER_THREAD_GUIDELINES.md** - MANDATORY rules for all worker threads
2. **docs/sprint4.5/SPRINT4.5_IMPLEMENTATION_GUIDE.md** - Complete technical specifications

All documents are in the repository.

## 🔑 What You Have

You have been provided with:
1. **Service Account Key**: JSON file with full project access
2. **Repository Access**: Can read/write to GitHub repository
3. **Firebase Configuration**: All values provided below
4. **Project Context**: Sprints 1-4 complete, authentication is broken

## 📊 Current State

### What's Broken
- ❌ Mock authentication only (demo user)
- ❌ Notes don't persist to Firestore
- ❌ Security rules reject writes (no valid auth token)
- ❌ Can't test end-to-end workflow

### Root Cause
Mock authentication doesn't provide valid Firebase Auth tokens:
```typescript
// Current: Mock auth (BROKEN)
const signInMock = (userId: string = 'test-user') => {
  setUser({ uid: userId, ... }); // No real Firebase token
}
```

Firestore security rules require real Firebase Auth:
```javascript
allow create: if isAuthenticated() && request.resource.data.userId == request.auth.uid;
```

Mock auth has no `request.auth.uid` → Writes rejected → Notes never created

### What You're Fixing
- ✅ Real Firebase Authentication
- ✅ Email/Password sign-in
- ✅ Google Sign-In
- ✅ Notes persisting to Firestore
- ✅ Review queue working

## 🔐 Firebase Configuration (Provided by User)

### Firebase Web App Config
```javascript
const firebaseConfig = {
  apiKey: "AIzaSyCPUO0yS3_1BiJyMP96TgDy_tJgrpEvPTY",
  authDomain: "aletheia-codex-prod.firebaseapp.com",
  projectId: "aletheia-codex-prod",
  storageBucket: "aletheia-codex-prod.firebasestorage.app",
  messagingSenderId: "679360092359",
  appId: "1:679360092359:web:9af0ba475c8d03538686e2"
};
```

### Google OAuth Client ID
```
679360092359-76o7ffrihe56t2kq0qp9omvdm48bjkvj.apps.googleusercontent.com
```

### Authorized Domains (Verified by User)
- ✅ aletheia-codex-prod.web.app
- ✅ aletheia-codex-prod.firebaseapp.com
- ✅ localhost

### API Endpoints
```
ORCHESTRATION_URL=https://us-central1-aletheia-codex-prod.cloudfunctions.net/orchestration
REVIEW_API_URL=https://us-central1-aletheia-codex-prod.cloudfunctions.net/review-api
NOTES_API_URL=https://us-central1-aletheia-codex-prod.cloudfunctions.net/notes-api
```

## 🎯 Success Criteria (12 Checkboxes)

Sprint 4.5 is ONLY complete when ALL of these are true:

### Code & Testing
- [ ] Mock authentication code removed
- [ ] Real Firebase Auth implemented
- [ ] Email/Password sign-in working
- [ ] Google Sign-In working
- [ ] Sign-up working
- [ ] Password reset working
- [ ] Sign-out working
- [ ] All tests passing locally

### Deployment
- [ ] Frontend deployed to Firebase Hosting
- [ ] Tested in production

### Production Validation
- [ ] Notes persist to Firestore in production
- [ ] Review queue works with real users in production

### Documentation
- [ ] ONE completion report created using template

**If ANY checkbox is unchecked, the sprint is NOT complete.**

## 🚨 Critical Rules (From WORKER_THREAD_GUIDELINES.md)

### 1. Deploy Everything Before Marking Complete

✅ **DO**: Deploy and test in production
```
Building frontend...
Deploying to Firebase Hosting...
Testing in production...
All tests passing. Sprint complete!
```

❌ **DON'T**: Mark complete without deployment
```
Code is ready. Please deploy and test...
```

### 2. One Completion Report Only

✅ **DO**: Create ONE comprehensive report at the end using `docs/sprint3/COMPLETION_REPORT_TEMPLATE.md`

❌ **DON'T**: Create 12+ status documents

### 3. Create PR Only When 100% Complete

✅ **DO**: PR after full deployment and testing

❌ **DON'T**: PR before production validation

## 📁 Repository Structure

```
aletheia-codex/
├── web/
│   ├── .env.production              # NEW - Firebase config
│   ├── .env.development             # NEW - Firebase config
│   ├── src/
│   │   ├── components/
│   │   │   ├── SignIn.tsx           # NEW - Sign-in UI
│   │   │   ├── SignUp.tsx           # NEW - Sign-up UI
│   │   │   └── Navigation.tsx       # UPDATE - Add sign-out
│   │   ├── hooks/
│   │   │   └── useAuth.ts           # UPDATE - Real Firebase Auth
│   │   ├── firebase/
│   │   │   └── config.ts            # UPDATE - Use env vars
│   │   └── App.tsx                  # UPDATE - Remove mock auth
│   └── .gitignore                   # UPDATE - Ignore .env files
└── docs/
    └── sprint4.5/
        └── COMPLETION_REPORT.md     # CREATE at end
```

## 🔧 Technology Stack

### Frontend
- **React 18**: UI framework
- **TypeScript**: Type safety
- **Firebase SDK**: Authentication
- **Existing**: React Router, custom CSS

### Backend
- **No changes needed**: Backend already expects Firebase Auth tokens

## 📝 Implementation Phases

### Phase 1: Environment Configuration (30 minutes)
1. Create `web/.env.production` with Firebase config
2. Create `web/.env.development` with Firebase config
3. Update `web/src/firebase/config.ts` to use env vars
4. Update `web/.gitignore` to ignore .env files
5. Test locally

### Phase 2: Authentication Hook (1 hour)
1. Update `web/src/hooks/useAuth.ts`
2. Remove mock authentication code
3. Implement real Firebase Auth methods:
   - signInWithEmail
   - signUpWithEmail
   - signInWithGoogle
   - signOut
   - resetPassword
4. Test locally

### Phase 3: Authentication UI (2 hours)
1. Create `web/src/components/SignIn.tsx`
   - Email/password form
   - Google Sign-In button
   - Password reset link
   - Switch to sign-up link
2. Create `web/src/components/SignUp.tsx`
   - Email/password form
   - Display name field
   - Google Sign-In button
   - Switch to sign-in link
3. Test locally

### Phase 4: Update App.tsx (30 minutes)
1. Remove mock authentication code
2. Use real Firebase Auth state
3. Show SignIn/SignUp components when not authenticated
4. Test locally

### Phase 5: Update Navigation (15 minutes)
1. Add sign-out button to Navigation component
2. Show user email/name
3. Test locally

### Phase 6: Local Testing (1 hour)
1. Test email/password sign-up
2. Test email/password sign-in
3. Test Google Sign-In
4. Test password reset
5. Test sign-out
6. Test note creation (should persist!)
7. Test review queue

### Phase 7: Deployment (30 minutes)
1. Build frontend: `npm run build`
2. Deploy to Firebase Hosting: `firebase deploy --only hosting`
3. Verify deployment successful

### Phase 8: Production Testing (30 minutes)
1. Open https://aletheia-codex-prod.web.app
2. Test sign-in/sign-up
3. Test note creation
4. Verify notes persist to Firestore
5. Test review queue
6. Check production logs

### Phase 9: Completion Report (30 minutes)
1. Use template: `docs/sprint3/COMPLETION_REPORT_TEMPLATE.md`
2. Fill ALL sections with production data
3. Verify all 12 checkboxes
4. Create PR
5. Mark sprint complete

## 🎯 Performance Targets

- Sign-in time: <2s
- Sign-up time: <3s
- Google Sign-In: <3s
- Note creation: <500ms (should work now!)

## 🔐 Security Requirements

1. **Environment Variables**: Firebase config in .env files (not in code)
2. **No Secrets in Code**: All sensitive values in environment variables
3. **HTTPS Only**: Firebase handles this automatically
4. **Firestore Rules**: Already configured, will work with real auth
5. **Password Requirements**: Minimum 6 characters (Firebase default)

## 📊 What to Track

### Metrics to Monitor
- Sign-in success rate
- Sign-up success rate
- Google Sign-In success rate
- Note creation success rate (should be 100% now!)
- Error rates

### Logs to Check
- Firebase Authentication logs
- Firestore operation logs
- Frontend console errors
- Cloud Functions logs

## 🚀 Getting Started

### Step 1: Read Documentation (15 minutes)
1. Read `docs/sprint3/WORKER_THREAD_GUIDELINES.md` (MANDATORY)
2. Read `docs/sprint4.5/SPRINT4.5_IMPLEMENTATION_GUIDE.md` (technical specs)

### Step 2: Set Up Environment (15 minutes)
1. Authenticate with service account key
2. Pull latest code from repository
3. Install dependencies: `cd web && npm install`

### Step 3: Create Todo.md (10 minutes)
1. Break down implementation into tasks
2. Organize by phase
3. Add checkboxes for tracking

### Step 4: Implement (3-4 hours)
1. Follow phases in order
2. Test after each phase
3. Commit changes regularly

### Step 5: Deploy & Test (1 hour)
1. Build and deploy to production
2. Test all functionality in production
3. Verify notes persist

### Step 6: Complete (30 minutes)
1. Create ONE completion report using template
2. Fill out ALL sections
3. Verify all 12 checkboxes
4. Create PR
5. Mark sprint complete

## 🆘 When You Need Help

### If Firebase Auth Fails
- Check environment variables are set correctly
- Verify Firebase config matches provided values
- Check browser console for errors
- Verify authorized domains are configured

### If Notes Still Don't Persist
- Verify user is actually authenticated (check `user.uid`)
- Check Firestore security rules
- Verify auth token is being sent to API
- Check Firestore logs for permission errors

### If Google Sign-In Fails
- Verify Google OAuth client ID is correct
- Check authorized domains
- Verify OAuth consent screen is configured
- Check browser allows popups

## ✅ Final Checklist Before Marking Complete

Go through this checklist before marking sprint complete:

- [ ] All 12 success criteria checkboxes are checked
- [ ] Mock authentication code completely removed
- [ ] Real Firebase Auth working in production
- [ ] Notes persist to Firestore in production
- [ ] Review queue works with real users
- [ ] No critical errors in production logs
- [ ] ONE completion report created using template
- [ ] PR created with all changes

**If ANY item is unchecked, the sprint is NOT complete.**

## 🎯 Your Mission

Fix authentication by replacing mock auth with real Firebase Auth. This will unblock:
- ✅ Notes persisting to Firestore
- ✅ Review queue working properly
- ✅ End-to-end testing
- ✅ Production readiness

**Remember**: The sprint is only complete when everything is deployed, tested, and working in production. This is a critical fix that unblocks all other functionality.

**Estimated Time**: 4-6 hours total

Good luck! 🚀

---

**END OF PROMPT** - Attach service account key and begin!