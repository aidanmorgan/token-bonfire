# Communication Protocol

All inter-agent communication uses `SendMessage` — the native Claude Code Agent Teams messaging tool. There is no custom event log or file-based communication.

## SendMessage API

```
SendMessage({
  type: "message",           // "message" | "broadcast" | "shutdown_request" | "shutdown_response"
  recipient: "<name>",       // target teammate name (required for "message" and "shutdown_request")
  content: "<message body>", // the full message text (required)
  summary: "<5-10 words>"    // short preview for UI (required for "message" and "broadcast")
})
```

### Message Types

| Type | Use | Recipient Required? |
|------|-----|-------------------|
| `message` | Direct message to one teammate | Yes |
| `broadcast` | Same message to all teammates (expensive, avoid) | No |
| `shutdown_request` | Ask a teammate to shut down | Yes |
| `shutdown_response` | Reply to a shutdown request | Yes (`"team-lead"`) |
| `plan_approval_response` | Approve or reject a teammate's plan | Yes |

### Shutdown Protocol

**Request shutdown:**
```
SendMessage({
  type: "shutdown_request",
  recipient: "<teammate-name>",
  content: "All tasks completed. Shutting down."
})
```

**Respond to shutdown:**
```
SendMessage({
  type: "shutdown_response",
  recipient: "team-lead",
  content: "approve"
})
```

**Approve a teammate's plan:**
```
SendMessage({
  type: "plan_approval_response",
  recipient: "<teammate-name>",
  content: "approved"
})
```

### Critical Constraints

- **Text output is NOT visible to other agents.** You MUST use `SendMessage` for all inter-agent communication. Writing to stdout or using print statements will not be seen by any teammate.
- **Messages auto-deliver.** There is no need to poll or check mailboxes — messages are delivered automatically when sent.

## Message Flow

All messages flow through the team lead. No direct peer-to-peer communication (developer-to-developer, developer-to-expert, developer-to-critic, etc.).

```
Developer ──REQUESTING_WORK──────→ Team Lead ──TASK_ASSIGNMENT──→ Developer
Developer ──READY_FOR_REVIEW─────→ Team Lead ──review request──→ Critic
Developer ←──review feedback───── Team Lead ←──REVIEW_FAILED─── Critic
                                   Team Lead ──ripple request──→ Ripple (after Critic passes)
Developer ←──ripple feedback───── Team Lead ←──RIPPLE_FAILED─── Ripple
                                   Team Lead ──audit request───→ Auditor (after Ripple passes)
                                   Team Lead ←──AUDIT_PASS/FAIL── Auditor

Developer ──NEED_EXPERT_ADVICE──→ Team Lead ──question─────────→ Expert Advisor
Developer ←──domain guidance───── Team Lead ←──EXPERT_ADVICE──── Expert Advisor
```

## Signal Reference

### Developer → Team Lead

| Signal | When | Content |
|--------|------|---------|
| `REQUESTING_WORK` | On startup, after signaling ready, when idle | Request next task assignment |
| `READY_FOR_REVIEW: <task-id>` | Task implemented and self-verified | Summary, files modified |
| `NEED_EXPERT_ADVICE: <expert-name> <question>` | Needs domain guidance | Question details, task context |
| `NEED_CLARIFICATION: <question>` | Ambiguous requirements or missing dependency | What's unclear |
| `INFRA_BLOCKED: <details>` | Infrastructure prevents progress | Error output, commands tried |
| `FILE_CONFLICT: <file> <details>` | Conflict with another developer's changes | File path, nature of conflict |
| `CHECKPOINT: <task-id>` | Optional progress update during complex tasks | Progress status, files modified |

### Team Lead → Developer

| Message | When |
|---------|------|
| `TASK_ASSIGNMENT: <task-id>` + full task detail | Assigning a new task (from `TaskGet`) |
| Review feedback | Critic, ripple, or auditor rejected task |
| Expert advice | Expert advisor provided domain guidance |
| Clarification response | User or business-analyst answered question |
| `NO_TASKS_AVAILABLE` | All tasks completed, in-progress, or blocked |

### Critic → Team Lead

| Signal | When |
|--------|------|
| `REVIEW_PASSED: <task-id>` | Code quality acceptable |
| `REVIEW_FAILED: <task-id> [feedback]` | Quality issues found |
| `REQUESTING_WORK` | No pending reviews |

### Ripple → Team Lead

| Signal | When |
|--------|------|
| `RIPPLE_PASSED: <task-id>` | No breaking downstream impacts |
| `RIPPLE_FAILED: <task-id> [feedback]` | Second-order issues found |
| `REQUESTING_WORK` | No pending requests |

### Auditor → Team Lead

| Signal | When |
|--------|------|
| `AUDIT_PASSED: <task-id>` | All acceptance criteria verified |
| `AUDIT_FAILED: <task-id> [feedback]` | Criteria not met |
| `AUDIT_BLOCKED: <task-id> [details]` | Pre-existing infrastructure failures |
| `REQUESTING_WORK` | No pending audits |

### Expert Advisor → Team Lead

| Signal | When |
|--------|------|
| `EXPERT_ADVICE_PROVIDED: <task-id> [advice]` | Domain guidance provided |
| `REQUESTING_WORK` | No pending questions |

### Business Analyst → Team Lead

| Signal | When |
|--------|------|
| `EXPANDED_TASK_SPECIFICATION: <task-id>` | Task expanded successfully |
| `SEEKING_DIVINE_CLARIFICATION: <question>` | Needs user input |
| `REQUESTING_WORK` | No pending requests |

### Remediation → Team Lead

| Signal | When |
|--------|------|
| `REMEDIATION_COMPLETE` | Infrastructure fixed, all checks pass |
| `SEEKING_DIVINE_CLARIFICATION` | Cannot fix after 3 attempts |
| `REQUESTING_WORK` | No pending requests |

### Health Auditor → Team Lead

| Signal | When |
|--------|------|
| `HEALTH_AUDIT: HEALTHY` | All verification commands pass |
| `HEALTH_AUDIT: UNHEALTHY [details]` | Verification failures found |
| `REQUESTING_WORK` | No pending requests |

## Audit Trail

The team lead maintains visibility into the workflow by tracking:
- Which tasks are at which stage in the critic → ripple → auditor pipeline
- Failure counts per task
- Infrastructure status
- Which developers are idle vs working

This information is maintained in the team lead's context. It does not need to be persisted because:
- Task state persists in the shared task list (via plan slug)
- Expert advisor definitions persist on disk (at `.claude/experts/<plan_slug>/`)
- On resume, the team lead reconstructs state from `TaskList` and expert advisor files
