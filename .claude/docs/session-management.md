# Session Management

## Auto-Compaction Procedure

When context ≤`{{CONTEXT_THRESHOLD}}` remaining:

### Persist Phase
1. Pause all new task assignments
2. Collect checkpoints from all active developers
3. Increment `compaction_count`
4. Write state to `{{STATE_FILE}}`
5. Log event: `compaction_start` with `compaction_number` and `context_remaining`

### Compact Phase
1. Execute `/compact`

### Resume Phase
1. Read state file to restore coordinator memory
2. Check if `compaction_count % 2 == 0` for full plan reload
3. If full reload required, read the complete plan; otherwise read plan summary only
4. Restore developers by re-assigning in-progress tasks with checkpoint context
5. Log event: `compaction_complete` with `compaction_number` and `full_reload` boolean
6. Continue the execution loop

### Compaction Output

Before compaction:
```
AUTO-COMPACTION #[N] - Context at {{CONTEXT_THRESHOLD}}

State persisted to: {{STATE_FILE}}
```

After reload (odd compaction - state only):
```
RESUMED - Compaction #[N] complete

Completed: [N]/[total] tasks
Restoring: [N] in-progress tasks
Pending audit: [N] tasks
```

After reload (even compaction - full plan reload):
```
RESUMED - Compaction #[N] complete (full plan reload)

Plan reloaded: {{PLAN_FILE}}
Total tasks: [N]
Completed: [N]/[total] tasks
Restoring: [N] in-progress tasks
Pending audit: [N] tasks
Blocked graph rebuilt: [N] relationships
```

## Full Plan Reload (Every Second Compaction)

**Trigger:** `compaction_count % 2 == 0` (compactions 2, 4, 6, ...)

Context compaction discards detail to fit the window. After two compactions, accumulated loss causes drift from the plan. Full reload restores accuracy.

**Procedure:**
1. Read `{{PLAN_FILE}}` in full without summarization
2. Re-parse all task definitions, dependencies, and acceptance criteria
3. Cross-reference with `completed_tasks` to identify remaining work
4. Verify `in_progress_tasks` match plan task definitions
5. Rebuild `blocked_tasks` graph from plan dependencies

**Output:**
```
FULL PLAN RELOAD - Compaction #[N]

Plan: {{PLAN_FILE}}
Total tasks: [N]
Completed: [N] (verified against plan)
Remaining: [N]
Blocked graph rebuilt: [N] blocking relationships
```

## Session Pause Procedure

Triggers: `remaining` ≤`{{SESSION_THRESHOLD}}` from usage script, user stop, or system error.

1. Stop all new task assignments immediately
2. Collect checkpoints from all active developers
3. Write state to `{{STATE_FILE}}`
4. Log event: `session_pause` with `reason`, `remaining_percent`, and `resets_at`
5. Output the pause message with progress summary
6. Wait until `resets_at` + 5 minutes
7. Auto-resume using the After Session Pause procedure

### Session Pause Output

When pausing:
```
SESSION PAUSED - [reason: Usage limit | User stop | System error]

State persisted to: {{STATE_FILE}}
Progress: [N]/[total] tasks complete
In progress: [N] tasks
Pending audit: [N] tasks
Compactions this session: [N]

Session remaining: [remaining]%
Session resets at: [resets_at]
Auto-resuming at: [resets_at + 5 minutes]
```

After wait completes:
```
SESSION RESUMED - Reset complete
```

## Resume Procedures

### After Compaction

1. Read state file to restore coordinator memory
2. Check if `compaction_count % 2 == 0` for full plan reload
3. Read plan file and reference definitions
4. Process `pending_divine_questions` before restoring agents
5. Restore in-progress work by re-assigning tasks with checkpoint context
6. Process pending audits by spawning auditors for tasks in `pending_audit`
7. Continue the execution loop

### After Session Pause

