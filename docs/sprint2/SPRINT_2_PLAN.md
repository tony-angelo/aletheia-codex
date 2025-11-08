# Sprint 2: AI Integration & Entity Extraction

## Status: Ready to Plan (Awaiting Sprint 1 Completion)

## Overview

Sprint 2 focuses on integrating Google Gemini AI for entity extraction and relationship detection. This sprint builds on the solid foundation established in Sprint 1 and implements the core intelligence of AletheiaCodex.

---

## Objectives

### Primary Goals
1. **AI Service Abstraction Layer**: Create flexible AI provider interface
2. **Entity Extraction Pipeline**: Extract entities from document content
3. **Relationship Detection**: Identify relationships between entities
4. **Neo4j Graph Population**: Store extracted data in knowledge graph
5. **Cost Monitoring**: Track and alert on AI API usage costs

### Success Criteria
- ✅ Gemini API successfully integrated
- ✅ Entities extracted from test documents with >80% accuracy
- ✅ Relationships correctly identified and stored
- ✅ Cost tracking functional with configurable alerts
- ✅ Comprehensive error handling for AI failures

---

## Prerequisites

### From Sprint 1
- ✅ Neo4j connectivity working
- ✅ Orchestration function deployed
- ✅ Service accounts configured
- ✅ Secret Manager setup complete
- ⚠️ Orchestration function verified (pending)

### New Requirements
- [ ] Gemini API key in Secret Manager
- [ ] AI service design reviewed
- [ ] Entity extraction prompts designed
- [ ] Test dataset prepared
- [ ] Cost monitoring strategy defined

---

## Architecture Overview

### AI Service Abstraction Layer

```
┌─────────────────────────────────────────┐
│     Orchestration Function              │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │   AI Service Interface            │ │
│  │   (Abstract Base Class)           │ │
│  └───────────────┬───────────────────┘ │
│                  │                      │
│  ┌───────────────┴───────────────────┐ │
│  │                                   │ │
│  ▼                                   ▼ │
│  Gemini Provider          Future Providers│
│  (Google AI Studio)       (OpenAI, etc.) │
└─────────────────────────────────────────┘
```

### Data Flow

```
Document (Firestore)
    │
    ▼
Orchestration Function
    │
    ├─→ AI Service (Gemini)
    │   ├─→ Extract Entities
    │   └─→ Detect Relationships
    │
    ├─→ Neo4j Client
    │   ├─→ Create Entity Nodes
    │   └─→ Create Relationships
    │
    └─→ Cost Tracker
        └─→ Log Usage & Check Alerts
```

---

## Task Breakdown

### Phase 1: AI Service Foundation (Week 1)

#### Task 1.1: AI Service Interface Design
**Objective**: Create abstract interface for AI providers

**Deliverables**:
- `shared/ai/base_ai_service.py` - Abstract base class
- Interface methods:
  - `extract_entities(text: str) -> List[Entity]`
  - `detect_relationships(text: str, entities: List[Entity]) -> List[Relationship]`
  - `get_cost_estimate(text: str) -> float`
  - `get_provider_name() -> str`

**Implementation Details**:
```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class Entity:
    type: str  # Person, Organization, Place, etc.
    name: str
    properties: Dict[str, Any]
    confidence: float

@dataclass
class Relationship:
    source_entity: str
    target_entity: str
    relationship_type: str
    properties: Dict[str, Any]
    confidence: float

class BaseAIService(ABC):
    @abstractmethod
    async def extract_entities(self, text: str, user_id: str) -> List[Entity]:
        """Extract entities from text"""
        pass
    
    @abstractmethod
    async def detect_relationships(self, text: str, entities: List[Entity]) -> List[Relationship]:
        """Detect relationships between entities"""
        pass
    
    @abstractmethod
    def get_cost_estimate(self, text: str) -> float:
        """Estimate cost for processing text"""
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Return provider name"""
        pass
```

**Testing**:
- Unit tests for interface validation
- Mock implementation for testing

**Estimated Time**: 4-6 hours

---

#### Task 1.2: Gemini Provider Implementation
**Objective**: Implement Gemini-specific AI service

**Deliverables**:
- `shared/ai/gemini_service.py` - Gemini implementation
- Prompt templates for entity extraction
- Prompt templates for relationship detection
- Response parsing logic

