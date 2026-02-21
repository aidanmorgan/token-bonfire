# Timeout Specification

Timeout behavior in the native Agent Teams system.

## Native Timeouts

The primary timeout mechanism is the **heartbeat timeout** (~5 min), which is built into the Agent Teams framework. When a teammate stops responding, the heartbeat timeout:
- Detects the unresponsive teammate
- Releases any tasks claimed by that teammate (auto-release)
- Notifies the team lead

| Timeout | Mechanism | Purpose |
|---|---|---|
| Heartbeat timeout | Native (~5 min) | Detects unresponsive teammates, releases claimed tasks |
| Review response timeout | Team lead monitoring | Detects stuck critic or auditor |
| Shutdown timeout | `requestShutdown` | Graceful shutdown with timeout, then forced |

## Review Response Monitoring

The team lead tracks how long critic and auditor take to respond to review/audit requests. If no response arrives within a reasonable time:

### Critic Timeout

1. Team lead re-sends review request via `write`
2. Tracks timeout count per task
3. After 3 timeouts: bypass critic, send directly to auditor
4. See [update-triggers.md](state/update-triggers.md) for the quality gate tradeoff

### Auditor Timeout

1. Team lead re-sends audit request via `write`
2. Tracks timeout count per task
3. After 3 timeouts: escalate via `AskUserQuestion`

### Expert Stall Detection

If an expert claims a task but does not signal `READY_FOR_REVIEW` or any other message for an extended period:
1. Team lead can send a status inquiry via `write`
2. If no response: heartbeat timeout handles it automatically
3. Task auto-releases and becomes available for other experts

## Escalation After Repeated Timeouts

After 3 timeouts on the same task (any teammate type):

The team lead escalates via `AskUserQuestion`:

```
Task <task-id> has timed out 3 times. Possible causes:
- Task too large for a single expert
- Unclear requirements
- Infrastructure issue

Options:
1. Split task into smaller subtasks
2. Clarify requirements
3. Reassign to a different expert
4. Skip task and continue
```

## Context Windows

Each teammate has a 1M token context window, managed natively:

| Aspect | Behavior |
|---|---|
| Context size | 1M tokens per teammate |
| Context isolation | Each teammate has its own window — no sharing |
| Context persistence | NOT preserved across crashes |
| Context recovery | Teammate respawned with its prompt (persisted on disk for experts) |

No custom compaction, session pause, or usage tracking is needed. The native 1M token context is sufficient for most tasks.

## What Replaces Custom Timeout Infrastructure

| Old System | New System |
|---|---|
| `AGENT_TIMEOUT` (15 min) | Native heartbeat timeout (~5 min) |
| `CHECKPOINT_INTERVAL` (5 min) mandatory | Optional CHECKPOINT signals — informational only, not mandatory |
| `CHECKPOINT_TIMEOUT` (30 sec) | Not needed — CHECKPOINT signals are optional; native heartbeat handles detection |
| `DELEGATION_TIMEOUT` (10 min) | Native heartbeat timeout |
| `DIVINE_RESPONSE_TIMEOUT` (none) | Still none — human responses have no timeout |
| `CONTEXT_THRESHOLD` (10%) | Not needed — native 1M token context management |
| `SESSION_THRESHOLD` (10%) | Not needed — no custom session pause |
| `STALL_THRESHOLD` (3 missed) | Heartbeat timeout handles stall detection |
| `TIMEOUT_ESCALATION` (3 timeouts) | Team lead tracks and escalates after 3 failures |
| Custom checkpoint miss tracking | Not needed — native heartbeat is the detection mechanism |
| Stalled agent recovery procedure | Native task auto-release |

**Key principle**: The old system required teammates to send mandatory checkpoints on a fixed interval. The new system uses the native heartbeat timeout (~5 min) as the primary detection mechanism. Teammates MAY send optional CHECKPOINT signals for team lead visibility, but missing a checkpoint does NOT trigger any recovery action.

## Shutdown Timeout

When the team lead initiates shutdown:

1. `TeammateTool({ operation: "requestShutdown", to: "<name>" })` for each teammate
2. Teammate finishes current work and responds with `shutdown_approved`
3. If no response within timeout: forced termination
4. `TeammateTool({ operation: "cleanup" })` removes team resources

---

## Cross-References

- [Progress Monitoring](agent-context-management.md#progress-monitoring-team-lead) - How the team lead monitors progress
- [Session Management](session-management.md) - Session lifecycle
- [State Management](state/index.md) - Task state tracking
- [Team Architecture](team-architecture.md) - Failure handling
