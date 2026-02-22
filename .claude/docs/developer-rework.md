# Developer Rework

This document covers how the team lead routes rework assignments to developer agents after review or audit failures.

**Related Documents:**

- [review-audit-flow.md](review-audit-flow.md) - Review and audit flow
- [task-delivery-loop.md](task-delivery-loop.md) - Full delivery loop
- [communication-protocol.md](communication-protocol.md) - Team structure and communication

---

## Overview

Developer rework is triggered when:

- **REVIEW_FAILED** - Critic found code quality issues
- **RIPPLE_FAILED** - Ripple found second-order effects (downstream breakage, API contract drift, test coverage gaps)
- **AUDIT_FAILED** - Auditor found acceptance criteria not met

The team lead routes the failure feedback back to the developer via mailbox.

- CRITIC -> (REVIEW_FAILED with issues) -> DEVELOPER (rework via mailbox)
- RIPPLE -> (RIPPLE_FAILED with issues) -> DEVELOPER (rework via mailbox)
- AUDITOR -> (AUDIT_FAILED with issues) -> DEVELOPER (rework via mailbox)

---

## On REVIEW_FAILED (from Critic)

When the critic signals `REVIEW_FAILED`, the team lead routes the issues back to the developer.

### State Updates

1. Increment `critique_failures` count for the task
2. Check against `TASK_FAILURE_LIMIT` - if exceeded, escalate to user
3. Update task status: `TaskUpdate({ taskId, status: "in_progress" })`

### Route Rework via Mailbox

```
SendMessage({
    type: "message",
    recipient: "<developer-name>",
    summary: "Critic review failed, rework required",
    content: "REWORK: <task-id>

CRITIC REVIEW FAILED

The Critic reviewed your code and found issues that must be fixed.

Issues Found:
<critic_issues>

Required Fixes:
<required_fixes>

Priority: <priority>

Your Previous Work:
Files Modified:
<files_modified>

Instructions:
1. Read the issues carefully
2. Fix ALL issues listed above
3. Re-run verification commands
4. Signal READY_FOR_REVIEW when all issues are addressed

Do NOT skip any issues. The same Critic will review again.

Begin rework."
})
```

---

## On AUDIT_FAILED (from Auditor)

When the auditor signals `AUDIT_FAILED`, the team lead routes the issues back to the developer.

### State Updates

1. Increment `audit_failures` count for the task
2. Check against `TASK_FAILURE_LIMIT` - if exceeded, escalate to user
3. Update task status: `TaskUpdate({ taskId, status: "in_progress" })`

### Route Rework via Mailbox

```
SendMessage({
    type: "message",
    recipient: "<developer-name>",
    summary: "Audit failed, rework required",
    content: "REWORK: <task-id>

AUDIT_FAILED

The Auditor verified your implementation against the acceptance criteria and found issues.

Failed Criteria:
<failed_criteria>

Issues Found:
<audit_issues>

Required Fixes:
<required_fixes>

Passing Criteria:
<passing_criteria>

Your Previous Work:
Files Modified:
<files_modified>

Instructions:
1. Review the failed criteria carefully
2. Understand WHY each criterion failed
3. Fix ALL issues listed above
4. Re-run verification commands in ALL environments
5. Signal READY_FOR_REVIEW when all criteria are met

The code will go through Critic review again before re-audit.

Begin rework."
})
```

---

## Rework Flow

DEVELOPER -> (READY_FOR_REVIEW) -> CRITIC

- On REVIEW_FAILED -> DEVELOPER reworks
- On REVIEW_PASSED -> RIPPLE
    - On RIPPLE_FAILED -> DEVELOPER reworks
    - On RIPPLE_PASSED -> AUDITOR
        - On AUDIT_FAILED -> DEVELOPER reworks
        - On AUDIT_PASSED -> TASK COMPLETE

---

## Environment-Specific Rework

When audit fails in specific environments, include environment details in the rework message:

```
SendMessage({
    type: "message",
    recipient: "<developer-name>",
    summary: "Environment-specific failure, rework required",
    content: "REWORK: <task-id>

ENVIRONMENT-SPECIFIC FAILURE

Your implementation passes in some environments but fails in others.

Environment Results:
| Environment | Status | Details |
|-------------|--------|---------|
| Mac | PASS | ... |
| Devcontainer | FAIL | ... |

Failed Environments:
<failed_environment_details>

Common Causes:
- Missing dependencies in specific environments
- Hardcoded paths that differ between environments
- Version differences in libraries
- Platform-specific code assumptions

Instructions:
1. Analyze why the code fails in specific environments
2. Ensure the fix works in ALL environments
3. Run verification commands in EVERY environment before signaling
4. Signal READY_FOR_REVIEW only when ALL environments pass

Begin rework."
})
```

---

## Failure Tracking

Track failures to detect patterns and prevent infinite loops:

| Field               | Type           | Description                          |
|---------------------|----------------|--------------------------------------|
| `critique_failures` | task_id -> int | Number of critic failures per task   |
| `audit_failures`    | task_id -> int | Number of audit failures per task    |
| `TASK_FAILURE_LIMIT`| constant       | Max failures before escalation (3)   |

On reaching the failure limit for a task:

1. Escalate to user via `AskUserQuestion`
2. Update task with failure details
3. Continue routing other work to developers (do not block the pipeline)

---

## Rework vs Fresh Start

| Scenario               | Action                           |
|------------------------|----------------------------------|
| First failure          | Rework with feedback             |
| Second failure         | Rework with accumulated feedback |
| Third failure          | Escalate to user                 |
| Different failure type | Reset counter for that type      |

---

## Cross-References

- [review-audit-flow.md](review-audit-flow.md) - Review and audit flow
- [task-dispatch.md](task-dispatch.md) - Task dispatch and developer routing
- [task-delivery-loop.md](task-delivery-loop.md) - Full delivery loop
- [communication-protocol.md](communication-protocol.md) - Team structure and communication
- [base_variables.md](../base_variables.md) - Configuration values
