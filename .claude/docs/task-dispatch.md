# Task Dispatch

The team lead is the sole task assigner. Developers never claim tasks themselves. When a developer is idle, they send `REQUESTING_WORK` to the team lead, who selects the next task, retrieves it via `TaskGet`, and sends the full detail as an assignment.

> **Note**: The native Claude Code Agent Teams pattern is **self-claiming** — teammates independently call `TaskList`, find unclaimed tasks, and claim them via `TaskUpdate`. Bonfire deliberately uses **push-based assignment** instead, where the team lead centrally assigns tasks. This enables priority ordering, review pipeline routing, expert consultation coordination, and prevents developers from calling `TaskUpdate` to claim tasks themselves.

## Assignment Flow

```
Developer → SendMessage(REQUESTING_WORK) → Team Lead
Team Lead → TaskList (find pending, unblocked) → select task
Team Lead → TaskGet({ taskId }) → full task detail
Team Lead → TaskUpdate({ taskId, status: "in_progress", owner: "<dev-name>" })
Team Lead → SendMessage(TASK_ASSIGNMENT + full detail) → Developer
Developer → implements → self-verifies → SendMessage(READY_FOR_REVIEW) → Team Lead
Team Lead → routes to review pipeline (see review-audit-flow.md)
```

## Step 1: Select Task

When a developer sends `REQUESTING_WORK`:

1. Call `TaskList` to get all tasks and their statuses
2. Filter tasks where status is `pending` and `blockedBy` is empty (completed dependencies are automatically removed from `blockedBy`)
3. Sort by priority (phase order, then number of dependents — tasks with more dependents first)
4. Select one task for the requesting developer

If no tasks are available (all completed, in-progress, or blocked), inform the developer:

```
SendMessage({
  type: "message",
  recipient: "<dev-name>",
  content: "NO_TASKS_AVAILABLE: All tasks are either completed, in-progress by other developers, or blocked. Stand by for review feedback or new work.",
  summary: "No tasks available"
})
```

## Step 2: Retrieve Full Task Detail

Call `TaskGet({ taskId: "<selected-task-id>" })` to get the full task description including:
- Work to be done
- Acceptance criteria
- Required reading (files to read before starting)
- Dependencies and context

## Step 3: Assign to Developer

1. **Mark task as assigned:**
   ```
   TaskUpdate({ taskId: "<id>", status: "in_progress", owner: "<dev-name>" })
   ```

2. **Send full assignment via message:**
   ```
   SendMessage({
     type: "message",
     recipient: "<dev-name>",
     content: "TASK_ASSIGNMENT: <task-id>\n\nSubject: <subject>\n\n<full description from TaskGet including work, acceptance criteria, required reading, environment>",
     summary: "Assigned task <task-id>"
   })
   ```

## Step 4: Receive Developer Results

Monitor mailbox for developer messages:

| Signal | Next Action |
|--------|-------------|
| `READY_FOR_REVIEW: <task-id>` | Route to critic (see [review-audit-flow.md](review-audit-flow.md)) |
| `REQUESTING_WORK` | Assign next available task |
| `NEED_EXPERT_ADVICE: <expert-name> <question>` | Forward to named expert |
| `NEED_CLARIFICATION: <question>` | Route to business-analyst or `AskUserQuestion` |
| `INFRA_BLOCKED: <details>` | Forward to remediation |
| `FILE_CONFLICT: <file> <details>` | Coordinate ownership between developers |

## Initial Assignment Burst

After spawning the team, developers will immediately send `REQUESTING_WORK`. Assign one task per developer in the order requests arrive, until all developers have work or all available tasks are assigned.
