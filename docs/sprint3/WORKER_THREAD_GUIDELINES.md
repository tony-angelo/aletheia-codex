# Worker Thread Guidelines for AletheiaCodex Sprints

**MANDATORY READING**: All worker threads MUST follow these guidelines.

## Core Principle: Sprints Are Not Complete Until Fully Deployed and Tested

A sprint is ONLY complete when:
1. ✅ All code is written and tested locally
2. ✅ All code is deployed to production (Cloud Functions, Firebase Hosting, etc.)
3. ✅ All functionality is tested in production environment
4. ✅ All tests pass in production
5. ✅ End-to-end workflows verified in production
6. ✅ No critical errors in production logs
7. ✅ Performance targets met
8. ✅ Documentation updated
9. ✅ PR created with all changes
10. ✅ User has confirmed completion

**NEVER mark a sprint complete if there are tasks remaining for the user to do manually.**

---

## Handling Blockers: Request Permissions, Don't Ask User to Do Manual Work

### ✅ DO: Request IAM Roles/Permissions

When you need additional permissions:

```
I need the `roles/datastore.indexAdmin` role to create Firestore indexes programmatically.

Please run this command:
gcloud projects add-iam-policy-binding aletheia-codex \
  --member="serviceAccount:aletheia-codex@aletheia-codex.iam.gserviceaccount.com" \
  --role="roles/datastore.indexAdmin"

Once you've run this command, please confirm and I'll continue.
```

### ✅ DO: Request API Keys/Secrets

When you need API keys or secrets:

```
I need the Gemini API key to proceed with AI integration.

Please add it to Secret Manager:
gcloud secrets create gemini-api-key \
  --data-file=- \
  --replication-policy="automatic"

Then paste the API key when prompted.

Once you've added the secret, please confirm and I'll continue.
```

### ✅ DO: Request Permission to Create Resources

When you need to create infrastructure:

```
I need to create a Firestore composite index for the review queue.

May I proceed with creating this index programmatically using the Firestore Admin API?

If yes, I'll need the `roles/datastore.indexAdmin` role (see command above).
```

### ❌ DON'T: Ask User to Deploy Manually

**WRONG**:
```
The code is ready. Please deploy it to Cloud Functions using:
gcloud functions deploy orchestration-function ...
```

**RIGHT**:
```
Deploying to Cloud Functions...
[Execute deployment command]
Deployment successful. Testing in production...
```

### ❌ DON'T: Ask User to Create Indexes Manually

**WRONG**:
```
Please create this Firestore index manually in the console:
- Collection: review_queue
- Fields: userId ASC, status ASC, createdAt DESC
```

**RIGHT**:
```
I need the `roles/datastore.indexAdmin` role to create this index programmatically.
[Request permission, wait for user, then create index automatically]
```

### ❌ DON'T: Mark Sprint Complete with Remaining Tasks

**WRONG**:
```
Sprint 2 is complete! 

Remaining tasks for you:
- Deploy the function to production
- Create the Firestore index
- Test the API endpoints
```

**RIGHT**:
```
Deploying to production...
[Deploy everything]
Testing in production...
[Run all tests]
All tests passing. Sprint 2 is complete!
```

---

## Completion Criteria: 15 Explicit Checkboxes

Before marking a sprint complete, verify ALL of these:

### Code & Testing
- [ ] All code written and committed
- [ ] All unit tests passing locally
- [ ] All integration tests passing locally
- [ ] Code reviewed and refactored

### Deployment
- [ ] All functions deployed to Cloud Functions
- [ ] All static assets deployed to Firebase Hosting
- [ ] All secrets configured in Secret Manager
- [ ] All IAM permissions configured

### Production Validation
- [ ] All API endpoints tested in production
- [ ] All UI features tested in production
- [ ] End-to-end workflows verified in production
- [ ] No critical errors in production logs
- [ ] Performance targets met (response times, costs, etc.)

### Documentation & Handoff
- [ ] All documentation updated
- [ ] PR created with all changes
- [ ] User has confirmed completion

**If ANY checkbox is unchecked, the sprint is NOT complete.**

---

## Documentation: One Completion Report Only

### ✅ DO: Create ONE Comprehensive Completion Report

At the end of the sprint, create a single document:

```
docs/sprint(n)/COMPLETION_REPORT.md
```

This should include:
1. **Summary**: What was accomplished
2. **Deployment Details**: What was deployed and where
3. **Test Results**: All test results from production
4. **Performance Metrics**: Actual vs. target metrics
5. **Known Issues**: Any issues discovered (if any)
6. **Next Steps**: Recommendations for next sprint

