# State Persistence

[← Back to State Management](index.md)

State mutations must be atomic to survive coordinator crashes.

---

## Atomic State Updates

### Write Procedure

```python
def save_state_atomic(state):
    temp_path = f"{STATE_FILE}.tmp"

    # 1. Write to temp file with fsync
    with open(temp_path, 'w') as f:
        json.dump(state, f, indent=2)
        f.flush()
        os.fsync(f.fileno())

    # 2. Atomic rename (POSIX guarantees atomicity)
    os.rename(temp_path, STATE_FILE)
```

### Recovery on Resume

```python
def load_state_with_recovery():
    temp_path = f"{STATE_FILE}.tmp"

    # Check for incomplete write
    if os.path.exists(temp_path):
        os.remove(temp_path)  # Discard incomplete

    if os.path.exists(STATE_FILE):
        return json.load(open(STATE_FILE))

    # Reconstruct from event log if no state file
    if os.path.exists(EVENT_LOG_FILE):
        return reconstruct_state_from_events()

    return None  # Fresh start
```

---

## Related Documentation

- [Update Triggers](update-triggers.md) - When state is persisted
- [Recovery Procedures](../recovery-procedures.md) - Error recovery
- [State Schema](../orchestrator/state-schema.md) - Complete state file format
- [Event Schema](../orchestrator/event-schema.md) - Event log format
