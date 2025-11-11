# Sprint 2 Implementation Guide - AI Integration & Entity Extraction

**Sprint**: Sprint 2  
**Duration**: 3 weeks (estimated)  
**Focus**: Core AI functionality for entity extraction and knowledge graph population  
**Prerequisites**: Sprint 1 complete (Neo4j HTTP API working)

---

## Overview

Sprint 2 implements the core AI functionality that transforms natural language notes into structured knowledge graph data. This sprint integrates Google Gemini for entity extraction, relationship detection, and populates the Neo4j knowledge graph.

---

## Objectives

### Primary Goals
1. Implement AI service abstraction layer
2. Integrate Google Gemini API for entity extraction
3. Build relationship detection logic
4. Populate Neo4j knowledge graph with extracted entities
5. Implement cost monitoring and optimization

### Success Criteria
- ✅ Gemini API integrated and functional
- ✅ Entity extraction working (Person, Place, Organization, Concept, Moment)
- ✅ Relationship detection identifying connections between entities
- ✅ Neo4j graph populated with extracted data
- ✅ Cost monitoring tracking API usage
- ✅ End-to-end workflow: Note → Entities → Graph

---

## Architecture

### Component Overview

```
User Note
    ↓
Orchestration Function
    ↓
AI Service Layer (Gemini)
    ↓
Entity Extraction
    ↓
Relationship Detection
    ↓
Neo4j Graph Population
    ↓
Review Queue (Firestore)
```

### Key Components

1. **AI Service Abstraction Layer** (`shared/ai/`)
   - Provider-agnostic interface
   - Supports multiple AI providers (Gemini, OpenAI, etc.)
   - Handles API calls, retries, and error handling

2. **Entity Extraction** (`shared/ai/entity_extractor.py`)
   - Extracts entities from text using Gemini
   - Classifies entities by type (Person, Place, Organization, etc.)
   - Extracts entity properties and metadata

3. **Relationship Detection** (`shared/ai/relationship_detector.py`)
   - Identifies relationships between entities
   - Classifies relationship types
   - Extracts relationship properties

4. **Graph Population** (`shared/db/graph_populator.py`)
   - Creates nodes in Neo4j for entities
   - Creates relationships between nodes
   - Handles deduplication and merging

5. **Cost Monitoring** (`shared/utils/cost_monitor.py`)
   - Tracks API usage and costs
   - Implements usage limits and alerts
   - Provides cost reporting

---

## Implementation Phases

### Phase 1: AI Service Abstraction Layer (Week 1, Days 1-2)

**Objective**: Create provider-agnostic AI service interface

**Files to Create**:
- `shared/ai/__init__.py`
- `shared/ai/base_provider.py` - Abstract base class
- `shared/ai/gemini_provider.py` - Gemini implementation
- `shared/ai/ai_service.py` - Main service interface

**Key Features**:
- Abstract provider interface
- Gemini API integration
- Retry logic and error handling
- Response parsing and validation
- Token counting and cost tracking

**Testing**:
- Unit tests for each provider
- Integration tests with Gemini API
- Error handling tests
- Cost tracking validation

---

### Phase 2: Entity Extraction (Week 1, Days 3-5)

**Objective**: Extract entities from natural language text

**Files to Create**:
- `shared/ai/entity_extractor.py` - Main extraction logic
- `shared/ai/prompts/entity_extraction.py` - Prompt templates
- `shared/models/entity.py` - Entity data models

**Entity Types**:
1. **Person** - Names, roles, attributes
2. **Place** - Locations, addresses, coordinates
3. **Organization** - Companies, institutions, groups
4. **Concept** - Ideas, topics, themes
5. **Moment** - Events, dates, time periods
6. **Thing** - Objects, products, items (catch-all)

**Extraction Process**:
1. Send text to Gemini with entity extraction prompt
2. Parse JSON response with extracted entities
3. Validate entity structure and types
4. Enrich entities with additional properties
5. Return structured entity list

**Testing**:
- Test with various note types
- Validate entity extraction accuracy
- Test edge cases (empty text, malformed input)
- Performance testing (latency, token usage)

---

### Phase 3: Relationship Detection (Week 2, Days 1-3)

**Objective**: Identify relationships between extracted entities

**Files to Create**:
- `shared/ai/relationship_detector.py` - Main detection logic
- `shared/ai/prompts/relationship_detection.py` - Prompt templates
- `shared/models/relationship.py` - Relationship data models

