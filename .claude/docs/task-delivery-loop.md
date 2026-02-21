# Task Delivery Loop

This document specifies the step-by-step procedure for the team lead to route tasks, receive results via mailbox, and
manage the developer -> critic -> ripple -> auditor pipeline.

## Overview

The task delivery loop has two phases, each detailed in separate documents:

**Phase A: Task Dispatch** ([task-dispatch.md](task-dispatch.md)):

1. SELECT TASK - Choose from available, unblocked tasks via `TaskList`
2. PREPARE ASSIGNMENT - Expand templates, include references
3. ROUTE TO DEVELOPER - Send assignment via `TeammateTool({ operation: "write" })`
4. RECEIVE DEVELOPER RESULT - Monitor mailbox for `READY_FOR_REVIEW`

**Phase B: Review, Ripple Analysis & Audit** ([review-audit-flow.md](review-audit-flow.md)):

5. ROUTE TO CRITIC - Code quality review via mailbox
6. RECEIVE CRITIC OUTCOME - `REVIEW_PASSED` or `REVIEW_FAILED`
7. ROUTE TO RIPPLE - Second-order effects analysis via mailbox
8. RECEIVE RIPPLE OUTCOME - `RIPPLE_PASSED` or `RIPPLE_FAILED`
9. ROUTE TO AUDITOR - Acceptance criteria verification via mailbox
10. RECEIVE AUDIT OUTCOME - `AUDIT_PASSED`, `AUDIT_FAILED`, or `AUDIT_BLOCKED`
11. ROUTE - PASS -> complete | FAIL -> rework | BLOCKED -> remediation

After routing, fill developer slots and loop.

---

## Step 1: Select Task

**Input**: Tasks from `TaskList`

**Procedure**:

1. Call `TaskList` to get all tasks
2. Filter tasks where status is "pending" and all `blockedBy` have status "completed"
3. Sort by priority (phase order, then dependency count)
4. Select top N tasks where N = `MAX_DEVELOPERS` - active developer count

**Output**: List of task IDs to route

---

## Step 2: Prepare Assignment

**Input**: Task ID, plan content, developer name

**The team lead builds the assignment by combining:**

1. **Task-Specific Context** (from plan and configuration)
2. **Developer Agent Definition** (`.claude/agents/developer.md`, loaded automatically via `subagent_type: "developer"`)

See [task-dispatch.md](task-dispatch.md) for the detailed assignment construction procedure.

**Key Elements**:

- Task work description and acceptance criteria
- Required reading files (MUST READ + REFERENCE)
- Verification commands and environments

**Output**: Complete assignment message

---

## Step 3: Route to Developer

**Input**: Prepared assignment, task ID, developer name

**Procedure**:

1. Update task status: `TaskUpdate({ taskId, status: "in_progress" })`
2. Send via mailbox: `TeammateTool({ operation: "write", to: "<developer>", content: "<assignment>" })`

See [task-dispatch.md](task-dispatch.md) for routing details.

**Output**: Developer is now working on the task

---

## Step 4: Receive Developer Result

**Input**: Developer's mailbox message

**Signal Detection**: Read mailbox messages for these patterns:

- `READY_FOR_REVIEW: <task_id>` -> Validate environment matrix, route to critic
- `NEED_EXPERT_ADVICE: <task_id>` -> Route question to appropriate expert advisor, relay response back
- `SEEKING_DIVINE_CLARIFICATION` -> Ask user for clarification
- `INFRA_BLOCKED: <task_id>` -> Route to remediation teammate

**Environment Verification**: Before routing to critic, validate the environment matrix is complete.

**Output**: Parsed result or blocker information

---

## Steps 5-6: Critic Review

**Input**: Task ID, developer's READY_FOR_REVIEW message

See [review-audit-flow.md](review-audit-flow.md) for the full critic routing and response handling.

**Summary**:

