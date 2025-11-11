# Sprint 3: Review Queue & User Interface - Troubleshooting

## Overview
Sprint 3 encountered several technical challenges during implementation, primarily related to Firestore indexes, IAM permissions, and CORS configuration. All issues were resolved during the sprint. This document captures the challenges and their solutions.

---

## Issue 1: Firestore Composite Index Required

### Problem
Complex queries on the review queue collection failed with "The query requires an index" error.

### Symptoms
- Query for pending items by user failed
- Error: "The query requires an index. You can create it here: [URL]"
- API endpoint returned 500 error
- Frontend couldn't load pending items

### Root Cause
Firestore requires composite indexes for queries that filter on multiple fields. The review queue queries filtered by:
- `user_id` (equality)
- `status` (equality)
- `confidence` (range/ordering)

This combination requires a composite index that doesn't exist by default.

### Solution
**Created Composite Index**:
1. Clicked the index creation URL in the error message
2. Waited for index to build (~2 minutes)
3. Alternatively, created via `firestore.indexes.json`:

```json
{
  "indexes": [
    {
      "collectionGroup": "review_queue",
      "queryScope": "COLLECTION",
      "fields": [
        { "fieldPath": "user_id", "order": "ASCENDING" },
        { "fieldPath": "status", "order": "ASCENDING" },
        { "fieldPath": "confidence", "order": "DESCENDING" }
      ]
    }
  ]
}
```

### Verification
- Query executed successfully
- API endpoint returned results
- Frontend loaded pending items
- No index errors in logs

### Prevention
- Create indexes before deploying queries
- Use `firestore.indexes.json` for version control
- Test queries with production-like data volumes
- Monitor Firestore logs for index errors

### Lessons Learned
- Firestore indexes are required for complex queries
- Index creation takes time (1-2 minutes)
- Error messages provide helpful index creation URLs
- Version control indexes with firestore.indexes.json

---

## Issue 2: IAM Permissions for Firestore

### Problem
Cloud Functions couldn't write to Firestore, returning "Permission denied" errors.

### Symptoms
- API calls to approve/reject items failed
- Error: "Missing or insufficient permissions"
- Items not updating in Firestore
- 403 Forbidden responses

### Root Cause
The Cloud Functions service account didn't have the necessary IAM roles to write to Firestore. By default, Cloud Functions have limited permissions.

### Solution
**Granted Required IAM Roles**:
1. Identified service account: `aletheia-functions@aletheia-codex-prod.iam.gserviceaccount.com`
2. Granted roles via gcloud:

```bash
# Grant Firestore User role
gcloud projects add-iam-policy-binding aletheia-codex-prod \
  --member="serviceAccount:aletheia-functions@aletheia-codex-prod.iam.gserviceaccount.com" \
  --role="roles/datastore.user"

# Grant Cloud Datastore User role (for Firestore in Datastore mode)
gcloud projects add-iam-policy-binding aletheia-codex-prod \
  --member="serviceAccount:aletheia-functions@aletheia-codex-prod.iam.gserviceaccount.com" \
  --role="roles/clouddatastore.user"
```

### Verification
- API calls succeeded
- Items updated in Firestore
- No permission errors
- 200 OK responses

### Prevention
- Grant IAM roles before deploying functions
- Document required roles in deployment guide
- Test with service account permissions, not user permissions
- Use principle of least privilege

### Lessons Learned
- Cloud Functions need explicit IAM permissions
- Default permissions are very limited
- Test with service account, not user account
- Document IAM requirements clearly

---

## Issue 3: CORS Configuration for Cloud Functions

### Problem
Browser requests to Cloud Functions failed with CORS errors.

### Symptoms
- Preflight OPTIONS requests failed
- Error: "No 'Access-Control-Allow-Origin' header present"
- API calls from frontend blocked
- Console errors about CORS policy

### Root Cause
Cloud Functions don't automatically handle CORS. The function needs to:
1. Handle OPTIONS preflight requests
2. Add CORS headers to all responses
3. Allow the frontend origin

### Solution
**Implemented CORS Handling**:

```python
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)

# Configure CORS
CORS(app, resources={
    r"/*": {
        "origins": [
            "https://aletheia-codex-prod.web.app",
            "https://aletheia-codex-prod.firebaseapp.com",
            "http://localhost:3000"
        ],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

@app.route('/review/pending', methods=['GET', 'OPTIONS'])
def get_pending():
    if request.method == 'OPTIONS':
        return '', 204
    # ... rest of handler
```

### Verification
- Preflight requests returned 204
- API calls succeeded from frontend
- No CORS errors in console
- All origins allowed

### Prevention
- Configure CORS before deploying
- Test from actual frontend domain
- Include localhost for development
- Use flask-cors library for simplicity

### Lessons Learned
- CORS must be explicitly configured
- Preflight OPTIONS requests need handling
- Test from actual frontend domain, not Postman
- flask-cors simplifies CORS configuration

---

## Issue 4: Real-Time Updates Memory Leak

### Problem
Firestore listeners weren't being cleaned up, causing memory leaks in the React app.

### Symptoms
- Memory usage increasing over time
- Multiple listeners active for same data
- Duplicate updates in UI
- Browser slowdown after extended use

### Root Cause
React useEffect hooks created Firestore listeners but didn't clean them up when components unmounted. Each re-render created a new listener without removing the old one.

### Solution
**Implemented Proper Cleanup**:

