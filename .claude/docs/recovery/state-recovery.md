# State File Recovery

Procedures for detecting and recovering from state file corruption or loss.

## Overview

The state file maintains the current operational state of the coordinator. When corrupted or missing, it can be
reconstructed from the event log, which serves as the authoritative record.

See also:

- [Event Log Recovery](event-log-recovery.md) - Event log as source of truth for reconstruction
- [Session Recovery](session-recovery.md) - Complete session recovery procedures
- [Recovery Index](index.md) - Overview of all recovery procedures

---

## Corruption Detection

```python
def validate_state_file(state_file_path: str) -> ValidationResult:
    """Validate state file integrity."""

    if not os.path.exists(state_file_path):
        return ValidationResult(status='missing', recoverable=True)

    try:
        with open(state_file_path, 'r') as f:
            content = f.read()

        state = json.loads(content)

        # Validate required fields
        required_fields = ['session_id', 'saved_at', 'completed_tasks', 'available_tasks']
        missing = [f for f in required_fields if f not in state]

        if missing:
            return ValidationResult(
                status='incomplete',
                recoverable=True,
                missing_fields=missing
            )

        return ValidationResult(status='valid', state=state)

    except json.JSONDecodeError as e:
        return ValidationResult(
            status='corrupted',
            recoverable=True,
            error=str(e)
        )
```

## Recovery from Corrupted State

```python
def recover_corrupted_state(state_file_path: str, event_log_path: str):
    """Recover state from event log."""

    # 1. Backup corrupted state
    backup_path = f"{state_file_path}.corrupted.{datetime.now().strftime('%Y%m%d%H%M%S')}"
    if os.path.exists(state_file_path):
        shutil.copy(state_file_path, backup_path)

    # 2. Reconstruct from event log
    state = reconstruct_state_from_events(event_log_path)

    # 3. Add session info
    state['session_id'] = str(uuid.uuid4())
    state['session_started_at'] = datetime.now().isoformat()
    state['previous_session_id'] = 'recovered'
    state['session_resume_count'] = 0
    state['recovered_from'] = 'event_log'
    state['recovery_timestamp'] = datetime.now().isoformat()

    # 4. Save recovered state
    save_state(state, state_file_path)

    log_event("state_recovered_from_event_log",
              backup_path=backup_path)

    return state
```

---

## Cross-References

- [Event Log Recovery](event-log-recovery.md) - Event reconstruction procedures
- [Session Recovery](session-recovery.md) - Complete recovery orchestration
- [State Management](../state-management.md) - State schema and persistence
