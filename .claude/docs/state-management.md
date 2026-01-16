# Coordinator State Tracking

Track these fields to coordinate parallel work and resume after interruption.

See [State Schema](orchestrator/state-schema.md) for complete state file format.
See [Event Schema](orchestrator/event-schema.md) for event log format.

---

## State Fields

### Session Tracking

| Field                  | Type     | Description                                    |
|------------------------|----------|------------------------------------------------|
| `session_id`           | UUID     | Generated at start, used for event correlation |
| `session_started_at`   | ISO-8601 | When this session began                        |
| `previous_session_id`  | UUID     | Previous session ID if resuming                |
| `session_resume_count` | Integer  | How many times coordinator has resumed         |
| `compaction_count`     | Integer  | Compactions since session start                |

### Task Tracking

| Field               | Type     | Description                                        |
|---------------------|----------|----------------------------------------------------|
| `in_progress_tasks` | object[] | Tasks currently being worked (see state-schema.md) |
| `active_developers` | object   | Maps agent ID → {task_id, dispatched_at}           |
| `active_auditors`   | object   | Maps agent ID → {task_id, dispatched_at}           |
| `active_critics`    | object   | Maps agent ID → {task_id, dispatched_at}           |
| `pending_audit`     | string[] | Task IDs awaiting auditor verification             |
| `pending_critique`  | string[] | Task IDs awaiting critic review                    |
| `completed_tasks`   | string[] | Task IDs that passed audit                         |
| `blocked_tasks`     | object   | Maps task ID → array of blocking task IDs          |
| `available_tasks`   | string[] | Unblocked tasks ready for assignment               |
| `audit_failures`    | object   | Maps task ID → failure count                       |
| `critique_failures` | object   | Maps task ID → critic failure count                |
| `critic_timeouts`   | object   | Maps task ID → timeout count                       |

### Infrastructure Tracking

| Field                       | Type    | Description                              |
|-----------------------------|---------|------------------------------------------|
| `infrastructure_blocked`    | Boolean | Assignments halted for remediation       |
| `infrastructure_issue`      | Object  | Details of blocking issue                |
| `active_remediation`        | String  | Agent ID if remediation in progress      |
| `remediation_attempt_count` | Integer | Current remediation loop iteration (0-3) |

### Expert Tracking

| Field                         | Type  | Description                                            |
|-------------------------------|-------|--------------------------------------------------------|
| `experts`                     | Array | Registry of plan-derived experts (see structure below) |
| `active_experts`              | Map   | Expert ID → delegation details                         |
| `paused_agents`               | Map   | Agent ID → pause state for delegation waits            |
| `pending_delegation_requests` | Array | Queue of delegation requests waiting                   |
| `expert_stats`                | Map   | Agent ID → usage metrics                               |

**Expert Object Structure** (required fields for each expert in `experts` array):

```json
{
  "name": "crypto-expert",
  "domain": "Cryptography",
  "file": ".claude/agents/experts/crypto-expert.md",
  "tasks": ["task-2-1", "task-2-3"],
  "requesting_agents": ["developer", "auditor"],
  "capabilities": [
    "Verify cryptographic algorithm correctness",
    "Review key management practices",
    "Assess secure random number generation"
  ],
  "delegation_triggers": {
    "developer": "When implementing encryption, hashing, or key derivation",
    "auditor": "When verifying cryptographic implementations"
  },
  "created_at": "2025-01-16T10:00:00Z"
}
```

### File Conflict Tracking

| Field                      | Type  | Description                                        |
|----------------------------|-------|----------------------------------------------------|
| `queued_for_file_conflict` | Array | Tasks queued waiting for file availability         |
| `queue_retry_tracker`      | Map   | Task ID → retry count (persisted across sessions)  |
| `queue_timeout_context`    | Map   | Task ID → coordination context for timed-out tasks |

### Divine Intervention

