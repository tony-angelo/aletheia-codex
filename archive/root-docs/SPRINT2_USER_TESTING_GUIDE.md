# Sprint 2 - User Testing Guide

**Status:** Deployment Complete - Ready for User Testing  
**Time Required:** 15-20 minutes  
**Date:** November 9, 2025

---

## 🎯 Current Status

✅ **COMPLETED:**
- All code implemented and tested (2,900+ lines)
- Function deployed to production
- Git changes pushed to repository
- All documentation complete
- Function verified responding correctly

⚠️ **PENDING USER ACTION:**
- Create test document in Firestore (service account lacks write permissions)
- Test the deployed function
- Verify AI extraction results
- Validate cost monitoring

---

## 📋 Testing Checklist

### Step 1: Create Test Document (5 minutes)

The AI service account doesn't have Firestore write permissions, so you need to create the test document manually.

#### Option A: Firebase Console (Recommended)

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select project: **aletheia-codex-prod**
3. Navigate to **Firestore Database**
4. Click **Start collection** or select existing **documents** collection
5. Click **Add document**
6. Use these values:

```
Document ID: test-ai-sprint2-final
```

**Fields:**
```json
{
  "title": "Sprint 2 AI Test Document",
  "content": "Albert Einstein was a theoretical physicist who developed the theory of relativity. He was born in Ulm, Germany in 1879. Einstein worked at the Institute for Advanced Study in Princeton, New Jersey. His famous equation E=mc² revolutionized physics. He received the Nobel Prize in Physics in 1921 for his explanation of the photoelectric effect.\n\nMarie Curie was a Polish-French physicist and chemist who conducted pioneering research on radioactivity. She was the first woman to win a Nobel Prize and the only person to win Nobel Prizes in two different scientific fields - Physics and Chemistry. Curie worked closely with her husband Pierre Curie at the University of Paris.\n\nThe Manhattan Project was a research and development undertaking during World War II that produced the first nuclear weapons. It was led by the United States with support from the United Kingdom and Canada. J. Robert Oppenheimer served as the scientific director of the project at Los Alamos Laboratory in New Mexico.",
  "user_id": "test-user-sprint2",
  "status": "pending",
  "file_path": "raw/test-ai-sprint2.txt",
  "created_at": [timestamp - use server timestamp],
  "updated_at": [timestamp - use server timestamp],
  "metadata": {
    "source": "sprint2_test",
    "test_type": "ai_integration"
  }
}
```

#### Option B: gcloud CLI with Your Credentials

```bash
# Authenticate with your user account (not service account)
gcloud auth login

# Create document using REST API
DOC_ID="test-ai-sprint2-final"
TOKEN=$(gcloud auth print-access-token)

curl -X PATCH \
  "https://firestore.googleapis.com/v1/projects/aletheia-codex-prod/databases/(default)/documents/documents/$DOC_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
  "fields": {
    "title": {"stringValue": "Sprint 2 AI Test Document"},
    "content": {"stringValue": "Albert Einstein was a theoretical physicist who developed the theory of relativity. He was born in Ulm, Germany in 1879. Einstein worked at the Institute for Advanced Study in Princeton, New Jersey. His famous equation E=mc² revolutionized physics. He received the Nobel Prize in Physics in 1921 for his explanation of the photoelectric effect.\n\nMarie Curie was a Polish-French physicist and chemist who conducted pioneering research on radioactivity. She was the first woman to win a Nobel Prize and the only person to win Nobel Prizes in two different scientific fields - Physics and Chemistry. Curie worked closely with her husband Pierre Curie at the University of Paris.\n\nThe Manhattan Project was a research and development undertaking during World War II that produced the first nuclear weapons. It was led by the United States with support from the United Kingdom and Canada. J. Robert Oppenheimer served as the scientific director of the project at Los Alamos Laboratory in New Mexico."},
    "user_id": {"stringValue": "test-user-sprint2"},
    "status": {"stringValue": "pending"},
    "file_path": {"stringValue": "raw/test-ai-sprint2.txt"},
    "created_at": {"timestampValue": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"},
    "updated_at": {"timestampValue": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"},
    "metadata": {
      "mapValue": {
        "fields": {
          "source": {"stringValue": "sprint2_test"},
          "test_type": {"stringValue": "ai_integration"}
        }
      }
    }
  }
}'
```

