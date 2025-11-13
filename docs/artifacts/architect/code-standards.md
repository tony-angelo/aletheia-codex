# Code Standards - AletheiaCodex Project

**Document Type**: Standards Definition  
**Created**: January 2025  
**Author**: Architect Node  
**Status**: Active  

---

## Overview

This document defines the code standards for the AletheiaCodex project. All code must follow these standards to ensure consistency, maintainability, and quality across the codebase.

---

## General Principles

### Code Quality Principles

1. **Readability**: Code should be easy to read and understand
2. **Simplicity**: Prefer simple solutions over complex ones
3. **Consistency**: Follow established patterns and conventions
4. **Maintainability**: Write code that is easy to modify and extend
5. **Testability**: Write code that is easy to test
6. **Documentation**: Document complex logic and design decisions

### SOLID Principles

1. **Single Responsibility**: Each module/class should have one reason to change
2. **Open/Closed**: Open for extension, closed for modification
3. **Liskov Substitution**: Subtypes must be substitutable for their base types
4. **Interface Segregation**: Many specific interfaces are better than one general interface
5. **Dependency Inversion**: Depend on abstractions, not concretions

---

## Python Standards (Backend)

### Style Guide

**Base Standard**: PEP 8

**Formatter**: Black (line length: 88)

**Linter**: Flake8 with pylint

### Code Organization

#### File Structure
```python
"""Module docstring describing the module's purpose.

This module provides functionality for...
"""

# Standard library imports
import os
import sys
from typing import Dict, List, Optional

# Third-party imports
import requests
from google.cloud import firestore

# Local imports
from shared.db import neo4j_client
from shared.models import Entity

# Constants
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30

# Module-level variables (if needed)
_cache: Dict[str, Any] = {}

# Classes and functions
class MyClass:
    """Class docstring."""
    pass

def my_function():
    """Function docstring."""
    pass
```

### Naming Conventions

#### Variables and Functions
```python
# Use snake_case for variables and functions
user_id = "123"
entity_count = 10

def get_user_entities(user_id: str) -> List[Entity]:
    """Retrieve entities for a user."""
    pass

# Use UPPER_CASE for constants
MAX_ENTITIES = 100
API_TIMEOUT = 30
```

#### Classes
```python
# Use PascalCase for classes
class EntityExtractor:
    """Extract entities from text."""
    pass

class Neo4jClient:
    """Client for Neo4j database operations."""
    pass
```

#### Private Members
```python
# Use leading underscore for private/internal
class MyClass:
    def __init__(self):
        self._internal_state = {}
        self.__private_var = None  # Name mangling
    
    def _internal_method(self):
        """Internal method not part of public API."""
        pass
```

### Type Hints

**Required**: All function signatures must have type hints

```python
from typing import Dict, List, Optional, Union, Any

def process_entities(
    entities: List[Dict[str, Any]],
    user_id: str,
    confidence_threshold: float = 0.8
) -> Dict[str, List[Entity]]:
    """Process entities and group by type.
    
    Args:
        entities: List of entity dictionaries
        user_id: User identifier
        confidence_threshold: Minimum confidence score
        
    Returns:
        Dictionary mapping entity types to entity lists
        
    Raises:
        ValueError: If entities list is empty
        RuntimeError: If processing fails
    """
    pass

# Optional types
def get_entity(entity_id: str) -> Optional[Entity]:
    """Get entity by ID, returns None if not found."""
    pass

# Union types
def process_input(data: Union[str, Dict[str, Any]]) -> Entity:
    """Process input that can be string or dict."""
    pass
```

### Docstrings

**Required**: All modules, classes, and public functions must have docstrings

**Format**: Google style

```python
def extract_entities(
    text: str,
    entity_types: List[str],
    confidence_threshold: float = 0.8
) -> List[Entity]:
    """Extract entities from text using AI.
    
    This function uses the Gemini API to extract entities of specified
    types from the input text. Only entities with confidence scores above
    the threshold are returned.
    
    Args:
        text: Input text to extract entities from
        entity_types: List of entity types to extract (e.g., ["Person", "Organization"])
        confidence_threshold: Minimum confidence score (0.0 to 1.0), defaults to 0.8
        
    Returns:
        List of Entity objects with confidence scores above threshold
        
    Raises:
        ValueError: If text is empty or entity_types is empty
        RuntimeError: If API call fails after retries
        
    Example:
        >>> entities = extract_entities(
        ...     "John works at Google",
        ...     ["Person", "Organization"]
        ... )
        >>> len(entities)
        2
    """
    pass
```

### Error Handling

