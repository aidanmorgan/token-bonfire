# State Schema

Coordinator state persists to `{{STATE_FILE}}` for resumption after interruption.

## State File Format

```json
{
  "saved_at": "ISO-8601",
  "save_reason": "compaction | session_pause | infrastructure_blocked",
  "tokens_remaining_percent": 9,
  "compaction_count": 3,
  "session_resume_count": 1,

  "plan_file": "path/to/plan.md",
  "total_tasks": 25,

  "completed_tasks": ["task-1", "task-2"],
  "in_progress_tasks": [
    {
      "task_id": "task-3",
      "agent_id": "dev-agent-1",
      "status": "implementing | awaiting-review | awaiting-audit | awaiting-divine-guidance",
      "last_checkpoint": "unit tests written"
    }
  ],
  "pending_critique": ["task-4"],
  "pending_audit": ["task-5"],
  "active_developers": {"dev-agent-1": {"task_id": "task-3", "dispatched_at": "ISO-8601"}},
  "active_auditors": {},
  "active_critics": {"critic-agent-1": {"task_id": "task-4", "dispatched_at": "ISO-8601"}},
  "critique_failures": {"task-6": 1},
  "critic_timeouts": {"task-6": 0},
  "blocked_tasks": {"task-7": ["task-3", "task-4"]},
  "audit_failures": {"task-8": 2},
  "available_tasks": ["task-7", "task-8"],

  "infrastructure_blocked": false,
  "infrastructure_issue": null,
  "active_remediation": null,
  "remediation_attempt_count": 0,

  "last_usage_check": "ISO-8601",
  "session_utilisation": 85,
  "session_remaining": 15,
  "session_resets_at": "ISO-8601",

  "pending_divine_questions": [
    {
      "agent_id": "dev-agent-2",
      "task_id": "task-9",
      "question": "Should validation reject negative values or clamp them to zero?",
      "options": ["Reject with error", "Clamp to zero", "Allow negative"],
      "timestamp": "ISO-8601",
      "response": null
    }
  ],

  "experts": [
    {
      "agent_id": "crypto-expert",
      "name": "Cryptography Expert",
      "domain": "cryptographic protocols",
      "file_path": ".claude/agents/experts/crypto-expert.md",
      "created_at": "ISO-8601"
    }
  ],
  "active_experts": {},
  "expert_stats": {},
  "pending_delegation_requests": [],
  "paused_agents": {},

  "task_quality_assessed": true,
  "pending_expansions": {},
  "active_business_analysts": {},
  "expanded_tasks": {
    "task-7": {
      "summary": "Add rate limiting to /api/users endpoint",
      "scope": ["Implement token bucket rate limiter"],
      "target_files": ["src/api/users.rs"],
      "technical_approach": "Use existing RateLimiter from src/common",
      "acceptance_criteria": ["Returns 429 after 100 requests/minute"],
      "dependencies": ["src/common/rate_limit.rs"],
      "assumptions": ["REST endpoint pattern follows src/api/auth.rs"],
      "confidence": "HIGH",
      "expanded_at": "ISO-8601",
      "expanded_by": "ba-agent-1"
    }
  }
}
```

## Field Definitions

### Session Tracking

| Field                      | Type     | Description                        |
|----------------------------|----------|------------------------------------|
| `saved_at`                 | ISO-8601 | Timestamp of last save             |
| `save_reason`              | enum     | Why state was persisted            |
| `tokens_remaining_percent` | int      | Context budget remaining           |
| `compaction_count`         | int      | Number of compactions this session |
| `session_resume_count`     | int      | Number of session resumes          |

### Plan Tracking

| Field               | Type     | Description                               |
|---------------------|----------|-------------------------------------------|
| `plan_file`         | string   | Path to plan document                     |
| `total_tasks`       | int      | Total tasks in plan                       |
| `completed_tasks`   | string[] | Task IDs that passed audit                |
| `in_progress_tasks` | object[] | Tasks currently being worked              |
| `pending_critique`  | string[] | Tasks awaiting Critic code quality review |
| `pending_audit`     | string[] | Tasks awaiting Auditor verification       |
| `active_developers` | object   | Maps developer agent ID to task info      |
| `active_auditors`   | object   | Maps auditor agent ID to task info        |
| `active_critics`    | object   | Maps critic agent ID to task info         |
| `critique_failures` | object   | Maps task to critique failure count       |
| `critic_timeouts`   | object   | Maps task to critic timeout count         |
| `blocked_tasks`     | object   | Maps task to its blockers                 |
| `audit_failures`    | object   | Maps task to audit failure count          |
| `available_tasks`   | string[] | Unblocked tasks ready for assignment      |

### Task Status Values

The `status` field in `in_progress_tasks` uses kebab-case and must be one of:

| Status                     | Description                                     |
|----------------------------|-------------------------------------------------|
| `implementing`             | Developer actively working on task              |
| `awaiting-review`          | Developer done, waiting for Critic review       |
| `awaiting-audit`           | Critic passed, waiting for Auditor verification |
| `awaiting-divine-guidance` | Blocked on user clarification                   |

### Infrastructure

| Field                       | Type    | Description                                 |
|-----------------------------|---------|---------------------------------------------|
| `infrastructure_blocked`    | bool    | Whether assignments are halted              |
| `infrastructure_issue`      | string? | Description of blocking issue               |
| `active_remediation`        | string? | Agent ID if remediation in progress         |
| `remediation_attempt_count` | int     | Current remediation loop iteration (max 10) |

### Usage Tracking

| Field                 | Type     | Description                 |
|-----------------------|----------|-----------------------------|
| `last_usage_check`    | ISO-8601 | When usage was last checked |
| `session_utilisation` | int      | Percentage of budget used   |
| `session_remaining`   | int      | Percentage remaining        |
| `session_resets_at`   | ISO-8601 | When budget resets          |

### Divine Intervention

| Field                      | Type     | Description                      |
|----------------------------|----------|----------------------------------|
| `pending_divine_questions` | object[] | Questions awaiting user response |

### Expert Tracking

| Field                         | Type     | Description                              |
|-------------------------------|----------|------------------------------------------|
| `experts`                     | object[] | Registry of plan-derived experts         |
| `active_experts`              | object   | Maps run_id to active expert info        |
| `expert_stats`                | object   | Maps expert_id to usage metrics          |
| `pending_delegation_requests` | object[] | Queue of delegation requests waiting     |
| `paused_agents`               | object   | Agents paused awaiting delegation result |

Expert entry structure:

```json
{
  "agent_id": "crypto-expert",
  "name": "Cryptography Expert",
  "domain": "cryptographic protocols",
  "capabilities": ["key derivation", "encryption selection"],
  "keyword_triggers": ["encryption", "hashing", "key"],
  "file_path": ".claude/agents/experts/crypto-expert.md",
  "created_at": "ISO-8601"
}
```

Expert stats structure:

```json
{
  "crypto-expert": {
    "delegations": 5,
    "completions": 4,
    "failures": 0,
    "out_of_scope": 1,
    "avg_duration_seconds": 45
  }
}
```

### Task Quality

| Field                      | Type   | Description                         |
|----------------------------|--------|-------------------------------------|
| `task_quality_assessed`    | bool   | Whether initial assessment complete |
| `pending_expansions`       | object | Tasks being expanded by BA          |
| `active_business_analysts` | object | Maps BA agent to task               |
| `expanded_tasks`           | object | Expanded task specifications        |

## Save Triggers

State MUST be saved:

- Before any agent dispatch
- After any agent completion
- On infrastructure state change
- On divine intervention events
- Before compaction
- On session pause
