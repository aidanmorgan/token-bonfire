# Task Dependencies

[<-- Back to Concurrency Index](index.md)

Task dependencies use native Agent Teams primitives to manage blocking and unblocking. No custom queue management, timeouts, or retry tracking is needed.

## Native Dependency Management

### Setting Dependencies

Dependencies are set via `TaskUpdate({ addBlockedBy })` during task creation:

```
TaskUpdate({ taskId: "task-7", addBlockedBy: ["task-3"] })
```

This tells the system that `task-7` cannot start until `task-3` is completed.

### Automatic Unblocking

When a blocking task is marked `completed` via `TaskUpdate({ status: "completed" })`, all tasks that were `blockedBy` it automatically become available. No manual unblocking, notification, or queue processing is needed.

### Dependency Source

The bootstrapper script (`generate-orchestrator.py`) parses `Blocked By` fields from the plan file and includes them in the task manifest. The team lead uses these during `TaskCreate` to set up the initial dependency graph.

## How Experts See Dependencies

When an expert calls `TaskList`, tasks with unresolved dependencies appear with their blocked status. Experts:

1. **Skip blocked tasks** when claiming work
2. **Prefer their applicable tasks** that are pending and unblocked
3. **Claim via** `TaskUpdate({ status: "in_progress" })` which uses file locking to prevent race conditions

If all of an expert's applicable tasks are blocked, they may claim other unblocked tasks where their expertise is relevant, or check their mailbox for review feedback on previously submitted work.

## File Conflict as Implicit Dependency

When an expert signals `FILE_CONFLICT` and the team lead determines the expert should wait:

1. The team lead can add a dependency: `TaskUpdate({ taskId: "<waiting-task>", addBlockedBy: ["<owning-task>"] })`
2. The waiting task is automatically unblocked when the owning task completes
3. No custom timeout or retry logic is needed

## Deadlock Prevention

Circular dependencies are prevented at plan parse time by the bootstrapper script:

- The script validates the dependency graph during parsing
- Cycles are detected and reported as errors before any tasks are created
- The team lead verifies the dependency graph during gap analysis

If a dependency deadlock is discovered at runtime (all remaining tasks are blocked), the team lead reports the blocking chain to the user via `AskUserQuestion`.

---

[<-- Back to Concurrency Index](index.md)