| Field                      | Type    | Description                          |
|----------------------------|---------|--------------------------------------|
| `pending_divine_questions` | Array   | Questions awaiting human response    |
| `task_quality_assessed`    | Boolean | Whether initial assessment completed |
| `pending_expansions`       | Map     | Task ID → agent ID being expanded    |

---

## Attempt Tracking

Track attempts across agent crashes and session restarts to enforce escalation paths.

### Attempt Tracking Structure

```json
{
  "task_attempts": {
    "task-3-1-1": {
      "self_solve_attempts": 2,
      "delegation_attempts": 1,
      "audit_failures": 1,
      "critic_failures": 0,
      "critic_timeouts": 0,
      "incomplete_count": 0,
      "signal_rejections": 1,
      "last_attempt_at": "2025-01-16T10:30:00Z",
      "escalation_level": "delegation",
      "last_blocker": null,
      "history": [...]
    }
  }
}
```

### Escalation Thresholds

| Attempt Type          | Threshold | Escalation Action                      |
|-----------------------|-----------|----------------------------------------|
| `self_solve_attempts` | 3         | Escalate to delegation                 |
| `delegation_attempts` | 3         | Escalate to divine intervention        |
| `audit_failures`      | 3         | Halt task, require human review        |
| `critic_failures`     | 3         | Halt task, require human review        |
| `critic_timeouts`     | 3         | Re-dispatch critic with same task      |
| `incomplete_count`    | 3         | Escalate to divine intervention        |
| `signal_rejections`   | 5         | Notify coordinator of persistent issue |

---

## State Update Triggers

Update state, persist to `{{STATE_FILE}}`, and append to `{{EVENT_LOG_FILE}}` at these events.

### Developer Dispatch

1. Add task to `in_progress_tasks` with agent ID, status "implementing"
2. Remove task from `available_tasks`
3. Update `blocked_tasks` to remove this task
4. Save state immediately
5. Log event: `developer_dispatched`

### Developer Ready for Review

1. Update task status to "awaiting-review"
2. Add task to `pending_critique` queue
3. Save state
4. Log event: `developer_ready_for_review`

### Developer TASK_INCOMPLETE

When developer signals TASK_INCOMPLETE (blocked, missing info, etc.):

1. Parse blocker details from signal (blocker, attempted, needed)
2. Increment `incomplete_count` for this task in attempt tracking
3. Update task status to "blocked"
4. Route based on blocker category (see below)
5. Save state
6. Fill actor slots with other available tasks

**Blocker Categories and Handlers**:

| Category                | Action                       | Escalation              |
|-------------------------|------------------------------|-------------------------|
| `missing_info`          | Escalate immediately         | Divine clarification    |
| `blocked_by_dependency` | Add to `blocked_tasks`, wait | After 3 attempts        |
| `infrastructure`        | Enter remediation loop       | After remediation limit |
| `out_of_scope`          | Escalate immediately         | Divine clarification    |

**Handler: `blocked_by_dependency`**

```python
def handle_blocked_by_dependency(task_id, blocker_task_id, incomplete_count):
    """Handle task blocked by another task's completion."""

    if blocker_task_id in completed_tasks:
        # Dependency already complete - retry immediately
        log_event("developer_incomplete",
                  task_id=task_id,
                  blocker="blocked_by_dependency",
                  blocker_task=blocker_task_id,
                  note="Dependency was already complete, retrying")
        available_tasks.append(task_id)
        return

    if incomplete_count >= 3:
        # Same dependency blocked 3 times - escalate
        log_event("developer_incomplete",
                  task_id=task_id,
                  blocker="blocked_by_dependency",
                  blocker_task=blocker_task_id,
                  escalate=True)
        escalate_to_divine(
            task_id=task_id,
            question=f"Task {task_id} blocked by {blocker_task_id} after 3 attempts",
            options=["Wait longer", "Re-prioritize blocker", "Restructure tasks"]
        )
        return

    # Add to blocked_tasks - will auto-unblock when dependency completes
    if task_id not in blocked_tasks:
        blocked_tasks[task_id] = []
    if blocker_task_id not in blocked_tasks[task_id]:
        blocked_tasks[task_id].append(blocker_task_id)

    # Remove from available (if present) and in_progress
    if task_id in available_tasks:
        available_tasks.remove(task_id)
    remove_from_in_progress(task_id)

    log_event("developer_incomplete",
              task_id=task_id,
              blocker="blocked_by_dependency",
              blocker_task=blocker_task_id,
              action="added_to_blocked_tasks")
```

