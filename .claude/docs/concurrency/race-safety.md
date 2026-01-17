# Race Safety

[← Back to Concurrency Index](index.md)

Prevention of race conditions when dispatching and managing parallel developers.

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

---

[← Back to Concurrency Index](index.md)
