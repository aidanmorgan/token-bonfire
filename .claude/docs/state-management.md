# Coordinator State Tracking

Track these fields to coordinate parallel work and resume after interruption:

## State Fields

- **Active developers**: Maps agent ID to task ID
- **Active auditors**: Maps agent ID to task ID
- **Active actor count**: Computed as `len(active_developers) + len(active_auditors)`. Must equal `{{ACTIVE_DEVELOPERS}}` when work is available
- **Active remediation**: Agent ID if infrastructure remediation is in progress, null otherwise
- **Infrastructure blocked**: Boolean indicating assignments are halted for remediation
- **Remediation attempt count**: Integer 0-`{{REMEDIATION_ATTEMPTS}}` tracking current remediation loop iteration
- **Pending audit**: Task IDs awaiting audit after developer completion
- **Completed tasks**: Task IDs that passed audit
- **Blocked tasks**: Maps task ID to blocking task IDs
- **Available tasks**: Unblocked tasks ready for assignment
- **Compaction count**: Integer tracking compactions since session start
- **Plan complete**: Boolean for termination condition
- **Validation complete**: Boolean indicating session-start validation finished
- **Last usage check**: Timestamp of most recent usage script execution
- **Session utilisation**: Integer percentage from last usage check
- **Session remaining**: Integer percentage from last usage check
- **Session resets at**: ISO-8601 timestamp from last usage check
- **Pending divine questions**: Queue of questions awaiting God's response
- **Task quality assessed**: Boolean indicating whether initial task quality assessment has completed
- **Pending expansions**: Task IDs currently being expanded by business analyst agents. Maps task_id to agent_id
- **Active business analysts**: Maps agent ID to task ID being expanded
- **Expanded tasks**: Task specifications that have been expanded. Maps task_id to the expanded specification object
- **Supporting agents**: Registry of plan-derived supporting agents (domain experts, advisors, task executors, quality reviewers, pattern specialists) with capabilities and keyword triggers
- **Active supporting agents**: Maps supporting agent ID to delegating agent ID, task ID, and request details
- **Pending delegation requests**: Queue of delegation requests waiting for agent availability
- **Supporting agent stats**: Maps agent_id to detailed usage metrics

## State Update Triggers

Update coordinator state, persist to `{{STATE_FILE}}`, and append to `{{EVENT_LOG_FILE}}` at these events.

### On developer agent dispatch
1. Add task to `in_progress_tasks` with agent ID, task ID, status "implementing", and empty checkpoint
2. Remove task from `available_tasks`
3. Update `blocked_tasks` to remove this task from any blocking lists
4. Save state to `{{STATE_FILE}}` immediately
5. Log event: `developer_dispatched`

### On remediation agent dispatch
1. Set `infrastructure_blocked` to true
2. Set `active_remediation` to the agent ID
3. Record `infrastructure_issue` with the specific problem
4. Save state to `{{STATE_FILE}}` immediately
5. Log event: `remediation_dispatched`

### On developer signals ready for audit
1. Update task status in `in_progress_tasks` to "awaiting-audit"
2. Add task to `pending_audit` queue
3. Save state to `{{STATE_FILE}}`
4. Log event: `developer_ready_for_audit`

**Note**: The task is NOT complete at this point. Only the auditor can mark a task complete.

### On auditor agent PASS (TASK COMPLETE)
**This is the ONLY point where a task becomes complete.**

1. Remove task from `pending_audit`
2. Remove task from `in_progress_tasks`
3. Add task to `completed_tasks` ← **Task is now officially complete**
4. Recalculate `blocked_tasks` to unblock dependent tasks
5. Recalculate `available_tasks` to include newly unblocked tasks
6. Save state to `{{STATE_FILE}}`
7. Log event: `task_complete` with `task_id`, `agent_id`, `evidence_summary`

### On auditor agent FAIL (task-specific)
1. Update task status in `in_progress_tasks` to "implementing" for rework
2. Remove task from `pending_audit`
3. Increment failure count in `failed_audits`
4. Save state to `{{STATE_FILE}}`
5. Log event: `auditor_fail`

### On auditor agent BLOCKED (pre-existing failures)
1. Set `infrastructure_blocked` to true
2. Record `infrastructure_issue` with the pre-existing failures
3. Save state to `{{STATE_FILE}}`
4. Log event: `auditor_blocked`
5. Log event: `infrastructure_blocked`

