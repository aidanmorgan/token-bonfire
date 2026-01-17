# State Fields

[← Back to State Management](index.md)

All state field definitions organized by category.

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

| Field                       | Type    | Description                                                                |
|-----------------------------|---------|----------------------------------------------------------------------------|
| `infrastructure_blocked`    | Boolean | Assignments halted for remediation                                         |
| `infrastructure_issue`      | Object  | Details of blocking issue                                                  |
| `active_remediation`        | String  | Agent ID if remediation in progress                                        |
| `remediation_attempt_count` | Integer | Current remediation loop iteration (0 to REMEDIATION_ATTEMPTS, default 10) |

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

## Related Documentation

- [Attempt Tracking](attempt-tracking.md) - Attempt tracking and escalation
- [Update Triggers](update-triggers.md) - When and how state updates
- [State Schema](../orchestrator/state-schema.md) - Complete state file format
