# File Ownership Protocol

[<-- Back to Concurrency Index](index.md)

The file ownership protocol prevents concurrent modifications by assigning clear file ownership to each task. Unlike custom file locks, ownership is encoded in task descriptions and enforced by developer behavior.

## File Ownership Assignment

### At Task Creation Time

The team lead assigns file ownership when creating tasks during the bootstrap phase:

1. **Analyze the plan**: Extract file paths from task specifications (work descriptions, required reading, acceptance criteria)
2. **Assign ownership**: Each file is owned by exactly one task
3. **Encode in task description**: File ownership boundaries are appended to each task's description via `TaskCreate`

```markdown
## File Ownership

Files you own (may modify):
- src/auth/authenticator.py
- tests/unit/test_authenticator.py

Files you may read (do NOT modify):
- src/models/user.py (owned by task-1)
- src/config.py (shared — additive only)
```

### Single-Writer Pattern

When a file must be touched by multiple tasks:
- Assign **one task** as the owner of that file
- Other tasks depend on it via `TaskUpdate({ addBlockedBy })`
- The owning task creates the foundation; dependent tasks extend it after it completes

### Interface-First Pattern

When multiple tasks share types or API contracts:
1. Create a **contract task** that defines types, interfaces, and schemas
2. All implementation tasks `blockedBy` the contract task
3. Developers implement against the defined contracts without modifying them
4. Prevents parallel developers from creating conflicting type definitions

## Developer Enforcement

Developers enforce file ownership during implementation:

1. **Only modify files listed in your task's ownership section**
2. **If you discover you need a file outside your scope**: Signal `FILE_CONFLICT` to the team lead via `write` and wait for guidance
3. **For shared files** (e.g., `__init__.py`, config, type exports): Read the current state first, make only additive changes (append imports, add exports), never restructure

## Ownership Release

### On Task Completion

When a task receives `AUDIT_PASSED` and the team lead marks it `completed` via `TaskUpdate`:
- The task's owned files are implicitly released
- Any tasks blocked by this task are automatically unblocked by the native dependency system
- No manual lock release or notification needed

### On Task Failure

If a task fails repeatedly (3+ audit failures) or its developer crashes:
- The team lead can reassign the task to another developer
- File ownership transfers with the task reassignment
- Blocked tasks remain blocked until the reassigned task completes

## Coordination Instructions

When the team lead detects potential file overlap between concurrent tasks, it sends coordination instructions via mailbox:

```
TeammateTool({ operation: "write", to: "<expert-name>", message: "FILE COORDINATION NOTICE:\n\nTask [other-task-id] is concurrently modifying related code.\nFiles: [list]\n\nTo avoid conflicts:\n1. Do NOT modify: [specific files to avoid]\n2. Focus changes on: [your designated files]\n3. If you discover you need a locked file, signal FILE_CONFLICT and wait for guidance\n4. Prefer additive changes over modifications to shared modules" })
```

---

[<-- Back to Concurrency Index](index.md)