**Implementation Details**:
```python
import google.generativeai as genai
from .base_ai_service import BaseAIService, Entity, Relationship

class GeminiService(BaseAIService):
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
    async def extract_entities(self, text: str, user_id: str) -> List[Entity]:
        prompt = self._build_entity_extraction_prompt(text)
        response = await self.model.generate_content_async(prompt)
        return self._parse_entity_response(response.text)
    
    def _build_entity_extraction_prompt(self, text: str) -> str:
        return f"""
        Extract all entities from the following text. Return as JSON array.
        
        Entity types: Person, Organization, Place, Concept, Moment, Thing
        
        For each entity, provide:
        - type: entity type
        - name: entity name
        - properties: relevant properties (dict)
        - confidence: confidence score (0-1)
        
        Text: {text}
        
        Return only valid JSON, no markdown formatting.
        """
```

**Prompt Engineering**:
- Entity extraction prompt with examples
- Relationship detection prompt with examples
- Few-shot learning examples
- Output format specification

**Testing**:
- Test with sample documents
- Verify JSON parsing
- Check entity accuracy
- Validate confidence scores

**Estimated Time**: 8-12 hours

---

#### Task 1.3: Secret Manager Integration
**Objective**: Securely access Gemini API key

**Deliverables**:
- Update `shared/utils/secret_manager.py`
- Add `get_gemini_api_key()` function
- Add caching for API key
- Add error handling

**Implementation Details**:
```python
def get_gemini_api_key() -> str:
    """Get Gemini API key from Secret Manager"""
    return get_secret("GEMINI_API_KEY")

# Usage in orchestration function
from shared.utils.secret_manager import get_gemini_api_key
from shared.ai.gemini_service import GeminiService

api_key = get_gemini_api_key()
ai_service = GeminiService(api_key)
```

**Testing**:
- Verify secret retrieval
- Test caching behavior
- Check error handling

**Estimated Time**: 2-3 hours

---

### Phase 2: Entity Extraction Pipeline (Week 1-2)

#### Task 2.1: Entity Extraction Logic
**Objective**: Implement entity extraction in orchestration function

**Deliverables**:
- Update `functions/orchestration/main.py`
- Add entity extraction step
- Add entity validation
- Add error handling

**Implementation Details**:
```python
async def process_document(document_id: str, content: str, user_id: str):
    # Initialize AI service
    ai_service = GeminiService(get_gemini_api_key())
    
    # Extract entities
    logger.info(f"Extracting entities from document {document_id}")
    entities = await ai_service.extract_entities(content, user_id)
    logger.info(f"Extracted {len(entities)} entities")
    
    # Validate entities
    valid_entities = [e for e in entities if e.confidence > 0.7]
    logger.info(f"Validated {len(valid_entities)} entities")
    
    # Store in review queue
    for entity in valid_entities:
        await store_in_review_queue(document_id, entity, user_id)
    
    return valid_entities
```

**Entity Validation**:
- Confidence threshold (default: 0.7)
- Required fields validation
- Duplicate detection
- Type validation

**Testing**:
- Test with various document types
- Verify entity quality
- Check error handling
- Validate logging

**Estimated Time**: 6-8 hours

---

#### Task 2.2: Review Queue Integration
**Objective**: Store extracted entities in Firestore review queue

**Deliverables**:
- Update Firestore schema for review queue
- Implement `store_in_review_queue()` function
- Add batch processing for multiple entities
- Add status tracking

**Firestore Schema**:
```typescript
interface ReviewQueueItem {
  id: string;
  user_id: string;
  document_id: string;
  entity_type: string;
  entity_name: string;
  entity_properties: Record<string, any>;
  confidence: number;
  status: 'pending' | 'approved' | 'rejected';
  created_at: Timestamp;
  reviewed_at?: Timestamp;
}
```

**Implementation Details**:
```python
async def store_in_review_queue(document_id: str, entity: Entity, user_id: str):
    firestore_client = get_firestore_client()
    review_queue = firestore_client.collection('review_queue')
    
    item = {
        'user_id': user_id,
        'document_id': document_id,
        'entity_type': entity.type,
        'entity_name': entity.name,
        'entity_properties': entity.properties,
        'confidence': entity.confidence,
        'status': 'pending',
        'created_at': firestore.SERVER_TIMESTAMP
    }
    
    doc_ref = review_queue.add(item)
    logger.info(f"Added entity to review queue: {doc_ref.id}")
    return doc_ref.id
```

