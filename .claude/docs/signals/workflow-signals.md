# Workflow Signals

Primary signals for the main development workflow: Developer → Critic → Auditor.

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

Environment Verification Matrix:
| Check | Environment | Exit Code | Result |
|-------|-------------|-----------|--------|
| [check_name] | [env1] | [actual_code] | PASS |
| [check_name] | [env2] | [actual_code] | PASS |
| [check2_name] | [env1] | [actual_code] | PASS |
| [check2_name] | [env2] | [actual_code] | PASS |

Environments Tested: [env1], [env2]
All Required Environments: VERIFIED

Expert Consultation:
- Consulted: [expert-name] for [topic] - Advice: [brief summary]
  OR
- Not needed: [justification]
  OR
- Pre-implementation review: [expert-name] confirmed approach

Summary: [brief description of implementation]
```

**Environment Verification Matrix (MANDATORY)**:

| Requirement              | Description                                                   |
|--------------------------|---------------------------------------------------------------|
| Row per combination      | MUST include a row for EACH (check × environment) pair        |
| Empty Environment column | Command MUST be run in EVERY environment - add a row for each |
| Specific Environment     | Command runs only in that environment - one row               |
| Exit Code                | MUST show ACTUAL exit code returned, not assumed              |
| Result                   | PASS only if actual exit code matches required exit code      |
| Environments Tested      | List ALL environments you executed commands in                |
| VERIFIED line            | Confirms you ran in all required environments                 |

**MALFORMED SIGNALS REJECTED**: Missing environments = signal rejected, must re-run verification.

**Expert Consultation (MANDATORY)**:

| Format                                                   | When to Use                             |
|----------------------------------------------------------|-----------------------------------------|
| `Consulted: [expert] for [topic] - Advice: [summary]`    | You asked an expert for guidance        |
| `Not needed: [justification]`                            | Task didn't require expert input        |
| `Pre-implementation review: [expert] confirmed approach` | Expert confirmed approach before coding |

Invalid values (will cause REVIEW_FAILED): "N/A", "None", empty, or missing field.

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
| [check2_name] | [env1] | [actual_code] | PASS |
| [check2_name] | [env2] | [actual_code] | PASS |

Environments Verified: [env1], [env2]
All Required Environments: CONFIRMED

Summary: [brief conclusion]
```

**Environment Verification Matrix (MANDATORY for AUDIT_PASSED)**:

The auditor MUST independently execute all verification commands and include the matrix.
Same requirements as developer signal - see above.

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

## Related Documentation

- [Signal Index](index.md) - Overview and detection rules
- [Supporting Signals](supporting-signals.md) - BA, Remediation, Health Auditor signals
- [Coordination Signals](coordination-signals.md) - Escalation, Expert, Concurrency, Checkpoint signals
- [Signal Parsing](parsing.md) - Implementation details
