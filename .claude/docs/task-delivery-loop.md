# Task Delivery Loop

This document specifies the step-by-step procedure for the coordinator to dispatch tasks, parse results, and route work
through the system.

## Overview

The task delivery loop has two phases, each detailed in separate documents:

**Phase A: Task Dispatch** ([task-dispatch.md](task-dispatch.md) - Steps 1-4):

1. SELECT TASK - Choose from available, unblocked tasks
2. PREPARE PROMPT - Expand templates, include references
3. DISPATCH DEVELOPER - Spawn agent via Task tool
4. PARSE DEVELOPER SIGNAL - Handle READY_FOR_REVIEW

**Phase B: Review & Audit** ([review-audit-flow.md](review-audit-flow.md) - Steps 5-9):

5. DISPATCH CRITIC - Code quality review
6. PARSE CRITIC OUTCOME - REVIEW_PASSED or REVIEW_FAILED
7. DISPATCH AUDITOR - Acceptance criteria verification
8. PARSE AUDIT OUTCOME - AUDIT_PASSED, AUDIT_FAILED, or AUDIT_BLOCKED
9. ROUTE - PASS → complete | FAIL → rework | BLOCKED → remediation

After routing, fill actor slots and loop.

---

## Step 1: Select Task

**Input**: `available_tasks`, `blocked_tasks`, `in_progress_tasks`

**Procedure**:

1. Filter tasks where all `blocked_by` dependencies are in `completed_tasks`
2. Sort by Task Selection Priority (see [state-management.md](state-management.md))
3. Select top N tasks where N = `ACTIVE_DEVELOPERS` - `active_actor_count`

**Output**: List of task IDs to dispatch

---

## Step 2: Prepare Agent Prompt

**Input**: Task ID, plan content, experts registry, agent type

**The coordinator builds the complete prompt by concatenating:**

1. **Agent Definition** (from `.claude/agents/[agent-type].md`)
2. **Task-Specific Context** (from plan and configuration)

See [task-dispatch.md](task-dispatch.md) for the detailed prompt construction procedure.

**Key Elements**:

- Agent definition file content
- Task work description and acceptance criteria
- Required reading files (MUST READ + REFERENCE)
- Matched experts table
- Verification commands and environments

**Output**: Complete prompt string (agent definition + task context)

---

## Step 3: Dispatch Agent

**Input**: Prepared prompt, task ID, agent type

**Procedure**:

1. Read agent model from file frontmatter
2. Spawn agent via Task tool with prepared prompt
3. Update state with dispatch information
4. Log event: `agent_dispatched`

See [task-dispatch.md](task-dispatch.md) for agent output retrieval and timeout handling.

**Output**: Agent ID (for tracking)

---

## Step 4: Parse Developer Output

**Input**: Developer agent output (full response text)

**Signal Detection**: Search for these patterns:

- `^READY_FOR_REVIEW: (.+)$` → Validate environment matrix, route to Critic
- `^SEEKING_DIVINE_CLARIFICATION$` → Handle per [divine-clarification.md](divine-clarification.md)
- `^EXPERT_REQUEST$` → Handle per [agent-coordination.md](agent-coordination.md)
- `^INFRA_BLOCKED: (.+)$` → Enter [remediation loop](remediation-loop.md)

**Environment Verification**: Before routing to Critic, validate the environment matrix is complete.
See [environment-verification.md](environment-verification.md) for validation procedure.

**Output**: Parsed completion data or blocker information

---

## Steps 5-6: Critic Review

**Input**: Task ID, developer completion signal

See [review-audit-flow.md](review-audit-flow.md) for the full Critic dispatch and parsing procedure (Steps 5-6).

**Summary**:

1. Prepare critic prompt with modified files and task context
2. Dispatch Critic agent
3. Parse outcome: `REVIEW_PASSED` → continue to audit | `REVIEW_FAILED` → developer rework

---

## Steps 7-8: Auditor Verification

**Input**: Task ID, files modified, acceptance criteria

See [review-audit-flow.md](review-audit-flow.md) for the full Auditor dispatch and parsing procedure (Steps 7-8).

**Summary**:

1. Extract task acceptance criteria and modified files
2. Dispatch Auditor agent
3. Parse audit outcome: PASS | FAIL | BLOCKED

---

## Step 9: Route Based on Outcome

### PASS Routing

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

log_event("task_complete", task_id=task_id)
save_state()
```

### FAIL Routing

**State updates**: See [state/update-triggers.md - AUDIT_FAILED](state/update-triggers.md#audit_failed) for the
authoritative state transition.

**Summary**: Increment failure count, check limit, dispatch rework or escalate.

See [developer-rework.md](developer-rework.md) for rework prompt construction.

### BLOCKED Routing

See [remediation-loop.md](remediation-loop.md) for the full remediation procedure.

**Summary**: Set `infrastructure_blocked`, dispatch remediation agent.

---

## Fill Actor Slots (After Each Routing Decision)

After any routing decision, immediately check and fill actor slots.

**CRITICAL: Dispatch in priority order - complete in-flight work before starting new work.**

```python
def fill_actor_slots():
    """Fill slots with priority: critics > auditors > developers."""

    if infrastructure_blocked or pending_divine_questions:
        return

    # PRIORITY 1: Dispatch critics for pending reviews
    # Tasks waiting for review should not be starved by new work
    while pending_critique and count_active_critics() < MAX_PARALLEL_CRITICS:
        task_id = pending_critique.pop(0)
        dispatch_critic(task_id)

    # PRIORITY 2: Dispatch auditors for pending audits
    # Tasks that passed review should complete before new work starts
    while pending_audit and count_active_auditors() < MAX_PARALLEL_AUDITORS:
        task_id = pending_audit.pop(0)
        dispatch_auditor(task_id)

    # PRIORITY 3: Dispatch developers for new tasks
    # Only start new work after in-flight work is being processed
    while count_active_developers() < MAX_PARALLEL_DEVELOPERS:
        if not available_tasks:
            break
        task = select_next_task()
        dispatch_developer(task)
