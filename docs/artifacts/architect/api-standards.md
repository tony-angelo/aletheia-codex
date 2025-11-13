# API Standards - AletheiaCodex Project

**Document Type**: Standards Definition  
**Created**: January 2025  
**Author**: Architect Node  
**Status**: Active  

---

## Overview

This document defines the API standards for the AletheiaCodex project. All API endpoints must follow these standards to ensure consistency, usability, and maintainability.

---

## RESTful Design Principles

### Resource-Based URLs

**Good**:
- `GET /api/entities` - Get list of entities
- `GET /api/entities/{id}` - Get specific entity
- `POST /api/entities` - Create entity
- `PUT /api/entities/{id}` - Update entity
- `DELETE /api/entities/{id}` - Delete entity

**Bad**:
- `GET /api/getEntities` - Verb in URL
- `POST /api/entity/create` - Redundant verb
- `GET /api/entities/list` - Redundant action

### HTTP Methods

- **GET**: Retrieve resource(s), idempotent, no side effects
- **POST**: Create new resource, not idempotent
- **PUT**: Update entire resource, idempotent
- **PATCH**: Partial update, idempotent
- **DELETE**: Remove resource, idempotent

### HTTP Status Codes

**Success Codes**:
- `200 OK` - Successful GET, PUT, PATCH, DELETE
- `201 Created` - Successful POST (resource created)
- `204 No Content` - Successful DELETE (no response body)

**Client Error Codes**:
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Missing or invalid authentication
- `403 Forbidden` - Authenticated but not authorized
- `404 Not Found` - Resource doesn't exist
- `409 Conflict` - Resource conflict (e.g., duplicate)
- `422 Unprocessable Entity` - Validation error

**Server Error Codes**:
- `500 Internal Server Error` - Unexpected server error
- `502 Bad Gateway` - Upstream service error
- `503 Service Unavailable` - Service temporarily unavailable
- `504 Gateway Timeout` - Upstream service timeout

---

## URL Structure

### Base URL
```
https://api.aletheiacodex.app/v1
```

### Versioning
- Include version in URL: `/v1/`, `/v2/`
- Maintain backward compatibility within major version
- Deprecate old versions with advance notice

### Resource Naming
- Use plural nouns: `/entities`, `/notes`, `/relationships`
- Use lowercase: `/entities` not `/Entities`
- Use hyphens for multi-word resources: `/review-queue` not `/reviewQueue`

### Query Parameters
- Use for filtering: `?type=Person&confidence_min=0.8`
- Use for pagination: `?page=2&limit=20`
- Use for sorting: `?sort=created_at&order=desc`
- Use for field selection: `?fields=id,name,type`

---

## Request Format

### Headers

**Required Headers**:
```http
Content-Type: application/json
Authorization: Bearer <firebase-token>
```

**Optional Headers**:
```http
Accept: application/json
X-Request-ID: <unique-request-id>
```

### Request Body

**JSON Format**:
```json
{
  "name": "John Doe",
  "type": "Person",
  "confidence": 0.95,
  "metadata": {
    "source": "note-123",
    "extracted_at": "2025-01-15T10:30:00Z"
  }
}
```

**Naming Convention**:
- Use snake_case for field names
- Use descriptive names
- Avoid abbreviations unless widely understood

---

## Response Format

### Success Response

**Structure**:
```json
{
  "status": "success",
  "data": {
    "id": "entity-123",
    "name": "John Doe",
    "type": "Person",
    "confidence": 0.95,
    "created_at": "2025-01-15T10:30:00Z",
    "updated_at": "2025-01-15T10:30:00Z"
  }
}
```

**List Response**:
```json
{
  "status": "success",
  "data": [
    {
      "id": "entity-123",
      "name": "John Doe",
      "type": "Person"
    },
    {
      "id": "entity-456",
      "name": "Jane Smith",
      "type": "Person"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 150,
    "total_pages": 8
  }
}
```

### Error Response

**Structure**:
```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid entity data",
    "details": [
      {
        "field": "name",
        "message": "Name is required"
      },
      {
        "field": "confidence",
        "message": "Confidence must be between 0 and 1"
      }
    ]
  }
}
```

**Error Codes**:
- Use UPPER_SNAKE_CASE
- Be specific and descriptive
- Document all error codes

---

