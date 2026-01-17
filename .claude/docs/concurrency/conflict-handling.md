# Conflict Handling

[← Back to Concurrency Index](index.md)

Runtime conflict detection and resolution when developers discover file access issues during implementation.

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

---

[← Back to Concurrency Index](index.md)