```

**Why this order matters:**

- Completing in-flight work unblocks dependent tasks faster
- Prevents task starvation where reviews pile up while new work starts
- Ensures the full Developer→Critic→Auditor pipeline flows smoothly

---

## Coordinator State Machine

**States**: SELECT_TASK → DISPATCH_DEV → AWAIT_DEV

**From AWAIT_DEV**:

- DELEGATION → HANDLE_DELEGATE → back to loop
- READY_FOR_REVIEW → DISPATCH_CRIT → AWAIT_CRITIC
- DIVINE_QUESTION → AWAIT_DIVINE → back to loop

**From AWAIT_CRITIC**:

- REVIEW_PASSED → DISPATCH_AUD → AWAIT_AUDIT
- REVIEW_FAILED → REWORK → back to loop

**From AWAIT_AUDIT**:

- PASS → TASK_DONE → FILL_SLOTS → loop
- FAIL → REWORK → FILL_SLOTS → loop
- BLOCKED → REMEDIATE → FILL_SLOTS → loop

### Task States

| State           | Meaning                              |
|-----------------|--------------------------------------|
| implementing    | Developer working                    |
| awaiting-review | Developer done, critic reviewing     |
| awaiting-audit  | Critic passed, auditor reviewing     |
| complete        | Auditor PASSED (only state = "done") |
| rework          | Critic FAILED or Auditor FAILED      |

**Critical**: Only `AUDIT_PASSED` marks a task as complete.

---

## Signal Detection Summary

See [signal-specification.md](signal-specification.md) for complete signal formats.

### Task Flow Signals

| Pattern          | Regex                      | Handler             |
|------------------|----------------------------|---------------------|
| Ready for review | `^READY_FOR_REVIEW: (.+)$` | → dispatch critic   |
| Task incomplete  | `^TASK_INCOMPLETE: (.+)$`  | → log, fill slots   |
| Review passed    | `^REVIEW_PASSED: (.+)$`    | → dispatch auditor  |
| Review failed    | `^REVIEW_FAILED: (.+)$`    | → developer rework  |
| Audit pass       | `^AUDIT_PASSED: (.+)$`     | → **TASK COMPLETE** |
| Audit fail       | `^AUDIT_FAILED: (.+)$`     | → developer rework  |
| Audit blocked    | `^AUDIT_BLOCKED: (.+)$`    | → remediation loop  |
| Infra blocked    | `^INFRA_BLOCKED: (.+)$`    | → remediation loop  |

### Remediation Signals

| Pattern              | Regex                       | Handler                 |
|----------------------|-----------------------------|-------------------------|
| Remediation complete | `^REMEDIATION_COMPLETE$`    | → dispatch health audit |
| Health healthy       | `^HEALTH_AUDIT: HEALTHY$`   | → resume flow           |
| Health unhealthy     | `^HEALTH_AUDIT: UNHEALTHY$` | → loop remediation      |

### Coordination Signals

| Pattern            | Regex                            | Handler               |
|--------------------|----------------------------------|-----------------------|
| Divine question    | `^SEEKING_DIVINE_CLARIFICATION$` | → pause, escalate     |
| Delegation request | `^EXPERT_REQUEST$`               | → spawn expert        |
| Agent complete     | `^EXPERT_ADVICE: (.+)$`          | → return to delegator |

---

## Error Recovery

See [recovery-procedures.md](recovery-procedures.md) for detailed error handling.

| Error Type       | Recovery Action                                     |
|------------------|-----------------------------------------------------|
| Agent timeout    | Re-dispatch if under limit, else escalate           |
| Parse failure    | Log output, request checkpoint, treat as incomplete |
| State corruption | Reconstruct from event log or request manual repair |

---

## Related Documentation

- [task-dispatch.md](task-dispatch.md) - Prompt construction and dispatch details
- [review-audit-flow.md](review-audit-flow.md) - Critic and Auditor dispatch
- [developer-rework.md](developer-rework.md) - Rework dispatch after failures
- [remediation-loop.md](remediation-loop.md) - Infrastructure remediation
- [checkpoint-enforcement.md](checkpoint-enforcement.md) - Progress visibility
- [environment-verification.md](environment-verification.md) - Environment execution rules
- [signal-specification.md](signal-specification.md) - Complete signal formats
- [state-management.md](state-management.md) - State tracking and persistence
- [recovery-procedures.md](recovery-procedures.md) - Error recovery procedures
