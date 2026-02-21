# Review and Audit Flow

This document covers how the team lead routes work through the critic -> ripple -> auditor pipeline after a developer signals
`READY_FOR_REVIEW`.

**Related Documents:**

- [task-dispatch.md](task-dispatch.md) - Task dispatch and developer routing
- [developer-rework.md](developer-rework.md) - Rework routing after failures
- [team-architecture.md](team-architecture.md) - Team structure and communication

---

## Overview

**Review & Audit Flow**:

1. ROUTE TO CRITIC (on `READY_FOR_REVIEW` from developer)
2. RECEIVE CRITIC RESPONSE -> `REVIEW_PASSED` or `REVIEW_FAILED`
3. On `REVIEW_PASSED` -> ROUTE TO RIPPLE | On `REVIEW_FAILED` -> Developer rework
4. RECEIVE RIPPLE RESPONSE -> `RIPPLE_PASSED` or `RIPPLE_FAILED`
5. On `RIPPLE_PASSED` -> ROUTE TO AUDITOR | On `RIPPLE_FAILED` -> Developer rework
6. RECEIVE AUDITOR RESPONSE -> `AUDIT_PASSED` / `AUDIT_FAILED` / `AUDIT_BLOCKED`
7. ROUTE: PASS -> complete | FAIL -> rework | BLOCKED -> remediation

### Workflow

DEVELOPER -> READY_FOR_REVIEW -> CRITIC -> REVIEW_PASSED -> RIPPLE -> RIPPLE_PASSED -> AUDITOR -> AUDIT_PASSED -> Complete

On failure: REVIEW_FAILED, RIPPLE_FAILED, or AUDIT_FAILED returns to DEVELOPER with issues

| Stage          | Teammate     | Purpose             | Success            | Failure           |
|----------------|--------------|---------------------|--------------------|-------------------|
| Implementation | Developer    | Write code          | `READY_FOR_REVIEW` | `TASK_INCOMPLETE` |
| Quality Review | **Critic** | Code quality check  | `REVIEW_PASSED`    | `REVIEW_FAILED`   |
| Impact Analysis | **Ripple** | Second-order effects | `RIPPLE_PASSED`    | `RIPPLE_FAILED`   |
| Verification   | Auditor    | Acceptance criteria | `AUDIT_PASSED`     | `AUDIT_FAILED`    |

---

## Step 5: Route to Critic

**Input**: Task ID, files modified, developer's `READY_FOR_REVIEW` message

**Trigger**: Team lead receives `READY_FOR_REVIEW` from developer via mailbox

The critic reviews code quality before formal audit:

- Code style violations
- Missing error handling
- Poor naming conventions
- Architectural violations
- Best practice deviations

### Procedure

1. **Prepare review request**: Build a message containing the task ID, files modified, and the developer's READY_FOR_REVIEW signal

2. **Route to critic via mailbox**:
   ```
   TeammateTool({
       operation: "write",
       to: "critic",
       content: "Review task <task-id>:\n\nFiles to Review:\n<files_list>\n\nDeveloper Signal:\n<ready_signal>\n\nReview Focus:\n- Code quality and best practices\n- Error handling patterns\n- Naming conventions\n- Architectural consistency\n\nEnd with REVIEW_PASSED: <task-id> or REVIEW_FAILED: <task-id>"
   })
   ```

3. **Track routing state** (team lead context only — no TaskUpdate needed):
   Team lead records this task as `in_critic_review` in its internal review pipeline tracking.

---

## Step 6: Receive Critic Response

**Input**: Critic's mailbox message

### REVIEW_PASSED Signal Format

```
REVIEW_PASSED: <task_id>

Files Reviewed:
- <file1>
- <file2>

Quality Assessment:
- Code style: COMPLIANT
- Error handling: ADEQUATE
- Naming: CONSISTENT
- Architecture: ALIGNED

Summary: <brief_assessment>
```

### REVIEW_FAILED Signal Format

```
REVIEW_FAILED: <task_id>

Files Reviewed:
- <file1>
- <file2>

Issues Found:
- <file>:<line>: <issue_description>
- <file>:<line>: <issue_description>

Required Fixes:
- <concrete_action>
- <concrete_action>

Priority: <HIGH|MEDIUM|LOW>

Developer: Please address all issues above and signal READY_FOR_REVIEW when complete.
```

### On REVIEW_PASSED -> Route to Ripple

1. Team lead tracks task as `in_ripple_review` in its review pipeline (no TaskUpdate needed)
2. Route to ripple (see Step 6b)

### On REVIEW_FAILED -> Developer Rework

1. Increment `critique_failures` for the task
2. Check against `TASK_FAILURE_LIMIT` - if exceeded, escalate to user
3. Route failure details back to the developer via mailbox for rework

See [developer-rework.md](developer-rework.md) for rework message construction.

---

## Step 6b: Route to Ripple

**Input**: Task ID, files modified, developer summary, critic assessment

**Trigger**: Team lead receives `REVIEW_PASSED` from critic via mailbox

The ripple analyst examines second-order effects — downstream consumer breakage, API contract drift, test coverage gaps in affected modules, behavioral changes in callers, and shared state impacts.

### Procedure

1. **Prepare ripple request**: Build a message containing the task ID, files modified, developer summary, and critic's quality assessment

2. **Route to ripple via mailbox**:
   ```
   TeammateTool({
       operation: "write",
       to: "ripple",
       content: "Analyze impact for task <task-id>:\n\nFiles Modified:\n<files_list>\n\nDeveloper Summary:\n<summary>\n\nCritic Assessment: PASSED\n<quality_assessment>\n\nAnalysis Focus:\n- Downstream consumer breakage\n- API contract drift\n- Test coverage gaps in affected modules\n- Behavioral changes in callers\n- Shared state impacts\n\nEnd with RIPPLE_PASSED: <task-id> or RIPPLE_FAILED: <task-id>"
   })
   ```

