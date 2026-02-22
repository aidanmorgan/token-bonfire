# Race Safety

[<-- Back to Concurrency Index](index.md)

How named teammates and native Agent Teams primitives prevent race conditions in parallel work.

## Why Races Are Largely Eliminated

Named teammates and native Agent Teams primitives eliminate most race conditions through:

1. **Named teammates**: Each developer is a persistent, named agent. No two agents race for the same identity.
2. **Push-based assignment**: The team lead assigns tasks sequentially via `TaskUpdate({ status: "in_progress", owner })`, eliminating race conditions.
3. **Single team lead**: All routing decisions go through the team lead (the main session). No parallel team leads competing for state.
4. **Native dependency management**: `addBlockedBy` and automatic unblocking are handled atomically by the framework.

## Task Assignment Safety

The team lead assigns tasks to developers via push-based assignment. Since the team lead is a single session, it processes assignment requests sequentially:

```
Developer A: SendMessage(REQUESTING_WORK) --> team lead assigns task-3 to A
Developer B: SendMessage(REQUESTING_WORK) --> team lead assigns task-4 to B (task-3 already assigned)
```

The team lead calls `TaskUpdate({ status: "in_progress", owner: "<dev-name>" })` before sending the assignment. Since the team lead processes requests sequentially, no race condition is possible.

## Concurrent Completion Safety

When two developers complete tasks that unblock the same dependent task:

1. Developer A completes `task-1`, team lead calls `TaskUpdate({ status: "completed" })`
2. Developer B completes `task-2`, team lead calls `TaskUpdate({ status: "completed" })`
3. If `task-3` was `blockedBy: ["task-1", "task-2"]`, it auto-unblocks only after BOTH are completed
4. The native dependency system handles this atomically — no double-dispatch risk

## Review Pipeline Safety

The team lead routes signals sequentially (it is a single session processing its mailbox):

1. Developer sends `READY_FOR_REVIEW: task-1`
2. Team lead reads mailbox, sends review request to `critic`
3. Critic sends `REVIEW_PASSED: task-1`
4. Team lead reads mailbox, sends ripple request to `ripple`
5. Ripple sends `RIPPLE_PASSED: task-1`
6. Team lead reads mailbox, sends audit request to `auditor`
7. Auditor sends `AUDIT_PASSED: task-1`
8. Team lead reads mailbox, calls `TaskUpdate({ status: "completed" })`

Because the team lead processes messages sequentially, there is no risk of a task being simultaneously in critic review and audit, or being completed twice.

## Shared File Safety

For files that multiple developers might touch (e.g., `__init__.py`, config files):

1. **Additive-only rule**: Developers append imports/exports, never restructure shared files
2. **Read-before-write**: Developers read the current state of shared files before modifying
3. **Team lead coordination**: If restructuring is needed, the team lead assigns a single owner via mailbox

---

## Best Practices for Plan Authors

To minimize file conflicts, plan authors should:

1. **Isolate task scope**: Each task should have clear file boundaries
2. **Sequence shared file access**: Use `blocked_by` to serialize tasks touching the same files
3. **Split large files early**: If multiple tasks need the same file, consider splitting it first
4. **Document file ownership**: In work descriptions, be explicit about which files the task should modify

Example of good task sequencing:

```markdown
#### Task 2-1-1: Create User Model

**Work**: Create `src/models/user.py`
**Blocked By**: none

---

#### Task 2-1-2: Create User Repository

**Work**: Create `src/repositories/user_repository.py`
**Blocked By**: 2-1-1

---

#### Task 2-1-3: Add User Validation

**Work**: Add validation methods to `src/models/user.py`
**Blocked By**: 2-1-1 # <-- Serializes access to user.py
```

---

[<-- Back to Concurrency Index](index.md)
