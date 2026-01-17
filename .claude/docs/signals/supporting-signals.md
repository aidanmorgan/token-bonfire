# Supporting Signals

Signals for supporting agents and processes: Business Analyst, Remediation, and Health Auditor.

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

## Related Documentation

- [Signal Index](index.md) - Overview and detection rules
- [Workflow Signals](workflow-signals.md) - Developer, Critic, Auditor signals
- [Coordination Signals](coordination-signals.md) - Escalation, Expert, Concurrency, Checkpoint signals
- [Signal Parsing](parsing.md) - Implementation details
