# Error Classification

Errors fall into categories based on their recoverability and required response. This classification guides the
team lead's error handling.

## Error Categories

| Category           | Description                                          | Recovery             | Escalation                   |
|--------------------|------------------------------------------------------|----------------------|------------------------------|
| **Transient**      | Temporary failures that may resolve on retry         | Automatic retry      | After retry limit            |
| **Agent Failure**  | Teammate crashes, timeouts, or invalid output        | Re-assign task       | After `TASK_FAILURE_LIMIT`   |
| **Infrastructure** | Tests broken, env unavailable, pre-existing failures | Remediation loop     | After `REMEDIATION_ATTEMPTS` |
| **Configuration**  | Invalid plan, missing deps, ambiguous requirements   | User clarification   | Immediate                    |
| **Unrecoverable**  | Repeated failures, limits exceeded                   | Halt workflow        | Immediate                    |

---

## Transient Errors

Temporary failures that often resolve on retry.

### Examples

- Tool invocation timeout
- Network connectivity issue
- File system busy
- Rate limiting

### Recovery Strategy

Retry with exponential backoff (1s, 2s, 4s). After 3 retries, escalate to agent failure handling.

---

## Agent Failure Errors

Teammate did not produce valid output.

### Examples

- Teammate timeout
- Teammate crashed
- No recognizable message in mailbox
- Invalid message format
- Task ID mismatch

### Recovery Strategy

The team lead returns the task to `pending` status via `TaskUpdate({ status: "pending" })` so another developer
can be assigned it. Track failure count per task. After reaching `TASK_FAILURE_LIMIT`, escalate to unrecoverable.

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

The team lead sets `infrastructure_blocked = true` in its context and enters the remediation loop.
The team lead sends a remediation request to the `remediation` teammate via SendMessage.

### Remediation Escalation

If remediation exceeds `REMEDIATION_ATTEMPTS`, the team lead halts the workflow and asks the user for guidance.

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

The team lead asks the user for clarification directly. The task remains blocked until guidance is received.
See [escalation-specification.md](escalation-specification.md) for the clarification procedure.

---

## Unrecoverable Errors

Failures requiring human intervention.

### Examples

- Task exceeded `TASK_FAILURE_LIMIT`
- Remediation exceeded `REMEDIATION_ATTEMPTS`
- Circular dependency detected in plan
- Critical file missing

### Recovery Strategy

The team lead halts the workflow and informs the user. The shared task list preserves all task states, so
the session can be resumed after the user resolves the issue.

---

## Error Classification Logic

The team lead classifies errors based on indicators:

| Indicator | Classification |
|-----------|---------------|
| Timeout, network error, rate limit | Transient |
| Agent timeout, crash, parse failure | Agent failure |
| Test failure, lint error, type error (pre-existing) | Infrastructure |
| Test failure, lint error (introduced by developer) | Agent failure |
| Ambiguous requirement, missing info | Configuration |
| Limits exceeded | Unrecoverable |

---

## Error Response Summary

| Error Type     | First Response      | Escalation Path          |
|----------------|---------------------|--------------------------|
| Transient      | Retry with backoff  | -> Agent failure         |
| Agent failure  | Re-assign task      | -> Unrecoverable         |
| Infrastructure | Remediation loop    | -> Unrecoverable         |
| Configuration  | User clarification  | -> Blocks until resolved |
| Unrecoverable  | Halt workflow       | -> Human review          |