**Testing**:
- Verify Firestore writes
- Check batch processing
- Validate schema compliance
- Test error handling

**Estimated Time**: 4-6 hours

---

#### Task 2.3: Entity Type Mapping
**Objective**: Map extracted entities to Neo4j node types

**Deliverables**:
- Entity type mapping configuration
- Dynamic type handling for "Thing" nodes
- Type validation logic
- Fallback handling

**Implementation Details**:
```python
ENTITY_TYPE_MAPPING = {
    'Person': 'Person',
    'Organization': 'Organization',
    'Place': 'Place',
    'Concept': 'Concept',
    'Moment': 'Moment',
    'Company': 'Organization',  # Alias
    'Location': 'Place',  # Alias
    'Event': 'Moment',  # Alias
}

def map_entity_type(extracted_type: str) -> str:
    """Map extracted entity type to Neo4j node type"""
    return ENTITY_TYPE_MAPPING.get(extracted_type, 'Thing')
```

**Testing**:
- Test all standard types
- Test aliases
- Test unknown types (should map to Thing)
- Verify Neo4j compatibility

**Estimated Time**: 2-3 hours

---

### Phase 3: Relationship Detection (Week 2)

#### Task 3.1: Relationship Detection Logic
**Objective**: Identify relationships between entities

**Deliverables**:
- Relationship detection implementation
- Relationship validation
- Confidence scoring
- Error handling

**Implementation Details**:
```python
async def detect_relationships(content: str, entities: List[Entity], user_id: str):
    ai_service = GeminiService(get_gemini_api_key())
    
    # Detect relationships
    logger.info(f"Detecting relationships for {len(entities)} entities")
    relationships = await ai_service.detect_relationships(content, entities)
    logger.info(f"Detected {len(relationships)} relationships")
    
    # Validate relationships
    valid_relationships = [r for r in relationships if r.confidence > 0.6]
    logger.info(f"Validated {len(valid_relationships)} relationships")
    
    return valid_relationships
```

**Relationship Types**:
- Standard types: WORKS_AT, LOCATED_IN, KNOWS, etc.
- Dynamic types: AI can create new relationship types
- Bidirectional handling
- Property extraction

**Testing**:
- Test with entity pairs
- Verify relationship types
- Check confidence scores
- Validate properties

**Estimated Time**: 6-8 hours

---

#### Task 3.2: Relationship Storage
**Objective**: Store relationships in review queue

**Deliverables**:
- Relationship review queue schema
- Storage implementation
- Batch processing
- Status tracking

**Firestore Schema**:
```typescript
interface RelationshipReviewItem {
  id: string;
  user_id: string;
  document_id: string;
  source_entity_id: string;
  target_entity_id: string;
  relationship_type: string;
  properties: Record<string, any>;
  confidence: number;
  status: 'pending' | 'approved' | 'rejected';
  created_at: Timestamp;
  reviewed_at?: Timestamp;
}
```

**Testing**:
- Verify Firestore writes
- Check entity references
- Validate schema
- Test error handling

**Estimated Time**: 4-6 hours

---

### Phase 4: Neo4j Graph Population (Week 2-3)

#### Task 4.1: Entity Node Creation
**Objective**: Create entity nodes in Neo4j from approved items

**Deliverables**:
- Node creation logic
- Property mapping
- Duplicate detection
- Error handling

**Implementation Details**:
```python
async def create_entity_node(entity: Entity, user_id: str):
    neo4j_client = get_neo4j_client()
    
    # Map entity type
    node_type = map_entity_type(entity.type)
    
    # Create node with properties
    query = f"""
    MATCH (u:User {{user_id: $user_id}})
    MERGE (u)-[:OWNS]->(e:{node_type} {{name: $name}})
    SET e += $properties
    RETURN e
    """
    
    result = await neo4j_client.execute_query(
        query,
        user_id=user_id,
        name=entity.name,
        properties=entity.properties
    )
    
    logger.info(f"Created {node_type} node: {entity.name}")
    return result
```

**Testing**:
- Test all entity types
- Verify property storage
- Check duplicate handling
- Validate user isolation

**Estimated Time**: 6-8 hours

---

#### Task 4.2: Relationship Creation
**Objective**: Create relationships in Neo4j from approved items

**Deliverables**:
- Relationship creation logic
- Dynamic relationship type handling
- Property storage
- Error handling

