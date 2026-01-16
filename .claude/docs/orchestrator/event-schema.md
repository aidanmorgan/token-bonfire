# Event Schema

All events are appended to `{{EVENT_LOG_FILE}}` as JSONL. Never overwrite the file.

## Event Structure

```json
{
  "timestamp": "ISO-8601",
  "sequence": 1,
  "session_id": "UUID",
  "event_type": "event_name",
  "agent_id": "string or null",
  "task_id": "string or null",
  "details": {}
}
```

**Note**: The `event_type` field is the canonical name for event types (not `event`).

## Event Types

### Session Lifecycle

| Event                          | Trigger                        | Fields                                                                    |
|--------------------------------|--------------------------------|---------------------------------------------------------------------------|
| `session_start`                | New session begins             | `plan_file`, `total_tasks`                                                |
| `session_resumed`              | Coordinator resumes from state | `previous_session_id`, `in_progress_tasks_count`, `completed_tasks_count` |
| `session_pause`                | Budget exhausted or user stop  | `reason`, `remaining_percent`, `resets_at`                                |
| `task_restarted_on_resume`     | Task moved back to available   | `previous_status`, `reason`                                               |
| `task_reverification_required` | Completed task needs re-audit  | `completed_at`, `time_since_completion_minutes`                           |
| `compaction_start`             | Context compaction begins      | `compaction_number`, `context_remaining`                                  |
| `compaction_complete`          | Context compaction finished    | `compaction_number`, `full_reload`                                        |
| `workflow_complete`            | All tasks done                 | `total_tasks`, `compactions`, `session_resumes`                           |
| `workflow_failed`              | Unrecoverable error            | `reason`, `last_state`                                                    |

### Task Quality Assessment

| Event                           | Trigger                  | Fields                                                                      |
|---------------------------------|--------------------------|-----------------------------------------------------------------------------|
| `task_quality_assessment`       | Plan tasks assessed      | `implementable_count`, `needs_expansion_count`, `needs_clarification_count` |
| `business_analyst_dispatched`   | BA agent spawned         | `task_id`, `agent_id`, `missing_criteria`                                   |
| `task_expanded`                 | BA completed expansion   | `task_id`, `confidence`, `expansion_summary`                                |
| `expansion_needs_clarification` | BA needs divine guidance | `task_id`, `questions`, `options`                                           |

### Developer Lifecycle

| Event                        | Trigger                            | Fields                                         |
|------------------------------|------------------------------------|------------------------------------------------|
| `developer_dispatched`       | Developer agent spawned            | `task_id`, `agent_id`, `blocked_by`            |
| `developer_checkpoint`       | Progress checkpoint collected      | `task_id`, `agent_id`, `status`, `checkpoint`  |
| `developer_ready_for_review` | Developer signals READY_FOR_REVIEW | `task_id`, `agent_id`, `files_modified`        |
| `developer_incomplete`       | Developer signals TASK_INCOMPLETE  | `task_id`, `agent_id`, `blocker`, `attempted`  |
| `developer_blocked`          | Developer reports infra issue      | `task_id`, `agent_id`, `issue_type`            |
| `signal_rejected`            | Signal rejected (incomplete)       | `task_id`, `agent_id`, `signal_type`, `reason` |

### Environment Verification

| Event                             | Trigger                   | Fields                                     |
|-----------------------------------|---------------------------|--------------------------------------------|
| `environment_verification_passed` | All environments verified | `task_id`, `environments_tested`           |
| `environment_verification_failed` | Environment(s) failed     | `task_id`, `failed_environments`, `errors` |

### Critic Lifecycle

| Event               | Trigger                   | Fields                                      |
|---------------------|---------------------------|---------------------------------------------|
| `critic_dispatched` | Critic agent spawned      | `task_id`, `agent_id`                       |
| `critic_pass`       | Code quality approved     | `task_id`, `agent_id`, `quality_assessment` |
| `critic_fail`       | Code quality issues found | `task_id`, `agent_id`, `issues`, `failures` |
| `critic_timeout`    | Critic agent timed out    | `task_id`, `agent_id`                       |

### Audit Lifecycle

