# Task Tracking

[← Back to Documentation Index](../index.md)

Task selection, rollback, and parallel developer tracking using native Agent Teams primitives.

---

## Task Selection Priority

The team lead assigns tasks to developers using push-based assignment. When selecting which task to assign:

1. **Priority ordering** — select tasks that unblock the most downstream tasks
2. Among equals, select task with highest priority in plan
3. If all tasks are complete/blocked, respond with `NO_TASKS_AVAILABLE`

The team lead calls `TaskList` to find pending unblocked tasks, `TaskGet` to retrieve full detail, then `TaskUpdate({ status: "in_progress", owner: "<dev-name>" })` before sending the assignment via `SendMessage`.

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

Include relevant patterns when sending review feedback to developers via `SendMessage({ type: "message", recipient: "<dev-name>", content: "...", summary: "..." })`.

---

## Parallel Developer Tracking

### Developer Tracking via Task List

Developer activity is tracked through the shared task list:
- When the team lead assigns a task: `TaskUpdate({ taskId, status: "in_progress", owner: "<dev-name>" })` then `SendMessage` with full task detail
- When a developer signals ready: `READY_FOR_REVIEW` mailbox message to team lead
- When a task completes: team lead calls `TaskUpdate({ taskId, status: "completed" })` after auditor approval

The team lead monitors developer activity by:
1. Checking `TaskList` for task status changes
2. Reading mailbox messages from developers
3. Heartbeat timeout (~5 min) detects crashed developers — orphaned tasks auto-release

### Developer Lifecycle

| Event | When | Action |
|---|---|---|
| Developer spawned | `Task({ team_name, name, run_in_background: true })` | Developer sends `REQUESTING_WORK` to team lead |
| Task assigned | Team lead calls `TaskUpdate({ status: "in_progress", owner })` then `SendMessage` | Push-based assignment by team lead |
| Ready for review | Developer sends `READY_FOR_REVIEW` mailbox message | Team lead routes to critic |
| Task completed | Auditor passes, team lead calls `TaskUpdate({ status: "completed" })` | Dependencies auto-unblock |
| Developer crashed | Heartbeat timeout (~5 min) | Task auto-releases; team lead respawns from persisted prompt |

### Review Pipeline (team lead manages)

**Process reviews BEFORE dispatching new work to developers.**

The team lead routes tasks through the review pipeline:

1. **Critic review**: On `READY_FOR_REVIEW` from developer, team lead sends review request to `critic` via `SendMessage`
2. **Ripple review**: On `REVIEW_PASSED` from critic, team lead sends ripple analysis request to `ripple` via `SendMessage`
3. **Auditor verification**: On `RIPPLE_PASSED` from ripple, team lead sends audit request to `auditor` via `SendMessage`
4. **Completion**: On `AUDIT_PASSED` from auditor, team lead marks task `completed` via `TaskUpdate`

**Rationale**: Completing in-flight work (reviews, ripple analysis, audits) unblocks dependent tasks faster than starting new work.

---

## Related Documentation

- [Update Triggers](update-triggers.md) - When state changes occur
- [Attempt Tracking](attempt-tracking.md) - Attempt counting and escalation thresholds
- [Communication Protocol](../communication-protocol.md) - Team structure and task lifecycle