### On health auditor HEALTHY
1. Set `infrastructure_blocked` to false
2. Set `active_remediation` to null
3. Set `infrastructure_issue` to null
4. Reset `remediation_attempt_count` to 0
5. Save state to `{{STATE_FILE}}`
6. Log event: `health_audit_pass`
7. Log event: `infrastructure_restored`

### On health auditor UNHEALTHY
1. Increment `remediation_attempt_count`
2. Save state to `{{STATE_FILE}}`
3. Log event: `health_audit_fail`

### On checkpoint request
1. Collect checkpoints from all active developers and update `last_checkpoint`
2. Save state to `{{STATE_FILE}}`
3. Log event: `developer_checkpoint` for each active developer

### On agent seeks divine clarification
1. Parse the "SEEKING DIVINE CLARIFICATION" signal
2. Update agent status to "awaiting-divine-guidance"
3. Add entry to `pending_divine_questions`
4. Save state to `{{STATE_FILE}}`
5. Log event: `agent_seeks_guidance`

### On divine response received
1. Record God's response in the pending question entry
2. Log event: `divine_response_received`
3. Deliver the divine response to the waiting agent
4. Update agent status to "implementing"
5. Remove the answered question from `pending_divine_questions`
6. Save state to `{{STATE_FILE}}`
7. Log event: `agent_resumes_with_guidance`

### On task quality assessment complete
1. Set `task_quality_assessed` to true
2. Update `available_tasks` with only `IMPLEMENTABLE` tasks
3. Update `pending_expansions` with tasks classified as `NEEDS_EXPANSION`
4. Save state to `{{STATE_FILE}}`
5. Log event: `task_quality_assessment`

### On business analyst dispatch
1. Add entry to `active_business_analysts` mapping agent_id to task_id
2. Add task_id to `pending_expansions`
3. Save state to `{{STATE_FILE}}`
4. Log event: `business_analyst_dispatched`

### On business analyst completion (HIGH/MEDIUM confidence)
1. Store expanded specification in `expanded_tasks` under task_id
2. Remove task from `pending_expansions`
3. Remove agent from `active_business_analysts`
4. Add task to `available_tasks`
5. Save state to `{{STATE_FILE}}`
6. Log event: `task_expanded`

### On business analyst completion (LOW confidence)
1. Extract clarification questions from BA output
2. Add entry to `pending_divine_questions`
3. Keep task in `pending_expansions` with status "awaiting-clarification"
4. Remove agent from `active_business_analysts`
5. Save state to `{{STATE_FILE}}`
6. Log event: `expansion_needs_clarification`
7. Invoke divine intervention protocol

### On supporting agent delegation request
1. Check agent availability (MAX_CONCURRENT_PER_AGENT = 2)
2. If available:
   - Add entry to `active_supporting_agents` with delegating agent, task, request details, timestamp
   - Increment `delegations` count in `supporting_agent_stats`
   - Spawn supporting agent using its creation prompt
   - Log event: `supporting_agent_delegated`
3. If busy:
   - Add entry to `pending_delegation_requests`
   - Notify baseline agent of queue position
   - Log event: `delegation_queued`
4. Save state to `{{STATE_FILE}}`

### On supporting agent completion
1. Parse agent output for deliverables (look for `AGENT COMPLETE` signal)
2. Remove entry from `active_supporting_agents`
3. Update `supporting_agent_stats` with completion, duration, and confidence level
4. Check `pending_delegation_requests` for queued work for same agent
5. If queued work exists, dispatch next request
6. Deliver results to delegating baseline agent
7. Save state to `{{STATE_FILE}}`
8. Log event: `supporting_agent_complete`

### On supporting agent error/timeout
1. Remove entry from `active_supporting_agents`
2. Notify delegating baseline agent of failure
3. Log event: `supporting_agent_failed`
4. Save state to `{{STATE_FILE}}`

### On supporting agent out-of-scope signal
1. Parse `OUT_OF_SCOPE` signal for suggested alternative
2. Log event: `supporting_agent_out_of_scope`
3. If alternative agent exists, route to that agent
4. Otherwise, return to delegating agent with guidance
5. Save state to `{{STATE_FILE}}`

## State File Format

