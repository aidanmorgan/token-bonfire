# Review and Audit Flow

The staged review pipeline: Developer → Critic → Ripple → Auditor. All routing is performed by the team lead via `SendMessage`.

## Overview

```
Developer → READY_FOR_REVIEW → Team Lead → Critic
                                             │
                                   REVIEW_PASSED / REVIEW_FAILED
                                             │
                              (passed) → Team Lead → Ripple
                              (failed) → Team Lead → Developer (rework)
                                             │
                                   RIPPLE_PASSED / RIPPLE_FAILED
                                             │
                              (passed) → Team Lead → Auditor
                              (failed) → Team Lead → Developer (rework)
                                             │
                                   AUDIT_PASSED / AUDIT_FAILED / AUDIT_BLOCKED
                                             │
                      (passed) → TaskUpdate(completed) → check for newly unblocked tasks
                      (failed) → Team Lead → Developer (rework)
                      (blocked) → Team Lead → Remediation
```

| Stage | Teammate | Purpose | Success | Failure |
|-------|----------|---------|---------|---------|
| Implementation | Developer | Write code | `READY_FOR_REVIEW` | `INFRA_BLOCKED` |
| Quality Review | Critic | Code quality check | `REVIEW_PASSED` | `REVIEW_FAILED` |
| Impact Analysis | Ripple | Second-order effects | `RIPPLE_PASSED` | `RIPPLE_FAILED` |
| Verification | Auditor | Acceptance criteria | `AUDIT_PASSED` | `AUDIT_FAILED` |

## Route to Critic

**Trigger**: Developer sends `READY_FOR_REVIEW: <task-id>` to team lead.

Team lead forwards to critic:

```
SendMessage({
  type: "message",
  recipient: "critic",
  content: "Review task <task-id>:\n\nFiles to Review:\n<files_list>\n\nDeveloper Summary:\n<summary>\n\nReview Focus:\n- Code quality and best practices\n- Error handling patterns\n- Naming conventions\n- Architectural consistency",
  summary: "Review request for task <task-id>"
})
```

Team lead tracks task as `in-critic-review` internally.

### On REVIEW_PASSED → Route to Ripple

Team lead forwards to ripple:

```
SendMessage({
  type: "message",
  recipient: "ripple",
  content: "Analyze impact for task <task-id>:\n\nFiles Modified:\n<files_list>\n\nDeveloper Summary:\n<summary>\n\nCritic Assessment: PASSED\n<quality_notes>",
  summary: "Ripple request for task <task-id>"
})
```

### On REVIEW_FAILED → Developer Rework

1. Increment failure count for the task
2. Check against `TASK_FAILURE_LIMIT` — if exceeded, escalate to user
3. Forward failure details to the developer:

```
SendMessage({
  type: "message",
  recipient: "<dev-name>",
  content: "REVIEW_FEEDBACK: <task-id>\n\n<critic's feedback with specific issues and fix instructions>\n\nPlease address all issues, re-run developer commands, and signal READY_FOR_REVIEW when complete.",
  summary: "Review feedback for task <task-id>"
})
```

## Route to Ripple

**Trigger**: Critic sends `REVIEW_PASSED: <task-id>` to team lead.

Team lead tracks task as `in-ripple-review` internally.

### On RIPPLE_PASSED → Route to Auditor

Team lead forwards to auditor:

```
SendMessage({
  type: "message",
  recipient: "auditor",
  content: "Audit task <task-id>:\n\nAcceptance Criteria:\n<criteria from task description>\n\nFiles to Verify:\n<files_list>\n\nEnvironment:\n<environment from task>\n\nCritic Assessment: PASSED\nRipple Assessment: PASSED",
  summary: "Audit request for task <task-id>"
})
```

### On RIPPLE_FAILED → Developer Rework

Same pattern as REVIEW_FAILED — increment count, check limit, forward to developer.

## Route to Auditor

**Trigger**: Ripple sends `RIPPLE_PASSED: <task-id>` to team lead.

Team lead tracks task as `in-audit` internally.

### On AUDIT_PASSED → Task Complete

1. Mark task complete: `TaskUpdate({ taskId: "<id>", status: "completed" })`
2. Call `TaskList` to check for newly unblocked tasks
3. Assign newly unblocked tasks to idle developers (those who have sent `REQUESTING_WORK`)

### On AUDIT_FAILED → Developer Rework

Same pattern as REVIEW_FAILED — increment count, check limit, forward to developer.

### On AUDIT_BLOCKED → Remediation

Forward to remediation:

```
SendMessage({
  type: "message",
  recipient: "remediation",
  content: "INFRA_BLOCKED: <infrastructure issue from auditor's AUDIT_BLOCKED message>",
  summary: "Infrastructure issue blocking task <task-id>"
})
```

Hold task assignments until remediation completes and health-auditor confirms HEALTHY.

## Review State Tracking

The team lead maintains this internally (no TaskUpdate needed — task status stays `in_progress` throughout the review pipeline):

- `pending-review` → `in-critic-review` → `pending-ripple` → `in-ripple-review` → `pending-audit` → `in-audit` → `passed` / `needs-rework`

## Failure Escalation

If a task fails at the same stage `TASK_FAILURE_LIMIT` times (default 3):
1. Team lead reads all feedback from the failing stage
2. Considers routing to an expert advisor for guidance
3. If still stuck, escalates to user via `AskUserQuestion`
