# State Persistence

[← Back to State Management](index.md)

State persists automatically via native Agent Teams primitives. No custom state files or atomic write procedures are needed.

---

## Persistence Mechanisms

### Shared Task List (primary state)

The shared task list is the central state store. It is keyed by the **plan slug** — a deterministic, URL-safe string derived from the plan title. Key properties:

- **Persists on disk** — tasks survive crashes and session restarts
- **Native atomic claiming** — concurrent claims by multiple developers are safe
- **Auto-unblocking** — dependencies release automatically when blocking tasks complete
- **Deterministic slug** — same plan title always produces the same slug, so re-running loads the same task list

Task state transitions via `TaskUpdate({ taskId, status })` use only three values:
- `pending` → `in_progress` → `completed`
- `completed` (terminal — only set by team lead after `AUDIT_PASSED`)
- `in_progress` → `pending` (reset on resume, or when rework is needed)

The review pipeline stages (critic, ripple, audit) are tracked by the team lead in its own context as routing state — they are NOT status values in `TaskUpdate`.

### Expert Prompt Files (persisted on disk)

Expert definitions are saved to `.claude/experts/<plan_slug>/`:
```
.claude/experts/
  user-auth-implementation/
    auth-expert.md
    database-expert.md
    api-expert.md
```

On resume, these files are loaded from disk — no regeneration needed. This preserves the deep research investment.

### Teammate Context (ephemeral)

Each teammate has its own 1M token context window. This context is:
- **Not persisted** across crashes or restarts
- **Self-contained** via the spawn prompt (expert identity, domain knowledge, configuration)
- **Recoverable** by respawning the teammate using the persisted prompt files

### Team Lead Context (ephemeral but reconstructable)

The team lead tracks review pipeline state, failure counts, and infrastructure status in its context. On resume:
1. Call `TaskList` to reconstruct task state
2. Load expert files from disk to reconstruct the roster
3. Respawn teammates using persisted prompts
4. Developers reclaim pending work automatically

---

## Recovery on Resume

Recovery is automatic via the plan slug:

1. Re-run `/bonfire $PLAN_FILE` — bootstrapper produces the same `plan_slug`
2. Team lead finds expert files at `.claude/experts/<plan_slug>/` — loads them (no regeneration)
3. Team lead calls `TaskList` — finds existing tasks with all progress intact
4. Spawns fresh teammates using persisted prompts — developers claim pending tasks
5. Completed tasks stay completed; orphaned in-progress tasks auto-release after heartbeat timeout

---

## Related Documentation

- [Update Triggers](update-triggers.md) - When state transitions occur
- [Recovery Procedures](../recovery/index.md) - Error recovery
- [State Fields](fields.md) - Task list field reference
- [Team Architecture](../team-architecture.md) - Resume and crash recovery details
