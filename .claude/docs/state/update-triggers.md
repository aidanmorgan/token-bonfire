# State Update Triggers

[← Back to State Management](index.md)

Update state, persist to `{{STATE_FILE}}`, and append to `{{EVENT_LOG_FILE}}` at these events.

---

## Developer Dispatch

1. Add task to `in_progress_tasks` with agent ID, status "implementing"
2. Remove task from `available_tasks`
3. Update `blocked_tasks` to remove this task
4. Save state immediately
5. Log event: `developer_dispatched`

## Developer Ready for Review

1. Update task status to "awaiting-review"
2. Add task to `pending_critique` queue
3. Save state
4. Log event: `developer_ready_for_review`

## Developer TASK_INCOMPLETE

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

## Critic Review Complete

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

## Critic Timeout

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

## Auditor PASS (Task Complete)

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

## Auditor FAIL

1. Update task status to "implementing" for rework
2. Remove task from `pending_audit`
3. Increment failure count in `audit_failures`
4. Update attempt tracking: increment `audit_failures`
5. Check escalation threshold (3 failures = halt)
6. Save state
7. Log event: `auditor_fail`

## Auditor BLOCKED

1. Set `infrastructure_blocked` to true
2. Record `infrastructure_issue` with failure details
3. Compare against baseline (pre-existing vs task-introduced)
4. Record blocked task state for resume
5. Save state
6. Log events: `auditor_blocked`, `infrastructure_blocked`

## Remediation/Health Audit

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
2. If `remediation_attempt_count` > `REMEDIATION_ATTEMPTS`:
    - Log event: `remediation_exhausted`
    - Signal `SEEKING_DIVINE_CLARIFICATION` with infrastructure details
    - Add to `pending_divine_questions`
3. Else:
    - Dispatch Remediation agent with updated context
    - Log event: `remediation_dispatched`
4. Save state
5. Log event: `health_audit_fail`

## Divine Intervention

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

## Expert Delegation

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

## Related Documentation

- [State Fields](fields.md) - All state field definitions
- [Attempt Tracking](attempt-tracking.md) - Attempt tracking and escalation
- [Persistence](persistence.md) - Atomic updates and recovery
- [Event Schema](../orchestrator/event-schema.md) - Event log format
