# Signal Specification

All agent-to-coordinator signals are defined here. **This is the single source of truth.**

## Workflow Overview

```
Developer → READY_FOR_REVIEW → Critic → REVIEW_PASSED → Auditor → AUDIT_PASSED → Complete
                                    ↓                        ↓
                              REVIEW_FAILED             AUDIT_FAILED
                                    ↓                        ↓
                              (back to Developer)    (back to Developer)
```

## Signal Detection Rules

| Rule               | Requirement                        | Example                                |
|--------------------|------------------------------------|----------------------------------------|
| Line position      | Signal MUST start at column 0      | `READY_FOR_REVIEW: task-1` (correct)   |
| Signal name        | Use EXACT name from this spec      | `AUDIT_PASSED` not `Audit Passed`      |
| Separator          | Use colon and space after signal   | `READY_FOR_REVIEW: task-1`             |
| Placement          | Signal at END of response          | After all explanatory text             |
| No false positives | Don't use signal keywords in prose | Don't write "this is READY_FOR_REVIEW" |

---

## Developer Signals

### READY_FOR_REVIEW

```
^READY_FOR_REVIEW:\s*(\S+)
```

**Usage**: Developer has completed implementation and requests **Critic review** (NOT audit yet).

**Triggers**: Orchestrator dispatches Critic agent.

**Format**:

```
READY_FOR_REVIEW: [task_id]

Files Modified:
- [file1]: [change description]
- [file2]: [change description]

Tests Written:
- [test_file]: [what it tests]

Verification Results (self-verified):
- [check]: PASS ([environment])

Summary: [brief description of implementation]
```

### TASK_INCOMPLETE

```
^TASK_INCOMPLETE:\s*(\S+)
```

**Usage**: Developer cannot complete task (missing info, blocked).

**Triggers**: Orchestrator logs event, fills actor slots with other work.

**Format**:

```
TASK_INCOMPLETE: [task_id]

Blocker: [description of what's missing]
Attempted: [what was tried]
Needed: [what would unblock]
```

### INFRA_BLOCKED

```
^INFRA_BLOCKED:\s*(\S+)
```

**Usage**: Infrastructure issue prevents task completion.

**Triggers**: Orchestrator enters remediation loop.

**Format**:

```
INFRA_BLOCKED: [task_id]

Issue: [specific infrastructure problem]
Command: [command that failed]
Output: [error output]
Environment: [which environment]
```

---

## Auditor Signals

### AUDIT_PASSED

```
^AUDIT_PASSED:\s*(\S+)
```

**Usage**: All acceptance criteria verified. **Task is now COMPLETE.**

**Triggers**: Orchestrator marks task complete, unblocks dependents.

**Format**:

```
AUDIT_PASSED: [task_id]

Verification Results:
- [criterion_1]: VERIFIED - [evidence]
- [criterion_2]: VERIFIED - [evidence]

Commands Executed:
- [check] ([env]): PASS
- [check] ([env]): PASS

Summary: [brief conclusion]
```

### AUDIT_FAILED

```
^AUDIT_FAILED:\s*(\S+)
```

**Usage**: One or more acceptance criteria not met. Requires rework.

**Triggers**: Orchestrator sends issues to Developer for rework.

**Format**:

```
AUDIT_FAILED: [task_id]

Failed Criteria:
- [criterion]: FAILED - [reason]

Issues Found:
- [file]:[line]: [issue description]

Required Fixes:
- [concrete action]

Passing Criteria:
- [what passed]
```

### AUDIT_BLOCKED

```
^AUDIT_BLOCKED:\s*(\S+)
```

**Usage**: Pre-existing failures prevent audit completion.

**Triggers**: Orchestrator enters remediation loop.

**Format**:

```
AUDIT_BLOCKED: [task_id]

Pre-existing Failures:
- [failure not caused by this task]

Cannot proceed with audit until infrastructure is fixed.
```

---

## Critic Signals

The Critic reviews code quality between Developer and Auditor.

### REVIEW_PASSED

```
^REVIEW_PASSED:\s*(\S+)
```

**Usage**: Code has passed quality review and is ready for formal audit.

**Triggers**: Orchestrator dispatches Auditor agent.

**Format**:

```
REVIEW_PASSED: [task_id]

Files Reviewed:
- [file1]
- [file2]

Quality Assessment:
- Code style: COMPLIANT
- Error handling: ADEQUATE
- Naming: CONSISTENT
- Architecture: ALIGNED

Summary: [brief assessment - what was done well]
```

