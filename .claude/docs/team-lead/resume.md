# Team Lead Resume

Resume session procedures when tasks already exist in `TaskList`.

---

## Navigation

- **[Resume](resume.md)** - This file
- [Communication Protocol](../communication-protocol.md) - Team communication and signals

---

## RESUME FROM EXISTING TASKS (Tasks Exist in TaskList)

**CRITICAL**: The team lead must properly restore state from `TaskList` and handle interrupted work.

### Step 1: Load Task State

Call `TaskList` to retrieve all tasks and their current status. This is the source of truth for what work has been done, what is in progress, and what remains.

### Step 2: Verify Agent Definitions Exist

Check that all required agent definition files exist.

**Required agent definitions:**

| Teammate         | File Path                              |
|------------------|----------------------------------------|
| Developer        | `.claude/agents/developer.md`          |
| Critic           | `.claude/agents/critic.md`             |
| Ripple           | `.claude/agents/ripple.md`             |
| Auditor          | `.claude/agents/auditor.md`            |
| Business Analyst | `.claude/agents/business-analyst.md`   |
| Remediation      | `.claude/agents/remediation.md`        |
| Health Auditor   | `.claude/agents/health-auditor.md`     |

**Decision Logic:**

- If ALL definitions exist -> Use existing, proceed to step 3
- If ANY definition is missing -> Cannot proceed (agent definitions are checked into the repo)

**Also verify expert prompts exist:**

Check the `.claude/experts/<plan_slug>/` directory for expected expert prompt files based on the plan.

For missing expert prompts only, run gap analysis and create the missing ones. Existing expert prompts are reused since they were created for this same plan.

### Step 3: Recreate the Team and Re-spawn Teammates

**IMPORTANT**: `/resume` does NOT restore agent team teammates. The team and all teammates must be recreated from scratch.

**3a. Recreate the team:**
```
TeamCreate({ team_name: "<plan_slug>" })
```

**3b. Re-spawn support teammates** (each uses its agent definition from `.claude/agents/`):
```
Task({ team_name: "<plan_slug>", name: "dev-1", subagent_type: "developer", model: "sonnet", run_in_background: true })
Task({ team_name: "<plan_slug>", name: "critic", subagent_type: "critic", model: "sonnet", run_in_background: true })
Task({ team_name: "<plan_slug>", name: "ripple", subagent_type: "ripple", model: "sonnet", run_in_background: true })
Task({ team_name: "<plan_slug>", name: "auditor", subagent_type: "auditor", model: "opus", run_in_background: true })
Task({ team_name: "<plan_slug>", name: "business-analyst", subagent_type: "business-analyst", model: "sonnet", run_in_background: true })
Task({ team_name: "<plan_slug>", name: "remediation", subagent_type: "remediation", model: "sonnet", run_in_background: true })
Task({ team_name: "<plan_slug>", name: "health-auditor", subagent_type: "health-auditor", model: "haiku", run_in_background: true })
```

**3c. Re-spawn expert advisors** (inline prompts from persisted files):
```
for each expert prompt file in .claude/experts/<plan_slug>/:
    Task({
      team_name: "<plan_slug>",
      name: "<expert-name>",
      subagent_type: "general-purpose",
      model: "sonnet",
      prompt: "<content of expert prompt file>",
      run_in_background: true
    })
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

Tasks completed recently (within the current or previous session) should be re-audited to ensure subsequent work did not break them:

For each recently completed task:
1. Route to `auditor` teammate via mailbox for re-verification (do NOT reset status to `pending` unless the auditor fails — `completed` status is only cleared if the re-audit fails)
2. If re-audit fails: `TaskUpdate({ taskId, status: "in_progress" })` to allow rework

**Rationale**: Tasks completed near session end may have passed audit but subsequent work could have broken them. Re-verification ensures integrity.

### Step 7: Reconcile Tasks with Plan

Check if the plan file has changed since the tasks were created:

- If new tasks added -> create via `TaskCreate`, then set dependencies via `TaskUpdate({ addBlockedBy })`
- If tasks removed -> update status to reflect removal (log warning)
- If task specs changed -> mark as needing re-implementation if already complete

### Step 8: Proceed to Execution Loop

Begin the main loop: assign tasks to developers as they send `REQUESTING_WORK`, monitor mailbox for results, route through Developer -> Critic -> Ripple -> Auditor pipeline.

---

## Related Documentation

- [Communication Protocol](../communication-protocol.md) - Team communication and signals
