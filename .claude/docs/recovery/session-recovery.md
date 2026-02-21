# Session Recovery

Complete session recovery procedures that orchestrate all recovery mechanisms on resume.

## Overview

Session recovery runs automatically when the team lead detects a resume scenario (re-running `/bonfire $PLAN_FILE`). The native Agent Teams primitives handle most recovery automatically — the team lead primarily needs to audit state and respawn teammates.

See also:

- [Agent Recovery](agent-file-recovery.md) - Expert advisor prompt file recovery
- [Baseline Failures](baseline-failures.md) - Pre-existing failure tracking
- [Recovery Index](index.md) - Overview of all recovery procedures

---

## Resume Detection

The team lead determines the resume mode by checking two things:

1. **Expert advisor definitions on disk**: Do files exist at `.claude/experts/<plan_slug>/`?
2. **Shared task list**: Does `TaskList` return existing tasks?

| Expert advisors on disk? | Tasks exist? | Mode |
|---|---|---|
| No | No | **FRESH START** — full bootstrap |
| Yes | Yes | **RESUME** — load expert advisors, audit tasks, spawn team |
| Yes | No | **EXPERT REUSE** — load expert advisors, create tasks, spawn team |
| No | Yes | **ORPHANED TASKS** — regenerate expert advisors, audit tasks, spawn team |

## Resume Flow (most common recovery path)

When both expert advisor files and tasks exist:

### 1. Load Expert Advisor Definitions

Read all `.md` files from `.claude/experts/<plan_slug>/`. Log the roster:

```
LOADED EXPERT ADVISORS from .claude/experts/<plan_slug>/:
  1. <expert-name> - <domain description>
  2. <expert-name> - <domain description>
```

### 2. Audit Task State

Call `TaskList` and report current state:

```
TASK AUDIT for <plan_slug>:
  Completed: <list of completed task subjects>
  In Progress: <list - likely orphaned by crashed experts>
  Pending (blocked): <list with their blockers>
  Pending (ready): <list - ready to be claimed>
  Needs Rework: <list - had review failures>
```

### 3. Handle Orphaned Tasks

Tasks that are `in_progress` but have no active developer are orphaned from a crashed session. These auto-release after the heartbeat timeout (~5 min). The team lead can note them but does not need to manually intervene — fresh developers will claim them once released.

### 4. Validate Plan File

Run the bootstrapper to verify the plan file is still valid:

```bash
python .claude/scripts/generate-orchestrator.py "$PLAN_FILE"
```

If the plan file is missing, halt and inform the user.

### 5. Spawn Fresh Teammates

Spawn all teammates using documentation and persisted expert advisor prompts:

- Developers (generic, parallel) from developer prompt
- Named expert advisors from `.claude/experts/<plan_slug>/` files
- Critic, ripple, auditor, business-analyst, remediation, health-auditor from documentation

### 6. Resume Normal Operation

Developers claim pending tasks from the shared task list. The team lead enters the monitoring loop.

---

## Recovery Summary

After recovery, the team lead reports:

```
SESSION RECOVERED for <plan_slug>:
  Mode: RESUME
  Expert advisors loaded: <N> from disk
  Developers spawned: <N>
  Tasks: <completed>/<total> complete
  Orphaned in-progress: <N> (will auto-release)
  Pending (ready): <N> tasks available
  Total teammates spawned: <N>
```

---

## Cross-References

- [Agent Recovery](agent-file-recovery.md) - Expert advisor prompt file recovery
- [Task List Recovery](state-recovery.md) - Task state audit
- [Baseline Failures](baseline-failures.md) - Pre-existing failure baseline
- [Session Management](../session-management.md) - Session lifecycle
- [Team Architecture](../team-architecture.md) - Resume and crash recovery
