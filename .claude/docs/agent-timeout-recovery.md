# Agent Recovery

This document covers timeout handling, crash recovery, and disagreement detection for all agent types.

**Related Documents:**

- [task-dispatch.md](task-dispatch.md) - Task dispatch procedures
- [review-audit-flow.md](review-audit-flow.md) - Review and audit flow
- [state-management.md](state-management.md) - State tracking

---

## Timeout Handling

### Timeout Values by Agent Type

| Agent Type     | Default Timeout | Rationale                   |
|----------------|-----------------|-----------------------------|
| Developer      | 15 min          | Complex implementation work |
| Critic         | 10 min          | Code review is focused      |
| Auditor        | 10 min          | Verification is structured  |
| Remediation    | 5 min           | Targeted fixes              |
| Health Auditor | 5 min           | Just run checks             |

### Timeout Tracking

```python
# On dispatch, record start time in state
in_progress_tasks.append({
    "task_id": task_id,
    "developer_id": agent_id,
    "status": "implementing",
    "dispatched_at": datetime.now().isoformat(),
    "timeout_ms": AGENT_TIMEOUT
})

# Periodic check (during slot fill or await)
def check_agent_timeouts():
    now = datetime.now()
    for task in in_progress_tasks:
        dispatch_time = datetime.fromisoformat(task["dispatched_at"])
        elapsed_ms = (now - dispatch_time).total_seconds() * 1000
        if elapsed_ms > task["timeout_ms"]:
            handle_agent_timeout(task["task_id"], task["developer_id"])
```

---

## Developer Timeout/Crash

When a Developer agent times out or crashes:

```python
def handle_developer_timeout(task_id: str, developer_id: str):
    """Handle Developer agent timeout or crash."""

    log_event("developer_timeout", task_id=task_id, developer_id=developer_id)

    # Remove from active developers
    del active_developers[developer_id]

    # Check failure count
    task_failures[task_id] = task_failures.get(task_id, 0) + 1

    if task_failures[task_id] >= TASK_FAILURE_LIMIT:
        log_event("workflow_failed", reason="developer_crash_limit", task_id=task_id)
        # Mark task as failed, don't re-dispatch
    else:
        # Re-dispatch with same context
        dispatch_developer(task_id, attempt_count=task_failures[task_id])
        log_event("developer_redispatched",
                  task_id=task_id,
                  attempt=task_failures[task_id])
```

---

## Critic Timeout/Crash

When a Critic agent times out or crashes:

```python
def handle_critic_timeout(task_id: str, critic_id: str):
    """Handle Critic agent timeout or crash."""

    log_event("critic_timeout", task_id=task_id, critic_id=critic_id)

    # Remove from active critics
    del active_critics[critic_id]
    pending_critique.remove(task_id)

    # Check failure count
    critique_failures[task_id] = critique_failures.get(task_id, 0) + 1

    if critique_failures[task_id] >= TASK_FAILURE_LIMIT:
        log_event("workflow_failed", reason="critic_crash_limit", task_id=task_id)
    else:
        # Re-dispatch Critic with same context
        dispatch_critic(task_id)
        log_event("critic_redispatched",
                  task_id=task_id,
                  attempt=critique_failures[task_id])
```

---

## Auditor Timeout/Crash

When an Auditor agent times out or crashes:

```python
def handle_auditor_timeout(task_id: str, auditor_id: str):
    """Handle Auditor agent timeout or crash."""

    log_event("auditor_timeout", task_id=task_id, auditor_id=auditor_id)

    # Remove from active auditors
    del active_auditors[auditor_id]
    pending_audit.remove(task_id)

    # Check failure count
    audit_failures[task_id] = audit_failures.get(task_id, 0) + 1

    if audit_failures[task_id] >= TASK_FAILURE_LIMIT:
        log_event("workflow_failed", reason="auditor_crash_limit", task_id=task_id)
    else:
        # Re-dispatch Auditor with same context
        dispatch_auditor(task_id)
        log_event("auditor_redispatched",
                  task_id=task_id,
                  attempt=audit_failures[task_id])
```

---

## Agent Crash Recovery

```python
if result.status == "failed":
    log_event("agent_crashed", agent_id=result.agent_id, task_id=task_id)

    # Check if recoverable
    if attempt_count < TASK_FAILURE_LIMIT:
        # Re-dispatch
        dispatch_agent(task_id, agent_type, attempt_count + 1)
    else:
        # Escalate
        log_event("workflow_failed", reason="agent_crash_limit", task_id=task_id)
```

---

## Critic/Auditor Disagreement Detection

When a Critic passes code that the Auditor subsequently fails, this may indicate:

1. Critic missed a quality issue
2. Acceptance criteria interpretation mismatch
3. Verification environment issues

### Detection

```python
def detect_review_audit_disagreement(task_id: str, audit_result: dict) -> bool:
    """Check if Auditor failed something that Critic passed."""

    if audit_result['signal'] != 'AUDIT_FAILED':
        return False

    # Get the task's review history
    task_history = get_task_history(task_id)

    # Check if this task was just reviewed (REVIEW_PASSED) before audit
    last_review = get_last_review_result(task_history)
    if last_review and last_review['signal'] == 'REVIEW_PASSED':
        return True

    return False
```

