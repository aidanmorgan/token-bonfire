# Team Lead Resume

Resume session procedures when tasks already exist in `TaskList`.

---

## Navigation

- [Fresh Start](fresh-start.md) - Fresh session initialization
- **[Resume](resume.md)** - This file
- [Team Lead Configuration](../coordinator-configuration.md) - Configuration values
- [Team Architecture](../team-architecture.md) - Team structure and communication

---

## RESUME FROM EXISTING TASKS (Tasks Exist in TaskList)

**CRITICAL**: The team lead must properly restore state from `TaskList` and handle interrupted work.

### Step 1: Load Task State

Call `TaskList` to retrieve all tasks and their current status. This is the source of truth for what work has been done, what is in progress, and what remains.

### Step 2: Verify Agent Definitions Exist

Check that all required agent definition files exist.

**Required agent definitions:**

| Teammate         | File Path                          |
|------------------|------------------------------------|
| Developer        | `.claude/agents/developer.md`      |
| Critic           | `.claude/agents/critic.md`         |
| Auditor          | `.claude/agents/auditor.md`        |

**Decision Logic:**

- If ALL definitions exist -> Use existing, proceed to step 3
- If ANY definition is missing -> Cannot proceed (agent definitions are checked into the repo)

**Also verify expert prompts exist:**

Check the `.claude/experts/{{PLAN_NAME}}/` directory for expected expert prompt files based on the plan.

For missing expert prompts only, run gap analysis and create the missing ones. Existing expert prompts are reused since they were created for this same plan.

### Step 3: Re-spawn the Team

All named teammates must be re-spawned since they do not persist across sessions:

```
Task({ team_name: "bonfire", name: "critic", run_in_background: true, ... })
Task({ team_name: "bonfire", name: "auditor", run_in_background: true, ... })
Task({ team_name: "bonfire", name: "business-analyst", run_in_background: true, ... })
Task({ team_name: "bonfire", name: "remediation", run_in_background: true, ... })
Task({ team_name: "bonfire", name: "health-auditor", run_in_background: true, ... })

# Re-spawn expert agents
for each expert prompt file in .claude/experts/{{PLAN_NAME}}/:
    Task({ team_name: "bonfire", name: expert.name, run_in_background: true,
           prompt: Read(expert prompt file) })
```

### Step 4: Handle In-Progress Tasks

All tasks with status `in_progress` in `TaskList` are considered **INCOMPLETE** and must be restarted:

For each in-progress task:
1. Call `TaskUpdate({ taskId, status: "pending" })` to reset it
2. The task becomes available for developer assignment again

**Rationale**: We cannot know the state of interrupted teammates. Partial work may exist but is unreliable. Starting fresh is safer.

### Step 5: Handle In-Review Tasks

Since review pipeline stages are tracked in the team lead context (not as `TaskUpdate` statuses), tasks in the shared task list will only be `in_progress` or `completed` when the session resumes. Any task that was mid-review is treated as incomplete since the review never completed:

For each task that was `in_progress` (already handled in Step 4, which resets to `pending`), the team lead restarts the full Developer -> Critic -> Ripple -> Auditor pipeline from scratch. No special handling is needed for review pipeline state — it is reconstructed as developers re-implement and re-signal.

### Step 6: Re-Verify Recent Completions

Tasks completed recently (within `{{RECENT_COMPLETION_WINDOW}}`) should be re-audited to ensure subsequent work did not break them:

For each recently completed task:
1. Route to `auditor` teammate via mailbox for re-verification (do NOT reset status to `pending` unless the auditor fails — `completed` status is only cleared if the re-audit fails)
2. If re-audit fails: `TaskUpdate({ taskId, status: "in_progress" })` to allow rework

**Rationale**: Tasks completed near session end may have passed audit but subsequent work could have broken them. Re-verification ensures integrity.

### Step 7: Reconcile Tasks with Plan

Check if `{{PLAN_FILE}}` has changed since the tasks were created:

- If new tasks added -> create via `TaskCreate` with appropriate `blockedBy`
- If tasks removed -> update status to reflect removal (log warning)
- If task specs changed -> mark as needing re-implementation if already complete

### Step 8: Proceed to Execution Loop

Begin the main loop: developers claim available tasks, monitor mailbox for results, route through Developer -> Critic -> Ripple -> Auditor pipeline.

---

## Related Documentation

- [Fresh Start](fresh-start.md) - Fresh session initialization
- [Team Lead Configuration](../coordinator-configuration.md) - Configuration values
- [Team Architecture](../team-architecture.md) - Team structure and communication
