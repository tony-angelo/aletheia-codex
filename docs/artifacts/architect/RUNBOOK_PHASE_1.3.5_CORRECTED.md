# Runbook: Phase 1.3.5 - Update Firebase Hosting Configuration (CORRECTED)

**Phase**: 1.3.5  
**Objective**: Verify and deploy Firebase Hosting configuration with Cloud Run proxy  
**Estimated Duration**: 10 minutes  
**Prerequisites**: Phase 1.3.4 complete (Cloud Run service updated with `--no-invoker-iam-check`)

---

## ⚠️ IMPORTANT DISCOVERY

The `firebase.json` file is **already configured correctly** with the Cloud Run proxy! The configuration shows:

```json
"rewrites": [
  {
    "source": "/api/review/**",
    "run": {
      "serviceId": "review-api",
      "region": "us-central1",
      "invoker": "firebase-invoker@aletheia-codex-prod.iam.gserviceaccount.com"
    }
  }
]
```

**This means Phase 1.3.5 configuration is already complete. We only need to build and deploy.**

---

## Prerequisites Checklist

- [x] Phase 1.3.4 complete (Cloud Run service has `--no-invoker-iam-check` applied)
- [ ] Access to Cloud Shell
- [ ] Authenticated with `gcloud` CLI
- [ ] Firebase CLI installed
- [ ] On `sprint-1` branch

---

## Corrected Steps

### Step 1: Navigate to Project (Root Directory)
```bash
cd ~/aletheia-codex
git checkout sprint-1
git pull origin sprint-1
```

**Note**: `firebase.json` is in the **root directory**, not in `web/`

---

### Step 2: Verify Configuration (Already Complete)
```bash
cat firebase.json | grep -A 8 '"rewrites"'
```

**Expected Output**:
```json
"rewrites": [
  {
    "source": "/api/review/**",
    "run": {
      "serviceId": "review-api",
      "region": "us-central1",
      "invoker": "firebase-invoker@aletheia-codex-prod.iam.gserviceaccount.com"
    }
  }
]
```

✅ **Configuration is correct - no changes needed**

---

### Step 3: Build React Application
```bash
cd web
npm install
npm run build
cd ..
```

**Expected Output**: "Compiled successfully"

---

### Step 4: Deploy to Firebase Hosting
```bash
firebase deploy --only hosting --project aletheia-codex-prod
```

**Expected Output**: "Deploy complete!"

---

### Step 5: Test API Endpoint
```bash
curl -X GET "https://aletheiacodex.app/api/review/pending" \
  -H "Content-Type: application/json" \
  -w "\n\nHTTP Status: %{http_code}\n"
```

**Expected Output**:
```json
{"error":"Missing Authorization header"}

HTTP Status: 401
```

✅ **This is correct - API requires Firebase authentication**

---

## Success Criteria

- [ ] Build completed without errors
- [ ] Firebase Hosting deployed successfully
- [ ] `https://aletheiacodex.app` loads (HTTP 200)
- [ ] API returns 401 (not 403 or 500)
- [ ] No CORS errors in browser

---

## Next Steps

After completing Phase 1.3.5:
- **Proceed to Phase 1.3.6**: Frontend Testing with Authentication

---

**Created By**: Architect (SuperNinja AI Agent)  
**Date**: 2024-01-13  
**Status**: Configuration Already Complete - Deploy Only