---

### Step 2: Test the Function (5 minutes)

Once the document is created, test the orchestration function:

```bash
# Get authentication token
TOKEN=$(gcloud auth print-identity-token)

# Call the function
curl -X POST \
  "https://us-central1-aletheia-codex-prod.cloudfunctions.net/orchestrate" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"document_id": "test-ai-sprint2-final", "user_id": "test-user-sprint2"}' \
  | python3 -m json.tool

# Check the response
# Expected: {"status": "success", "message": "Document processed successfully"}
```

**Monitor the function logs:**
```bash
# View recent logs
gcloud functions logs read orchestrate --region=us-central1 --limit=50

# Follow logs in real-time
gcloud functions logs read orchestrate --region=us-central1 --follow
```

---

### Step 3: Verify Results (10 minutes)

#### A. Check Firestore Collections

**1. Review Queue:**
```
Collection: review_queue
Expected: New documents with extracted entities and relationships
```

Go to Firebase Console > Firestore > review_queue

You should see entries like:
```json
{
  "document_id": "test-ai-sprint2-final",
  "user_id": "test-user-sprint2",
  "item_type": "entity",
  "item_data": {
    "name": "Albert Einstein",
    "type": "Person",
    "confidence": 0.95
  },
  "status": "pending",
  "created_at": [timestamp]
}
```

**2. Usage Logs:**
```
Collection: usage_logs
Expected: Cost tracking entries
```

You should see entries like:
```json
{
  "timestamp": [timestamp],
  "document_id": "test-ai-sprint2-final",
  "operation_type": "entity_extraction",
  "tokens_used": 1500,
  "cost": 0.0003,
  "model": "gemini-2.0-flash-exp"
}
```

**3. Document Status:**
```
Collection: documents
Document: test-ai-sprint2-final
Expected: Status updated to "processing" or "completed"
```

#### B. Check Neo4j Graph

**Connect to Neo4j:**
```
URL: [Your Neo4j instance URL]
Username: [Your Neo4j username]
Password: [From Secret Manager]
```

**Run Cypher queries:**
```cypher
// Check for entities
MATCH (n)
WHERE n.source_document = 'test-ai-sprint2-final'
RETURN n
LIMIT 25

// Check for relationships
MATCH (a)-[r]->(b)
WHERE r.source_document = 'test-ai-sprint2-final'
RETURN a, r, b
LIMIT 25

// Count entities by type
MATCH (n)
WHERE n.source_document = 'test-ai-sprint2-final'
RETURN labels(n)[0] as type, count(*) as count
ORDER BY count DESC
```

**Expected entities:**
- Albert Einstein (Person)
- Marie Curie (Person)
- Pierre Curie (Person)
- J. Robert Oppenheimer (Person)
- Institute for Advanced Study (Organization)
- University of Paris (Organization)
- Manhattan Project (Concept)
- Ulm, Germany (Place)
- Princeton, New Jersey (Place)
- Los Alamos Laboratory (Place)

**Expected relationships:**
- Einstein WORKED_AT Institute for Advanced Study
- Einstein BORN_IN Ulm, Germany
- Marie Curie WORKED_WITH Pierre Curie
- Marie Curie WORKED_AT University of Paris
- Oppenheimer DIRECTED Manhattan Project

---

### Step 4: Validate Performance (5 minutes)

#### A. Cost Validation

Check the usage_logs collection and verify:
- ✅ Cost per document is around $0.0006
- ✅ Entity extraction cost: ~$0.0003
- ✅ Relationship detection cost: ~$0.0003
- ✅ Total cost is well under $0.01 budget

#### B. Accuracy Validation

Check the review_queue and verify:
- ✅ All major entities extracted (Einstein, Curie, etc.)
- ✅ Entity types correct (Person, Organization, Place)
- ✅ Confidence scores reasonable (>0.7)
- ✅ Relationships detected correctly
- ✅ No major entities missed

