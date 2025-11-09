# Sprint 4.5: Firebase Authentication Implementation

## 📋 Quick Start for Worker Threads

### Your Workflow:
1. Open `WORKER_PROMPT.md` in this directory
2. Copy the entire prompt
3. Paste into new worker thread
4. Attach service account JSON key
5. Click begin

---

## 🎯 Sprint 4.5 Objectives

Fix authentication by replacing mock auth with real Firebase Authentication:
- Email/Password sign-in and sign-up
- Google Sign-In
- Proper user authentication
- Notes persisting to Firestore
- Review queue working with real users

---

## 🚨 Why This Sprint is Critical

### Current Problem
- Mock authentication doesn't provide valid Firebase tokens
- Firestore security rules reject writes without valid auth
- Notes don't persist to database
- Review queue doesn't work
- Can't test end-to-end workflow

### Root Cause
```typescript
// Mock auth (BROKEN)
const signInMock = (userId: string = 'test-user') => {
  setUser({ uid: userId, ... }); // No real Firebase token
}
```

Firestore rules require real auth:
```javascript
allow create: if request.auth.uid == resource.data.userId;
```

Mock auth has no `request.auth.uid` → Writes rejected → Notes never created

---

## 📊 Success Criteria

Sprint 4.5 is complete when:
- ✅ Email/Password sign-in works
- ✅ Google Sign-In works
- ✅ Sign-up creates new users
- ✅ Password reset works
- ✅ Sign-out works
- ✅ Notes persist to Firestore
- ✅ Review queue works with real users
- ✅ Deployed to production
- ✅ Tested in production
- ✅ All 12 checkboxes complete

---

## 🔐 Firebase Configuration (Provided)

### Firebase Web App Config
```javascript
apiKey: "AIzaSyCPUO0yS3_1BiJyMP96TgDy_tJgrpEvPTY"
authDomain: "aletheia-codex-prod.firebaseapp.com"
projectId: "aletheia-codex-prod"
storageBucket: "aletheia-codex-prod.firebasestorage.app"
messagingSenderId: "679360092359"
appId: "1:679360092359:web:9af0ba475c8d03538686e2"
```

### Google OAuth Client ID
```
679360092359-76o7ffrihe56t2kq0qp9omvdm48bjkvj.apps.googleusercontent.com
```

### Authorized Domains
- ✅ aletheia-codex-prod.web.app
- ✅ aletheia-codex-prod.firebaseapp.com
- ✅ localhost

---

## 🚀 What Gets Built

### New Components
```
web/src/components/
├── SignIn.tsx           # Email/password + Google sign-in
└── SignUp.tsx           # User registration

web/
├── .env.production      # Firebase config
└── .env.development     # Firebase config
```

### Updated Components
```
web/src/
├── hooks/useAuth.ts     # Real Firebase Auth (remove mock)
├── firebase/config.ts   # Use environment variables
├── App.tsx              # Remove mock auth
└── components/Navigation.tsx  # Add sign-out
```

---

## ⏱️ Timeline

**Total Duration**: 4-6 hours

- **Phase 1**: Environment Configuration (30 min)
- **Phase 2**: Authentication Hook (1 hour)
- **Phase 3**: Authentication UI (2 hours)
- **Phase 4**: Update App.tsx (30 min)
- **Phase 5**: Update Navigation (15 min)
- **Phase 6**: Local Testing (1 hour)
- **Phase 7**: Deployment (30 min)
- **Phase 8**: Production Testing (30 min)
- **Phase 9**: Completion Report (30 min)

---

## 🔧 Technology Stack

### Frontend
- React 18 + TypeScript
- Firebase SDK (Authentication)
- Existing: React Router, custom CSS

### Backend
- No changes needed (already expects Firebase Auth tokens)

---

## 📝 Testing Checklist

### Local Testing
- [ ] Sign up with email/password
- [ ] Sign in with email/password
- [ ] Sign in with Google
- [ ] Password reset
- [ ] Sign out
- [ ] Create note (should persist!)
- [ ] View note history
- [ ] Navigate between pages

### Production Testing
- [ ] Sign in works in production
- [ ] Notes persist to Firestore
- [ ] Review queue works
- [ ] No errors in console
- [ ] No errors in logs

---

## 🎯 Expected Outcome

After Sprint 4.5:
- ✅ Users can sign in with email/password
- ✅ Users can sign in with Google
- ✅ Notes persist to Firestore
- ✅ Review queue works with real users
- ✅ Security rules properly enforced
- ✅ No more mock authentication
- ✅ End-to-end workflow functional

---

## 📚 Documentation in This Directory

### For Worker Threads (Read in Order):
1. **WORKER_PROMPT.md** - Complete prompt to copy/paste (START HERE)
2. **docs/sprint3/WORKER_THREAD_GUIDELINES.md** - MANDATORY rules
3. **SPRINT4.5_IMPLEMENTATION_GUIDE.md** - Technical specifications

### For Orchestrator:
- Sprint planning and coordination documents
- Reference materials for briefing workers

---

## 🔑 Prerequisites

Before starting Sprint 4.5:
- ✅ Sprint 4 complete (code exists, auth is broken)
- ✅ Firebase Auth providers enabled (Email/Password, Google)
- ✅ Firebase web app configuration obtained
- ✅ Authorized domains configured
- ✅ Service account key available
- ✅ Repository access configured

---

## 📞 Questions?

If you need clarification:
1. Check WORKER_THREAD_GUIDELINES.md first
2. Check SPRINT4.5_IMPLEMENTATION_GUIDE.md for technical details
3. Ask the orchestrator (user) for clarification

---

**Ready to start?** Open `WORKER_PROMPT.md` and follow the instructions!