| Event                | Trigger                            | Fields                                     |
|----------------------|------------------------------------|--------------------------------------------|
| `auditor_dispatched` | Auditor agent spawned              | `task_id`, `agent_id`                      |
| `task_complete`      | **Auditor confirms task complete** | `task_id`, `agent_id`, `evidence_summary`  |
| `auditor_fail`       | Task failed verification           | `task_id`, `agent_id`, `failures`          |
| `auditor_blocked`    | Pre-existing failures found        | `task_id`, `agent_id`, `blocking_failures` |

**Note**: `task_complete` is the ONLY event that marks a task as complete. There is no separate `auditor_pass` event.

### Expert Lifecycle

| Event                          | Trigger                      | Fields                                              |
|--------------------------------|------------------------------|-----------------------------------------------------|
| `expert_created`               | Plan-derived expert created  | `agent_id`, `name`, `domain`, `definition_hash`     |
| `expert_request_received`      | EXPERT_REQUEST intercepted   | `from_agent_id`, `task_id`, `expert_name`           |
| `expert_delegated`             | Expert spawned               | `run_id`, `agent_id`, `from_agent_id`, `task_id`    |
| `delegation_queued`            | Request queued (agent busy)  | `request_id`, `agent_id`, `queue_position`          |
| `expert_complete`              | Expert returns result        | `run_id`, `agent_id`, `task_id`, `duration_seconds` |
| `expert_failed`                | Expert errored or timed out  | `run_id`, `agent_id`, `error_reason`                |
| `expert_out_of_scope`          | Request outside expert scope | `run_id`, `agent_id`, `suggested_alternative`       |
| `delegation_results_delivered` | Results delivered to agent   | `agent_id`, `from_agent_id`, `task_id`              |

### Infrastructure

| Event                     | Trigger                            | Fields                                               |
|---------------------------|------------------------------------|------------------------------------------------------|
| `health_audit_dispatched` | Health auditor spawned             | `agent_id`, `attempt_number`                         |
| `health_audit_pass`       | Codebase verified healthy          | `agent_id`                                           |
| `health_audit_fail`       | Codebase still unhealthy           | `agent_id`, `failures`                               |
| `health_audit_unexpected` | Health auditor unexpected response | `agent_id`, `attempt_number`, `response_summary`     |
| `remediation_exhausted`   | Remediation attempts exceeded      | `attempt_count`, `issue_type`, `escalation_required` |
| `infrastructure_blocked`  | Assignments halted                 | `issue`, `blocking_failures`                         |
| `infrastructure_restored` | Assignments resumed                | `attempts_used`, `fixes_applied`                     |
| `remediation_dispatched`  | Remediation agent spawned          | `agent_id`, `issue`, `attempt_count`                 |
| `remediation_complete`    | Remediation finished               | `agent_id`, `fixes_applied`, `summary`               |
| `remediation_failed`      | Remediation agent failed           | `agent_id`, `reason`, `attempt_number`               |
| `usage_check`             | Usage script executed              | `utilisation`, `remaining`, `resets_at`              |

### Divine Intervention

| Event                         | Trigger                   | Fields                                        |
|-------------------------------|---------------------------|-----------------------------------------------|
| `agent_seeks_guidance`        | Agent needs clarification | `agent_id`, `task_id`, `question`, `options`  |
| `coordinator_prays`           | Coordinator asks user     | `agent_id`, `task_id`, `question`             |
| `divine_response_received`    | User provides guidance    | `agent_id`, `task_id`, `question`, `response` |
| `agent_resumes_with_guidance` | Agent continues           | `agent_id`, `task_id`, `guidance_summary`     |

### Agent Management

| Event                      | Trigger                       | Fields                          |
|----------------------------|-------------------------------|---------------------------------|
| `agent_definition_created` | Agent definition file created | `agent_type`, `definition_hash` |

### Recovery Events

| Event                     | Trigger                        | Fields                                                    |
|---------------------------|--------------------------------|-----------------------------------------------------------|
| `event_log_reconstructed` | Event log recreated from state | `reason`, `state_file_timestamp`                          |
| `state_checkpoint`        | State snapshot for recovery    | `completed_tasks`, `in_progress_tasks`, `available_tasks` |

## Logging Requirements

1. Append after every state-changing operation
2. Never overwrite - append only
3. Include timestamp in ISO-8601 format
4. Missing events make debugging impossible
