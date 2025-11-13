# Git Standards - AletheiaCodex Project

**Document Type**: Standards Definition  
**Created**: January 2025  
**Author**: Architect Node  
**Status**: Active  

---

## Overview

This document defines the Git standards for the AletheiaCodex project. All contributors must follow these standards to maintain a clean, organized, and traceable git history.

---

## Branch Naming Conventions

### Sprint Branches
**Format**: `sprint-[N]`

**Examples**:
- `sprint-1`
- `sprint-2`
- `sprint-10`

**Purpose**: Main development branch for each sprint

**Lifecycle**:
- Created at sprint start by Architect
- All sprint work happens on this branch
- Merged to main at sprint completion
- Deleted after successful merge

---

### Feature Branches (Optional)
**Format**: `sprint-[N]-[domain]-[feature-name]`

**Examples**:
- `sprint-1-backend-api-endpoints`
- `sprint-2-frontend-review-queue`
- `sprint-3-infrastructure-monitoring`

**Purpose**: Optional branches for isolating specific features

**Lifecycle**:
- Created from sprint branch
- Merged back to sprint branch when complete
- Deleted after merge

---

### Hotfix Branches
**Format**: `hotfix-[issue-description]`

**Examples**:
- `hotfix-api-timeout`
- `hotfix-auth-bug`

**Purpose**: Emergency fixes for production issues

**Lifecycle**:
- Created from main
- Merged to main and current sprint branch
- Deleted after merge

---

## Commit Message Standards

### Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type
Must be one of the following:

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, missing semicolons, etc.)
- **refactor**: Code refactoring (no functional changes)
- **perf**: Performance improvements
- **test**: Adding or updating tests
- **chore**: Maintenance tasks (dependencies, build, etc.)
- **ci**: CI/CD changes
- **revert**: Reverting a previous commit

### Scope
The scope should indicate the area of the codebase affected:

**Backend Scopes**:
- `ingestion` - Ingestion function
- `orchestration` - Orchestration function
- `graph` - Graph API function
- `notes` - Notes API function
- `review` - Review API function
- `ai` - AI services
- `db` - Database clients
- `models` - Data models
- `auth` - Authentication

**Frontend Scopes**:
- `components` - React components
- `pages` - Page components
- `services` - API services
- `hooks` - Custom hooks
- `utils` - Utility functions
- `styles` - Styling

**Infrastructure Scopes**:
- `deployment` - Deployment scripts
- `config` - Configuration files
- `firebase` - Firebase configuration
- `gcp` - GCP resources

**General Scopes**:
- `docs` - Documentation
- `tests` - Tests
- `deps` - Dependencies

### Subject
- Use imperative mood ("add" not "added" or "adds")
- Don't capitalize first letter
- No period at the end
- Maximum 50 characters
- Be specific and descriptive

### Body (Optional)
- Wrap at 72 characters
- Explain what and why, not how
- Separate from subject with blank line
- Use bullet points for multiple items

### Footer (Optional)
- Reference issues: `Closes #123` or `Fixes #456`
- Note breaking changes: `BREAKING CHANGE: description`

---

## Commit Message Examples

### Good Examples

#### Feature Addition
```
feat(graph): add entity relationship query endpoint

- Implement GET /graph/relationships endpoint
- Add filtering by entity type
- Include pagination support
- Add unit tests for new endpoint

Closes #45
```

#### Bug Fix
```
fix(auth): resolve token expiration handling

The auth middleware was not properly handling expired tokens,
causing 500 errors instead of 401. Updated to check expiration
before validation and return appropriate error response.

Fixes #78
```

#### Documentation
```
docs(api): update API documentation for review endpoints

- Add request/response examples
- Document error codes
- Update authentication requirements
```

#### Refactoring
```
refactor(components): extract common button styles

Extracted button styles into reusable component to reduce
duplication across the codebase. No functional changes.
```

#### Performance
```
perf(db): optimize Neo4j query for entity retrieval

Reduced query time from 500ms to 50ms by adding index on
entity type and using more efficient Cypher query pattern.
```

---

### Bad Examples (Don't Do This)

❌ `update code` - Too vague, no type or scope

❌ `Fixed bug` - No scope, not descriptive

❌ `feat: Added new feature for users to see their profile` - Too long, not imperative

❌ `WIP` - Not descriptive, should not be committed

❌ `asdf` - Meaningless

---

## Commit Frequency

### When to Commit

**Commit Often**:
- After completing a logical unit of work
- After fixing a bug
- After adding a test
- Before switching tasks
- At the end of each work session

**Don't Commit**:
- Broken code (unless explicitly marked as WIP and on feature branch)
- Code that doesn't compile
- Code that fails tests
- Sensitive information (API keys, passwords, etc.)

### Commit Size

**Ideal Commit**:
- Single logical change
- Can be understood in isolation
- Can be reverted without breaking other features
- Includes related tests and documentation

**Too Small**:
- Fixing a typo in a commit message (use `git commit --amend`)
- Adding a single line of code

