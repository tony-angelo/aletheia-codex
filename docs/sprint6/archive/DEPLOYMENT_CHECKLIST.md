# 📋 Deployment Checklist

Use this checklist to deploy and verify the authentication implementation.

---

## Pre-Deployment ✅

- [x] Code changes complete
- [x] Deployment script created
- [x] Documentation written
- [x] Configuration files ready

---

## Deployment Steps

### Step 1: Prepare Environment
- [ ] Open terminal on your local machine
- [ ] Verify gcloud CLI is installed: `gcloud version`
- [ ] Verify authenticated: `gcloud auth list`
- [ ] Verify project set: `gcloud config get-value project`
  - Should show: `aletheia-codex-prod`

### Step 2: Navigate to Project
- [ ] `cd /path/to/aletheia-codex`
- [ ] Verify you're in the right directory: `ls -la`
  - Should see: `functions/`, `web/`, etc.

### Step 3: Run Deployment Script
- [ ] Make script executable: `chmod +x deploy-authenticated-functions.sh`
- [ ] Run deployment: `./deploy-authenticated-functions.sh`
- [ ] Wait for completion (~10-15 minutes)
- [ ] Note the function URLs displayed at the end

### Step 4: Verify Deployment
- [ ] Check functions are deployed:
  ```bash
  gcloud functions list --project=aletheia-codex-prod
  ```
- [ ] Verify all three functions are listed:
  - [ ] notes-api-function
  - [ ] review-api-function
  - [ ] graph-function

---

## Testing Steps

### Test 1: Unauthenticated Request (Should Fail)
- [ ] Run command:
  ```bash
  curl https://us-central1-aletheia-codex-prod.cloudfunctions.net/graph-function
  ```
- [ ] Verify response:
  - [ ] Status: 401 Unauthorized
  - [ ] Body contains: "Missing Authorization header"

### Test 2: Invalid Token (Should Fail)
- [ ] Run command:
  ```bash
  curl -H "Authorization: Bearer invalid-token" \
    https://us-central1-aletheia-codex-prod.cloudfunctions.net/graph-function
  ```
- [ ] Verify response:
  - [ ] Status: 401 Unauthorized
  - [ ] Body contains: "Invalid authentication token"

### Test 3: Valid Token (Should Succeed)
- [ ] Go to: https://aletheia-codex-prod.web.app
- [ ] Sign in with your account
- [ ] Open browser console (F12)
- [ ] Run: `await firebase.auth().currentUser.getIdToken()`
- [ ] Copy the token
- [ ] Run command with your token:
  ```bash
  curl -H "Authorization: Bearer YOUR_ACTUAL_TOKEN" \
    https://us-central1-aletheia-codex-prod.cloudfunctions.net/graph-function
  ```
- [ ] Verify response:
  - [ ] Status: 200 OK
  - [ ] Body contains: `{"nodes": [...], "total": ...}`

### Test 4: Browser Integration
- [ ] Navigate to: https://aletheia-codex-prod.web.app
- [ ] Sign in
- [ ] Open DevTools (F12)
- [ ] Go to Network tab
- [ ] Navigate to different pages (Notes, Review, etc.)
- [ ] Check API requests:
  - [ ] Requests have `Authorization: Bearer ...` header
  - [ ] Responses are 200 OK (not 401)
  - [ ] Data is loading correctly

---

## Verification Steps

### Check Function Logs
- [ ] View Notes API logs:
  ```bash
  gcloud functions logs read notes-api-function \
    --region=us-central1 --limit=50
  ```
- [ ] Look for: "Authenticated request from user: USER_ID"

- [ ] View Review API logs:
  ```bash
  gcloud functions logs read review-api-function \
    --region=us-central1 --limit=50
  ```
- [ ] Look for: "Authenticated request from user: USER_ID"

- [ ] View Graph API logs:
  ```bash
  gcloud functions logs read graph-function \
    --region=us-central1 --limit=50
  ```
- [ ] Look for: "Authenticated request from user: USER_ID"

### Check for Errors
- [ ] No "Missing Authorization header" errors for authenticated users
- [ ] No "Invalid authentication token" errors for valid tokens
- [ ] No CORS errors in browser console
- [ ] No 401 errors for authenticated requests

---

## Success Criteria

All items below should be checked:

- [ ] All three functions deployed successfully
- [ ] Unauthenticated requests return 401
- [ ] Invalid tokens return 401
- [ ] Valid tokens return 200 with data
- [ ] Frontend can access all APIs
- [ ] Authorization headers present in requests
- [ ] Function logs show authentication events
- [ ] No CORS errors
- [ ] Users can only access their own data

---

## Troubleshooting

### If deployment fails:
1. Check gcloud is authenticated: `gcloud auth list`
2. Check project is set: `gcloud config get-value project`
3. Check you have permissions to deploy functions
4. Check the error message in deployment output

### If authentication fails:
1. Verify token is not expired (tokens expire after 1 hour)
2. Get a fresh token: `await firebase.auth().currentUser.getIdToken(true)`
3. Check Authorization header format: `Bearer <token>` (note the space)
4. Check function logs for specific error messages

### If CORS errors occur:
1. Verify you're accessing from allowed origin
2. Check browser console for specific CORS error
3. Verify function deployed successfully
4. Check function logs for CORS-related messages

---

## Post-Deployment

### Update Frontend (if needed)
- [ ] Verify `graphService.ts` exists (create if needed for Sprint 6)
- [ ] Verify all services use `getAuthHeaders()`
- [ ] Test all API calls from frontend

### Monitor Functions
- [ ] Set up monitoring/alerting (optional)
- [ ] Check function metrics in GCP Console
- [ ] Monitor error rates

### Documentation
- [ ] Update team documentation with function URLs
- [ ] Share authentication testing guide with team
- [ ] Document any issues encountered

---

## Next Steps

After successful deployment:

1. ✅ Continue Sprint 6 development:
   - Create Graph page components
   - Build Dashboard page
   - Build Settings page
   - Organize component library

2. ✅ Monitor function performance:
   - Check logs regularly
   - Monitor error rates
   - Track authentication failures

3. ✅ Iterate and improve:
   - Gather user feedback
   - Optimize performance
   - Add features as needed

---

## Completion

When all items are checked:

- [ ] All deployment steps complete
- [ ] All tests passing
- [ ] All verification steps complete
- [ ] No errors or issues
- [ ] Frontend working correctly
- [ ] Team notified of completion

**Deployment Date**: _______________  
**Deployed By**: _______________  
**Status**: _______________

---

**Estimated Total Time**: 20-25 minutes  
**Difficulty**: Easy (just follow the steps)  
**Support**: See documentation files for help

---

*Use this checklist to ensure nothing is missed during deployment.*