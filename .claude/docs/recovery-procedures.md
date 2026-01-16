# Recovery Procedures

Procedures for recovering from various failure scenarios.

## Event Log Recovery

### Corruption Detection

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

### Recovery from Truncation

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

### Recovery from Missing Event Log

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

### State Reconstruction from Event Log

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
    """Apply a single event to state.

    Event types match event-logging.md definitions.
    State structure matches state-schema.md (in_progress_tasks is array of objects).
    """

    event_type = event['event_type']

    if event_type == 'developer_dispatched':
        task_id = event['task_id']
        if task_id in state['available_tasks']:
            state['available_tasks'].remove(task_id)
        # in_progress_tasks is array of objects per state-schema.md
        state['in_progress_tasks'].append({
            'task_id': task_id,
            'agent_id': event.get('agent_id'),
            'status': 'implementing',
            'dispatched_at': event['timestamp']
        })
        # Track active developer
        state['active_developers'][event.get('agent_id')] = {
            'task_id': task_id,
            'dispatched_at': event['timestamp']
        }

    elif event_type == 'developer_ready_for_review':
        task_id = event['task_id']
        # Update status in in_progress_tasks array
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
        task_id = event['task_id']
        if task_id in state['pending_critique']:
            state['pending_critique'].remove(task_id)
        # Update status
        for task in state['in_progress_tasks']:
            if task['task_id'] == task_id:
                task['status'] = 'awaiting-audit'
                break
        if task_id not in state['pending_audit']:
            state['pending_audit'].append(task_id)

    elif event_type == 'critic_fail':
        task_id = event['task_id']
        if task_id in state['pending_critique']:
            state['pending_critique'].remove(task_id)
        # Update status back to implementing
        for task in state['in_progress_tasks']:
            if task['task_id'] == task_id:
                task['status'] = 'implementing'
                break
        state['critique_failures'][task_id] = state['critique_failures'].get(task_id, 0) + 1

    elif event_type == 'task_complete':
        task_id = event['task_id']
        if task_id in state['pending_audit']:
            state['pending_audit'].remove(task_id)
        # Remove from in_progress_tasks array
        state['in_progress_tasks'] = [t for t in state['in_progress_tasks'] if t['task_id'] != task_id]
        # Add to completed_tasks (which is string[] per state-schema.md)
        if task_id not in state['completed_tasks']:
            state['completed_tasks'].append(task_id)

    elif event_type == 'auditor_fail':
        task_id = event['task_id']
        if task_id in state['pending_audit']:
            state['pending_audit'].remove(task_id)
        state['audit_failures'][task_id] = state['audit_failures'].get(task_id, 0) + 1
        # Update status back to implementing for rework
        for task in state['in_progress_tasks']:
            if task['task_id'] == task_id:
                task['status'] = 'implementing'
                break

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
        task_id = event['task_id']
        agent_id = event.get('agent_id')
        state['active_critics'][agent_id] = {
            'task_id': task_id,
            'dispatched_at': event['timestamp']
        }

    elif event_type == 'critic_timeout':
        task_id = event['task_id']
        state['critic_timeouts'][task_id] = state['critic_timeouts'].get(task_id, 0) + 1

    elif event_type == 'auditor_dispatched':
        task_id = event['task_id']
        agent_id = event.get('agent_id')
        state['active_auditors'][agent_id] = {
            'task_id': task_id,
            'dispatched_at': event['timestamp']
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

## State File Recovery

### Corruption Detection

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

### Recovery from Corrupted State

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

## Plan File Recovery

### Integrity Check

```python
def validate_plan_file(plan_file_path: str) -> ValidationResult:
    """Validate plan file exists and is parseable."""

    if not os.path.exists(plan_file_path):
        return ValidationResult(
            status='missing',
            recoverable=False,
            error="Plan file not found - cannot continue without plan"
        )

    try:
        content = Read(plan_file_path)

        # Check for required sections
        required_patterns = [
            r'^## Phase \d+',  # At least one phase
            r'^### Task \d+',   # At least one task
        ]

        for pattern in required_patterns:
            if not re.search(pattern, content, re.MULTILINE):
                return ValidationResult(
                    status='incomplete',
                    recoverable=False,
                    error=f"Plan missing required section matching: {pattern}"
                )

        return ValidationResult(status='valid')

    except Exception as e:
        return ValidationResult(
            status='unreadable',
            recoverable=False,
            error=str(e)
        )
```

### Plan File Missing

If plan file is missing, this is **NOT recoverable** - escalate immediately:

```python
def handle_missing_plan():
    """Handle missing plan file - requires human intervention."""

    log_event("plan_file_missing",
              severity="CRITICAL",
              action="halting")

    raise PlanFileMissingError(
        "Plan file not found. Cannot continue execution. "
        "Please restore the plan file and restart."
    )
```

---

## Agent File Recovery

### Missing Agent Definition

```python
def recover_missing_agent_file(agent_name: str, agent_definitions_doc: str):
    """Recreate missing agent file from definitions document."""

    # 1. Find the creation prompt for this agent
    creation_prompt = extract_creation_prompt(agent_definitions_doc, agent_name)

    if not creation_prompt:
        raise AgentRecoveryError(f"No creation prompt found for {agent_name}")

    # 2. Spawn agent to recreate the file
    Task(
        model='opus',
        subagent_type='developer',
        prompt=creation_prompt
    )

    # 3. Validate the created file
    agent_file_path = f".claude/agents/{agent_name}.md"
    validation = validate_agent_definition(agent_file_path)

    if validation.status != 'valid':
        raise AgentRecoveryError(
            f"Failed to recreate {agent_name}: {validation.error}"
        )

    log_event("agent_file_recovered",
              agent_name=agent_name,
              path=agent_file_path)
```

---

## Critic State Recovery

### Recovering Pending Critique State

If `pending_critique` or `active_critics` state is corrupted:

```python
def recover_critic_state_from_events(event_log_path: str, current_state: dict):
    """Reconstruct critic-related state from event log."""

    pending_critique = []
    active_critics = {}
    critique_failures = {}

    with open(event_log_path, 'r') as f:
        for line in f:
            event = json.loads(line.strip())
            event_type = event['event_type']

            if event_type == 'developer_ready_for_review':
                task_id = event['task_id']
                pending_critique.append(task_id)

            elif event_type == 'critic_dispatched':
                task_id = event['task_id']
                critic_id = event['agent_id']
                if task_id in pending_critique:
                    pending_critique.remove(task_id)
                active_critics[critic_id] = task_id

            elif event_type == 'critic_pass':
                task_id = event['task_id']
                critic_id = event.get('agent_id')
                if critic_id in active_critics:
                    del active_critics[critic_id]
                # Task moves to pending_audit (handled by other recovery)

            elif event_type == 'critic_fail':
                task_id = event['task_id']
                critic_id = event.get('agent_id')
                if critic_id in active_critics:
                    del active_critics[critic_id]
                critique_failures[task_id] = critique_failures.get(task_id, 0) + 1

    # Update state
    current_state['pending_critique'] = pending_critique
    current_state['active_critics'] = active_critics
    current_state['critique_failures'] = critique_failures

    return current_state
```

### Missing Critic Agent File

If the Critic agent file is missing:

```python
def recover_critic_agent_file():
    """Recreate critic agent file from creation template."""

    critic_creation_doc = Read(".claude/docs/agent-creation/critic.md")
    creation_prompt = extract_creation_prompt(critic_creation_doc)

    Task(
        model='opus',
        subagent_type='developer',
        prompt=creation_prompt
    )

    # Validate the created file
    critic_file_path = ".claude/agents/critic.md"
    validation = validate_agent_definition(critic_file_path)

    if validation.status != 'valid':
        raise AgentRecoveryError(f"Failed to recreate critic: {validation.error}")

    log_event("critic_agent_recovered", path=critic_file_path)
```

---

## Pre-Existing Failures Baseline

Establish a baseline of what failures exist BEFORE any work begins. This allows distinguishing between:

- **Pre-existing failures**: Issues that existed before the session started
- **Task-introduced failures**: Issues caused by work done in this session

### Baseline Capture at Session Start

```python
def capture_pre_existing_failures_baseline(config: dict) -> dict:
    """Run all verification commands and capture any failures as baseline."""

    baseline = {
        'captured_at': datetime.now().isoformat(),
        'environments': {},
        'summary': {
            'total_failures': 0,
            'by_environment': {},
            'by_check': {}
        }
    }

    for env in config['ENVIRONMENTS']:
        env_name = env['name']
        baseline['environments'][env_name] = {
            'checks': {},
            'failure_count': 0
        }

        for cmd in config['VERIFICATION_COMMANDS']:
            check_name = cmd['check']
            command = cmd['command']
            expected_exit = cmd.get('exit_code', 0)

            # Execute check in environment with timeout to prevent hang
            BASELINE_CHECK_TIMEOUT_SECONDS = 60  # Max time per check
            try:
                result = execute_in_environment(command, env_name,
                                                timeout=BASELINE_CHECK_TIMEOUT_SECONDS)
            except TimeoutError:
                # Treat timeout as failure with special marker
                result = ExecutionResult(
                    exit_code=-1,
                    output=f"TIMEOUT after {BASELINE_CHECK_TIMEOUT_SECONDS}s"
                )
                log_event("baseline_check_timeout",
                          check=check_name,
                          environment=env_name,
                          command=command)

            check_result = {
                'command': command,
                'exit_code': result.exit_code,
                'expected_exit_code': expected_exit,
                'passed': result.exit_code == expected_exit,
                'timed_out': result.exit_code == -1,
                'output_summary': result.output[:500] if not result.exit_code == expected_exit else None
            }

            baseline['environments'][env_name]['checks'][check_name] = check_result

            if not check_result['passed']:
                baseline['environments'][env_name]['failure_count'] += 1
                baseline['summary']['total_failures'] += 1
                baseline['summary']['by_environment'][env_name] =
                    baseline['summary']['by_environment'].get(env_name, 0) + 1
                baseline['summary']['by_check'][check_name] =
                    baseline['summary']['by_check'].get(check_name, 0) + 1

    return baseline
```

### Baseline Storage

Store the baseline in state and in a dedicated file for reference:

```python
def store_pre_existing_baseline(baseline: dict, plan_dir: str):
    """Store baseline for later reference."""

    # Store in state
    state['pre_existing_failures_baseline'] = baseline

    # Also write to file for debugging
    baseline_path = f"{plan_dir}/.pre-existing-baseline.json"
    Write(baseline_path, json.dumps(baseline, indent=2))

    log_event("pre_existing_baseline_captured",
              total_failures=baseline['summary']['total_failures'],
              by_environment=baseline['summary']['by_environment'],
              by_check=baseline['summary']['by_check'])

    save_state()
```

### Pre-Existing Failure Classification

When an auditor reports failures, classify them:

```python
def classify_audit_failures(current_failures: list, baseline: dict, task_id: str) -> dict:
    """Classify failures as pre-existing or task-introduced."""

    classification = {
        'pre_existing': [],
        'task_introduced': [],
        'uncertain': []
    }

    for failure in current_failures:
        check_name = failure['check']
        env_name = failure['environment']

        # Check if this failure existed in baseline
        baseline_check = baseline['environments'].get(env_name, {}).get('checks', {}).get(check_name, {})

        if not baseline_check:
            # Check didn't exist in baseline - uncertain
            classification['uncertain'].append(failure)
        elif not baseline_check['passed']:
            # Failed in baseline too - pre-existing
            failure['baseline_exit_code'] = baseline_check['exit_code']
            classification['pre_existing'].append(failure)
        else:
            # Passed in baseline, fails now - task introduced
            failure['baseline_exit_code'] = baseline_check['exit_code']
            classification['task_introduced'].append(failure)

    log_event("failure_classification",
              task_id=task_id,
              pre_existing=len(classification['pre_existing']),
              task_introduced=len(classification['task_introduced']),
              uncertain=len(classification['uncertain']))

    return classification
```

### Handling Based on Classification

```python
def handle_classified_failures(task_id: str, classification: dict):
    """Route failures based on classification."""

    # Task-introduced failures: Developer must fix
    if classification['task_introduced']:
        return {
            'action': 'REWORK',
            'failures': classification['task_introduced'],
            'message': f"Task introduced {len(classification['task_introduced'])} new failures"
        }

    # Pre-existing failures only: Trigger remediation
    if classification['pre_existing'] and not classification['task_introduced']:
        return {
            'action': 'REMEDIATE_PRE_EXISTING',
            'failures': classification['pre_existing'],
            'message': f"{len(classification['pre_existing'])} pre-existing failures detected - triggering remediation"
        }

    # Mixed: Developer fixes task-introduced, then remediation for pre-existing
    if classification['pre_existing'] and classification['task_introduced']:
        return {
            'action': 'REWORK_THEN_REMEDIATE',
            'task_failures': classification['task_introduced'],
            'pre_existing_failures': classification['pre_existing'],
            'message': f"Fix {len(classification['task_introduced'])} task-introduced failures first, then remediate {len(classification['pre_existing'])} pre-existing"
        }

    return {'action': 'PASS', 'message': 'No failures detected'}
```

### Session Start with Baseline Check

```python
def session_start_with_baseline():
    """Full session start including baseline capture."""

    # 1. Run standard recovery checks
    recovery_issues = session_recovery_check()

    # 2. Check if baseline already exists (session resume)
    if 'pre_existing_failures_baseline' in state:
        baseline = state['pre_existing_failures_baseline']
        log_event("using_existing_baseline",
                  captured_at=baseline['captured_at'],
                  total_failures=baseline['summary']['total_failures'])
    else:
        # 3. Capture fresh baseline
        output("Capturing pre-existing failures baseline...")
        baseline = capture_pre_existing_failures_baseline(CONFIG)
        store_pre_existing_baseline(baseline, PLAN_DIR)

        if baseline['summary']['total_failures'] > 0:
            output(f"WARNING: {baseline['summary']['total_failures']} pre-existing failures detected")
            output(f"  By environment: {baseline['summary']['by_environment']}")
            output(f"  By check: {baseline['summary']['by_check']}")

            # Ask whether to proceed or remediate first
            if baseline['summary']['total_failures'] > 10:
                output("RECOMMEND: Remediate pre-existing failures before starting work")

    return baseline
```

### State Format for Baseline

```json
{
  "pre_existing_failures_baseline": {
    "captured_at": "2025-01-16T10:00:00Z",
    "environments": {
      "native": {
        "checks": {
          "unit_tests": {
            "passed": true,
            "exit_code": 0
          },
          "lint": {
            "passed": false,
            "exit_code": 1,
            "output_summary": "..."
          }
        },
        "failure_count": 1
      },
      "devcontainer": {
        "checks": {
          "unit_tests": {
            "passed": true,
            "exit_code": 0
          },
          "lint": {
            "passed": false,
            "exit_code": 1,
            "output_summary": "..."
          }
        },
        "failure_count": 1
      }
    },
    "summary": {
      "total_failures": 2,
      "by_environment": {
        "native": 1,
        "devcontainer": 1
      },
      "by_check": {
        "lint": 2
      }
    }
  }
}
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

    # 5. Check critic-specific state
    if 'pending_critique' not in state or 'active_critics' not in state:
        recover_critic_state_from_events(EVENT_LOG_FILE, state)
        issues.append("Critic state recovered from event log")

    if issues:
        log_event("session_recovery_completed",
                  issues_resolved=issues)

    return issues
```

---

## Cross-References

- Event logging: [event-logging.md](event-logging.md)
- State management: [state-management.md](state-management.md)
- Session management: [session-management.md](session-management.md)
