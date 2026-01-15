# Error Classification

Errors fall into categories based on their recoverability and required response. This classification guides the coordinator's error handling.

## Error Categories

| Category | Description | Recovery | Escalation |
|----------|-------------|----------|------------|
| **Transient** | Temporary failures that may resolve on retry | Automatic retry | After retry limit |
| **Agent Failure** | Agent crashes, timeouts, or invalid output | Re-dispatch task | After `TASK_FAILURE_LIMIT` |
| **Infrastructure** | Tests broken, env unavailable, pre-existing failures | Remediation loop | After `REMEDIATION_ATTEMPTS` |
| **Configuration** | Invalid plan, missing deps, ambiguous requirements | Divine intervention | Immediate |
| **Unrecoverable** | Repeated failures, limits exceeded | Halt workflow | Immediate |

---

## Transient Errors

Temporary failures that often resolve on retry.

### Examples
- Tool invocation timeout
- Network connectivity issue
- File system busy
- Rate limiting

### Recovery Strategy

```python
def handle_transient_error(error, context):
    """Handle transient errors with exponential backoff."""

    retry_count = context.get('retry_count', 0)
    max_retries = 3

    if retry_count >= max_retries:
        return escalate_to_agent_failure(error, context)

    delay = 2 ** retry_count  # 1s, 2s, 4s
    log_event("transient_error_retry",
              error_type=error.type,
              retry=retry_count + 1,
              delay_seconds=delay)

    sleep(delay)
    return retry_operation(context, retry_count + 1)
```

### Events
| Event | Fields |
|-------|--------|
| `transient_error_retry` | error_type, retry, delay_seconds |
| `transient_error_resolved` | error_type, total_retries |
| `transient_error_escalated` | error_type, reason |

---

## Agent Failure Errors

Agent did not produce valid output.

### Examples
- Agent timeout (exceeded `AGENT_TIMEOUT`)
- Agent crashed (Task tool error)
- No recognizable signal in output
- Invalid signal format
- Task ID mismatch

### Recovery Strategy

```python
def handle_agent_failure(error, task_id, agent_type):
    """Handle agent failures with re-dispatch."""

    failures = failed_attempts.get(task_id, 0) + 1
    failed_attempts[task_id] = failures

    if failures >= TASK_FAILURE_LIMIT:
        return escalate_to_unrecoverable(
            f"Task {task_id} failed {failures} times",
            task_id
        )

    log_event("agent_failure",
              task_id=task_id,
              agent_type=agent_type,
              error_type=error.type,
              attempt=failures)

    # Return task to queue for re-dispatch
    available_tasks.append(task_id)
    return {'action': 'redispatch', 'task_id': task_id}
```

### Events
| Event | Fields |
|-------|--------|
| `agent_failure` | task_id, agent_type, error_type, attempt |
| `agent_timeout` | agent_id, task_id, elapsed_ms |
| `agent_crashed` | agent_id, task_id, error_message |
| `signal_parse_failure` | agent_id, task_id, raw_output_sample |

---

## Infrastructure Errors

Systemic issues blocking all development.

### Examples
- Pre-existing test failures
- Linter/type checker errors in baseline code
- Devcontainer unavailable
- Missing dependencies
- Environment disagreement (passes in one env, fails in another)

### Recovery Strategy

```python
def handle_infrastructure_error(error, reported_by):
    """Handle infrastructure errors with remediation loop."""

    infrastructure_blocked = True
    infrastructure_issue = error.details

    log_event("infrastructure_blocked",
              issue=error.details,
              reported_by=reported_by)

    # Enter remediation loop (see infrastructure-remediation.md)
    return enter_remediation_loop(error.details)
```

### Remediation Escalation

If remediation exceeds `REMEDIATION_ATTEMPTS`:

