# Component Library Documentation

## Overview

This directory contains all React components for the Aletheia Codex application, organized by category for better maintainability and AI-assisted development.

## Directory Structure

### common/
Reusable UI components that can be used across the application.

**Components:**
- `ConfidenceBadge.tsx` - Displays confidence scores with color-coded badges

### layout/
Components that define the application layout and structure.

**Components:**
- `Navigation.tsx` - Main navigation menu with links to all pages

### features/
Feature-specific components organized by domain.

#### features/auth/
Authentication-related components.

**Components:**
- `SignIn.tsx` - User sign-in form with email/password and Google authentication
- `SignUp.tsx` - User registration form

#### features/notes/
Components related to note creation and management.

**Components:**
- `NoteInput.tsx` - Text input component for creating new notes
- `NoteCard.tsx` - Display component for individual notes
- `NoteHistory.tsx` - List view of user's notes with filtering
- `ProcessingStatus.tsx` - Shows note processing status and progress

#### features/review/
Components for the review queue and approval workflow.

**Components:**
- `ReviewQueue.tsx` - Main review queue interface with filtering
- `EntityCard.tsx` - Display and action component for entity review items
- `RelationshipCard.tsx` - Display and action component for relationship review items
- `BatchActions.tsx` - Bulk action controls for multiple review items
- `ExtractionResults.tsx` - Shows AI extraction results from notes

#### features/graph/
Components for knowledge graph browsing and visualization.

**Components:**
- `NodeBrowser.tsx` - Browse and search nodes in the knowledge graph
- `NodeDetails.tsx` - Detailed view of a node with properties and relationships

## Component Patterns

### Props Interface
All components define a TypeScript interface for their props:

```typescript
interface MyComponentProps {
  title: string;
  onAction: () => void;
  optional?: boolean;
}

export const MyComponent: React.FC<MyComponentProps> = ({ title, onAction, optional }) => {
  // Component implementation
};
```

### State Management
Use React hooks for local state:

```typescript
const [value, setValue] = useState<string>('');
const [loading, setLoading] = useState(false);
const [error, setError] = useState<string | null>(null);
```

### Error Handling
Always handle errors gracefully:

```typescript
try {
  await someAsyncOperation();
} catch (error) {
  console.error('Operation failed:', error);
  setError(error instanceof Error ? error.message : 'Unknown error');
}
```

### Loading States
Show loading indicators for async operations:

```typescript
if (loading) {
  return (
    <div className="flex justify-center items-center h-64">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
    </div>
  );
}
```

## Naming Conventions

- **Components**: PascalCase (e.g., `NoteInput.tsx`)
- **Props Interfaces**: PascalCase with "Props" suffix (e.g., `NoteInputProps`)
- **Functions**: camelCase (e.g., `handleSubmit`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `MAX_LENGTH`)

## Styling

All components use Tailwind CSS for styling. Follow these guidelines:

- Use utility classes for styling
- Keep responsive design in mind (use `sm:`, `md:`, `lg:` prefixes)
- Use consistent color scheme:
  - Primary: `indigo-600` (buttons, links, highlights)
  - Success: `green-600` (success states, approvals)
  - Warning: `yellow-600` (warnings, pending states)
  - Error: `red-600` (errors, rejections)
  - Neutral: `gray-*` (text, borders, backgrounds)
- Maintain consistent spacing (use `p-4`, `m-4`, `gap-4`, etc.)

## Common Patterns

### Async Data Loading

```typescript
const [data, setData] = useState<DataType[]>([]);
const [loading, setLoading] = useState(true);
const [error, setError] = useState<string | null>(null);

useEffect(() => {
  loadData();
}, []);

const loadData = async () => {
  try {
    setLoading(true);
    setError(null);
    const result = await fetchData();
    setData(result);
  } catch (err) {
    setError(err instanceof Error ? err.message : 'Failed to load data');
  } finally {
    setLoading(false);
  }
};
```

### Form Handling

```typescript
const [formData, setFormData] = useState({ field1: '', field2: '' });

const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();
  // Handle form submission
};

const handleChange = (field: string, value: string) => {
  setFormData(prev => ({ ...prev, [field]: value }));
};
```

### Modal/Dialog Pattern

```typescript
const [isOpen, setIsOpen] = useState(false);

return (
  <>
    <button onClick={() => setIsOpen(true)}>Open Modal</button>
    
    {isOpen && (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-6 max-w-md">
          {/* Modal content */}
          <button onClick={() => setIsOpen(false)}>Close</button>
        </div>
      </div>
    )}
  </>
);
```

## Adding New Components

1. Create component file in appropriate directory
2. Define TypeScript interface for props
3. Implement component with proper error handling
4. Add to this documentation
5. Write tests if applicable

## Testing

Components should be testable. Write tests for:
- User interactions (clicks, form submissions)
- State changes
- Error handling
- Edge cases

Example test structure:
```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { MyComponent } from './MyComponent';

describe('MyComponent', () => {
  it('renders correctly', () => {
    render(<MyComponent title="Test" />);
    expect(screen.getByText('Test')).toBeInTheDocument();
  });
});
```

## Resources

- [React Documentation](https://react.dev/)
- [TypeScript Documentation](https://www.typescriptlang.org/docs/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/)