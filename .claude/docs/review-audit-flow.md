# Review and Audit Flow

This document covers Steps 5-9 of the coordinator loop: Critic review, Auditor verification, and outcome routing.

**Related Documents:**

- [task-dispatch.md](task-dispatch.md) - Steps 1-4: Task dispatch
- [signal-specification.md](signal-specification.md) - All signal formats
- [agent-recovery.md](agent-recovery.md) - Timeout and crash handling
- [developer-rework.md](developer-rework.md) - Rework dispatch procedures

---

## Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    REVIEW & AUDIT FLOW (Steps 5-9)                       │
├─────────────────────────────────────────────────────────────────────────┤
│  5. DISPATCH CRITIC (on READY_FOR_REVIEW)                                │
│     ↓                                                                    │
│  6. AWAIT CRITIC → parse REVIEW_PASSED or REVIEW_FAILED                  │
│     ↓ REVIEW_PASSED                    ↓ REVIEW_FAILED                   │
│  7. DISPATCH AUDITOR                   → Developer rework                │
│     ↓                                                                    │
│  8. AWAIT AUDITOR → parse AUDIT_PASSED/FAILED/BLOCKED                    │
│     ↓                                                                    │
│  9. ROUTE: PASS → complete | FAIL → rework | BLOCKED → remediation       │
└─────────────────────────────────────────────────────────────────────────┘
```

### Workflow Diagram

```
┌──────────────┐    READY_FOR_REVIEW    ┌──────────────┐    REVIEW_PASSED    ┌──────────────┐
│              │ ────────────────────►  │              │ ──────────────────► │              │
│  DEVELOPER   │                        │    CRITIC    │                     │   AUDITOR    │
│              │ ◄────────────────────  │              │                     │              │
└──────────────┘    REVIEW_FAILED       └──────────────┘                     └──────────────┘
       ▲            (with issues)                                                   │
       │                                                                            │
       │                                    AUDIT_FAILED                            │
       └────────────────────────────────────(with issues)───────────────────────────┘
```

| Stage          | Agent      | Purpose             | Success            | Failure           |
|----------------|------------|---------------------|--------------------|-------------------|
| Implementation | Developer  | Write code          | `READY_FOR_REVIEW` | `TASK_INCOMPLETE` |
| Quality Review | **Critic** | Code quality check  | `REVIEW_PASSED`    | `REVIEW_FAILED`   |
| Verification   | Auditor    | Acceptance criteria | `AUDIT_PASSED`     | `AUDIT_FAILED`    |

---

## Step 5: Dispatch Critic

**Input**: Task ID, files modified, developer READY_FOR_REVIEW signal

**Trigger**: Orchestrator receives `READY_FOR_REVIEW` signal from Developer

The Critic reviews code quality before formal audit:

- Code style violations
- Missing error handling
- Poor naming conventions
- Architectural violations
- Best practice deviations

### Procedure

1. **Extract from state**:
    - Task details (from plan)
    - Files modified (from developer completion)
    - Best practices (from configuration)

2. **Prepare critic prompt**:
   ```python
   critic_prompt = f"""
   {Read(".claude/agents/critic.md")}

   ---

   ## Review Assignment

   Task ID: {task_id}

   ### Files to Review
   {format_files_list(files_modified)}

   ### Developer READY_FOR_REVIEW Signal
   {developer_ready_signal}

   ### Review Focus
   - Code quality and best practices
   - Error handling patterns
   - Naming conventions
   - Architectural consistency
   - Project standards compliance

   ### Required Output Signal
   You MUST end your review with one of:
   - `REVIEW_PASSED: {task_id}` - if code quality is acceptable
   - `REVIEW_FAILED: {task_id}` - if issues need fixing

   Begin review.
   """
   ```

3. **Dispatch**:
   ```python
   Task tool parameters:
     model: [from critic agent file frontmatter]
     subagent_type: "developer"
     prompt: [prepared critic prompt]
   ```

4. **Update state**:
   ```python
   active_critics[critic_id] = {
       'task_id': task_id,
       'dispatched_at': datetime.now().isoformat()
   }
   pending_critique.append(task_id)
   in_progress_tasks[task_id]['status'] = 'awaiting-review'
   log_event("critic_dispatched", task_id=task_id)
   save_state()
   ```

---

## Step 6: Parse Critic Output

**Input**: Critic agent output

### REVIEW_PASSED Signal Format

```
REVIEW_PASSED: <task_id>

Files Reviewed:
- <file1>
- <file2>

Quality Assessment:
- Code style: COMPLIANT
- Error handling: ADEQUATE
- Naming: CONSISTENT
- Architecture: ALIGNED

Summary: <brief_assessment>
```

### REVIEW_FAILED Signal Format

```
REVIEW_FAILED: <task_id>