**Too Large**:
- Multiple unrelated changes
- Entire feature implementation in one commit
- Refactoring + new feature + bug fix

---

## Branch Management

### Working on Sprint Branch

1. **Start of Sprint**:
   ```bash
   git checkout main
   git pull origin main
   git checkout sprint-N
   ```

2. **During Sprint**:
   ```bash
   # Make changes
   git add .
   git commit -m "feat(scope): description"
   git push origin sprint-N
   ```

3. **Pulling Updates**:
   ```bash
   git pull origin sprint-N
   ```

---

### Working on Feature Branch (Optional)

1. **Create Feature Branch**:
   ```bash
   git checkout sprint-N
   git checkout -b sprint-N-domain-feature-name
   ```

2. **During Development**:
   ```bash
   # Make changes
   git add .
   git commit -m "feat(scope): description"
   git push origin sprint-N-domain-feature-name
   ```

3. **Merge to Sprint Branch**:
   ```bash
   git checkout sprint-N
   git merge sprint-N-domain-feature-name
   git push origin sprint-N
   git branch -d sprint-N-domain-feature-name
   ```

---

## Merge Strategy

### Sprint Branch to Main

**Strategy**: Squash and Merge (preferred) or Merge Commit

**Process**:
1. Ensure all tests pass on sprint branch
2. Ensure all documentation is updated
3. Create merge commit with summary of sprint work
4. Delete sprint branch after successful merge

**Merge Commit Message**:
```
Merge sprint-N: [Sprint Name]

Sprint Summary:
- Feature 1: description
- Feature 2: description
- Feature 3: description

Closes #issue1, #issue2
```

---

### Feature Branch to Sprint Branch

**Strategy**: Merge Commit (preferred) or Squash and Merge

**Process**:
1. Ensure feature is complete
2. Ensure tests pass
3. Merge to sprint branch
4. Delete feature branch

---

## Git Workflow Best Practices

### Before Committing

1. **Review Changes**:
   ```bash
   git status
   git diff
   ```

2. **Stage Changes Selectively**:
   ```bash
   git add -p  # Interactive staging
   ```

3. **Write Good Commit Message**:
   - Follow commit message standards
   - Be descriptive and specific

---

### During Development

1. **Commit Frequently**: Small, logical commits are better than large ones

2. **Pull Regularly**: Stay up to date with sprint branch
   ```bash
   git pull origin sprint-N
   ```

3. **Push Regularly**: Share your work with the team
   ```bash
   git push origin sprint-N
   ```

---

### Handling Conflicts

1. **Pull Latest Changes**:
   ```bash
   git pull origin sprint-N
   ```

2. **Resolve Conflicts**:
   - Open conflicted files
   - Resolve conflicts manually
   - Test that code still works

3. **Complete Merge**:
   ```bash
   git add .
   git commit -m "merge: resolve conflicts from sprint-N"
   git push origin sprint-N
   ```

---

## What NOT to Commit

### Never Commit

❌ **Secrets and Credentials**:
- API keys
- Passwords
- Private keys
- Access tokens
- Database credentials

❌ **Environment-Specific Files**:
- `.env` files with real values
- Local configuration files
- IDE-specific files (unless in .gitignore)

❌ **Build Artifacts**:
- `node_modules/`
- `dist/` or `build/`
- Compiled binaries
- Log files

❌ **Large Binary Files**:
- Large datasets
- Video files
- Large images (unless necessary for UI)

❌ **Temporary Files**:
- `.DS_Store`
- `*.swp`, `*.swo`
- `*.tmp`

---

## .gitignore

Ensure your `.gitignore` includes:

```gitignore
# Dependencies
node_modules/
__pycache__/
*.pyc
.venv/
venv/

# Build outputs
dist/
build/
*.egg-info/

# Environment files
.env
.env.local
.env.*.local

# IDE files
.vscode/
.idea/
*.swp
*.swo

# OS files
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Test coverage
coverage/
.coverage
htmlcov/

# Temporary files
*.tmp
.cache/
```

---

## Git Hooks (Optional)

### Pre-commit Hook
Automatically run checks before committing:

```bash
#!/bin/sh
# .git/hooks/pre-commit

# Run linter
npm run lint
if [ $? -ne 0 ]; then
    echo "Linting failed. Please fix errors before committing."
    exit 1
fi

# Run tests
npm test
if [ $? -ne 0 ]; then
    echo "Tests failed. Please fix tests before committing."
    exit 1
fi
```

---

## Troubleshooting

### Undo Last Commit (Not Pushed)
```bash
git reset --soft HEAD~1  # Keep changes
git reset --hard HEAD~1  # Discard changes
```

### Amend Last Commit
```bash
git commit --amend -m "new message"
```

### Discard Local Changes
```bash
git checkout -- <file>  # Single file
git reset --hard        # All files
```

### View Commit History
```bash
git log --oneline --graph --all
```

---

## Version History

**v1.0.0** - Initial git standards
- Defined branch naming conventions
- Established commit message standards
- Documented merge strategy
- Defined best practices

---

**End of Git Standards**