**Handler: `missing_info` / `out_of_scope`**

```python
def handle_missing_info_or_out_of_scope(task_id, blocker_category, details):
    """Handle tasks that need divine guidance immediately."""

    log_event("developer_incomplete",
              task_id=task_id,
              blocker=blocker_category,
              details=details,
              escalate=True)

    escalate_to_divine(
        task_id=task_id,
        question=f"Task {task_id}: {blocker_category}",
        context=details,
        options=["Provide clarification", "Restructure task", "Remove from plan"]
    )
```

**Handler: `infrastructure`**

```python
def handle_infrastructure_blocker(task_id, issue_details):
    """Handle infrastructure blockers by entering remediation."""

    log_event("developer_incomplete",
              task_id=task_id,
              blocker="infrastructure",
              issue=issue_details)

    # Enter remediation loop (same as INFRA_BLOCKED signal)
    handle_infrastructure_block(issue_details, reporter_id=task_id)
```

### Critic Review Complete

**REVIEW_PASSED:**

1. Remove task from `pending_critique`
2. Update task status to "awaiting-audit"
3. Add task to `pending_audit` queue
4. Save state
5. Log event: `critic_pass`

**REVIEW_FAILED:**

1. Remove task from `pending_critique`
2. Update task status to "implementing" for rework
3. Increment failure count in `critique_failures`
4. Save state
5. Log event: `critic_fail`

### Critic Timeout

When a Critic agent times out (no response within timeout period):

1. Increment `critic_timeouts` for this task
2. If `critic_timeouts` < 3:
    - Log event: `critic_timeout` with attempt number
    - Re-dispatch fresh Critic with same task context
    - Task remains in `pending_critique`
3. If `critic_timeouts` >= 3:
    - Log event: `critic_timeout` with `escalate: true`
    - **Skip Critic and proceed to Auditor** (task was already implemented, only review timed out)
    - **Remove task from `pending_critique`** (explicit removal FIRST)
    - Add task to `pending_audit`
    - Update task status to `awaiting-audit`
    - Log event: `critic_bypassed` with reason `timeout_limit_exceeded`
    - Dispatch Auditor immediately

   ```python
   # Explicit state transition
   if task_id in pending_critique:
       pending_critique.remove(task_id)
   pending_audit.append(task_id)
   update_task_status(task_id, "awaiting-audit")
   ```

   **Note**: Do NOT move back to developer - the implementation is complete, only critic review failed. Auditor will
   verify if implementation meets acceptance criteria regardless of code quality review.
4. Save state

**Rationale**: Critic timeouts are typically transient (context exhaustion, network issues). Retry with a fresh agent
before penalizing the developer's work.

**Quality Gate Tradeoff**: When critic is bypassed after 3 timeouts, the code quality review is skipped but the Auditor
still verifies acceptance criteria. This is an intentional tradeoff:

- **Pros**: Progress is not blocked indefinitely by transient issues
- **Cons**: Code quality issues that don't affect functionality may ship
- **Mitigation**: Auditor failure will catch functional issues; quality issues can be addressed in subsequent
  refactoring tasks
- **Alternative**: If stricter quality control is required, change this to escalate to divine intervention instead of
  bypassing

### Auditor PASS (Task Complete)

**This is the ONLY point where a task becomes complete.**

1. Remove task from `pending_audit`
2. Remove task from `in_progress_tasks`
3. Add task to `completed_tasks` ← **Task officially complete**
4. Unblock dependent tasks (see below)
5. Save state
6. Log event: `task_complete`

**Step 4: Unblock Dependents**

