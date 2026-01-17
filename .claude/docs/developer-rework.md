# Developer Rework

This document covers how the coordinator dispatches developer agents for rework after review or audit failures.

**Related Documents:**

- [review-audit-flow.md](review-audit-flow.md) - Review and audit flow
- [signal-specification.md](signal-specification.md) - Signal formats
- [state-management.md](state-management.md) - State tracking

---

## Overview

Developer rework is triggered when:

- **REVIEW_FAILED** - Critic found code quality issues
- **AUDIT_FAILED** - Auditor found acceptance criteria not met

The coordinator re-dispatches the developer with the failure feedback.

- CRITIC → (REVIEW_FAILED with issues) → DEVELOPER (rework)
- AUDITOR → (AUDIT_FAILED with issues) → DEVELOPER (rework)

---

## On REVIEW_FAILED (from Critic)

When the Critic signals `REVIEW_FAILED`, the orchestrator dispatches the developer for rework.

### State Updates

> **Authoritative source**: [state/update-triggers.md - REVIEW_FAILED](state/update-triggers.md#review_failed)

```python
# Remove from review queue
pending_critique.remove(task_id)

# Track failure count
critique_failures[task_id] = critique_failures.get(task_id, 0) + 1

# Check if exceeded limit
if critique_failures[task_id] >= TASK_FAILURE_LIMIT:
    log_event("workflow_failed", reason="review_failure_limit", task_id=task_id)
    return

# Update task status
in_progress_tasks[task_id]['status'] = 'implementing'
```

### Rework Prompt

```python
rework_prompt = f"""
{Read(".claude/agents/developer.md")}

---

## Rework Assignment

Task ID: {task_id}

### CRITIC REVIEW FAILED

The Critic reviewed your code and found issues that must be fixed.

### Issues Found
{format_critic_issues(critic_output)}

### Required Fixes
{format_required_fixes(critic_output)}

### Priority: {extract_priority(critic_output)}

### Your Previous Work
You previously submitted this work for review.

Files Modified:
{format_files_modified(previous_work)}

### Instructions

1. Read the issues carefully
2. Fix ALL issues listed above
3. Re-run verification commands
4. Signal READY_FOR_REVIEW when all issues are addressed

Do NOT skip any issues. The same Critic will review again.

Begin rework.
"""
```

### Dispatch

```python
Task tool parameters:
  description: "developer rework for {task_id} (review failure)"
  model: [from developer agent file]
  subagent_type: "developer"
  prompt: [rework_prompt]

log_event("developer_rework_dispatched",
          task_id=task_id,
          reason="critic_fail",
          attempt=critique_failures[task_id])
save_state()
```

---

## On AUDIT_FAILED (from Auditor)

When the Auditor signals `AUDIT_FAILED`, the orchestrator dispatches the developer for rework.

### State Updates

> **Authoritative source**: [state/update-triggers.md - AUDIT_FAILED](state/update-triggers.md#audit_failed)

```python
# Remove from audit queue
pending_audit.remove(task_id)

# Track failure count
audit_failures[task_id] = audit_failures.get(task_id, 0) + 1

# Check if exceeded limit
if audit_failures[task_id] >= TASK_FAILURE_LIMIT:
    log_event("workflow_failed", reason="audit_failure_limit", task_id=task_id)
    return

# Update task status
in_progress_tasks[task_id]['status'] = 'implementing'
```

### Rework Prompt

```python
rework_prompt = f"""
{Read(".claude/agents/developer.md")}

---

## Rework Assignment

Task ID: {task_id}

### AUDIT_FAILED

The Auditor verified your implementation against the acceptance criteria and found issues.

### Failed Criteria
{format_failed_criteria(auditor_output)}

### Issues Found
{format_audit_issues(auditor_output)}

### Required Fixes
{format_required_fixes(auditor_output)}

### Passing Criteria
These criteria were verified successfully:
{format_passing_criteria(auditor_output)}

### Your Previous Work
You previously submitted this work for audit.

Files Modified:
{format_files_modified(previous_work)}

### Instructions

1. Review the failed criteria carefully
2. Understand WHY each criterion failed
3. Fix ALL issues listed above
4. Re-run verification commands in ALL environments
5. Signal READY_FOR_REVIEW when all criteria are met

The code will go through Critic review again before re-audit.

Begin rework.
"""
```

### Dispatch

```python
Task tool parameters:
  description: "developer rework for {task_id} (audit failure)"
  model: [from developer agent file]
  subagent_type: "developer"
  prompt: [rework_prompt]

log_event("developer_rework_dispatched",
          task_id=task_id,
          reason="audit_failed",
          attempt=audit_failures[task_id])
save_state()
```

---

## Rework Flow

DEVELOPER → (READY_FOR_REVIEW) → CRITIC

- On REVIEW_FAILED → DEVELOPER reworks
- On REVIEW_PASSED → AUDITOR
    - On AUDIT_FAILED → DEVELOPER reworks
    - On AUDIT_PASSED → TASK COMPLETE

---

## Environment-Specific Rework

When audit fails in specific environments:

```python
rework_prompt = f"""
{Read(".claude/agents/developer.md")}

---

## Rework Assignment

Task ID: {task_id}

### ENVIRONMENT-SPECIFIC FAILURE

Your implementation passes in some environments but fails in others.

### Environment Results

| Environment | Status | Details |
|-------------|--------|---------|
{{#each environment_results}}
| {{this.name}} | {{this.status}} | {{this.details}} |
{{/each}}

### Failed Environments
{{#each failed_environments}}
## {{this.name}}

Check: {{this.check}}
Error: {{this.error}}
{{/each}}

### Common Causes
- Missing dependencies in specific environments
- Hardcoded paths that differ between environments
- Version differences in libraries
- Platform-specific code assumptions

### Instructions

1. Analyze why the code fails in specific environments
2. Ensure the fix works in ALL environments
3. Run verification commands in EVERY environment before signaling
4. Signal READY_FOR_REVIEW only when ALL environments pass

Begin rework.
"""
```

---

## Failure Tracking

Track failures to detect patterns and prevent infinite loops:

```python
# State tracking for failures
critique_failures: dict[str, int] = {}  # task_id -> failure count
audit_failures: dict[str, int] = {}   # task_id -> failure count

# Constants
TASK_FAILURE_LIMIT = 3  # Max failures before workflow fails

# On workflow failure
def handle_workflow_failure(task_id: str, reason: str):
    log_event("workflow_failed", task_id=task_id, reason=reason)

    # Remove from active work
    in_progress_tasks = [t for t in in_progress_tasks if t['task_id'] != task_id]

    # Add to failed tasks
    failed_tasks.append({
        'task_id': task_id,
        'reason': reason,
        'review_attempts': critique_failures.get(task_id, 0),
        'audit_attempts': audit_failures.get(task_id, 0)
    })

    save_state()
```

---

## Rework vs Fresh Start

| Scenario               | Action                           |
|------------------------|----------------------------------|
| First failure          | Rework with feedback             |
| Second failure         | Rework with accumulated feedback |
| Third failure          | Workflow fails, escalate         |
| Different failure type | Reset counter for that type      |

---

## Cross-References

- [review-audit-flow.md](review-audit-flow.md) - Review and audit flow
- [signal-specification.md](signal-specification.md) - Signal formats
- [agent-recovery.md](agent-recovery.md) - Timeout and crash handling
- [state-management.md](state-management.md) - State tracking
- [environment-verification.md](environment-verification.md) - Multi-env verification
