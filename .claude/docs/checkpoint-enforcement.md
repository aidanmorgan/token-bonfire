# Checkpoint Enforcement

Long-running developers may work in silence. The coordinator proactively requests checkpoints to maintain visibility.

## Checkpoint Configuration

| Variable              | Value    | Description                                         |
|-----------------------|----------|-----------------------------------------------------|
| `CHECKPOINT_INTERVAL` | `300000` | Request checkpoint every 5 minutes of agent runtime |
| `CHECKPOINT_TIMEOUT`  | `30000`  | Agent must respond within 30 seconds                |

See [timeout-specification.md](timeout-specification.md) for complete timeout reference.

## Checkpoint Request Trigger

```python
def check_checkpoint_needed():
    """Determine if any active developers need checkpoint requests."""

    now = datetime.now()
    checkpoint_due = []

    for task in in_progress_tasks:
        if task["status"] != "implementing":
            continue

        last_checkpoint = task.get("last_checkpoint_time")
        if last_checkpoint is None:
            last_checkpoint = task["dispatched_at"]

        last_time = datetime.fromisoformat(last_checkpoint)
        elapsed_ms = (now - last_time).total_seconds() * 1000

        if elapsed_ms > CHECKPOINT_INTERVAL:
            checkpoint_due.append(task)

    return checkpoint_due
```

## Checkpoint Request Procedure

When checkpoint is due:

```python
def request_checkpoint(task):
    """Request progress update from active developer."""

    output(f"CHECKPOINT REQUEST: {task['task_id']}")

    # The developer agent should respond with checkpoint format
    # defined in developer-spec.md

    # Update tracking
    task["checkpoint_requested_at"] = datetime.now().isoformat()

    log_event("checkpoint_requested", task_id=task["task_id"],
              developer_id=task["developer_id"])
```

## Expected Checkpoint Response

Developers must respond with:

```
CHECKPOINT: [task_id]
Status: [implementing | testing | awaiting-verification]
Completed:
- [concrete deliverable]
- [concrete deliverable]
Remaining:
- [specific next step]
- [specific next step]
Files Modified: [list of paths]
Estimated Progress: [N]%
```

## On Checkpoint Received

```python
def handle_checkpoint(task_id, checkpoint_data):
    """Process checkpoint from developer."""

    task = get_task(task_id)

    task["last_checkpoint"] = checkpoint_data["summary"]
    task["last_checkpoint_time"] = datetime.now().isoformat()
    task["estimated_progress"] = checkpoint_data.get("progress", 0)

    log_event("developer_checkpoint",
              task_id=task_id,
              status=checkpoint_data["status"],
              progress=checkpoint_data.get("progress"))

    save_state()

    # Output progress for coordinator visibility
    output(f"CHECKPOINT: {task_id} - {checkpoint_data['status']} ({checkpoint_data.get('progress', '?')}%)")
```

## On Checkpoint Timeout

If developer doesn't respond to checkpoint within `CHECKPOINT_TIMEOUT`:

```python
def handle_checkpoint_timeout(task_id):
    """Handle non-responsive developer."""

    log_event("checkpoint_timeout", task_id=task_id)

    # Check if agent is still running (via task status)
    if is_agent_running(task_id):
        # Agent may be in deep work - allow continuation
        output(f"WARNING: {task_id} checkpoint timeout - agent still active")
    else:
        # Agent may have crashed
        output(f"WARNING: {task_id} checkpoint timeout - checking agent status")
        handle_potential_agent_failure(task_id)
```

## Coordinator Loop Integration

Add to the continuous operation loop:

```python
# In main coordinator loop, after processing agent results:
def coordinator_loop_iteration():
    # ... existing logic ...

    # Check for checkpoint needs during idle moments
    if count_active_actors() < ACTIVE_DEVELOPERS or not available_tasks:
        checkpoint_due = check_checkpoint_needed()
        for task in checkpoint_due:
            request_checkpoint(task)

    # Check for timeouts
    check_agent_timeouts()

    # Continue with slot filling
    fill_actor_slots()
```

## Progress Dashboard Output

Periodically output overall progress:

```
PROGRESS DASHBOARD
==================
Active: [N]/[ACTIVE_DEVELOPERS] actors
Phase: [current phase] ([N]/[total] tasks)
Overall: [N]/[total] tasks complete ([percentage]%)

Active Tasks:
- [task-id]: [status] ([progress]%) - [last checkpoint summary]
- [task-id]: [status] ([progress]%) - [last checkpoint summary]

Pending Audit: [N] tasks
Available: [N] tasks
Blocked: [N] tasks
```

## Cross-References

- Timeout values: [timeout-specification.md](timeout-specification.md)
- State management: [state-management.md](state-management.md)
- Task delivery loop: [task-delivery-loop.md](task-delivery-loop.md)