**Implementation Details**:
```python
async def create_relationship(relationship: Relationship, user_id: str):
    neo4j_client = get_neo4j_client()
    
    query = f"""
    MATCH (u:User {{user_id: $user_id}})
    MATCH (u)-[:OWNS]->(source {{name: $source_name}})
    MATCH (u)-[:OWNS]->(target {{name: $target_name}})
    MERGE (source)-[r:{relationship.relationship_type}]->(target)
    SET r += $properties
    RETURN r
    """
    
    result = await neo4j_client.execute_query(
        query,
        user_id=user_id,
        source_name=relationship.source_entity,
        target_name=relationship.target_entity,
        properties=relationship.properties
    )
    
    logger.info(f"Created relationship: {relationship.relationship_type}")
    return result
```

**Testing**:
- Test standard relationship types
- Test dynamic relationship types
- Verify property storage
- Check error handling

**Estimated Time**: 6-8 hours

---

### Phase 5: Cost Monitoring (Week 3)

#### Task 5.1: Cost Tracking Implementation
**Objective**: Track AI API usage and costs

**Deliverables**:
- `shared/monitoring/cost_tracker.py`
- Usage logging
- Cost calculation
- Alert system

**Implementation Details**:
```python
class CostTracker:
    def __init__(self):
        self.firestore_client = get_firestore_client()
        
    async def log_usage(self, user_id: str, provider: str, 
                       input_tokens: int, output_tokens: int, cost: float):
        usage_log = {
            'user_id': user_id,
            'provider': provider,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'cost': cost,
            'timestamp': firestore.SERVER_TIMESTAMP
        }
        
        self.firestore_client.collection('usage_logs').add(usage_log)
        
        # Check alerts
        await self.check_cost_alerts(user_id)
    
    async def check_cost_alerts(self, user_id: str):
        # Get user's cost settings
        user_doc = self.firestore_client.collection('users').document(user_id).get()
        cost_limits = user_doc.get('cost_limits', {})
        
        # Calculate current usage
        daily_cost = await self.get_daily_cost(user_id)
        weekly_cost = await self.get_weekly_cost(user_id)
        monthly_cost = await self.get_monthly_cost(user_id)
        
        # Check thresholds and send alerts
        if daily_cost > cost_limits.get('daily', float('inf')):
            await self.send_alert(user_id, 'daily', daily_cost)
```

**Cost Calculation**:
- Gemini 2.0 Flash pricing:
  - Input: $0.075 per 1M tokens
  - Output: $0.30 per 1M tokens
- Token counting
- Cost aggregation by timeframe

**Testing**:
- Test usage logging
- Verify cost calculations
- Check alert triggers
- Validate timeframe aggregation

**Estimated Time**: 8-10 hours

---

#### Task 5.2: Cost Monitoring Dashboard Data
**Objective**: Provide cost data for future dashboard

**Deliverables**:
- Cost aggregation queries
- Usage statistics
- Trend analysis
- Export functionality

**Implementation Details**:
```python
async def get_cost_summary(user_id: str, timeframe: str):
    """Get cost summary for user"""
    if timeframe == 'daily':
        start_date = datetime.now() - timedelta(days=1)
    elif timeframe == 'weekly':
        start_date = datetime.now() - timedelta(weeks=1)
    elif timeframe == 'monthly':
        start_date = datetime.now() - timedelta(days=30)
    
    usage_logs = self.firestore_client.collection('usage_logs') \
        .where('user_id', '==', user_id) \
        .where('timestamp', '>=', start_date) \
        .stream()
    
    total_cost = sum(log.get('cost', 0) for log in usage_logs)
    return {
        'timeframe': timeframe,
        'total_cost': total_cost,
        'start_date': start_date,
        'end_date': datetime.now()
    }
```

**Testing**:
- Test aggregation queries
- Verify timeframe calculations
- Check data accuracy
- Validate export format

**Estimated Time**: 4-6 hours

---

## Testing Strategy

### Unit Tests
- AI service interface tests
- Gemini provider tests
- Entity validation tests
- Relationship detection tests
- Cost calculation tests

### Integration Tests
- End-to-end entity extraction
- Neo4j graph population
- Cost tracking workflow
- Error handling scenarios

### Test Documents
Prepare diverse test documents:
1. **Simple**: Clear entities and relationships
2. **Complex**: Multiple entities, complex relationships
3. **Ambiguous**: Unclear entities, low confidence
4. **Edge Cases**: Empty, very long, special characters

