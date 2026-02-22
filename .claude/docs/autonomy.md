# Autonomy Boundaries

[← Back to Documentation Index](index.md)

This document defines hard constraints on agent autonomy. These are NOT guidelines — they are invariants that must hold at all times. Violation indicates a system failure.

---

## Team Lead Autonomy Constraints

### INVARIANT 1: Every Task Must Complete the Full Pipeline

A task is NOT complete until it has passed through ALL pipeline stages in order:

```
Developer → Critic → Ripple → Auditor → AUDIT_PASSED → TaskUpdate(completed)
```

**No exceptions. No shortcuts. No "already implemented" bypass.**

| Scenario | Required Action |
|----------|----------------|
| Developer says "already implemented, tests pass" | Still route through critic → ripple → auditor |
| Task involves only verification (no code changes) | Still route through critic → ripple → auditor |
| Developer self-verified with pyright + pytest | Still route through critic → ripple → auditor |
| Critic times out 3 times | Escalate to user via AskUserQuestion — do NOT skip to auditor |
| Team lead believes the change is trivial | Still route through critic → ripple → auditor |

**Why**: The critic catches quality issues the developer missed. The ripple catches downstream impacts. The auditor independently verifies acceptance criteria. Skipping any stage means unverified code ships.

### INVARIANT 2: Only AUDIT_PASSED Triggers Task Completion

The team lead MUST NOT call `TaskUpdate({ status: "completed" })` unless the auditor has explicitly signaled `AUDIT_PASSED` for that specific task ID.

**Forbidden patterns:**
- Marking a task complete because the developer said tests pass
- Marking a task complete because the team lead verified it independently
- Marking a task complete because the critic or ripple passed (without auditor)
- Marking a task complete because the code was "already implemented"

### INVARIANT 3: The Team Lead Does Not Implement

The team lead MUST use Delegate Mode (Shift+Tab). The team lead:
- Does NOT write code
- Does NOT edit files
- Does NOT run developer commands
- Does NOT spawn standalone Task agents as a substitute for the team pipeline

**If the team approach fails** (idle loops, messaging issues), the team lead MUST:
1. Diagnose and fix the team communication issue
2. Respawn crashed teammates
3. Escalate to the user if the team cannot be recovered

The team lead MUST NOT abandon the team and use direct Task agents as a workaround. This bypasses the entire quality pipeline.

### INVARIANT 4: Experts Are Advisory Only

Expert advisors MUST NOT be:
- Assigned implementation tasks
- Asked to write or edit code
- Used as substitute developers
- Routed review or audit work

Expert advisors activate ONLY when:
- A developer signals `NEED_EXPERT_ADVICE` through the team lead
- The team lead needs domain guidance for task assignment decisions

### INVARIANT 5: All Communication Routes Through the Team Lead

No teammate communicates directly with another teammate. The team lead is the sole message router:

```
Developer ←→ Team Lead ←→ Critic
Developer ←→ Team Lead ←→ Ripple
Developer ←→ Team Lead ←→ Auditor
Developer ←→ Team Lead ←→ Expert
```

**Why**: The team lead maintains pipeline state. Direct communication bypasses state tracking and can lead to lost handoffs.

---

## Pipeline State Persistence

### INVARIANT 6: Pipeline State Must Be Recoverable

The team lead MUST persist pipeline state to the task metadata so it survives context loss:

```
TaskUpdate({
  taskId: "<id>",
  metadata: {
    "pipeline_stage": "in_critic_review",
    "critic_attempts": 1,
    "ripple_attempts": 0,
    "audit_attempts": 0,
    "assigned_developer": "dev-3"
  }
})
```

On resume, the team lead MUST:
1. Read task metadata to reconstruct pipeline state
2. Re-route tasks to the correct pipeline stage (not restart from pending)
3. Never mark a task complete without verifying it passed all stages

---

## Developer Autonomy Constraints

### INVARIANT 7: Developers Do Not Self-Complete

Developers MUST NOT:
- Call `TaskUpdate({ status: "completed" })`
- Skip `READY_FOR_REVIEW` and go directly to `REQUESTING_WORK`
- Consider their work "done" before the auditor passes it

The developer's terminal action for any task is `READY_FOR_REVIEW`. Everything after that is the team lead's responsibility.

### INVARIANT 8: Developers Handle Review Feedback Before New Work

When a developer receives review feedback (from critic, ripple, or auditor):
1. The developer MUST address ALL feedback items
2. The developer MUST re-run self-verification
3. The developer MUST re-signal `READY_FOR_REVIEW`
4. Only THEN may the developer request new work

**Priority**: Review feedback > New task assignment. Always.

---

## Reviewer Autonomy Constraints

### INVARIANT 9: Binary Verdicts Only

All reviewers (critic, ripple, auditor) produce exactly one of:
- **PASS** (with evidence)
- **FAIL** (with specific, actionable feedback)

No conditional passes. No "pass with caveats." No "pass pending future work."

### INVARIANT 10: Reviewers Do Not Edit Code

Critic, ripple, auditor, and health-auditor have `disallowedTools: Write, Edit, NotebookEdit`. They read and verify. They never fix.

---

## Escalation Requirements

### When the Team Lead MUST Escalate to User

| Situation | Escalation Method |
|-----------|------------------|
| Critic times out 3 times on same task | `AskUserQuestion` — user decides skip vs retry |
| Same task fails audit 3 times | `AskUserQuestion` — user reviews root cause |
| Team messaging system fails (idle loops) | `AskUserQuestion` — user decides recovery approach |
| Remediation fails 3 times | `AskUserQuestion` — user provides infrastructure fix |
| No unblocked tasks remain but work is incomplete | `AskUserQuestion` — user reviews dependency chain |

The team lead MUST NOT silently work around these situations.

---

## Anti-Patterns (Explicitly Forbidden)

| Anti-Pattern | Why It's Forbidden | What To Do Instead |
|-------------|-------------------|-------------------|
| Spawning standalone Task agents instead of using the team | Bypasses quality pipeline | Fix the team, escalate if broken |
| Marking tasks complete without auditor approval | Unverified code ships | Route through full pipeline |
| Assigning implementation work to experts | Experts lack developer tooling | Assign to developers only |
| Skipping critic after timeouts without user approval | Code quality review is skipped | Escalate to user |
| Team lead running developer commands | Team lead should delegate, not implement | Assign to a developer |
| Trusting developer self-verification as final | Developer is biased toward their own code | Independent auditor verification required |
| Broadcasting messages to all teammates | Expensive, scales with team size | Use targeted SendMessage |

---

## Related Documentation

- [Team Lead Prompt](../prompts/team-lead.md) — Team lead orchestration instructions
- [Update Triggers](state/update-triggers.md) — State transition rules
- [Agent Conduct](agent-conduct.md) — Cross-cutting teammate rules
- [Task Delivery Loop](task-delivery-loop.md) — Pipeline routing procedure
