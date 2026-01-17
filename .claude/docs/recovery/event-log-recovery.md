# Event Log Recovery

Procedures for detecting and recovering from event log corruption, truncation, or loss.

## Overview

The event log is the authoritative source of truth for the coordination system. When the event log is corrupted or
missing, it must be recovered or reconstructed to ensure system integrity.

See also:

- [State Recovery](state-recovery.md) - Recovering state files from event logs
- [Session Recovery](session-recovery.md) - Complete session recovery procedures
- [Recovery Index](index.md) - Overview of all recovery procedures

---

## Corruption Detection

Check event log integrity on session start:

```python
def validate_event_log(event_log_path: str) -> ValidationResult:
    """Validate event log file integrity."""

    if not os.path.exists(event_log_path):
        return ValidationResult(status='missing', recoverable=True)

    try:
        with open(event_log_path, 'r') as f:
            line_number = 0
            last_valid_line = 0
            events = []

            for line in f:
                line_number += 1
                line = line.strip()
                if not line:
                    continue

                try:
                    event = json.loads(line)
                    # Validate required fields
                    if 'event_type' not in event or 'timestamp' not in event:
                        raise ValueError("Missing required fields")
                    events.append(event)
                    last_valid_line = line_number
                except json.JSONDecodeError as e:
                    return ValidationResult(
                        status='corrupted',
                        recoverable=True,
                        corruption_line=line_number,
                        last_valid_line=last_valid_line,
                        error=str(e)
                    )

        return ValidationResult(status='valid', events=events)

    except IOError as e:
        return ValidationResult(status='unreadable', recoverable=False, error=str(e))
```

## Recovery from Truncation

If event log is truncated (incomplete last line):

```python
def recover_truncated_log(event_log_path: str, last_valid_line: int):
    """Recover event log by truncating to last valid entry."""

    # 1. Read valid portion
    valid_lines = []
    with open(event_log_path, 'r') as f:
        for i, line in enumerate(f, 1):
            if i > last_valid_line:
                break
            valid_lines.append(line)

    # 2. Backup corrupted file
    backup_path = f"{event_log_path}.corrupted.{datetime.now().strftime('%Y%m%d%H%M%S')}"
    shutil.copy(event_log_path, backup_path)

    # 3. Write valid portion
    with open(event_log_path, 'w') as f:
        f.writelines(valid_lines)

    # 4. Log recovery
    log_event("event_log_recovered",
              original_lines=last_valid_line + 1,  # Approximate
              recovered_lines=last_valid_line,
              backup_path=backup_path)

    return len(valid_lines)
```

## Recovery from Missing Event Log

If event log doesn't exist but state file does:

```python
def recover_missing_event_log(state_file_path: str, event_log_path: str):
    """Reconstruct minimal event log from state file."""

    state = load_state(state_file_path)

    # Create minimal event log with current state as checkpoint
    events = [
        {
            "event_type": "event_log_reconstructed",
            "timestamp": datetime.now().isoformat(),
            "reason": "event_log_missing",
            "state_file_timestamp": state.get('saved_at', 'unknown')
        },
        {
            "event_type": "state_checkpoint",
            "timestamp": datetime.now().isoformat(),
            "completed_tasks": state.get('completed_tasks', []),  # string[]
            "in_progress_tasks": [t['task_id'] for t in state.get('in_progress_tasks', [])],  # object[] → task_ids
            "available_tasks": state.get('available_tasks', [])
        }
    ]

    with open(event_log_path, 'w') as f:
        for event in events:
            f.write(json.dumps(event) + '\n')

    log_event("event_log_created_from_state",
              events_created=len(events))
```

## State Reconstruction from Event Log

If state file is corrupted but event log is valid:

```python
def reconstruct_state_from_events(event_log_path: str) -> dict:
    """Rebuild state by replaying events."""

    state = {
        # Task tracking (per state-schema.md)
        'completed_tasks': [],  # string[] - task IDs that passed audit
        'in_progress_tasks': [],  # object[] - tasks being worked
        'available_tasks': [],  # string[] - unblocked tasks ready for assignment
        'blocked_tasks': {},  # object - maps task to its blockers
        'pending_critique': [],  # string[] - tasks awaiting critic review
        'pending_audit': [],  # string[] - tasks awaiting auditor verification

        # Agent tracking
        'active_agents': {},  # maps agent_id to {task_id, type, dispatched_at}
        'active_developers': {},  # maps agent_id to task info
        'active_auditors': {},  # maps agent_id to task info
        'active_critics': {},  # maps agent_id to task info

        # Failure tracking
        'critique_failures': {},  # maps task_id to failure count
        'critic_timeouts': {},  # maps task_id to timeout count
        'audit_failures': {},  # maps task_id to audit failure count

        # Infrastructure
        'infrastructure_blocked': False,
        'infrastructure_issue': None,
        'active_remediation': None,
        'remediation_attempt_count': 0,

        # Expert tracking
        'experts': [],  # array of expert definitions
        'active_experts': {},  # maps run_id to active expert info
        'expert_stats': {},  # maps expert_id to usage metrics
        'pending_delegation_requests': [],
        'paused_agents': {},

        # Divine intervention
        'pending_divine_questions': [],

        # File conflict tracking
        'queued_for_file_conflict': [],  # tasks waiting for file availability
        'queue_retry_tracker': {},  # maps task_id to retry count (persisted)

        # Task quality / BA
        'task_quality_assessed': False,
        'pending_expansions': {},
        'active_business_analysts': {},
        'expanded_tasks': {},

        # Agent files
        'agent_files_created': {}
    }

    with open(event_log_path, 'r') as f:
        for line in f:
            event = json.loads(line.strip())
            apply_event_to_state(state, event)

    return state


def apply_event_to_state(state: dict, event: dict):
    """Apply a single event to state."""

    event_type = event.get('event_type')

    if event_type == 'developer_dispatched':
        task_id = event.get('task_id') or event.get('task')
        if task_id in state['available_tasks']:
            state['available_tasks'].remove(task_id)
        state['in_progress_tasks'].append({
            'task_id': task_id,
            'agent_id': event.get('agent_id'),
            'status': 'implementing',
            'dispatched_at': event.get('timestamp')
        })
        agent_id = event.get('agent_id')
        if agent_id:
            state['active_developers'][agent_id] = {
                'task_id': task_id,
                'dispatched_at': event.get('timestamp')
            }

    elif event_type == 'developer_ready_for_review':
        task_id = event.get('task_id')
        agent_id = event.get('agent_id')

        if agent_id and agent_id in state['active_developers']:
            del state['active_developers'][agent_id]

        for task in state['in_progress_tasks']:
            if task['task_id'] == task_id:
                task['status'] = 'awaiting-review'
                break
        if task_id not in state['pending_critique']:
            state['pending_critique'].append(task_id)

    elif event_type == 'developer_blocked':
        task_id = event['task_id']
        state['infrastructure_blocked'] = True
        state['infrastructure_issue'] = event.get('issue_type')
        # Task status remains 'implementing' - will resume after remediation

    elif event_type == 'developer_incomplete':
        task_id = event['task_id']
        # Task stays in progress but may need escalation based on attempt_number
        if event.get('escalate'):
            # Divine intervention needed - update status
            for task in state['in_progress_tasks']:
                if task['task_id'] == task_id:
                    task['status'] = 'awaiting-divine-guidance'
                    break

    elif event_type == 'critic_pass':
        task_id = event.get('task_id')
        if task_id in state['pending_critique']:
            state['pending_critique'].remove(task_id)
        for task in state['in_progress_tasks']:
            if task['task_id'] == task_id:
                task['status'] = 'awaiting-audit'
                break
        if task_id not in state['pending_audit']:
            state['pending_audit'].append(task_id)
        agent_id = event.get('agent_id')
        if agent_id and agent_id in state['active_critics']:
            del state['active_critics'][agent_id]

    elif event_type == 'critic_fail':
        task_id = event.get('task_id')
        if task_id in state['pending_critique']:
            state['pending_critique'].remove(task_id)
        for task in state['in_progress_tasks']:
            if task['task_id'] == task_id:
                task['status'] = 'implementing'
                break
        state['critique_failures'][task_id] = state['critique_failures'].get(task_id, 0) + 1
        agent_id = event.get('agent_id')
        if agent_id and agent_id in state['active_critics']:
            del state['active_critics'][agent_id]

    elif event_type == 'task_complete':
        task_id = event.get('task_id')
        if task_id in state['pending_audit']:
            state['pending_audit'].remove(task_id)
        state['in_progress_tasks'] = [t for t in state['in_progress_tasks'] if t['task_id'] != task_id]
        if task_id not in state['completed_tasks']:
            state['completed_tasks'].append(task_id)
        agent_id = event.get('agent_id')
        if agent_id and agent_id in state['active_auditors']:
            del state['active_auditors'][agent_id]

    elif event_type == 'auditor_fail':
        task_id = event.get('task_id')
        if task_id in state['pending_audit']:
            state['pending_audit'].remove(task_id)
        state['audit_failures'][task_id] = state['audit_failures'].get(task_id, 0) + 1
        for task in state['in_progress_tasks']:
            if task['task_id'] == task_id:
                task['status'] = 'implementing'
                break
        agent_id = event.get('agent_id')
        if agent_id and agent_id in state['active_auditors']:
            del state['active_auditors'][agent_id]

    elif event_type == 'infrastructure_blocked':
        state['infrastructure_blocked'] = True
        state['infrastructure_issue'] = event.get('issue_type')

    elif event_type == 'infrastructure_restored':
        state['infrastructure_blocked'] = False
        state['infrastructure_issue'] = None
        state['remediation_attempt_count'] = 0

    elif event_type == 'agent_definition_created':
        agent_type = event.get('agent_type')
        state['agent_files_created'][agent_type] = {
            'definition_hash': event.get('definition_hash'),
            'created_at': event['timestamp']
        }

    elif event_type == 'critic_dispatched':
        task_id = event.get('task_id')
        agent_id = event.get('agent_id')
        if task_id in state['pending_critique']:
            state['pending_critique'].remove(task_id)
        if agent_id:
            state['active_critics'][agent_id] = {
                'task_id': task_id,
                'dispatched_at': event.get('timestamp')
            }

    elif event_type == 'critic_timeout':
        task_id = event.get('task_id')
        state['critic_timeouts'][task_id] = state['critic_timeouts'].get(task_id, 0) + 1

    elif event_type == 'auditor_dispatched':
        task_id = event.get('task_id')
        agent_id = event.get('agent_id')
        if task_id in state['pending_audit']:
            state['pending_audit'].remove(task_id)
        if agent_id:
            state['active_auditors'][agent_id] = {
                'task_id': task_id,
                'dispatched_at': event.get('timestamp')
            }

    elif event_type == 'auditor_blocked':
        task_id = event['task_id']
        state['infrastructure_blocked'] = True
        state['infrastructure_issue'] = event.get('pre_existing_failures')

    elif event_type == 'remediation_dispatched':
        agent_id = event.get('agent_id')
        state['active_remediation'] = agent_id
        state['remediation_attempt_count'] = event.get('attempt_number', 1)

    elif event_type == 'remediation_complete':
        state['active_remediation'] = None

    elif event_type == 'health_audit_pass':
        state['infrastructure_blocked'] = False
        state['infrastructure_issue'] = None
        state['remediation_attempt_count'] = 0

    elif event_type == 'health_audit_fail':
        # Keep infrastructure_blocked = True, increment count handled by remediation
        pass

    elif event_type == 'task_queued_for_conflict':
        # Track queue retry counts
        task_id = event['task_id']
        retry_count = event.get('retry_count', 0)
        if 'queue_retry_tracker' not in state:
            state['queue_retry_tracker'] = {}
        state['queue_retry_tracker'][task_id] = retry_count

    elif event_type == 'queue_timeout':
        # Update retry count when task times out
        task_id = event['task_id']
        retry_count = event.get('retry_count', 1)
        if 'queue_retry_tracker' not in state:
            state['queue_retry_tracker'] = {}
        state['queue_retry_tracker'][task_id] = retry_count

    elif event_type == 'task_unqueued':
        # Clean up retry tracker when task is unqueued
        task_id = event['task_id']
        if 'queue_retry_tracker' in state and task_id in state['queue_retry_tracker']:
            del state['queue_retry_tracker'][task_id]

    elif event_type == 'expert_created':
        expert_info = {
            'agent_id': event.get('agent_id'),
            'agent_type': event.get('agent_type'),
            'name': event.get('name'),
            'domain': event.get('domain'),
            'created_at': event['timestamp']
        }
        if 'experts' not in state:
            state['experts'] = []
        state['experts'].append(expert_info)

    elif event_type == 'expert_delegated':
        run_id = event.get('run_id')
        state['active_experts'][run_id] = {
            'agent_id': event.get('agent_id'),
            'from_agent_id': event.get('from_agent_id'),
            'task_id': event.get('task_id'),
            'dispatched_at': event['timestamp']
        }

    elif event_type == 'expert_complete':
        run_id = event.get('run_id')
        agent_id = event.get('agent_id')
        if run_id in state.get('active_experts', {}):
            del state['active_experts'][run_id]
        # Update expert stats
        if agent_id and 'expert_stats' in state:
            if agent_id not in state['expert_stats']:
                state['expert_stats'][agent_id] = {'completions': 0, 'failures': 0}
            state['expert_stats'][agent_id]['completions'] += 1

    elif event_type == 'expert_failed':
        run_id = event.get('run_id')
        agent_id = event.get('agent_id')
        if run_id in state.get('active_experts', {}):
            del state['active_experts'][run_id]
        # Update expert stats
        if agent_id and 'expert_stats' in state:
            if agent_id not in state['expert_stats']:
                state['expert_stats'][agent_id] = {'completions': 0, 'failures': 0}
            state['expert_stats'][agent_id]['failures'] += 1

    elif event_type == 'agent_seeks_guidance':
        question = {
            'agent_id': event.get('agent_id'),
            'task_id': event.get('task_id'),
            'question': event.get('question'),
            'options': event.get('options'),
            'timestamp': event['timestamp'],
            'response': None
        }
        state['pending_divine_questions'].append(question)

    elif event_type == 'divine_response_received':
        # Find and update the pending question
        task_id = event.get('task_id')
        for q in state['pending_divine_questions']:
            if q['task_id'] == task_id:
                q['response'] = event.get('response')
                break

    elif event_type == 'business_analyst_dispatched':
        task_id = event['task_id']
        agent_id = event.get('agent_id')
        state['active_business_analysts'][agent_id] = task_id
        state['pending_expansions'][task_id] = agent_id

    elif event_type == 'task_expanded':
        task_id = event['task_id']
        if task_id in state['pending_expansions']:
            del state['pending_expansions'][task_id]
        state['expanded_tasks'][task_id] = {
            'confidence': event.get('confidence'),
            'expansion_summary': event.get('expansion_summary'),
            'expanded_at': event['timestamp']
        }

    elif event_type == 'task_quality_assessment':
        state['task_quality_assessed'] = True

    elif event_type == 'workflow_complete':
        # Final state - all tasks complete
        pass

    elif event_type == 'workflow_failed':
        # Record failure but don't modify task state
        pass

    # Audit-trail only events - no state modification needed
    # These events are logged for debugging/auditing but don't change coordinator state
    elif event_type in (
            # Session lifecycle (state managed separately)
            'session_start', 'session_resumed', 'session_pause',
            'compaction_start', 'compaction_complete', 'usage_check',
            'event_log_reconstructed', 'state_checkpoint',
            # Agent management (state in agent_files_created)
            'agent_definition_created',
            # Progress reporting (informational only)
            'developer_checkpoint', 'signal_rejected',
            'environment_verification_passed', 'environment_verification_failed',
            # Expert lifecycle (handled by expert_complete/expert_failed)
            'expert_request_received', 'delegation_queued', 'delegation_results_delivered',
            'expert_out_of_scope',
            # Divine intervention (handled by divine_response_received)
            'coordinator_prays', 'agent_resumes_with_guidance',
            # Resume handling (state already reconstructed)
            'task_restarted_on_resume', 'task_reverification_required',
            # Infrastructure (state handled by blocked/restored events)
            'health_audit_dispatched', 'remediation_failed', 'health_audit_unexpected',
            'remediation_exhausted',
            # BA workflow (handled by task_expanded)
            'expansion_needs_clarification',
    ):
        pass  # Audit trail only

    else:
        # Unknown event type - log warning but don't fail reconstruction
        # This allows forward compatibility with new event types
        import logging
        logging.warning(f"Unknown event type during state reconstruction: {event_type}")
```

---

## Cross-References

- [State Recovery](state-recovery.md) - Recovering corrupted state files
- [Session Recovery](session-recovery.md) - Complete session recovery flow
- [Event Logging](../event-logging.md) - Event structure and logging procedures