### Performance Tests
- Token usage measurement
- Response time tracking
- Cost per document analysis
- Throughput testing

---

## Documentation Requirements

### Technical Documentation
- [ ] AI service architecture guide
- [ ] Gemini integration guide
- [ ] Entity extraction guide
- [ ] Relationship detection guide
- [ ] Cost monitoring guide

### Operational Documentation
- [ ] Deployment guide for AI components
- [ ] Troubleshooting guide
- [ ] Cost optimization guide
- [ ] Prompt engineering guide

### Testing Documentation
- [ ] Test plan
- [ ] Test cases
- [ ] Test results
- [ ] Performance benchmarks

---

## Risk Assessment

### High Risk
1. **AI Response Quality**: Gemini may not extract entities accurately
   - **Mitigation**: Extensive prompt engineering, confidence thresholds
   
2. **Cost Overruns**: AI API costs could exceed budget
   - **Mitigation**: Cost monitoring, rate limiting, alerts

### Medium Risk
1. **API Rate Limits**: Gemini API may have rate limits
   - **Mitigation**: Implement retry logic, queue management
   
2. **Response Parsing**: AI responses may not match expected format
   - **Mitigation**: Robust parsing, fallback handling

### Low Risk
1. **Neo4j Performance**: Large graphs may slow down
   - **Mitigation**: Indexing, query optimization
   
2. **Firestore Limits**: Review queue may grow large
   - **Mitigation**: Cleanup policies, archiving

---

## Success Metrics

### Functional Metrics
- Entity extraction accuracy: >80%
- Relationship detection accuracy: >70%
- System uptime: >99%
- Error rate: <5%

### Performance Metrics
- Entity extraction time: <5 seconds per document
- Neo4j write time: <1 second per entity
- Cost per document: <$0.01
- Throughput: >100 documents per hour

### Quality Metrics
- Confidence scores calibrated
- Review queue manageable (<100 pending items)
- User satisfaction with entity quality
- Cost within budget

---

## Timeline Estimate

### Week 1: Foundation
- Days 1-2: AI service interface and Gemini provider
- Days 3-4: Entity extraction pipeline
- Day 5: Testing and refinement

### Week 2: Relationships & Storage
- Days 1-2: Relationship detection
- Days 3-4: Neo4j graph population
- Day 5: Integration testing

### Week 3: Cost Monitoring & Polish
- Days 1-2: Cost tracking implementation
- Days 3-4: Documentation and testing
- Day 5: Final verification and handoff

### Total Duration: 3 weeks

---

## Dependencies

### External Services
- Google Gemini API (2.0 Flash)
- Neo4j Aura database
- Google Cloud Secret Manager
- Google Cloud Firestore
- Google Cloud Logging

### Internal Components
- Sprint 1 orchestration function
- Neo4j client (enhanced)
- Firestore client
- Secret Manager utilities
- Logging infrastructure

---

## Completion Criteria

### Must Have
- ✅ Gemini API integrated and working
- ✅ Entities extracted with >80% accuracy
- ✅ Relationships detected and stored
- ✅ Neo4j graph populated correctly
- ✅ Cost monitoring functional
- ✅ Comprehensive testing completed
- ✅ Documentation complete

### Should Have
- Integration tests passing
- Performance benchmarks established
- Error handling comprehensive
- Logging detailed and structured

### Nice to Have
- Multiple AI provider support
- Advanced prompt optimization
- Cost optimization strategies
- Performance tuning

---

## Next Steps After Sprint 2

Once Sprint 2 is complete:

1. **Sprint 3: Review Queue & User Interface**
   - Build user approval workflow
   - Create basic web interface
   - Implement real-time updates

2. **Sprint 4: Query Interface**
   - Natural language query processing
   - Graph visualization
   - Search functionality

3. **Sprint 5: Proactive Suggestions**
   - Pattern detection
   - Suggestion generation
   - Notification system

---

## Conclusion

Sprint 2 is the most critical sprint as it implements the core AI functionality of AletheiaCodex. Success in this sprint will validate the entire architecture and enable rapid progress in subsequent sprints.

The modular design with AI service abstraction ensures flexibility for future enhancements and provider changes. The comprehensive testing and monitoring will ensure quality and cost control.

**Recommended Start Date**: Immediately after Sprint 1 orchestration verification is complete.