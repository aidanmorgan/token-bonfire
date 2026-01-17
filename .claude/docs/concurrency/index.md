# Concurrent File Modification

With `{{ACTIVE_DEVELOPERS}}` parallel developers, file conflicts are possible. This document provides an overview of how
the coordinator prevents and handles concurrent modifications.

## Overview

The concurrency system uses a file-locking protocol to prevent conflicts when multiple developers work in parallel. The
system includes:

- **File Lock Protocol**: Pre-dispatch analysis and conflict detection
- **Queue Management**: Timeout handling for tasks waiting on locked files
- **Conflict Handling**: Runtime conflict detection and resolution
- **Race Safety**: Prevention of race conditions in parallel operations

## Navigation

- [File Locks](file-locks.md) - File lock protocol and lifecycle
- [Queue Management](queue-management.md) - Queue timeout handling
- [Conflict Handling](conflict-handling.md) - Runtime conflict handling
- [Race Safety](race-safety.md) - Race condition prevention and best practices

## Quick Reference

### File Lock States

1. **Locked** - File is actively being modified by a developer
2. **Releasing** - Developer completed work, awaiting review/audit
3. **Released** - File available for modification

### Conflict Resolution Options

- **QUEUE** - Wait for conflicting task to complete
- **COORDINATE** - Dispatch with explicit coordination instructions
- **SKIP** - Select different task instead

### Queue Behavior

- **Timeout**: 30 minutes maximum wait
- **Max Retries**: 3 timeouts before escalation
- **Escalation**: Divine intervention after retry exhaustion

## State Tracking

File locks and queued tasks are tracked in `{{STATE_FILE}}`:

```json
{
  "in_progress_tasks": [
    {
      "task_id": "task-3",
      "developer_id": "dev-agent-1",
      "status": "implementing",
      "locked_files": ["src/auth/authenticator.py"],
      "lock_acquired_at": "ISO-8601"
    }
  ],
  "queued_for_file_conflict": [
    {
      "task_id": "task-7",
      "waiting_for": "task-3",
      "conflicting_files": ["src/auth/authenticator.py"],
      "queued_at": "ISO-8601",
      "timeout_at": "ISO-8601",
      "queue_retry_count": 0
    }
  ]
}
```
