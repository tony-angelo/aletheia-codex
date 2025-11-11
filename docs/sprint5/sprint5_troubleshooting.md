# Sprint 5: Note Processing Workflow Fix - Troubleshooting

## Overview
Sprint 5 focused on debugging a critical issue where notes weren't being processed by AI. The root cause was identified as an incorrect trigger configuration, and several related issues were resolved during the fix.

---

## Issue 1: Orchestration Function Not Triggering

### Problem
Notes created in Firestore weren't triggering the orchestration function, causing complete workflow failure.

### Symptoms
- Notes created successfully in Firestore
- Orchestration function never called
- No function logs
- Review queue empty
- Silent failure with no errors

### Root Cause
Orchestration function was deployed with **HTTP trigger** instead of **Firestore trigger**. HTTP triggers require manual API calls, while Firestore triggers respond to document events automatically.

### Solution
**Redeployed with Firestore Trigger**:

1. Created new entry point:
```python
@functions_framework.cloud_event
def orchestration_function(cloud_event: CloudEvent) -> None:
    """
    Firestore trigger for note processing orchestration.
    Triggered on: google.cloud.firestore.document.v1.created
    Document path: notes/{noteId}
    """
```

2. Deployed with correct trigger:
```bash
gcloud functions deploy orchestration-function \
  --gen2 \
  --runtime=python311 \
  --region=us-central1 \
  --source=. \
  --entry-point=orchestration_function \
  --trigger-event-filters="type=google.cloud.firestore.document.v1.created" \
  --trigger-event-filters="database=(default)" \
  --trigger-event-filters-path-pattern="document=notes/{noteId}" \
  --trigger-location=nam5
```

### Verification
- Created test note
- Function triggered within 1 second
- Function logs showed processing
- Review queue populated

### Prevention
- Always specify trigger type explicitly
- Test automatic triggering
- Verify trigger configuration
- Monitor function invocations

### Lessons Learned
- Trigger type is critical for Cloud Functions
- HTTP and Firestore triggers serve different purposes
- Always test automatic triggering
- Silent failures are hard to debug

---

## Issue 2: Wrong Trigger Region

### Problem
Initial Firestore trigger deployment failed with region mismatch error.

### Symptoms
- Deployment error: "Trigger region must match Firestore region"
- Function deployed but never triggered
- Eventarc configuration failed

### Root Cause
Firestore database in `nam5` region, but trigger configured for `us-central1`.

### Solution
**Matched Trigger Region to Firestore**:
```bash
--trigger-location=nam5  # Match Firestore region
```

### Verification
- Deployment successful
- Eventarc trigger created
- Function triggered correctly

### Prevention
- Always check Firestore region
- Match trigger region to database region
- Verify Eventarc configuration

### Lessons Learned
- Trigger region must match Firestore region
- Regional configuration is critical
- Deployment errors provide helpful hints

---

## Issue 3: CloudEvents Library Missing

### Problem
Function failed with import error for CloudEvents.

### Symptoms
- Deployment successful
- Function failed on invocation
- Error: "No module named 'cloudevents'"

### Root Cause
CloudEvents library not in requirements.txt.

### Solution
**Added CloudEvents Dependency**:
```
cloudevents>=1.9.0
```

### Verification
- Redeployed function
- Function invoked successfully
- No import errors

### Prevention
- Always update requirements.txt
- Test imports before deployment
- Verify dependencies

### Lessons Learned
- Cloud Functions Gen 2 use CloudEvents
- Always include all dependencies
- Test after adding dependencies

---

## Issue 4: Event Data Parsing

### Problem
Function couldn't parse Firestore event data correctly.

### Symptoms
- Function triggered
- Error accessing note data
- KeyError exceptions

### Root Cause
CloudEvent data structure different from expected format.

### Solution
**Proper Event Parsing**:
```python
def orchestration_function(cloud_event: CloudEvent) -> None:
    # Parse event data
    event_data = cloud_event.data
    
    # Extract note ID from resource path
    resource_path = event_data.get('value', {}).get('name', '')
    note_id = resource_path.split('/')[-1]
    
    # Get note data
    note_data = event_data.get('value', {}).get('fields', {})
```

### Verification
- Event data parsed correctly
- Note ID extracted
- Note content accessible

### Prevention
- Study CloudEvent structure
- Add error handling
- Log event data for debugging

### Lessons Learned
- CloudEvent structure is nested
- Need to parse carefully
- Logging helps debugging

---

## Summary

### Issues Encountered
1. ✅ Wrong trigger type (HTTP vs Firestore) - Resolved
2. ✅ Wrong trigger region - Resolved
3. ✅ Missing CloudEvents library - Resolved
4. ✅ Event data parsing - Resolved

### Severity Distribution
- **Critical**: 1 (wrong trigger type)
- **High**: 1 (wrong region)
- **Medium**: 2 (missing library, parsing)
- **Low**: 0

### Resolution Rate
- **100%** of issues resolved during sprint
- **0** issues carried forward

### Key Takeaways
1. Trigger type is critical for Cloud Functions
2. Region matching is essential
3. CloudEvents library required for Gen 2
4. Event data structure needs careful parsing

---

**Sprint**: Sprint 5  
**Issues**: 4 (1 critical, 1 high, 2 medium - all resolved)  
**Status**: ✅ All issues resolved  
**Date**: November 9, 2025