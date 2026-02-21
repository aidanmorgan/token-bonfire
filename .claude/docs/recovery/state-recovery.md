# Task List Recovery

Procedures for auditing and recovering task state from the native shared task list.

## Overview

In the native Agent Teams system, task state persists in the shared task list (keyed by plan slug). There is no custom state file to corrupt or reconstruct. The team lead audits task state on resume by calling `TaskList`.

See also:

- [Session Recovery](session-recovery.md) - Complete session recovery procedures
- [Recovery Index](index.md) - Overview of all recovery procedures

---

## Task State Audit

On resume, the team lead calls `TaskList` and audits each task:

### Status Categories

The shared task list only stores three valid status values via `TaskUpdate`:

| Status | Meaning on Resume | Action |
|---|---|---|
| `completed` | Task finished in a previous session | No action needed — skip |
| `pending` (unblocked) | Available for developers to claim | Will be claimed by fresh developers |
| `pending` (blocked) | Waiting for dependencies | Will auto-unblock when blockers complete |
| `in_progress` | Orphaned — developer that claimed it crashed | Auto-releases after heartbeat timeout (~5 min) |

**Note**: Review pipeline stages (`in_critic_review`, `in_ripple_review`, `in_audit`, `needs_rework`) are NOT task statuses — they are tracked by the team lead in its context. When the session crashes, this context is lost. On resume, any task that was mid-review will appear as `in_progress` in the task list and is treated as incomplete (reset to `pending` per the resume procedure).

### Orphaned In-Progress Tasks

Tasks stuck in `in_progress` with no active developer are the most common resume issue. Resolution:

1. The native heartbeat timeout (~5 min) automatically releases orphaned tasks
2. Fresh developers will then be able to claim them
3. The team lead does NOT need to manually change task status — the native system handles it
4. Partial work from the crashed developer remains in the file system (git working tree)

### Review Pipeline Reconstruction

Since review pipeline state is stored in team lead context (not the task list), it cannot be reconstructed on resume. Instead:

- Tasks that were mid-review will be `in_progress` in the task list and auto-release after heartbeat timeout
- Fresh developers claim them and run the full Developer -> Critic -> Ripple -> Auditor pipeline again
- This is safe — the auditor always verifies final state, not intermediate review history

### Completed Task Verification

For recently completed tasks (completed near the end of the previous session), the team lead may optionally:

1. Ask the auditor to re-verify the most recent completions
2. This catches edge cases where a task was marked complete but the crash occurred before all effects settled

This is optional — the shared task list state is reliable.

---

## What Replaces Custom State Recovery

| Old System | New System |
|---|---|
| Custom JSON state file (`STATE_FILE`) | Native shared task list via `TaskList` |
| `save_state()` / `load_state()` | `TaskUpdate({ taskId, status })` for transitions |
| Atomic writes with temp files | Native file-locked task updates |
| State file corruption detection | Not needed — native persistence |
| State reconstruction from event log | Not needed — `TaskList` returns current state |

---

## Cross-References

- [Session Recovery](session-recovery.md) - Complete recovery orchestration
- [State Management](../state/index.md) - Task state tracking
- [Team Architecture](../team-architecture.md) - Resume behavior
