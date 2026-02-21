# Concurrent File Modification

With multiple named developers working in parallel, file conflicts are possible. This document provides an overview of how
the team lead and native Agent Teams primitives prevent and handle concurrent modifications.

## Overview

The concurrency system relies on three mechanisms:

- **File Ownership**: Tasks specify which files each developer owns; developers only modify files within their scope
- **Task Dependencies**: Native `TaskUpdate({ addBlockedBy })` serializes access to shared files
- **Conflict Handling**: Developers signal `FILE_CONFLICT` to the team lead, who coordinates resolution via mailbox
- **Named Teammate Ownership**: Each task is claimed by a specific named developer — no anonymous agents racing for work

## Navigation

- [File Ownership](file-ownership.md) - File ownership protocol and task decomposition
- [Task Dependencies](queue-management.md) - Native task dependency management
- [Conflict Handling](conflict-handling.md) - Runtime conflict handling via mailbox
- [Race Safety](race-safety.md) - Race condition prevention with named teammates

## Quick Reference

### File Ownership States

1. **Owned** - File is actively being modified by a named developer as part of their claimed task
2. **Released** - Developer's task completed, file available for other tasks
3. **Shared** - File is a common resource (e.g., `__init__.py`, config) — additive-only changes allowed

### Conflict Resolution Options

- **WAIT** - Developer waits for the owning task to complete (dependency auto-unblocks)
- **COORDINATE** - Team lead assigns single owner via mailbox, other developer yields
- **ADDITIVE** - Both developers make additive-only changes to shared files (append imports, never restructure)

### Task Dependencies

Dependencies are managed via native `TaskUpdate({ addBlockedBy })`:
- Blocking tasks automatically unblock dependents when marked `completed`
- No manual queue management or timeout handling needed
- The bootstrapper script sets up initial dependencies from the plan file's `Blocked By` fields

## State Tracking

Task state is tracked in the **shared task list** via `TaskCreate`/`TaskUpdate`/`TaskList`/`TaskGet`. File ownership is encoded in task descriptions (file ownership boundaries).

No custom state file is needed — the native task list provides all coordination state.