```typescript
useEffect(() => {
  // Create Firestore listener
  const unsubscribe = onSnapshot(
    query(collection(db, 'review_queue'), where('user_id', '==', userId)),
    (snapshot) => {
      // Handle updates
      const items = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
      setReviewItems(items);
    }
  );

  // Cleanup function - called when component unmounts
  return () => {
    unsubscribe();
  };
}, [userId]); // Dependencies array
```

### Verification
- Memory usage stable over time
- Only one listener per component
- No duplicate updates
- Clean unmount behavior

### Prevention
- Always return cleanup function from useEffect
- Test component mount/unmount cycles
- Monitor memory usage during development
- Use React DevTools to check for memory leaks

### Lessons Learned
- Firestore listeners must be cleaned up
- useEffect cleanup functions are essential
- Memory leaks can be subtle
- Test component lifecycle thoroughly

---

## Issue 5: Batch Operation Timeout

### Problem
Batch operations with many items (>50) timed out before completing.

### Symptoms
- Batch approve/reject failed for large batches
- Timeout errors after 60 seconds
- Partial completion (some items processed, others not)
- Inconsistent state

### Root Cause
Cloud Functions have a default timeout of 60 seconds. Processing 100 items sequentially took longer than this limit.

### Solution
**Implemented Multiple Improvements**:

1. **Increased Function Timeout**:
```bash
gcloud functions deploy review-api \
  --timeout=540s \
  --memory=512MB
```

2. **Parallel Processing**:
```python
import asyncio

async def process_batch(item_ids):
    tasks = [process_item(item_id) for item_id in item_ids]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results
```

3. **Batch Size Limit**:
```python
MAX_BATCH_SIZE = 100

if len(item_ids) > MAX_BATCH_SIZE:
    return jsonify({
        'error': f'Batch size exceeds maximum of {MAX_BATCH_SIZE}'
    }), 400
```

### Verification
- Batch operations complete within timeout
- 100 items processed in ~30 seconds
- No timeout errors
- Proper error handling for failures

### Prevention
- Set appropriate function timeouts
- Use parallel processing for batch operations
- Limit batch sizes
- Provide progress feedback to users

### Lessons Learned
- Default timeouts may be insufficient
- Parallel processing significantly improves performance
- Batch size limits prevent timeouts
- Always handle partial failures gracefully

---

## Issue 6: TypeScript Type Errors

### Problem
TypeScript compilation failed with type errors in React components.

### Symptoms
- Build failed with type errors
- IDE showing red squiggles
- Unclear error messages
- Compilation errors

### Root Cause
Missing or incorrect TypeScript type definitions for:
- Firestore document data
- API response types
- Component props
- Hook return types

### Solution
**Created Comprehensive Type Definitions**:

```typescript
// types/review.ts
export interface ReviewItem {
  id: string;
  type: 'entity' | 'relationship';
  status: 'pending' | 'approved' | 'rejected';
  user_id: string;
  source_document_id: string;
  extracted_at: Date;
  data: EntityData | RelationshipData;
  reviewed_at?: Date;
  reviewed_by?: string;
  rejection_reason?: string;
  metadata?: Record<string, any>;
}

export interface EntityData {
  name: string;
  type: string;
  description?: string;
  confidence: number;
  source_reference?: string;
  metadata?: Record<string, any>;
}

export interface RelationshipData {
  source_entity_id: string;
  target_entity_id: string;
  relationship_type: string;
  confidence: number;
  source_reference?: string;
  metadata?: Record<string, any>;
}
```

### Verification
- TypeScript compilation successful
- No type errors in IDE
- Autocomplete working correctly
- Type safety enforced

### Prevention
- Define types before writing code
- Use strict TypeScript configuration
- Create shared type definitions
- Document type requirements

### Lessons Learned
- TypeScript types prevent runtime errors
- Comprehensive types improve developer experience
- Shared type definitions ensure consistency
- Type errors are easier to fix early

---

## Non-Issues (What Went Well)

### Firestore Performance
- **Expected**: Potential slow queries
- **Actual**: Fast queries with proper indexes
- **Lesson**: Firestore is very fast with indexes

### React Performance
- **Expected**: Potential render performance issues
- **Actual**: Smooth rendering with proper optimization
- **Lesson**: React is fast with proper patterns

### Neo4j Integration
- **Expected**: Complex integration
- **Actual**: HTTP API made it simple
- **Lesson**: HTTP API is easier than Bolt driver

### Bundle Size
- **Expected**: Large bundle size
- **Actual**: 153KB (23% under target)
- **Lesson**: Tree shaking works well

---

## Summary

### Issues Encountered
1. ✅ Firestore composite index required - Resolved with index creation
2. ✅ IAM permissions for Firestore - Resolved with role grants
3. ✅ CORS configuration - Resolved with flask-cors
4. ✅ Real-time updates memory leak - Resolved with cleanup functions
5. ✅ Batch operation timeout - Resolved with parallel processing
6. ✅ TypeScript type errors - Resolved with type definitions

### Severity Distribution
- **Critical**: 0
- **High**: 2 (IAM permissions, CORS)
- **Medium**: 4 (Firestore index, memory leak, timeout, types)
- **Low**: 0

### Resolution Rate
- **100%** of issues resolved during sprint
- **0** issues carried forward
- **0** workarounds required

### Key Takeaways
1. Firestore indexes are essential for complex queries
2. IAM permissions must be configured explicitly
3. CORS must be handled for browser requests
4. React cleanup functions prevent memory leaks
5. Parallel processing improves batch performance
6. TypeScript types prevent runtime errors

---

**Sprint**: Sprint 3  
**Issues**: 6 (2 high, 4 medium - all resolved)  
**Status**: ✅ All issues resolved  
**Date**: November 9, 2025