### On Disagreement Detected

```python
def handle_review_audit_disagreement(
    task_id: str,
    critic_assessment: dict,
    audit_failures: dict
):
    """Handle case where Critic passed but Auditor failed."""

    log_event("review_audit_disagreement",
              task_id=task_id,
              critic_passed=critic_assessment,
              auditor_failed=audit_failures)

    # Categorize the disagreement
    disagreement_type = categorize_disagreement(critic_assessment, audit_failures)

    if disagreement_type == 'acceptance_criteria':
        # Auditor found criteria not met - this is expected (different roles)
        # No special handling needed, normal AUDIT_FAILED flow
        pass

    elif disagreement_type == 'code_quality':
        # Auditor found quality issues Critic missed - flag for learning
        log_event("critic_missed_quality_issue",
                  task_id=task_id,
                  issues=audit_failures['issues'])

    elif disagreement_type == 'environment_specific':
        # Different results in different environments
        handle_environment_disagreement(task_id, audit_failures)
```

### Disagreement Categories

| Type                   | Description                          | Handling                              |
|------------------------|--------------------------------------|---------------------------------------|
| `acceptance_criteria`  | Criteria not met (Auditor's domain)  | Normal flow - not a true disagreement |
| `code_quality`         | Quality issue Critic missed          | Log for Critic improvement feedback   |
| `environment_specific` | Passes in some envs, fails in others | See Environment Disagreement section  |

### Learning from Disagreements

Track disagreement patterns to improve Critic effectiveness:

```python
# In state, track disagreement history
disagreement_history = [
    {
        "task_id": "task-1-1",
        "critic_assessment": {...},
        "audit_failure": {...},
        "disagreement_type": "code_quality",
        "issue_category": "error_handling"
    }
]

# When patterns emerge, feed back to Critic prompts
def enhance_critic_prompt_from_patterns():
    """Add learned patterns to Critic's focus areas."""

    common_misses = analyze_disagreement_history()

    if common_misses:
        return f"""
        ADDITIONAL FOCUS AREAS (from historical patterns):
        The following issues have been missed in past reviews:
        {format_common_misses(common_misses)}

        Pay special attention to these areas.
        """
    return ""
```

---

## Environment Disagreement Protocol

When verification passes in some environments but fails in others.

### Detection

```python
def detect_environment_disagreement(
    verification_results: dict[str, dict]
) -> dict | None:
    """
    Check for environment-specific failures.
    Returns disagreement details or None if no disagreement.
    """

    passed_envs = []
    failed_envs = []

    for env_name, result in verification_results.items():
        if result['status'] == 'pass':
            passed_envs.append(env_name)
        else:
            failed_envs.append({
                'env': env_name,
                'check': result['check'],
                'error': result.get('error', 'Unknown')
            })

    if passed_envs and failed_envs:
        return {
            'type': 'environment_disagreement',
            'passed_in': passed_envs,
            'failed_in': failed_envs
        }

    return None
```

### On Environment Disagreement

```python
def handle_environment_disagreement(
    task_id: str,
    disagreement: dict
):
    """Handle environment-specific verification failures."""

    log_event("environment_disagreement",
              task_id=task_id,
              passed=disagreement['passed_in'],
              failed=disagreement['failed_in'])

    # Format for developer rework prompt
    env_context = format_environment_context(disagreement)

    # Dispatch developer with environment-specific context
    dispatch_developer_rework(
        task_id,
        issues={
            'type': 'environment_specific',
            'context': env_context,
            'failed_environments': disagreement['failed_in']
        }
    )
```

### Common Environment Disagreement Causes

| Cause                | Detection                | Resolution                   |
|----------------------|--------------------------|------------------------------|
| Missing dependencies | Package not in some envs | Add to all env configs       |
| Path differences     | Hardcoded paths          | Use relative/env-aware paths |
| Version mismatches   | Different lib versions   | Pin versions consistently    |
| Platform-specific    | OS-specific code         | Add platform guards          |

---

## Error Recovery Summary

| Error Type                | Detection                     | Recovery Action               |
|---------------------------|-------------------------------|-------------------------------|
| Agent timeout             | Elapsed > timeout_ms          | Re-dispatch (up to limit)     |
| Agent crash               | status == "failed"            | Re-dispatch (up to limit)     |
| Parse failure             | No recognized signal          | Request checkpoint            |
| State corruption          | JSON parse error              | Restore from backup           |
| Review/audit disagreement | Critic passed, Auditor failed | Log pattern, normal flow      |
| Environment disagreement  | Pass in some, fail in others  | Developer rework with context |

---

## Cross-References

- [task-dispatch.md](task-dispatch.md) - Task dispatch procedures
- [review-audit-flow.md](review-audit-flow.md) - Review and audit flow
- [developer-rework.md](developer-rework.md) - Rework dispatch
- [state-management.md](state-management.md) - State tracking
- [recovery-procedures.md](recovery-procedures.md) - General recovery
- [environment-verification.md](environment-verification.md) - Multi-env verification
