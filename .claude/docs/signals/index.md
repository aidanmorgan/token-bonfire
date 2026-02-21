# Signal Reference

All teammate-to-team-lead signals are defined here. **This is the single source of truth.**

## Delivery Mechanism

Signals are sent as **plain-text mailbox messages** via `TeammateTool({ operation: "write", to: "team-lead" })`. The team lead reads its mailbox to receive signals. There is no regex parsing of agent output — signals are explicit messages between named teammates.

### Sending a Signal

```
TeammateTool({ operation: "write", to: "team-lead", message: "READY_FOR_REVIEW: task-1\n\nSummary: ..." })
```

### Receiving Signals

The team lead reads its mailbox to receive signals from all teammates. Each message has a known sender (the named teammate), so routing decisions are straightforward.

## Signal Format Rules

| Rule               | Requirement                        | Example                                |
|--------------------|------------------------------------|----------------------------------------|
| Signal name        | Use EXACT name from this spec      | `READY_FOR_REVIEW` not `Ready for Review` |
| Separator          | Use colon and space after signal   | `READY_FOR_REVIEW: task-1`             |
| Placement          | Signal at START of message         | First line of the mailbox message      |
| No false positives | Don't use signal keywords in prose | Don't write "this is READY_FOR_REVIEW" |

## Signal Priority

When multiple signals could apply, use this priority:

1. `INFRA_BLOCKED` / `AUDIT_BLOCKED` - Infrastructure issues take precedence
2. `SEEKING_DIVINE_CLARIFICATION` - Human escalation
3. `FILE_CONFLICT` - File ownership coordination
4. Primary workflow signals (`READY_FOR_REVIEW`, `REVIEW_PASSED`, `AUDIT_PASSED`, etc.)

## Workflow Overview

```
Developer ──READY_FOR_REVIEW──> Team Lead ──review request──> Critic ──REVIEW_PASSED──> Ripple ──RIPPLE_PASSED──> Auditor ──AUDIT_PASSED──> Complete
                                                                  ↓                         ↓                          ↓
                                                            REVIEW_FAILED             RIPPLE_FAILED              AUDIT_FAILED
                                                                  ↓                         ↓                          ↓
                                                         (feedback to Developer)  (feedback to Developer)  (feedback to Developer)

Developer ──NEED_EXPERT_ADVICE──> Team Lead ──question──> Expert Advisor ──EXPERT_ADVICE_PROVIDED──> Team Lead ──advice──> Developer
```

---

## Signal Routing Table

| Signal | Sender | Team Lead Action |
|--------|--------|-----------------|
| `READY_FOR_REVIEW: <id>` | Developer | `write` review request to `critic` |
| `NEED_CLARIFICATION: <question>` | Developer | Route to `business-analyst` or `AskUserQuestion` |
| `NEED_EXPERT_ADVICE: <id>` | Developer | Route question to appropriate expert advisor via `write` |
| `INFRA_BLOCKED: <details>` | Developer | `write` to `remediation` |
| `FILE_CONFLICT: <file>` | Developer | Coordinate ownership via `write` to involved developers |
| `EXPERT_ADVICE_PROVIDED: <id>` | Expert advisor | Forward advice to requesting developer via `write` |
| `REVIEW_PASSED: <id>` | `critic` | `write` ripple request to `ripple` |
| `REVIEW_FAILED: <id>` | `critic` | `write` feedback to owning developer |
| `RIPPLE_PASSED: <id>` | `ripple` | `write` audit request to `auditor` |
| `RIPPLE_FAILED: <id>` | `ripple` | `write` feedback to owning developer |
| `AUDIT_PASSED: <id>` | `auditor` | `TaskUpdate({ status: "completed" })` |
| `AUDIT_FAILED: <id>` | `auditor` | `write` feedback to owning developer |
| `AUDIT_BLOCKED: <id>` | `auditor` | `write` to `remediation` |
| `EXPANDED_TASK_SPECIFICATION: <id>` | `business-analyst` | `TaskUpdate` description, route to developer |
| `REMEDIATION_COMPLETE` | `remediation` | `write` to `health-auditor` |
| `HEALTH_AUDIT: HEALTHY` | `health-auditor` | Resume normal flow |
| `HEALTH_AUDIT: UNHEALTHY` | `health-auditor` | `write` details to `remediation` |
| `SEEKING_DIVINE_CLARIFICATION` | Any teammate | `AskUserQuestion` to escalate |
| `CHECKPOINT: <id>` | Any teammate | Log progress, no routing needed |

