# Timeout Specification

All timeout values and their interactions are defined here.

## Timeout Values

| Timeout                   | Value               | Purpose                                  |
|---------------------------|---------------------|------------------------------------------|
| `AGENT_TIMEOUT`           | 900,000 ms (15 min) | Maximum agent execution time             |
| `CHECKPOINT_INTERVAL`     | 300,000 ms (5 min)  | How often to request checkpoints         |
| `CHECKPOINT_TIMEOUT`      | 30,000 ms (30 sec)  | How long to wait for checkpoint response |
| `DELEGATION_TIMEOUT`      | 600,000 ms (10 min) | Maximum expert execution                 |
| `DIVINE_RESPONSE_TIMEOUT` | None                | Human responses have no timeout          |

## Timeout Interactions

### Agent Timeout vs Checkpoint Timeout

```
Timeline:
0 min      5 min      10 min     15 min
|----------|----------|----------|
           ^          ^          ^
           |          |          |
           Checkpoint Checkpoint Agent
           Request    Request    Timeout
           (30s wait) (30s wait)
```

**Rules**:

1. Checkpoint timeout (30s) is independent of agent timeout (15 min)
2. Agent timeout clock continues during checkpoint requests
3. Missing a checkpoint does NOT extend agent timeout
4. Missing a checkpoint triggers "stalled agent" warning

### Checkpoint Non-Response

```python
def handle_checkpoint_timeout(agent_id: str, task_id: str):
    """Handle agent not responding to checkpoint within 30 seconds."""

    log_event("checkpoint_timeout",
              agent_id=agent_id,
              task_id=task_id,
              checkpoint_count=state['checkpoint_misses'].get(agent_id, 0) + 1)

    state['checkpoint_misses'][agent_id] = state['checkpoint_misses'].get(agent_id, 0) + 1

    if state['checkpoint_misses'][agent_id] >= 3:
        # Agent considered stalled after 3 missed checkpoints
        log_event("agent_stalled",
                  agent_id=agent_id,
                  task_id=task_id,
                  action="marked_for_restart")
        state['stalled_agents'].append(agent_id)
```

### Agent Timeout Reached

```python
def handle_agent_timeout(agent_id: str, task_id: str):
    """Handle agent exceeding 15-minute execution limit."""

    log_event("agent_timeout",
              agent_id=agent_id,
              task_id=task_id,
              elapsed_ms=AGENT_TIMEOUT)

    # Task returns to available pool
    move_task_to_available(task_id, reason="agent_timeout")

    # Agent slot freed for new dispatch
    remove_from_active_agents(agent_id)

    # Increment task's timeout counter
    task = get_task(task_id)
    task['timeout_count'] = task.get('timeout_count', 0) + 1

    if task['timeout_count'] >= 3:
        # Task has timed out 3 times - escalate
        log_event("task_repeated_timeout",
                  task_id=task_id,
                  count=3,
                  action="divine_intervention")
        add_to_pending_divine_questions(task_id, "Task times out repeatedly")
```

## Delegation Timeout

Experts have a shorter timeout (10 min) than baseline agents (15 min).

```python
def dispatch_expert(delegation: dict) -> str:
    """Dispatch with delegation-specific timeout."""

    return Task(
        model=agent_model,
        subagent_type=agent_name,
        prompt=prompt,
        timeout=DELEGATION_TIMEOUT  # 10 minutes, not 15
    )
```

**Rationale**: Experts handle focused requests, not full tasks.

## Session-Level Timeouts

### Context Threshold

| Threshold           | Value         | Action                  |
|---------------------|---------------|-------------------------|
| `CONTEXT_THRESHOLD` | 10% remaining | Trigger auto-compaction |
| `SESSION_THRESHOLD` | 10% remaining | Trigger session pause   |

### Compaction Timing

```python
def check_context_threshold():
    """Check if compaction needed."""

    usage = get_current_usage()

    if usage['remaining_percentage'] <= CONTEXT_THRESHOLD:
        # Collect checkpoints with timeout
        checkpoints = collect_checkpoints_with_timeout(
            agents=state['active_agents'],
            timeout=CHECKPOINT_TIMEOUT
        )

        # Proceed even if some agents don't respond
        trigger_compaction(checkpoints)
```

## Timeout State Tracking

```json
{
  "timeout_tracking": {
    "checkpoint_misses": {
      "[agent_id]": 0
    },
    "stalled_agents": [],
    "task_timeouts": {
      "[task_id]": 0
    }
  }
}
```

## Recovery Procedures

### Stalled Agent Recovery

```python
def recover_stalled_agent(agent_id: str):
    """Recover from agent that stopped responding."""

    task_id = get_agent_task(agent_id)

    # 1. Mark agent as terminated
    terminate_agent(agent_id)

    # 2. Return task to available pool
    move_task_to_available(task_id, reason="agent_stalled")

    # 3. Clear checkpoint miss counter
    state['checkpoint_misses'].pop(agent_id, None)

    # 4. Free slot for new dispatch
    state['active_agents'].remove(agent_id)

    log_event("stalled_agent_recovered",
              agent_id=agent_id,
              task_id=task_id)
```

### Repeated Timeout Escalation

After 3 timeouts on the same task:

```python
def escalate_repeated_timeout(task_id: str):
    """Escalate task that repeatedly times out."""

    state['pending_divine_questions'].append({
        'task_id': task_id,
        'question': f"Task {task_id} has timed out 3 times. Possible causes: "
                    "task too large, unclear requirements, or infrastructure issue. "
                    "How should we proceed?",
        'options': [
            "Split task into smaller subtasks",
            "Clarify requirements",
            "Increase timeout for this task",
            "Skip task and continue"
        ],
        'asked_at': datetime.now().isoformat()
    })
```

## Timeout Configuration

All timeouts are configurable in the orchestrator prompt:

```markdown
### Timeout Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `AGENT_TIMEOUT` | 900000 | Agent execution limit (ms) |
| `CHECKPOINT_INTERVAL` | 300000 | Checkpoint request frequency (ms) |
| `CHECKPOINT_TIMEOUT` | 30000 | Checkpoint response wait (ms) |
| `DELEGATION_TIMEOUT` | 600000 | Expert limit (ms) |
| `STALL_THRESHOLD` | 3 | Missed checkpoints before stall |
| `TIMEOUT_ESCALATION` | 3 | Timeouts before divine intervention |
```

## Cross-References

- Checkpoint protocol: [task-delivery-loop.md](task-delivery-loop.md)
- Session management: [session-management.md](session-management.md)
- State tracking: [state-management.md](state-management.md)
