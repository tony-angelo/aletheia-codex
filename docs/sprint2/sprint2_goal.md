# Sprint 2: AI Integration & Entity Extraction - Goal

## Sprint Objective
Build a complete AI integration layer that extracts entities and relationships from natural language documents, populates the Neo4j knowledge graph, and monitors costs - all while achieving high accuracy and staying within budget.

## Problem Statement

### Current State (Before Sprint 2)
- Neo4j connection established (Sprint 1)
- No AI integration
- No entity extraction capability
- No relationship detection
- No knowledge graph population
- No cost monitoring

### Desired State (After Sprint 2)
- AI service layer with provider abstraction
- Entity extraction with >85% accuracy
- Relationship detection with >75% accuracy
- Knowledge graph automatically populated
- Cost monitoring with alerts
- Complete end-to-end workflow tested

### Why This Matters
This is the **core value proposition** of Aletheia Codex. Without accurate AI extraction:
- The knowledge graph remains empty
- Users can't discover connections
- The application has no intelligence
- The entire concept fails

This sprint validates whether the fundamental idea is viable.

## Success Criteria

### 1. AI Service Abstraction Layer ✅
**Criteria**:
- Base provider interface defined
- Gemini provider implemented
- Service wrapper created
- Extensible for future providers

**Verification**:
- Can swap providers without changing calling code
- Gemini API calls working
- Error handling robust
- Cost estimation accurate

### 2. Entity Extraction Accuracy >85% ✅
**Criteria**:
- Extract Person, Place, Organization, Concept, Moment, Thing
- Confidence scoring implemented
- Property extraction working
- Validation logic in place

**Verification**:
- Test with diverse documents
- Measure accuracy against ground truth
- Confidence scores correlate with accuracy
- Properties extracted correctly

### 3. Relationship Detection Accuracy >75% ✅
**Criteria**:
- Detect relationships between entities
- Support 15+ relationship types
- Dynamic type creation
- Confidence scoring

**Verification**:
- Test with documents containing relationships
- Measure accuracy against ground truth
- Relationship types appropriate
- Confidence scores meaningful

### 4. Neo4j Graph Population ✅
**Criteria**:
- Entities created in graph
- Relationships linked correctly
- User isolation working
- Deduplication logic (basic)

**Verification**:
- Query graph to verify entities
- Check relationships are linked
- Verify user isolation
- Test deduplication

### 5. Cost Monitoring ✅
**Criteria**:
- Token counting accurate
- Cost calculation correct
- Alert system functional
- Cost per document < $0.01

**Verification**:
- Track costs during testing
- Verify calculations match API billing
- Test alert thresholds
- Measure cost per document

### 6. End-to-End Workflow ✅
**Criteria**:
- Complete pipeline working
- Document → Entities → Relationships → Graph
- Error handling robust
- Performance acceptable

**Verification**:
- Process test documents end-to-end
- Verify results in Neo4j
- Check error handling
- Measure processing time

## Scope

### In Scope
✅ **AI Service Layer**:
- Base provider interface
- Gemini 2.0 Flash implementation
- Prompt management
- JSON response parsing
- Error handling and retry logic

✅ **Entity Extraction**:
- 6 entity types (Person, Place, Organization, Concept, Moment, Thing)
- Property extraction
- Confidence scoring
- Validation and normalization

✅ **Relationship Detection**:
- 15+ relationship types
- Dynamic type creation
- Confidence scoring
- Bidirectional relationships

✅ **Graph Population**:
- Entity creation in Neo4j
- Relationship linking
- User isolation (OWNS relationships)
- Basic deduplication

✅ **Cost Monitoring**:
- Token counting
- Cost calculation
- Usage tracking
- Alert system

✅ **Testing**:
- Unit tests for components
- Integration tests for workflow
- Performance benchmarks
- Cost validation

### Out of Scope
❌ **Advanced Features**:
- Multi-language support
- Image/video processing
- Audio transcription
- Advanced deduplication algorithms

❌ **UI Components**:
- Review queue interface
- Entity browser
- Relationship visualizer
- Dashboard

❌ **Optimization**:
- Caching layer
- Batch processing
- Parallel processing
- Advanced prompt optimization

❌ **Additional Providers**:
- OpenAI integration
- Claude integration
- Local model support

## Prerequisites

### Required Before Starting
1. ✅ Sprint 1 complete (Neo4j connection working)
2. ✅ Google AI Studio API key obtained
3. ✅ API key stored in Secret Manager
4. ✅ Neo4j database accessible
5. ✅ Development environment set up

### Dependencies
- Python 3.11
- google-generativeai library
- Neo4j Python driver
- Firestore client library
- Cloud Functions Gen 2

## Timeline

### Estimated Duration
**1 day** (actual: 1 day)

### Phase Breakdown
1. **AI Service Layer** (3 hours)
   - Base provider interface
   - Gemini implementation
   - Prompt management
   - Testing

