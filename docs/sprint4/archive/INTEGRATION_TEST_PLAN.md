# Sprint 4 Integration Test Plan

## Overview
This document outlines the integration testing strategy for Sprint 4: Note Input & AI Processing.

## Test Environments
- **Local Development**: http://localhost:3000
- **Production**: https://aletheia-codex.web.app

## Test Scenarios

### 1. End-to-End Note Processing Flow
**Objective**: Verify complete note processing from input to review queue

**Steps**:
1. Navigate to Notes page
2. Enter note content: "Met John Smith at the conference. He works at Google on AI projects."
3. Click Submit
4. Verify processing status appears
5. Wait for processing to complete
6. Verify extraction results are displayed
7. Navigate to Review Queue
8. Verify extracted entities appear in review queue

**Expected Results**:
- Note is created in Firestore
- Processing status updates in real-time
- Entities extracted: John Smith (Person), Google (Organization)
- Relationship detected: John Smith WORKS_AT Google
- Items appear in review queue with correct confidence scores

### 2. Navigation Flow
**Objective**: Verify navigation between pages

**Steps**:
1. Start on Notes page
2. Click "Review Queue" in navigation
3. Verify Review Queue page loads
4. Click "Knowledge Graph" in navigation
5. Verify Graph page loads
6. Click "Notes" in navigation
7. Verify Notes page loads

**Expected Results**:
- All pages load without errors
- Navigation highlights current page
- Page content displays correctly

### 3. Note History
**Objective**: Verify note history displays and updates

**Steps**:
1. Create 3 notes with different content
2. Verify all notes appear in history sidebar
3. Verify notes are sorted by creation date (newest first)
4. Verify note status indicators are correct
5. Delete one note
6. Verify note is removed from history

**Expected Results**:
- All notes display in history
- Correct sorting order
- Status badges show correct colors
- Real-time updates when notes change

### 4. Processing Status Updates
**Objective**: Verify real-time processing status updates

**Steps**:
1. Submit a note
2. Observe processing status component
3. Verify progress bar updates
4. Verify step indicators update (extraction → review → graph)
5. Verify elapsed time updates
6. Wait for completion
7. Verify completion message appears

**Expected Results**:
- Progress bar animates from 0% to 100%
- Step indicators change from pending → processing → completed
- Elapsed time increments
- Completion message displays with summary

### 5. Error Handling
**Objective**: Verify error scenarios are handled gracefully

**Steps**:
1. Submit empty note
2. Verify validation error
3. Submit note with 10,001 characters
4. Verify length validation error
5. Disconnect network
6. Submit note
7. Verify network error message

**Expected Results**:
- Validation errors display clearly
- Error messages are user-friendly
- UI remains functional after errors
- Errors are logged appropriately

### 6. Concurrent Processing
**Objective**: Verify multiple notes can be processed

**Steps**:
1. Submit first note
2. Wait for processing to start
3. Verify cannot submit second note while first is processing
4. Wait for first note to complete
5. Submit second note
6. Verify second note processes successfully

**Expected Results**:
- Only one note processes at a time
- Submit button disabled during processing
- Queue system works correctly

### 7. Real-time Updates
**Objective**: Verify Firestore real-time updates work

**Steps**:
1. Open app in two browser tabs
2. Submit note in tab 1
3. Verify note appears in tab 2 history
4. Wait for processing to complete in tab 1
5. Verify status updates in tab 2
6. Delete note in tab 2
7. Verify note disappears in tab 1

**Expected Results**:
- Changes sync across tabs in real-time
- No page refresh required
- All state updates correctly

### 8. Performance Testing
**Objective**: Verify acceptable performance

**Steps**:
1. Submit note with 5,000 characters
2. Measure processing time
3. Submit note with 100 characters
4. Measure processing time
5. Load page with 50 notes in history
6. Measure page load time

**Expected Results**:
- Processing time < 30 seconds for any note
- Page load time < 3 seconds
- UI remains responsive during processing
- No memory leaks

## Backend Integration Tests

### 1. Orchestration Function
**Test**: POST to orchestration endpoint with noteId and content

```bash
curl -X POST https://us-central1-aletheia-codex.cloudfunctions.net/orchestration \
  -H "Content-Type: application/json" \
  -d '{
    "noteId": "test-note-123",
    "content": "Test note content",
    "userId": "test-user-456"
  }'
```

**Expected**: 200 response with extraction summary

### 2. Notes API
**Test**: GET user notes

```bash
curl -X GET https://us-central1-aletheia-codex.cloudfunctions.net/notes_api/notes \
  -H "Authorization: Bearer test-user-456"
```

**Expected**: 200 response with notes array

### 3. Firestore Rules
**Test**: Attempt to access another user's note

**Expected**: Permission denied error

### 4. Firestore Indexes
**Test**: Query notes with filters

**Expected**: Query completes without index warning

## Acceptance Criteria Verification

### Code & Testing
- [ ] Navigation system works across all pages
- [ ] Note input accepts and validates content
- [ ] Note history displays and updates in real-time
- [ ] Processing status shows accurate progress
- [ ] Unit tests pass (npm test)
- [ ] Integration tests pass (manual verification)

### Deployment
- [ ] Orchestration function deployed with noteId support
- [ ] Notes API function deployed and accessible
- [ ] Frontend deployed to Firebase Hosting
- [ ] Firestore rules deployed
- [ ] Firestore indexes created
- [ ] Environment variables configured

### Production Validation
- [ ] Can submit notes via UI
- [ ] Notes are processed by AI
- [ ] Extracted items appear in review queue
- [ ] Can navigate between all pages
- [ ] Real-time updates work
- [ ] No critical errors in logs

## Test Data

### Sample Notes
1. "Met Sarah Johnson at the tech conference. She's the CTO of DataCorp."
2. "Reading 'Clean Code' by Robert Martin. Great insights on software design."
3. "Project deadline is March 15, 2024. Need to coordinate with the development team."
4. "Attended workshop on machine learning. Learned about neural networks and transformers."
5. "Call with client tomorrow at 2 PM. Discuss Q1 roadmap and budget."

## Bug Tracking
Document any issues found during testing:

| ID | Severity | Description | Status |
|----|----------|-------------|--------|
|    |          |             |        |

## Sign-off
- [ ] All test scenarios passed
- [ ] All acceptance criteria met
- [ ] No critical bugs remaining
- [ ] Performance acceptable
- [ ] Ready for production