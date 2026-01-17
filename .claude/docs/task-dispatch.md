# Task Dispatch

This document covers Steps 1-4 of the coordinator loop: selecting tasks, preparing prompts, dispatching developers, and
parsing results.

**Related Documents:**

- [review-audit-flow.md](review-audit-flow.md) - Steps 5-9: Critic and Auditor flow
- [signal-specification.md](signal-specification.md) - All signal formats
- [agent-timeout-recovery.md](agent-timeout-recovery.md) - Timeout and crash handling
- [state-management.md](state-management.md) - State tracking

---

## Overview

**Task Dispatch (Steps 1-4)**:

1. SELECT TASK (from available, unblocked tasks)
2. PREPARE PROMPT (expand templates, include references)
3. DISPATCH DEVELOPER (Task tool)
4. AWAIT DEVELOPER → parse for READY_FOR_REVIEW signal
   → Continue to review-audit-flow.md

---

## Step 1: Select Task

**Input**: `available_tasks`, `blocked_tasks`, `in_progress_tasks`

**Procedure**:

1. Filter tasks where all `blocked_by` dependencies are in `completed_tasks`
2. Sort by Task Selection Priority (see [state-management.md](state-management.md))
3. Select top N tasks where N = `ACTIVE_DEVELOPERS` - `active_actor_count`

**Output**: List of task IDs to dispatch

```python
def select_tasks_for_dispatch() -> list[str]:
    """Select tasks ready for developer assignment."""

    ready_tasks = []
    invalid_blockers = []

    for task_id in available_tasks:
        blockers = blocked_tasks.get(task_id, [])

        # ═══════════════════════════════════════════════════════════════════
        # VALIDATION: Ensure all blockers are valid task IDs in the plan
        # ═══════════════════════════════════════════════════════════════════
        for blocker in blockers:
            if not is_valid_task_id(blocker):
                invalid_blockers.append({
                    'task_id': task_id,
                    'invalid_blocker': blocker
                })

        # Only dispatch if all blockers are complete (or invalid blockers logged)
        if all(b in completed_tasks for b in blockers):
            ready_tasks.append(task_id)

    # Log invalid blockers for debugging (but don't halt)
    if invalid_blockers:
        log_event("invalid_blockers_detected",
                  count=len(invalid_blockers),
                  details=invalid_blockers)

    # Sort by priority (phase order, then dependency count)
    ready_tasks.sort(key=lambda t: (
        get_phase_priority(t),
        len(get_dependents(t))  # Tasks with more dependents first
    ))

    # Select up to available slots
    slots = ACTIVE_DEVELOPERS - len(active_developers)
    return ready_tasks[:slots]


def is_valid_task_id(task_id: str) -> bool:
    """Check if a task ID exists in the plan or state."""

    # Check various task collections
    all_known_tasks = (
            set(available_tasks) |
            set(completed_tasks) |
            set(blocked_tasks.keys()) |
            {t['task_id'] for t in in_progress_tasks} |
            set(pending_critique) |
            set(pending_audit)
    )

    return task_id in all_known_tasks
```

---

## Step 2: Prepare Agent Prompt

**Input**: Task ID, plan content, agent type

**The coordinator builds the complete prompt by concatenating:**

1. **Agent Definition** (from `.claude/agents/[agent-type].md`)
2. **Task-Specific Context** (from plan and configuration)

### Prompt Construction

```
FINAL_PROMPT = READ(".claude/agents/[agent-type].md")
            + "---"
            + TASK_SPECIFIC_PROMPT
```

### Step 2.1: Read Agent Definition File

```python
agent_file_path = f".claude/agents/{agent_type}.md"
agent_definition = Read(agent_file_path)

# The agent file contains:
# - YAML frontmatter (name, description, model, tools)
# - Identity, success criteria, quality tells
# - Method (phases), boundaries
# - Signal formats, escalation protocol
```

### Step 2.2: Build Task-Specific Context

1. Extract task details from `PLAN_FILE`:
    - Work description
    - Acceptance criteria
    - Blocked by (dependencies)
    - Required reading (task-specific files)