```python
def unblock_dependents(completed_task_id):
    """Unblock tasks that were waiting for this task to complete."""

    newly_available = []

    for blocked_task_id, blockers in list(blocked_tasks.items()):
        if completed_task_id in blockers:
            blockers.remove(completed_task_id)

            if not blockers:
                # All blockers cleared - task is now available
                del blocked_tasks[blocked_task_id]
                available_tasks.append(blocked_task_id)
                newly_available.append(blocked_task_id)

                log_event("task_unblocked",
                          task_id=blocked_task_id,
                          unblocked_by=completed_task_id)

    return newly_available
```

**IMPORTANT**: This handles both:

- Static `blocked_by` dependencies from the plan
- Dynamic blockers added via TASK_INCOMPLETE `blocked_by_dependency`

### Auditor FAIL

1. Update task status to "implementing" for rework
2. Remove task from `pending_audit`
3. Increment failure count in `audit_failures`
4. Update attempt tracking: increment `audit_failures`
5. Check escalation threshold (3 failures = halt)
6. Save state
7. Log event: `auditor_fail`

### Auditor BLOCKED

1. Set `infrastructure_blocked` to true
2. Record `infrastructure_issue` with failure details
3. Compare against baseline (pre-existing vs task-introduced)
4. Record blocked task state for resume
5. Save state
6. Log events: `auditor_blocked`, `infrastructure_blocked`

### Remediation/Health Audit

**Constants:**

```python
REMEDIATION_ATTEMPTS_LIMIT = 3  # Max remediation cycles before escalation
```

**Handler: DISPATCH_HEALTH_AUDITOR** (on REMEDIATION_COMPLETE signal)

1. Dispatch Health Auditor agent
2. Log event: `health_audit_dispatched`

**Handler: EXIT_REMEDIATION** (on HEALTH_AUDIT: HEALTHY signal)

1. Set `infrastructure_blocked` to false
2. Clear `active_remediation` and `infrastructure_issue`
3. Reset `remediation_attempt_count` to 0
4. Resume any blocked tasks
5. Save state
6. Log events: `health_audit_pass`, `infrastructure_restored`

**Handler: RETRY_REMEDIATION** (on HEALTH_AUDIT: UNHEALTHY signal)

1. Increment `remediation_attempt_count`
2. If `remediation_attempt_count` >= `REMEDIATION_ATTEMPTS_LIMIT`:
    - Log event: `remediation_exhausted`
    - Signal `SEEKING_DIVINE_CLARIFICATION` with infrastructure details
    - Add to `pending_divine_questions`
3. Else:
    - Dispatch Remediation agent with updated context
    - Log event: `remediation_dispatched`
4. Save state
5. Log event: `health_audit_fail`

### Divine Intervention

**Handler: AWAIT_DIVINE_RESPONSE** (on SEEKING_DIVINE_CLARIFICATION signal)

1. Parse question details from agent output
2. Update agent status to "awaiting-divine-guidance" in `in_progress_tasks`
3. Add question to `pending_divine_questions`:
   ```python
   pending_divine_questions.append({
       'agent_id': agent_id,
       'task_id': task_id,
       'question': parsed_question,
       'options': parsed_options,
       'context': parsed_context,
       'timestamp': datetime.now().isoformat(),
       'response': None
   })
   ```
4. Save state
5. Log event: `agent_seeks_guidance`
6. Invoke `AskUserQuestion` tool with question and options
7. Block task progress until response received

**Divine response received:**

1. Record response in pending question entry
2. Format response for agent consumption
3. Resume agent with divine guidance prompt
4. Update agent status to "implementing"
5. Remove from `pending_divine_questions`
6. Save state
7. Log event: `divine_response_received`

### Expert Delegation

**Request accepted:**

1. Add to `active_experts`
2. Increment `delegations` count in `expert_stats`
3. Spawn expert
4. Log event: `expert_delegated`

**Request queued (agent busy):**

1. Add to `pending_delegation_requests`
2. Notify baseline agent of position
3. Log event: `delegation_queued`

**Expert complete:**

