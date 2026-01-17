# Infrastructure Remediation Loop

When `AUDIT_BLOCKED` or `INFRA_BLOCKED` is detected, the coordinator enters the remediation loop. This loop continues
until either:

- Infrastructure is restored (HEALTHY)
- Maximum attempts exceeded (workflow fails)

## Remediation Loop Steps

1. **INFRASTRUCTURE BLOCKED** - AUDIT_BLOCKED or INFRA_BLOCKED signal detected
2. **PAUSE NEW ASSIGNMENTS** - Set infrastructure_blocked = true
3. **DISPATCH REMEDIATION AGENT** - Increment attempt counter
4. **AWAIT REMEDIATION_COMPLETE** - Parse signal
5. **DISPATCH HEALTH_AUDITOR** - Verify fix
6. **PARSE HEALTH_AUDIT RESULT**:
    - **HEALTHY** → RESTORE FLOW (blocked = false, attempt = 0, RESUME)
    - **UNHEALTHY** → CHECK ATTEMPT LIMIT:
        - **< LIMIT** → Go back to step 3
        - **>= LIMIT** → WORKFLOW FAILED (human intervention required)

## Remediation Loop Procedure

### Step R1: Detect Infrastructure Block

Triggers:

- Developer signals `INFRA_BLOCKED: [task ID]`
- Auditor signals `AUDIT_BLOCKED: [task_id]` with pre-existing failures

```python
def handle_infrastructure_block(issue_details, reporter_id):
    infrastructure_blocked = True
    infrastructure_issues.append(issue_details)

    # Pause new assignments
    log_event("infrastructure_blocked", issue=issue_details, reported_by=reporter_id)
    save_state()

    # Enter remediation loop
    remediation_loop()
```

### Step R2: Remediation Loop

```python
def remediation_loop():
    while infrastructure_blocked:
        remediation_attempt_count += 1

        if remediation_attempt_count > REMEDIATION_ATTEMPTS:
            log_event("workflow_failed", reason="remediation_limit_exceeded")
            output("WORKFLOW FAILED - REMEDIATION LIMIT EXCEEDED")
            return  # Human intervention required

        # Dispatch remediation agent
        output(f"REMEDIATION ATTEMPT {remediation_attempt_count}/{REMEDIATION_ATTEMPTS}")
        remediation_agent_id = dispatch_remediation_agent(infrastructure_issues)
        log_event("remediation_dispatched", attempt=remediation_attempt_count)

        # Wait for remediation completion
        remediation_result = await_agent(remediation_agent_id)

        if "REMEDIATION_COMPLETE" not in remediation_result:
            # Remediation agent failed unexpectedly (crash, timeout, malformed output)
            log_event("remediation_failed", reason="no_completion_signal",
                      attempt=remediation_attempt_count)

            # CRITICAL: Check attempt limit HERE to prevent infinite loop
            # (Don't wait for health audit - agent already failed)
            if remediation_attempt_count > REMEDIATION_ATTEMPTS:
                log_event("remediation_exhausted",
                          reason="agent_failures_without_completion",
                          attempt_count=remediation_attempt_count)
                output("REMEDIATION EXHAUSTED - Agents failed to signal completion")
                # Escalate to divine intervention
                escalate_to_divine(
                    question="Remediation agents failed {count} times without completing. Infrastructure issue: {issue}".format(
                        count=remediation_attempt_count,
                        issue=infrastructure_issues
                    ),
                    options=["Retry with different approach", "Mark infrastructure as healthy (override)", "Halt workflow"]
                )
                return  # Exit loop, await human guidance

            # Otherwise, retry with next attempt (counter already incremented at loop start)
            continue

        # Dispatch health auditor to verify
        health_auditor_id = dispatch_health_auditor()
        log_event("health_audit_dispatched", attempt=remediation_attempt_count)

        # Wait for health audit
        health_result = await_agent(health_auditor_id)

        if "HEALTH_AUDIT: HEALTHY" in health_result:
            # Success! Restore normal operation
            # Log BEFORE resetting counter to capture actual attempts used
            log_event("infrastructure_restored", attempts_used=remediation_attempt_count)

            infrastructure_blocked = False
            infrastructure_issues = []
            remediation_attempt_count = 0

            output("INFRASTRUCTURE RESTORED")
            return  # Exit loop, resume normal operation

        elif "HEALTH_AUDIT: UNHEALTHY" in health_result:
            # Still broken, loop continues
            log_event("health_audit_fail", attempt=remediation_attempt_count)
            output(f"HEALTH_AUDIT: UNHEALTHY - Attempt {remediation_attempt_count}/{REMEDIATION_ATTEMPTS}")
            # Loop continues to next iteration

        else:
            # Unexpected health audit response - treat as failure
            log_event("health_audit_unexpected",
                      attempt=remediation_attempt_count,
                      response_summary=health_result[:200])
            output(f"HEALTH_AUDIT: UNEXPECTED RESPONSE - Treating as UNHEALTHY")
            # Loop continues to next iteration
```