---

## Workflow Signals

### READY_FOR_REVIEW

**Sent by**: Developer | **Action**: Forward to `critic`

```
READY_FOR_REVIEW: [task_id]

Summary: [1-2 sentence description of changes]

Files Modified:
- [file1]: [change description]
- [file2]: [change description]

Files Read-Only (referenced but not modified):
- [file1]

Tests Written:
- [test_file]: [what it tests]

Environment Verification Matrix:
| Check | Environment | Exit Code | Result |
|-------|-------------|-----------|--------|
| [check_name] | [env1] | [actual_code] | PASS |
| [check_name] | [env2] | [actual_code] | PASS |

Environments Tested: [env1], [env2]
All Required Environments: VERIFIED
```

**Environment Verification Matrix (MANDATORY)**: Must include a row for EACH (check x environment) pair. Exit code must be ACTUAL value returned. MALFORMED SIGNALS REJECTED: Missing environments = signal rejected, must re-run verification.

---

### NEED_CLARIFICATION

**Sent by**: Developer | **Action**: Route to `business-analyst` or `AskUserQuestion`

```
NEED_CLARIFICATION: [task_id]

Question: [specific question]
Context: [what the developer was attempting]
Options Considered:
- [option A]: [implications]
- [option B]: [implications]
```

---

### NEED_EXPERT_ADVICE

**Sent by**: Developer | **Action**: Route question to appropriate expert advisor via `write`

```
NEED_EXPERT_ADVICE: [task_id]

Question: [specific domain question]
Context: [what the developer is implementing]
Domain: [relevant technology/area]
```

---

### INFRA_BLOCKED

**Sent by**: Developer | **Action**: Forward to `remediation` via `write`

```
INFRA_BLOCKED: [task_id]

Issue: [specific infrastructure problem]
Command: [command that failed]
Output: [error output]
Environment: [which environment]
```

---

### EXPERT_ADVICE_PROVIDED

**Sent by**: Named expert advisor | **Action**: Forward advice to requesting developer via `write`

```
EXPERT_ADVICE_PROVIDED: [task_id]

Question: [original developer question]

Advice:
- [recommendation or guidance]
- [patterns to follow]
- [pitfalls to avoid]

References:
- [relevant documentation or resources]
```

---

### REVIEW_PASSED

**Sent by**: `critic` | **Action**: Forward to `ripple` via `write`

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

---

### REVIEW_FAILED

**Sent by**: `critic` | **Action**: Forward feedback to owning developer via `write`

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
```

**Note**: Critic focuses purely on code quality. Acceptance criteria verification is the Auditor's responsibility.

---

### RIPPLE_PASSED

**Sent by**: `ripple` | **Action**: Forward to `auditor` via `write`

```
RIPPLE_PASSED: [task_id]

Impact Summary:
- Files analyzed: [count]
- Direct importers checked: [count]
- Transitive dependents checked: [count]

Impact Graph:
- [modified-file] → imported by [[consumer-1], [consumer-2], ...]

Notes:
- [any latent observations — informational only]
```

---

### RIPPLE_FAILED

**Sent by**: `ripple` | **Action**: Forward feedback to owning developer via `write`

```
RIPPLE_FAILED: [task_id]

Issues Found:
1. [severity] Source: [modified-file]
   Affected: [consumer-file]:[line]
   Problem: [specific description]
   Remediation: [specific instruction]

Test Coverage Gaps:
- [impacted-file]: no tests for [affected-behavior]

Impact Graph:
- [modified-file] → imported by [[consumer-1], [consumer-2], ...]
```

**Note**: Ripple focuses on second-order effects. First-order code quality is the Critic's responsibility.

---

### AUDIT_PASSED

**Sent by**: `auditor` | **Action**: Mark task `completed` via `TaskUpdate`. **This is the ONLY signal that triggers task completion.**

```
AUDIT_PASSED: [task_id]

Quality Verification:
- Code quality tells: NONE FOUND
- Standards compliance: VERIFIED

Requirements Verification:
- [criterion_1]: VERIFIED - [evidence]
- [criterion_2]: VERIFIED - [evidence]

