# State Fields

[← Back to State Management](index.md)

All state field definitions organized by category. State is tracked via native Agent Teams primitives — the shared task list (`TaskCreate`/`TaskUpdate`/`TaskList`/`TaskGet`) and mailbox messages (`TeammateTool write`).

---

## State Fields

### Task Tracking (via Shared Task List)

These fields are managed natively by the shared task list keyed by the plan slug:

| Field | Storage | Description |
|---|---|---|
| Task status | `TaskUpdate({ status })` | `pending`, `in_progress`, `completed` — these are the only valid `TaskUpdate` status values |
| Task dependencies | `TaskUpdate({ addBlockedBy })` | Auto-unblock when blocking task completes |
| Task assignment | `TaskUpdate({ status: "in_progress" })` | Native atomic task claiming prevents race conditions |
| Task description | `TaskCreate` / `TaskUpdate` | Full task spec including acceptance criteria |

### Team Lead Review State (maintained in team lead context)

The team lead maintains these review pipeline mappings in its own context:

| Field | Type | Description |
|---|---|---|
| Review pipeline status | Map | Task ID to review stage: `pending_review`, `in_critic_review`, `in_ripple_review`, `pending_audit`, `in_audit`, `needs_rework`, `passed` |
| Critique failure counts | Map | Task ID to critic failure count |
| Critic timeout counts | Map | Task ID to critic timeout count |
| Audit failure counts | Map | Task ID to audit failure count |

### Infrastructure Tracking (team lead context)

| Field | Type | Description |
|---|---|---|
| `infrastructure_blocked` | Boolean | Assignments halted for remediation |
| `infrastructure_issue` | String | Details of blocking issue |
| `remediation_attempt_count` | Integer | Current remediation loop iteration (max 3) |

### Expert Tracking (persisted prompt files on disk)

Expert state is stored as prompt files on disk at `.claude/experts/<plan_slug>/`:

| Field | Storage | Description |
|---|---|---|
| Expert definitions | `.claude/experts/<plan_slug>/<expert-name>.md` | Persisted prompt files with identity, domain expertise, and applicable tasks |
| Expert roster | Team lead context | Which experts are spawned, their names and domains |
| Expert task affinity | Expert prompt files | Which task IDs each expert is responsible for |

**Expert Prompt File Structure** (persisted on disk):

```markdown
# <Expert Name>

## Identity
- Domain authority description
- Applicable task IDs

## Expertise
- Deep domain research (technologies, patterns, pitfalls)
- Decision frameworks
- Verification criteria

## Applicable Tasks
| Task ID | Subject | Key Challenge |
```

### File Conflict Tracking (via mailbox)

| Field | Storage | Description |
|---|---|---|
| File conflict signals | Mailbox messages | Developers signal `FILE_CONFLICT` to team lead |
| Ownership resolution | Mailbox messages | Team lead routes resolution to developers |

### User Escalation (team lead context)

| Field | Type | Description |
|---|---|---|
| Pending questions | Team lead context | Questions awaiting human response via `AskUserQuestion` |
| Task quality assessed | Boolean | Whether initial assessment completed |
| Pending expansions | Map | Task ID to business-analyst expansion in progress |

---

## Related Documentation

- [Attempt Tracking](attempt-tracking.md) - Attempt tracking and escalation
- [Update Triggers](update-triggers.md) - When and how state updates
- [State Fields](fields.md) - Task list field reference