1. Route review request to `critic` teammate via mailbox
2. Receive critic response: `REVIEW_PASSED` -> continue to ripple | `REVIEW_FAILED` -> developer rework

---

## Steps 7-8: Ripple Analysis

**Input**: Task ID, files modified, REVIEW_PASSED message

**Summary**:

1. Route ripple analysis request to `ripple` teammate via mailbox
2. Receive ripple response: `RIPPLE_PASSED` -> continue to auditor | `RIPPLE_FAILED` -> developer rework

Ripple analyzes second-order effects: broken consumers, altered API contracts, test coverage gaps, behavioral drift in callers. Ripple is read-only and never edits files. It does NOT review first-order code quality (that is the critic's role) or acceptance criteria (that is the auditor's role).

---

## Steps 9-10: Auditor Verification

**Input**: Task ID, files modified, acceptance criteria

See [review-audit-flow.md](review-audit-flow.md) for the full auditor routing and response handling.

**Summary**:

1. Route audit request to `auditor` teammate via mailbox
2. Receive audit response: PASS | FAIL | BLOCKED

---

## Step 11: Route Based on Outcome

### PASS Routing

On `AUDIT_PASSED`:

1. Update task status: `TaskUpdate({ taskId, status: "completed" })`
2. Check `TaskList` for tasks that were blocked by this one - they may now be unblocked
3. Route new work to idle developers

### FAIL Routing

On `AUDIT_FAILED`, `RIPPLE_FAILED`, or `REVIEW_FAILED`:

1. Increment failure count for the task
2. Check against `TASK_FAILURE_LIMIT`
3. If under limit: route rework to the developer via mailbox (see [developer-rework.md](developer-rework.md))
4. If at limit: escalate to user
5. Update task status: `TaskUpdate({ taskId, status: "in_progress" })`

### BLOCKED Routing

On `AUDIT_BLOCKED` (infrastructure issues):

1. Route to `remediation` teammate via mailbox:
   ```
   TeammateTool({ operation: "write", to: "remediation",
                  content: "INFRA_BLOCKED: <issue description>" })
   ```
2. Hold task assignments until remediation completes

---

## Fill Developer Slots (After Each Routing Decision)

After any routing decision, immediately check and fill developer slots.

**CRITICAL: Route in priority order - complete in-flight work before starting new work.**

Priority order:

1. **Route pending reviews to critic** - Tasks waiting for review should not be starved by new work
2. **Route pending ripple analyses to ripple** - Tasks that passed review should get impact analysis before audit
3. **Route pending audits to auditor** - Tasks that passed ripple should complete before new work starts
4. **Route new tasks to developers** - Only start new work after in-flight work is being processed

**Why this order matters:**

- Completing in-flight work unblocks dependent tasks faster
- Prevents task starvation where reviews pile up while new work starts
- Ensures the full Developer -> Critic -> Ripple -> Auditor pipeline flows smoothly

---

## Team Lead State Machine

**States**: SELECT_TASK -> ROUTE_DEVELOPER -> AWAIT_DEVELOPER

**From AWAIT_DEVELOPER**:

- READY_FOR_REVIEW -> ROUTE_CRITIC -> AWAIT_CRITIC
- DIVINE_QUESTION -> AWAIT_USER -> back to loop

**From AWAIT_CRITIC**:

- REVIEW_PASSED -> ROUTE_RIPPLE -> AWAIT_RIPPLE
- REVIEW_FAILED -> DEVELOPER_REWORK -> back to loop

**From AWAIT_RIPPLE**:

- RIPPLE_PASSED -> ROUTE_AUDITOR -> AWAIT_AUDITOR
- RIPPLE_FAILED -> DEVELOPER_REWORK -> back to loop

**From AWAIT_AUDITOR**:

- PASS -> TASK_DONE -> FILL_SLOTS -> loop
- FAIL -> DEVELOPER_REWORK -> FILL_SLOTS -> loop
- BLOCKED -> ROUTE_REMEDIATION -> FILL_SLOTS -> loop

