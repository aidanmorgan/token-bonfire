# Agent File Recovery

Procedures for recovering missing or corrupted agent definition files.

## Overview

Agent definition files (`.claude/agents/*.md`) contain the prompts and behaviors for different agent types. When
missing, they must be recreated from the agent creation templates.

See also:

- [Event Log Recovery](event-log-recovery.md) - Event log integrity
- [Session Recovery](session-recovery.md) - Complete recovery procedures
- [Recovery Index](index.md) - Overview of all recovery procedures

---

## Plan File Recovery

### Integrity Check

```python
def validate_plan_file(plan_file_path: str) -> ValidationResult:
    """Validate plan file exists and is parseable."""

    if not os.path.exists(plan_file_path):
        return ValidationResult(
            status='missing',
            recoverable=False,
            error="Plan file not found - cannot continue without plan"
        )

    try:
        content = Read(plan_file_path)

        # Check for required sections
        required_patterns = [
            r'^## Phase \d+',  # At least one phase
            r'^### Task \d+',   # At least one task
        ]

        for pattern in required_patterns:
            if not re.search(pattern, content, re.MULTILINE):
                return ValidationResult(
                    status='incomplete',
                    recoverable=False,
                    error=f"Plan missing required section matching: {pattern}"
                )

        return ValidationResult(status='valid')

    except Exception as e:
        return ValidationResult(
            status='unreadable',
            recoverable=False,
            error=str(e)
        )
```

### Plan File Missing

If plan file is missing, this is **NOT recoverable** - escalate immediately:

```python
def handle_missing_plan():
    """Handle missing plan file - requires human intervention."""

    log_event("plan_file_missing",
              severity="CRITICAL",
              action="halting")

    raise PlanFileMissingError(
        "Plan file not found. Cannot continue execution. "
        "Please restore the plan file and restart."
    )
```

---

## Agent File Recovery

### Missing Agent Definition

```python
def recover_missing_agent_file(agent_name: str, agent_definitions_doc: str):
    """Recreate missing agent file from definitions document."""

    # 1. Find the creation prompt for this agent
    creation_prompt = extract_creation_prompt(agent_definitions_doc, agent_name)

    if not creation_prompt:
        raise AgentRecoveryError(f"No creation prompt found for {agent_name}")

    # 2. Spawn agent to recreate the file
    Task(
        model='opus',
        subagent_type='developer',
        prompt=creation_prompt
    )

    # 3. Validate the created file
    agent_file_path = f".claude/agents/{agent_name}.md"
    validation = validate_agent_definition(agent_file_path)

    if validation.status != 'valid':
        raise AgentRecoveryError(
            f"Failed to recreate {agent_name}: {validation.error}"
        )

    log_event("agent_file_recovered",
              agent_name=agent_name,
              path=agent_file_path)
```

---

## Critic State Recovery

### Recovering Pending Critique State

If `pending_critique` or `active_critics` state is corrupted:

```python
def recover_critic_state_from_events(event_log_path: str, current_state: dict):
    """Reconstruct critic-related state from event log."""

    pending_critique = []
    active_critics = {}
    critique_failures = {}

    with open(event_log_path, 'r') as f:
        for line in f:
            event = json.loads(line.strip())
            event_type = event['event_type']

            if event_type == 'developer_ready_for_review':
                task_id = event['task_id']
                pending_critique.append(task_id)

            elif event_type == 'critic_dispatched':
                task_id = event['task_id']
                critic_id = event['agent_id']
                if task_id in pending_critique:
                    pending_critique.remove(task_id)
                active_critics[critic_id] = task_id

            elif event_type == 'critic_pass':
                task_id = event['task_id']
                critic_id = event.get('agent_id')
                if critic_id in active_critics:
                    del active_critics[critic_id]
                # Task moves to pending_audit (handled by other recovery)

            elif event_type == 'critic_fail':
                task_id = event['task_id']
                critic_id = event.get('agent_id')
                if critic_id in active_critics:
                    del active_critics[critic_id]
                critique_failures[task_id] = critique_failures.get(task_id, 0) + 1

    # Update state
    current_state['pending_critique'] = pending_critique
    current_state['active_critics'] = active_critics
    current_state['critique_failures'] = critique_failures

    return current_state
```

### Missing Critic Agent File

If the Critic agent file is missing:

```python
def recover_critic_agent_file():
    """Recreate critic agent file from creation template."""

    critic_creation_doc = Read(".claude/docs/agent-creation/critic.md")
    creation_prompt = extract_creation_prompt(critic_creation_doc)

    Task(
        model='opus',
        subagent_type='developer',
        prompt=creation_prompt
    )

    # Validate the created file
    critic_file_path = ".claude/agents/critic.md"
    validation = validate_agent_definition(critic_file_path)

    if validation.status != 'valid':
        raise AgentRecoveryError(f"Failed to recreate critic: {validation.error}")

    log_event("critic_agent_recovered", path=critic_file_path)
```

---

## Cross-References

- [Event Log Recovery](event-log-recovery.md) - Event log as source of truth
- [Session Recovery](session-recovery.md) - Complete recovery orchestration
- [Agent Definitions](../agent-definitions.md) - Agent file structure and requirements