2. Run task-agent matching (see [agent-coordination.md](agent-coordination.md)):
    - Extract task keywords
    - Match against `experts` registry
    - Categorize as RECOMMENDED, SUGGESTED, or AVAILABLE
    - **VALIDATE expert files exist** before including in prompt

   ```python
   def match_experts_to_task(task_id: str, experts: list[dict]) -> list[dict]:
       """Match experts to task using keyword triggers from expert definitions."""

       task = get_task(task_id)
       task_text = f"{task.work} {' '.join(task.acceptance_criteria)}".lower()

       matched = []
       for expert in experts:
           # Each expert has keyword_triggers generated during expert creation
           keywords = expert.get('keyword_triggers', [])

           # Check if any keyword matches task text
           matching_keywords = [kw for kw in keywords if kw.lower() in task_text]

           if matching_keywords:
               matched.append({
                   **expert,
                   'match_type': 'SUGGESTED',
                   'matched_keywords': matching_keywords
               })

       return matched


   def match_and_validate_experts(task_id: str, experts: list[dict]) -> list[dict]:
       """Match experts to task and validate their files exist."""

       matched = match_experts_to_task(task_id, experts)
       validated = []

       for expert in matched:
           expert_file = expert.get('file')
           if expert_file and os.path.exists(expert_file):
               validated.append(expert)
           else:
               log_event("expert_file_missing",
                         expert_name=expert.get('name'),
                         expected_file=expert_file,
                         task_id=task_id)
               # Expert not available - still continue but without this expert

       return validated
   ```

3. Expand template placeholders:
    - `{{#each VERIFICATION_COMMANDS}}` → actual commands from config
    - `{{#each recommended_agents}}` → matched agents
    - `{{#each ENVIRONMENTS}}` → environment definitions

4. **Include required reading** (CRITICAL - agents have no implicit knowledge):
    - Include both MUST READ files and REFERENCE files
    - Include task-specific Required Reading from the plan
    - Format as explicit file paths, not patterns

### Step 2.3: Concatenate Final Prompt

```python
task_specific_prompt = f"""
---

## Task Assignment

Task ID: {task_id}
Work: {task.work}

### Acceptance Criteria
{format_acceptance_criteria(task.acceptance_criteria)}

### Required Reading
{format_required_reading(agent_docs, task.required_reading)}

### Available Experts
{format_experts(matched_experts)}

### Commands
{format_commands_table(agent_type)}

### Environments
{format_environments_table()}

---

Begin work on this task.
"""

final_prompt = agent_definition + task_specific_prompt
```

### Required Reading Format

All agent prompts MUST include:

```markdown
## Required Reading

**MUST READ** - Read these files FIRST, before any implementation work:

- `path/to/file`: purpose
- Task-specific files from plan

**REFERENCE** - Consult as needed during work:

- `path/to/docs`: purpose

IMPORTANT: You MUST read all MUST READ files before starting work.
```

---

## Step 3: Dispatch Agent

**Input**: Prepared prompt, task ID, agent type

### Procedure

1. **Read Agent Model from File**:
   ```python
   agent_file = Read(f".claude/agents/{agent_type}.md")
   model = parse_frontmatter(agent_file)['model']  # e.g., "sonnet", "opus", "haiku"
   ```

2. **Spawn Agent via Task Tool**:
   ```
   Task tool parameters:
     description: "[agent_type] agent for [task_id]"
     model: [model from agent file frontmatter]
     subagent_type: "developer"  # Always "developer" - agent definition provides behavior
     prompt: [final_prompt from Step 2]
   ```

3. **Update State**:
   ```python
   active_developers[agent_id] = {
       'task_id': task_id,
       'agent_type': agent_type,
       'dispatched_at': datetime.now().isoformat()
   }
   log_event("agent_dispatched", task_id=task_id, agent_type=agent_type)
   save_state()
   ```

### Agent Output Retrieval

**Synchronous Execution (default)**:

```python
result = Task(
    description="developer agent for task-1-1",
    model="sonnet",
    subagent_type="developer",
    prompt=final_prompt
)

# result contains:
# - agent_id: Unique identifier
# - output: Full response text
# - status: "completed" | "failed" | "timeout"
```

**Background Execution** (for parallel dispatch):

```python
task_result = Task(
    description="developer agent for task-1-1",
    model="sonnet",
    subagent_type="developer",
    prompt=final_prompt,
    run_in_background=True
)

# Poll for completion
output = TaskOutput(task_id=task_result.task_id, block=True, timeout=300000)
```

### Timeout and Crash Handling

See [agent-timeout-recovery.md](agent-timeout-recovery.md) for:

- Timeout tracking and handling
- Crash recovery procedures
- Re-dispatch logic

### Post-Dispatch Updates

1. Update state:
   ```python
   in_progress_tasks.append({
       "task_id": task_id,
       "developer_id": agent_id,
       "status": "implementing",
       "dispatched_at": datetime.now().isoformat()
   })
   available_tasks.remove(task_id)
   ```
2. Save state to `STATE_FILE`
3. Log event: `developer_dispatched`

---

## Step 4: Parse Developer Output

**Input**: Developer agent output (full response text)

### READY_FOR_REVIEW Signal Format

Developers signal readiness for review:

