# Concurrent File Modification

With `{{ACTIVE_DEVELOPERS}}` parallel developers, file conflicts are possible. This document specifies how the coordinator prevents and handles concurrent modifications.

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
        "QUEUE",       # Wait for conflicting task to complete
        "COORDINATE",  # Dispatch with explicit coordination instructions
        "SKIP"         # Select different task instead
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
      "conflicting_files": ["src/auth/authenticator.py"],
      "queued_at": "ISO-8601"
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

When a developer signals `READY FOR AUDIT`:

```python
def release_file_locks(task_id):
    """Release file locks and process queued tasks."""

    task = get_in_progress_task(task_id)

    # Note: Don't fully release until audit PASSES
    # But allow other developers to see files will be available soon
    task["status"] = "awaiting-audit"
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
        return f"File locked by {lock_holder['task_id']} (awaiting audit). " \
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
**Blocked By**: 2-1-1  # ← Serializes access to user.py
```