```python
# Use specific exceptions
def get_entity(entity_id: str) -> Entity:
    """Get entity by ID."""
    if not entity_id:
        raise ValueError("entity_id cannot be empty")
    
    try:
        entity = db.get(entity_id)
    except DatabaseError as e:
        logger.error(f"Database error: {e}")
        raise RuntimeError(f"Failed to retrieve entity: {entity_id}") from e
    
    if entity is None:
        raise EntityNotFoundError(f"Entity not found: {entity_id}")
    
    return entity

# Use context managers for resources
def process_file(file_path: str) -> None:
    """Process file contents."""
    with open(file_path, 'r') as f:
        content = f.read()
        # Process content
```

### Logging

```python
import logging

# Module-level logger
logger = logging.getLogger(__name__)

def process_data(data: Dict[str, Any]) -> None:
    """Process data with logging."""
    logger.info(f"Processing data for user: {data.get('user_id')}")
    
    try:
        result = expensive_operation(data)
        logger.debug(f"Operation result: {result}")
    except Exception as e:
        logger.error(f"Processing failed: {e}", exc_info=True)
        raise
    
    logger.info("Processing complete")
```

### Testing

```python
import pytest
from unittest.mock import Mock, patch

def test_extract_entities_success():
    """Test successful entity extraction."""
    # Arrange
    text = "John works at Google"
    expected_entities = [
        Entity(name="John", type="Person"),
        Entity(name="Google", type="Organization")
    ]
    
    # Act
    result = extract_entities(text, ["Person", "Organization"])
    
    # Assert
    assert len(result) == 2
    assert result[0].name == "John"
    assert result[1].name == "Google"

def test_extract_entities_empty_text():
    """Test extraction with empty text raises ValueError."""
    with pytest.raises(ValueError, match="text cannot be empty"):
        extract_entities("", ["Person"])

@patch('shared.ai.gemini_client.GeminiClient')
def test_extract_entities_with_mock(mock_client):
    """Test extraction with mocked API client."""
    # Setup mock
    mock_client.return_value.extract.return_value = [...]
    
    # Test with mock
    result = extract_entities("test", ["Person"])
    
    # Verify mock was called
    mock_client.return_value.extract.assert_called_once()
```

---

## TypeScript Standards (Frontend)

### Style Guide

**Base Standard**: Airbnb TypeScript Style Guide

**Formatter**: Prettier

**Linter**: ESLint with TypeScript plugin

### Code Organization

#### File Structure
```typescript
/**
 * Component for displaying entity cards.
 * 
 * This component renders entity information in a card format
 * with actions for approval and rejection.
 */

// React imports
import React, { useState, useEffect } from 'react';

// Third-party imports
import { useQuery } from 'react-query';

// Local imports
import { Entity } from '@/types/entity';
import { Button } from '@/components/Button';
import { useAuth } from '@/hooks/useAuth';

// Types
interface EntityCardProps {
  entity: Entity;
  onApprove: (id: string) => void;
  onReject: (id: string) => void;
}

// Component
export const EntityCard: React.FC<EntityCardProps> = ({
  entity,
  onApprove,
  onReject,
}) => {
  // Component implementation
};
```

### Naming Conventions

#### Variables and Functions
```typescript
// Use camelCase for variables and functions
const userId = "123";
const entityCount = 10;

function getUserEntities(userId: string): Entity[] {
  // Implementation
}

// Use UPPER_CASE for constants
const MAX_ENTITIES = 100;
const API_TIMEOUT = 30;
```

#### Types and Interfaces
```typescript
// Use PascalCase for types and interfaces
interface EntityCardProps {
  entity: Entity;
  onApprove: (id: string) => void;
}

type EntityType = 'Person' | 'Organization' | 'Place';

// Use 'I' prefix for interfaces (optional, but consistent)
interface IEntityService {
  getEntity(id: string): Promise<Entity>;
  createEntity(entity: Entity): Promise<Entity>;
}
```

#### Components
```typescript
// Use PascalCase for React components
export const EntityCard: React.FC<EntityCardProps> = (props) => {
  // Component implementation
};

// Use PascalCase for component files
// EntityCard.tsx, ReviewQueue.tsx
```

### Type Definitions

**Required**: All function signatures and component props must have types

```typescript
// Function types
function processEntities(
  entities: Entity[],
  userId: string,
  confidenceThreshold: number = 0.8
): Record<string, Entity[]> {
  // Implementation
}

// Component props
interface ButtonProps {
  label: string;
  onClick: () => void;
  disabled?: boolean;
  variant?: 'primary' | 'secondary';
}

export const Button: React.FC<ButtonProps> = ({
  label,
  onClick,
  disabled = false,
  variant = 'primary',
}) => {
  // Component implementation
};

// Generic types
function mapEntities<T extends Entity>(
  entities: T[],
  mapper: (entity: T) => T
): T[] {
  return entities.map(mapper);
}
```