2. **Data Models** (1 hour)
   - Entity model
   - Relationship model
   - Validation logic

3. **Entity Extraction** (2 hours)
   - Extraction logic
   - Confidence scoring
   - Testing with documents

4. **Relationship Detection** (2 hours)
   - Detection logic
   - Type handling
   - Testing with documents

5. **Graph Population** (2 hours)
   - Neo4j integration
   - User isolation
   - Deduplication
   - Testing

6. **Cost Monitoring** (1 hour)
   - Token counting
   - Cost calculation
   - Alert system

7. **Integration & Testing** (1 hour)
   - End-to-end workflow
   - Performance testing
   - Cost validation

## Deliverables

### Code
1. ✅ `shared/ai/base_provider.py` - Abstract provider interface
2. ✅ `shared/ai/gemini_provider.py` - Gemini implementation
3. ✅ `shared/ai/ai_service.py` - Service wrapper
4. ✅ `shared/ai/prompts/entity_extraction.py` - Entity prompts
5. ✅ `shared/ai/prompts/relationship_detection.py` - Relationship prompts
6. ✅ `shared/models/entity.py` - Entity data model
7. ✅ `shared/models/relationship.py` - Relationship data model
8. ✅ `shared/graph/entity_extractor.py` - Extraction logic
9. ✅ `shared/graph/relationship_detector.py` - Detection logic
10. ✅ `shared/graph/graph_populator.py` - Graph population
11. ✅ `shared/monitoring/cost_tracker.py` - Cost monitoring

### Tests
1. ✅ Test scripts for each component
2. ✅ Integration test for end-to-end workflow
3. ✅ Performance benchmarks
4. ✅ Cost validation tests

### Documentation
1. ✅ Implementation guide
2. ✅ API documentation
3. ✅ Testing procedures
4. ✅ Completion report

## Known Challenges

### Challenge 1: AI Accuracy
**Issue**: AI models can produce inconsistent results
**Solution**: Use confidence scoring and validation
**Status**: ✅ Resolved with confidence thresholds

### Challenge 2: Cost Control
**Issue**: AI API calls can be expensive
**Solution**: Monitor costs in real-time, optimize prompts
**Status**: ✅ Resolved - 94% under budget

### Challenge 3: JSON Parsing
**Issue**: AI responses may not always be valid JSON
**Solution**: Robust parsing with error handling
**Status**: ✅ Resolved with retry logic

### Challenge 4: Entity Deduplication
**Issue**: Same entity may be extracted multiple times
**Solution**: Basic deduplication by name/type
**Status**: ✅ Basic implementation working

### Challenge 5: Relationship Ambiguity
**Issue**: Relationships may be unclear or ambiguous
**Solution**: Use confidence scoring, allow dynamic types
**Status**: ✅ Resolved with confidence thresholds

## Risk Assessment

### Medium Risk ⚠️
- AI accuracy may vary with document types
- Cost may exceed budget with large documents
- JSON parsing may fail occasionally
- Deduplication may miss some duplicates

### Mitigation Strategies
1. **Accuracy**: Test with diverse documents, use confidence thresholds
2. **Cost**: Monitor in real-time, set alerts, optimize prompts
3. **Parsing**: Implement robust error handling and retry logic
4. **Deduplication**: Start with basic approach, improve in future

## Success Metrics

### Functional Metrics
- ✅ Entity extraction accuracy >85%
- ✅ Relationship detection accuracy >75%
- ✅ Cost per document < $0.01
- ✅ Processing time < 10 seconds per document

### Performance Metrics
- ✅ Entity extraction: 2-4 seconds
- ✅ Relationship detection: 2-3 seconds
- ✅ Graph population: 2-3 seconds
- ✅ Total processing: 4-10 seconds

### Quality Metrics
- ✅ Confidence scores correlate with accuracy
- ✅ Error handling prevents failures
- ✅ User isolation working correctly
- ✅ No data corruption

### Cost Metrics
- ✅ Cost per document: $0.0006 (94% under target)
- ✅ Projected monthly cost: $1.80 (99% under budget)
- ✅ Development cost: ~$0.08
- ✅ Cost monitoring accurate

## Target Accuracy Benchmarks

### Entity Extraction
- **Person**: >90% accuracy
- **Place**: >85% accuracy
- **Organization**: >85% accuracy
- **Concept**: >80% accuracy
- **Moment**: >80% accuracy
- **Thing**: >75% accuracy

### Relationship Detection
- **KNOWS**: >80% accuracy
- **WORKS_AT**: >80% accuracy
- **LOCATED_IN**: >75% accuracy
- **PART_OF**: >75% accuracy
- **RELATED_TO**: >70% accuracy

### Overall Targets
- **Entity Extraction**: >85% average
- **Relationship Detection**: >75% average
- **False Positives**: <10%
- **False Negatives**: <15%

---

**Sprint**: Sprint 2  
**Objective**: Build AI integration layer with high accuracy and low cost  
**Duration**: 1 day  
**Status**: ✅ Complete