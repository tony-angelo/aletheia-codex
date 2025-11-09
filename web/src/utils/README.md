# Function Library Documentation

## Overview

This directory contains utility functions and helper modules used throughout the Aletheia Codex application.

## Current Structure

Currently, utility functions are distributed across the codebase. This document serves as a reference for organizing and documenting utility functions as they are created.

## Recommended Structure

```
web/src/utils/
├── api/              # API client utilities
├── formatting/       # Data formatting functions
├── validation/       # Input validation functions
└── README.md        # This file
```

## API Utilities

### Purpose
Functions for making API calls and handling responses.

### Common Patterns

**Error Handling:**
```typescript
try {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`API call failed: ${response.statusText}`);
  }
  return await response.json();
} catch (error) {
  console.error('API error:', error);
  throw error;
}
```

**Type Safety:**
```typescript
interface ApiResponse<T> {
  data: T;
  error?: string;
}

async function fetchData<T>(url: string): Promise<ApiResponse<T>> {
  // Implementation
}
```

## Formatting Utilities

### Date Formatting

**formatRelativeTime**
```typescript
/**
 * Format date to relative time (e.g., "2 hours ago")
 * @param date - Date to format
 * @returns Formatted relative time string
 */
export function formatRelativeTime(date: Date): string {
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffSecs = Math.floor(diffMs / 1000);
  const diffMins = Math.floor(diffSecs / 60);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffSecs < 60) return 'just now';
  if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
  if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
  if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
  
  return date.toLocaleDateString();
}
```

**formatShortDate**
```typescript
/**
 * Format date to short format (e.g., "Jan 15, 2025")
 * @param date - Date to format
 * @returns Formatted date string
 */
export function formatShortDate(date: Date): string {
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  });
}
```

### Text Formatting

**truncateText**
```typescript
/**
 * Truncate text to specified length with ellipsis
 * @param text - Text to truncate
 * @param maxLength - Maximum length
 * @returns Truncated text
 */
export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength - 3) + '...';
}
```

**capitalizeWords**
```typescript
/**
 * Capitalize first letter of each word
 * @param text - Text to capitalize
 * @returns Capitalized text
 */
export function capitalizeWords(text: string): string {
  return text.replace(/\b\w/g, char => char.toUpperCase());
}
```

## Validation Utilities

### Email Validation

```typescript
/**
 * Validate email address format
 * @param email - Email to validate
 * @returns True if valid email format
 */
export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}
```

### Password Validation

```typescript
interface ValidationResult {
  valid: boolean;
  message: string;
}

/**
 * Validate password strength
 * @param password - Password to validate
 * @returns Validation result with message
 */
export function validatePassword(password: string): ValidationResult {
  if (password.length < 8) {
    return { valid: false, message: 'Password must be at least 8 characters' };
  }
  if (!/[A-Z]/.test(password)) {
    return { valid: false, message: 'Password must contain an uppercase letter' };
  }
  if (!/[a-z]/.test(password)) {
    return { valid: false, message: 'Password must contain a lowercase letter' };
  }
  if (!/[0-9]/.test(password)) {
    return { valid: false, message: 'Password must contain a number' };
  }
  return { valid: true, message: 'Password is strong' };
}
```

## Best Practices

### 1. Type Safety
Always use TypeScript types for parameters and return values:

```typescript
function processData(input: string): ProcessedData {
  // Implementation
}
```

### 2. Error Handling
Handle errors consistently:

```typescript
try {
  const result = await operation();
  return result;
} catch (error) {
  console.error('Operation failed:', error);
  throw new Error(error instanceof Error ? error.message : 'Unknown error');
}
```

### 3. Documentation
Use JSDoc comments for all functions:

```typescript
/**
 * Brief description of what the function does
 * @param paramName - Description of parameter
 * @returns Description of return value
 * @throws Description of errors that might be thrown
 */
export function myFunction(paramName: string): ReturnType {
  // Implementation
}
```

### 4. Pure Functions
Prefer pure functions when possible:

```typescript
// Good: Pure function
function add(a: number, b: number): number {
  return a + b;
}

// Avoid: Function with side effects
let total = 0;
function addToTotal(value: number): void {
  total += value; // Side effect
}
```

### 5. Single Responsibility
Each function should do one thing well:

```typescript
// Good: Single responsibility
function validateEmail(email: string): boolean { /* ... */ }
function sendEmail(to: string, subject: string, body: string): Promise<void> { /* ... */ }

// Avoid: Multiple responsibilities
function validateAndSendEmail(email: string, subject: string, body: string): Promise<void> {
  // Validation and sending in one function
}
```

## Common Patterns

### Async/Await
Use async/await for asynchronous operations:

```typescript
export async function fetchData(): Promise<DataType> {
  const response = await fetch(url);
  const data = await response.json();
  return data;
}
```

### Optional Parameters
Use optional parameters with default values:

```typescript
export function formatText(
  text: string,
  options: {
    maxLength?: number;
    uppercase?: boolean;
  } = {}
): string {
  const { maxLength = 100, uppercase = false } = options;
  // Implementation
}
```

### Type Guards
Use type guards for runtime type checking:

```typescript
function isString(value: unknown): value is string {
  return typeof value === 'string';
}

function processValue(value: unknown): string {
  if (isString(value)) {
    return value.toUpperCase();
  }
  return String(value);
}
```

## Adding New Utilities

1. Create utility file in appropriate directory
2. Add JSDoc comments with parameter and return type documentation
3. Export function from index file (if applicable)
4. Add to this documentation with examples
5. Write tests for the utility

## Testing Utilities

Example test structure:

```typescript
import { myUtility } from './myUtility';

describe('myUtility', () => {
  it('handles normal input', () => {
    expect(myUtility('input')).toBe('expected');
  });

  it('handles edge cases', () => {
    expect(myUtility('')).toBe('');
    expect(myUtility(null)).toThrow();
  });
});
```

## Resources

- [TypeScript Documentation](https://www.typescriptlang.org/docs/)
- [MDN Web Docs](https://developer.mozilla.org/)
- [JavaScript Best Practices](https://github.com/ryanmcdermott/clean-code-javascript)