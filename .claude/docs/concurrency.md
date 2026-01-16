# Concurrent File Modification

With `{{ACTIVE_DEVELOPERS}}` parallel developers, file conflicts are possible. This document specifies how the
coordinator prevents and handles concurrent modifications.

## File Lock Protocol

### Pre-Dispatch File Analysis

Before dispatching a developer, the coordinator analyzes potential file conflicts:

```python
def analyze_file_conflicts(task_id, plan):
    """Identify files the task is likely to modify."""

    # Extract from task specification
    task = get_task(task_id, plan)

    # Sources of file information:
    # 1. Explicit file paths in work description
    # 2. Module/class names that imply file locations
    # 3. Required reading files (often targets for modification)
    # 4. Test files implied by acceptance criteria

    potential_files = extract_file_references(task.work_description)
    potential_files += infer_files_from_modules(task.work_description)
    potential_files += task.required_reading
    potential_files += infer_test_files(task.acceptance_criteria)

    return set(potential_files)
```

### Conflict Detection

Before dispatching:

```python
def check_file_conflicts(task_id, potential_files):
    """Check if any in-progress task is modifying the same files."""

    conflicts = []

    for in_progress in in_progress_tasks:
        locked_files = in_progress.get("locked_files", [])
        overlap = potential_files.intersection(locked_files)

        if overlap:
            conflicts.append({
                "task_id": in_progress["task_id"],
                "developer_id": in_progress["developer_id"],
                "conflicting_files": list(overlap)
            })

    return conflicts
```

### Conflict Resolution

When conflicts are detected:

```python
def resolve_file_conflicts(task_id, conflicts):
    """Decide how to handle detected conflicts."""

    resolution_options = [
        "QUEUE",  # Wait for conflicting task to complete
        "COORDINATE",  # Dispatch with explicit coordination instructions
        "SKIP"  # Select different task instead
    ]

    # Decision criteria:
    # 1. If conflicting task is in awaiting-audit, likely to complete soon → QUEUE
    # 2. If files are truly independent sections → COORDINATE
    # 3. If other tasks are available without conflicts → SKIP

    for conflict in conflicts:
        conflicting_task = get_task_status(conflict["task_id"])

        if conflicting_task["status"] == "awaiting-audit":
            # Will resolve soon, queue this task
            return "QUEUE", conflict["task_id"]

        if can_coordinate_safely(task_id, conflict, conflicting_files):
            return "COORDINATE", generate_coordination_instructions(conflict)

    # Default: select a different task
    return "SKIP", None
```

## Lock Tracking in State

Track file locks in `{{STATE_FILE}}`:

```json
{
  "in_progress_tasks": [
    {
      "task_id": "task-3",
      "developer_id": "dev-agent-1",
      "status": "implementing",
      "locked_files": [
        "src/auth/authenticator.py",
        "tests/unit/test_authenticator.py"
      ],
      "lock_acquired_at": "ISO-8601"
    }
  ],
  "queued_for_file_conflict": [
    {
      "task_id": "task-7",
      "waiting_for": "task-3",
      "conflicting_files": [
        "src/auth/authenticator.py"
      ],
      "queued_at": "ISO-8601",
      "timeout_at": "ISO-8601",
      "queue_retry_count": 0
    }
  ]
}
```

## Coordination Instructions

When dispatching a developer for a task that might touch shared files, include coordination instructions:

```markdown
FILE COORDINATION NOTICE:

Task [other-task-id] is concurrently modifying related code:
- Developer: [agent-id]
- Files: [list]

To avoid conflicts:
1. Do NOT modify: [specific files to avoid]
2. Focus changes on: [your designated files]
3. If you discover you need to modify a locked file:
   - Signal with: "FILE CONFLICT: [file path]"
   - Wait for coordinator guidance
4. Prefer additive changes over modifications to shared modules
```

## Lock Release

### On Developer Completion

When a developer signals `READY_FOR_REVIEW:`:

```python
def release_file_locks(task_id):
    """Release file locks and process queued tasks."""

    task = get_in_progress_task(task_id)

    # Note: Don't fully release until audit PASSES
    # Task goes: READY_FOR_REVIEW → Critic → REVIEW_PASSED → Auditor → AUDIT_PASSED
    # But allow other developers to see files will be available soon
    task["status"] = "awaiting-review"
    task["locks_releasing"] = True

    # Check queued tasks
    for queued in queued_for_file_conflict:
        if queued["waiting_for"] == task_id:
            # Task will be available after audit
            notify_queued_task(queued["task_id"], "Conflict resolving soon")

    save_state()
```

