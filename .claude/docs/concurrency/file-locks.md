# File Lock Protocol

[← Back to Concurrency Index](index.md)

The file lock protocol prevents concurrent modifications by analyzing and tracking file access across parallel
developers.

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

---

[← Back to Concurrency Index](index.md)