## Authentication

### Firebase Auth Token

**Header**:
```http
Authorization: Bearer <firebase-id-token>
```

**Token Validation**:
- Verify token signature
- Check token expiration
- Extract user ID from token
- Validate user permissions

**Error Responses**:
```json
// Missing token
{
  "status": "error",
  "error": {
    "code": "AUTH_TOKEN_MISSING",
    "message": "Authentication token is required"
  }
}

// Invalid token
{
  "status": "error",
  "error": {
    "code": "AUTH_TOKEN_INVALID",
    "message": "Invalid authentication token"
  }
}

// Expired token
{
  "status": "error",
  "error": {
    "code": "AUTH_TOKEN_EXPIRED",
    "message": "Authentication token has expired"
  }
}
```

---

## Pagination

### Request Parameters
```
GET /api/entities?page=2&limit=20
```

**Parameters**:
- `page`: Page number (1-indexed)
- `limit`: Items per page (default: 20, max: 100)

### Response Format
```json
{
  "status": "success",
  "data": [...],
  "pagination": {
    "page": 2,
    "limit": 20,
    "total": 150,
    "total_pages": 8,
    "has_next": true,
    "has_prev": true
  }
}
```

---

## Filtering

### Query Parameters
```
GET /api/entities?type=Person&confidence_min=0.8&status=approved
```

**Operators**:
- `field=value` - Exact match
- `field_min=value` - Greater than or equal
- `field_max=value` - Less than or equal
- `field_like=value` - Partial match (case-insensitive)
- `field_in=value1,value2` - In list

### Example
```
GET /api/entities?type=Person&confidence_min=0.8&created_at_min=2025-01-01
```

---

## Sorting

### Query Parameters
```
GET /api/entities?sort=created_at&order=desc
```

**Parameters**:
- `sort`: Field to sort by
- `order`: `asc` or `desc` (default: `asc`)

### Multiple Fields
```
GET /api/entities?sort=type,confidence&order=asc,desc
```

---

## Field Selection

### Query Parameters
```
GET /api/entities?fields=id,name,type
```

**Response**:
```json
{
  "status": "success",
  "data": [
    {
      "id": "entity-123",
      "name": "John Doe",
      "type": "Person"
    }
  ]
}
```

---

## Rate Limiting

