# Sprint [N] Guide - [Sprint Name]

**Sprint Number**: [N]  
**Sprint Goal**: [Brief statement of sprint goal]  
**Created**: [Date]  
**Author**: Architect  
**Target Completion**: [Date]  

---

## Sprint Overview

### Purpose
[Describe the overall purpose and objectives of this sprint. What are we trying to achieve? Why is this sprint important?]

### Success Criteria
[Define measurable criteria for sprint success. How will we know the sprint is complete and successful?]

- [ ] Criterion 1: [Specific, measurable criterion]
- [ ] Criterion 2: [Specific, measurable criterion]
- [ ] Criterion 3: [Specific, measurable criterion]

### Sprint Context
[Provide context about where this sprint fits in the overall project. What was completed in previous sprints? How does this sprint build on that work?]

---

## Features by Domain

### Backend Features

#### Feature 1: [Feature Name]
**Priority**: High | Medium | Low  
**Assigned to**: Admin-Backend  
**Estimated Effort**: [Hours/Days]

**Description**:
[Detailed description of the feature. What needs to be implemented?]

**Acceptance Criteria**:
- [ ] [Specific, testable criterion]
- [ ] [Specific, testable criterion]
- [ ] [Specific, testable criterion]

**Technical Requirements**:
- [Specific technical requirement]
- [Specific technical requirement]
- [Specific technical requirement]

**Dependencies**:
- [List any dependencies on other features or external factors]

**Integration Points**:
- [Describe how this integrates with other domains]

**Testing Requirements**:
- [Specific testing requirements]

---

#### Feature 2: [Feature Name]
[Repeat structure for each backend feature]

---

### Frontend Features

#### Feature 1: [Feature Name]
**Priority**: High | Medium | Low  
**Assigned to**: Admin-Frontend  
**Estimated Effort**: [Hours/Days]

**Description**:
[Detailed description of the feature. What needs to be implemented?]

**Acceptance Criteria**:
- [ ] [Specific, testable criterion]
- [ ] [Specific, testable criterion]
- [ ] [Specific, testable criterion]

**Technical Requirements**:
- [Specific technical requirement]
- [Specific technical requirement]
- [Specific technical requirement]

**Dependencies**:
- [List any dependencies on other features or external factors]

**Integration Points**:
- [Describe how this integrates with other domains]

**Testing Requirements**:
- [Specific testing requirements]

---

#### Feature 2: [Feature Name]
[Repeat structure for each frontend feature]

---

### Infrastructure Features

#### Feature 1: [Feature Name]
**Priority**: High | Medium | Low  
**Assigned to**: Admin-Infrastructure  
**Estimated Effort**: [Hours/Days]

**Description**:
[Detailed description of the task. What needs to be configured or deployed?]

**Acceptance Criteria**:
- [ ] [Specific, testable criterion]
- [ ] [Specific, testable criterion]
- [ ] [Specific, testable criterion]

**Technical Requirements**:
- [Specific technical requirement]
- [Specific technical requirement]
- [Specific technical requirement]

**Dependencies**:
- [List any dependencies on other features or external factors]

**Integration Points**:
- [Describe how this integrates with other domains]

**Validation Requirements**:
- [Specific validation requirements]

---

#### Feature 2: [Feature Name]
[Repeat structure for each infrastructure feature]

---

## Architectural Guidance

### Overall Approach
[Describe the overall architectural approach for this sprint. What patterns should be used? What principles should guide implementation?]

### Design Patterns
[Specify design patterns to use for this sprint]

- **Pattern 1**: [When to use, how to implement]
- **Pattern 2**: [When to use, how to implement]

### Technical Constraints
[List any technical constraints that must be respected]

- [Constraint 1]
- [Constraint 2]

### Integration Considerations
[Describe how different domains should integrate their work]