```json
{
  "saved_at": "ISO-8601",
  "save_reason": "compaction | session_pause | infrastructure_blocked",
  "tokens_remaining_percent": 9,
  "compaction_count": 3,
  "session_resume_count": 1,
  "plan_file": "{{PLAN_FILE}}",
  "total_tasks": 25,
  "completed_tasks": ["task-1", "task-2"],
  "in_progress_tasks": [
    {
      "task_id": "task-3",
      "developer_id": "dev-agent-1",
      "status": "implementing",
      "last_checkpoint": "unit tests written"
    }
  ],
  "pending_audit": ["task-4"],
  "blocked_tasks": {"task-5": ["task-3", "task-4"]},
  "failed_audits": {"task-6": 2},
  "next_available_tasks": ["task-7", "task-8"],
  "infrastructure_blocked": false,
  "infrastructure_issue": null,
  "active_remediation": null,
  "remediation_attempt_count": 0,
  "last_usage_check": "ISO-8601 timestamp",
  "session_utilisation": 85,
  "session_remaining": 15,
  "session_resets_at": "ISO-8601 timestamp",
  "pending_divine_questions": [],
  "supporting_agents": [
    {
      "agent_id": "db-expert-1",
      "agent_type": "domain_expert",
      "name": "Database Expert",
      "domain": "Database design and optimization",
      "capabilities": ["schema design", "query optimization", "migration scripts"],
      "applicable_tasks": ["task-3", "task-7", "task-12"],
      "keyword_triggers": ["migration", "schema", "index", "query", "database"],
      "request_types": ["task", "advice"],
      "creation_prompt": "...",
      "created_at": "ISO-8601"
    },
    {
      "agent_id": "security-reviewer-1",
      "agent_type": "quality_reviewer",
      "name": "Security Reviewer",
      "domain": "Application security",
      "capabilities": ["auth review", "input validation", "OWASP checks"],
      "applicable_tasks": ["task-2", "task-5", "task-9"],
      "keyword_triggers": ["auth", "password", "token", "input", "sanitize"],
      "request_types": ["review"],
      "creation_prompt": "...",
      "created_at": "ISO-8601"
    }
  ],
  "active_supporting_agents": {
    "supporting-agent-run-1": {
      "agent_id": "db-expert-1",
      "delegating_agent": "dev-agent-2",
      "task_id": "task-7",
      "request_type": "task",
      "request_summary": "Design optimal index strategy for user queries",
      "dispatched_at": "ISO-8601"
    }
  },
  "pending_delegation_requests": [
    {
      "request_id": "req-1",
      "agent_id": "db-expert-1",
      "delegating_agent": "dev-agent-3",
      "task_id": "task-12",
      "request_type": "task",
      "request_summary": "Write migration script for new schema",
      "queued_at": "ISO-8601"
    }
  ],
  "supporting_agent_stats": {
    "db-expert-1": {
      "delegations": 5,
      "completions": 4,
      "failures": 0,
      "out_of_scope": 1,
      "avg_duration_seconds": 120,
      "avg_confidence": "HIGH",
      "tasks_benefited": ["task-3", "task-7"]
    }
  }
}
```

## Atomic State Updates

State mutations must be atomic to survive coordinator crashes:

### Write Procedure

```python
def save_state_atomic(state):
    """Write state atomically to survive crashes."""

    temp_path = f"{STATE_FILE}.tmp"

    # 1. Write to temp file
    with open(temp_path, 'w') as f:
        json.dump(state, f, indent=2)
        f.flush()
        os.fsync(f.fileno())  # Ensure data reaches disk

    # 2. Atomic rename (POSIX guarantees atomicity)
    os.rename(temp_path, STATE_FILE)
```

### Recovery on Resume

```python
def load_state_with_recovery():
    """Load state, recovering from incomplete writes if needed."""

    temp_path = f"{STATE_FILE}.tmp"

    # Check for incomplete write
    if os.path.exists(temp_path):
        log_event("state_recovery_needed", reason="temp_file_exists")
        os.remove(temp_path)  # Discard incomplete write
        # Fall through to load from last good state

    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)

    # No state file - reconstruct from event log if possible
    if os.path.exists(EVENT_LOG_FILE):
        return reconstruct_state_from_events()

    return None  # Fresh start
```

### Event Log as Backup

The append-only event log serves as a backup for state reconstruction:

```python
def reconstruct_state_from_events():
    """Rebuild state by replaying event log."""

    state = create_empty_state()

    with open(EVENT_LOG_FILE) as f:
        for line in f:
            event = json.loads(line)
            apply_event_to_state(state, event)

    log_event("state_reconstructed", events_replayed=count)
    return state
```

## Task Selection Priority

1. Select tasks that unblock the most downstream tasks
2. Among equals, select the task with highest priority in the plan
3. Among equals, select first in document order

---

## Rollback Capability

