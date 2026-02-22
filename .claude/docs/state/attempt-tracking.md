# Attempt Tracking

[← Back to Documentation Index](../index.md)

Track attempts across expert crashes and session restarts to enforce escalation paths. The team lead maintains attempt counts in its context, and they can be reconstructed from task list state and mailbox history on resume.

---

## Attempt Tracking Structure

The team lead tracks per-task attempt counts:

| Field | Type | Description |
|---|---|---|
| `self_solve_attempts` | Integer | Times a developer attempted this task |
| `audit_failures` | Integer | Times auditor rejected this task |
| `critic_failures` | Integer | Times critic rejected this task |
| `critic_timeouts` | Integer | Times critic timed out on this task |
| `clarification_requests` | Integer | Times expert asked for clarification |

## Escalation Thresholds

| Attempt Type | Threshold | Escalation Action |
|---|---|---|
| `self_solve_attempts` | 3 | Team lead investigates, considers reassigning to different developer |
| `audit_failures` | 3 | Team lead investigates root cause, escalates via `AskUserQuestion` |
| `critic_failures` | 3 | Team lead investigates root cause, escalates via `AskUserQuestion` |
| `critic_timeouts` | 3 | Bypass critic, send directly to auditor |
| `clarification_requests` | 3 | Team lead escalates to user via `AskUserQuestion` |

## Persistence Across Crashes

On resume, attempt tracking is partially reconstructable:
- **Task status** persists in the shared task list (via plan slug)
- **Expert prompts** persist on disk at `.claude/experts/<plan_slug>/`
- **Attempt counts** in the team lead's context are lost on crash, but the team lead can infer state from task list status and take conservative action (e.g., if a task has been in `needs_rework` multiple times)

The team lead should note repeated `needs_rework` cycles as a signal that escalation may be needed, even if exact counts are not preserved.

---

## Related Documentation

- [Update Triggers](update-triggers.md) - When attempt counts are incremented
- [Task Tracking](task-tracking.md) - Task selection, rollback, and failure patterns
- [Communication Protocol](../communication-protocol.md) - Failure handling