### ❌ DON'T: Create Excessive Status Documents

**WRONG**: Creating 12+ documents like:
- STATUS_UPDATE_1.md
- STATUS_UPDATE_2.md
- DEPLOYMENT_STATUS.md
- TEST_RESULTS.md
- PERFORMANCE_REPORT.md
- etc.

**RIGHT**: ONE comprehensive completion report at the end.

---

## Pull Requests: Only When 100% Complete

### ✅ DO: Create PR After Full Deployment and Testing

```
1. Deploy everything to production
2. Test everything in production
3. Verify all tests pass
4. Verify no critical errors
5. Create PR with all changes
6. Mark sprint complete
```

### ❌ DON'T: Create PR Before Production Validation

**WRONG**:
```
1. Write code
2. Test locally
3. Create PR
4. Ask user to deploy and test
```

---

## Examples of Proper Blocker Handling

### Example 1: Missing IAM Role

**Situation**: Need to create Firestore index programmatically

**Proper Response**:
```
I need to create a Firestore composite index for the review queue. To do this programmatically, I need the `roles/datastore.indexAdmin` role.

Please run this command:
gcloud projects add-iam-policy-binding aletheia-codex \
  --member="serviceAccount:aletheia-codex@aletheia-codex.iam.gserviceaccount.com" \
  --role="roles/datastore.indexAdmin"

Once you've run this command, please confirm and I'll continue with the index creation.
```

**After User Confirms**:
```
Thank you! Creating Firestore index programmatically...
[Execute index creation]
Index created successfully. Continuing with deployment...
```

### Example 2: Missing API Key

**Situation**: Need Gemini API key for AI integration

**Proper Response**:
```
I need the Gemini API key to proceed with AI integration testing.

Please add it to Secret Manager:
echo "your-api-key-here" | gcloud secrets create gemini-api-key \
  --data-file=- \
  --replication-policy="automatic"

Once you've added the secret, please confirm and I'll continue.
```

**After User Confirms**:
```
Thank you! Testing AI integration with Gemini...
[Run tests]
All tests passing. Deploying to production...
```

### Example 3: Need Permission to Create Resource

**Situation**: Need to create Cloud Storage bucket

**Proper Response**:
```
I need to create a Cloud Storage bucket for storing processed documents.

Bucket details:
- Name: aletheia-codex-documents
- Location: us-central1
- Storage class: STANDARD

May I proceed with creating this bucket? I'll need the `roles/storage.admin` role:

gcloud projects add-iam-policy-binding aletheia-codex \
  --member="serviceAccount:aletheia-codex@aletheia-codex.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

Once you've granted the role, please confirm and I'll create the bucket.
```

---

## Sprint Workflow Summary

### Phase 1: Planning (5-10 minutes)
1. Read sprint brief and implementation guide
2. Review reference documentation
3. Create todo.md with all tasks
4. Confirm understanding with user

### Phase 2: Implementation (80-90% of time)
1. Write code incrementally
2. Test locally after each component
3. Request permissions when needed (WAIT for user)
4. Continue after user grants permissions
5. Commit changes regularly

### Phase 3: Deployment (5-10% of time)
1. Deploy all functions to Cloud Functions
2. Deploy all static assets to Firebase Hosting
3. Configure all secrets and permissions
4. Verify deployment successful

### Phase 4: Production Testing (5-10% of time)
1. Test all API endpoints in production
2. Test all UI features in production
3. Run end-to-end workflows
4. Check production logs for errors
5. Verify performance targets met

### Phase 5: Completion (5 minutes)
1. Create ONE completion report
2. Create PR with all changes
3. Mark sprint complete
4. Wait for user confirmation

---

## Key Takeaways

1. **Automation First**: Request permissions to automate, don't ask user to do manual work
2. **Deploy Everything**: Sprints aren't complete until deployed and tested in production
3. **One Report**: Create ONE comprehensive completion report, not 12+ status documents
4. **PR Last**: Create PR only after everything is deployed and tested
5. **Wait for User**: When you need permissions/keys, request them and WAIT for user confirmation
6. **15 Checkboxes**: Verify all 15 completion criteria before marking sprint complete

---

## Questions?

If you're unsure about anything:
1. ✅ DO: Ask the user for clarification
2. ✅ DO: Request permissions you need
3. ✅ DO: Wait for user confirmation before continuing
4. ❌ DON'T: Mark sprint complete with tasks remaining
5. ❌ DON'T: Ask user to deploy/test manually
6. ❌ DON'T: Create PR before production validation

**Remember**: The goal is to deliver a fully working, deployed, tested feature - not just code that "should work if the user deploys it."