- **Backend ↔ Frontend**: [Integration approach]
- **Backend ↔ Infrastructure**: [Integration approach]
- **Frontend ↔ Infrastructure**: [Integration approach]

### Performance Considerations
[Specify performance requirements and optimization strategies]

- [Performance requirement 1]
- [Performance requirement 2]

### Security Considerations
[Specify security requirements and best practices]

- [Security requirement 1]
- [Security requirement 2]

---

## Escalation Criteria

### When to Escalate
Escalate to Architect when you encounter:

1. **Architectural Ambiguity**
   - Requirements are unclear or contradictory
   - Multiple valid implementation approaches exist
   - Architectural decision needed

2. **Technical Blockers**
   - External dependency is unavailable or broken
   - Technical limitation prevents implementation
   - Unexpected technical constraint discovered

3. **Scope Concerns**
   - Feature scope is larger than estimated
   - Requirements conflict with existing architecture
   - New requirements emerge during implementation

4. **Integration Issues**
   - Cross-domain integration is unclear
   - API contract needs clarification
   - Data model conflicts arise

5. **Resource Constraints**
   - Time estimate was significantly off
   - Additional expertise needed
   - External service limitations discovered

### How to Escalate
1. Document the blocker using the escalation template at [artifacts]/templates/escalation-doc.md
2. Save to your outbox: [artifacts]/admin-[domain]/outbox/escalation-[topic].md
3. Notify Human that escalation is ready
4. Wait for Architect response before proceeding

### What to Include in Escalation
- Clear description of the blocker
- Context and background
- What you've tried
- Proposed solutions (if any)
- Impact on sprint timeline
- Questions for Architect

---

## Quality Standards

### Code Quality
- Follow code standards defined in [artifacts]/architect/code-standards.md
- Maintain test coverage >80%
- All tests must pass before sprint completion
- Code must be reviewed and approved

### Documentation
- Update inline code documentation
- Update README files for modified components
- Document API changes
- Create session logs for each work session

### Testing
- Unit tests for all new code
- Integration tests for workflows
- Manual testing of user-facing features
- Performance testing for critical paths

### Git Standards
- Follow git standards defined in [artifacts]/architect/git-standards.md
- Descriptive commit messages
- Logical commit organization
- Branch naming conventions

---

## Sprint Workflow

### 1. Sprint Initialization
- Review this sprint guide thoroughly
- Understand all assigned features
- Identify dependencies and risks
- Create implementation plan
- Set up sprint branch

### 2. Implementation
- Implement features according to specifications
- Follow architectural guidance
- Write tests alongside code
- Commit changes regularly
- Create session logs

### 3. Testing
- Run all tests frequently
- Fix failing tests immediately
- Perform manual testing
- Validate against acceptance criteria

### 4. Documentation
- Update inline documentation
- Update README files
- Document API changes
- Create final session log

### 5. Sprint Completion
- Verify all acceptance criteria met
- Ensure all tests pass
- Commit all changes
- Push branch to repository
- Notify Docmaster-Sprint

---

## References

### Related Documentation
- [Project Vision](../../PROJECT_VISION.md)
- [Code Standards]([artifacts]/architect/code-standards.md)
- [Git Standards]([artifacts]/architect/git-standards.md)
- [API Standards]([artifacts]/architect/api-standards.md)

### Previous Sprint Outcomes
[Reference previous sprint summaries if applicable]

- [Sprint N-1 Summary]([artifacts]/docmaster-sprint/outbox/sprint-[N-1]-summary.md)

### Architecture Documents
[Reference relevant architecture documents]

- [Domain Definitions]([artifacts]/architect/domain-definitions.md)
- [Architecture Documentation]([artifacts]/architect/architecture/)

---

## Notes

### Important Considerations
[Any additional notes or considerations for this sprint]

### Known Issues
[List any known issues that may affect this sprint]

### Future Work
[Note any work that is out of scope for this sprint but should be considered in future sprints]

---

**End of Sprint Guide**