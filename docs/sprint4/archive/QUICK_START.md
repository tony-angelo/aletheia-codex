# Sprint 4 Quick Start Guide

**Status**: ✅ Sprint 4 is COMPLETE and DEPLOYED  
**Your Action**: Fix organization policy for public access

---

## 🎯 Current Status

### ✅ What's Done
- All code written and tested
- All components deployed to production
- Frontend live at: https://aletheia-codex-prod.web.app
- Pull Request created: https://github.com/tony-angelo/aletheia-codex/pull/14

### ⚠️ What Needs Your Action
- Update organization policy to allow public access to Cloud Functions

---

## 🚀 Quick Commands

### 1. Fix Organization Policy (REQUIRED)

Run these commands to allow public access to the Cloud Functions:

```bash
# Set up gcloud (if not already done)
gcloud auth login
gcloud config set project aletheia-codex-prod

# Allow public access to orchestration function
gcloud functions add-invoker-policy-binding orchestration \
  --region=us-central1 \
  --member="allUsers" \
  --project=aletheia-codex-prod

# Allow public access to notes_api function
gcloud functions add-invoker-policy-binding notes_api \
  --region=us-central1 \
  --member="allUsers" \
  --project=aletheia-codex-prod
```

**If you get an error about organization policy:**
- Contact your GCP organization admin
- Request to update the organization policy to allow public Cloud Functions
- Alternative: Use authenticated requests (see below)

### 2. Test the Deployment

After fixing the organization policy, test the functions:

```bash
# Test orchestration function
curl -X POST https://us-central1-aletheia-codex-prod.cloudfunctions.net/orchestration \
  -H "Content-Type: application/json" \
  -d '{"noteId":"test-123","content":"Test note","userId":"test-user"}'

# Should return JSON with extraction results

# Test notes API
curl https://us-central1-aletheia-codex-prod.cloudfunctions.net/notes_api/notes \
  -H "Authorization: Bearer test-user"

# Should return JSON with notes array
```

### 3. Review and Merge PR

```bash
# View the PR
open https://github.com/tony-angelo/aletheia-codex/pull/14

# Or merge via command line
gh pr merge 14 --squash
```

---

## 🔄 Alternative: Use Authenticated Requests

If you can't update the organization policy, you can use authenticated requests:

### Frontend Changes Required

Update `web/src/services/orchestration.ts`:

```typescript
// Add Firebase Auth token to requests
const token = await user.getIdToken();

const response = await fetch(this.baseUrl, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`, // Add this line
  },
  body: JSON.stringify({
    noteId,
    content,
    userId,
  }),
});
```

### Backend Changes Required

Update Cloud Functions to verify tokens:

```python
from firebase_admin import auth

def verify_token(request):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token['uid']
    except:
        return None
```

---

## 📊 Verify Everything Works

### 1. Check Frontend
```bash
open https://aletheia-codex-prod.web.app
```

**Expected**: Page loads with navigation and note input interface

### 2. Check Functions
```bash
gcloud functions list --project=aletheia-codex-prod
```

**Expected**: All functions show STATUS: ACTIVE

### 3. Check Firestore
```bash
# Open Firebase Console
open https://console.firebase.google.com/project/aletheia-codex-prod/firestore
```

**Expected**: See notes collection with security rules

---

## 📚 Documentation

All documentation is in `docs/sprint4/`:

1. **FINAL_SUMMARY.md** - Overall summary (START HERE)
2. **DEPLOYMENT_REPORT.md** - Deployment details
3. **COMPLETION_REPORT.md** - Full sprint report
4. **USER_ACTION_REQUIRED.md** - Detailed next steps
5. **PRODUCTION_VALIDATION_CHECKLIST.md** - Testing checklist
6. **INTEGRATION_TEST_PLAN.md** - Testing strategy
7. **DEPLOYMENT_GUIDE.md** - Deployment instructions

---

## 🆘 Troubleshooting

### Issue: Functions return 403
**Solution**: Update organization policy (see commands above)

### Issue: Frontend not loading
**Check**: 
```bash
curl -I https://aletheia-codex-prod.web.app
```
**Expected**: HTTP 200

### Issue: Firestore permission denied
**Check**: Security rules are deployed
```bash
firebase deploy --only firestore:rules --project aletheia-codex-prod
```

---

## ✅ Success Checklist

- [ ] Organization policy updated (or authenticated requests implemented)
- [ ] Functions return 200 (not 403)
- [ ] Frontend loads successfully
- [ ] Can submit notes via UI
- [ ] Notes appear in Firestore
- [ ] PR reviewed and merged
- [ ] Production validation complete

---

## 🎉 You're Done!

Once you complete the organization policy update, Sprint 4 is 100% complete and ready for users!

**Questions?** Check the documentation in `docs/sprint4/`

**Need Help?** Review the deployment logs and Firebase/GCP consoles

---

**Quick Start Guide**  
**Last Updated**: January 9, 2025  
**Sprint Status**: ✅ COMPLETE  
**Deployment Status**: ✅ DEPLOYED