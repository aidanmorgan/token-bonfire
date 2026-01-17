# Coordinator Resume

Resume session procedures when state file exists.

---

## Navigation

- [Startup Overview](startup-overview.md) - Overview and decision logic
- [Fresh Start](fresh-start.md) - Fresh session initialization
- **[Resume](resume.md)** - This file
- [Coordinator Configuration](../coordinator-configuration.md) - Configuration values
- [State Management](../state-management.md) - State tracking

---

## RESUME FROM STATE (State File Exists)

**CRITICAL**: The coordinator must properly restore state and handle interrupted work.

### Step 1: Load State File

Read `{{STATE_FILE}}` and restore coordinator memory.

### Step 2: Generate New Session ID

Create a new UUID for this session, preserving the previous one:

```json
{
  "session_id": "<new UUID>",
  "session_started_at": "<current ISO-8601 timestamp>",
  "previous_session_id": "<session_id from loaded state>",
  "session_resume_count": "<previous count + 1>"
}
```

### Step 3: Log Session Resume Event

```json
{
  "event": "session_resumed",
  "session_id": "<new session ID>",
  "previous_session_id": "<old session ID>",
  "resumed_at": "<ISO-8601>",
  "state_saved_at": "<saved_at from state file>"
}
```

### Step 4: Verify Agent Files Exist

Check that all required agent files exist.

```python
REQUIRED_AGENTS = [
    ("developer", ".claude/agents/developer.md"),
    ("auditor", ".claude/agents/auditor.md"),
    ("business-analyst", ".claude/agents/business-analyst.md"),
    ("remediation", ".claude/agents/remediation.md"),
    ("health-auditor", ".claude/agents/health-auditor.md"),
    ("critic", ".claude/agents/critic.md"),
]

missing_agents = []
for name, path in REQUIRED_AGENTS:
    if not os.path.exists(path):
        missing_agents.append(name)
```

**Decision Logic:**

- If ALL agents exist → Use existing agents, proceed to step 5
- If ANY agent is missing → Regenerate ALL agents AND experts

**If agents need regeneration:**

1. Run best practices research (see FRESH START step 4)
2. Run gap analysis (see FRESH START step 5) - includes deleting existing experts
3. Create experts (see FRESH START step 6)
4. Create ALL agent files with expert list embedded (see FRESH START step 7)
5. Update state with new `agents_regenerated_at` timestamp

Log the check result:

```json
{
  "event": "resume_agent_check",
  "missing_agents": ["critic"],
  "decision": "regenerate_all" | "use_existing"
}
```

**If using existing agents:** Also verify experts exist:

```python
# Check if experts from state still exist
missing_experts = []
for expert in state.get('available_experts', []):
    expert_path = f".claude/agents/experts/{expert['name']}.md"
    if not os.path.exists(expert_path):
        missing_experts.append(expert['name'])

# If any experts missing, recreate just the missing ones
# (unlike agents, we don't regenerate all experts if some are missing)
```

For missing experts only, run gap analysis and create the missing experts.
Existing experts are reused since they were created for this same plan.

### Step 5: Handle In-Progress Tasks

All tasks in `in_progress_tasks` are considered **INCOMPLETE** and must be restarted:

```
FOR EACH task in in_progress_tasks:
  1. Move task back to available_tasks
  2. Clear any associated agent tracking
  3. Log event: task_restarted_on_resume
     - task_id
     - previous_status (implementing, awaiting-audit, etc.)
     - reason: "session_interrupted"
```

**Rationale**: We cannot know the state of interrupted agents. Partial work may exist but is unreliable. Starting
fresh is safer.

### Step 6: Handle Pending Audit Tasks

Tasks in `pending_audit` are treated as incomplete since the audit never happened:

```
FOR EACH task in pending_audit:
  1. Move task back to available_tasks
  2. Log event: task_restarted_on_resume
     - task_id
     - previous_status: "pending_audit"
     - reason: "audit_interrupted"
```

### Step 7: Re-Verify Recent Completions

Find the last event timestamp in `{{EVENT_LOG_FILE}}`. Tasks completed within
`{{RECENT_COMPLETION_WINDOW}}` of that timestamp must be re-audited:

```
last_event_time = timestamp of final event in EVENT_LOG_FILE

FOR EACH task_id, completion_data in completed_tasks:
  IF (last_event_time - completion_data.completed_at) <= {{RECENT_COMPLETION_WINDOW}}:
    1. Move task from completed_tasks to pending_audit
    2. Log event: task_reverification_required
       - task_id
       - completed_at
       - last_event_time
       - time_since_completion
       - reason: "completed_near_session_end"
```

**Rationale**: Tasks completed near session end may have passed audit but subsequent work could have broken them.
Re-verification ensures integrity.

### Step 8: Reconcile State with Plan

Check if `{{PLAN_FILE}}` has changed since state was saved:

- If new tasks added → add to `available_tasks` or `blocked_tasks` as appropriate
- If tasks removed → remove from all tracking (log warning)
- If task specs changed → mark as needing re-implementation if already complete

### Step 9: Clear Stale Agent Tracking

Reset all `active_*` fields since those agents are gone:

```json
{
  "active_developers": {},
  "active_auditors": {},
  "active_business_analysts": {},
  "active_experts": {},
  "active_remediation": null
}
```

### Step 10: Save Updated State

Persist the reconciled state before proceeding.

### Step 11: Proceed to Execution Loop

See [State Management](../state-management.md) for state field details.

---

## Related Documentation

- [Startup Overview](startup-overview.md) - Overview and decision logic
- [Fresh Start](fresh-start.md) - Fresh session initialization
- [Coordinator Configuration](../coordinator-configuration.md) - Configuration values
- [State Management](../state-management.md) - State tracking
- [Recovery Procedures](../recovery-procedures.md) - Error recovery