```
READY_FOR_REVIEW: <task_id>

Files Modified:
- <file_path>
- <file_path>

Tests Written:
- <test_file>: <what_it_tests>

Verification Results (self-verified):
- <check_name>: PASS

Expert Consultation:
- Consulted: <expert-name> for <topic> - Advice: <brief summary>
  OR
- Not needed: <justification>
  OR
- Pre-implementation review: <expert-name> confirmed approach

Summary:
<brief_description_of_implementation>
```

### Parse Procedure

```python
def parse_developer_output(output: str, expected_task_id: str) -> dict:
    """Parse developer output for READY_FOR_REVIEW signal."""

    # Check for READY_FOR_REVIEW signal
    match = re.search(r'^READY_FOR_REVIEW:\s*(\S+)', output, re.MULTILINE)

    if match:
        task_id = match.group(1)
        if task_id != expected_task_id:
            raise SignalError(f"Task ID mismatch: expected {expected_task_id}, got {task_id}")

        return {
            'signal': 'READY_FOR_REVIEW',
            'task_id': task_id,
            'files_modified': extract_files_modified(output),
            'tests_written': extract_tests_written(output),
            'verification_results': extract_verification_results(output),
            'expert_consultation': extract_expert_consultation(output),
            'summary': extract_summary(output),
            'next_action': 'DISPATCH_CRITIC'
        }

    # Check for other signals
    if re.search(r'^TASK_INCOMPLETE:', output, re.MULTILINE):
        return {'signal': 'TASK_INCOMPLETE', 'next_action': 'LOG_AND_FILL_SLOTS'}

    if re.search(r'^INFRA_BLOCKED:', output, re.MULTILINE):
        return {'signal': 'INFRA_BLOCKED', 'next_action': 'ENTER_REMEDIATION'}

    if re.search(r'^SEEKING_DIVINE_CLARIFICATION', output, re.MULTILINE):
        return {'signal': 'DIVINE_CLARIFICATION', 'next_action': 'AWAIT_DIVINE'}

    # No recognized signal
    return {'signal': 'UNKNOWN', 'next_action': 'REQUEST_CHECKPOINT'}


def extract_expert_consultation(output: str) -> dict:
    """Extract Expert Consultation field from READY_FOR_REVIEW signal."""

    # Look for Expert Consultation section
    consultation_match = re.search(
        r'Expert Consultation:\s*\n-\s*(.+?)(?=\n\n|\nSummary:)',
        output, re.DOTALL
    )

    if not consultation_match:
        return {'type': 'missing', 'value': None}

    consultation_text = consultation_match.group(1).strip()

    # Parse the three valid formats
    if consultation_text.startswith('Consulted:'):
        return {'type': 'consulted', 'value': consultation_text}
    elif consultation_text.startswith('Not needed:'):
        return {'type': 'not_needed', 'value': consultation_text}
    elif consultation_text.startswith('Pre-implementation review:'):
        return {'type': 'pre_implementation', 'value': consultation_text}
    else:
        return {'type': 'invalid', 'value': consultation_text}
```

### On READY_FOR_REVIEW

1. Extract task ID (must match assigned task)
2. Extract files modified list
3. Extract self-verification results
4. Update state to `awaiting-review`
5. Add to `pending_critique`
6. **DISPATCH CRITIC** → Continue to [review-audit-flow.md](review-audit-flow.md)

### TASK_INCOMPLETE Signal Format

If developer cannot complete:

```
TASK_INCOMPLETE: <task_id>

Blocker: <description>
Attempted: <what_was_tried>
Needed: <what_would_unblock>
```

---

## Signal Reference

| Signal                         | Format                        | Next Action       |
|--------------------------------|-------------------------------|-------------------|
| `READY_FOR_REVIEW`             | `READY_FOR_REVIEW: <task_id>` | Dispatch Critic   |
| `TASK_INCOMPLETE`              | `TASK_INCOMPLETE: <task_id>`  | Log, fill slots   |
| `INFRA_BLOCKED`                | `INFRA_BLOCKED: <task_id>`    | Enter remediation |
| `SEEKING_DIVINE_CLARIFICATION` | (no task ID)                  | Await human       |

See [signal-specification.md](signal-specification.md) for complete signal formats.

---

## Next Steps

After parsing developer output:

- On `READY_FOR_REVIEW` → [review-audit-flow.md](review-audit-flow.md) (Critic dispatch)
- On `INFRA_BLOCKED` → [remediation-loop.md](remediation-loop.md)
- On `TASK_INCOMPLETE` → Fill actor slots, log event

---

## Cross-References

- [review-audit-flow.md](review-audit-flow.md) - Steps 5-9
- [signal-specification.md](signal-specification.md) - Signal formats
- [state-management.md](state-management.md) - State tracking
- [agent-coordination.md](agent-coordination.md) - Task-agent matching
- [agent-timeout-recovery.md](agent-timeout-recovery.md) - Timeout handling