### REVIEW_FAILED

```
^REVIEW_FAILED:\s*(\S+)
```

**Usage**: Code has quality issues that must be fixed before audit.

**Triggers**: Orchestrator sends issues to Developer for rework.

**Format**:

```
REVIEW_FAILED: [task_id]

Files Reviewed:
- [file1]
- [file2]

Issues Found:
- [file]:[line]: [issue description]
- [file]:[line]: [issue description]

Required Fixes:
- [concrete action]
- [concrete action]

Priority: [HIGH | MEDIUM | LOW]

Developer: Please address all issues above and signal READY_FOR_REVIEW when complete.
```

**Note**: Critic focuses purely on code quality. Acceptance criteria verification is the Auditor's responsibility.

---

## Business Analyst Signals

### EXPANDED_TASK_SPECIFICATION

```
^EXPANDED_TASK_SPECIFICATION:\s*(\S+)
```

**Usage**: BA has expanded an underspecified task.

**Format**:

```
EXPANDED_TASK_SPECIFICATION: [task_id]
Confidence: [HIGH | MEDIUM | LOW]

Original: [original description]

Expanded Specification:
[detailed specification]

Acceptance Criteria:
- [ ] [criterion 1]
- [ ] [criterion 2]

Technical Approach:
[recommended approach]

Target Files:
- [file paths]
```

---

## Remediation Signals

### REMEDIATION_COMPLETE

```
^REMEDIATION_COMPLETE$
```

**Usage**: Infrastructure issues have been fixed.

**Format**:

```
REMEDIATION_COMPLETE

Issues Fixed:
- [issue]: [fix applied]

Verification Results:
- [check]: PASS

All infrastructure issues resolved.
```

---

## Health Auditor Signals

### HEALTH_AUDIT: HEALTHY

```
^HEALTH_AUDIT: HEALTHY$
```

**Usage**: All verification commands pass in all environments.

**Format**:

```
HEALTH_AUDIT: HEALTHY

Verification Results:
- [check] ([env]): PASS

All checks pass in all environments.
```

### HEALTH_AUDIT: UNHEALTHY

```
^HEALTH_AUDIT: UNHEALTHY$
```

**Usage**: One or more verification commands fail.

**Format**:

```
HEALTH_AUDIT: UNHEALTHY

Failed Checks:
- [check] ([env]): FAIL
  Exit: [code]
  Output: [error]

Passing Checks:
- [check] ([env]): PASS
```

---

## Escalation Signals

### SEEKING_DIVINE_CLARIFICATION

```
^SEEKING_DIVINE_CLARIFICATION$
```

**Usage**: Agent needs human guidance after exhausting self-solve and delegation.

**Allowed By**: Baseline agents only (developer, auditor, BA, remediation, health auditor)

**Format**:

```
SEEKING_DIVINE_CLARIFICATION

Task: [task_id]
Agent: [agent_type]

Question: [specific question for human]

Context:
[relevant background]

Options Considered:
1. [option]: [why insufficient]
2. [option]: [why insufficient]

Attempts Made:
- Self-solve: [N] attempts
- Delegation: [N] attempts (if applicable)

What Would Help:
[specific guidance needed]
```

### EXPERT_REQUEST

```
^EXPERT_REQUEST$
```

**Usage**: Baseline agent requests expert assistance.

**Allowed By**: Baseline agents only

**Format**:

```
EXPERT_REQUEST
Target Agent: [agent name]
Request Type: [decision | interpretation | ambiguity | options | validation]
Context Snapshot: [path to snapshot file]

---DELEGATION PROMPT START---
[Agent-generated prompt for expert]
---DELEGATION PROMPT END---
```

---

## Expert Signals

Experts are specialist agents created per-plan to support default agents.

### EXPERT_ADVICE

```
^EXPERT_ADVICE: (.+)$
```

**Usage**: Expert has provided advice in response to a default agent's request.

**Format**:

```
EXPERT_ADVICE: [request_id]

Requesting Agent: [who asked]
Task: [which task]
Question: [what was asked]

Recommendation:
[Clear guidance]

Rationale:
- [Why this is correct for this plan]

Pitfalls Avoided:
- [What this recommendation avoids]

Next Steps:
[What the default agent should do]
```

### EXPERT_UNSUCCESSFUL

```
^EXPERT_UNSUCCESSFUL: (.+)$
```

**Usage**: Expert cannot provide advice after 3 attempts. Default agent should escalate to divine intervention.

