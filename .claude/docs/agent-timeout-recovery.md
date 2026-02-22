# Teammate Recovery

This document covers timeout handling, crash recovery, and disagreement detection for all teammate types.

**Related Documents:**

- [Communication Protocol](communication-protocol.md) - Team structure and failure handling
- [Task Tracking](state/task-tracking.md) - Task state tracking

---

## Timeout Handling

### Native Heartbeat Timeout

Each teammate has a native heartbeat. When a teammate stops responding:
- Heartbeat timeout (~5 min) detects the issue
- The teammate's assigned tasks auto-release and become available for reassignment
- The team lead can respawn the teammate from its persisted prompt (experts) or agent definition (support teammates)

### Timeout by Teammate Type

| Teammate Type | Recovery | Notes |
|---|---|---|
| Developer | Respawn with `subagent_type: "developer"` | Task auto-releases; role instructions from `.claude/agents/developer.md` |
| Named Expert | Respawn from `.claude/experts/<plan_slug>/<name>.md` | Task auto-releases; domain knowledge preserved in prompt file |
| Critic | Respawn from agent definition | Stateless — processes review requests from mailbox |
| Ripple | Respawn from agent definition | Stateless — processes ripple requests from mailbox |
| Auditor | Respawn from agent definition | Stateless — processes audit requests from mailbox |
| Business Analyst | Respawn from agent definition | Stateless — processes expansion requests from mailbox |
| Remediation | Respawn from agent definition | Stateless — processes infrastructure fix requests |
| Health Auditor | Respawn from agent definition | Stateless — runs verification commands on request |

---

## Expert Timeout/Crash

When a named expert stops responding:

1. Heartbeat timeout (~5 min) detects the unresponsive expert
2. The assigned task auto-releases (becomes available for reassignment)
3. Team lead respawns the expert from its persisted prompt file:
   ```
   Task({
     team_name: "<plan_slug>",
     name: "<expert-name>",
     subagent_type: "general-purpose",
     model: "<EXPERT_MODEL>",
     prompt: "<expert prompt from disk>",
     run_in_background: true
   })
   ```
4. Fresh teammate sends `REQUESTING_WORK` to team lead (may be assigned the same task)
5. Partial work from the crashed expert remains in the file system

### Repeated Expert Failures

If the same expert crashes repeatedly on the same task:
- Team lead tracks failure counts in its context
- After 3 failures: team lead investigates (task may be too large, unclear, or have infrastructure issues)
- Consider splitting the task, reassigning to a different expert, or escalating via `AskUserQuestion`

---

## Critic Timeout/Crash

When the critic stops responding:

1. Team lead detects timeout (no `REVIEW_PASSED`/`REVIEW_FAILED` response)
2. Team lead tracks critic timeout count per task
3. If timeout count < 3: respawn critic, re-send review request via `SendMessage`
4. If timeout count >= 3: bypass critic, send directly to auditor (see [update-triggers.md](state/update-triggers.md))

---

## Auditor Timeout/Crash

When the auditor stops responding:

1. Team lead detects timeout (no `AUDIT_PASSED`/`AUDIT_FAILED`/`AUDIT_BLOCKED` response)
2. Team lead respawns auditor from documentation
3. Re-sends audit request via `SendMessage`
4. After 3 timeouts on the same task: escalate via `AskUserQuestion`

---

## Teammate Crash Recovery (General)

For any crashed teammate:

1. Heartbeat timeout detects the unresponsive teammate
2. Team lead sends `SendMessage({ type: "shutdown_request", recipient: "<name>", content: "Crash recovery — shutting down stuck teammate" })` (in case the teammate is still running but stuck)
3. Team lead respawns the teammate using `Task({ team_name: "<plan_slug>", name: "<name>", subagent_type: "<agent-type>", run_in_background: true })`
4. For experts: use persisted prompt file from disk
5. For support teammates: use documentation-based prompt

---

## Critic/Auditor Disagreement Detection

When a critic passes code that the auditor subsequently fails, this may indicate:

1. Critic missed a quality issue
2. Acceptance criteria interpretation mismatch
3. Verification environment issues

### Detection

The team lead tracks the review pipeline. If a task goes through:
`REVIEW_PASSED` from critic, then `AUDIT_FAILED` from auditor — this is a disagreement.

### On Disagreement Detected

The team lead categorizes the disagreement:

| Type | Description | Handling |
|---|---|---|
| `acceptance_criteria` | Criteria not met (auditor's domain) | Normal flow — not a true disagreement |
| `code_quality` | Quality issue critic missed | Team lead notes pattern for future critic requests |
| `environment_specific` | Passes in some environments, fails in others | Route to expert with environment-specific context |

### Learning from Disagreements

The team lead includes relevant disagreement patterns when sending future review requests to the critic:

```
REVIEW REQUEST for <task-id>

...

NOTE: Previous reviews have missed <pattern> issues.
Pay extra attention to: <specific area>
```

---

## Environment Disagreement Protocol

When verification passes in some environments but fails in others:

1. Team lead identifies which environments pass and which fail
2. Team lead sends the developer environment-specific feedback via `SendMessage`:
   ```
   REVIEW_FAILED: <task-id>

   Environment-specific failure:
   - PASS in: <env-1>
   - FAIL in: <env-2>

   Failed check: <command>
   Error: <error output>

   Common causes: missing dependencies, hardcoded paths, version mismatches, platform-specific code
   ```
3. Developer fixes the environment-specific issue and re-signals `READY_FOR_REVIEW`

---

## Error Recovery Summary

| Error Type | Detection | Recovery Action |
|---|---|---|
| Expert timeout/crash | Heartbeat timeout (~5 min) | Task auto-releases; respawn from prompt file |
| Critic timeout | No response to review request | Retry up to 3x, then bypass to auditor |
| Auditor timeout | No response to audit request | Retry up to 3x, then escalate |
| Support teammate crash | Heartbeat timeout | Respawn from documentation |
| Review/audit disagreement | Critic passed, auditor failed | Log pattern, normal rework flow |
| Environment disagreement | Pass in some envs, fail in others | Developer rework with environment context |

---

## Cross-References

- [Communication Protocol](communication-protocol.md) - Failure handling table
- [Task Tracking](state/task-tracking.md) - Task state tracking
- [Baseline Failures](recovery/baseline-failures.md) - Pre-session failure baseline capture