```python
def escalate_remediation_failure():
    """Escalate when remediation loop exhausted."""

    log_event("workflow_failed",
              reason="remediation_limit_exceeded",
              attempts=REMEDIATION_ATTEMPTS,
              last_issue=infrastructure_issue)

    output(f"""
WORKFLOW FAILED - REMEDIATION LIMIT EXCEEDED

Infrastructure could not be restored after {REMEDIATION_ATTEMPTS} attempts.

Last issue: {infrastructure_issue}
State preserved: {STATE_FILE}
Event log: {EVENT_LOG_FILE}

Human intervention required.
""")
```

### Events
| Event | Fields |
|-------|--------|
| `infrastructure_blocked` | issue, reported_by |
| `remediation_dispatched` | attempt, issue |
| `infrastructure_restored` | attempts_used |

---

## Configuration Errors

Issues requiring human clarification.

### Examples
- Ambiguous acceptance criteria
- Conflicting requirements
- Missing information in plan
- Scope unclear
- Multiple valid interpretations

### Recovery Strategy

```python
def handle_configuration_error(error, task_id):
    """Handle configuration errors with divine intervention."""

    question = formulate_clarification_question(error)

    pending_divine_questions.append({
        'task_id': task_id,
        'question': question,
        'options': error.options if hasattr(error, 'options') else [],
        'context': error.context
    })

    log_event("configuration_error",
              task_id=task_id,
              error_type=error.type)

    # Invoke divine intervention protocol
    return invoke_divine_clarification(task_id, question, error.options)
```

### Events
| Event | Fields |
|-------|--------|
| `configuration_error` | task_id, error_type |
| `agent_seeks_guidance` | agent_id, task_id, question |
| `divine_response_received` | task_id, response |

---

## Unrecoverable Errors

Failures requiring human intervention.

### Examples
- Task exceeded `TASK_FAILURE_LIMIT`
- Remediation exceeded `REMEDIATION_ATTEMPTS`
- State corruption unrecoverable from event log
- Circular dependency detected in plan
- Critical file missing

### Recovery Strategy

```python
def handle_unrecoverable_error(error, context):
    """Handle unrecoverable errors by halting workflow."""

    # Persist state for debugging
    save_state_atomic(state)

    log_event("workflow_failed",
              reason=error.type,
              details=error.details,
              context=context)

    output(f"""
WORKFLOW FAILED - {error.type.upper()}

{error.details}

State preserved: {STATE_FILE}
Event log: {EVENT_LOG_FILE}

Review event log for failure history.
Human intervention required to proceed.
""")

    return {'action': 'halt', 'reason': error.type}
```

### Events
| Event | Fields |
|-------|--------|
| `workflow_failed` | reason, details, last_state |

---

## Error Classification Logic

```python
def classify_error(error) -> str:
    """Classify error into category for appropriate handling."""

    # Check for transient indicators
    if error.type in ('timeout', 'network_error', 'rate_limit'):
        return 'transient'

    # Check for agent failure indicators
    if error.type in ('agent_timeout', 'agent_crash', 'parse_failure', 'signal_missing'):
        return 'agent_failure'

    # Check for infrastructure indicators
    if error.type in ('test_failure', 'lint_error', 'type_error', 'env_unavailable'):
        if is_pre_existing(error):
            return 'infrastructure'
        return 'agent_failure'  # Agent introduced the error

    # Check for configuration indicators
    if error.type in ('ambiguous_requirement', 'missing_info', 'scope_unclear'):
        return 'configuration'

    # Check for limit exceeded
    if error.type in ('task_limit_exceeded', 'remediation_limit_exceeded'):
        return 'unrecoverable'

    # Default to agent failure (recoverable)
    return 'agent_failure'
```

---

## Error Response Summary

| Error Type | First Response | Escalation Path |
|------------|----------------|-----------------|
| Transient | Retry with backoff | → Agent failure |
| Agent failure | Re-dispatch task | → Unrecoverable |
| Infrastructure | Remediation loop | → Unrecoverable |
| Configuration | Divine intervention | → Blocks until resolved |
| Unrecoverable | Halt workflow | → Human review |