Environment Verification Matrix:
| Check | Environment | Exit Code | Result |
|-------|-------------|-----------|--------|
| [check_name] | [env1] | [actual_code] | PASS |
| [check_name] | [env2] | [actual_code] | PASS |

Environments Verified: [env1], [env2]
All Required Environments: CONFIRMED

Summary: [brief conclusion]
```

**Environment Verification Matrix (MANDATORY)**: Auditor MUST independently execute all verification commands and include the matrix.

---

### AUDIT_FAILED

**Sent by**: `auditor` | **Action**: Forward feedback to owning developer via `write`

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

---

### AUDIT_BLOCKED

**Sent by**: `auditor` | **Action**: Forward to `remediation` via `write`

```
AUDIT_BLOCKED: [task_id]

Pre-existing Failures:
- [failure not caused by this task]

Cannot proceed with audit until infrastructure is fixed.
```

---

## Supporting Signals

### EXPANDED_TASK_SPECIFICATION

**Sent by**: `business-analyst` | **Action**: Update task description via `TaskUpdate`, route to developer

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

### REMEDIATION_COMPLETE

**Sent by**: `remediation` | **Action**: Forward to `health-auditor` via `write`

```
REMEDIATION_COMPLETE

Issues Fixed:
- [issue]: [fix applied]

Verification Results:
- [check]: PASS

All infrastructure issues resolved.
```

---

### HEALTH_AUDIT: HEALTHY

**Sent by**: `health-auditor` | **Action**: Resume normal development flow

```
HEALTH_AUDIT: HEALTHY

Verification Results:
- [check] ([env]): PASS

All checks pass in all environments.
```

---

### HEALTH_AUDIT: UNHEALTHY

**Sent by**: `health-auditor` | **Action**: Forward details to `remediation` via `write`; escalate after 3 remediation cycles

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

## Coordination Signals

### SEEKING_DIVINE_CLARIFICATION

**Sent by**: Any teammate | **Action**: Escalate to user via `AskUserQuestion`

```
SEEKING_DIVINE_CLARIFICATION

Task: [task_id]
Agent: [teammate name]

Question: [specific question for human]

Context:
[relevant background]

Options Considered:
1. [option]: [why insufficient]
2. [option]: [why insufficient]

What Would Help:
[specific guidance needed]
```

---

### FILE_CONFLICT

**Sent by**: Developer | **Action**: Coordinate ownership between developers via `write` — assign single owner, other yields

```
FILE_CONFLICT: [file_path]

Task: [task_id]
I Need To: [description of needed change]
Reason: [why this file must be modified]
Can Wait: [YES | NO]
```

**Team lead resolution**:
- If the file owner's task is nearly complete: tell the requesting developer to wait
- If the conflict can be coordinated: assign single owner, instruct the other to yield
- If the file is shared (e.g., `__init__.py`): instruct additive-only changes

---

### CHECKPOINT

**Sent by**: Any teammate | **Action**: Log progress, no routing needed

```
CHECKPOINT: [task_id]

Progress: [percentage or phase]
Current Activity: [what the teammate is doing]
Files Modified: [count]
Blockers: [NONE | description]
Estimated Remaining: [description, not time]
```

---

## Unrecognized Message Handling

When the team lead receives a mailbox message that does not match any known signal format, it should NOT ignore it. Unrecognized messages indicate either a malformed signal, a confused teammate, or legitimate non-signal communication.

### Recovery Procedure

1. **First unrecognized message**: Send `write` to teammate asking them to resend using the correct signal format.
2. **Second unrecognized message from same teammate**: Send more detailed `write` with the exact signal format that seems intended.
3. **Third unrecognized message**: Consider the teammate may be stuck. Check task status and potentially reassign or respawn.

### Message Integrity

Because signals are explicit mailbox messages between named teammates:
- **No false positives**: Signals are intentional messages, not patterns extracted from verbose output
- **Clear sender**: Every message has a known sender (the named teammate)
- **Targeted delivery**: Messages go to a specific recipient, not broadcast
- **No regex fragility**: Signal format is human-readable plain text, not regex-matched

---

## Related Documentation

- Team architecture and communication: [team-architecture.md](../team-architecture.md)
- Troubleshooting: [troubleshooting.md](../troubleshooting.md)
