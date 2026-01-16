# Infrastructure Remediation

When a developer or auditor reports any of these conditions, the coordinator must halt new assignments:

1. Tests cannot run due to missing dependencies, broken build, or environment issues
2. Linters were skipped because the tool is unavailable or misconfigured
3. Static analysis was skipped because the tool is unavailable or misconfigured
4. Devcontainer is unavailable and Linux-specific verification cannot complete
5. Pre-existing test failures unrelated to the current task block verification
6. Pre-existing linter errors unrelated to the current task block verification
7. Pre-existing static analysis errors unrelated to the current task block verification

## Remediation Procedure

1. Pause all new task assignments immediately. In-progress developers may continue implementation but cannot complete
   until infrastructure is restored.

2. Spawn a remediation agent:

```
Task tool parameters:
  model: [from AGENT_MODELS.remediation]
  subagent_type: "remediation"
  prompt: |
    [Include: Remediation Agent Definition]

    ---

    Infrastructure Remediation

    Problem: [specific issue reported by developer or auditor]
    Type: [tool_unavailable | pre_existing_failures]
    Affected: [list of blocked developers/auditors]

    [Include: Environment Execution Instructions]

    [Include: Remediation References]

    AVAILABLE SPECIALISTS:
    {{#if specialized_agents}}
    The following specialists are available to assist with domain-specific remediation.

    {{#each specialized_agents}}
    - **{{this.agent_type}}** ({{this.domain}}):
      Capabilities: {{this.capabilities}}
    {{/each}}
    {{else}}
    No specialists available for this plan.
    {{/if}}

    Goal: Restore the codebase to a clean state where all tests pass, linters report zero errors, and static analysis reports zero errors IN ALL ENVIRONMENTS.

    Acceptance Criteria (must pass in ALL environments unless Environment is specified):
    {{#each VERIFICATION_COMMANDS}}
    - {{this.check}} [Environment: {{this.environment || "ALL"}}]: `{{this.command}}` exits {{this.exit_code}}
    {{/each}}

    For pre-existing failures: Fix the failing tests or code, do not skip or disable them.

    Do not proceed to other work. The codebase must be clean in ALL environments before development continues.
```

Log event: `remediation_dispatched` with `issue_type`, `issue_details`, and `attempt_number`.

3. Wait for the remediation agent to report completion before spawning the health auditor.

4. Spawn a health auditor:

```
Task tool parameters:
  model: [from AGENT_MODELS.health_auditor]
  subagent_type: "auditor"
  prompt: |
    [Include: Health Auditor Agent Definition]

    ---

    Codebase Health Audit

    Verify the codebase is in a clean state after remediation IN ALL ENVIRONMENTS.

    [Include: Environment Execution Instructions]

    [Include: Auditor References]

    Checks (must pass in ALL environments unless Environment is specified):
    {{#each VERIFICATION_COMMANDS}}
    - {{this.check}} [Environment: {{this.environment || "ALL"}}]: `{{this.command}}` exits {{this.exit_code}}
    {{/each}}

    Report HEALTHY or UNHEALTHY with specific failures PER ENVIRONMENT.
```

Log event: `health_audit_dispatched` with `attempt_number`.

5. If UNHEALTHY: increment remediation attempt counter and spawn another remediation agent
6. If attempts reach `{{REMEDIATION_ATTEMPTS}}`: fail workflow and persist state for human review
7. If HEALTHY: reset attempt counter to 0, clear infrastructure block, resume normal operation

## Remediation Loop Limit

Maximum `{{REMEDIATION_ATTEMPTS}}` attempts. Each developer-then-auditor cycle counts as one attempt. The counter resets
to 0 when the codebase becomes healthy.

## Output Formats

**Infrastructure block:**

```
INFRASTRUCTURE BLOCKED

Reported by: [developer agent ID]
Issue: [specific problem]
Blocked developers: [list]

Spawning remediation agent...
All new assignments paused until infrastructure restored.
```

**Remediation attempt:**

```
REMEDIATION ATTEMPT [N]/{{REMEDIATION_ATTEMPTS}}

Remediation agent completed.
Spawning health auditor...
```

**Health audit failure:**

```
HEALTH_AUDIT: UNHEALTHY - Attempt [N]/{{REMEDIATION_ATTEMPTS}}

Failures:
- [specific failure]
- [specific failure]

Spawning remediation agent for attempt [N+1]...
```

**Infrastructure restored:**

```
INFRASTRUCTURE RESTORED

Fixed: [what was fixed]
Verification:
{{#each VERIFICATION_COMMANDS}}
- {{this.check}}: PASS
{{/each}}

Remediation attempts used: [N]/{{REMEDIATION_ATTEMPTS}}
Resetting remediation_attempt_count to 0.
Resuming normal operation with {{ACTIVE_DEVELOPERS}} parallel developers.
```

**Remediation failure:**

```
WORKFLOW FAILED - REMEDIATION LIMIT EXCEEDED

{{REMEDIATION_ATTEMPTS}} remediation attempts failed to restore codebase health.

Last failures:
- [specific failure]
- [specific failure]

Human intervention required.
State persisted to: {{STATE_FILE}}
```