Files Reviewed:
- <file1>
- <file2>

Issues Found:
- <file>:<line>: <issue_description>
- <file>:<line>: <issue_description>

Required Fixes:
- <concrete_action>
- <concrete_action>

Priority: <HIGH|MEDIUM|LOW>

Developer: Please address all issues above and signal READY_FOR_REVIEW when complete.
```

### Parse Procedure

```python
def parse_critic_output(output: str, expected_task_id: str) -> dict:
    """Parse critic output for REVIEW_PASSED or REVIEW_FAILED signal."""

    # Check for REVIEW_PASSED
    passed_match = re.search(r'^REVIEW_PASSED:\s*(\S+)', output, re.MULTILINE)
    if passed_match:
        task_id = passed_match.group(1)
        if task_id != expected_task_id:
            raise SignalError(f"Task ID mismatch")

        return {
            'signal': 'REVIEW_PASSED',
            'task_id': task_id,
            'quality_assessment': extract_quality_assessment(output),
            'next_action': 'DISPATCH_AUDITOR'
        }

    # Check for REVIEW_FAILED
    failed_match = re.search(r'^REVIEW_FAILED:\s*(\S+)', output, re.MULTILINE)
    if failed_match:
        task_id = failed_match.group(1)
        return {
            'signal': 'REVIEW_FAILED',
            'task_id': task_id,
            'issues': extract_issues(output),
            'required_fixes': extract_required_fixes(output),
            'priority': extract_priority(output),
            'next_action': 'DISPATCH_DEVELOPER_REWORK'
        }

    return {'signal': 'UNKNOWN', 'next_action': 'REQUEST_CLARIFICATION'}
```

### On REVIEW_PASSED → Dispatch Auditor

```python
pending_critique.remove(task_id)
pending_audit.append(task_id)
in_progress_tasks[task_id]['status'] = 'awaiting-audit'
log_event("critic_pass", task_id=task_id)
dispatch_auditor(task_id)  # → Step 7
```

### On REVIEW_FAILED → Developer Rework

```python
pending_critique.remove(task_id)
critique_failures[task_id] = critique_failures.get(task_id, 0) + 1

if critique_failures[task_id] >= TASK_FAILURE_LIMIT:
    log_event("workflow_failed", reason="critique_failure_limit", task_id=task_id)
else:
    in_progress_tasks[task_id]['status'] = 'implementing'
    dispatch_developer_rework(task_id, critic_issues)
    log_event("critic_fail", task_id=task_id, failures=critique_failures[task_id])
```

See [developer-rework.md](developer-rework.md) for rework dispatch details.

---

## Step 7: Dispatch Auditor

**Input**: Task ID, files modified, acceptance criteria

**Trigger**: Orchestrator receives `REVIEW_PASSED` signal from Critic

### Procedure

1. **Extract from state**:
    - Task's acceptance criteria (from plan)
    - Files modified (from developer completion)
    - Verification commands (from config)
    - Critic's quality assessment

2. **Prepare auditor prompt**:
   ```python
   auditor_prompt = f"""
   {Read(".claude/agents/auditor.md")}

   ---

   ## Audit Assignment

   Task ID: {task_id}

   ### Acceptance Criteria
   {format_acceptance_criteria(task.acceptance_criteria)}

   ### Files to Verify
   {format_files_list(files_modified)}

   ### Critic Assessment (PASSED)
   {critic_quality_assessment}

   ### Verification Commands
   {format_verification_commands()}

   ### Required Output Signal
   You MUST end your audit with one of:
   - `AUDIT_PASSED: {task_id}` - if all acceptance criteria verified
   - `AUDIT_FAILED: {task_id}` - if criteria not met
   - `AUDIT_BLOCKED: {task_id}` - if pre-existing infrastructure issues

   Begin audit.
   """
   ```

3. **Dispatch**:
   ```python
   Task tool parameters:
     model: [from auditor agent file frontmatter]
     subagent_type: "developer"
     prompt: [prepared auditor prompt]
   ```

4. **Update state**:
   ```python
   active_auditors[auditor_id] = {
       'task_id': task_id,
       'dispatched_at': datetime.now().isoformat()
   }
   in_progress_tasks[task_id]['status'] = 'awaiting-audit'
   log_event("auditor_dispatched", task_id=task_id)
   save_state()
   ```

---

## Step 8: Parse Auditor Output

**Input**: Auditor agent output

### AUDIT_PASSED Signal Format

```
AUDIT_PASSED: <task_id>

Verification Results:
- <criterion_1>: VERIFIED - <evidence>
- <criterion_2>: VERIFIED - <evidence>

Commands Executed:
- <command> (<env>): PASS

