# Task Tracking

[← Back to State Management](index.md)

Task selection, rollback, and parallel developer tracking using native Agent Teams primitives.

---

## Task Selection Priority

Developers self-organize by claiming tasks from the shared task list:

1. **Priority ordering** — select tasks that unblock the most downstream tasks
2. Among equals, select task with highest priority in plan
3. If all tasks are complete/blocked, developers wait for pending work

Task claiming uses native atomic task claiming — if two developers try to claim the same task simultaneously, only one succeeds. The other tries the next available task.

---

## Rollback Capability

Track commit SHAs per task to enable rollback if issues are discovered after completion.

### Commit Tracking

The team lead tracks commit information in its context, including the commit SHA, completion timestamp, list of modified files, and branch for each completed task. This information is used to determine rollback scope when issues are discovered.

### Rollback Rules

1. Cannot rollback if dependent tasks have completed
2. Task returns to `pending` status after rollback (via `TaskUpdate`)
3. In-progress dependent tasks are aborted
4. Plan re-evaluation triggered

---

## Learning from Failures

Track failure patterns to improve future development cycles.

### Failure Pattern Storage

The team lead maintains failure pattern records in its context, tracking the count and affected tasks for each failure category, along with common causes and suggested prevention steps (e.g., running type checkers before signaling completion). This information accumulates over the session and is used to provide targeted guidance to developers.

### Using Failure Patterns

Include relevant patterns when sending review feedback to developers via `TeammateTool({ operation: "write", to: "<dev-name>" })`.

---

## Parallel Developer Tracking

### Developer Tracking via Task List

Developer activity is tracked through the shared task list:
- When a developer claims a task: `TaskUpdate({ taskId, status: "in_progress" })` — native atomic claiming
- When a developer signals ready: `READY_FOR_REVIEW` mailbox message to team lead
- When a task completes: team lead calls `TaskUpdate({ taskId, status: "completed" })` after auditor approval

The team lead monitors developer activity by:
1. Checking `TaskList` for task status changes
2. Reading mailbox messages from developers
3. Heartbeat timeout (~5 min) detects crashed developers — orphaned tasks auto-release

### Developer Lifecycle

| Event | When | Action |
|---|---|---|
| Developer spawned | `Task({ team_name, name, run_in_background: true })` | Developer starts claiming tasks |
| Task claimed | Developer calls `TaskUpdate({ status: "in_progress" })` | Native atomic claiming, prevents race conditions |
| Ready for review | Developer sends `READY_FOR_REVIEW` mailbox message | Team lead routes to critic |
| Task completed | Auditor passes, team lead calls `TaskUpdate({ status: "completed" })` | Dependencies auto-unblock |
| Developer crashed | Heartbeat timeout (~5 min) | Task auto-releases; team lead respawns from persisted prompt |

### Review Pipeline (team lead manages)

**Process reviews BEFORE dispatching new work to developers.**

The team lead routes tasks through the review pipeline:

1. **Critic review**: On `READY_FOR_REVIEW` from developer, team lead sends review request to `critic` via `write`
2. **Ripple review**: On `REVIEW_PASS` from critic, team lead sends ripple analysis request to `ripple` via `write`
3. **Auditor verification**: On `RIPPLE_PASSED` from ripple, team lead sends audit request to `auditor` via `write`
4. **Completion**: On `AUDIT_PASSED` from auditor, team lead marks task `completed` via `TaskUpdate`

**Rationale**: Completing in-flight work (reviews, ripple analysis, audits) unblocks dependent tasks faster than starting new work.

---

## Related Documentation

- [State Fields](fields.md) - All state field definitions
- [Update Triggers](update-triggers.md) - When state changes occur
- [Team Architecture](../team-architecture.md) - Team structure and task lifecycle