**Relationship Types**:
1. **KNOWS** - Person to Person
2. **WORKS_AT** - Person to Organization
3. **LOCATED_IN** - Entity to Place
4. **RELATED_TO** - Generic relationship
5. **HAPPENED_AT** - Moment to Place
6. **INVOLVES** - Moment to Entity
7. **PART_OF** - Entity to Entity

**Detection Process**:
1. Send entities and text to Gemini
2. Identify relationships between entities
3. Classify relationship types
4. Extract relationship properties
5. Return structured relationship list

**Testing**:
- Test relationship detection accuracy
- Validate relationship types
- Test with complex entity graphs
- Performance testing

---

### Phase 4: Graph Population (Week 2, Days 4-5)

**Objective**: Populate Neo4j knowledge graph with extracted data

**Files to Create**:
- `shared/db/graph_populator.py` - Main population logic
- `shared/db/graph_queries.py` - Cypher query templates
- `shared/db/graph_merger.py` - Entity deduplication logic

**Population Process**:
1. Create User node (if not exists)
2. Create entity nodes with properties
3. Create relationships between entities
4. Link entities to User node
5. Handle deduplication and merging
6. Update entity metadata

**Deduplication Strategy**:
- Match entities by name and type
- Merge properties from multiple mentions
- Maintain entity history
- Update confidence scores

**Testing**:
- Test node creation
- Test relationship creation
- Test deduplication logic
- Test with large entity sets
- Verify graph structure

---

### Phase 5: Cost Monitoring (Week 3, Days 1-2)

**Objective**: Track and optimize AI API costs

**Files to Create**:
- `shared/utils/cost_monitor.py` - Main monitoring logic
- `shared/utils/cost_config.py` - Cost configuration
- `shared/models/usage_record.py` - Usage tracking models

**Monitoring Features**:
1. **Token Counting** - Track input/output tokens
2. **Cost Calculation** - Calculate costs per request
3. **Usage Limits** - Enforce daily/weekly/monthly limits
4. **Alerts** - Notify when approaching limits
5. **Reporting** - Generate usage reports

**Cost Optimization**:
- Batch processing where possible
- Cache common queries
- Use appropriate model sizes
- Implement rate limiting

**Testing**:
- Test token counting accuracy
- Validate cost calculations
- Test usage limit enforcement
- Test alert triggering

---

### Phase 6: Integration & End-to-End Testing (Week 3, Days 3-5)

**Objective**: Integrate all components and validate end-to-end workflow

**Integration Tasks**:
1. Update orchestration function to use new components
2. Implement complete note processing pipeline
3. Add error handling and logging
4. Implement review queue population
5. Add monitoring and observability

**End-to-End Workflow**:
```
1. User submits note
2. Orchestration function receives request
3. Extract entities using Gemini
4. Detect relationships between entities
5. Populate Neo4j graph
6. Add to review queue (Firestore)
7. Track costs and usage
8. Return success response
```

**Testing**:
- Test complete workflow with various notes
- Test error handling and recovery
- Test with high volume
- Performance testing
- Cost validation

---

## Technical Specifications

### Gemini API Configuration

**Model**: `gemini-2.0-flash-exp`  
**Reason**: Fast, cost-effective, good for structured output

**API Endpoint**: `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent`

**Authentication**: API Key via Secret Manager (`GEMINI_API_KEY`)

**Request Format**:
```json
{
  "contents": [{
    "parts": [{"text": "prompt text"}]
  }],
  "generationConfig": {
    "temperature": 0.2,
    "topK": 40,
    "topP": 0.95,
    "maxOutputTokens": 2048,
    "responseMimeType": "application/json"
  }
}
```

**Response Parsing**:
- Extract JSON from response
- Validate structure
- Handle errors and retries

---

### Entity Extraction Prompt Template

```python
ENTITY_EXTRACTION_PROMPT = """
Extract entities from the following text. Return a JSON array of entities.

Each entity should have:
- name: The entity name
- type: One of [Person, Place, Organization, Concept, Moment, Thing]
- properties: Object with relevant properties
- confidence: Float between 0 and 1

Text:
{text}

Return only valid JSON, no additional text.
"""
```

---

### Relationship Detection Prompt Template

```python
RELATIONSHIP_DETECTION_PROMPT = """
Identify relationships between the following entities based on the text.

Entities:
{entities_json}

Text:
{text}

Return a JSON array of relationships. Each relationship should have:
- source: Entity name (must match an entity from the list)
- target: Entity name (must match an entity from the list)
- type: Relationship type (e.g., KNOWS, WORKS_AT, LOCATED_IN)
- properties: Object with relevant properties
- confidence: Float between 0 and 1

Return only valid JSON, no additional text.
"""
```

---

### Neo4j Graph Schema