1. Parse output for deliverables
2. Remove from `active_experts`
3. Update `expert_stats`
4. **Process delegation queue** (see below)
5. Deliver results to delegating agent
6. Save state
7. Log event: `expert_complete`

```python
def process_delegation_queue(completed_expert_id):
    """Check queue and dispatch next pending request for this expert type."""

    completed_expert_type = expert_stats[completed_expert_id]['type']

    # Find next queued request for this expert type
    for i, request in enumerate(pending_delegation_requests):
        if request['target_expert'] == completed_expert_type:
            # Found a waiting request - dispatch it
            pending_delegation_requests.pop(i)

            # Dispatch the expert
            active_experts[generate_expert_id()] = {
                'type': completed_expert_type,
                'requesting_agent': request['requesting_agent'],
                'task_id': request['task_id'],
                'dispatched_at': datetime.now().isoformat()
            }

            log_event("delegation_dequeued",
                      expert_type=completed_expert_type,
                      requesting_agent=request['requesting_agent'],
                      waited_since=request['queued_at'])

            # Dispatch the expert agent
            dispatch_expert(completed_expert_type, request)
            break  # Only dispatch one at a time
```

---

## Atomic State Updates

State mutations must be atomic to survive coordinator crashes.

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

## Task Selection Priority

1. Select tasks that unblock the most downstream tasks
2. Among equals, select task with highest priority in plan
3. Among equals, select first in document order

---

## Rollback Capability

Track commit SHAs per task to enable rollback if issues are discovered after completion.

### Commit Tracking

```json
{
  "task_commits": {
    "task-1": {
      "commit_sha": "abc123",
      "completed_at": "ISO-8601",
      "files_modified": [
        "src/auth.py",
        "tests/test_auth.py"
      ],
      "branch": "main"
    }
  }
}
```

### Rollback Rules

1. Cannot rollback if dependent tasks have completed
2. Task returns to `available_tasks` after rollback
3. In-progress dependent tasks are aborted
4. Plan re-evaluation triggered

---

## Learning from Failures

Track failure patterns to improve future development cycles.

### Failure Pattern Storage

```json
{
  "failure_patterns": {
    "type_errors": {
      "count": 5,
      "tasks": [
        "task-3",
        "task-7"
      ],
      "common_causes": [
        "Missing type annotation"
      ],
      "suggested_prevention": "Run pyright before signaling completion"
    }
  }
}
```

### Using Failure Patterns

Include relevant patterns in developer prompts when dispatching similar tasks.

---

## Parallel Agent Tracking

### Agent Tracking Structure

```json
{
  "active_agents": {
    "agent-uuid-1": {
      "type": "developer",
      "task_id": "1-1-1",
      "dispatched_at": "2025-01-16T10:00:00Z",
      "timeout_at": "2025-01-16T10:15:00Z",
      "last_checkpoint": null
    }
  }
}
```

### Slot Management

```python
def fill_actor_slots():
    while get_empty_slots() > 0 and available_tasks:
        if infrastructure_blocked:
            break
        if pending_divine_questions:
            break

        task = select_next_task()
        dispatch_developer(task)
```

### Agent Lifecycle Events

| Event              | When                | State Change                       |
|--------------------|---------------------|------------------------------------|
| `agent_dispatched` | Task tool called    | Add to `active_agents`             |
| `agent_checkpoint` | Checkpoint received | Update `last_checkpoint`           |
| `agent_timeout`    | Timeout exceeded    | Remove, re-dispatch if under limit |
| `agent_complete`   | Signal received     | Remove, route based on signal      |
| `agent_crashed`    | Task tool error     | Remove, re-dispatch if under limit |

---

## Related Documentation

- [State Schema](orchestrator/state-schema.md) - Complete state file format
- [Event Schema](orchestrator/event-schema.md) - Event log format
- [Recovery Procedures](recovery-procedures.md) - Error recovery
- [Session Management](session-management.md) - Pause/resume protocols
- [Task Delivery Loop](task-delivery-loop.md) - Main execution loop
