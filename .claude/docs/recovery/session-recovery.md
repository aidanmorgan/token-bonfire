# Session Recovery

Complete session recovery procedures that orchestrate all recovery mechanisms.

## Overview

Session recovery runs on every session start and coordinates all recovery procedures to ensure system integrity. This is
the main entry point for recovery operations.

See also:

- [Event Log Recovery](event-log-recovery.md) - Event log validation and recovery
- [State Recovery](state-recovery.md) - State file recovery
- [Agent Recovery](agent-file-recovery.md) - Agent file recovery
- [Baseline Failures](baseline-failures.md) - Pre-existing failure tracking
- [Recovery Index](index.md) - Overview of all recovery procedures

---

## Pending Queue Reconstruction

On session resume, explicitly reconstruct `pending_critique` and `pending_audit` from the event log.
This catches any tasks that completed development but haven't been reviewed/audited.

```python
def reconstruct_pending_queues(event_log_path: str, state: dict):
    """Reconstruct pending_critique and pending_audit from event log.

    This is CRITICAL for session recovery - ensures no tasks are lost
    in the review/audit pipeline.
    """

    # Track task states through events
    task_states = {}  # task_id -> 'implementing' | 'awaiting-review' | 'awaiting-audit' | 'complete'

    with open(event_log_path, 'r') as f:
        for line in f:
            event = json.loads(line.strip())
            event_type = event.get('event_type')
            task_id = event.get('task_id')

            if not task_id:
                continue

            if event_type == 'developer_dispatched':
                task_states[task_id] = 'implementing'

            elif event_type == 'developer_ready_for_review':
                task_states[task_id] = 'awaiting-review'

            elif event_type == 'critic_dispatched':
                # Still awaiting review until critic completes
                pass

            elif event_type == 'critic_pass':
                task_states[task_id] = 'awaiting-audit'

            elif event_type == 'critic_fail':
                task_states[task_id] = 'implementing'

            elif event_type == 'auditor_dispatched':
                # Still awaiting audit until auditor completes
                pass

            elif event_type == 'task_complete':
                task_states[task_id] = 'complete'

            elif event_type == 'auditor_fail':
                task_states[task_id] = 'implementing'

    # Rebuild pending queues from final states
    state['pending_critique'] = [
        tid for tid, status in task_states.items()
        if status == 'awaiting-review'
    ]
    state['pending_audit'] = [
        tid for tid, status in task_states.items()
        if status == 'awaiting-audit'
    ]

    return state
```

---

## Session Recovery Summary

On session start, run this recovery check:

```python
def session_recovery_check():
    """Run full recovery check on session start."""

    issues = []

    # 1. Check event log
    event_log_result = validate_event_log(EVENT_LOG_FILE)
    if event_log_result.status == 'corrupted':
        recover_truncated_log(EVENT_LOG_FILE, event_log_result.last_valid_line)
        issues.append(f"Event log recovered from corruption at line {event_log_result.corruption_line}")
    elif event_log_result.status == 'missing':
        issues.append("Event log missing - will create new")

    # 2. Check state file
    state_result = validate_state_file(STATE_FILE)
    if state_result.status == 'corrupted':
        recover_corrupted_state(STATE_FILE, EVENT_LOG_FILE)
        issues.append("State file recovered from event log")
    elif state_result.status == 'missing':
        issues.append("State file missing - fresh start")

    # 3. Check plan file
    plan_result = validate_plan_file(PLAN_FILE)
    if plan_result.status != 'valid':
        handle_missing_plan()  # This raises and halts

    # 4. Check agent files
    # REQUIRED_AGENTS = ['developer', 'critic', 'auditor', 'ba', 'remediation', 'health-auditor']
    for agent_name in REQUIRED_AGENTS:
        agent_path = f".claude/agents/{agent_name}.md"
        if not os.path.exists(agent_path):
            recover_missing_agent_file(agent_name, AGENT_DEFINITIONS_DOC)
            issues.append(f"Agent file recovered: {agent_name}")

    # 5. ALWAYS reconstruct pending queues on session resume
    # This is critical - ensures no tasks are lost in review/audit pipeline
    reconstruct_pending_queues(EVENT_LOG_FILE, state)
    if state['pending_critique']:
        issues.append(f"Recovered {len(state['pending_critique'])} tasks pending review")
    if state['pending_audit']:
        issues.append(f"Recovered {len(state['pending_audit'])} tasks pending audit")

    if issues:
        log_event("session_recovery_completed",
                  issues_resolved=issues)

    return issues
```

---

## Cross-References

- [Event Log Recovery](event-log-recovery.md) - Event log validation and recovery
- [State Recovery](state-recovery.md) - State file recovery procedures
- [Agent Recovery](agent-file-recovery.md) - Agent file recovery procedures
- [Baseline Failures](baseline-failures.md) - Pre-existing failure baseline
- [Session Management](../session-management.md) - Session lifecycle