### Task States (via TaskUpdate)

The shared task list supports only three status values via `TaskUpdate`:

| Status       | Meaning                                                     |
|--------------|-------------------------------------------------------------|
| `pending`    | Available for developer assignment (created or reset)       |
| `in_progress`| Developer claimed and working                               |
| `completed`  | Auditor PASSED — only terminal state                        |

**Pipeline stages are NOT task statuses.** The team lead tracks the review pipeline (critic review, ripple analysis, audit) in its own context as routing state — these do NOT map to `TaskUpdate` status values.

**Critical**: Only `AUDIT_PASSED` marks a task as completed via `TaskUpdate({ status: "completed" })`.

The team lead's internal routing states (tracked in team lead context only):

| Team Lead Routing State | Meaning                                          |
|-------------------------|--------------------------------------------------|
| `pending_review`        | Developer signaled ready, routing to critic       |
| `in_critic_review`      | Critic is reviewing                               |
| `in_ripple_review`      | Critic passed, ripple analyzing                   |
| `pending_audit`         | Ripple passed, routing to auditor                 |
| `in_audit`              | Auditor is verifying                              |
| `needs_rework`          | Review/audit failed, feedback sent to developer   |

---

## Signal Detection Summary

### Task Flow Signals (from mailbox messages)

| Signal           | Content Pattern              | Handler              |
|------------------|------------------------------|----------------------|
| Ready for review | `READY_FOR_REVIEW: <id>`     | -> route to critic   |
| Expert advice    | `NEED_EXPERT_ADVICE: <id>`   | -> route to expert advisor |
| Advice provided  | `EXPERT_ADVICE_PROVIDED: <id>`| -> relay to developer|
| Task incomplete  | `TASK_INCOMPLETE: <id>`      | -> log, fill slots   |
| Review passed    | `REVIEW_PASSED: <id>`        | -> route to ripple   |
| Review failed    | `REVIEW_FAILED: <id>`        | -> developer rework  |
| Ripple passed    | `RIPPLE_PASSED: <id>`        | -> route to auditor  |
| Ripple failed    | `RIPPLE_FAILED: <id>`        | -> developer rework  |
| Audit pass       | `AUDIT_PASSED: <id>`         | -> **TASK COMPLETE** |
| Audit fail       | `AUDIT_FAILED: <id>`         | -> developer rework  |
| Audit blocked    | `AUDIT_BLOCKED: <id>`        | -> route remediation |
| Infra blocked    | `INFRA_BLOCKED: <id>`        | -> route remediation |

### Remediation Signals

| Signal               | Content Pattern               | Handler                 |
|----------------------|-------------------------------|-------------------------|
| Remediation complete | `REMEDIATION_COMPLETE`        | -> route health audit   |
| Health healthy       | `HEALTH_AUDIT: HEALTHY`       | -> resume flow          |
| Health unhealthy     | `HEALTH_AUDIT: UNHEALTHY`     | -> loop remediation     |

### Coordination Signals

| Signal             | Content Pattern                  | Handler               |
|--------------------|----------------------------------|-----------------------|
| User question      | `SEEKING_DIVINE_CLARIFICATION`   | -> ask user           |

---

## Error Recovery

| Error Type       | Recovery Action                                         |
|------------------|---------------------------------------------------------|
| Teammate idle    | Re-send work via mailbox                                |
| Parse failure    | Log message, treat as incomplete                        |
| Task stuck       | Reset via `TaskUpdate({ status: "pending" })`, re-route  |

---

## Related Documentation

- [task-dispatch.md](task-dispatch.md) - Assignment construction and routing details
- [review-audit-flow.md](review-audit-flow.md) - Critic and Auditor routing
- [developer-rework.md](developer-rework.md) - Rework routing after failures
- [team-architecture.md](team-architecture.md) - Team structure and communication
- [coordinator-configuration.md](coordinator-configuration.md) - Configuration values
