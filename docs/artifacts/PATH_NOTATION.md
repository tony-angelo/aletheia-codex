# Path Notation Standard

## Purpose
This document defines the standard notation for file paths across all SuperNinja documentation to eliminate ambiguity about file locations.

## Notation System

### [workspace]
**Meaning:** Files in the AI node's personal workspace
**Full Path:** `/workspace/...`
**Access:** Only the current AI node can access these files
**Persistence:** Files are temporary and exist only during the node's session
**Example:** `[workspace]/drafts/analysis.txt` = `/workspace/drafts/analysis.txt`

### [artifacts]
**Meaning:** Files in the artifacts branch of the repository
**Full Path:** Repository artifacts branch at `/docs/artifacts/...`
**Access:** All nodes can access these files (shared interface)
**Persistence:** Files persist across sessions and are version controlled
**Example:** `[artifacts]/templates/node.txt` = `/docs/artifacts/templates/node.txt` (on artifacts branch)

### [main]
**Meaning:** Files in the main branch of the repository (production code)
**Full Path:** Repository main branch
**Access:** All nodes can read; only Admin nodes write during sprints
**Persistence:** Files persist and are version controlled
**Example:** `[main]/src/app.py` = `/src/app.py` (on main branch)

## Usage Rules

### 1. Always Use Notation
Every file path in documentation MUST use one of the three notations.

**Correct:**
- `[workspace]/todo.md`
- `[artifacts]/architect/architect.txt`
- `[main]/README.md`

**Incorrect:**
- `/workspace/todo.md` (ambiguous - could be artifacts path)
- `docs/artifacts/architect/architect.txt` (which branch?)
- `README.md` (where is this?)

### 2. Workspace Paths
When referencing files in your personal workspace:
- Use `[workspace]/path/to/file`
- These files are NOT shared with other nodes
- These files do NOT persist after your session ends

### 3. Artifacts Branch Paths
When referencing files in the artifacts branch:
- Use `[artifacts]/path/to/file`
- These files ARE shared with other nodes
- These files DO persist across sessions
- This is the primary interface between nodes

### 4. Main Branch Paths
When referencing files in the main code repository:
- Use `[main]/path/to/file`
- These are production code files
- Admin nodes modify these during sprints
- Other nodes read these for context

## Common Locations

### Node Prime Directives
- `[artifacts]/node-master/node-master.txt`
- `[artifacts]/architect/architect.txt`
- `[artifacts]/admin-[domain]/admin-[domain].txt`
- `[artifacts]/docmaster-sprint/docmaster-sprint.txt`
- `[artifacts]/docmaster-code/docmaster-code.txt`

### Templates
- `[artifacts]/templates/deliverable-header.md`
- `[artifacts]/templates/node.txt`
- `[artifacts]/templates/sprint-guide.md`
- etc.

### Node Directories
- `[artifacts]/[node-name]/` - Node's home directory
- `[artifacts]/[node-name]/inbox/` - Incoming deliverables
- `[artifacts]/[node-name]/outbox/` - Outgoing deliverables
- `[artifacts]/[node-name]/templates/` - Node-specific templates

### Workspace (Node-Specific)
- `[workspace]/` - Your personal workspace root
- `[workspace]/drafts/` - Work in progress
- `[workspace]/analysis/` - Analysis documents
- `[workspace]/temp/` - Temporary files

## Examples

### Example 1: Architect Referencing Template
**Correct:** "Use the template at `[artifacts]/templates/node.txt`"
**Meaning:** The template is in the artifacts branch, shared across all nodes

### Example 2: Admin Working on Code
**Correct:** "Modify the file at `[main]/src/app.py`"
**Meaning:** The file is in the main branch (production code)

### Example 3: Node Creating Draft
**Correct:** "Save your draft to `[workspace]/drafts/analysis.txt`"
**Meaning:** The file is in your personal workspace, not shared

### Example 4: Node Delivering Work
**Correct:** "Commit your deliverable to `[artifacts]/admin-backend/outbox/session-log.md`"
**Meaning:** The file goes to artifacts branch where other nodes can access it

## Migration Guide

When updating existing documents:
1. Find all file paths
2. Determine the intended location (workspace, artifacts, or main)
3. Add the appropriate notation prefix
4. Verify the path makes sense in context

## Quick Reference

| Notation | Location | Shared? | Persistent? | Use For |
|----------|----------|---------|-------------|---------|
| `[workspace]` | AI's workspace | No | No | Drafts, temp files, personal work |
| `[artifacts]` | Artifacts branch | Yes | Yes | Node interface, templates, deliverables |
| `[main]` | Main branch | Yes | Yes | Production code |

---

**This notation MUST be used in all SuperNinja documentation.**