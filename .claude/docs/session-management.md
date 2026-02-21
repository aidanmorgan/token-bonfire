# Session Management

## Context Management

Each teammate (expert, critic, auditor, etc.) has its own independent 1M token context window. Context management is handled natively — no custom compaction or session pause procedures are needed.

### Key Properties

- **Context windows are isolated**: Teammates do NOT inherit the team lead's conversation history and cannot see each other's context
- **1M token capacity per teammate**: Sufficient for most tasks without compaction
- **Spawn prompts are self-contained**: Each teammate receives everything it needs at spawn time
- **No custom compaction**: Native context management replaces custom compaction procedures

### What Each Teammate Sees

- Their spawn prompt (must be self-contained)
- CLAUDE.md files in the working directory (auto-loaded)
- Mailbox messages received via `TeammateTool write`

## Resume Procedures

For the complete recovery flow — including how the plan slug drives state recovery, expert file loading, and orphaned task handling — see [state/persistence.md](state/persistence.md#recovery-on-resume).

The full resume detection mode matrix (FRESH START / RESUME / EXPERT REUSE / ORPHANED TASKS) is in [recovery/session-recovery.md](recovery/session-recovery.md).

### Resume Task Context

When teammates are respawned on resume, they receive their full spawn prompt (identity, domain expertise, applicable tasks) but NOT the in-flight conversation from the crashed session. This means:

- Domain knowledge is preserved (from persisted expert prompt files)
- Partial implementation progress is preserved (in the git working tree)
- In-flight context is lost (conversation history within the crashed teammate's context window)

Teammates handle this gracefully by:
1. Calling `TaskList` to find available work
2. Reading existing files to understand what was already done
3. Claiming and continuing from the current file system state

## Team Lead Recovery

If the team lead crashes or is terminated mid-operation:

### Recovery Trigger

A new `/bonfire $PLAN_FILE` invocation after unexpected termination triggers recovery when:
- Expert files exist at `.claude/experts/<plan_slug>/`
- Tasks exist in the shared task list (from `TaskList`)

### Recovery Procedure

1. Parse plan file (produces same `plan_slug`)
2. Load expert definitions from disk
3. Call `TaskList` to audit current state
4. Report recovery status:
   ```
   TEAM LEAD RECOVERY for <plan_slug>

   Experts loaded: <N> from disk
   Tasks: <completed>/<total> complete
   Orphaned in-progress: <N>
   Pending review: <N>
   Pending audit: <N>
   Available: <N>
   ```
5. Spawn fresh teammates
6. Resume monitoring loop

### Orphaned Teammate Handling

When the team lead crashes, teammates that were running:
- Complete their current work, then idle
- The `TeammateIdle` hook prompts them to check for work, but with no lead to route messages, they eventually stop
- On resume, the new team lead spawns fresh teammates — old ones are replaced

## Shutdown Sequence

When all tasks are complete:

1. Team lead calls `TeammateTool({ operation: "requestShutdown" })` for each teammate
2. Each teammate finishes current work, sends `shutdown_approved`
3. Team lead calls `TeammateTool({ operation: "cleanup" })` to remove team resources
4. Team lead reports final status to user

### Shutdown Output

```
ALL TASKS COMPLETE for <plan_slug>

Total tasks: <N>
All passed through critic review and auditor verification.

Shutting down team...
  <expert-1>: shutdown_approved
  <expert-2>: shutdown_approved
  critic: shutdown_approved
  auditor: shutdown_approved
  ...

Team cleanup complete.
```

---

## Cross-References

- [Session Recovery](recovery/session-recovery.md) - Complete recovery orchestration
- [State Management](state/index.md) - Task state tracking
- [Team Architecture](team-architecture.md) - Team structure and lifecycle
- [Recovery Procedures](recovery/index.md) - All recovery procedures
