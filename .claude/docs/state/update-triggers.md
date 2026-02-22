# State Update Triggers

[← Back to Documentation Index](../index.md)

State updates use native Agent Teams primitives: `TaskUpdate` for task state transitions and `SendMessage` for inter-agent communication.

---

## Developer Dispatch (Task Assigned)

When the team lead assigns a task to a developer (push-based):

1. Team lead calls `TaskUpdate({ taskId, status: "in_progress", owner: "<dev-name>" })`
2. Team lead sends full task detail via `SendMessage({ type: "message", recipient: "<dev-name>", content: "TASK_ASSIGNMENT\n...", summary: "Task assignment" })`
3. No manual blocking/unblocking needed — native dependency tracking handles this

## Developer Ready for Review

When a developer signals `READY_FOR_REVIEW` via mailbox:

1. Team lead receives the message
2. Team lead tracks task as `pending_review` in its review pipeline (team lead context only — not a `TaskUpdate` status)
3. Team lead sends review request to `critic` via `SendMessage` (with task ID, acceptance criteria, modified files, environment)

## Developer NEED_CLARIFICATION

When a developer signals `NEED_CLARIFICATION`:

1. Team lead reads the question from the mailbox message
2. Route based on blocker category:

**Blocker Categories and Handlers**:

| Category | Action | Escalation |
|---|---|---|
| Missing info / ambiguous requirements | Route to `business-analyst` via `SendMessage`, or escalate via `AskUserQuestion` | After 3 attempts |
| Blocked by dependency | Check if dependency is already `completed` in task list; if not, developer waits | After 3 attempts |
| Infrastructure issue | Route to `remediation` via `SendMessage` | After remediation limit |
| Out of scope | Escalate via `AskUserQuestion` | Immediate |

**Blocked by dependency handling:**

- Team lead calls `TaskGet` to check if the blocking task is already `completed`
- If completed: inform developer via `SendMessage` that the dependency is ready
- If not completed: the native `addBlockedBy` ensures the task auto-unblocks when the dependency completes
- After 3 attempts with the same blocker: escalate via `AskUserQuestion`

**Missing info / out of scope handling:**

- Team lead escalates to the user via `AskUserQuestion` tool
- Response is forwarded to the developer via `SendMessage`

**Infrastructure blocker handling:**

- Team lead sends details to `remediation` teammate via `SendMessage`
- Same as `INFRA_BLOCKED` signal flow

## Critic Review Complete

**REVIEW_PASSED:**

1. Team lead receives `REVIEW_PASSED` from critic via mailbox
2. Team lead tracks task as `in_ripple_review` in its review pipeline (team lead context only)
3. Team lead sends ripple analysis request to `ripple` via `SendMessage` (with task ID, modified files, summary, critic assessment)

**REVIEW_FAILED:**

1. Team lead receives `REVIEW_FAILED` from critic via mailbox
2. Team lead forwards feedback to the owning developer via `SendMessage`
3. Team lead tracks task as `needs_rework` in its review pipeline (team lead context only); task status via `TaskUpdate` remains `in_progress`
4. Team lead increments critique failure count in its context

## Ripple Review Complete

**RIPPLE_PASSED:**

1. Team lead receives `RIPPLE_PASSED` from ripple via mailbox
2. Team lead tracks task as `pending_audit` in its review pipeline (team lead context only)
3. Team lead sends audit request to `auditor` via `SendMessage` (with task ID, acceptance criteria, modified files, environment)

**RIPPLE_FAILED:**

1. Team lead receives `RIPPLE_FAILED` from ripple via mailbox
2. Team lead forwards feedback to the owning developer via `SendMessage`
3. Team lead tracks task as `needs_rework` in its review pipeline (team lead context only); task status via `TaskUpdate` remains `in_progress`
4. Team lead increments ripple failure count in its context

## Critic Timeout

When a critic does not respond within a reasonable time:

1. Team lead increments critic timeout count for this task
2. If timeout count < 3:
    - Team lead re-sends review request to `critic` via `SendMessage`
    - Team lead continues tracking task as `pending_review` in its review pipeline (no `TaskUpdate` needed)
3. If timeout count >= 3:
    - **Escalate to user via `AskUserQuestion`** — the user decides whether to skip critic or retry
    - Do NOT silently bypass the critic — see [autonomy.md](../autonomy.md) INVARIANT 1
    - Team lead tracks task as `pending_review` until user responds

   **Note**: Do NOT send back to developer — the implementation is complete, only the code review timed out.

**Why no automatic bypass**: Skipping the critic means code quality issues may ship undetected. The auditor verifies acceptance criteria but does NOT review code quality. Only the user can authorize skipping a pipeline stage.

## Auditor PASS (Task Complete)

**This is the ONLY point where a task becomes complete.**

1. Team lead receives `AUDIT_PASSED` from auditor via mailbox
2. Team lead calls `TaskUpdate({ taskId, status: "completed" })` — **task officially complete**
3. Dependencies auto-unblock: tasks that were `blockedBy` this task automatically become available
4. Newly unblocked tasks can be assigned to requesting developers immediately

**IMPORTANT**: The native `addBlockedBy` mechanism handles both:
- Static dependencies from the plan
- Dynamic blockers added during execution

## Auditor FAIL

1. Team lead receives `AUDIT_FAILED` from auditor via mailbox
2. Team lead forwards failure feedback to the owning developer via `SendMessage`
3. Team lead tracks task as `needs_rework` in its review pipeline (team lead context only); task status via `TaskUpdate` is reset to `in_progress` for the developer to rework
4. Team lead increments audit failure count in its context
5. Check escalation threshold (3 failures = investigate root cause, consider escalating)

## Auditor BLOCKED

1. Team lead receives `AUDIT_BLOCKED` from auditor via mailbox
2. Team lead sets `infrastructure_blocked` flag in its context
3. Team lead sends issue details to `remediation` teammate via `SendMessage`
4. Pauses new task assignments until infrastructure is restored

## Remediation/Health Audit

**On REMEDIATION_COMPLETE (from remediation teammate):**

1. Team lead sends verification request to `health-auditor` via `SendMessage`

**On HEALTH_AUDIT: HEALTHY (from health-auditor teammate):**

1. Team lead clears `infrastructure_blocked` flag
2. Team lead resets `remediation_attempt_count` to 0
3. Resumes normal development flow — team lead can assign tasks again

**On HEALTH_AUDIT: UNHEALTHY (from health-auditor teammate):**

1. Team lead increments `remediation_attempt_count`
2. If count > 3:
    - Escalate via `AskUserQuestion` with infrastructure details
3. Else:
    - Send updated context to `remediation` teammate via `SendMessage` for retry

## User Escalation

**On SEEKING_DIVINE_CLARIFICATION (from any teammate):**

1. Team lead parses question details from mailbox message
2. Team lead invokes `AskUserQuestion` tool with question and options
3. Task progress blocked until response received

**When user responds:**

1. Team lead formats response
2. Team lead sends guidance to the requesting teammate via `SendMessage`

## Expert Delegation (business-analyst)

**On EXPANDED_TASK_SPECIFICATION (from business-analyst):**

1. Team lead updates task description via `TaskUpdate`
2. Team lead routes the expanded spec to the owning developer via `SendMessage`

**On SEEKING_DIVINE_CLARIFICATION (from business-analyst):**

1. Same user escalation flow as above

---

## Related Documentation

- [Attempt Tracking](attempt-tracking.md) - Attempt tracking and escalation
- [Task Tracking](task-tracking.md) - Task selection, rollback, and failure patterns
- [Communication Protocol](../communication-protocol.md) - Communication protocol