Track commit SHAs per task to enable rollback if issues are discovered after completion.

### Commit Tracking

When a task passes audit, record the commit:

```python
def record_task_commit(task_id, auditor_result):
    """Record commit SHA associated with completed task."""

    # Get current HEAD after task completion
    commit_sha = get_current_commit_sha()  # git rev-parse HEAD

    task_commits[task_id] = {
        'commit_sha': commit_sha,
        'completed_at': datetime.now().isoformat(),
        'files_modified': auditor_result['files_modified'],
        'branch': get_current_branch()
    }

    log_event("task_commit_recorded",
              task_id=task_id,
              commit_sha=commit_sha)

    save_state()
```

### State Tracking

Add to `{{STATE_FILE}}`:

```json
{
  "task_commits": {
    "task-1": {
      "commit_sha": "abc123",
      "completed_at": "ISO-8601",
      "files_modified": ["src/auth.py", "tests/test_auth.py"],
      "branch": "main"
    },
    "task-2": {
      "commit_sha": "def456",
      "completed_at": "ISO-8601",
      "files_modified": ["src/user.py"],
      "branch": "main"
    }
  }
}
```

### Rollback Procedure

If issues are discovered after task completion:

```python
def rollback_task(task_id):
    """Rollback a completed task's changes."""

    if task_id not in task_commits:
        log_event("rollback_failed", task_id=task_id, reason="no_commit_recorded")
        return False

    task_commit = task_commits[task_id]

    # Check if safe to rollback (no dependent tasks completed after)
    dependent_tasks = get_tasks_blocked_by(task_id)
    completed_dependents = [t for t in dependent_tasks if t in completed_tasks]

    if completed_dependents:
        log_event("rollback_blocked", task_id=task_id,
                  reason="dependent_tasks_completed",
                  dependents=completed_dependents)
        output(f"Cannot rollback {task_id}: dependent tasks completed: {completed_dependents}")
        return False

    # Perform rollback
    parent_sha = get_parent_commit(task_commit['commit_sha'])
    revert_to_commit(parent_sha)

    # Update state
    completed_tasks.remove(task_id)
    available_tasks.append(task_id)
    del task_commits[task_id]

    log_event("task_rolled_back",
              task_id=task_id,
              from_sha=task_commit['commit_sha'],
              to_sha=parent_sha)

    save_state()
    return True
```

### Rollback Signal

If coordinator needs to rollback (e.g., discovered breaking change):

```
ROLLBACK REQUIRED: [task ID]

Reason: [why rollback is needed]
Commit: [sha to revert]
Files Affected: [list]

Proceeding with rollback...
```

### Post-Rollback Actions

After successful rollback:

1. Task returns to `available_tasks`
2. Any dependent tasks that were in-progress are aborted
3. Plan re-evaluation triggered
4. Event logged for audit trail

```python
def handle_post_rollback(task_id):
    """Clean up after rollback."""

    # Abort dependent tasks
    for task in in_progress_tasks:
        if task_id in get_task_dependencies(task['task_id']):
            abort_task(task['task_id'], reason="dependency_rolled_back")
            available_tasks.append(task['task_id'])

    # Re-evaluate plan
    recalculate_available_tasks()

    output(f"Rollback complete. {task_id} returned to available queue.")
```

---

## Learning from Failures

Track failure patterns to improve future development cycles.

### Failure Pattern Storage

```json
{
  "failure_patterns": {
    "type_errors": {
      "count": 5,
      "tasks": ["task-3", "task-7"],
      "common_causes": ["Missing type annotation", "Wrong return type"],
      "suggested_prevention": "Run pyright before signaling completion"
    },
    "test_failures": {
      "count": 12,
      "tasks": ["task-2", "task-5", "task-8"],
      "common_causes": ["Missing fixture", "Assertion wrong"],
      "suggested_prevention": "Review test output carefully"
    },
    "environment_disagreement": {
      "count": 3,
      "tasks": ["task-4"],
      "common_causes": ["Path separator", "Case sensitivity"],
      "suggested_prevention": "Test in all environments before completion"
    }
  }
}
```

### Recording Failures

```python
def record_failure_pattern(task_id, failure_type, details):
    """Record failure for pattern analysis."""

    if failure_type not in failure_patterns:
        failure_patterns[failure_type] = {
            'count': 0,
            'tasks': [],
            'common_causes': [],
            'suggested_prevention': None
        }

    pattern = failure_patterns[failure_type]
    pattern['count'] += 1
    pattern['tasks'].append(task_id)

    # Extract cause if identifiable
    cause = identify_failure_cause(details)
    if cause and cause not in pattern['common_causes']:
        pattern['common_causes'].append(cause)

    save_state()

    # Log for analysis
    log_event("failure_pattern_recorded",
              failure_type=failure_type,
              task_id=task_id,
              total_occurrences=pattern['count'])
```