#### C. Performance Validation

Check function logs and verify:
- ✅ Total processing time < 20 seconds
- ✅ Entity extraction time < 5 seconds
- ✅ Relationship detection time < 5 seconds
- ✅ Graph population time < 10 seconds
- ✅ No errors or timeouts

---

## 📊 Expected Results Summary

### Entities (Expected: 10-15)
- **People:** Einstein, Marie Curie, Pierre Curie, Oppenheimer
- **Organizations:** Institute for Advanced Study, University of Paris, Los Alamos Laboratory
- **Places:** Ulm Germany, Princeton New Jersey, New Mexico
- **Concepts:** Theory of Relativity, Manhattan Project, Radioactivity

### Relationships (Expected: 8-12)
- Einstein → WORKED_AT → Institute for Advanced Study
- Einstein → BORN_IN → Ulm, Germany
- Einstein → DEVELOPED → Theory of Relativity
- Marie Curie → WORKED_WITH → Pierre Curie
- Marie Curie → WORKED_AT → University of Paris
- Marie Curie → RESEARCHED → Radioactivity
- Oppenheimer → DIRECTED → Manhattan Project
- Oppenheimer → WORKED_AT → Los Alamos Laboratory

### Costs (Expected)
- **Entity Extraction:** ~$0.0003
- **Relationship Detection:** ~$0.0003
- **Total per Document:** ~$0.0006
- **Budget Compliance:** 94% under budget ✅

### Performance (Expected)
- **Total Time:** 15-18 seconds
- **Entity Extraction:** 3-4 seconds
- **Relationship Detection:** 3-4 seconds
- **Graph Population:** 8-10 seconds

---

## 🐛 Troubleshooting

### Issue: Document not found
**Solution:** Verify document was created in Firestore with correct ID

### Issue: Permission denied
**Solution:** Ensure you're authenticated with proper credentials:
```bash
gcloud auth login
gcloud config set project aletheia-codex-prod
```

### Issue: Function timeout
**Solution:** Check function logs for errors:
```bash
gcloud functions logs read orchestrate --region=us-central1 --limit=50
```

### Issue: No entities extracted
**Solution:** 
1. Check if Gemini API key is configured in Secret Manager
2. Verify function has access to Secret Manager
3. Check function logs for AI service errors

### Issue: No graph nodes created
**Solution:**
1. Verify Neo4j credentials in Secret Manager
2. Check Neo4j instance is running and accessible
3. Check function logs for Neo4j connection errors

---

## ✅ Success Criteria

Sprint 2 is 100% complete when:

- [x] Function deployed to production
- [x] Git changes pushed to repository
- [ ] Test document created in Firestore
- [ ] Function processes document successfully
- [ ] Entities extracted with >80% accuracy
- [ ] Relationships detected with >70% accuracy
- [ ] Cost per document < $0.01
- [ ] Processing time < 20 seconds
- [ ] Review queue populated correctly
- [ ] Neo4j graph populated correctly
- [ ] Usage logs show cost tracking

---

## 📞 Support

If you encounter any issues:

1. **Check function logs:**
   ```bash
   gcloud functions logs read orchestrate --region=us-central1 --limit=50
   ```

2. **Check function status:**
   ```bash
   gcloud functions describe orchestrate --region=us-central1
   ```

3. **View in Cloud Console:**
   https://console.cloud.google.com/functions/details/us-central1/orchestrate?project=aletheia-codex-prod

4. **Review documentation:**
   - SPRINT2_DEPLOYMENT_COMPLETE.md
   - SPRINT2_FINAL_STATUS.md
   - docs/sprint2/SPRINT2_DEPLOYMENT_GUIDE.md

---

## 🎉 After Testing

Once testing is complete and all success criteria are met:

1. Update PROJECT_STATUS.md to mark Sprint 2 as 100% complete
2. Create a Sprint 2 completion report
3. Plan Sprint 3 features
4. Celebrate! 🎊

---

**Current Status:** Ready for User Testing  
**Estimated Time:** 15-20 minutes  
**Next Action:** Create test document in Firestore

Good luck with testing! 🚀