### Step R3: Resume Normal Operation

After `HEALTH_AUDIT: HEALTHY`:

```python
# Clear infrastructure block
infrastructure_blocked = False
infrastructure_issues = []
remediation_attempt_count = 0

# Resume task assignments
output(f"Resuming normal operation with {ACTIVE_DEVELOPERS} parallel developers.")

# Fill actor slots immediately
fill_actor_slots()
```

### Step R4: Divine Response Handler (Remediation Context)

When divine intervention was requested from remediation loop (via `escalate_to_divine()`), the coordinator must handle
the response appropriately:

```python
def handle_remediation_divine_response(response: dict):
    """Handle divine response for remediation escalation."""

    option_selected = response['selected_option']
    task_context = response.get('context', {})

    if option_selected == "Retry with different approach":
        # Reset attempt counter and retry with human guidance
        remediation_attempt_count = 0

        log_event("remediation_divine_retry",
                  guidance=response.get('additional_guidance', ''))

        # Re-enter remediation loop with divine guidance appended
        remediation_loop(divine_guidance=response.get('additional_guidance'))

    elif option_selected == "Mark infrastructure as healthy (override)":
        # Human override - force healthy status
        log_event("remediation_divine_override",
                  reason="human_marked_healthy")

        infrastructure_blocked = False
        infrastructure_issues = []
        remediation_attempt_count = 0

        output("INFRASTRUCTURE MARKED HEALTHY (DIVINE OVERRIDE)")
        fill_actor_slots()

    elif option_selected == "Halt workflow":
        # Human chose to stop the workflow
        log_event("workflow_halted",
                  reason="divine_decision")

        output("WORKFLOW HALTED BY DIVINE DECISION")
        # Do not fill slots, do not continue
        return

    else:
        # Unknown option - treat as retry with guidance
        log_event("remediation_divine_unknown_option",
                  option=option_selected)
        remediation_loop(divine_guidance=str(response))
```

**CRITICAL**: This handler must be called by the coordinator when a divine response arrives and
`pending_divine_questions` contains a remediation-related question. Check the question context to route appropriately.

## Remediation Detection Patterns

| Signal                     | Source            | Meaning                               |
|----------------------------|-------------------|---------------------------------------|
| `INFRA_BLOCKED: [task]`    | Developer         | Cannot run verification commands      |
| `AUDIT_BLOCKED: [task_id]` | Auditor           | Pre-existing failures detected        |
| `REMEDIATION_COMPLETE`     | Remediation Agent | Fixes applied, ready for health check |
| `HEALTH_AUDIT: HEALTHY`    | Health Auditor    | All verifications pass, resume work   |
| `HEALTH_AUDIT: UNHEALTHY`  | Health Auditor    | Still broken, loop again              |

## Remediation State Fields

Track these in `STATE_FILE`:

```json
{
  "infrastructure_blocked": true,
  "infrastructure_issues": [
    "15 test failures in tests/unit/",
    "3 type errors in src/core/"
  ],
  "active_remediation": "remediation-agent-1",
  "remediation_attempt_count": 2,
  "remediation_history": [
    {
      "attempt": 1,
      "fixes_applied": ["fixed import in foo.py"],
      "health_result": "UNHEALTHY",
      "remaining_failures": 8
    },
    {
      "attempt": 2,
      "fixes_applied": ["updated test fixtures"],
      "health_result": "pending"
    }
  ]
}
```

## Cross-References

- Signal formats: [signal-specification.md](signal-specification.md)
- State management: [state-management.md](state-management.md)
- Recovery procedures: [recovery-procedures.md](recovery-procedures.md)
