# Task Delivery Loop

This document specifies the step-by-step procedure for the coordinator to dispatch tasks, parse results, and route work through the system.

## Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         COORDINATOR LOOP                                 │
├─────────────────────────────────────────────────────────────────────────┤
│  1. SELECT TASK                                                          │
│     ↓                                                                    │
│  2. PREPARE PROMPT (expand templates, include references)                │
│     ↓                                                                    │
│  3. DISPATCH DEVELOPER (Task tool)                                       │
│     ↓                                                                    │
│  4. PARSE COMPLETION SIGNAL                                              │
│     ↓                                                                    │
│  5. DISPATCH AUDITOR (Task tool)                                         │
│     ↓                                                                    │
│  6. PARSE AUDIT OUTCOME                                                  │
│     ↓                                                                    │
│  7. ROUTE: PASS → complete | FAIL → rework | BLOCKED → remediation       │
│     ↓                                                                    │
│  8. LOOP (fill actor slots)                                              │
└─────────────────────────────────────────────────────────────────────────┘
```

## Step 1: Select Task

**Input**: `available_tasks`, `blocked_tasks`, `in_progress_tasks`

**Procedure**:
1. Filter tasks where all `blocked_by` dependencies are in `completed_tasks`
2. Sort by Task Selection Priority (see state-management.md)
3. Select top N tasks where N = `ACTIVE_DEVELOPERS` - `active_actor_count`

**Output**: List of task IDs to dispatch

## Step 2: Prepare Developer Prompt

**Input**: Task ID, plan content, supporting agents registry

**Procedure**:
1. Extract task details from `PLAN_FILE`:
   - Work description
   - Acceptance criteria
   - Blocked by (dependencies)
   - Required reading (task-specific files)

2. Run task-agent matching algorithm (see agent-coordination.md):
   - Extract task keywords
   - Match against `supporting_agents` registry
   - Categorize as RECOMMENDED, SUGGESTED, or AVAILABLE

3. Expand template placeholders:
   - `{{#each VERIFICATION_COMMANDS}}` → actual commands from config
   - `{{#each recommended_agents}}` → matched agents
   - `{{#if ...}}` → conditionals based on matches

4. Include required references:
   - Developer Agent Definition (from agent-definitions.md)
   - Environment Execution Instructions (from main prompt)
   - Developer References (MUST READ and REFERENCE docs)

**Output**: Complete prompt string ready for Task tool

## Step 3: Dispatch Developer

**Input**: Prepared prompt, task ID

**Tool Call**:
```
Task tool parameters:
  model: [AGENT_MODELS.developer]  # e.g., "sonnet"
  subagent_type: "developer"
  prompt: [prepared prompt from Step 2]
```

### Agent Output Retrieval

The Task tool returns agent output when the agent completes. The coordinator receives results as follows:

**Synchronous Execution (default)**:
```python
# Task tool invocation returns when agent completes
result = Task(
    model="sonnet",
    subagent_type="developer",
    prompt=prepared_prompt
)

# result contains:
# - agent_id: Unique identifier for the agent run
# - output: Full response text from the agent
# - status: "completed" | "failed" | "timeout"
```

**Background Execution** (for long-running tasks):
```python
# Dispatch with run_in_background=True
task_result = Task(
    model="sonnet",
    subagent_type="developer",
    prompt=prepared_prompt,
    run_in_background=True
)

# task_result contains:
# - task_id: Identifier for polling
# - output_file: Path to read results

# Poll for completion using TaskOutput tool
output = TaskOutput(task_id=task_result.task_id, block=True, timeout=300000)
```

**Timeout Handling**:
- Default timeout: `{{AGENT_TIMEOUT}}` ms (15 minutes) for all agent types
- If timeout exceeded: Agent is terminated, coordinator treats as incomplete
- Recovery: Re-dispatch with same task, increment attempt counter
- Track timeout internally via coordinator state, not shell timeout command

**Timeout Tracking**:
```python
# On dispatch, record start time in state
in_progress_tasks.append({
    "task_id": task_id,
    "developer_id": agent_id,
    "status": "implementing",
    "dispatched_at": datetime.now().isoformat(),  # For timeout tracking
    "timeout_ms": AGENT_TIMEOUT
})

# Periodic check (during slot fill or await)
def check_agent_timeouts():
    now = datetime.now()
    for task in in_progress_tasks:
        dispatch_time = datetime.fromisoformat(task["dispatched_at"])
        elapsed_ms = (now - dispatch_time).total_seconds() * 1000
        if elapsed_ms > task["timeout_ms"]:
            handle_agent_timeout(task["task_id"], task["developer_id"])
```

**Agent Crash Recovery**:
```python
if result.status == "failed":
    log_event("agent_crashed", agent_id=result.agent_id, task_id=task_id)

    # Check if recoverable
    if attempt_count < {{TASK_FAILURE_LIMIT}}:
        # Re-dispatch
        dispatch_developer(task_id, attempt_count + 1)
    else:
        # Escalate
        log_event("workflow_failed", reason="agent_crash_limit", task_id=task_id)
```

**Immediately After Dispatch**:
1. Update state:
   ```python
   in_progress_tasks.append({
       "task_id": task_id,
       "developer_id": agent_id,  # from Task tool response
       "status": "implementing",
       "last_checkpoint": None
   })
   available_tasks.remove(task_id)
   ```
2. Save state to `STATE_FILE`
3. Log event: `developer_dispatched`
4. Execute usage script: `uv run {{USAGE_SCRIPT}}`

**Output**: Agent ID (for tracking)

## Step 4: Parse Developer Output

**Input**: Developer agent output (full response text)

**Ready for Audit Signal Format**:

Developers signal readiness for audit (NOT completion - only auditors can mark complete):
```
READY FOR AUDIT: [task ID]

Files Modified:
- [file path]
- [file path]

Tests Written:
- [test file]: [what it tests]

Verification Results (self-verified):
- [check name]: PASS
- [check name]: PASS

Evidence for Auditor:
- Criterion 1: [evidence of completion]
- Criterion 2: [evidence of completion]
```

**Parse Procedure**:
1. Search for `READY FOR AUDIT:` signal
2. If found:
   - Extract task ID (must match assigned task)
   - Extract files modified list
   - Extract self-verification results
   - Update state to `awaiting-audit`
   - Add to `pending_audit`
   - **Route to auditor** (task is NOT complete until auditor PASS)
3. If not found:
   - Search for `SEEKING DIVINE CLARIFICATION` → handle per divine-clarification.md
   - Search for `DELEGATION REQUEST` → handle per agent-coordination.md
   - Search for `INFRA BLOCKED` → trigger remediation
   - Otherwise → treat as incomplete, request checkpoint

**Incomplete Work Signal**:

If developer cannot complete:
```
TASK INCOMPLETE: [task ID]

Progress:
- [what was done]

Blocked By:
- [specific blocker]

Attempted:
- [what was tried]
```

**Output**: Parsed completion data or blocker information

## Step 5: Dispatch Auditor

**Input**: Task ID, files modified, acceptance criteria

**Procedure**:
1. Extract from state:
   - Task's acceptance criteria (from plan)
   - Files modified (from developer completion)
   - Verification commands (from config)

2. Prepare auditor prompt (expand auditor-spec.md template)

3. Dispatch:
   ```
   Task tool parameters:
     model: [AGENT_MODELS.auditor]  # e.g., "opus"
     subagent_type: "auditor"
     prompt: [prepared auditor prompt]
   ```

4. Update state:
   - Add auditor ID to `active_auditors`
   - Log event: `auditor_dispatched`

**Output**: Auditor agent ID

## Step 6: Parse Audit Outcome

**Input**: Auditor agent output

**Parse Procedure**:

Search for these signals in order:

1. **`AUDIT PASSED`**:
   ```
   AUDIT PASSED - [task ID]
   ```
   → Route to PASS handling

2. **`AUDIT FAILED`**:
   ```
   AUDIT FAILED - [task ID]

   Failed:
   - [check]: [specific issue]

   Required:
   - [concrete fix action]
   ```
   → Route to FAIL handling

3. **`AUDIT BLOCKED`**:
   ```
   AUDIT BLOCKED - [task ID]

   Pre-existing failures detected:
   - [N] test failures in [files]
   ```
   → Route to BLOCKED handling

**Output**: Audit outcome (PASS | FAIL | BLOCKED) + details

## Step 7: Route Based on Outcome

### PASS Routing

```python
# Remove from active work
in_progress_tasks.remove(task_id)
pending_audit.remove(task_id)

# Mark complete
completed_tasks.append(task_id)

# Unblock dependents
for task, blockers in blocked_tasks.items():
    if task_id in blockers:
        blockers.remove(task_id)
        if not blockers:
            available_tasks.append(task)

# Log and save
log_event("auditor_pass", task_id=task_id)
save_state()
```

### FAIL Routing

```python
# Check failure count
failed_audits[task_id] = failed_audits.get(task_id, 0) + 1

if failed_audits[task_id] >= TASK_FAILURE_LIMIT:
    # Escalate
    log_event("workflow_failed", reason="task exceeded failure limit", task_id=task_id)
    # Halt and report
else:
    # Return to developer
    in_progress_tasks[task_id]["status"] = "implementing"
    pending_audit.remove(task_id)

    # Dispatch developer with fix requirements
    dispatch_developer_rework(task_id, audit_failures)
```

### BLOCKED Routing

```python
# Halt task assignments
infrastructure_blocked = True
infrastructure_issue = parse_blocked_reason(auditor_output)

# Spawn remediation
dispatch_remediation_agent(infrastructure_issue)

# Log
log_event("infrastructure_blocked", issue=infrastructure_issue)
save_state()
```

---

## Infrastructure Remediation Loop

When `AUDIT BLOCKED` or `INFRA BLOCKED` is detected, the coordinator enters the remediation loop. This loop continues until either:
- Infrastructure is restored (HEALTHY)
- Maximum attempts exceeded (workflow fails)

### Remediation Loop Diagram

```
                    ┌────────────────────────────────┐
                    │  INFRASTRUCTURE BLOCKED        │
                    │  (AUDIT BLOCKED or INFRA       │
                    │   BLOCKED signal detected)     │
                    └───────────────┬────────────────┘
                                    │
                                    ▼
                    ┌────────────────────────────────┐
                    │  PAUSE NEW ASSIGNMENTS         │
                    │  infrastructure_blocked = true │
                    └───────────────┬────────────────┘
                                    │
                    ┌───────────────▼────────────────┐
             ┌─────►│  DISPATCH REMEDIATION AGENT    │
             │      │  attempt = attempt + 1         │
             │      └───────────────┬────────────────┘
             │                      │
             │                      ▼
             │      ┌────────────────────────────────┐
             │      │  AWAIT REMEDIATION COMPLETE    │
             │      │  Parse: REMEDIATION COMPLETE   │
             │      └───────────────┬────────────────┘
             │                      │
             │                      ▼
             │      ┌────────────────────────────────┐
             │      │  DISPATCH HEALTH AUDITOR       │
             │      └───────────────┬────────────────┘
             │                      │
             │                      ▼
             │      ┌────────────────────────────────┐
             │      │  PARSE HEALTH AUDIT RESULT     │
             │      └───────────────┬────────────────┘
             │                      │
             │           ┌──────────┴──────────┐
             │           │                     │
             │        HEALTHY              UNHEALTHY
             │           │                     │
             │           ▼                     ▼
             │  ┌─────────────────┐   ┌─────────────────────┐
             │  │ RESTORE FLOW    │   │ CHECK ATTEMPT LIMIT │
             │  │ blocked = false │   └──────────┬──────────┘
             │  │ attempt = 0     │              │
             │  │ RESUME          │    ┌─────────┴─────────┐
             │  └─────────────────┘    │                   │
             │                    < LIMIT             >= LIMIT
             │                         │                   │
             └─────────────────────────┘                   ▼
                                              ┌─────────────────────┐
                                              │ WORKFLOW FAILED     │
                                              │ Human intervention  │
                                              │ required            │
                                              └─────────────────────┘
```

### Remediation Loop Procedure

**Step R1: Detect Infrastructure Block**

Triggers:
- Developer signals `INFRA BLOCKED: [task ID]`
- Auditor signals `AUDIT BLOCKED - [task ID]` with pre-existing failures

```python
def handle_infrastructure_block(issue_details, reporter_id):
    infrastructure_blocked = True
    infrastructure_issue = issue_details

    # Pause new assignments
    log_event("infrastructure_blocked", issue=issue_details, reported_by=reporter_id)
    save_state()

    # Enter remediation loop
    remediation_loop()
```

**Step R2: Remediation Loop**

```python
def remediation_loop():
    while infrastructure_blocked:
        remediation_attempt_count += 1

        if remediation_attempt_count > REMEDIATION_ATTEMPTS:
            log_event("workflow_failed", reason="remediation_limit_exceeded")
            output("WORKFLOW FAILED - REMEDIATION LIMIT EXCEEDED")
            return  # Human intervention required

        # Dispatch remediation agent
        output(f"REMEDIATION ATTEMPT {remediation_attempt_count}/{REMEDIATION_ATTEMPTS}")
        remediation_agent_id = dispatch_remediation_agent(infrastructure_issue)
        log_event("remediation_dispatched", attempt=remediation_attempt_count)

        # Wait for remediation completion
        remediation_result = await_agent(remediation_agent_id)

        if "REMEDIATION COMPLETE" not in remediation_result:
            # Remediation agent failed unexpectedly
            log_event("remediation_failed", reason="no_completion_signal")
            continue  # Try again

        # Dispatch health auditor to verify
        health_auditor_id = dispatch_health_auditor()
        log_event("health_audit_dispatched", attempt=remediation_attempt_count)

        # Wait for health audit
        health_result = await_agent(health_auditor_id)

        if "HEALTH AUDIT: HEALTHY" in health_result:
            # Success! Restore normal operation
            infrastructure_blocked = False
            infrastructure_issue = None
            remediation_attempt_count = 0

            log_event("infrastructure_restored", attempts_used=remediation_attempt_count)
            output("INFRASTRUCTURE RESTORED")
            return  # Exit loop, resume normal operation

        elif "HEALTH AUDIT: UNHEALTHY" in health_result:
            # Still broken, loop continues
            log_event("health_audit_fail", attempt=remediation_attempt_count)
            output(f"HEALTH AUDIT FAILED - Attempt {remediation_attempt_count}/{REMEDIATION_ATTEMPTS}")
            # Loop continues to next iteration
```

**Step R3: Resume Normal Operation**

After `HEALTH AUDIT: HEALTHY`:

```python
# Clear infrastructure block
infrastructure_blocked = False
infrastructure_issue = None
remediation_attempt_count = 0

# Resume task assignments
output(f"Resuming normal operation with {ACTIVE_DEVELOPERS} parallel developers.")

# Fill actor slots immediately
fill_actor_slots()
```

### Remediation Detection Patterns

| Signal | Source | Meaning |
|--------|--------|---------|
| `INFRA BLOCKED: [task]` | Developer | Cannot run verification commands |
| `AUDIT BLOCKED - [task]` | Auditor | Pre-existing failures detected |
| `REMEDIATION COMPLETE` | Remediation Agent | Fixes applied, ready for health check |
| `HEALTH AUDIT: HEALTHY` | Health Auditor | All verifications pass, resume work |
| `HEALTH AUDIT: UNHEALTHY` | Health Auditor | Still broken, loop again |

### Remediation State Fields

Track these in `STATE_FILE`:

```json
{
  "infrastructure_blocked": true,
  "infrastructure_issue": "15 test failures in tests/unit/",
  "active_remediation": "remediation-agent-1",
  "remediation_attempt_count": 2,
  "remediation_history": [
    {
      "attempt": 1,
      "fixes_applied": ["fixed import in foo.py"],
      "health_result": "UNHEALTHY",
      "remaining_failures": 8
    },
    {
      "attempt": 2,
      "fixes_applied": ["updated test fixtures"],
      "health_result": "pending"
    }
  ]
}
```

---

## Step 8: Fill Actor Slots

After any routing decision, immediately check and fill actor slots:

```python
while count_active_actors() < ACTIVE_DEVELOPERS:
    if not available_tasks:
        break
    if infrastructure_blocked:
        break
    if pending_divine_questions:
        break

    task = select_next_task()
    dispatch_developer(task)
```

**Active Actor Count**:
```python
def count_active_actors():
    return len(active_developers) + len(active_auditors)
```

## Developer Rework Dispatch

When a task fails audit, dispatch the same developer with fix requirements:

```
Task tool parameters:
  model: [AGENT_MODELS.developer]
  subagent_type: "developer"
  prompt: |
    [Include: Developer Agent Definition]

    ---

    REWORK REQUIRED: [task ID]

    Original Work: [copied from plan]
    Acceptance Criteria: [copied from plan]

    AUDIT FAILURES:
    {{#each failures}}
    - {{this.check}}: {{this.issue}}
    {{/each}}

    REQUIRED FIXES:
    {{#each required_fixes}}
    - {{this}}
    {{/each}}

    Previous Files Modified:
    {{#each previous_files}}
    - {{this}}
    {{/each}}

    Fix the identified issues. All verification commands must pass.

    [Include: Environment Execution Instructions]
    [Include: VERIFICATION_COMMANDS]
```

## Coordinator State Machine

```
                     ┌──────────────────┐
                     │  SELECT_TASK     │
                     └────────┬─────────┘
                              │
                              ▼
                     ┌──────────────────┐
                     │ DISPATCH_DEV     │
                     └────────┬─────────┘
                              │
                              ▼
                     ┌──────────────────┐
              ┌──────┤ AWAIT_DEV        ├──────┐
              │      └────────┬─────────┘      │
              │               │                │
         DELEGATION    READY_FOR_AUDIT   DIVINE_QUESTION
              │               │                │
              ▼               ▼                ▼
    ┌─────────────────┐ ┌──────────────┐ ┌─────────────────┐
    │ HANDLE_DELEGATE │ │ DISPATCH_AUD │ │ AWAIT_DIVINE    │
    └────────┬────────┘ └──────┬───────┘ └────────┬────────┘
              │                │                   │
              │                ▼                   │
              │      ┌──────────────────┐         │
              │      │ AWAIT_AUDIT      │         │
              │      └────────┬─────────┘         │
              │               │                   │
              │    ┌──────────┼──────────┐       │
              │    │          │          │       │
              │   PASS       FAIL     BLOCKED    │
              │    │          │          │       │
              │    ▼          ▼          ▼       │
              │ ┌──────┐ ┌────────┐ ┌─────────┐ │
              │ │TASK  │ │REWORK  │ │REMEDIATE│ │
              │ │DONE  │ │        │ │         │ │
              │ └──┬───┘ └───┬────┘ └────┬────┘ │
              │    │         │           │      │
              └────┴─────────┴───────────┴──────┘
                              │
                              ▼
                     ┌──────────────────┐
                     │ FILL_SLOTS       │
                     └────────┬─────────┘
                              │
                              ▼
                          (loop)

TASK STATES:
- implementing: Developer working
- awaiting-audit: Developer done, auditor reviewing
- complete: Auditor PASSED (only state that means "done")
- rework: Auditor FAILED, back to developer

Only AUDIT PASSED transitions a task to "complete".
```

## Signal Detection Patterns

The coordinator must detect these patterns in agent output:

### Task Flow Signals

| Pattern | Regex | Handler |
|---------|-------|---------|
| Ready for audit | `^READY FOR AUDIT: (.+)$` | → dispatch auditor (task NOT complete yet) |
| Task incomplete | `^TASK INCOMPLETE: (.+)$` | → log, fill slots |
| Audit pass | `^AUDIT PASSED - (.+)$` | → **TASK NOW COMPLETE**, route pass |
| Audit fail | `^AUDIT FAILED - (.+)$` | → route fail, developer rework |
| Audit blocked | `^AUDIT BLOCKED - (.+)$` | → enter remediation loop |
| Infra blocked | `^INFRA BLOCKED: (.+)$` | → enter remediation loop |

### Remediation Signals

| Pattern | Regex | Handler |
|---------|-------|---------|
| Remediation complete | `^REMEDIATION COMPLETE$` | → dispatch health auditor |
| Health healthy | `^HEALTH AUDIT: HEALTHY$` | → exit remediation loop, resume flow |
| Health unhealthy | `^HEALTH AUDIT: UNHEALTHY$` | → loop remediation (if under limit) |

### Coordination Signals

| Pattern | Regex | Handler |
|---------|-------|---------|
| Divine question | `^SEEKING DIVINE CLARIFICATION$` | → pause, escalate to user |
| Delegation request | `^DELEGATION REQUEST$` | → spawn supporting agent |
| Agent complete | `^AGENT COMPLETE: (.+)$` | → deliver results to delegating agent |

**Critical**: Only `AUDIT PASSED` marks a task as complete. All other signals represent intermediate states.

---

## Signal Schemas

Each signal has a defined schema. Agents MUST use these exact formats for reliable parsing.

### Developer Ready Signal

```
READY FOR AUDIT: <task_id>

Files Modified:
- <path>
- <path>

Tests Written:
- <path>: <description>
- <path>: <description>

Verification Results (self-verified):
- <check_name>: PASS
- <check_name>: PASS

Evidence for Auditor:
- <criterion_number>: <specific_evidence>
- <criterion_number>: <specific_evidence>
```

**Required fields**: task_id, at least one file, at least one verification, evidence for each criterion.

### Audit Pass Signal

```
AUDIT PASSED - <task_id>

Quality Verification:
- Code quality tells: NONE FOUND
- Standards compliance: VERIFIED

Requirements Verification:
- <criterion>: <evidence_location_and_description>
- <criterion>: <evidence_location_and_description>

Verification Commands:
- <check> (<environment>): PASS
- <check> (<environment>): PASS

Conclusion: <summary>
```

### Audit Fail Signal

```
AUDIT FAILED - <task_id>

Failed Checks:
- <issue_with_file_line_if_applicable>
- <issue_with_file_line_if_applicable>

Required Fixes:
- <concrete_action>
- <concrete_action>

Unverified Requirements:
- <criterion_that_lacks_evidence>
```

### Business Analyst Expansion Signal

```
EXPANDED TASK SPECIFICATION
Task: <task_id>
Confidence: <HIGH|MEDIUM|LOW>

Summary: <1-2_sentence_description>

Scope:
- <deliverable>

Target Files:
- <path>: <changes>

Technical Approach:
<implementation_strategy>

Acceptance Criteria:
- [ ] <verifiable_criterion>

Dependencies:
- <module_or_interface>

Assumptions (require validation):
- <assumption>
```

### Parsing Implementation

```python
def parse_signal(output: str) -> dict:
    """Parse agent output for known signals."""

    signals = [
        ('ready_for_audit', r'^READY FOR AUDIT: (.+)$'),
        ('audit_passed', r'^AUDIT PASSED - (.+)$'),
        ('audit_failed', r'^AUDIT FAILED - (.+)$'),
        ('audit_blocked', r'^AUDIT BLOCKED - (.+)$'),
        ('infra_blocked', r'^INFRA BLOCKED: (.+)$'),
        ('task_incomplete', r'^TASK INCOMPLETE: (.+)$'),
        ('remediation_complete', r'^REMEDIATION COMPLETE$'),
        ('health_healthy', r'^HEALTH AUDIT: HEALTHY$'),
        ('health_unhealthy', r'^HEALTH AUDIT: UNHEALTHY$'),
        ('divine_clarification', r'^SEEKING DIVINE CLARIFICATION$'),
        ('delegation_request', r'^DELEGATION REQUEST$'),
        ('expanded_task', r'^EXPANDED TASK SPECIFICATION$'),
    ]

    for signal_type, pattern in signals:
        match = re.search(pattern, output, re.MULTILINE)
        if match:
            return {
                'type': signal_type,
                'task_id': match.group(1) if match.groups() else None,
                'raw_output': output
            }

    return {'type': 'unknown', 'raw_output': output}
```

---

## Error Recovery

### Agent Timeout
If agent doesn't respond within expected time:
1. Log event: `agent_timeout`
2. Mark task as failed for this attempt
3. If under failure limit, re-dispatch
4. Otherwise, escalate

### Parse Failure
If agent output doesn't contain expected signals:
1. Log full output for debugging
2. Request clarification from agent (if still active)
3. If no response, treat as incomplete
4. Log event: `parse_failure`

### State Corruption
If state file is inconsistent:
1. Log event: `state_corruption_detected`
2. Reconstruct from event log if possible
3. If not possible, request manual repair guidance via AskUserQuestionTool

---

## Phase Completion: Architectural Consistency Check

When a phase completes, perform an architectural consistency review before starting the next phase.

### Trigger Condition

```python
def check_phase_completion(completed_task_id):
    """Check if completing this task finishes a phase."""

    task_phase = get_task_phase(completed_task_id)
    phase_tasks = get_tasks_in_phase(task_phase)

    completed_in_phase = [t for t in phase_tasks if t in completed_tasks]

    if len(completed_in_phase) == len(phase_tasks):
        return task_phase  # Phase is complete
    return None
```

### Consistency Review Procedure

On phase completion:

```python
def perform_architectural_review(completed_phase):
    """Review architectural consistency across phase deliverables."""

    log_event("phase_complete", phase=completed_phase)
    output(f"PHASE {completed_phase} COMPLETE - Initiating architectural review")

    # Collect all files modified in this phase
    phase_tasks = get_tasks_in_phase(completed_phase)
    modified_files = []
    for task in phase_tasks:
        modified_files.extend(get_task_modified_files(task))

    # Dispatch architectural reviewer if available
    arch_reviewer = find_supporting_agent(agent_type="quality_reviewer",
                                          capabilities=["architecture"])

    if arch_reviewer:
        dispatch_architectural_review(arch_reviewer, completed_phase, modified_files)
    else:
        # Coordinator performs basic consistency check
        perform_basic_consistency_check(modified_files)
```

### Basic Consistency Check (Coordinator)

If no architectural reviewer is available, the coordinator performs these checks:

```python
def perform_basic_consistency_check(modified_files):
    """Basic architectural consistency validation."""

    issues = []

    # Check 1: Naming convention consistency
    naming_patterns = extract_naming_patterns(modified_files)
    if len(set(naming_patterns)) > 1:
        issues.append({
            'type': 'naming_inconsistency',
            'details': f"Mixed naming patterns: {naming_patterns}"
        })

    # Check 2: Import pattern consistency
    import_patterns = extract_import_patterns(modified_files)
    if has_conflicting_imports(import_patterns):
        issues.append({
            'type': 'import_inconsistency',
            'details': "Conflicting import styles detected"
        })

    # Check 3: Error handling pattern consistency
    error_patterns = extract_error_patterns(modified_files)
    if len(set(error_patterns)) > 1:
        issues.append({
            'type': 'error_handling_inconsistency',
            'details': f"Mixed error handling: {error_patterns}"
        })

    if issues:
        log_event("architectural_issues_detected", issues=issues)
        # Queue remediation task for next phase
        queue_consistency_fix_task(issues)
    else:
        log_event("architectural_review_pass")
```

### Architectural Review Signal Format

If using a supporting agent for review:

```
ARCHITECTURAL REVIEW: [phase]

Patterns Analyzed:
- Naming conventions: [consistent | inconsistent]
- Error handling: [consistent | inconsistent]
- Import organization: [consistent | inconsistent]
- Data structures: [consistent | inconsistent]

Issues Found:
- [issue 1 with file locations]
- [issue 2 with file locations]

Recommendation:
- [PROCEED | FIX_BEFORE_CONTINUE]
- [specific fixes if needed]
```

### On Issues Detected

```python
if recommendation == "FIX_BEFORE_CONTINUE":
    # Create remediation task at start of next phase
    create_task({
        'id': f'{next_phase}-0-0',
        'title': 'Fix architectural inconsistencies from Phase {completed_phase}',
        'work': f'Address the following inconsistencies:\n{issues}',
        'acceptance_criteria': [
            'All naming follows project convention',
            'All error handling uses standard pattern',
            'All imports follow project organization'
        ],
        'blocked_by': 'none',
        'priority': 'HIGH'  # Execute first in next phase
    })
```

---

## Progress Visibility: Checkpoint Enforcement

Long-running developers may work in silence. The coordinator proactively requests checkpoints to maintain visibility.

### Checkpoint Configuration

| Variable | Value | Description |
|----------|-------|-------------|
| `CHECKPOINT_INTERVAL` | `300000` | Request checkpoint every 5 minutes of agent runtime |
| `CHECKPOINT_TIMEOUT` | `30000` | Agent must respond within 30 seconds |

### Checkpoint Request Trigger

```python
def check_checkpoint_needed():
    """Determine if any active developers need checkpoint requests."""

    now = datetime.now()
    checkpoint_due = []

    for task in in_progress_tasks:
        if task["status"] != "implementing":
            continue

        last_checkpoint = task.get("last_checkpoint_time")
        if last_checkpoint is None:
            last_checkpoint = task["dispatched_at"]

        last_time = datetime.fromisoformat(last_checkpoint)
        elapsed_ms = (now - last_time).total_seconds() * 1000

        if elapsed_ms > CHECKPOINT_INTERVAL:
            checkpoint_due.append(task)

    return checkpoint_due
```

### Checkpoint Request Procedure

When checkpoint is due:

```python
def request_checkpoint(task):
    """Request progress update from active developer."""

    output(f"CHECKPOINT REQUEST: {task['task_id']}")

    # The developer agent should respond with checkpoint format
    # defined in developer-spec.md

    # Update tracking
    task["checkpoint_requested_at"] = datetime.now().isoformat()

    log_event("checkpoint_requested", task_id=task["task_id"],
              developer_id=task["developer_id"])
```

### Expected Checkpoint Response

Developers must respond with:

```
Checkpoint: [task ID]
Status: [implementing | testing | awaiting-verification]
Completed:
- [concrete deliverable]
- [concrete deliverable]
Remaining:
- [specific next step]
- [specific next step]
Files Modified: [list of paths]
Estimated Progress: [N]%
```

### On Checkpoint Received

```python
def handle_checkpoint(task_id, checkpoint_data):
    """Process checkpoint from developer."""

    task = get_task(task_id)

    task["last_checkpoint"] = checkpoint_data["summary"]
    task["last_checkpoint_time"] = datetime.now().isoformat()
    task["estimated_progress"] = checkpoint_data.get("progress", 0)

    log_event("developer_checkpoint",
              task_id=task_id,
              status=checkpoint_data["status"],
              progress=checkpoint_data.get("progress"))

    save_state()

    # Output progress for coordinator visibility
    output(f"CHECKPOINT: {task_id} - {checkpoint_data['status']} ({checkpoint_data.get('progress', '?')}%)")
```

### On Checkpoint Timeout

If developer doesn't respond to checkpoint within `CHECKPOINT_TIMEOUT`:

```python
def handle_checkpoint_timeout(task_id):
    """Handle non-responsive developer."""

    log_event("checkpoint_timeout", task_id=task_id)

    # Check if agent is still running (via task status)
    if is_agent_running(task_id):
        # Agent may be in deep work - allow continuation
        output(f"WARNING: {task_id} checkpoint timeout - agent still active")
    else:
        # Agent may have crashed
        output(f"WARNING: {task_id} checkpoint timeout - checking agent status")
        handle_potential_agent_failure(task_id)
```

### Coordinator Loop Integration

Add to the continuous operation loop:

```python
# In main coordinator loop, after processing agent results:
def coordinator_loop_iteration():
    # ... existing logic ...

    # Check for checkpoint needs during idle moments
    if count_active_actors() < {{ACTIVE_DEVELOPERS}} or not available_tasks:
        checkpoint_due = check_checkpoint_needed()
        for task in checkpoint_due:
            request_checkpoint(task)

    # Check for timeouts
    check_agent_timeouts()

    # Continue with slot filling
    fill_actor_slots()
```

### Progress Dashboard Output

Periodically output overall progress:

```
PROGRESS DASHBOARD
==================
Active: [N]/{{ACTIVE_DEVELOPERS}} actors
Phase: [current phase] ([N]/[total] tasks)
Overall: [N]/[total] tasks complete ([percentage]%)

Active Tasks:
- [task-id]: [status] ([progress]%) - [last checkpoint summary]
- [task-id]: [status] ([progress]%) - [last checkpoint summary]

Pending Audit: [N] tasks
Available: [N] tasks
Blocked: [N] tasks
```

---

## Environment Disagreement Protocol

When verification commands pass in some environments but fail in others, follow this protocol.

### Detection

During audit or verification:

```python
def run_verification_in_all_environments(command, environments):
    """Run verification command in all required environments."""

    results = {}
    for env in environments:
        exit_code = execute_in_environment(command, env)
        results[env] = {
            'exit_code': exit_code,
            'passed': exit_code == 0,
            'output': capture_output()
        }

    return results


def check_environment_agreement(results):
    """Check if all environments agree on pass/fail."""

    passed = [env for env, r in results.items() if r['passed']]
    failed = [env for env, r in results.items() if not r['passed']]

    if len(failed) == 0:
        return 'ALL_PASS', None
    elif len(passed) == 0:
        return 'ALL_FAIL', None
    else:
        return 'DISAGREEMENT', {'passed': passed, 'failed': failed}
```

### On Disagreement

When environments disagree, treat as FAIL (most conservative):

```python
def handle_environment_disagreement(task_id, check_name, disagreement):
    """Handle case where environments disagree on verification result."""

    log_event("environment_disagreement",
              task_id=task_id,
              check=check_name,
              passed_in=disagreement['passed'],
              failed_in=disagreement['failed'])

    # Treat as failure - developer must fix
    return {
        'result': 'FAIL',
        'reason': 'environment_disagreement',
        'details': {
            'check': check_name,
            'passed_environments': disagreement['passed'],
            'failed_environments': disagreement['failed'],
            'investigation_needed': True
        }
    }
```

### Developer Rework with Environment Details

When dispatching developer rework for environment disagreements:

```markdown
REWORK REQUIRED: [task ID]

ENVIRONMENT-SPECIFIC FAILURE DETECTED

Check: [check name]
Passed In: {{#each passed_envs}}{{this}}, {{/each}}
Failed In: {{#each failed_envs}}{{this}}, {{/each}}

Failure Details by Environment:
{{#each failed_envs}}
## {{this.name}}
Exit Code: {{this.exit_code}}
Output:
```
{{this.output}}
```
{{/each}}

REQUIRED INVESTIGATION:
1. Reproduce the failure in [failed environment]
2. Identify environment-specific cause:
   - Path differences?
   - Dependency version differences?
   - OS-specific behavior?
   - Missing environment variables?
3. Fix to work in ALL environments

All verification commands must pass in ALL required environments.
```

### Common Environment Disagreement Causes

| Cause | Symptom | Typical Fix |
|-------|---------|-------------|
| Path separators | Works on Mac, fails on Linux | Use `pathlib` or `os.path.join` |
| Line endings | Git diff fails | Configure `.gitattributes` |
| Case sensitivity | Import works on Mac, fails on Linux | Match exact case |
| Shell differences | `[[` works on Mac bash, fails elsewhere | Use POSIX `[` |
| Missing dependency | Works locally, fails in container | Update container setup |
| Timezone | Time tests fail in different TZ | Use UTC in tests |

### Auditor Reporting Format

Auditors must report per-environment results:

```
VERIFICATION RESULTS

{{#each VERIFICATION_COMMANDS}}
## {{this.check}}
{{#each ENVIRONMENTS}}
- {{this.name}}: {{result}} (exit {{exit_code}})
{{/each}}
{{/each}}

OVERALL: [PASS if all pass in all required environments | FAIL otherwise]

{{#if disagreements}}
ENVIRONMENT DISAGREEMENTS DETECTED:
{{#each disagreements}}
- {{this.check}}: Passed in [{{this.passed}}], Failed in [{{this.failed}}]
{{/each}}
{{/if}}
```
