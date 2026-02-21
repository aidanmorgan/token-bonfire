# Teammate Coordination

The team lead actively manages developer engagement through task analysis, domain-based routing, and mailbox-mediated communication.

**Related Documentation:**

- [Team Architecture](team-architecture.md) - Team structure, expert generation, and communication protocol
- [Teammate Definitions](agent-definitions.md) - All teammate roles and signals
- [Teammate Context Management](agent-context-management.md) - Context monitoring and checkpointing

---

## Task-Developer Matching

When generating the task plan during gap analysis, the team lead assigns task affinity to each developer based on domain clustering.

### Task Affinity

Each developer has a list of **applicable task IDs** determined during gap analysis:

```
DEVELOPER ROSTER for <plan_slug>:
  1. dev-1 — tasks: [task-1, task-2, task-5]
  2. dev-2 — tasks: [task-3, task-4]
  3. dev-3 — tasks: [task-6, task-7, task-8]
```

### Developer Self-Organization

Developers self-organize by checking `TaskList` for available work:

1. **Prefer applicable tasks** — tasks in their affinity list
2. **Claim via** `TaskUpdate({ status: "in_progress" })` — file ownership ensures only one developer succeeds
3. **If all applicable tasks are blocked or complete** — may claim other unblocked tasks
4. **Never idle** — always claim next work or check mailbox after signaling

The team lead can also route specific tasks to developers via `write` messages.

---

## Communication Flow

### Developer --> Team Lead --> Routing Target

All communication flows through the team lead:

```
Developer ──READY_FOR_REVIEW──> Team Lead ──review request──> Critic
Developer <──review feedback─── Team Lead <──REVIEW_PASSED/FAILED── Critic
                                Team Lead ──ripple request──> Ripple (after Critic passes)
                                Team Lead <──RIPPLE_PASSED/FAILED── Ripple
                                Team Lead ──audit request──> Auditor (after Ripple passes)
                                Team Lead <──AUDIT_PASSED/FAILED── Auditor
```

### Message Routing

**From developer agents:**

| Signal | Team Lead Action |
|--------|-----------------|
| `READY_FOR_REVIEW: <task-id>` | `write` review request to `critic` |
| `NEED_CLARIFICATION: <question>` | Route to `business-analyst` or `AskUserQuestion` |
| `INFRA_BLOCKED: <details>` | `write` to `remediation` |
| `FILE_CONFLICT: <file>` | Coordinate file ownership between developers via `write` |

**From `critic`:**

| Signal | Team Lead Action |
|--------|-----------------|
| `REVIEW_PASSED: <task-id>` | `write` ripple request to `ripple` |
| `REVIEW_FAILED: <task-id>` | `write` feedback to owning developer |

**From `ripple`:**

| Signal | Team Lead Action |
|--------|-----------------|
| `RIPPLE_PASSED: <task-id>` | `write` audit request to `auditor` |
| `RIPPLE_FAILED: <task-id>` | `write` feedback to owning developer |

**From `auditor`:**

| Signal | Team Lead Action |
|--------|-----------------|
| `AUDIT_PASSED: <task-id>` | `TaskUpdate({ status: "completed" })` — ONLY completion trigger |
| `AUDIT_FAILED: <task-id>` | `write` feedback to owning developer |
| `AUDIT_BLOCKED: <task-id>` | `write` to `remediation` |

**From supporting teammates:**

| Signal | Team Lead Action |
|--------|-----------------|
| `EXPANDED_TASK_SPECIFICATION: <task-id>` | `TaskUpdate` description, route to developer |
| `REMEDIATION_COMPLETE` | `write` to `health-auditor` |
| `HEALTH_AUDIT: HEALTHY` | Resume normal flow |
| `HEALTH_AUDIT: UNHEALTHY` | `write` to `remediation` for retry |

---

## File Ownership Coordination

### Proactive (At Task Creation)

During gap analysis, the team lead:

1. **Assigns file ownership** to each task — no two concurrent tasks own the same file
2. **Sets dependencies** via `TaskUpdate({ addBlockedBy })` to serialize access to shared files
3. **Encodes ownership** in task descriptions so developers know their boundaries

### Reactive (At Runtime)

When a developer signals `FILE_CONFLICT`:

1. Team lead identifies the file owner
2. Coordinates via `write` to both developers:
   - Assigns single owner
   - Other developer yields or waits
   - Or instructs additive-only changes for shared files

See [Concurrency - Conflict Handling](concurrency/conflict-handling.md) for full details.

---

## Review Pipeline

Tasks flow through a staged pipeline managed by the team lead:

```
pending --> in_progress --> in_critic_review --> in_ripple_review --> in_audit --> completed
                                                                              ↘ needs_rework --> in_progress (loop)
```

### Review State Tracking

The team lead maintains a mapping of task-id to review status:

| Status | Meaning |
|--------|---------|
| `in_critic_review` | Dispatched to critic |
| `in_ripple_review` | Critic passed, dispatched to ripple |
| `in_audit` | Ripple passed, dispatched to auditor |
| `needs_rework` | Critic, ripple, or auditor failed, feedback sent to developer |
| `completed` | Auditor approved, task marked completed |

---

## Clarification Handling

When a developer sends `NEED_CLARIFICATION`, the team lead decides:

| Situation | Action |
|-----------|--------|
| Requirements ambiguity | `write` to `business-analyst` for expansion |
| Missing dependency information | Answer directly if known, or `AskUserQuestion` |
| Technical decision needed | Answer based on project context, or `AskUserQuestion` |
| Missing `blockedBy` dependency | Add dependency via `TaskUpdate({ addBlockedBy })` |

---

## Error Escalation

| Situation | Action |
|-----------|--------|
| Developer fails self-verification repeatedly | Read developer's messages, `write` specific guidance |
| Critic or auditor rejects same task 3+ times | Investigate root cause, consider reassigning |
| No unblocked tasks but work remains | Report blocking chain to user |
| Infrastructure failure | Route to `remediation` via `write` |
| Ambiguous acceptance criteria | Route to `business-analyst` or `AskUserQuestion` |
| Teammate crash (heartbeat timeout ~5 min) | Task auto-releases; respawn from persisted prompt |
| File conflict between developers | `write` to both, assign single owner |
| Health auditor reports UNHEALTHY after remediation | Route back to `remediation`, escalate after 3 cycles |

---

## Inter-Developer Artifact Transfer

For complex artifacts that need to be shared between developers, use the task dependency system:

1. **Contract task** creates types, interfaces, or schemas
2. **Implementation tasks** `blockedBy` the contract task
3. Developers implement against the defined contracts after they are available
4. Task descriptions reference the artifact locations

No custom artifact manifest or transfer protocol is needed — the shared file system and task dependencies handle coordination.

---

## Related Documentation

- [Team Architecture](team-architecture.md) - Team structure and expert advisor generation
- [Teammate Definitions](agent-definitions.md) - All teammate roles and signals
- [Teammate Context Management](agent-context-management.md) - Context and checkpointing
- [Signal Specification](signals/index.md) - Signal format reference
- [Concurrency](concurrency/index.md) - File ownership and conflict handling