**Node Labels**:
- `User` - User who created the note
- `Person` - Person entity
- `Place` - Location entity
- `Organization` - Organization entity
- `Concept` - Concept/idea entity
- `Moment` - Event/time entity
- `Thing` - Generic entity (catch-all)

**Relationship Types**:
- `CREATED` - User to Entity (who extracted it)
- `KNOWS` - Person to Person
- `WORKS_AT` - Person to Organization
- `LOCATED_IN` - Entity to Place
- `RELATED_TO` - Generic relationship
- `HAPPENED_AT` - Moment to Place
- `INVOLVES` - Moment to Entity
- `PART_OF` - Entity to Entity

**Node Properties**:
```cypher
// User node
(:User {
  id: string,
  email: string,
  created_at: datetime
})

// Entity nodes (example: Person)
(:Person {
  id: string,
  name: string,
  properties: map,
  confidence: float,
  created_at: datetime,
  updated_at: datetime,
  mention_count: int
})
```

**Relationship Properties**:
```cypher
// Relationship (example: KNOWS)
-[:KNOWS {
  confidence: float,
  created_at: datetime,
  source_note_id: string
}]->
```

---

### Cost Monitoring Configuration

**Gemini Pricing** (as of Jan 2025):
- Input: $0.075 per 1M tokens
- Output: $0.30 per 1M tokens

**Usage Limits**:
- Daily: $10
- Weekly: $50
- Monthly: $150

**Alert Thresholds**:
- 50% of limit: Warning
- 75% of limit: Alert
- 90% of limit: Critical
- 100% of limit: Block requests

---

## Testing Strategy

### Unit Tests
- Test each component in isolation
- Mock external dependencies (Gemini API, Neo4j)
- Validate input/output formats
- Test error handling

### Integration Tests
- Test component interactions
- Use real Gemini API (with test key)
- Use real Neo4j instance (test database)
- Validate end-to-end data flow

### Performance Tests
- Measure latency for each component
- Test with various note sizes
- Test with high entity counts
- Validate cost per operation

### Acceptance Tests
- Test complete user workflows
- Validate against success criteria
- Test with real-world notes
- User acceptance testing

---

## Deployment Strategy

### Deployment Steps
1. Deploy updated orchestration function
2. Verify Gemini API connectivity
3. Test entity extraction
4. Test relationship detection
5. Test graph population
6. Verify cost monitoring
7. Run end-to-end tests
8. Monitor logs and metrics

### Rollback Plan
- Keep Sprint 1 version deployed
- Test Sprint 2 in staging first
- Deploy to production incrementally
- Monitor for errors
- Rollback if issues detected

---

## Success Metrics

### Functional Metrics
- ✅ Entity extraction accuracy > 85%
- ✅ Relationship detection accuracy > 75%
- ✅ Graph population success rate > 95%
- ✅ End-to-end latency < 10 seconds
- ✅ Cost per note < $0.01

### Quality Metrics
- ✅ Code coverage > 80%
- ✅ All tests passing
- ✅ No critical bugs
- ✅ Documentation complete
- ✅ Performance within targets

---

## Risks & Mitigations

### Risk 1: Gemini API Rate Limits
**Mitigation**: Implement exponential backoff, request queuing, and rate limiting

### Risk 2: High API Costs
**Mitigation**: Implement cost monitoring, usage limits, and optimization strategies

### Risk 3: Entity Extraction Accuracy
**Mitigation**: Iterative prompt engineering, validation, and user feedback loop

### Risk 4: Graph Complexity
**Mitigation**: Implement deduplication, entity merging, and graph optimization

### Risk 5: Performance Issues
**Mitigation**: Batch processing, caching, and asynchronous processing

---

## Documentation Requirements

### Code Documentation
- Docstrings for all functions and classes
- Type hints for all parameters and returns
- Inline comments for complex logic
- README files for each module

### API Documentation
- Gemini API integration guide
- Neo4j query documentation
- Cost monitoring guide
- Error handling guide

### User Documentation
- Entity types and examples
- Relationship types and examples
- Cost information
- Troubleshooting guide

---

## Next Steps After Sprint 2

### Sprint 3 Preview
- Review queue implementation
- User approval workflow
- Confidence scoring refinement
- Basic web interface

### Future Enhancements
- Support for additional AI providers
- Advanced entity merging
- Temporal relationship tracking
- Graph visualization

---

**Sprint 2 Start**: TBD (after Sprint 1 PR merge)  
**Estimated Completion**: 3 weeks from start  
**Success Criteria**: All objectives met, tests passing, deployed to production

---

*End of Sprint 2 Implementation Guide*