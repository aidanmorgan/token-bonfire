# Task Delivery Loop

This document specifies the step-by-step procedure for the coordinator to dispatch tasks, parse results, and route work
through the system.

## Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         COORDINATOR LOOP                                 │
├─────────────────────────────────────────────────────────────────────────┤
│  1. SELECT TASK                                                          │
│     ↓                                                                    │
│  2. PREPARE PROMPT (expand templates, include references)                │
│     ↓                                                                    │
│  3. DISPATCH DEVELOPER (Task tool)                                       │
│     ↓                                                                    │
│  4. PARSE DEVELOPER SIGNAL (READY_FOR_REVIEW)                            │
│     ↓                                                                    │
│  5. DISPATCH CRITIC (Task tool)                                          │
│     ↓                                                                    │
│  6. PARSE CRITIC OUTCOME (REVIEW_PASSED | REVIEW_FAILED)                 │
│     ↓                                                                    │
│  7. IF REVIEW_FAILED → rework | IF REVIEW_PASSED → continue              │
│     ↓                                                                    │
│  8. DISPATCH AUDITOR (Task tool)                                         │
│     ↓                                                                    │
│  9. PARSE AUDIT OUTCOME                                                  │
│     ↓                                                                    │
│ 10. ROUTE: PASS → complete | FAIL → rework | BLOCKED → remediation       │
│     ↓                                                                    │
│ 11. LOOP (fill actor slots)                                              │
└─────────────────────────────────────────────────────────────────────────┘
```

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

## Step 5: Dispatch Critic

**Input**: Task ID, developer completion signal

**Procedure**:

1. Prepare critic prompt with modified files and task context
2. Dispatch Critic agent
3. Await `REVIEW_PASSED` or `REVIEW_FAILED`

See [review-audit-flow.md](review-audit-flow.md) for the full Critic dispatch procedure.

---

## Step 6: Dispatch Auditor

**Input**: Task ID, files modified, acceptance criteria

**Procedure**:

1. Extract task acceptance criteria and modified files
2. Include required reading and verification commands
3. Dispatch Auditor agent
4. Parse audit outcome

See [review-audit-flow.md](review-audit-flow.md) for the full Auditor dispatch procedure.

**Output**: Audit outcome (PASS | FAIL | BLOCKED) + details

---

## Step 7: Route Based on Outcome

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

```python
# Check failure count
audit_failures[task_id] = audit_failures.get(task_id, 0) + 1

if audit_failures[task_id] >= TASK_FAILURE_LIMIT:
    log_event("workflow_failed", reason="task exceeded failure limit")
else:
    # Return to developer with fix requirements
    dispatch_developer_rework(task_id, audit_failures)
```

See [developer-rework.md](developer-rework.md) for rework dispatch details.

### BLOCKED Routing

```python
infrastructure_blocked = True
infrastructure_issue = parse_blocked_reason(auditor_output)
dispatch_remediation_agent(infrastructure_issue)
```

See [remediation-loop.md](remediation-loop.md) for the full remediation procedure.

---

## Step 8: Fill Actor Slots

After any routing decision, immediately check and fill actor slots:

```python
while count_active_actors() < ACTIVE_DEVELOPERS:
    if not available_tasks:
        break
    if infrastructure_blocked:
        break
    if pending_divine_questions:
        break

    task = select_next_task()
    dispatch_developer(task)
```

---

## Coordinator State Machine

```
                     ┌──────────────────┐
                     │  SELECT_TASK     │
                     └────────┬─────────┘
                              │
                              ▼
                     ┌──────────────────┐
                     │ DISPATCH_DEV     │
                     └────────┬─────────┘
                              │
                              ▼
                     ┌──────────────────┐
              ┌──────┤ AWAIT_DEV        ├──────┐
              │      └────────┬─────────┘      │
              │               │                │
         DELEGATION    READY_FOR_REVIEW  DIVINE_QUESTION
              │               │                │
              ▼               ▼                ▼
    ┌─────────────────┐ ┌──────────────┐ ┌─────────────────┐
    │ HANDLE_DELEGATE │ │DISPATCH_CRIT │ │ AWAIT_DIVINE    │
    └────────┬────────┘ └──────┬───────┘ └────────┬────────┘
              │                │                   │
              │                ▼                   │
              │      ┌──────────────────┐         │
              │      │ AWAIT_CRITIC     │         │
              │      └────────┬─────────┘         │
              │               │                   │
              │    ┌──────────┴──────────┐       │
              │    │                     │       │
              │ REVIEW_PASSED      REVIEW_FAILED │
              │    │                     │       │
              │    ▼                     │       │
              │ ┌──────────────┐         │       │
              │ │ DISPATCH_AUD │         │       │
              │ └──────┬───────┘         │       │
              │        │                 │       │
              │        ▼                 │       │
              │ ┌──────────────────┐     │       │
              │ │ AWAIT_AUDIT      │     │       │
              │ └────────┬─────────┘     │       │
              │          │               │       │
              │  ┌───────┼───────┐       │       │
              │  │       │       │       │       │
              │ PASS    FAIL  BLOCKED    │       │
              │  │       │       │       │       │
              │  ▼       ▼       ▼       ▼       │
              │┌────┐┌──────┐┌────────┐┌──────┐  │
              ││TASK││REWORK││REMEDIATE││REWORK│  │
              ││DONE││      ││        ││      │  │
              │└─┬──┘└──┬───┘└───┬────┘└──┬───┘  │
              │  │      │        │        │      │
              └──┴──────┴────────┴────────┴──────┘
                              │
                              ▼
                     ┌──────────────────┐
                     │ FILL_SLOTS       │
                     └────────┬─────────┘
                              │
                              ▼
                          (loop)
```

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
