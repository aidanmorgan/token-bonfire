# Agent File Recovery

Procedures for recovering missing or corrupted expert advisor prompt files and plan files.

## Overview

Expert advisor prompt files (`.claude/experts/<plan_slug>/*.md`) contain the deep domain research and identity for each named expert advisor. When missing, they must be regenerated through the gap analysis and research process.

See also:

- [Session Recovery](session-recovery.md) - Complete recovery procedures
- [Recovery Index](index.md) - Overview of all recovery procedures

---

## Plan File Recovery

### Integrity Check

On resume, the team lead verifies the plan file exists and is parseable:

1. Check that the plan file path exists
2. Run the bootstrapper: `python .claude/scripts/generate-orchestrator.py "$PLAN_FILE"`
3. Verify the output contains `plan_title`, `plan_slug`, and `tasks`

### Plan File Missing

If the plan file is missing, this is **NOT recoverable** — the team lead must halt and inform the user:

```
RECOVERY HALTED: Plan file not found at <path>.
Cannot continue execution. Please restore the plan file and re-run /bonfire.
```

---

## Expert Advisor Prompt File Recovery

### Detection

The team lead checks for expert advisor files on resume:

1. Look for files at `.claude/experts/<plan_slug>/`
2. If the directory exists and contains `.md` files: **expert advisors found** — load from disk
3. If the directory is empty or missing: **expert advisors missing** — must regenerate

### Recovery Modes

See [session-recovery.md](session-recovery.md) for the complete recovery mode matrix.

### Expert Advisor Regeneration (when files missing)

If expert advisor files are missing but tasks exist in the task list:

1. Team lead runs gap analysis on the plan (same as fresh start step 4a)
2. Team lead performs deep domain research for each expert advisor (step 5a)
3. Team lead generates expert advisor prompt files and saves to `.claude/experts/<plan_slug>/` (step 6a)
4. Team lead spawns fresh expert advisors using the regenerated prompts

This is the most expensive recovery path because it requires re-doing the research synthesis. The persisted files prevent this in normal operation.

---

## Support Teammate Recovery

The critic, ripple, auditor, business-analyst, remediation, and health-auditor teammates do not have persisted prompt files — they are spawned from documentation files in `.claude/docs/agent-creation/`. Recovery is simply respawning them:

1. Team lead calls `requestShutdown` for the crashed teammate (if still running)
2. Team lead respawns the teammate using `Task({ team_name, name, run_in_background: true })` with the same prompt

These teammates are stateless — they process requests from their mailbox and do not need state recovery.

---

## Cross-References

- [Session Recovery](session-recovery.md) - Complete recovery orchestration
- [Team Architecture](../team-architecture.md) - Expert advisor generation and persistence
