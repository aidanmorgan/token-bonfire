# Infrastructure Remediation Loop

When `AUDIT_BLOCKED` or `INFRA_BLOCKED` is detected, the team lead enters the remediation loop. This loop continues
until either:

- Infrastructure is restored (HEALTHY)
- Maximum attempts exceeded (workflow fails)

## Remediation Loop Steps

1. **INFRASTRUCTURE BLOCKED** - AUDIT_BLOCKED or INFRA_BLOCKED message received
2. **PAUSE NEW ASSIGNMENTS** - Set infrastructure_blocked = true in team lead context
3. **MESSAGE REMEDIATION TEAMMATE** - Increment attempt counter
4. **AWAIT REMEDIATION_COMPLETE** - Check mailbox for completion message
5. **MESSAGE HEALTH AUDITOR** - Verify fix
6. **PARSE HEALTH AUDIT RESULT**:
    - **HEALTHY** -> RESTORE FLOW (blocked = false, attempt = 0, RESUME)
    - **UNHEALTHY** -> CHECK ATTEMPT LIMIT:
        - **< LIMIT** -> Go back to step 3
        - **>= LIMIT** -> WORKFLOW FAILED (human intervention required)

## Remediation Loop Procedure

### Step R1: Detect Infrastructure Block

Triggers:

- Developer messages `INFRA_BLOCKED: [task ID]`
- Auditor messages `AUDIT_BLOCKED: [task_id]` with pre-existing failures

The team lead sets `infrastructure_blocked = true` in its context, pauses new task assignments, and enters the
remediation loop.

### Step R2: Remediation Loop

The team lead iterates:

1. Increment `remediation_attempt_count`
2. If attempt count exceeds limit, escalate to user and halt
3. Message the remediation teammate via `SendMessage({ type: "message", recipient: "remediation", content: "...", summary: "Infrastructure issues for remediation" })` with the infrastructure issues
4. Check mailbox for `REMEDIATION_COMPLETE` message from remediation teammate
5. If no completion message received (crash/timeout), check attempt limit and retry or escalate
6. If completion received, message the health auditor via `SendMessage({ type: "message", recipient: "health-auditor", content: "...", summary: "Request health audit" })`
7. Check mailbox for health audit result:
   - `HEALTH_AUDIT: HEALTHY` -> Clear blocked flag, reset attempt counter, resume normal operation
   - `HEALTH_AUDIT: UNHEALTHY` -> Loop continues to next iteration
   - Unexpected response -> Treat as UNHEALTHY, loop continues

### Step R3: Resume Normal Operation

After `HEALTH_AUDIT: HEALTHY`:

- Clear `infrastructure_blocked` flag
- Clear infrastructure issues list
- Reset `remediation_attempt_count` to 0
- Resume task assignments - team lead can assign new tasks to requesting developers

### Step R4: User Response Handler (Remediation Context)

When the remediation loop is exhausted, the team lead asks the user for guidance:

- **Retry with different approach**: Reset attempt counter, re-enter remediation loop with user guidance
- **Mark infrastructure as healthy (override)**: Force healthy status, resume operations
- **Halt workflow**: Stop all work, do not continue

## Remediation Detection Patterns

| Message                    | Source              | Meaning                               |
|----------------------------|---------------------|---------------------------------------|
| `INFRA_BLOCKED: [task]`   | Developer              | Cannot run verification commands      |
| `AUDIT_BLOCKED: [task_id]`| Auditor             | Pre-existing failures detected        |
| `REMEDIATION_COMPLETE`    | Remediation         | Fixes applied, ready for health check |
| `HEALTH_AUDIT: HEALTHY`   | Health Auditor      | All verifications pass, resume work   |
| `HEALTH_AUDIT: UNHEALTHY` | Health Auditor      | Still broken, loop again              |

## Remediation State Tracking

The team lead tracks remediation state in its context:

- `infrastructure_blocked`: Whether assignments are halted
- `infrastructure_issues`: List of reported issues
- `remediation_attempt_count`: Current attempt number (max from config)

## Cross-References

- Error classification and routing: [error-classification.md](error-classification.md)
- Team architecture: [communication-protocol.md](communication-protocol.md)
- Communication messages: [communication-protocol.md](communication-protocol.md)
