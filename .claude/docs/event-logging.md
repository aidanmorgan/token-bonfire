# Event Logging

The coordinator maintains `{{EVENT_LOG_FILE}}` as an append-only event store. Every coordinator operation and agent
result appends one JSON object per line (JSONL format).

## Event Structure

```json
{
  "timestamp": "ISO-8601",
  "sequence": 1,
  "session_id": "UUID identifying the current session",
  "event_type": "string",
  "agent_id": "string or null",
  "task_id": "string or null",
  "details": {}
}
```

**Session ID**: Every event MUST include the `session_id` field. This allows filtering events by session and correlating
work across session resumes.

## Append-Only Requirement

Events MUST be appended to the log file, never overwritten. Each new event adds one line to the end of the file.
Overwriting the log file destroys the audit trail.

## Event Types

| Event Type                        | Trigger                                                    | Details Fields                                                                                                     |
|-----------------------------------|------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------|
| `session_start`                   | Fresh coordinator start (no state file)                    | `plan_file`, `total_tasks`                                                                                         |
| `session_resumed`                 | Coordinator resumes from existing state                    | `previous_session_id`, `state_saved_at`, `in_progress_tasks_count`, `pending_audit_count`, `completed_tasks_count` |
| `task_restarted_on_resume`        | In-progress or pending-audit task moved back to available  | `previous_status`, `reason`                                                                                        |
| `task_reverification_required`    | Completed task needs re-audit (near session end)           | `completed_at`, `last_event_time`, `time_since_completion_minutes`                                                 |
| `agent_definition_created`        | Missing agent definition created                           | `agent_type`, `definition_hash`                                                                                    |
| `expert_created`                  | Plan-derived expert created                                | `agent_id`, `agent_type`, `name`, `domain`, `capabilities`, `keyword_triggers`, `request_types`, `definition_hash` |
| `expert_request_received`         | Coordinator intercepts EXPERT_REQUEST signal               | `from_agent_id`, `from_agent_type`, `task_id`, `expert_name`, `question_summary`                                   |
| `expert_delegated`                | Expert spawned for delegation                              | `run_id`, `agent_id`, `agent_type`, `from_agent_id`, `task_id`, `request_type`, `request_summary`                  |
| `delegation_queued`               | Delegation request queued (agent busy)                     | `request_id`, `agent_id`, `from_agent_id`, `task_id`, `request_type`, `queue_position`                             |
| `expert_complete`                 | Expert returns result                                      | `run_id`, `agent_id`, `from_agent_id`, `task_id`, `duration_seconds`, `confidence_level`, `deliverables_count`     |
| `expert_failed`                   | Expert errored or timed out                                | `run_id`, `agent_id`, `from_agent_id`, `task_id`, `error_reason`                                                   |
| `expert_out_of_scope`             | Expert signals request out of scope                        | `run_id`, `agent_id`, `from_agent_id`, `task_id`, `suggested_alternative`                                          |
| `delegation_results_delivered`    | Results delivered to delegating agent                      | `agent_id`, `from_agent_id`, `task_id`, `request_type`                                                             |
| `developer_dispatched`            | Developer agent spawned                                    | `task_id`, `agent_id`, `blocked_by`                                                                                |
| `developer_checkpoint`            | Developer reports progress                                 | `task_id`, `agent_id`, `status`, `checkpoint`                                                                      |
| `developer_ready_for_review`      | Developer signals ready for Critic review (NOT complete)   | `task_id`, `agent_id`, `files_modified`                                                                            |
| `developer_blocked`               | Developer reports infrastructure issue                     | `task_id`, `agent_id`, `issue_type`, `issue_details`                                                               |
| `developer_incomplete`            | Developer signals task incomplete                          | `task_id`, `agent_id`, `blocker`, `attempted`, `needed`, `attempt_number`, `escalate`                              |
| `critic_dispatched`               | Critic agent spawned for code review                       | `task_id`, `agent_id`, `files_to_review`                                                                           |
| `critic_pass`                     | Critic passes code quality review                          | `task_id`, `agent_id`, `review_summary`                                                                            |
| `critic_fail`                     | Critic fails code quality review                           | `task_id`, `agent_id`, `issues_found`, `required_fixes`                                                            |
| `critic_timeout`                  | Critic agent timed out                                     | `task_id`, `agent_id`, `timeout_ms`, `attempt_number`                                                              |
| `auditor_dispatched`              | Auditor agent spawned                                      | `task_id`, `agent_id`, `files_to_audit`                                                                            |
| `task_complete`                   | **Auditor confirms task complete** (ONLY completion event) | `task_id`, `agent_id`, `evidence_summary`                                                                          |
| `auditor_fail`                    | Auditor rejects task, returns to developer                 | `task_id`, `agent_id`, `failures`, `required_fixes`                                                                |
| `auditor_blocked`                 | Auditor finds pre-existing failures                        | `task_id`, `agent_id`, `pre_existing_failures`                                                                     |
| `signal_rejected`                 | Developer signal rejected (incomplete matrix)              | `task_id`, `agent_id`, `signal_type`, `reason`, `missing_environments`                                             |
| `environment_verification_passed` | All environments verified                                  | `task_id`, `environments_tested`, `all_passed`                                                                     |
| `environment_verification_failed` | One or more environments failed                            | `task_id`, `failed_environments`, `error_details`                                                                  |
| `remediation_dispatched`          | Remediation agent spawned                                  | `agent_id`, `issue_type`, `issue_details`, `attempt_number`                                                        |
| `remediation_complete`            | Remediation agent signals done                             | `agent_id`, `fixes_applied`, `summary`                                                                             |
| `remediation_failed`              | Remediation agent failed (no completion signal)            | `agent_id`, `reason`, `attempt_number`                                                                             |
| `health_audit_dispatched`         | Health auditor spawned                                     | `agent_id`, `attempt_number`                                                                                       |
| `health_audit_pass`               | Codebase verified healthy                                  | `agent_id`                                                                                                         |
| `health_audit_fail`               | Codebase still unhealthy                                   | `agent_id`, `failures`                                                                                             |
| `health_audit_unexpected`         | Health auditor returned unexpected response                | `agent_id`, `attempt_number`, `response_summary`                                                                   |
| `remediation_exhausted`           | Remediation attempts exceeded limit                        | `attempt_count`, `issue_type`, `escalation_required`                                                               |
| `infrastructure_blocked`          | Assignments halted                                         | `reported_by`, `issue_type`, `blocked_tasks`                                                                       |
| `infrastructure_restored`         | Assignments resumed                                        | `attempts_used`, `fixes_applied`                                                                                   |
| `compaction_start`                | Context compaction begins                                  | `compaction_number`, `context_remaining`                                                                           |
| `compaction_complete`             | Compaction finished                                        | `compaction_number`, `full_reload`                                                                                 |
| `session_pause`                   | Session limit reached, coordinator pausing                 | `reason`, `remaining_percent`, `resets_at`                                                                         |
| `usage_check`                     | Usage script executed                                      | `utilisation`, `remaining`, `resets_at`                                                                            |
| `workflow_complete`               | All tasks done                                             | `total_tasks`, `compactions`, `session_resumes`                                                                    |
| `workflow_failed`                 | Unrecoverable error                                        | `reason`, `last_state`                                                                                             |
| `agent_seeks_guidance`            | Agent signals need for clarification                       | `agent_id`, `task_id`, `question`, `options`                                                                       |
| `coordinator_prays`               | Coordinator invokes AskUserQuestionTool                    | `agent_id`, `task_id`, `question`                                                                                  |
| `divine_response_received`        | God provides guidance                                      | `agent_id`, `task_id`, `question`, `response`                                                                      |
| `agent_resumes_with_guidance`     | Agent continues with divine guidance                       | `agent_id`, `task_id`, `guidance_summary`                                                                          |
| `task_quality_assessment`         | Plan tasks assessed for implementability                   | `implementable_count`, `needs_expansion_count`, `needs_clarification_count`                                        |
| `business_analyst_dispatched`     | BA agent spawned to expand task                            | `task_id`, `agent_id`, `missing_criteria`                                                                          |
| `task_expanded`                   | BA successfully expanded task                              | `task_id`, `confidence`, `expansion_summary`                                                                       |
| `expansion_needs_clarification`   | BA expansion requires divine guidance                      | `task_id`, `questions`, `options`                                                                                  |

## Logging Requirement

After every state-changing operation, append the corresponding event to `{{EVENT_LOG_FILE}}` before proceeding. Never
overwrite the file.