1. Output "SESSION RESUMED"
2. Log event: `session_resume` with `resume_count` and `tasks_to_revalidate`
3. Read state file, plan file, and reference definitions
4. Validate state integrity
5. Increment `session_resume_count`
6. Process `pending_divine_questions` before restoring agents
7. Spawn auditor pool for tasks completed in the last `{{RECENT_COMPLETION_WINDOW}}`
8. Wait for validation to complete before assigning new work
9. Restore in-progress work by re-assigning tasks with checkpoint context
10. Process pending audits by spawning auditors
11. Continue the execution loop

### Resume Task Assignment Format

For tasks in progress when paused:

```
Task: [task ID from plan]
Work: [copied from plan]
Acceptance Criteria: [copied from plan - bash commands that verify completion]
Blocked By: [list or "none"]
Resume Context: [last_checkpoint from state file]
Previous Progress: Review existing work before continuing.

[Include: Developer References]
```

Log event: `developer_dispatched` with `task_id`, `agent_id`, `blocked_by`, and `resumed: true`.

---

## Coordinator Recovery

If the coordinator crashes or is terminated mid-operation, use this procedure to recover.

### Recovery Trigger

A coordinator restart (new conversation after unexpected termination) requires recovery when:
- `{{STATE_FILE}}` exists (indicating prior work)
- No explicit pause signal was recorded

### Recovery Procedure

```python
def coordinator_recovery():
    """Recover coordinator state after unexpected termination."""

    # Step 1: Load state with atomic recovery
    state = load_state_with_recovery()  # See state-management.md

    if state is None:
        output("No prior state found. Starting fresh.")
        return start_fresh()

    output(f"COORDINATOR RECOVERY - Restoring from {STATE_FILE}")

    # Step 2: Reconcile with event log
    last_state_time = datetime.fromisoformat(state['saved_at'])
    orphan_events = get_events_after(last_state_time)

    if orphan_events:
        output(f"Reconciling {len(orphan_events)} events from log")
        for event in orphan_events:
            apply_event_to_state(state, event)

    # Step 3: Identify orphaned agents
    orphaned = identify_orphaned_agents(state)
    if orphaned:
        output(f"Found {len(orphaned)} orphaned agents")
        for agent in orphaned:
            # Agent was dispatched but never completed
            # Re-add task to available queue
            state['available_tasks'].append(agent['task_id'])
            del state['active_agents'][agent['agent_id']]

    # Step 4: Validate completed tasks
    recent_completions = get_recent_completions(state, RECENT_COMPLETION_WINDOW)
    if recent_completions:
        output(f"Validating {len(recent_completions)} recent completions")
        state['pending_validation'] = recent_completions

    # Step 5: Save recovered state
    save_state_atomic(state)
    log_event("coordinator_recovered",
              orphaned_agents=len(orphaned),
              events_reconciled=len(orphan_events))

    # Step 6: Resume normal operation
    return state
```

### Orphan Agent Detection

An orphan agent is one that was dispatched (recorded in `active_agents`) but the coordinator never received its result:

```python
def identify_orphaned_agents(state):
    """Find agents dispatched but not completed."""

    orphaned = []
    for agent_id, agent in state.get('active_agents', {}).items():
        # Check if agent has a completion event in log
        if not has_completion_event(agent_id):
            orphaned.append({
                'agent_id': agent_id,
                'task_id': agent['task_id'],
                'type': agent['type'],
                'dispatched_at': agent['dispatched_at']
            })
    return orphaned
```

### Recovery Output

```
COORDINATOR RECOVERY

Prior state found: {{STATE_FILE}}
Saved at: [timestamp]
Events to reconcile: [N]
Orphaned agents: [N]
Recent completions to validate: [N]

Recovery complete. Resuming normal operation.

Progress: [N]/[total] tasks complete
Available: [N] tasks
Blocked: [N] tasks
```

### Events

| Event | Trigger | Fields |
|-------|---------|--------|
| `coordinator_recovered` | Recovery procedure completes | orphaned_agents, events_reconciled |
| `orphan_agent_detected` | Agent had no completion event | agent_id, task_id, type |
| `state_reconciled` | Event applied to recover state | event_type, task_id |