### JSDoc Comments

**Required**: All exported functions and components must have JSDoc

```typescript
/**
 * Extract entities from text using AI.
 * 
 * This function calls the backend API to extract entities of specified
 * types from the input text. Only entities with confidence scores above
 * the threshold are returned.
 * 
 * @param text - Input text to extract entities from
 * @param entityTypes - List of entity types to extract
 * @param confidenceThreshold - Minimum confidence score (0.0 to 1.0)
 * @returns Promise resolving to list of entities
 * @throws {Error} If API call fails
 * 
 * @example
 * ```typescript
 * const entities = await extractEntities(
 *   "John works at Google",
 *   ["Person", "Organization"]
 * );
 * ```
 */
export async function extractEntities(
  text: string,
  entityTypes: string[],
  confidenceThreshold: number = 0.8
): Promise<Entity[]> {
  // Implementation
}
```

### React Component Standards

```typescript
/**
 * Card component for displaying entity information.
 * 
 * Displays entity details with approve/reject actions.
 * Supports loading and error states.
 */
interface EntityCardProps {
  /** Entity to display */
  entity: Entity;
  /** Callback when entity is approved */
  onApprove: (id: string) => void;
  /** Callback when entity is rejected */
  onReject: (id: string) => void;
  /** Whether actions are disabled */
  disabled?: boolean;
}

export const EntityCard: React.FC<EntityCardProps> = ({
  entity,
  onApprove,
  onReject,
  disabled = false,
}) => {
  // Use hooks at the top
  const [isLoading, setIsLoading] = useState(false);
  const { user } = useAuth();
  
  // Event handlers
  const handleApprove = useCallback(() => {
    setIsLoading(true);
    onApprove(entity.id);
  }, [entity.id, onApprove]);
  
  // Effects
  useEffect(() => {
    // Effect logic
  }, [entity]);
  
  // Early returns for loading/error states
  if (isLoading) {
    return <LoadingSpinner />;
  }
  
  // Main render
  return (
    <div className="entity-card">
      {/* Component JSX */}
    </div>
  );
};
```

### Error Handling

```typescript
// Use try-catch for async operations
async function fetchEntity(id: string): Promise<Entity> {
  try {
    const response = await api.get(`/entities/${id}`);
    return response.data;
  } catch (error) {
    if (error instanceof ApiError) {
      console.error('API error:', error.message);
      throw new Error(`Failed to fetch entity: ${error.message}`);
    }
    throw error;
  }
}

// Use error boundaries for React components
class ErrorBoundary extends React.Component<Props, State> {
  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }
  
  render() {
    if (this.state.hasError) {
      return <ErrorDisplay />;
    }
    return this.props.children;
  }
}
```

### Testing

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { EntityCard } from './EntityCard';

describe('EntityCard', () => {
  const mockEntity: Entity = {
    id: '123',
    name: 'John Doe',
    type: 'Person',
    confidence: 0.95,
  };
  
  it('renders entity information', () => {
    render(
      <EntityCard
        entity={mockEntity}
        onApprove={jest.fn()}
        onReject={jest.fn()}
      />
    );
    
    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('Person')).toBeInTheDocument();
  });
  
  it('calls onApprove when approve button clicked', () => {
    const onApprove = jest.fn();
    
    render(
      <EntityCard
        entity={mockEntity}
        onApprove={onApprove}
        onReject={jest.fn()}
      />
    );
    
    fireEvent.click(screen.getByText('Approve'));
    
    expect(onApprove).toHaveBeenCalledWith('123');
  });
});
```

---

## Code Review Checklist

### Before Submitting Code

- [ ] Code follows style guide (Black/Prettier formatted)
- [ ] All functions have type hints (Python) or types (TypeScript)
- [ ] All public functions have docstrings/JSDoc
- [ ] No hardcoded secrets or credentials
- [ ] No commented-out code (remove or explain)
- [ ] No console.log or print statements (use proper logging)
- [ ] All tests pass
- [ ] Test coverage >80%
- [ ] No linting errors
- [ ] Code is self-documenting with clear variable names
- [ ] Complex logic is commented
- [ ] Error handling is appropriate
- [ ] Resources are properly cleaned up

### During Code Review

- [ ] Code is readable and understandable
- [ ] Logic is correct and handles edge cases
- [ ] Performance is acceptable
- [ ] Security considerations are addressed
- [ ] Error messages are helpful
- [ ] Tests cover important scenarios
- [ ] Documentation is accurate and complete

---

## Version History

**v1.0.0** - Initial code standards
- Defined Python standards (PEP 8, type hints, docstrings)
- Defined TypeScript standards (Airbnb, JSDoc, React)
- Established naming conventions
- Defined testing standards
- Created code review checklist

---

**End of Code Standards**