### On Audit Pass (Full Release)

```python
def fully_release_locks(task_id):
    """Fully release locks after audit passes."""

    # Remove from in_progress (which holds the locks)
    remove_from_in_progress(task_id)

    # Process queued tasks
    for queued in list(queued_for_file_conflict):
        if queued["waiting_for"] == task_id:
            # Move to available
            queued_for_file_conflict.remove(queued)
            available_tasks.append(queued["task_id"])

            log_event("task_unqueued", task_id=queued["task_id"],
                      was_waiting_for=task_id)

    save_state()
```

### On Blocking Task Failure

When a task that other tasks are waiting for fails or halts:

```python
def handle_blocking_task_failure(failed_task_id, failure_reason):
    """Release queued tasks when their blocker fails."""

    for queued in list(queued_for_file_conflict):
        if queued["waiting_for"] == failed_task_id:
            # Move to available with coordination notice
            queued_for_file_conflict.remove(queued)
            available_tasks.append(queued["task_id"])

            log_event("task_unqueued_blocker_failed",
                      task_id=queued["task_id"],
                      was_waiting_for=failed_task_id,
                      blocker_failure_reason=failure_reason)

    save_state()
```

**Trigger this handler when:**

- Blocking task receives `AUDIT_FAILED` 3 times (halted)
- Blocking task enters divine intervention
- Blocking task is manually aborted
- Blocking task times out

## Queue Timeout Handling

Queued tasks have a timeout to prevent indefinite waits.

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

## File Conflict Signal

If a developer discovers they need a locked file during work:

```
FILE CONFLICT: [task ID]

Discovered Need: [file path]
Reason: [why this file is needed]
Currently Locked By: [conflicting task if known]

Cannot proceed without access to this file.
```

### Coordinator Response

On receiving FILE CONFLICT:

```python
def handle_file_conflict_signal(task_id, file_path):
    """Handle developer-reported file conflict."""

    # Find who has the lock
    lock_holder = find_lock_holder(file_path)

    if lock_holder is None:
        # No conflict - developer may proceed
        return "No conflict detected. Proceed with modification."

    if lock_holder["status"] == "awaiting-audit":
        # Will resolve soon
        return f"File locked by {lock_holder['task_id']} (awaiting audit). "
               f"Estimated availability: soon. Continue with other work."

    # Active conflict
    options = [
        "1. Wait for task completion",
        "2. Coordinate with concurrent developer",
        "3. Restructure approach to avoid shared file"
    ]

    log_event("file_conflict_escalated", task_id=task_id, file=file_path,
              holder=lock_holder["task_id"])

    # May need divine clarification for complex conflicts
    return generate_conflict_guidance(task_id, lock_holder, options)
```

## Merge Conflict Recovery

If git merge conflicts occur despite precautions:

```python
def handle_merge_conflict(task_id, conflicting_files):
    """Handle unexpected merge conflicts."""

    log_event("merge_conflict", task_id=task_id, files=conflicting_files)

    # Dispatch remediation agent to resolve
    dispatch_remediation_agent({
        "issue_type": "merge_conflict",
        "task_id": task_id,
        "conflicting_files": conflicting_files,
        "instruction": "Resolve merge conflicts preserving both changes where possible"
    })
```

## Race Condition Handling for Parallel Dispatch

When dispatching multiple agents in parallel, race conditions can occur at multiple points. This section specifies
handling.

### Signal Processing Order

When multiple agents complete simultaneously:

```python
def process_agent_signals_safely(signals: list[dict]):
    """Process multiple agent signals atomically."""

    # 1. Acquire state lock
    with state_lock:
        state = load_state()

        # 2. Process signals in deterministic order (by timestamp)
        signals.sort(key=lambda s: s['timestamp'])

        for signal in signals:
            # 3. Each signal sees state updated by previous signals
            state = apply_signal_to_state(state, signal)
            log_event(f"{signal['type']}_processed",
                      agent_id=signal['agent_id'],
                      processing_order=signals.index(signal))

        # 4. Single atomic state save
        save_state_atomic(state)
```

### State Update Serialization

All state updates MUST be serialized through the coordinator:

| Operation        | Serialization Method      | Conflict Resolution                         |
|------------------|---------------------------|---------------------------------------------|
| Agent dispatch   | Single coordinator thread | N/A - only coordinator dispatches           |
| Signal receipt   | Timestamp-ordered queue   | Earlier signal wins                         |
| State file write | Atomic rename pattern     | Latest write wins (see state-management.md) |
| Event log append | Append-only JSONL         | No conflicts (append-only)                  |

### Parallel Dispatch Safety

When dispatching multiple developers simultaneously:

```python
def dispatch_parallel_developers(tasks: list[str]):
    """Dispatch multiple developers with race-safe state updates."""

    # 1. Pre-check all file conflicts BEFORE any dispatch
    conflict_check = {}
    for task_id in tasks:
        potential_files = analyze_file_conflicts(task_id, plan)
        conflict_check[task_id] = check_file_conflicts(task_id, potential_files)

    # 2. Filter to non-conflicting tasks only
    safe_tasks = [t for t in tasks if not conflict_check[t]]

    # 3. Reserve state slots atomically
    with state_lock:
        state = load_state()

        for task_id in safe_tasks:
            # Reserve slot in state
            state['in_progress_tasks'].append({
                'task_id': task_id,
                'status': 'dispatching',  # Pre-dispatch state
                'reserved_at': datetime.now().isoformat()
            })
            state['available_tasks'].remove(task_id)

        save_state_atomic(state)

    # 4. Now dispatch (outside lock - Task tool calls are slow)
    agent_ids = []
    for task_id in safe_tasks:
        result = Task(...)  # Dispatch developer
        agent_ids.append((task_id, result.agent_id))

    # 5. Update state with actual agent IDs
    with state_lock:
        state = load_state()

        for task_id, agent_id in agent_ids:
            task_entry = find_task_entry(state, task_id)
            task_entry['developer_id'] = agent_id
            task_entry['status'] = 'implementing'
            task_entry['dispatched_at'] = datetime.now().isoformat()

        save_state_atomic(state)
```

### Handling Concurrent Completions

When two agents signal completion for tasks that unblock the same dependent:

```python
def handle_concurrent_completions(completed_tasks: list[str]):
    """Ensure dependent tasks are unblocked exactly once."""

    with state_lock:
        state = load_state()

        newly_unblocked = set()

        for task_id in completed_tasks:
            # Mark complete
            state['completed_tasks'].append(task_id)

            # Check what this unblocks
            for blocked_task, blockers in state['blocked_tasks'].items():
                if task_id in blockers:
                    blockers.remove(task_id)
                    if not blockers:  # All blockers cleared
                        newly_unblocked.add(blocked_task)

        # Move newly unblocked to available (deduplicated via set)
        for task_id in newly_unblocked:
            if task_id not in state['available_tasks']:
                state['available_tasks'].append(task_id)
                del state['blocked_tasks'][task_id]

        save_state_atomic(state)

    return newly_unblocked
```

### Event Log Race Safety

The event log uses append-only writes to avoid race conditions:

```python
def log_event_safe(event: dict):
    """Append event to log atomically."""

    # JSONL format - each event is one line
    # Append is atomic on POSIX for reasonable line sizes
    with open(EVENT_LOG_FILE, 'a') as f:
        f.write(json.dumps(event) + '\n')
        f.flush()
        os.fsync(f.fileno())
```

Multiple concurrent appends are safe because:

1. Each event is a single line
2. POSIX guarantees atomic appends for small writes
3. Order in file reflects true append order

---

## Best Practices for Plan Authors

To minimize file conflicts, plan authors should:

1. **Isolate task scope**: Each task should have clear file boundaries
2. **Sequence shared file access**: Use `blocked_by` to serialize tasks touching the same files
3. **Split large files early**: If multiple tasks need the same file, consider splitting it first
4. **Document file ownership**: In work descriptions, be explicit about which files the task should modify

Example of good task sequencing:

```markdown
#### Task 2-1-1: Create User Model

**Work**: Create `src/models/user.py`
**Blocked By**: none

---

#### Task 2-1-2: Create User Repository

**Work**: Create `src/repositories/user_repository.py`
**Blocked By**: 2-1-1

---

#### Task 2-1-3: Add User Validation

**Work**: Add validation methods to `src/models/user.py`
**Blocked By**: 2-1-1 # ← Serializes access to user.py
```