### Headers
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1642262400
```

### Error Response
```json
{
  "status": "error",
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Try again in 60 seconds.",
    "retry_after": 60
  }
}
```

---

## API Endpoints

### Entities

#### List Entities
```
GET /api/v1/entities
```

**Query Parameters**:
- `type`: Filter by entity type
- `confidence_min`: Minimum confidence score
- `status`: Filter by status (pending, approved, rejected)
- `page`: Page number
- `limit`: Items per page

**Response** (200 OK):
```json
{
  "status": "success",
  "data": [
    {
      "id": "entity-123",
      "name": "John Doe",
      "type": "Person",
      "confidence": 0.95,
      "status": "approved",
      "created_at": "2025-01-15T10:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 150
  }
}
```

---

#### Get Entity
```
GET /api/v1/entities/{id}
```

**Response** (200 OK):
```json
{
  "status": "success",
  "data": {
    "id": "entity-123",
    "name": "John Doe",
    "type": "Person",
    "confidence": 0.95,
    "status": "approved",
    "properties": {
      "occupation": "Engineer"
    },
    "relationships": [
      {
        "id": "rel-456",
        "type": "WORKS_AT",
        "target_entity_id": "entity-789"
      }
    ],
    "created_at": "2025-01-15T10:30:00Z",
    "updated_at": "2025-01-15T10:30:00Z"
  }
}
```

**Error** (404 Not Found):
```json
{
  "status": "error",
  "error": {
    "code": "ENTITY_NOT_FOUND",
    "message": "Entity not found: entity-123"
  }
}
```

---

#### Create Entity
```
POST /api/v1/entities
```

**Request Body**:
```json
{
  "name": "John Doe",
  "type": "Person",
  "confidence": 0.95,
  "properties": {
    "occupation": "Engineer"
  }
}
```

**Response** (201 Created):
```json
{
  "status": "success",
  "data": {
    "id": "entity-123",
    "name": "John Doe",
    "type": "Person",
    "confidence": 0.95,
    "status": "pending",
    "created_at": "2025-01-15T10:30:00Z"
  }
}
```

**Error** (400 Bad Request):
```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid entity data",
    "details": [
      {
        "field": "name",
        "message": "Name is required"
      }
    ]
  }
}
```

---

#### Update Entity
```
PUT /api/v1/entities/{id}
```

**Request Body**:
```json
{
  "name": "John Doe",
  "type": "Person",
  "confidence": 0.98,
  "properties": {
    "occupation": "Senior Engineer"
  }
}
```

**Response** (200 OK):
```json
{
  "status": "success",
  "data": {
    "id": "entity-123",
    "name": "John Doe",
    "type": "Person",
    "confidence": 0.98,
    "updated_at": "2025-01-15T11:00:00Z"
  }
}
```

---

#### Delete Entity
```
DELETE /api/v1/entities/{id}
```

**Response** (204 No Content)

**Error** (404 Not Found):
```json
{
  "status": "error",
  "error": {
    "code": "ENTITY_NOT_FOUND",
    "message": "Entity not found: entity-123"
  }
}
```

---

### Notes

#### Create Note
```
POST /api/v1/notes
```

**Request Body**:
```json
{
  "content": "John works at Google and lives in San Francisco.",
  "metadata": {
    "source": "manual_entry"
  }
}
```

**Response** (201 Created):
```json
{
  "status": "success",
  "data": {
    "id": "note-123",
    "content": "John works at Google and lives in San Francisco.",
    "status": "processing",
    "created_at": "2025-01-15T10:30:00Z"
  }
}
```

---

### Review Queue

#### Get Pending Items
```
GET /api/v1/review/pending
```

**Response** (200 OK):
```json
{
  "status": "success",
  "data": [
    {
      "id": "review-123",
      "type": "entity",
      "entity": {
        "id": "entity-456",
        "name": "John Doe",
        "type": "Person",
        "confidence": 0.85
      },
      "created_at": "2025-01-15T10:30:00Z"
    }
  ]
}
```

---

#### Approve Item
```
POST /api/v1/review/{id}/approve
```

**Response** (200 OK):
```json
{
  "status": "success",
  "data": {
    "id": "review-123",
    "status": "approved",
    "approved_at": "2025-01-15T11:00:00Z"
  }
}
```

---

#### Reject Item
```
POST /api/v1/review/{id}/reject
```

**Request Body** (optional):
```json
{
  "reason": "Incorrect entity type"
}
```

**Response** (200 OK):
```json
{
  "status": "success",
  "data": {
    "id": "review-123",
    "status": "rejected",
    "rejected_at": "2025-01-15T11:00:00Z"
  }
}
```

---

## Error Codes Reference

### Authentication Errors
- `AUTH_TOKEN_MISSING` - No authentication token provided
- `AUTH_TOKEN_INVALID` - Invalid token format or signature
- `AUTH_TOKEN_EXPIRED` - Token has expired
- `AUTH_INSUFFICIENT_PERMISSIONS` - User lacks required permissions

### Validation Errors
- `VALIDATION_ERROR` - Request data validation failed
- `INVALID_PARAMETER` - Invalid query parameter
- `MISSING_REQUIRED_FIELD` - Required field is missing

### Resource Errors
- `ENTITY_NOT_FOUND` - Entity does not exist
- `NOTE_NOT_FOUND` - Note does not exist
- `REVIEW_ITEM_NOT_FOUND` - Review item does not exist
- `RESOURCE_CONFLICT` - Resource already exists

### Processing Errors
- `PROCESSING_ERROR` - Error during processing
- `AI_SERVICE_ERROR` - AI service unavailable or error
- `DATABASE_ERROR` - Database operation failed

### Rate Limiting
- `RATE_LIMIT_EXCEEDED` - Too many requests

---

## API Documentation

### OpenAPI/Swagger

Maintain OpenAPI 3.0 specification at:
```
/api/v1/openapi.json
```

### Documentation Site

Host API documentation at:
```
https://docs.aletheiacodex.app/api
```

---

## Version History

**v1.0.0** - Initial API standards
- Defined RESTful design principles
- Established URL structure and naming conventions
- Defined request/response formats
- Documented authentication and authorization
- Defined pagination, filtering, and sorting
- Created error code reference
- Documented all API endpoints

---

**End of API Standards**