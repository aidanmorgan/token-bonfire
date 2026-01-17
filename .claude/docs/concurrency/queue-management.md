# Queue Management

[← Back to Concurrency Index](index.md)

Queued tasks have a timeout to prevent indefinite waits when file conflicts occur.

## Queue Timeout Handling

### Constants

```python
FILE_CONFLICT_QUEUE_TIMEOUT_MINUTES = 30  # Max time to wait for file availability
```

### Queue Entry Creation

```python
def queue_task_for_conflict(task_id, waiting_for, conflicting_files):
    """Queue a task with timeout."""

    now = datetime.now()
    timeout = now + timedelta(minutes=FILE_CONFLICT_QUEUE_TIMEOUT_MINUTES)

    queued_for_file_conflict.append({
        "task_id": task_id,
        "waiting_for": waiting_for,
        "conflicting_files": conflicting_files,
        "queued_at": now.isoformat(),
        "timeout_at": timeout.isoformat()
    })

    log_event("task_queued_for_conflict",
              task_id=task_id,
              waiting_for=waiting_for,
              conflicting_files=conflicting_files,
              timeout_at=timeout.isoformat())

    save_state()
```

### Timeout Check (Run in Main Loop)

```python
MAX_QUEUE_RETRIES = 3  # After 3 timeouts, escalate instead of re-queue

# CRITICAL: queue_retry_tracker must be in state for persistence
# Initialize if not present: state['queue_retry_tracker'] = state.get('queue_retry_tracker', {})

def check_queue_timeouts():
    """Check for timed-out queued tasks. Call in main coordinator loop.

    IMPORTANT: This function uses state['queue_retry_tracker'] which is persisted
    to survive crashes and session restarts. The in-memory queue_retry_tracker
    is synchronized with state on every save.
    """

    now = datetime.now()

    # Ensure queue_retry_tracker exists in state (for recovery scenarios)
    if 'queue_retry_tracker' not in state:
        state['queue_retry_tracker'] = {}

    for queued in list(queued_for_file_conflict):
        timeout_at = datetime.fromisoformat(queued["timeout_at"])

        if now >= timeout_at:
            # Get retry count from state (persistent) not just queued entry
            task_id = queued["task_id"]
            retry_count = state['queue_retry_tracker'].get(task_id, queued.get("queue_retry_count", 0))

            if retry_count >= MAX_QUEUE_RETRIES:
                # Too many timeouts - escalate to divine intervention
                queued_for_file_conflict.remove(queued)

                log_event("queue_retry_exhausted",
                          task_id=queued["task_id"],
                          was_waiting_for=queued["waiting_for"],
                          retry_count=retry_count)

                escalate_to_divine(
                    task_id=queued["task_id"],
                    question=f"Task {queued['task_id']} queued {retry_count} times waiting for "
                             f"{queued['waiting_for']} to release files {queued['conflicting_files']}",
                    options=["Force dispatch with merge risk", "Restructure tasks", "Abort task"]
                )
                continue

            # Timeout reached - move to available with coordination instructions
            queued_for_file_conflict.remove(queued)

            # Track retry count in STATE for persistence (not just in-memory)
            state['queue_retry_tracker'][queued["task_id"]] = retry_count + 1

            # Add coordination context for the developer
            coordination_context = {
                "task_id": queued["task_id"],
                "note": f"Previously queued waiting for {queued['waiting_for']}. "
                        f"Timeout reached (retry {retry_count + 1}/{MAX_QUEUE_RETRIES}). "
                        f"Files may still be in use: {queued['conflicting_files']}. "
                        f"Proceed with caution, signal FILE CONFLICT if blocked.",
                "retry_count": retry_count + 1
            }

            available_tasks.append(queued["task_id"])

            # Store coordination context for dispatch
            queue_timeout_context[queued["task_id"]] = coordination_context

            log_event("queue_timeout",
                      task_id=queued["task_id"],
                      was_waiting_for=queued["waiting_for"],
                      conflicting_files=queued["conflicting_files"],
                      retry_count=retry_count + 1,
                      waited_minutes=(now - datetime.fromisoformat(queued["queued_at"])).seconds // 60)

    save_state()
```

### Re-Queue with Retry Tracking

When a task that was previously timed out gets queued again:

```python
def queue_task_for_conflict_with_retry(task_id, waiting_for, conflicting_files):
    """Queue a task, preserving retry count from previous timeouts."""

    now = datetime.now()
    timeout = now + timedelta(minutes=FILE_CONFLICT_QUEUE_TIMEOUT_MINUTES)

    # Ensure queue_retry_tracker exists in state
    if 'queue_retry_tracker' not in state:
        state['queue_retry_tracker'] = {}

    # Check if this task was previously timed out (from persistent state)
    retry_count = state['queue_retry_tracker'].pop(task_id, 0)

    queued_for_file_conflict.append({
        "task_id": task_id,
        "waiting_for": waiting_for,
        "conflicting_files": conflicting_files,
        "queued_at": now.isoformat(),
        "timeout_at": timeout.isoformat(),
        "queue_retry_count": retry_count  # Preserve retry count
    })

    log_event("task_queued_for_conflict",
              task_id=task_id,
              waiting_for=waiting_for,
              conflicting_files=conflicting_files,
              timeout_at=timeout.isoformat(),
              retry_count=retry_count)

    save_state()
```

### Integration with Main Loop

```python
def coordinator_main_loop():
    """Main coordinator loop with queue timeout check."""

    while not workflow_complete:
        # Check queue timeouts BEFORE filling slots
        check_queue_timeouts()

        # Normal operations
        fill_actor_slots()
        process_agent_signals()
        save_state()
```

---

[← Back to Concurrency Index](index.md)
