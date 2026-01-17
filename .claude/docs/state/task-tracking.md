# Task Tracking

[← Back to State Management](index.md)

Task selection, rollback, and parallel agent tracking.

---

## Task Selection Priority

1. Select tasks that unblock the most downstream tasks
2. Among equals, select task with highest priority in plan
3. Among equals, select first in document order

---

## Rollback Capability

Track commit SHAs per task to enable rollback if issues are discovered after completion.

### Commit Tracking

```json
{
  "task_commits": {
    "task-1": {
      "commit_sha": "abc123",
      "completed_at": "ISO-8601",
      "files_modified": [
        "src/auth.py",
        "tests/test_auth.py"
      ],
      "branch": "main"
    }
  }
}
```

### Rollback Rules

1. Cannot rollback if dependent tasks have completed
2. Task returns to `available_tasks` after rollback
3. In-progress dependent tasks are aborted
4. Plan re-evaluation triggered

---

## Learning from Failures

Track failure patterns to improve future development cycles.

### Failure Pattern Storage

```json
{
  "failure_patterns": {
    "type_errors": {
      "count": 5,
      "tasks": [
        "task-3",
        "task-7"
      ],
      "common_causes": [
        "Missing type annotation"
      ],
      "suggested_prevention": "Run pyright before signaling completion"
    }
  }
}
```

### Using Failure Patterns

Include relevant patterns in developer prompts when dispatching similar tasks.

---

## Parallel Agent Tracking

### Agent Tracking Structure

```json
{
  "active_agents": {
    "agent-uuid-1": {
      "type": "developer",
      "task_id": "1-1-1",
      "dispatched_at": "2025-01-16T10:00:00Z",
      "timeout_at": "2025-01-16T10:15:00Z",
      "last_checkpoint": null
    }
  }
}
```

### Slot Management

**CRITICAL: Process pending reviews/audits BEFORE dispatching new developers.**

```python
# Separate limits for each agent type
MAX_PARALLEL_DEVELOPERS = 5
MAX_PARALLEL_CRITICS = 5
MAX_PARALLEL_AUDITORS = 5

def fill_actor_slots():
    """Fill slots with priority: critics > auditors > developers."""

    if infrastructure_blocked or pending_divine_questions:
        return

    # PRIORITY 1: Critics for pending reviews
    while pending_critique and len(active_critics) < MAX_PARALLEL_CRITICS:
        task_id = pending_critique.pop(0)
        dispatch_critic(task_id)

    # PRIORITY 2: Auditors for pending audits
    while pending_audit and len(active_auditors) < MAX_PARALLEL_AUDITORS:
        task_id = pending_audit.pop(0)
        dispatch_auditor(task_id)

    # PRIORITY 3: Developers for new tasks
    while len(active_developers) < MAX_PARALLEL_DEVELOPERS and available_tasks:
        task = select_next_task()
        dispatch_developer(task)
```

**Rationale**: Completing in-flight work (reviews, audits) unblocks dependent tasks faster than starting new work.

### Agent Lifecycle Events

| Event              | When                | State Change                       |
|--------------------|---------------------|------------------------------------|
| `agent_dispatched` | Task tool called    | Add to `active_agents`             |
| `agent_checkpoint` | Checkpoint received | Update `last_checkpoint`           |
| `agent_timeout`    | Timeout exceeded    | Remove, re-dispatch if under limit |
| `agent_complete`   | Signal received     | Remove, route based on signal      |
| `agent_crashed`    | Task tool error     | Remove, re-dispatch if under limit |

---

## Related Documentation

- [State Fields](fields.md) - All state field definitions
- [Update Triggers](update-triggers.md) - When state changes occur
- [Task Delivery Loop](../task-delivery-loop.md) - Main execution loop
- [Signal Specification](../signal-specification.md) - Agent signals