**Format**:

```
EXPERT_UNSUCCESSFUL: [request_id]

Requesting Agent: [who asked]
Question: [what was asked]

Attempts:
1. [approach]: [outcome]
2. [approach]: [outcome]
3. [approach]: [outcome]

Reason: [why unable to help]
Recommendation: [escalate to divine intervention]
```

### EXPERT_CREATED

```
^EXPERT_CREATED: (.+)$
```

**Usage**: Orchestrator has created a new expert during plan analysis.

**Format**:

```
EXPERT_CREATED: [expert_name]

Gap Filled: [description]
Supports: [which default agents]
Tasks: [task IDs]
File: .claude/agents/experts/[expert_name].md

Expertise Encoded:
- [specific to this plan]

Delegation Triggers:
- Developer should ask when: [trigger]
- Auditor should ask when: [trigger]
```

---

## Concurrency Signals

### FILE CONFLICT

```
^FILE CONFLICT: (.+)$
```

**Usage**: Agent needs to modify a file assigned to another agent.

**Format**:

```
FILE CONFLICT: [file_path]

Assigned To: [other_agent_id or UNKNOWN]
I Need To: [description of needed change]
Reason: [why this file must be modified]
Can Wait: [YES | NO]
```

**Coordinator Response**:

- If can wait: Queue request, notify when available
- If cannot wait: Coordinate merge or reassign

---

## Checkpoint Signals

### CHECKPOINT RESPONSE

```
^CHECKPOINT: (.+)$
```

**Usage**: Developer responds to coordinator checkpoint request.

**Format**:

```
CHECKPOINT: [task_id]

Progress: [percentage or phase]
Current Activity: [what agent is doing]
Files Modified: [count]
Blockers: [NONE | description]
Estimated Remaining: [description, not time]
```

---

## Signal Parsing Reference

```python
SIGNAL_PATTERNS = {
    # Developer signals
    'ready_for_review': re.compile(r'^READY_FOR_REVIEW:\s*(\S+)', re.MULTILINE),
    'task_incomplete': re.compile(r'^TASK_INCOMPLETE:\s*(\S+)', re.MULTILINE),
    'infra_blocked': re.compile(r'^INFRA_BLOCKED:\s*(\S+)', re.MULTILINE),

    # Critic signals
    'review_passed': re.compile(r'^REVIEW_PASSED:\s*(\S+)', re.MULTILINE),
    'review_failed': re.compile(r'^REVIEW_FAILED:\s*(\S+)', re.MULTILINE),

    # Auditor signals
    'audit_passed': re.compile(r'^AUDIT_PASSED:\s*(\S+)', re.MULTILINE),
    'audit_failed': re.compile(r'^AUDIT_FAILED:\s*(\S+)', re.MULTILINE),
    'audit_blocked': re.compile(r'^AUDIT_BLOCKED:\s*(\S+)', re.MULTILINE),

    # BA signals
    'expanded_spec': re.compile(r'^EXPANDED_TASK_SPECIFICATION:\s*(\S+)', re.MULTILINE),

    # Remediation signals
    'remediation_complete': re.compile(r'^REMEDIATION_COMPLETE$', re.MULTILINE),

    # Health auditor signals
    'health_healthy': re.compile(r'^HEALTH_AUDIT: HEALTHY$', re.MULTILINE),
    'health_unhealthy': re.compile(r'^HEALTH_AUDIT: UNHEALTHY$', re.MULTILINE),

    # Escalation signals
    'divine_clarification': re.compile(r'^SEEKING_DIVINE_CLARIFICATION$', re.MULTILINE),

    # Expert signals
    'expert_request': re.compile(r'^EXPERT_REQUEST$', re.MULTILINE),
    'expert_advice': re.compile(r'^EXPERT_ADVICE:\s*(\S+)', re.MULTILINE),
    'expert_unsuccessful': re.compile(r'^EXPERT_UNSUCCESSFUL:\s*(\S+)', re.MULTILINE),
    'expert_created': re.compile(r'^EXPERT_CREATED:\s*(\S+)', re.MULTILINE),

    # Concurrency signals
    'file_conflict': re.compile(r'^FILE CONFLICT:\s*(\S+)', re.MULTILINE),

    # Checkpoint signals
    'checkpoint': re.compile(r'^CHECKPOINT:\s*(\S+)', re.MULTILINE),
}


# Signal to handler action mapping
SIGNAL_HANDLERS = {
    # Developer signals
    'ready_for_review': 'DISPATCH_CRITIC',
    'task_incomplete': 'LOG_AND_FILL_SLOTS',
    'infra_blocked': 'ENTER_REMEDIATION',

    # Critic signals
    'review_passed': 'DISPATCH_AUDITOR',
    'review_failed': 'DISPATCH_DEVELOPER_REWORK',

    # Auditor signals
    'audit_passed': 'MARK_COMPLETE',
    'audit_failed': 'DISPATCH_DEVELOPER_REWORK',
    'audit_blocked': 'ENTER_REMEDIATION',

    # BA signals
    'expanded_spec': 'PROCESS_EXPANSION',

    # Remediation signals
    'remediation_complete': 'DISPATCH_HEALTH_AUDITOR',
    'health_healthy': 'EXIT_REMEDIATION',
    'health_unhealthy': 'RETRY_REMEDIATION',

    # Escalation signals
    'divine_clarification': 'AWAIT_DIVINE_RESPONSE',

    # Expert signals
    'expert_request': 'DISPATCH_EXPERT',
    'expert_advice': 'DELIVER_TO_REQUESTING_AGENT',
    'expert_unsuccessful': 'ESCALATE_TO_DIVINE',
    'expert_created': 'REGISTER_EXPERT',

    # Concurrency signals
    'file_conflict': 'QUEUE_OR_COORDINATE',

    # Checkpoint signals
    'checkpoint': 'PROCESS_CHECKPOINT',

    # Unknown/malformed signal recovery
    'unknown': 'REQUEST_CLARIFICATION',
}


def parse_signal(agent_output: str) -> dict:
    """Parse agent output for signals. Returns signal info with handler action."""
    for signal_type, pattern in SIGNAL_PATTERNS.items():
        match = pattern.search(agent_output)
        if match:
            return {
                'signal': signal_type,
                'task_id': match.group(1) if match.lastindex else None,
                'handler': SIGNAL_HANDLERS.get(signal_type, 'UNKNOWN'),
                'raw_output': agent_output
            }
    return {'signal': 'unknown', 'handler': 'REQUEST_CLARIFICATION', 'raw_output': agent_output}
```