3. **Track routing state** (team lead context only — no TaskUpdate needed):
   Team lead records this task as `in_ripple_review` in its internal review pipeline tracking.

---

## Step 6c: Receive Ripple Response

**Input**: Ripple's mailbox message

### RIPPLE_PASSED Signal Format

```
RIPPLE_PASSED: <task_id>

Impact Summary:
- Files analyzed: <count>
- Direct importers checked: <count>
- Transitive dependents checked: <count>

Impact Graph:
- <modified-file> → imported by [<consumer-1>, <consumer-2>, ...]

Notes:
- <any latent observations — informational only>
```

### RIPPLE_FAILED Signal Format

```
RIPPLE_FAILED: <task_id>

Issues Found:
1. <severity> Source: <modified-file>
   Affected: <consumer-file>:<line>
   Problem: <specific description>
   Remediation: <specific instruction>

Test Coverage Gaps:
- <impacted-file>: no tests for <affected-behavior>

Impact Graph:
- <modified-file> → imported by [<consumer-1>, <consumer-2>, ...]
```

### On RIPPLE_PASSED -> Route to Auditor

1. Team lead tracks task as `pending_audit` in its review pipeline (no TaskUpdate needed)
2. Route to auditor (see Step 7)

### On RIPPLE_FAILED -> Developer Rework

1. Increment `ripple_failures` for the task
2. Check against `TASK_FAILURE_LIMIT` - if exceeded, escalate to user
3. Route failure details back to the developer via mailbox for rework

See [developer-rework.md](developer-rework.md) for rework message construction.

---

## Step 7: Route to Auditor

**Input**: Task ID, files modified, acceptance criteria

**Trigger**: Team lead receives `RIPPLE_PASSED` from ripple via mailbox

### Procedure

1. **Prepare audit request**: Build a message with the full task specification, files modified, acceptance criteria, verification commands, and critic's quality assessment

2. **Route to auditor via mailbox**:
   ```
   TeammateTool({
       operation: "write",
       to: "auditor",
       content: "Audit task <task-id>:\n\nAcceptance Criteria:\n<criteria>\n\nFiles to Verify:\n<files>\n\nCritic Assessment: PASSED\n<quality_assessment>\n\nVerification Commands:\n<commands>\n\nEnd with AUDIT_PASSED: <task-id>, AUDIT_FAILED: <task-id>, or AUDIT_BLOCKED: <task-id>"
   })
   ```

3. **Track routing state** (team lead context only — no TaskUpdate needed):
   Team lead records this task as `in_audit` in its internal review pipeline tracking.

---

## Step 8: Receive Auditor Response

**Input**: Auditor's mailbox message

### AUDIT_PASSED Signal Format

```
AUDIT_PASSED: <task_id>

Verification Results:
- <criterion_1>: VERIFIED - <evidence>
- <criterion_2>: VERIFIED - <evidence>

Commands Executed:
- <command> (<env>): PASS

Summary: <brief_conclusion>
```

### AUDIT_FAILED Signal Format

```
AUDIT_FAILED: <task_id>

Failed Criteria:
- <criterion>: FAILED - <reason>

Issues Found:
- <file>:<line>: <issue_description>

Required Fixes:
- <concrete_action>

Passing Criteria:
- <what_passed>
```

### AUDIT_BLOCKED Signal Format

```
AUDIT_BLOCKED: <task_id>

Pre-existing Failures:
- <N> test failures in <files>
- <infrastructure_issue>

Cannot proceed with audit until infrastructure is fixed.
```

---

## Step 9: Route Based on Outcome

### PASS Routing (Task Complete)

On `AUDIT_PASSED`:

1. Mark task complete: `TaskUpdate({ taskId, status: "completed" })`
2. Check `TaskList` for newly unblocked tasks (tasks whose `blockedBy` are now all completed)
3. Route new work to idle developers

### FAIL Routing (Developer Rework)

On `AUDIT_FAILED`:

1. Increment `audit_failures` for the task
2. Check against `TASK_FAILURE_LIMIT` - if exceeded, escalate to user
3. Route failure details to developer via mailbox for rework
4. Task status remains `in_progress` (set when developer originally claimed the task — no change needed)

See [developer-rework.md](developer-rework.md) for rework message construction.

### BLOCKED Routing (Infrastructure Remediation)

On `AUDIT_BLOCKED`:

1. Route to `remediation` teammate via mailbox:
   ```
   TeammateTool({
       operation: "write",
       to: "remediation",
       content: "INFRA_BLOCKED: <infrastructure issue description>"
   })
   ```
2. Hold task assignments until remediation completes

---

## Signal Quick Reference

| Signal          | Source  | Next Action       |
|-----------------|---------|-------------------|
| `REVIEW_PASSED` | Critic  | Route to ripple   |
| `REVIEW_FAILED` | Critic  | Developer rework  |
| `RIPPLE_PASSED` | Ripple  | Route to auditor  |
| `RIPPLE_FAILED` | Ripple  | Developer rework  |
| `AUDIT_PASSED`  | Auditor | Mark complete     |
| `AUDIT_FAILED`  | Auditor | Developer rework  |
| `AUDIT_BLOCKED` | Auditor | Route remediation |

---

## Cross-References

- [task-dispatch.md](task-dispatch.md) - Task dispatch and developer routing
- [developer-rework.md](developer-rework.md) - Rework routing
- [task-delivery-loop.md](task-delivery-loop.md) - Full delivery loop
- [team-architecture.md](team-architecture.md) - Team structure and communication
- [coordinator-configuration.md](coordinator-configuration.md) - Configuration values