Summary: <brief_conclusion>
```

### AUDIT_FAILED Signal Format

```
AUDIT_FAILED: <task_id>

Failed Criteria:
- <criterion>: FAILED - <reason>

Issues Found:
- <file>:<line>: <issue_description>

Required Fixes:
- <concrete_action>

Passing Criteria:
- <what_passed>
```

### AUDIT_BLOCKED Signal Format

```
AUDIT_BLOCKED: <task_id>

Pre-existing Failures:
- <N> test failures in <files>
- <infrastructure_issue>

Cannot proceed with audit until infrastructure is fixed.
```

### Parse Procedure

```python
def parse_auditor_output(output: str, expected_task_id: str) -> dict:
    """Parse auditor output for signals."""

    # Check for AUDIT_PASSED
    passed_match = re.search(r'^AUDIT_PASSED:\s*(\S+)', output, re.MULTILINE)
    if passed_match:
        return {
            'signal': 'AUDIT_PASSED',
            'task_id': passed_match.group(1),
            'verification_results': extract_verification_results(output),
            'next_action': 'MARK_COMPLETE'
        }

    # Check for AUDIT_FAILED
    failed_match = re.search(r'^AUDIT_FAILED:\s*(\S+)', output, re.MULTILINE)
    if failed_match:
        return {
            'signal': 'AUDIT_FAILED',
            'task_id': failed_match.group(1),
            'failed_criteria': extract_failed_criteria(output),
            'issues': extract_issues(output),
            'required_fixes': extract_required_fixes(output),
            'next_action': 'DISPATCH_DEVELOPER_REWORK'
        }

    # Check for AUDIT_BLOCKED
    blocked_match = re.search(r'^AUDIT_BLOCKED:\s*(\S+)', output, re.MULTILINE)
    if blocked_match:
        return {
            'signal': 'AUDIT_BLOCKED',
            'task_id': blocked_match.group(1),
            'pre_existing_failures': extract_failures(output),
            'next_action': 'ENTER_REMEDIATION'
        }

    return {'signal': 'UNKNOWN', 'next_action': 'REQUEST_CLARIFICATION'}
```

---

## Step 9: Route Based on Outcome

### PASS Routing (Task Complete)

```python
# Remove from active work
in_progress_tasks.remove(task_id)
pending_audit.remove(task_id)

# Mark complete
completed_tasks.append(task_id)

# Unblock dependents
for task, blockers in blocked_tasks.items():
    if task_id in blockers:
        blockers.remove(task_id)
        if not blockers:
            available_tasks.append(task)

# Log and save
log_event("task_complete", task_id=task_id)
save_state()
```

### FAIL Routing (Developer Rework)

```python
# Check failure count
audit_failures[task_id] = audit_failures.get(task_id, 0) + 1

if audit_failures[task_id] >= TASK_FAILURE_LIMIT:
    log_event("workflow_failed", reason="audit_failure_limit", task_id=task_id)
else:
    # Return to developer
    in_progress_tasks[task_id]["status"] = "implementing"
    pending_audit.remove(task_id)
    dispatch_developer_rework(task_id, audit_failures)
```

See [developer-rework.md](developer-rework.md) for rework dispatch details.

### BLOCKED Routing (Infrastructure Remediation)

```python
# Halt task assignments
infrastructure_blocked = True
infrastructure_issue = parse_blocked_reason(auditor_output)

# Spawn remediation
dispatch_remediation_agent(infrastructure_issue)

# Log
log_event("infrastructure_blocked", issue=infrastructure_issue)
save_state()
```

See [remediation-loop.md](remediation-loop.md) for remediation details.

---

## Signal Quick Reference

| Signal          | Source  | Next Action       |
|-----------------|---------|-------------------|
| `REVIEW_PASSED` | Critic  | Dispatch Auditor  |
| `REVIEW_FAILED` | Critic  | Developer rework  |
| `AUDIT_PASSED`  | Auditor | Mark complete     |
| `AUDIT_FAILED`  | Auditor | Developer rework  |
| `AUDIT_BLOCKED` | Auditor | Enter remediation |

See [signal-specification.md](signal-specification.md) for complete formats.

---

## Timeout and Recovery

For timeout and crash handling of Critics and Auditors, see [agent-recovery.md](agent-recovery.md).

---

## Cross-References

- [task-dispatch.md](task-dispatch.md) - Steps 1-4
- [signal-specification.md](signal-specification.md) - Signal formats
- [developer-rework.md](developer-rework.md) - Rework dispatch
- [agent-recovery.md](agent-recovery.md) - Timeout handling
- [remediation-loop.md](remediation-loop.md) - Infrastructure remediation
- [state-management.md](state-management.md) - State tracking