---

## Unknown Signal Handling

When `parse_signal()` returns `'unknown'`, the coordinator MUST NOT ignore it. Unknown signals indicate either:

- Agent produced malformed output
- Agent is confused about expected signal format
- New signal type not yet in patterns

**Handler: REQUEST_CLARIFICATION**

```python
def handle_unknown_signal(task_id, agent_id, raw_output):
    """Handle unrecognized agent output to prevent system halt."""

    unknown_signal_count[task_id] = unknown_signal_count.get(task_id, 0) + 1

    if unknown_signal_count[task_id] >= 3:
        # Agent consistently produces invalid signals - escalate
        log_event("agent_signal_failure", task_id=task_id, agent_id=agent_id,
                  reason="3_consecutive_unknown_signals")

        # Treat as agent timeout - re-dispatch with explicit signal instructions
        handle_agent_timeout(task_id, agent_id,
                             context="Agent produced 3 unrecognized signals. "
                                     "Re-dispatching with explicit format requirements.")
        unknown_signal_count[task_id] = 0
        return

    # Request checkpoint to verify agent is responsive
    request_checkpoint(task_id)

    # If checkpoint received within timeout: request signal re-send
    # If no checkpoint: treat as agent timeout
    log_event("unknown_signal_recovery", task_id=task_id,
              attempt=unknown_signal_count[task_id],
              output_preview=raw_output[:200])
```

**Recovery Path**:

1. First unknown signal → request checkpoint, log warning
2. Second unknown signal → request checkpoint, log error
3. Third unknown signal → treat as agent failure, re-dispatch task

---

## Signal Priority

When multiple signals could apply, use this priority:

1. `INFRA_BLOCKED` / `AUDIT_BLOCKED` - Infrastructure issues take precedence
2. `SEEKING_DIVINE_CLARIFICATION` - Human escalation
3. `EXPERT_REQUEST` - Expert consultation
4. `FILE CONFLICT` - Concurrency management
5. Primary workflow signals (`READY_FOR_REVIEW`, `REVIEW_PASSED`, `AUDIT_PASSED`, etc.)

---

## Cross-References

- Signal handling procedures: [task-delivery-loop.md](task-delivery-loop.md)
- Expert delegation: [expert-delegation.md](expert-delegation.md)
- State management: [state-management.md](state-management.md)
