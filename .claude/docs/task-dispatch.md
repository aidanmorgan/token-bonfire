# Task Dispatch

This document covers how the team lead selects tasks, prepares assignments, and routes work to developer agents via
mailbox messages.

**Related Documents:**

- [review-audit-flow.md](review-audit-flow.md) - Critic and Auditor flow
- [team-architecture.md](team-architecture.md) - Team structure and communication
- [task-delivery-loop.md](task-delivery-loop.md) - Full delivery loop overview

---

## Overview

**Task Dispatch**:

1. SELECT TASK (from available, unblocked tasks via `TaskList`)
2. PREPARE ASSIGNMENT (expand templates, include references)
3. ROUTE TO DEVELOPER (via `TeammateTool({ operation: "write", to: "<dev-N>", content: "..." })`)
4. MONITOR MAILBOX -> receive `READY_FOR_REVIEW` signal from developer
   -> Continue to [review-audit-flow.md](review-audit-flow.md)

---

## Step 1: Select Task

**Input**: Tasks from `TaskList` with various statuses

**Procedure**:

1. Call `TaskList` to get all tasks and their statuses
2. Filter tasks where status is "pending" and all `blockedBy` dependencies have status "completed"
3. Sort by priority (phase order, then number of dependents - tasks with more dependents first)
4. Select up to N tasks where N = NUM_DEVELOPERS - currently active developers

**Output**: List of task IDs to route to developers

---

## Step 2: Prepare Assignment

**Input**: Task ID, plan content, developer name

**The team lead builds the assignment message by combining:**

1. **Task-Specific Context** (from plan and configuration)
2. **Developer Agent Definition** (`.claude/agents/developer.md`, loaded automatically via `subagent_type: "developer"`) and **Expert Advisor Definitions** (from `.claude/experts/{{PLAN_NAME}}/<name>.md`)

### Assignment Elements

1. Extract task details from `PLAN_FILE`:
    - Work description
    - Acceptance criteria
    - Blocked by (dependencies)
    - Required reading (task-specific files)

2. Match expert advisors to tasks based on keyword triggers from expert advisor definitions:
    - Extract task keywords from work description and acceptance criteria
    - Match against expert advisor `keyword_triggers`
    - Categorize as RECOMMENDED, SUGGESTED, or AVAILABLE

3. Expand template placeholders:
    - `{{#each VERIFICATION_COMMANDS}}` -> actual commands from config
    - `{{#each ENVIRONMENTS}}` -> environment definitions

4. **Include required reading** (CRITICAL - developers have no implicit knowledge):
    - Include both MUST READ files and REFERENCE files
    - Include task-specific Required Reading from the plan
    - Format as explicit file paths, not patterns

### Required Reading Format

All assignment messages MUST include:

```markdown
## Required Reading

**MUST READ** - Read these files FIRST, before any implementation work:

- `path/to/file`: purpose
- Task-specific files from plan

**REFERENCE** - Consult as needed during work:

- `path/to/docs`: purpose

IMPORTANT: You MUST read all MUST READ files before starting work.
```

---

## Step 3: Route to Developer

**Input**: Prepared assignment, task ID, developer name

### Procedure

1. **Update task status**:
   ```
   TaskUpdate({ taskId: task_id, status: "in_progress" })
   ```

2. **Send assignment via mailbox**:
   ```
   TeammateTool({
       operation: "write",
       to: "<dev-N>",
       content: "<prepared assignment message>"
   })
   ```

3. The developer reads its mailbox, picks up the assignment, and begins work.

### Routing Multiple Tasks

When multiple developer slots are available, route all assignments in sequence:

```
TaskUpdate({ taskId: "task-1", status: "in_progress" })
TeammateTool({ operation: "write", to: "dev-1", content: "Assignment for task-1..." })

TaskUpdate({ taskId: "task-2", status: "in_progress" })
TeammateTool({ operation: "write", to: "dev-2", content: "Assignment for task-2..." })
```

---

## Step 4: Receive Developer Results

**Input**: Developer's mailbox message (read from team lead's mailbox)

The team lead monitors its mailbox for messages from developers. Developers send their results as plain-text mailbox messages containing signal keywords.

### READY_FOR_REVIEW Signal

Developers signal readiness for review with a message containing:

```
READY_FOR_REVIEW: <task_id>

Files Modified:
- <file_path>
- <file_path>

Tests Written:
- <test_file>: <what_it_tests>

Verification Results (self-verified):
- <check_name>: PASS

Summary:
<brief_description_of_implementation>
```

### On READY_FOR_REVIEW

1. Validate the task ID matches an in-progress task
2. Extract files modified and verification results
3. Team lead tracks task as `in_critic_review` in its review pipeline (team lead context only — no TaskUpdate needed; task status remains `in_progress`)
4. **Route to critic** -> Continue to [review-audit-flow.md](review-audit-flow.md)

### Other Signals

| Signal                         | Content Pattern                   | Next Action                |
|--------------------------------|-----------------------------------|----------------------------|
| `READY_FOR_REVIEW`             | `READY_FOR_REVIEW: <task_id>`     | Route to critic            |
| `TASK_INCOMPLETE`              | `TASK_INCOMPLETE: <task_id>`      | Log, route new work        |
| `INFRA_BLOCKED`                | `INFRA_BLOCKED: <task_id>`        | Route to remediation       |
| `SEEKING_DIVINE_CLARIFICATION` | (no task ID)                      | Ask user                   |

### TASK_INCOMPLETE Signal

If developer cannot complete:

```
TASK_INCOMPLETE: <task_id>

Blocker: <description>
Attempted: <what_was_tried>
Needed: <what_would_unblock>
```

---

## Next Steps

After receiving developer results:

- On `READY_FOR_REVIEW` -> [review-audit-flow.md](review-audit-flow.md) (Route to critic)
- On `INFRA_BLOCKED` -> Route to `remediation` teammate via mailbox
- On `TASK_INCOMPLETE` -> Route new work to developer, log event

---

## Cross-References

- [review-audit-flow.md](review-audit-flow.md) - Critic and Auditor flow
- [task-delivery-loop.md](task-delivery-loop.md) - Full delivery loop
- [team-architecture.md](team-architecture.md) - Team structure and communication
- [coordinator-configuration.md](coordinator-configuration.md) - Configuration values
