# Pre-Existing Failures Baseline

Procedures for establishing a baseline of pre-existing failures before work begins.

## Overview

Establish a baseline of what failures exist BEFORE any work begins. This allows distinguishing between:

- **Pre-existing failures**: Issues that existed before the session started
- **Task-introduced failures**: Issues caused by work done in this session

For error classification and routing, see [error-classification.md](../error-classification.md).

See also:

- [Resume Procedure](../team-lead/resume.md) - Session resume including baseline verification

---

## Baseline Capture at Session Start

The team lead (or auditor) captures the baseline by running all verification commands from `base_variables.md` before any tasks begin:

### Procedure

1. Run each verification command in each configured environment
2. Record exit codes and pass/fail status
3. Store results in the team lead's context for later comparison
4. If many pre-existing failures exist, warn the user and consider remediation first

### Baseline Data

For each check:
- Command executed
- Environment
- Exit code (expected vs actual)
- Pass/fail status
- Output summary (for failures only)

## Session Start with Baseline Check

On session start, the team lead:

1. Runs standard recovery checks (see [resume.md](../team-lead/resume.md))
2. Checks if a baseline was already established (resume case — baseline in context may be lost)
3. If no baseline exists, captures a fresh baseline before dispatching work
4. If many pre-existing failures exist (>10), warns the user:
   ```
   WARNING: <N> pre-existing failures detected.
   RECOMMEND: Remediate pre-existing failures before starting work.
   ```

## Baseline Format

The team lead tracks the baseline in its context:

```
Baseline captured at: <timestamp>
Environment: <env-name>
  - <check-name>: PASS (exit 0)
  - <check-name>: FAIL (exit 1) - <output summary>
Environment: <env-name>
  - <check-name>: PASS (exit 0)
  - <check-name>: FAIL (exit 1) - <output summary>
Summary: <N> total failures across <N> environments
```

---

## Cross-References

- [Error Classification](../error-classification.md) - Error types and routing logic
- [Resume Procedure](../team-lead/resume.md) - Session resume including baseline verification
- [Communication Protocol](../communication-protocol.md) - Verification protocol
