# Deploy Review API Path Fix

## Issue
The review-api is receiving requests with path `api/review/pending` but was only matching `review/pending` or `pending`, causing 404 errors.

## Fix Applied
Updated route matching in `main.py` to handle all three path formats:
- `api/review/pending` (from Firebase Hosting rewrite)
- `review/pending` (direct call with prefix)
- `pending` (direct call without prefix)

## Deployment Commands

Run these commands in Cloud Shell:

```bash
cd ~/aletheia-codex
git checkout sprint-1
git pull origin sprint-1

cd functions
gcloud run deploy review-api \
  --source=review_api \
  --region=us-central1 \
  --platform=managed \
  --allow-unauthenticated \
  --set-env-vars="GCP_PROJECT=aletheia-codex-prod" \
  --memory=512Mi \
  --cpu=1 \
  --project=aletheia-codex-prod
```

## Verification

After deployment, test the endpoint:

```bash
# Should return JSON with authentication error (expected)
curl https://aletheiacodex.app/api/review/pending
```

Expected response:
```json
{"error":"Missing Authorization header"}
```

## Testing in Browser

1. Open https://aletheiacodex.app
2. Log in with Firebase Auth
3. Navigate to Review page
4. Should now see data instead of "Endpoint not found" error

## Changes Made

**File**: `functions/review_api/main.py`

**Before**:
```python
if (path == 'review/pending' or path == 'pending') and request.method == 'GET':
```

**After**:
```python
if (path == 'api/review/pending' or path == 'review/pending' or path == 'pending') and request.method == 'GET':
```

Applied to all 6 endpoints:
- `/pending` (GET)
- `/approve` (POST)
- `/reject` (POST)
- `/batch-approve` (POST)
- `/batch-reject` (POST)
- `/stats` (GET)

## Git Commit
- Commit: `b2a8af9` - "fix(review-api): add api/review/* path matching for Firebase Hosting rewrites"
- Branch: `sprint-1`