### Using Failure Patterns

Include relevant patterns in developer prompts:

```python
def get_relevant_failure_warnings(task):
    """Get warnings based on past failures for similar work."""

    warnings = []

    # Check if task keywords match past failure patterns
    task_keywords = extract_task_keywords(task)

    for pattern_type, pattern in failure_patterns.items():
        if pattern['count'] >= 3:  # Only warn on recurring issues
            # Check if pattern is relevant to this task
            if is_pattern_relevant(pattern, task_keywords):
                warnings.append({
                    'type': pattern_type,
                    'message': f"Previous tasks had {pattern_type} issues",
                    'prevention': pattern.get('suggested_prevention'),
                    'occurrence_count': pattern['count']
                })

    return warnings
```

### Developer Prompt Enhancement

When dispatching developers, include failure warnings:

```markdown
{{#if failure_warnings}}
COMMON ISSUES TO AVOID:
Based on patterns from previous tasks, watch out for:

{{#each failure_warnings}}
- **{{this.type}}** (occurred {{this.occurrence_count}} times)
  Prevention: {{this.prevention}}
{{/each}}

Taking care to avoid these issues will reduce audit failures.
{{/if}}
```

### Pattern Analysis Events

| Event | Trigger | Data |
|-------|---------|------|
| `failure_pattern_recorded` | Audit failure categorized | failure_type, task_id, count |
| `failure_pattern_prevention_added` | Prevention suggestion added | failure_type, prevention |
| `failure_warning_issued` | Warning included in prompt | task_id, warnings |

---

## Parallel Agent Tracking

The coordinator manages multiple concurrent agents. Track each agent's lifecycle:

### Agent Tracking Structure

```json
{
  "active_agents": {
    "agent-uuid-1": {
      "type": "developer",
      "task_id": "1-1-1",
      "dispatched_at": "2025-01-16T10:00:00Z",
      "timeout_at": "2025-01-16T10:15:00Z",
      "last_checkpoint": null,
      "checkpoint_count": 0
    },
    "agent-uuid-2": {
      "type": "auditor",
      "task_id": "1-1-2",
      "dispatched_at": "2025-01-16T10:02:00Z",
      "timeout_at": "2025-01-16T10:17:00Z",
      "last_checkpoint": null,
      "checkpoint_count": 0
    },
    "agent-uuid-3": {
      "type": "business_analyst",
      "task_id": "1-2-1",
      "dispatched_at": "2025-01-16T10:03:00Z",
      "timeout_at": "2025-01-16T10:18:00Z",
      "last_checkpoint": null,
      "checkpoint_count": 0
    }
  }
}
```

### Timeout Monitoring

```python
def check_agent_timeouts():
    """Check for timed-out agents on each loop iteration."""

    now = datetime.now()
    timed_out = []

    for agent_id, agent in active_agents.items():
        timeout_at = datetime.fromisoformat(agent['timeout_at'])
        if now > timeout_at:
            timed_out.append(agent_id)

    for agent_id in timed_out:
        handle_agent_timeout(agent_id)

    return timed_out
```

### Slot Management

```python
def count_active_actors():
    """Count current developer + auditor agents."""
    return sum(1 for a in active_agents.values()
               if a['type'] in ('developer', 'auditor'))

def get_empty_slots():
    """Calculate how many more actors can be dispatched."""
    return ACTIVE_DEVELOPERS - count_active_actors()

def fill_actor_slots():
    """Fill all empty actor slots with available work."""
    while get_empty_slots() > 0 and available_tasks:
        if infrastructure_blocked:
            break
        if pending_divine_questions:
            break

        task = select_next_task()
        dispatch_developer(task)
```

### Agent Lifecycle Events

| Event | When | State Change |
|-------|------|--------------|
| `agent_dispatched` | Task tool called | Add to `active_agents` |
| `agent_checkpoint` | Checkpoint received | Update `last_checkpoint` |
| `agent_timeout` | Timeout exceeded | Remove, re-dispatch if under limit |
| `agent_complete` | Signal received | Remove, route based on signal |
| `agent_crashed` | Task tool error | Remove, re-dispatch if under limit |
