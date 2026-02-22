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

The bootstrapper script (`generate-orchestrator.py`) parses `Blocked By` fields from the plan file and includes them in the task manifest. The team lead creates tasks via `TaskCreate`, then sets up the initial dependency graph via `TaskUpdate({ addBlockedBy })` — dependencies cannot be set at creation time.

## How the Team Lead Uses Dependencies

The team lead calls `TaskList` to check task status. Tasks with unresolved dependencies remain blocked. The team lead:

1. **Skips blocked tasks** when assigning work to developers
2. **Assigns unblocked tasks** to requesting developers via SendMessage
3. **Claims on behalf of developers** via `TaskUpdate({ status: "in_progress", owner: "<dev-name>" })`

If all remaining tasks are blocked, the team lead responds with `NO_TASKS_AVAILABLE` when developers request work.

## File Conflict as Implicit Dependency

When a developer signals `FILE_CONFLICT` and the team lead determines the developer should wait:

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
